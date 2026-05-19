from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event, vText
from pathlib import Path
import json
import logging
import re
from urllib.parse import urlparse


# Caminho default do mapeamento de áreas: <repo>/config/areas.json.
# calendar.py está em src/adalove_extractor/io/, então a raiz do repo está 3 níveis acima.
_DEFAULT_AREAS_CONFIG = Path(__file__).resolve().parents[3] / "config" / "areas.json"

# Fallback embutido caso o arquivo não exista — preserva o comportamento mínimo histórico
# (classificação por palavras), mas sem o fallback silencioso pra [COMP].
_AREAS_FALLBACK: dict = {
    "dominios": {},
    "professores": {},
    "palavras": {
        "MAT": ["matemática", "matematica", "cálculo", "estatística", "álgebra", "física"],
        "UX": ["ux", "design", "usabilidade", "interface", "pesquisa", "usuário"],
        "BSS": ["negócios", "negocios", "business", "mercado", "economia"],
        "LID": ["liderança", "lideranca", "carreira", "comunicação", "pitch"],
        "COMP": ["computação", "computacao", "programação", "software", "algoritmo", "dados"],
    },
}


class ICalendarExport:
    """Exportador de dados extraídos para o formato iCalendar (.ics)."""

    def __init__(
        self,
        tz_name: str = "America/Sao_Paulo",
        horario_padrao: str = "08:00",
        duracao_padrao: int = 2,
        areas_config_path: Path | None = None,
    ):
        # Usando um offset fixo de -3 horas para São Paulo para evitar dependência do pytz
        self.timezone = timezone(timedelta(hours=-3), name="BRT")
        self.logger = logging.getLogger(__name__)
        self.horario_padrao = horario_padrao
        self.duracao_padrao = duracao_padrao
        self._areas = self._carregar_areas_config(areas_config_path or _DEFAULT_AREAS_CONFIG)

    def _carregar_areas_config(self, caminho: Path) -> dict:
        """Carrega o mapeamento de áreas. Se faltar/inválido, usa fallback embutido."""
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Garante que as três seções existam (mesmo vazias) para simplificar o consumo
            for chave in ("dominios", "professores", "palavras"):
                cfg.setdefault(chave, {})
            return cfg
        except FileNotFoundError:
            self.logger.warning(f"areas.json não encontrado em {caminho}; usando fallback embutido")
            return _AREAS_FALLBACK
        except json.JSONDecodeError as e:
            self.logger.error(f"areas.json inválido ({e}); usando fallback embutido")
            return _AREAS_FALLBACK

    def gerar_calendario(self, extracao_data: dict, output_path: Path) -> bool:
        cal = Calendar()
        cal.add('prodid', '-//AdaLove Extractor Enhanced//br//')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')

        eventos_adicionados = 0

        semanas = extracao_data.get("semanas", {})
        for semana_key, semana_data in semanas.items():
            if not isinstance(semana_data, dict):
                continue
            
            # Percorrer encontros
            encontros = semana_data.get("encontros", {})
            for date_key, card in encontros.items():
                # No formato api_extraction, 'tipo' comeca com 'encontro'
                tipo = card.get("tipo", "").lower()
                if "encontro" in tipo or card.get("is_sincrono") or card.get("is_encontro"):
                    adicionado = self._adicionar_evento(cal, card, semana_key, date_key=date_key)
                    if adicionado:
                        eventos_adicionados += 1

            # Sem âncora
            sem_ancora = semana_data.get("sem_ancora", [])
            for card in sem_ancora:
                tipo = card.get("tipo", "").lower()
                if "encontro" in tipo or card.get("is_sincrono") or card.get("is_encontro"):
                    adicionado = self._adicionar_evento(cal, card, semana_key)
                    if adicionado:
                        eventos_adicionados += 1

        if eventos_adicionados > 0:
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(cal.to_ical())
                self.logger.info(f"Calendário gerado com sucesso em {output_path} ({eventos_adicionados} eventos)")
                return True
            except Exception as e:
                self.logger.error(f"Erro ao salvar arquivo .ics: {e}")
                return False
        else:
            self.logger.info("Nenhum evento síncrono encontrado para gerar o calendário.")
            return False

    def _determinar_prefixo(self, card: dict) -> str:
        """Determina o prefixo da disciplina aplicando sinais em cascata.

        Ordem (do mais confiável ao mais frágil):
        1. Tipo do encontro (ex.: encontro_orientacao -> ORI, com override por palavra
           do título -> PRV para provas). Metadado estrutural carimbado pelo AdaLove.
        2. Domínio das URLs de autoestudos (livro/site bibliográfico carimba a área).
        3. Nome do professor (substring) via config/areas.json.
        4. Palavras no título + assuntos_relacionados via config/areas.json.
        5. Fallback [??] — explicitamente sinalizando incerteza (não chuta [COMP]).

        Sobre conflito Trilha-do-curso vs URL: quando o material adotado discorda do
        currículo nominal (ex.: tópico aparece em "Estrutura de Dados" na trilha mas o
        autoestudo aponta para livro de matemática discreta), a URL ganha — é o que
        o estudante de fato lê. A Trilha não é consultada nesta primeira leva.
        """
        # 1. Tipo do encontro (override por palavra do título tem prioridade)
        area = self._classificar_por_tipo(card)
        if area:
            self.logger.debug(f"prefixo via tipo: {area} ({card.get('titulo')!r})")
            return f"[{area}] "

        # 2. Domínio das URLs
        urls = self._coletar_urls_card(card)
        area = self._classificar_por_dominio(urls)
        if area:
            self.logger.debug(f"prefixo via dominio: {area} ({card.get('titulo')!r})")
            return f"[{area}] "

        # 3. Professor
        professor = (card.get("professor") or "").lower()
        area = self._classificar_por_professor(professor)
        if area:
            self.logger.debug(f"prefixo via professor: {area} ({card.get('titulo')!r})")
            return f"[{area}] "

        # 4. Texto (título + assuntos_relacionados)
        texto = (
            (card.get("titulo") or "") + " "
            + " ".join(card.get("assuntos_relacionados") or [])
        ).lower()
        area = self._classificar_por_palavras(texto)
        if area:
            self.logger.debug(f"prefixo via palavras: {area} ({card.get('titulo')!r})")
            return f"[{area}] "

        # 5. Fallback visível: deixa explícito que nenhum sinal bateu
        self.logger.info(f"prefixo indeterminado para {card.get('titulo')!r} — caiu em [??]")
        return "[??] "

    def _classificar_por_tipo(self, card: dict) -> str | None:
        """Classifica pelo campo `tipo` do encontro, com override por palavra do título.

        Ex.: `encontro_orientacao` por default vira ORI, mas se o título contiver
        "prova" o override mapeia para PRV. Útil pra carimbar cerimônias ágeis e
        avaliações como categorias próprias, em vez de tentar inferir pela ementa.
        """
        tipo = (card.get("tipo") or "").lower()
        cfg = (self._areas.get("tipos_encontro") or {}).get(tipo)
        if not cfg:
            return None
        titulo = (card.get("titulo") or "").lower()
        for area, palavras in (cfg.get("overrides_por_palavra") or {}).items():
            if any(p.lower() in titulo for p in palavras):
                return area
        return cfg.get("default")

    def _coletar_urls_card(self, card: dict) -> list[str]:
        """Extrai URLs do card e de seus autoestudos.

        Os autoestudos podem vir como dict (chave=nome) ou lista — ambos suportados.
        Cada autoestudo tem `conteudos_relacionados: [{titulo, url}, ...]`.
        """
        urls: list[str] = []
        for cr in card.get("conteudos_relacionados") or []:
            url = (cr or {}).get("url") if isinstance(cr, dict) else None
            if url:
                urls.append(url)

        autoestudos = card.get("autoestudos") or {}
        if isinstance(autoestudos, dict):
            iter_autoestudos = autoestudos.values()
        elif isinstance(autoestudos, list):
            iter_autoestudos = autoestudos
        else:
            iter_autoestudos = []

        for ae in iter_autoestudos:
            if not isinstance(ae, dict):
                continue
            for cr in ae.get("conteudos_relacionados") or []:
                url = (cr or {}).get("url") if isinstance(cr, dict) else None
                if url:
                    urls.append(url)
        return urls

    def _classificar_por_dominio(self, urls: list[str]) -> str | None:
        """Retorna a primeira área cujo domínio configurado bate em alguma URL."""
        mapa = self._areas.get("dominios") or {}
        if not mapa or not urls:
            return None
        dominios_url = []
        for u in urls:
            try:
                host = (urlparse(u).hostname or "").lower()
            except ValueError:
                continue
            if host:
                dominios_url.append(host)
        for dominio_cfg, area in mapa.items():
            alvo = dominio_cfg.lower()
            if any(alvo in host for host in dominios_url):
                return area
        return None

    def _classificar_por_professor(self, professor_lower: str) -> str | None:
        """Substring match no nome do professor. Ordem de iteração do dict define prioridade."""
        if not professor_lower:
            return None
        for chave, area in (self._areas.get("professores") or {}).items():
            if chave.lower() in professor_lower:
                return area
        return None

    def _classificar_por_palavras(self, texto_lower: str) -> str | None:
        """Primeira área cuja lista de palavras-chave bate como substring no texto."""
        if not texto_lower:
            return None
        for area, palavras in (self._areas.get("palavras") or {}).items():
            if any(p.lower() in texto_lower for p in palavras):
                return area
        return None

    def _adicionar_evento(self, cal: Calendar, card: dict, semana_nome: str, date_key: str = "") -> bool:
        """Adiciona um único evento ao calendário se possuir horários válidos."""
        dt_start = None
        
        # 1. Tentar parse iso (caso exista EnrichedCard structure no futuro)
        data_hora_iso = card.get("data_hora_iso")
        if data_hora_iso:
            try:
                dt_start = datetime.fromisoformat(data_hora_iso)
            except Exception:
                pass
                
        # 2. Avaliar date_key do formato antigo (YYYY-MM-DD)
        if not dt_start and date_key and date_key != "sem data":
            try:
                dt_start = datetime.strptime(date_key, "%Y-%m-%d")
                # Extrair hora do título se houver formato 'HHhMM' ou 'HH:MM'
                titulo = card.get("titulo", "")
                match = re.search(r'(\d{1,2})h(\d{2})?', titulo)
                
                try:
                    default_hour, default_minute = map(int, self.horario_padrao.split(":"))
                except ValueError:
                    default_hour, default_minute = 8, 0
                    
                hour, minute = default_hour, default_minute  # Default baseado no turno do módulo
                
                if match:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                else:
                    match_colon = re.search(r'(\d{2}):(\d{2})', titulo)
                    if match_colon:
                        hour = int(match_colon.group(1))
                        minute = int(match_colon.group(2))
                
                dt_start = dt_start.replace(hour=hour, minute=minute)
                dt_start = dt_start.replace(tzinfo=self.timezone)
            except ValueError:
                pass

        if not dt_start:
            return False

        # Configuração de duração padrão a partir da instância
        dt_end = dt_start + timedelta(hours=self.duracao_padrao)

        event = Event()
        
        prefix = self._determinar_prefixo(card)
        
        # Verificar se o encontro ou seus autoestudos têm ponderada
        tem_ponderada = False
        if card.get("is_avaliativo") or card.get("is_ponderada"):
            tem_ponderada = True
            
        autoestudos = card.get("autoestudos", {})
        if isinstance(autoestudos, dict):
            for _, dados in autoestudos.items():
                if dados.get("is_avaliativo") or dados.get("is_ponderada"):
                    tem_ponderada = True
                    break
        elif isinstance(autoestudos, list):
            for dados in autoestudos:
                if isinstance(dados, dict) and (dados.get("is_avaliativo") or dados.get("is_ponderada")):
                    tem_ponderada = True
                    break
                    
        if tem_ponderada:
            prefix = f"📝 {prefix}"
            
        titulo = card.get("titulo", "Encontro Sem Nome")
            
        event.add('summary', f"{prefix}{titulo}")
        event.add('dtstart', dt_start)
        event.add('dtend', dt_end)
        event.add('dtstamp', datetime.now(self.timezone))
        
        # Gerar descrição rica
        descricao_linhas = []
        
        prof = card.get("professor")
        if prof:
            descricao_linhas.append(f"👨‍🏫 Professor: {prof}")
            descricao_linhas.append("")
        
        # O usuário pediu para colocar a descrição do encontro ao invés de somente o professor
        descricao = card.get("descricao")
        if descricao:
            desc_clara = descricao.replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n")
            descricao_linhas.append(desc_clara)
            descricao_linhas.append("")
        else:
            descricao_linhas.append("Sem descrição detalhada disponível.")
            descricao_linhas.append("")
            
        # Lidando com links de arrays ou string
        links = card.get("links_urls") or card.get("links")
        if links:
            descricao_linhas.append("🔗 Links do Encontro:")
            if isinstance(links, str):
                for link in links.split("|"):
                    if link.strip():
                        descricao_linhas.append(link.strip())
            elif isinstance(links, list):
                for link in links:
                    descricao_linhas.append(str(link))
            descricao_linhas.append("")
                    
        desc_final = "\n".join(descricao_linhas).strip()
        event.add('description', vText(desc_final))
        
        uid_base = card.get("record_hash") or card.get("id") or str(dt_start.timestamp())
        event.add('uid', f"adalove-{uid_base}@inteli.edu.br")

        cal.add_component(event)
        return True

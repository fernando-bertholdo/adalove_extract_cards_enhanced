from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event, vText
from pathlib import Path
import logging
import re

class ICalendarExport:
    """Exportador de dados extraídos para o formato iCalendar (.ics)."""

    def __init__(self, tz_name: str = "America/Sao_Paulo", horario_padrao: str = "08:00", duracao_padrao: int = 2):
        # Usando um offset fixo de -3 horas para São Paulo para evitar dependência do pytz
        self.timezone = timezone(timedelta(hours=-3), name="BRT")
        self.logger = logging.getLogger(__name__)
        self.horario_padrao = horario_padrao
        self.duracao_padrao = duracao_padrao

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
        """Determina o prefixo da disciplina com base no professor, título ou assuntos."""
        # 1. Tentar classificar por professor
        prof = (card.get("professor", "") or "").lower()
        
        # Mapeamento heurístico de professores ou áreas
        if any(nome in prof for nome in ["ovidio", "rafael", "computação", "computacao"]):
            return "[COMP] "
        if any(nome in prof for nome in ["pedro", "teberga", "negócios", "business"]):
            return "[BSS] "
        if any(nome in prof for nome in ["guilherme", "cestari", "design", "ux"]):
            return "[UX] "
        if any(nome in prof for nome in ["liderança", "lid"]):
            return "[LID] "
        if any(nome in prof for nome in ["matemática", "matematica", "cálculo"]):
            return "[MAT] "
            
        # 2. Tentar classificar por texto geral (título e assuntos)
        texto = (
            card.get("titulo", "") + " " + 
            " ".join(card.get("assuntos_relacionados", []))
        ).lower()
        
        if any(palavra in texto for palavra in ["ux", "design", "usabilidade", "interface", "pesquisa", "usuário"]):
            return "[UX] "
        if any(palavra in texto for palavra in ["negócios", "negocios", "business", "mercado", "economia", "direito", "trabalho"]):
            return "[BSS] "
        if any(palavra in texto for palavra in ["liderança", "lideranca", "carreira", "comunicação", "pitch"]):
            return "[LID] "
        if any(palavra in texto for palavra in ["matemática", "matematica", "cálculo", "estatística", "álgebra", "física"]):
            return "[MAT] "
        if any(palavra in texto for palavra in ["computação", "computacao", "programação", "software", "algoritmo", "dados", "arquitetura", "qualidade", "código"]):
            return "[COMP] "
            
        # Padrão / Fallback genérico para Computação no Inteli (já que é um curso de tech)
        return "[COMP] "

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

#!/usr/bin/env python3
"""
Script de extração completa de uma turma.
Extrai todas as semanas com detalhes e organiza por pasta.

Uso: python extrair_turma_completa.py [nome_turma]
Exemplo: python extrair_turma_completa.py "2026-1A-T13"
"""

import asyncio
import json
import re
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from adalove_extractor.api import AdaLoveAPIClient
from adalove_extractor.api.endpoints import Endpoints
from adalove_extractor.config.settings import Settings
from adalove_extractor.models.api_card_types import get_type_name, get_type_portuguese
from adalove_extractor.extractors.api.anchor import organize_by_encontros


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def fetch_activity_details(
    client: AdaLoveAPIClient,
    student_activity_uuid: str
) -> Optional[Dict[str, Any]]:
    """Busca detalhes completos de uma atividade."""
    try:
        endpoint = Endpoints.student_activity_data(student_activity_uuid)
        return await client.get(endpoint)
    except Exception as e:
        logger.warning(f"   ⚠️ Erro ao buscar detalhes: {e}")
        return None


def simplificar_atividade(activity: Dict[str, Any], semana: str) -> Dict[str, Any]:
    """Simplifica uma atividade extraindo campos essenciais."""
    tipo_num = activity.get("type")
    card = {
        "semana": semana,
        "titulo": activity.get("caption", ""),
        "descricao": activity.get("description", ""),
        "card_type": get_type_name(tipo_num),
        "data_hora": activity.get("date"),
        "professor": activity.get("professorName"),
        "sort": activity.get("sort", 999),
    }
    
    # Links de conteúdo
    details = activity.get("details") or {}
    contents = details.get("contents", [])
    card["conteudos_relacionados"] = [
        {"titulo": c.get("caption", ""), "url": c.get("reference", "")}
        for c in contents
    ]
    
    # URL básica como fallback
    basic_url = activity.get("basicActivityURL", "")
    if not card["conteudos_relacionados"] and basic_url:
        card["conteudos_relacionados"] = [
            {"titulo": activity.get("caption", ""), "url": basic_url}
        ]
    
    # Assuntos relacionados
    subjects = details.get("subjects", [])
    card["assuntos_relacionados"] = [s.get("subject", "") for s in subjects]
    
    # Ponderada
    grade_weight = activity.get("gradeWeight", 0) or 0
    card["is_ponderada"] = grade_weight > 0 or tipo_num == 21
    
    return card


def slugify_semana(semana: str) -> str:
    """Converte 'Semana 08' para 'semana_08'"""
    match = re.search(r'(\d+)', semana)
    if match:
        num = match.group(1).zfill(2)
        return f"semana_{num}"
    return semana.lower().replace(" ", "_")


async def extrair_turma_completa(turma_nome: str):
    """
    Extrai todas as semanas de uma turma com detalhes e organiza em pastas.
    """
    logger.info("=" * 70)
    logger.info(f"🎯 EXTRAÇÃO COMPLETA: {turma_nome}")
    logger.info("=" * 70)
    
    settings = Settings()
    output_base = Path(__file__).parent / "output" / "api_extraction"
    
    async with AdaLoveAPIClient() as client:
        # 1. Autenticar
        logger.info("\n📋 ETAPA 1: Autenticação")
        await client.authenticate(settings.login, settings.senha)
        logger.info("✅ Autenticado!")
        
        # 2. Buscar turma
        logger.info(f"\n📋 ETAPA 2: Localizando turma {turma_nome}")
        sections = await client.get(Endpoints.SECTIONS)
        sections = sections if isinstance(sections, list) else sections.get("sections", [])
        
        turma_target = None
        for section in sections:
            nome = section.get('caption', section.get('name', ''))
            if nome == turma_nome:
                turma_target = section
                break
        
        if not turma_target:
            logger.error(f"❌ Turma {turma_nome} não encontrada!")
            return None
        
        turma_uuid = turma_target.get('uuid')
        logger.info(f"✅ Turma encontrada (UUID: {turma_uuid})")
        
        # 3. Buscar todas as atividades
        logger.info(f"\n📋 ETAPA 3: Extraindo atividades")
        userdata = await client.get(Endpoints.section_userdata(turma_uuid))
        all_activities = userdata.get("activities", [])
        logger.info(f"   Total de atividades na turma: {len(all_activities)}")
        
        # 4. Agrupar por semana
        logger.info(f"\n📋 ETAPA 4: Agrupando por semana")
        atividades_por_semana = {}
        
        for activity in all_activities:
            folder = activity.get("folderCaption", "")
            if not folder:
                continue
            if folder not in atividades_por_semana:
                atividades_por_semana[folder] = []
            atividades_por_semana[folder].append(activity)
        
        semanas_ordenadas = sorted(atividades_por_semana.keys())
        logger.info(f"   Semanas encontradas: {len(semanas_ordenadas)}")
        for semana in semanas_ordenadas:
            logger.info(f"      {semana}: {len(atividades_por_semana[semana])} atividades")
        
        # 5. Buscar detalhes de cada atividade
        logger.info(f"\n📋 ETAPA 5: Buscando detalhes de cada atividade")
        
        dados_brutos = {}
        total_atividades = 0
        total_com_links = 0
        
        for semana in semanas_ordenadas:
            logger.info(f"\n🗓️ {semana}")
            logger.info("-" * 50)
            
            dados_brutos[semana] = []
            
            for activity in atividades_por_semana[semana]:
                total_atividades += 1
                
                student_uuid = activity.get("studentActivityUuid")
                tipo = activity.get("type")
                caption = activity.get("caption", "N/A")[:45]
                
                # Buscar detalhes
                details = None
                if student_uuid:
                    details = await fetch_activity_details(client, student_uuid)
                    if details and details.get("contents"):
                        total_com_links += 1
                
                # Monta atividade com sort
                atividade_completa = {
                    **activity,
                    "details": details
                }
                
                dados_brutos[semana].append(atividade_completa)
                
                tipo_nome = get_type_portuguese(tipo)[:20]
                logger.info(f"   [{tipo_nome}] {caption}")
        
        # 6. Criar estrutura de pastas e salvar
        logger.info(f"\n📋 ETAPA 6: Organizando e salvando")
        
        turma_slug = turma_nome.replace(" ", "_")
        turma_dir = output_base / turma_slug
        semanas_dir = turma_dir / "semanas"
        semanas_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        
        extracao_completa = {
            "turma": turma_nome,
            "uuid": turma_uuid,
            "extração_timestamp": timestamp,
            "total_semanas": len(semanas_ordenadas),
            "semanas": {}
        }
        
        total_ancoradas = 0
        total_ponderadas = 0
        
        for semana in semanas_ordenadas:
            # Simplifica atividades
            cards = [simplificar_atividade(a, semana) for a in dados_brutos[semana]]
            
            # Aplica ancoragem
            semana_organizada = organize_by_encontros(cards)
            
            # Adiciona à extração completa
            extracao_completa["semanas"][semana] = semana_organizada
            
            # Salva arquivo individual
            semana_file = semanas_dir / f"{slugify_semana(semana)}.json"
            semana_data = {
                "turma": turma_nome,
                "semana": semana,
                "extração_timestamp": timestamp,
                **semana_organizada
            }
            with open(semana_file, 'w', encoding='utf-8') as f:
                json.dump(semana_data, f, ensure_ascii=False, indent=2)
            
            # Estatísticas (encontros agora é um dict com data como chave)
            encontros_dict = semana_organizada.get("encontros", {})
            for data, encontro in encontros_dict.items():
                if encontro.get("is_ponderada"):
                    total_ponderadas += 1
                # autoestudos agora é um dict com título como chave
                autoestudos_dict = encontro.get("autoestudos", {})
                for titulo, auto in autoestudos_dict.items():
                    total_ancoradas += 1
                    if auto.get("is_ponderada"):
                        total_ponderadas += 1
            
            logger.info(f"   ✅ {slugify_semana(semana)}.json salvo")
        
        # Salva extração completa
        extracao_completa["total_atividades"] = total_atividades
        extracao_completa["total_ponderadas"] = total_ponderadas
        extracao_completa["total_ancoradas"] = total_ancoradas
        extracao_completa["total_com_links"] = total_com_links
        
        completo_file = turma_dir / "extracao_completa.json"
        with open(completo_file, 'w', encoding='utf-8') as f:
            json.dump(extracao_completa, f, ensure_ascii=False, indent=2)
        
        # Resumo
        logger.info("\n" + "=" * 70)
        logger.info("📊 RESUMO DA EXTRAÇÃO")
        logger.info("=" * 70)
        logger.info(f"   🏫 Turma: {turma_nome}")
        logger.info(f"   📁 Pasta: {turma_dir}")
        logger.info(f"   📊 Semanas: {len(semanas_ordenadas)}")
        logger.info(f"   📚 Total de atividades: {total_atividades}")
        logger.info(f"   📝 Ponderadas: {total_ponderadas}")
        logger.info(f"   🔗 Cards ancorados: {total_ancoradas}")
        logger.info(f"   🔗 Com links: {total_com_links}")
        logger.info("=" * 70)
        
        return turma_dir


def main():
    # Turma padrão ou argumento
    if len(sys.argv) > 1:
        turma = sys.argv[1]
    else:
        turma = "2026-1A-T13"
    
    result = asyncio.run(extrair_turma_completa(turma))
    
    if result:
        logger.info(f"\n✅ Extração concluída! Pasta: {result}")
    else:
        logger.error("\n❌ Extração falhou!")
        sys.exit(1)


if __name__ == "__main__":
    main()

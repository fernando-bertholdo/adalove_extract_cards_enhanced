#!/usr/bin/env python3
"""
Script de diagnóstico para inspecionar os dados brutos da API
para atividades ponderadas.

Objetivo: Descobrir quais campos da API contêm os dados da aba "Avaliação"
(pergunta + campo de resposta) que aparecem nos cards de autoestudo ponderados.
"""

import asyncio
import json
import sys
from pathlib import Path

# Adiciona raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from adalove_extractor.api import AdaLoveAPIClient
from adalove_extractor.api.endpoints import Endpoints
from adalove_extractor.config.settings import Settings


async def inspect_ponderada():
    settings = Settings()
    
    async with AdaLoveAPIClient() as client:
        # 1. Autenticar
        print("🔐 Autenticando...")
        await client.authenticate(settings.login, settings.senha)
        print("✅ Autenticado!")
        
        # 2. Buscar turma 2026-1A-T13
        turma_nome = "2026-1A-T13"
        print(f"\n📋 Buscando turma {turma_nome}...")
        sections = await client.get(Endpoints.SECTIONS)
        sections = sections if isinstance(sections, list) else sections.get("sections", [])
        
        turma_target = None
        for section in sections:
            nome = section.get('caption', section.get('name', ''))
            if nome == turma_nome:
                turma_target = section
                break
        
        if not turma_target:
            print(f"❌ Turma {turma_nome} não encontrada!")
            return
        
        turma_uuid = turma_target.get('uuid')
        print(f"✅ Turma encontrada (UUID: {turma_uuid})")
        
        # 3. Buscar todas as atividades
        print("\n📋 Buscando atividades...")
        userdata = await client.get(Endpoints.section_userdata(turma_uuid))
        all_activities = userdata.get("activities", [])
        print(f"   Total de atividades: {len(all_activities)}")
        
        # 4. Filtrar ponderadas (gradeWeight > 0)
        ponderadas = []
        for act in all_activities:
            grade_weight = act.get("gradeWeight", 0) or 0
            if grade_weight > 0 or act.get("type") == 21:
                ponderadas.append(act)
        
        print(f"\n🎯 Atividades ponderadas encontradas: {len(ponderadas)}")
        
        # 5. Para cada ponderada, buscar detalhes COMPLETOS e salvar
        output_dir = PROJECT_ROOT / "output" / "debug_ponderadas"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, act in enumerate(ponderadas):
            caption = act.get("caption", "sem_titulo")
            student_uuid = act.get("studentActivityUuid")
            grade_weight = act.get("gradeWeight", 0)
            tipo = act.get("type")
            
            print(f"\n{'='*70}")
            print(f"📝 [{i+1}/{len(ponderadas)}] {caption}")
            print(f"   type={tipo}, gradeWeight={grade_weight}")
            print(f"   studentActivityUuid={student_uuid}")
            
            # Salvar dados da lista (userdata)
            userdata_file = output_dir / f"ponderada_{i+1}_userdata.json"
            with open(userdata_file, 'w', encoding='utf-8') as f:
                json.dump(act, f, ensure_ascii=False, indent=2)
            print(f"   📁 Dados userdata salvos em: {userdata_file.name}")
            
            # Buscar detalhes via student_activity_data
            if student_uuid:
                try:
                    endpoint = Endpoints.student_activity_data(student_uuid)
                    details = await client.get(endpoint)
                    
                    details_file = output_dir / f"ponderada_{i+1}_details.json"
                    with open(details_file, 'w', encoding='utf-8') as f:
                        json.dump(details, f, ensure_ascii=False, indent=2)
                    print(f"   📁 Detalhes salvos em: {details_file.name}")
                    
                    # Mostrar TODAS as chaves do detalhe
                    print(f"   🔑 Chaves no detalhe: {list(details.keys()) if isinstance(details, dict) else 'N/A (lista)'}")
                    
                    # Se for dict, mostrar chaves recursivamente (1 nível)
                    if isinstance(details, dict):
                        for key, value in details.items():
                            if isinstance(value, dict):
                                print(f"      {key}: dict com chaves {list(value.keys())}")
                            elif isinstance(value, list):
                                print(f"      {key}: lista com {len(value)} itens")
                                if value and isinstance(value[0], dict):
                                    print(f"         item[0] chaves: {list(value[0].keys())}")
                            else:
                                val_str = str(value)[:100]
                                print(f"      {key}: {val_str}")
                                
                except Exception as e:
                    print(f"   ⚠️ Erro ao buscar detalhes: {e}")
            
            # Tentar endpoints adicionais que possam conter dados de avaliação
            # Opção A: /student-activities/{uuid}/answer ou similar
            for extra_path in ["/answer", "/evaluation", "/grade", "/submission", "/response"]:
                try:
                    extra_endpoint = f"/student-activities/{student_uuid}{extra_path}"
                    extra_data = await client.get(extra_endpoint)
                    
                    extra_file = output_dir / f"ponderada_{i+1}_extra_{extra_path.strip('/')}.json"
                    with open(extra_file, 'w', encoding='utf-8') as f:
                        json.dump(extra_data, f, ensure_ascii=False, indent=2)
                    print(f"   ✅ Endpoint extra encontrado: {extra_endpoint}")
                    print(f"      Chaves: {list(extra_data.keys()) if isinstance(extra_data, dict) else 'N/A'}")
                except Exception as e:
                    print(f"   ❌ {extra_path}: {type(e).__name__}")
            
            print(f"{'='*70}")
        
        print(f"\n📂 Todos os dados salvos em: {output_dir}")
        print("🔍 Examine os arquivos JSON para descobrir onde estão os dados da aba Avaliação!")


if __name__ == "__main__":
    asyncio.run(inspect_ponderada())

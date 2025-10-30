"""
Writers para exportar dados em diferentes formatos (CSV, JSONL).
"""

import csv
import json
import os
import logging
from typing import Tuple


def write_cards_csv(
    cards_data: list[dict], 
    output_path: str,
    logger: logging.Logger
) -> str:
    """
    Escreve cards brutos em CSV.
    
    Args:
        cards_data: Lista de dicionários com dados dos cards
        output_path: Caminho completo do arquivo de saída
        logger: Logger para mensagens
        
    Returns:
        Caminho do arquivo criado
    """
    headers = [
        "semana", "indice", "id", "titulo", "descricao", "tipo",
        "texto_completo", "links", "materiais", "arquivos"
    ]
    
    logger.info(f"💾 Salvando {len(cards_data)} cards em: {output_path}")
    
    # Cria o diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for card in cards_data:
            # Extrai apenas os campos relevantes
            row = {key: card.get(key, "") for key in headers}
            writer.writerow(row)
    
    logger.info("✅ Dados salvos com sucesso!")
    return output_path


def write_enriched_outputs(
    enriched_data: list[dict], 
    output_dir: str, 
    timestamp: str,
    logger: logging.Logger
) -> Tuple[str, str]:
    """
    Escreve dados enriquecidos em CSV e JSONL.
    
    - CSV: Formato plano para BI/planilhas
    - JSONL: Um JSON por linha para pipelines de dados
    
    Args:
        enriched_data: Lista de dicionários com cards enriquecidos
        output_dir: Diretório onde salvar os arquivos
        timestamp: Timestamp para nomear arquivos
        logger: Logger para mensagens
        
    Returns:
        Tupla (caminho_csv, caminho_jsonl)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    csv_path = os.path.join(output_dir, f"cards_enriquecidos_{timestamp}.csv")
    jsonl_path = os.path.join(output_dir, f"cards_enriquecidos_{timestamp}.jsonl")
    
    # Campos do CSV enriquecido (35 campos totais)
    fields = [
        "semana", "semana_num", "sprint", "indice", "id", "titulo", "descricao", "tipo",
        "data_ddmmaaaa", "hora_hhmm", "data_hora_iso", "professor",
        # NOVA TAXONOMIA UNIFICADA
        "card_type", "is_encontro", "is_sincrono", "is_avaliativo",
        # SEÇÕES RELACIONADAS
        "assuntos_relacionados", "conteudos_relacionados",
        # CAMPOS LEGADOS (compatibilidade)
        "is_instrucao", "is_autoestudo", "is_atividade_ponderada",
        # ANCORAGEM
        "parent_instruction_id", "parent_instruction_title", "anchor_method", "anchor_confidence",
        # URLs NORMALIZADAS
        "links_urls", "materiais_urls", "arquivos_urls", "num_links", "num_materiais", "num_arquivos",
        # INTEGRIDADE
        "record_hash", "texto_completo", "links", "materiais", "arquivos"
    ]
    
    # Escreve CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for card in enriched_data:
            row = {}
            for key in fields:
                value = card.get(key)
                
                # Converter listas e dicionários para strings
                if key == "assuntos_relacionados" and isinstance(value, list):
                    row[key] = " | ".join(value) if value else ""
                elif key == "conteudos_relacionados" and isinstance(value, list):
                    if value:
                        conteudos_str = []
                        for cont in value:
                            if isinstance(cont, dict):
                                conteudos_str.append(f"{cont.get('titulo', '')}: {cont.get('url', '')}")
                            else:
                                conteudos_str.append(str(cont))
                        row[key] = " | ".join(conteudos_str)
                    else:
                        row[key] = ""
                else:
                    row[key] = value
            
            writer.writerow(row)
    
    logger.info(f"💾 Enriched CSV: {csv_path}")
    
    # Escreve JSONL
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for card in enriched_data:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
    
    logger.info(f"💾 Enriched JSONL: {jsonl_path}")
    
    return csv_path, jsonl_path


def compute_stats_by_week(cards_data: list[dict]) -> dict:
    """
    Calcula estatísticas por semana.
    
    Args:
        cards_data: Lista de cards
        
    Returns:
        Dicionário {semana: {cards, links, materiais}}
    """
    stats = {}
    
    for card in cards_data:
        semana = card.get("semana")
        
        if semana not in stats:
            stats[semana] = {"cards": 0, "links": 0, "materiais": 0}
        
        stats[semana]["cards"] += 1
        
        # Conta links
        if card.get("links"):
            stats[semana]["links"] += len(card["links"].split(" | "))
        
        # Conta materiais
        if card.get("materiais"):
            stats[semana]["materiais"] += len(card["materiais"].split(" | "))
    
    return stats



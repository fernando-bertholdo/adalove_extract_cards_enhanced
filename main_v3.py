#!/usr/bin/env python3
"""
Script de execução do Adalove Extractor v3.0.0 (Arquitetura Modular).

Este script utiliza a nova arquitetura modular para executar a extração completa.
"""

import asyncio
import sys

from adalove_extractor.cli.main import run_extraction


def main():
    """Ponto de entrada principal."""
    # Verificar se nome da turma foi passado como argumento
    if len(sys.argv) > 1:
        nome_turma = sys.argv[1].strip()
        print(f"📁 Usando turma: {nome_turma}")
    else:
        # Solicitar nome da turma interativamente
        print("🚀 ADALOVE CARDS EXTRACTOR - VERSÃO 3.1.0 (RESILIENTE)")
        print("=" * 60)
        print("📋 Extração completa incluindo:")
        print("   ✅ Títulos e descrições dos cards")
        print("   ✅ Links e materiais anexados")
        print("   ✅ Arquivos e documentos")
        print("   ✅ Organização por pasta da turma")
        print("   ✅ Enriquecimento e ancoragem de autoestudos")
        print("   ✅ Sistema de checkpoints e recuperação automática")
        print("=" * 60)
        print()
        
        try:
            nome_turma = input("📝 Digite o nome da turma: ").strip()
            if not nome_turma:
                print("❌ Nome da turma é obrigatório!")
                sys.exit(1)
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Entrada cancelada pelo usuário")
            sys.exit(1)
    
    # Executa extração
    if len(sys.argv) > 1:
        # Modo não-interativo quando executado com parâmetros
        import os
        os.environ["ADALOVE_INTERACTIVE"] = "false"
    
    try:
        asyncio.run(run_extraction(nome_turma))
    except KeyboardInterrupt:
        print("\n\n⚠️ Extração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()








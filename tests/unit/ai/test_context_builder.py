"""Testes unitários para ContextBuilder."""

import pytest
from adalove_extractor.ai.context_builder import ContextBuilder


POND_FIXTURE = {
    "titulo": "Implementar CRUD",
    "data_encontro": "2026-03-23",
    "encontro_titulo": "Aula de APIs REST",
    "professor": "Prof. Silva",
    "semana": "Semana 08",
    "avaliacao": {
        "pergunta": "Como você implementaria um CRUD com FastAPI?",
        "peso": 3,
    },
    "descricao": "Atividade sobre criação de APIs REST.",
    "student_activity_uuid": "abc-123",
}

EXTRACAO_FIXTURE = {
    "semanas": {
        "Semana 08": {
            "encontros": {
                "2026-03-23": {
                    "titulo": "Aula de APIs REST",
                    "tipo": "encontro_instrucao",
                    "professor": "Prof. Silva",
                    "descricao": "Aula sobre FastAPI e CRUD.",
                    "autoestudos": {
                        "Leitura: FastAPI Docs": {
                            "descricao": "Leia a documentação oficial do FastAPI.",
                            "professor": "Prof. Silva",
                            "conteudos_relacionados": ["https://fastapi.tiangolo.com"],
                        }
                    },
                }
            },
            "sem_ancora": [],
        }
    }
}


def test_build_returns_non_empty_string():
    builder = ContextBuilder()
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    assert isinstance(result, str)
    assert len(result) > 100


def test_build_includes_question():
    builder = ContextBuilder()
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    assert "Como você implementaria um CRUD com FastAPI?" in result


def test_build_includes_autoestudo_content():
    builder = ContextBuilder()
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    assert "Leitura: FastAPI Docs" in result
    assert "documentação oficial do FastAPI" in result


def test_build_includes_transcript_when_provided():
    builder = ContextBuilder()
    transcript = "O professor explicou que FastAPI usa Pydantic para validação."
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE, transcript=transcript)
    assert "Pydantic para validação" in result


def test_build_includes_user_notes_when_provided():
    builder = ContextBuilder()
    notes = "Entregar link do GitHub com código funcional."
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE, user_notes=notes)
    assert "Entregar link do GitHub" in result


def test_build_without_optional_context():
    builder = ContextBuilder()
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    assert "PERGUNTA DA ATIVIDADE" in result


def test_build_skeleton_mode_requests_structure_only():
    builder = ContextBuilder()
    skeleton = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE, skeleton_mode=True)
    assert "esqueleto" in skeleton.lower() or "estrutura" in skeleton.lower()

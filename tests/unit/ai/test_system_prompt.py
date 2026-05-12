"""Testes unitários para SystemPromptLoader."""

import pytest
from pathlib import Path
from adalove_extractor.ai.system_prompt import SystemPromptLoader


def test_load_returns_string():
    loader = SystemPromptLoader()
    result = loader.load()
    assert isinstance(result, str)
    assert len(result) > 50


def test_load_contains_default_content():
    loader = SystemPromptLoader()
    result = loader.load()
    assert "hífen" in result or "estudante" in result


def test_load_with_session_additions():
    loader = SystemPromptLoader()
    additions = "Entregar apenas o link do repositório GitHub no campo de resposta."
    result = loader.load(session_additions=additions)
    assert "link do repositório GitHub" in result


def test_load_with_empty_session_additions():
    loader = SystemPromptLoader()
    result_without = loader.load()
    result_with_empty = loader.load(session_additions="")
    assert result_without == result_with_empty


def test_load_custom_path(tmp_path):
    custom_prompt = tmp_path / "custom_system_prompt.md"
    custom_prompt.write_text("# Prompt customizado\nFaça respostas curtas.")
    loader = SystemPromptLoader(prompt_path=custom_prompt)
    result = loader.load()
    assert "Faça respostas curtas" in result


def test_load_fallback_when_file_missing(tmp_path):
    nonexistent = tmp_path / "nao_existe.md"
    loader = SystemPromptLoader(prompt_path=nonexistent)
    result = loader.load()
    assert isinstance(result, str)
    assert len(result) > 0

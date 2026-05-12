"""Testes unitários para AnswerGenerator (subprocess mockado)."""

import pytest
from unittest.mock import patch, MagicMock
from adalove_extractor.ai.answer_generator import AnswerGenerator, ClaudeNotFoundError


MOCK_RESPONSE = "Esta é uma resposta gerada pelo Claude sobre FastAPI e CRUD."


def _mock_run_success(*args, **kwargs):
    m = MagicMock()
    m.returncode = 0
    m.stdout = MOCK_RESPONSE
    m.stderr = ""
    return m


def _mock_run_failure(*args, **kwargs):
    m = MagicMock()
    m.returncode = 1
    m.stdout = ""
    m.stderr = "Error: authentication required"
    return m


def test_generate_returns_string_on_success():
    gen = AnswerGenerator()
    with patch("subprocess.run", side_effect=_mock_run_success):
        result = gen.generate(user_prompt="pergunta", system_prompt="instrucoes")
    assert result == MOCK_RESPONSE


def test_generate_raises_on_nonzero_returncode():
    gen = AnswerGenerator()
    with patch("subprocess.run", side_effect=_mock_run_failure):
        with pytest.raises(RuntimeError, match="claude"):
            gen.generate(user_prompt="pergunta", system_prompt="instrucoes")


def test_generate_raises_claude_not_found_when_missing():
    gen = AnswerGenerator()
    with patch("subprocess.run", side_effect=FileNotFoundError("claude not found")):
        with pytest.raises(ClaudeNotFoundError):
            gen.generate(user_prompt="pergunta", system_prompt="instrucoes")


def test_generate_strips_whitespace():
    gen = AnswerGenerator()
    with patch("subprocess.run", side_effect=lambda *a, **k: MagicMock(
        returncode=0, stdout="  resposta com espaços  \n", stderr=""
    )):
        result = gen.generate(user_prompt="p", system_prompt="s")
    assert result == "resposta com espaços"


def test_generate_passes_system_prompt_in_call():
    gen = AnswerGenerator()
    captured = {}

    def capture_run(*args, **kwargs):
        captured["args"] = args
        return MagicMock(returncode=0, stdout="ok", stderr="")

    with patch("subprocess.run", side_effect=capture_run):
        gen.generate(user_prompt="usuario", system_prompt="SISTEMA_ESPECIAL")

    full_cmd = " ".join(str(x) for x in captured["args"][0])
    assert "SISTEMA_ESPECIAL" in full_cmd

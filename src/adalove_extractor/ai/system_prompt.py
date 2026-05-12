"""Carrega e combina o system prompt padrão com adições por sessão."""

from __future__ import annotations
from pathlib import Path

_DEFAULT_PROMPT_PATH = (
    Path(__file__).parent.parent / "config" / "default_system_prompt.md"
)

_FALLBACK_PROMPT = (
    "Você é um assistente que ajuda um estudante universitário a elaborar "
    "respostas para atividades avaliativas. Escreva como um estudante em "
    "aprendizado, usando português coloquial mas correto. Sem hífens em listas, "
    "sem clichês de IA, sem jargão excessivo. Responda de forma completa."
)


class SystemPromptLoader:
    """Carrega system prompt do arquivo padrão e combina com adições por sessão."""

    def __init__(self, prompt_path: Path | None = None):
        self._path = prompt_path or _DEFAULT_PROMPT_PATH

    def load(self, session_additions: str | None = None) -> str:
        """
        Retorna o system prompt completo.

        Args:
            session_additions: Instruções extras adicionadas pelo usuário nesta sessão.

        Returns:
            String com system prompt pronto para uso.
        """
        base = self._load_base()

        if session_additions and session_additions.strip():
            base = (
                base
                + "\n\n## INSTRUÇÕES ADICIONAIS PARA ESTA RESPOSTA\n"
                + session_additions.strip()
            )

        return base

    def _load_base(self) -> str:
        try:
            return self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return _FALLBACK_PROMPT

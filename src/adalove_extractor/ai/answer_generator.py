"""Gera respostas usando o claude CLI como subprocess."""

from __future__ import annotations
import subprocess
import logging

logger = logging.getLogger(__name__)


class ClaudeNotFoundError(Exception):
    """Levantada quando o claude CLI não está instalado/disponível."""


class AnswerGenerator:
    """Chama o claude CLI em modo não-interativo e retorna o texto gerado."""

    def __init__(self, timeout: int = 180):
        self.timeout = timeout

    def generate(self, user_prompt: str, system_prompt: str) -> str:
        """
        Gera texto via claude CLI.

        Args:
            user_prompt: Contexto + tarefa montados pelo ContextBuilder.
            system_prompt: Instruções de estilo carregadas pelo SystemPromptLoader.

        Returns:
            Texto gerado pelo Claude.

        Raises:
            ClaudeNotFoundError: Se claude CLI não estiver no PATH.
            RuntimeError: Se claude retornar código de erro.
        """
        # Embute o system prompt no início do prompt para compatibilidade
        # com qualquer versão do claude CLI
        full_prompt = (
            f"<system>\n{system_prompt}\n</system>\n\n"
            f"<user>\n{user_prompt}\n</user>"
        )

        cmd = ["claude", "-p", full_prompt]

        logger.debug("Chamando claude CLI...")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except FileNotFoundError as e:
            raise ClaudeNotFoundError(
                "claude CLI não encontrado no PATH. "
                "Instale via: npm install -g @anthropic-ai/claude-code"
            ) from e

        if result.returncode != 0:
            error_msg = result.stderr or "erro desconhecido"
            raise RuntimeError(
                f"claude CLI retornou código {result.returncode}: {error_msg}"
            )

        return result.stdout.strip()

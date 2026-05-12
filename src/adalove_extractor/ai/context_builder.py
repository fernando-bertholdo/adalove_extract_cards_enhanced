"""Monta o contexto completo para geração de resposta de ponderada."""

from __future__ import annotations


class ContextBuilder:
    """Constrói o prompt de usuário com todo o contexto disponível."""

    def build(
        self,
        ponderada: dict,
        extracao_data: dict,
        transcript: str | None = None,
        user_notes: str | None = None,
        skeleton_mode: bool = False,
    ) -> str:
        """
        Monta o prompt completo para envio ao claude CLI.

        Args:
            ponderada: Dict com dados da ponderada (de extrair_ponderadas).
            extracao_data: Dict completo da extração (extracao_completa.json).
            transcript: Texto da transcrição de aula (opcional).
            user_notes: Notas adicionais do usuário (opcional).
            skeleton_mode: Se True, solicita apenas esqueleto/estrutura.

        Returns:
            String com o prompt completo.
        """
        sections: list[str] = []

        # 1. Metadados da ponderada
        aval = ponderada.get("avaliacao", {})
        sections.append("## ATIVIDADE PONDERADA")
        sections.append(f"**Título:** {ponderada.get('titulo', '')}")
        sections.append(f"**Semana:** {ponderada.get('semana', '')} — {ponderada.get('data_encontro', '')}")
        sections.append(f"**Encontro relacionado:** {ponderada.get('encontro_titulo', '')}")
        sections.append(f"**Professor:** {ponderada.get('professor', '')}")
        sections.append(f"**Peso:** {aval.get('peso', '?')}")
        if ponderada.get("descricao"):
            sections.append(f"\n**Descrição da atividade:**\n{ponderada['descricao']}")

        # 2. Pergunta
        pergunta = aval.get("pergunta", "")
        if pergunta:
            sections.append(f"\n## PERGUNTA DA ATIVIDADE\n{pergunta}")

        # 3. Autoestudos relacionados
        autoestudos = self._extract_autoestudos(ponderada, extracao_data)
        if autoestudos:
            sections.append("\n## MATERIAIS E AUTOESTUDOS RELACIONADOS")
            for titulo, auto in autoestudos.items():
                sections.append(f"\n### {titulo}")
                if auto.get("descricao"):
                    sections.append(auto["descricao"])
                conteudos = auto.get("conteudos_relacionados") or []
                if conteudos:
                    links = "\n".join(f"- {c}" for c in conteudos)
                    sections.append(f"**Links:**\n{links}")

        # 4. Transcrição (opcional)
        if transcript and transcript.strip():
            sections.append(f"\n## TRANSCRIÇÃO DA AULA\n{transcript.strip()}")

        # 5. Notas do usuário (opcional)
        if user_notes and user_notes.strip():
            sections.append(f"\n## INSTRUÇÕES E NOTAS ADICIONAIS\n{user_notes.strip()}")

        # 6. Instrução final
        if skeleton_mode:
            sections.append(
                "\n## TAREFA\n"
                "Com base no contexto acima, gere APENAS o **esqueleto/estrutura** da resposta. "
                "Inclua:\n"
                "1. Formato de entrega detectado (ex: texto corrido, link GitHub, etc.)\n"
                "2. Tópicos principais que serão abordados (3 a 5 pontos)\n"
                "3. Instruções do professor identificadas no contexto\n"
                "4. Fontes de contexto que serão usadas\n\n"
                "NÃO escreva a resposta completa ainda. Apenas a estrutura para validação."
            )
        else:
            sections.append(
                "\n## TAREFA\n"
                "Com base em todo o contexto acima, escreva a resposta completa para a "
                "atividade ponderada. Siga as instruções de estilo do system prompt e "
                "priorize o conteúdo do contexto fornecido."
            )

        return "\n".join(sections)

    def _extract_autoestudos(self, ponderada: dict, extracao_data: dict) -> dict:
        """Extrai autoestudos do encontro ancorado à ponderada."""
        data_encontro = ponderada.get("data_encontro")
        semana = ponderada.get("semana")

        if not data_encontro or not semana:
            return {}

        semana_data = extracao_data.get("semanas", {}).get(semana, {})
        encontro = semana_data.get("encontros", {}).get(data_encontro, {})
        return encontro.get("autoestudos", {})

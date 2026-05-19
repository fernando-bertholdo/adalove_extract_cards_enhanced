"""Testes para a cascata de classificação de áreas em ICalendarExport._determinar_prefixo.

Cobre as 5 etapas da cascata (tipo, URL, professor, palavras, fallback) com um config
isolado por teste — sem depender do estado real de `config/areas.json`. Isso permite
mudar a config de produção sem quebrar os testes e vice-versa.
"""

import json
import tempfile
from pathlib import Path

import pytest

from adalove_extractor.io.calendar import ICalendarExport


@pytest.fixture
def config_basico(tmp_path: Path) -> Path:
    """Config mínimo com uma entrada por etapa da cascata."""
    cfg = {
        "tipos_encontro": {
            "encontro_orientacao": {
                "default": "ORI",
                "overrides_por_palavra": {"PRV": ["prova"]},
            }
        },
        "dominios": {"discrete.openmathbooks.org": "MAT"},
        "professores": {"pizzo": "MAT", "romualdo": "COMP", "filipe": "LID"},
        "palavras": {
            "MAT": ["grafo"],
            "COMP": ["software"],
            "UX": ["design"],
        },
    }
    caminho = tmp_path / "areas.json"
    caminho.write_text(json.dumps(cfg), encoding="utf-8")
    return caminho


@pytest.fixture
def exporter(config_basico: Path) -> ICalendarExport:
    return ICalendarExport(areas_config_path=config_basico)


class TestCascataEtapa1Tipo:
    """Etapa 1: classificação por `tipo` do encontro (mais determinística)."""

    def test_encontro_orientacao_vira_ori(self, exporter):
        card = {"tipo": "encontro_orientacao", "titulo": "Sprint Planning 2"}
        assert exporter._determinar_prefixo(card) == "[ORI] "

    def test_override_por_palavra_prova(self, exporter):
        card = {"tipo": "encontro_orientacao", "titulo": "Prova do Módulo"}
        assert exporter._determinar_prefixo(card) == "[PRV] "

    def test_tipo_nao_mapeado_segue_cascata(self, exporter):
        """`encontro_instrucao` não está em tipos_encontro — cascata segue normal."""
        card = {"tipo": "encontro_instrucao", "titulo": "Aula sobre software"}
        assert exporter._determinar_prefixo(card) == "[COMP] "


class TestCascataEtapa2URL:
    """Etapa 2: classificação por domínio das URLs dos autoestudos."""

    def test_url_de_matematica_discreta_vira_mat(self, exporter):
        card = {
            "tipo": "encontro_instrucao",
            "titulo": "Grafos - Conceitos Básicos",
            "professor": "Professor Desconhecido",
            "autoestudos": {
                "Grafos": {
                    "conteudos_relacionados": [
                        {"url": "https://discrete.openmathbooks.org/dmoi3/ch_graphtheory.html"}
                    ]
                }
            },
        }
        assert exporter._determinar_prefixo(card) == "[MAT] "

    def test_url_ganha_de_palavra_de_titulo(self, exporter):
        """URL é etapa 2 e palavras é etapa 4 — URL precede mesmo com palavra batendo."""
        card = {
            "tipo": "encontro_instrucao",
            "titulo": "software development",  # bateria em COMP por palavra
            "autoestudos": {
                "Cap. Grafos": {
                    "conteudos_relacionados": [
                        {"url": "https://discrete.openmathbooks.org/x"}
                    ]
                }
            },
        }
        assert exporter._determinar_prefixo(card) == "[MAT] "


class TestCascataEtapa3Professor:
    """Etapa 3: classificação por substring no nome do professor."""

    def test_match_por_sobrenome(self, exporter):
        card = {
            "tipo": "encontro_instrucao",
            "titulo": "Aula qualquer",
            "professor": "Fernando Pizzo Ribeiro",
        }
        assert exporter._determinar_prefixo(card) == "[MAT] "

    def test_professor_ganha_de_palavra(self, exporter):
        """Mesmo título tendo "software" (COMP), professor mapeado (filipe→LID) vence."""
        card = {
            "tipo": "encontro_instrucao",
            "titulo": "Engenharia de software",
            "professor": "Filipe Gonçalves",
        }
        assert exporter._determinar_prefixo(card) == "[LID] "

    def test_professor_case_insensitive(self, exporter):
        card = {
            "tipo": "encontro_instrucao",
            "titulo": "Aula",
            "professor": "JOSÉ ROMUALDO DA COSTA FILHO",
        }
        assert exporter._determinar_prefixo(card) == "[COMP] "


class TestCascataEtapa4Palavras:
    """Etapa 4: classificação por substring no título + assuntos_relacionados."""

    def test_palavra_no_titulo(self, exporter):
        card = {
            "tipo": "encontro_instrucao",
            "titulo": "Introdução ao design system",
            "professor": None,
        }
        assert exporter._determinar_prefixo(card) == "[UX] "

    def test_palavra_em_assuntos_relacionados(self, exporter):
        card = {
            "tipo": "encontro_instrucao",
            "titulo": "Aula da semana",
            "professor": None,
            "assuntos_relacionados": ["Conceitos de grafo direcionado"],
        }
        assert exporter._determinar_prefixo(card) == "[MAT] "


class TestCascataEtapa5Fallback:
    """Etapa 5: fallback visível [??] quando nenhum sinal bateu."""

    def test_card_sem_sinal_vira_indefinido(self, exporter):
        card = {
            "tipo": "encontro_instrucao",
            "titulo": "Reunião genérica",
            "professor": None,
        }
        assert exporter._determinar_prefixo(card) == "[??] "

    def test_nunca_chuta_comp_silenciosamente(self, exporter):
        """Regressão: antes, o fallback retornava [COMP] silenciosamente."""
        card = {"tipo": "encontro_instrucao", "titulo": "x"}
        resultado = exporter._determinar_prefixo(card)
        assert "??" in resultado, f"fallback deveria ser visível, ficou {resultado!r}"


class TestConfigAusente:
    """Quando o arquivo de config não existe, usa fallback embutido sem crashar."""

    def test_config_inexistente_nao_quebra(self, tmp_path: Path):
        inexistente = tmp_path / "nao-existe.json"
        exp = ICalendarExport(areas_config_path=inexistente)
        # Card que bateria no fallback embutido por palavra
        card = {"tipo": "encontro_instrucao", "titulo": "Aula de software"}
        assert exp._determinar_prefixo(card) == "[COMP] "

    def test_config_invalido_usa_fallback(self, tmp_path: Path):
        invalido = tmp_path / "broken.json"
        invalido.write_text("{ isso não é json válido", encoding="utf-8")
        exp = ICalendarExport(areas_config_path=invalido)
        card = {"tipo": "encontro_instrucao", "titulo": "Aula de design"}
        assert exp._determinar_prefixo(card) == "[UX] "

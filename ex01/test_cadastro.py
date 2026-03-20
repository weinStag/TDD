# =============================================================================
# Exercício 1 — Formulário de Corrida: Classes de Equivalência e Casos de Teste
# =============================================================================
#
# Função alvo: verificarCadastro(participante)
#
# CLASSES DE EQUIVALÊNCIA
# ──────────────────────────────────────────────────────────────────────────────
# Campo            | ID   | Partição              | Condição              | Válido?
# ──────────────────────────────────────────────────────────────────────────────
# idade            | EC01 | Abaixo do mínimo      | idade < 10            | Não
#                  | EC02 | Faixa infantil        | 10 ≤ idade ≤ 14       | Sim
#                  | EC03 | Faixa juvenil         | 15 ≤ idade ≤ 17       | Sim
#                  | EC04 | Faixa adulto          | 18 ≤ idade ≤ 60       | Sim
#                  | EC05 | Acima do máximo       | idade > 60            | Não
# ──────────────────────────────────────────────────────────────────────────────
# tempo_estimado   | EC06 | Abaixo do mínimo      | tempo < 30            | Não
# (minutos)        | EC07 | Faixa válida          | 30 ≤ tempo ≤ 180      | Sim
#                  | EC08 | Acima do máximo       | tempo > 180           | Não
# ──────────────────────────────────────────────────────────────────────────────
# assinou_termo    | EC09 | Termo assinado        | True                  | Sim
#                  | EC10 | Termo não assinado    | False                 | Não
# ──────────────────────────────────────────────────────────────────────────────
#
# Retorno esperado de verificarCadastro:
#   {
#       "valido":    bool,
#       "categoria": "infantil" | "juvenil" | "adulto" | None,
#       "erros":     list[str]   # campos com violação
#   }
# =============================================================================

import pytest
from ex01.cadastro import verificarCadastro


# ---------------------------------------------------------------------------
# Helper: constrói um participante completamente válido, com overrides
# ---------------------------------------------------------------------------
def participante(**kwargs):
    base = {"idade": 25, "tempo_estimado": 60, "assinou_termo": True}
    base.update(kwargs)
    return base


# ===========================================================================
# Regra 1 + Regra 2  —  Idade e Categoria
# ===========================================================================

class TestIdade:

    # EC01 — idade < 10 → inválido
    def test_idade_abaixo_do_minimo_e_invalida(self):
        resultado = verificarCadastro(participante(idade=9))
        assert resultado["valido"] is False
        assert "idade" in resultado["erros"]

    # EC02 — 10 ≤ idade ≤ 14 → válido, categoria 'infantil'
    @pytest.mark.parametrize("idade", [10, 12, 14])
    def test_categoria_infantil(self, idade):
        resultado = verificarCadastro(participante(idade=idade))
        assert resultado["valido"] is True
        assert resultado["categoria"] == "infantil"

    # EC03 — 15 ≤ idade ≤ 17 → válido, categoria 'juvenil'
    @pytest.mark.parametrize("idade", [15, 16, 17])
    def test_categoria_juvenil(self, idade):
        resultado = verificarCadastro(participante(idade=idade))
        assert resultado["valido"] is True
        assert resultado["categoria"] == "juvenil"

    # EC04 — 18 ≤ idade ≤ 60 → válido, categoria 'adulto'
    @pytest.mark.parametrize("idade", [18, 35, 60])
    def test_categoria_adulto(self, idade):
        resultado = verificarCadastro(participante(idade=idade))
        assert resultado["valido"] is True
        assert resultado["categoria"] == "adulto"

    # EC05 — idade > 60 → inválido
    def test_idade_acima_do_maximo_e_invalida(self):
        resultado = verificarCadastro(participante(idade=61))
        assert resultado["valido"] is False
        assert "idade" in resultado["erros"]

    # Sem categoria quando a idade é inválida
    def test_sem_categoria_quando_idade_invalida(self):
        resultado = verificarCadastro(participante(idade=5))
        assert resultado["categoria"] is None


# ===========================================================================
# Regra 3  —  Tempo Estimado
# ===========================================================================

class TestTempoEstimado:

    # EC06 — tempo < 30 → inválido
    def test_tempo_abaixo_do_minimo_e_invalido(self):
        resultado = verificarCadastro(participante(tempo_estimado=29))
        assert resultado["valido"] is False
        assert "tempo_estimado" in resultado["erros"]

    # EC07 — 30 ≤ tempo ≤ 180 → válido
    @pytest.mark.parametrize("tempo", [30, 90, 180])
    def test_tempo_valido(self, tempo):
        resultado = verificarCadastro(participante(tempo_estimado=tempo))
        assert resultado["valido"] is True

    # EC08 — tempo > 180 → inválido
    def test_tempo_acima_do_maximo_e_invalido(self):
        resultado = verificarCadastro(participante(tempo_estimado=181))
        assert resultado["valido"] is False
        assert "tempo_estimado" in resultado["erros"]


# ===========================================================================
# Regra 4  —  Assinatura do Termo de Responsabilidade
# ===========================================================================

class TestAssinaturaTermo:

    # EC09 — assinou_termo = True → válido
    def test_termo_assinado_e_valido(self):
        resultado = verificarCadastro(participante(assinou_termo=True))
        assert resultado["valido"] is True

    # EC10 — assinou_termo = False → inválido
    def test_termo_nao_assinado_e_invalido(self):
        resultado = verificarCadastro(participante(assinou_termo=False))
        assert resultado["valido"] is False
        assert "assinou_termo" in resultado["erros"]


# ===========================================================================
# Casos combinados
# ===========================================================================

class TestCasosCombinados:

    def test_participante_totalmente_valido_sem_erros(self):
        """Participante adulto com todos os campos corretos."""
        resultado = verificarCadastro(
            {"idade": 25, "tempo_estimado": 90, "assinou_termo": True}
        )
        assert resultado["valido"] is True
        assert resultado["categoria"] == "adulto"
        assert resultado["erros"] == []

    def test_multiplas_violacoes_relata_todos_os_erros(self):
        """Todos os campos inválidos simultaneamente devem gerar três erros."""
        resultado = verificarCadastro(
            {"idade": 5, "tempo_estimado": 200, "assinou_termo": False}
        )
        assert resultado["valido"] is False
        assert "idade" in resultado["erros"]
        assert "tempo_estimado" in resultado["erros"]
        assert "assinou_termo" in resultado["erros"]

    def test_infantil_valido_completo(self):
        """Criança de 12 anos com tempo e termo válidos."""
        resultado = verificarCadastro(
            {"idade": 12, "tempo_estimado": 45, "assinou_termo": True}
        )
        assert resultado["valido"] is True
        assert resultado["categoria"] == "infantil"
        assert resultado["erros"] == []

    def test_juvenil_valido_completo(self):
        """Adolescente de 16 anos com tempo e termo válidos."""
        resultado = verificarCadastro(
            {"idade": 16, "tempo_estimado": 60, "assinou_termo": True}
        )
        assert resultado["valido"] is True
        assert resultado["categoria"] == "juvenil"
        assert resultado["erros"] == []

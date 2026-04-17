# =============================================================================
# Exercício 6.2 — MC/DC: Controle de Acesso
# =============================================================================
#
# Função alvo: access_control(is_admin, is_owner, is_public, is_logged_in)
#
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 1 — Condições booleanas identificadas
# ──────────────────────────────────────────────────────────────────────────────
#   A = is_admin
#   B = is_owner
#   C = is_public
#   D = is_logged_in
#
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 2 — Expressão lógica
# ──────────────────────────────────────────────────────────────────────────────
#   Resultado = (A or B) and (C or D)
#
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 3 — Tabela verdade completa (16 combinações)
# ──────────────────────────────────────────────────────────────────────────────
#
#   TC  │  A  │  B  │  C  │  D  │ A∨B │ C∨D │ Resultado
#  ─────┼─────┼─────┼─────┼─────┼─────┼─────┼──────────
#   T1  │  F  │  F  │  F  │  F  │  F  │  F  │    F
#   T2  │  F  │  F  │  F  │  T  │  F  │  T  │    F
#   T3  │  F  │  F  │  T  │  F  │  F  │  T  │    F     ← usado no conjunto MC/DC
#   T4  │  F  │  F  │  T  │  T  │  F  │  T  │    F
#   T5  │  F  │  T  │  F  │  F  │  T  │  F  │    F
#   T6  │  F  │  T  │  F  │  T  │  T  │  T  │    T
#   T7  │  F  │  T  │  T  │  F  │  T  │  T  │    T     ← usado no conjunto MC/DC
#   T8  │  F  │  T  │  T  │  T  │  T  │  T  │    T
#   T9  │  T  │  F  │  F  │  F  │  T  │  F  │    F     ← usado no conjunto MC/DC
#   T10 │  T  │  F  │  F  │  T  │  T  │  T  │    T     ← usado no conjunto MC/DC
#   T11 │  T  │  F  │  T  │  F  │  T  │  T  │    T     ← usado no conjunto MC/DC
#   T12 │  T  │  F  │  T  │  T  │  T  │  T  │    T
#   T13 │  T  │  T  │  F  │  F  │  T  │  F  │    F
#   T14 │  T  │  T  │  F  │  T  │  T  │  T  │    T
#   T15 │  T  │  T  │  T  │  F  │  T  │  T  │    T
#   T16 │  T  │  T  │  T  │  T  │  T  │  T  │    T
#
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 4 — Conjunto mínimo MC/DC  (N + 1 = 4 + 1 = 5 testes)
# ──────────────────────────────────────────────────────────────────────────────
#
#   TC  │  A  │  B  │  C  │  D  │ Resultado │ Par MC/DC
#  ─────┼─────┼─────┼─────┼─────┼───────────┼───────────────────────────────────────
#   T3  │  F  │  F  │  T  │  F  │     F     │ base
#   T11 │  T  │  F  │  T  │  F  │     T     │ A: T3↔T11 (só A muda F→T, resultado F→T)
#   T7  │  F  │  T  │  T  │  F  │     T     │ B: T3↔T7  (só B muda F→T, resultado F→T)
#   T9  │  T  │  F  │  F  │  F  │     F     │ C: T9↔T11 (só C muda F→T, resultado F→T)
#   T10 │  T  │  F  │  F  │  T  │     T     │ D: T9↔T10 (só D muda F→T, resultado F→T)
#
#   Demonstração de independência:
#     A: (F,F,T,F)→F  vs  (T,F,T,F)→T  │ B,C,D fixos, só A muda, resultado muda ✓
#     B: (F,F,T,F)→F  vs  (F,T,T,F)→T  │ A,C,D fixos, só B muda, resultado muda ✓
#     C: (T,F,F,F)→F  vs  (T,F,T,F)→T  │ A,B,D fixos, só C muda, resultado muda ✓
#     D: (T,F,F,F)→F  vs  (T,F,F,T)→T  │ A,B,C fixos, só D muda, resultado muda ✓
#
# =============================================================================

import pytest
from ex06.controle_acesso import access_control


# ===========================================================================
# Conjunto mínimo MC/DC — 5 testes
# ===========================================================================

class TestAccessControlMCDC:

    # ── TC3: base  (A=F, B=F, C=T, D=F) → False ────────────────────────────
    def test_tc3_sem_identidade_publico_sem_login_nega(self):
        """A=F, B=F, C=T, D=F → False.  Base do conjunto MC/DC."""
        assert access_control(
            is_admin=False,       # A=F
            is_owner=False,       # B=F
            is_public=True,       # C=T
            is_logged_in=False,   # D=F
        ) is False

    # ── TC11: (A=T, B=F, C=T, D=F) → True   — par de A com TC3 ─────────────
    def test_tc11_admin_publico_sem_login_aprova(self):
        """A=T, B=F, C=T, D=F → True.  Demonstra independência de A."""
        assert access_control(
            is_admin=True,        # A=T  (única mudança em relação a TC3)
            is_owner=False,       # B=F  (mantido)
            is_public=True,       # C=T  (mantido)
            is_logged_in=False,   # D=F  (mantido)
        ) is True

    # ── TC7:  (A=F, B=T, C=T, D=F) → True   — par de B com TC3 ─────────────
    def test_tc7_dono_publico_sem_login_aprova(self):
        """A=F, B=T, C=T, D=F → True.  Demonstra independência de B."""
        assert access_control(
            is_admin=False,       # A=F  (mantido de TC3)
            is_owner=True,        # B=T  (única mudança em relação a TC3)
            is_public=True,       # C=T  (mantido)
            is_logged_in=False,   # D=F  (mantido)
        ) is True

    # ── TC9:  (A=T, B=F, C=F, D=F) → False  — par de C com TC11 ────────────
    def test_tc9_admin_privado_sem_login_nega(self):
        """A=T, B=F, C=F, D=F → False.  Demonstra independência de C."""
        assert access_control(
            is_admin=True,        # A=T
            is_owner=False,       # B=F
            is_public=False,      # C=F  (única mudança em relação a TC11)
            is_logged_in=False,   # D=F  (mantido)
        ) is False

    # ── TC10: (A=T, B=F, C=F, D=T) → True   — par de D com TC9 ─────────────
    def test_tc10_admin_privado_logado_aprova(self):
        """A=T, B=F, C=F, D=T → True.  Demonstra independência de D."""
        assert access_control(
            is_admin=True,        # A=T  (mantido de TC9)
            is_owner=False,       # B=F  (mantido)
            is_public=False,      # C=F  (mantido)
            is_logged_in=True,    # D=T  (única mudança em relação a TC9)
        ) is True


# ===========================================================================
# Casos adicionais: curto-circuito e semântica das sub-expressões
# ===========================================================================

class TestAccessControlLogica:

    # (A or B) = False → nega independente de (C or D)
    def test_sem_admin_nem_owner_nega_mesmo_publico(self):
        assert access_control(False, False, True, True) is False

    # (C or D) = False → nega independente de (A or B)
    def test_admin_mas_sem_acesso_nega(self):
        assert access_control(True, True, False, False) is False

    # Ambas as sub-expressões verdadeiras
    def test_owner_logado_aprova(self):
        assert access_control(False, True, False, True) is True

    def test_admin_publico_aprova(self):
        assert access_control(True, False, True, False) is True

    # Nenhum acesso
    def test_nenhuma_condicao_verdadeira_nega(self):
        assert access_control(False, False, False, False) is False

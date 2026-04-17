# =============================================================================
# Exercício 6.1 — MC/DC: Aprovação de Empréstimo
# =============================================================================
#
# Função alvo: can_approve_loan(income, credit_score, has_debt)
#
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 1 — Condições booleanas identificadas
# ──────────────────────────────────────────────────────────────────────────────
#   A = income > 5000
#   B = credit_score > 700
#   C = not has_debt
#
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 2 — Expressão lógica
# ──────────────────────────────────────────────────────────────────────────────
#   Resultado = (A and B) or C
#
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 3 — Tabela verdade completa
# ──────────────────────────────────────────────────────────────────────────────
#
#   TC │  A  │  B  │  C  │ A∧B │ Resultado
#  ────┼─────┼─────┼─────┼─────┼──────────
#   T1 │  F  │  F  │  F  │  F  │    F
#   T2 │  F  │  F  │  T  │  F  │    T
#   T3 │  F  │  T  │  F  │  F  │    F     ← usado no conjunto MC/DC
#   T4 │  F  │  T  │  T  │  F  │    T
#   T5 │  T  │  F  │  F  │  F  │    F     ← usado no conjunto MC/DC
#   T6 │  T  │  F  │  T  │  F  │    T     ← usado no conjunto MC/DC
#   T7 │  T  │  T  │  F  │  T  │    T     ← usado no conjunto MC/DC
#   T8 │  T  │  T  │  T  │  T  │    T
#
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 4 — Conjunto mínimo MC/DC  (N + 1 = 3 + 1 = 4 testes)
# ──────────────────────────────────────────────────────────────────────────────
#
#   TC │  A  │  B  │  C  │ Resultado │ Par MC/DC
#  ────┼─────┼─────┼─────┼───────────┼──────────────────────────────────────────
#   T3 │  F  │  T  │  F  │     F     │ base
#   T7 │  T  │  T  │  F  │     T     │ A: T3↔T7 (só A muda F→T, resultado F→T)
#   T5 │  T  │  F  │  F  │     F     │ B: T5↔T7 (só B muda F→T, resultado F→T)
#   T6 │  T  │  F  │  T  │     T     │ C: T5↔T6 (só C muda F→T, resultado F→T)
#
#   Demonstração de independência:
#     A: (F,T,F)→F  vs  (T,T,F)→T   | B e C fixos, só A muda, resultado muda ✓
#     B: (T,F,F)→F  vs  (T,T,F)→T   | A e C fixos, só B muda, resultado muda ✓
#     C: (T,F,F)→F  vs  (T,F,T)→T   | A e B fixos, só C muda, resultado muda ✓
#
# =============================================================================

import pytest
from ex06.aprovacao_emprestimo import can_approve_loan


# ===========================================================================
# Conjunto mínimo MC/DC — 4 testes
# ===========================================================================

class TestCanApproveLoanMCDC:

    # ── TC3: base  (A=F, B=T, C=F) → False ─────────────────────────────────
    def test_tc3_sem_renda_sem_divida_nega(self):
        """A=F, B=T, C=F → False.  Base do conjunto MC/DC."""
        assert can_approve_loan(
            income=4000,          # A=F  (4000 ≤ 5000)
            credit_score=750,     # B=T  (750 > 700)
            has_debt=True,        # C=F  (not True = False)
        ) is False

    # ── TC7: (A=T, B=T, C=F) → True   — par de A com TC3 ───────────────────
    def test_tc7_renda_alta_score_alto_sem_divida_aprova(self):
        """A=T, B=T, C=F → True.  Demonstra independência de A (só A muda vs TC3)."""
        assert can_approve_loan(
            income=6000,          # A=T  (6000 > 5000)
            credit_score=750,     # B=T  (mantido de TC3)
            has_debt=True,        # C=F  (mantido de TC3)
        ) is True

    # ── TC5: (A=T, B=F, C=F) → False  — par de B com TC7 ───────────────────
    def test_tc5_renda_alta_score_baixo_com_divida_nega(self):
        """A=T, B=F, C=F → False.  Demonstra independência de B (só B muda vs TC7)."""
        assert can_approve_loan(
            income=6000,          # A=T  (mantido de TC7)
            credit_score=600,     # B=F  (600 ≤ 700)
            has_debt=True,        # C=F  (mantido de TC7)
        ) is False

    # ── TC6: (A=T, B=F, C=T) → True   — par de C com TC5 ───────────────────
    def test_tc6_sem_divida_aprova_independente_de_renda_e_score(self):
        """A=T, B=F, C=T → True.  Demonstra independência de C (só C muda vs TC5)."""
        assert can_approve_loan(
            income=6000,          # A=T  (mantido de TC5)
            credit_score=600,     # B=F  (mantido de TC5)
            has_debt=False,       # C=T  (not False = True)
        ) is True


# ===========================================================================
# Casos de fronteira BVA nos limiares das condições A e B
# (complementam MC/DC com detecção de off-by-one)
# ===========================================================================

class TestCanApproveLoanBVA:

    # Fronteira de A: income = 5000 (at boundary → não aprova pela renda)
    def test_renda_exatamente_5000_nao_satisfaz_A(self):
        assert can_approve_loan(5000, 750, True) is False  # 5000 não é > 5000

    # Fronteira de A: income = 5001 (just above)
    def test_renda_5001_satisfaz_A(self):
        assert can_approve_loan(5001, 750, True) is True

    # Fronteira de B: credit_score = 700 (at boundary → não aprova pelo score)
    def test_score_exatamente_700_nao_satisfaz_B(self):
        assert can_approve_loan(6000, 700, True) is False  # 700 não é > 700

    # Fronteira de B: credit_score = 701 (just above)
    def test_score_701_satisfaz_B(self):
        assert can_approve_loan(6000, 701, True) is True

    # C sozinho aprova — renda e score irrelevantes
    def test_sem_divida_aprova_com_renda_e_score_baixos(self):
        assert can_approve_loan(100, 100, False) is True

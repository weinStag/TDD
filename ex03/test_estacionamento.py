# =============================================================================
# Exercício 3 — Sistema de Cobrança de Estacionamento: BVA (Análise de Valor Limite)
# =============================================================================
#
# Função alvo: ParkingGarageBilling.calculate_fee(entry_time, exit_time, lost_ticket)
#
# FRONTEIRAS IDENTIFICADAS (BVA 3-Value onde aplicável)
# ──────────────────────────────────────────────────────────────────────────────
# Regra                  │ Fronteira                   │ Valor(es) testados
# ──────────────────────────────────────────────────────────────────────────────
# Período grátis         │ 30 min → início da cobrança │ 29, 30, 31 min
# Limite diário          │ R$100 por período de 24h    │ 20h29m, 20h30m, 20h31m
# Período de 24h         │ troca de diária             │ 24h29m, 24h30m, 24h31m
# Dia da semana          │ Sáb/Dom → desconto 20%      │ Sex, Sáb, Dom, Seg
# Noturno (início)       │ 22:00 → desconto R$10       │ 21:59, 22:00, 23:00
# Noturno (fim)          │ 06:00 → fim do desconto     │ 05:59, 06:00, 07:00
# Desconto noturno×taxa  │ R$10 vs valor cobrado       │ baixo (<10), igual (=10), acima (>10)
# Ticket perdido         │ R$300 fixo                  │ qualquer horário
# Validação saída        │ saída < entrada → erro      │ delta = -1s, 0s, +1s
# ──────────────────────────────────────────────────────────────────────────────
#
# Dias usados como referência (verificados):
#   datetime(2026, 3, 23) = Segunda-feira  (weekday=0)
#   datetime(2026, 3, 27) = Sexta-feira    (weekday=4)
#   datetime(2026, 3, 28) = Sábado         (weekday=5)
#   datetime(2026, 3, 29) = Domingo        (weekday=6)
# =============================================================================

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from ex03.estacionamento import ParkingGarageBilling


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def dt(year=2026, month=3, day=23, hour=12, minute=0, second=0) -> datetime:
    return datetime(year, month, day, hour, minute, second)


def park(entry: datetime, *, days: int = 0, hours: int = 0, minutes: int = 0):
    """Retorna (entry, exit) com a duração desejada a partir de entry."""
    return entry, entry + timedelta(days=days, hours=hours, minutes=minutes)


# Referências fixas de dia/hora
MONDAY    = dt(day=23, hour=12)   # weekday
FRIDAY    = dt(day=27, hour=12)   # weekday, véspera do fim de semana
SATURDAY  = dt(day=28, hour=12)   # fim de semana
SUNDAY    = dt(day=29, hour=12)   # fim de semana

MONDAY_AT_22 = dt(day=23, hour=22, minute=0)   # limiar noturno (início)
MONDAY_AT_21_59 = dt(day=23, hour=21, minute=59)  # just-below noturno
MONDAY_AT_06 = dt(day=23, hour=6, minute=0)    # limiar noturno (fim)
MONDAY_AT_05_59 = dt(day=23, hour=5, minute=59)   # just-inside noturno


@pytest.fixture
def billing():
    return ParkingGarageBilling()


# ===========================================================================
# Regra 1 — Período grátis: primeiros 30 minutos
# BVA 3-Value em torno de 30 minutos
#
#  ← grátis ───────────────┤├─── cobrado →
#       29 min           30 min  31 min
#  (just below)         (at)   (just above)
# ===========================================================================

class TestPeriodoGratis:

    def test_zero_minutos_gratis(self, billing):
        entry, exit_ = park(MONDAY, minutes=0)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    # EC: just below boundary — 29 min ainda é grátis
    def test_29_minutos_gratis(self, billing):
        entry, exit_ = park(MONDAY, minutes=29)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    # EC: at boundary — exatamente 30 min ainda é grátis
    def test_30_minutos_exatos_gratis(self, billing):
        entry, exit_ = park(MONDAY, minutes=30)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    # EC: just above boundary — 31 min começa a cobrar (1 min faturável)
    # (1 / 60) × 5.00 = 0.0833... → R$0.08
    def test_31_minutos_cobra_um_minuto(self, billing):
        entry, exit_ = park(MONDAY, minutes=31)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.08")

    def test_60_minutos_cobra_30_min_faturavel(self, billing):
        # (30/60) × 5.00 = R$2.50
        entry, exit_ = park(MONDAY, minutes=60)
        assert billing.calculate_fee(entry, exit_) == Decimal("2.50")

    def test_2_horas_cobra_90_min_faturavel(self, billing):
        # (90/60) × 5.00 = R$7.50
        entry, exit_ = park(MONDAY, hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("7.50")


# ===========================================================================
# Regra 3 — Limite diário de R$100 por período de 24h
# Taxa: R$5/h → para atingir R$100 precisamos de 20h faturáveis = 20h30m total
# BVA em torno de 20h30m (1230 min total / 1200 min faturáveis)
#
#  ← < cap ────────────────┤├───── = cap / > cap (capped) →
#    20h29m (R$99.92)   20h30m (R$100.00)  20h31m (R$100.00 — capped)
# ===========================================================================

class TestLimiteDiario:

    # EC: just below cap — 20h29m → 1199 min faturáveis → R$99.92
    def test_20h29m_abaixo_do_limite(self, billing):
        entry, exit_ = park(MONDAY, hours=20, minutes=29)
        assert billing.calculate_fee(entry, exit_) == Decimal("99.92")

    # EC: at cap — 20h30m → 1200 min faturáveis → R$100.00
    def test_20h30m_exatamente_no_limite(self, billing):
        entry, exit_ = park(MONDAY, hours=20, minutes=30)
        assert billing.calculate_fee(entry, exit_) == Decimal("100.00")

    # EC: just above cap — 20h31m → seria R$100.08, mas limitado a R$100.00
    def test_20h31m_acima_do_limite_e_capped(self, billing):
        entry, exit_ = park(MONDAY, hours=20, minutes=31)
        assert billing.calculate_fee(entry, exit_) == Decimal("100.00")

    def test_23h59m_capped_em_100(self, billing):
        entry, exit_ = park(MONDAY, hours=23, minutes=59)
        assert billing.calculate_fee(entry, exit_) == Decimal("100.00")


# ===========================================================================
# Regra 3b — Cálculo por períodos de 24h (diárias)
# BVA na troca de período: 24h29m / 24h30m / 24h31m
# ===========================================================================

class TestPeriodos24Horas:

    # 1 diária completa: R$100; restante 0 min → grátis → total R$100
    def test_exatamente_24h_igual_a_uma_diaria(self, billing):
        entry, exit_ = park(MONDAY, hours=24)
        assert billing.calculate_fee(entry, exit_) == Decimal("100.00")

    # 1 diária + 29 min restante (dentro do período grátis)
    def test_24h29m_restante_gratis(self, billing):
        entry, exit_ = park(MONDAY, hours=24, minutes=29)
        assert billing.calculate_fee(entry, exit_) == Decimal("100.00")

    # 1 diária + 30 min restante (exatamente na fronteira grátis)
    def test_24h30m_restante_no_limiar_gratis(self, billing):
        entry, exit_ = park(MONDAY, hours=24, minutes=30)
        assert billing.calculate_fee(entry, exit_) == Decimal("100.00")

    # 1 diária + 31 min restante → 1 min faturável → R$100 + R$0.08
    def test_24h31m_cobra_segundo_periodo(self, billing):
        entry, exit_ = park(MONDAY, hours=24, minutes=31)
        assert billing.calculate_fee(entry, exit_) == Decimal("100.08")

    # 2 diárias completas
    def test_48h_duas_diarias(self, billing):
        entry, exit_ = park(MONDAY, hours=48)
        assert billing.calculate_fee(entry, exit_) == Decimal("200.00")

    # Exemplo do enunciado: 4 dias e 12 horas
    # 4 × R$100 = R$400; restante 12h → 690 min faturáveis → (690/60)×5 = R$57.50
    def test_4_dias_e_12_horas_conforme_enunciado(self, billing):
        entry, exit_ = park(MONDAY, days=4, hours=12)
        assert billing.calculate_fee(entry, exit_) == Decimal("457.50")

    # 3 diárias completas + período parcial capped (R$100)
    def test_3_dias_mais_21h_capped(self, billing):
        # 3×100 + min(100, (21h - 30min) × 5) = 300 + 100 = 400
        entry, exit_ = park(MONDAY, days=3, hours=21)
        assert billing.calculate_fee(entry, exit_) == Decimal("400.00")


# ===========================================================================
# Regra 5 — Desconto de Fim de Semana (20%)
# BVA nos dias da semana: Sex (sem), Sáb (com), Dom (com), Seg (sem)
# ===========================================================================

class TestDescontoFimDeSemana:

    # EC: just before weekend boundary — Sexta sem desconto
    def test_sexta_sem_desconto(self, billing):
        # 2h → R$7.50 sem desconto
        entry, exit_ = park(FRIDAY, hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("7.50")

    # EC: at weekend boundary — Sábado com 20% de desconto
    def test_sabado_aplica_desconto_20_pct(self, billing):
        # 2h → base R$7.50 → 7.50 × 0.80 = R$6.00
        entry, exit_ = park(SATURDAY, hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("6.00")

    def test_domingo_aplica_desconto_20_pct(self, billing):
        # 2h → base R$7.50 → R$6.00
        entry, exit_ = park(SUNDAY, hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("6.00")

    # EC: just after weekend boundary — Segunda sem desconto
    def test_segunda_sem_desconto(self, billing):
        entry, exit_ = park(MONDAY, hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("7.50")

    def test_desconto_fim_semana_em_diaria_completa(self, billing):
        # 1 dia completo → R$100 → 100 × 0.80 = R$80.00
        entry, exit_ = park(SATURDAY, hours=24)
        assert billing.calculate_fee(entry, exit_) == Decimal("80.00")


# ===========================================================================
# Regra 6 — Desconto Noturno: R$10 off quando entrada entre 22:00 e 05:59
# BVA 3-Value nos dois limiares horários: 21:59/22:00 e 05:59/06:00
# ===========================================================================

class TestDescontoNoturno:

    # ── Limiar inferior (22:00) ──────────────────────────────────────────────

    # EC: just below lower boundary — 21:59 NÃO é noturno
    def test_21h59_nao_e_noturno(self, billing):
        entry, exit_ = park(MONDAY_AT_21_59, hours=2)
        # base = R$7.50, sem desconto noturno
        assert billing.calculate_fee(entry, exit_) == Decimal("7.50")

    # EC: at lower boundary — 22:00 É noturno
    def test_22h00_e_noturno(self, billing):
        # 2h → base R$7.50 → após desconto: max(0, 7.50 - 10) = R$0.00
        entry, exit_ = park(MONDAY_AT_22, hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    def test_23h00_e_noturno(self, billing):
        entry, exit_ = park(dt(day=23, hour=23), hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    def test_meia_noite_e_noturno(self, billing):
        entry, exit_ = park(dt(day=23, hour=0), hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    # ── Limiar superior (06:00) ──────────────────────────────────────────────

    # EC: just inside upper boundary — 05:59 ainda é noturno
    def test_05h59_ainda_e_noturno(self, billing):
        entry, exit_ = park(MONDAY_AT_05_59, hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    # EC: at upper boundary — 06:00 NÃO é noturno
    def test_06h00_nao_e_noturno(self, billing):
        entry, exit_ = park(MONDAY_AT_06, hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("7.50")

    def test_07h00_nao_e_noturno(self, billing):
        entry, exit_ = park(dt(day=23, hour=7), hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("7.50")

    # ── BVA: valor da taxa vs valor do desconto (R$10) ───────────────────────
    # Faturável de 120 min → (120/60)×5 = R$10.00 → total 150 min = 2h30m
    #
    #  ← taxa < R$10 ──────┤├──── taxa ≥ R$10 (sobra algo após desconto) →
    #      149 min        150 min      151 min

    # EC: just below — 149 min → R$9.92 → após desconto: max(0, 9.92−10) = R$0.00
    def test_noturno_taxa_abaixo_do_desconto_resulta_zero(self, billing):
        entry, exit_ = park(MONDAY_AT_22, minutes=149)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    # EC: at — 150 min → R$10.00 → após desconto: max(0, 10.00−10.00) = R$0.00
    def test_noturno_taxa_igual_ao_desconto_resulta_zero(self, billing):
        entry, exit_ = park(MONDAY_AT_22, minutes=150)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    # EC: just above — 151 min → R$10.08 → após desconto: 10.08−10 = R$0.08
    def test_noturno_taxa_acima_do_desconto_subtrai_10(self, billing):
        entry, exit_ = park(MONDAY_AT_22, minutes=151)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.08")

    def test_noturno_nunca_resulta_em_valor_negativo(self, billing):
        # 31 min → R$0.08, muito abaixo de R$10 → resultado R$0.00
        entry, exit_ = park(MONDAY_AT_22, minutes=31)
        result = billing.calculate_fee(entry, exit_)
        assert result == Decimal("0.00")
        assert result >= Decimal("0.00")


# ===========================================================================
# Regras 5+6 combinadas — Fim de Semana + Noturno
# ===========================================================================

class TestDescontosCombinadosFdSNoturno:

    def test_sabado_noturno_aplica_ambos_descontos(self, billing):
        # Sábado às 22:00, 6h de permanência
        # base: (330/60)×5 = R$27.50
        # fim de semana (20%): 27.50 × 0.80 = R$22.00
        # noturno (−R$10): 22.00 − 10.00 = R$12.00
        entry = dt(day=28, hour=22)   # Sábado 22:00
        exit_ = entry + timedelta(hours=6)
        assert billing.calculate_fee(entry, exit_) == Decimal("12.00")

    def test_sabado_noturno_taxa_pequena_resulta_zero(self, billing):
        # Sábado 22:00, 2h → base R$7.50 → weekend R$6.00 → nocturno max(0,6-10)=0
        entry = dt(day=28, hour=22)
        exit_ = entry + timedelta(hours=2)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    def test_domingo_diurno_sem_desconto_noturno(self, billing):
        # Domingo meio-dia (12h), sem noturno — só weekend
        entry = dt(day=29, hour=12)
        exit_ = entry + timedelta(hours=2)
        # base R$7.50 → weekend R$6.00
        assert billing.calculate_fee(entry, exit_) == Decimal("6.00")


# ===========================================================================
# Regra 4 — Ticket Perdido: taxa fixa R$300.00
# ===========================================================================

class TestTicketPerdido:

    def test_ticket_perdido_retorna_300(self, billing):
        entry, exit_ = park(MONDAY, hours=1)
        assert billing.calculate_fee(entry, exit_, lost_ticket=True) == Decimal("300.00")

    def test_ticket_perdido_ignora_duracao_curta(self, billing):
        entry, exit_ = park(MONDAY, minutes=5)
        assert billing.calculate_fee(entry, exit_, lost_ticket=True) == Decimal("300.00")

    def test_ticket_perdido_ignora_duracao_longa(self, billing):
        entry, exit_ = park(MONDAY, days=10)
        assert billing.calculate_fee(entry, exit_, lost_ticket=True) == Decimal("300.00")

    def test_ticket_perdido_ignora_desconto_fim_semana(self, billing):
        # Mesmo no sábado, ticket perdido = R$300
        entry, exit_ = park(SATURDAY, hours=2)
        assert billing.calculate_fee(entry, exit_, lost_ticket=True) == Decimal("300.00")

    def test_ticket_perdido_ignora_desconto_noturno(self, billing):
        entry, exit_ = park(MONDAY_AT_22, hours=2)
        assert billing.calculate_fee(entry, exit_, lost_ticket=True) == Decimal("300.00")


# ===========================================================================
# Validações — Entradas inválidas (Robust BVA)
# ===========================================================================

class TestValidacoes:

    # BVA limiar de saída: exit < entry proibido
    # EC: just below boundary (delta = −1 second) → inválido
    def test_saida_antes_da_entrada_levanta_erro(self, billing):
        entry = MONDAY
        exit_ = entry - timedelta(seconds=1)
        with pytest.raises(ValueError):
            billing.calculate_fee(entry, exit_)

    # EC: at boundary (delta = 0) → válido (duração zero → R$0.00)
    def test_saida_igual_a_entrada_retorna_zero(self, billing):
        entry = MONDAY
        assert billing.calculate_fee(entry, entry) == Decimal("0.00")

    # EC: just above boundary (delta = +1 second) → válido (dentro do período grátis)
    def test_saida_um_segundo_depois_retorna_zero(self, billing):
        entry = MONDAY
        exit_ = entry + timedelta(seconds=1)
        assert billing.calculate_fee(entry, exit_) == Decimal("0.00")

    def test_entry_nao_datetime_levanta_tipo_erro(self, billing):
        with pytest.raises(TypeError):
            billing.calculate_fee("2026-03-23 12:00", MONDAY)

    def test_exit_nao_datetime_levanta_tipo_erro(self, billing):
        with pytest.raises(TypeError):
            billing.calculate_fee(MONDAY, "2026-03-23 14:00")

    def test_entrada_none_levanta_tipo_erro(self, billing):
        with pytest.raises(TypeError):
            billing.calculate_fee(None, MONDAY)

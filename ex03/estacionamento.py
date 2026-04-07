from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


class ParkingGarageBilling:
    """
    Sistema de cobrança de estacionamento.

    Regras de cobrança:
        - Primeiros 30 min: grátis.
        - Após isso: R$5,00/hora, proporcional por minuto.
        - Limite diário: máximo de R$100,00 por período de 24h.
        - Cálculo multi-dia: cada período completo de 24h custa R$100,00;
          o período restante (incompleto) segue a regra proporcional com cap de R$100,00.
        - Ticket perdido: R$300,00 fixo (ignora horários e descontos).
        - Desconto fim de semana: 20% de desconto quando a entrada é sábado ou domingo.
        - Desconto noturno: R$10,00 subtraídos quando a entrada ocorre entre
          22:00 (inclusive) e 06:00 (exclusive); resultado nunca abaixo de R$0,00.

    Validações:
        - entry_time e exit_time devem ser objetos datetime.
        - exit_time não pode ser anterior a entry_time.
    """

    FREE_MINUTES = 30
    RATE_PER_HOUR = Decimal("5.00")
    DAILY_LIMIT = Decimal("100.00")
    LOST_TICKET_FEE = Decimal("300.00")
    WEEKEND_DISCOUNT_RATE = Decimal("0.20")
    NOCTURNAL_DISCOUNT = Decimal("10.00")

    def calculate_fee(
        self,
        entry_time: datetime,
        exit_time: datetime,
        lost_ticket: bool = False,
    ) -> Decimal:
        if not isinstance(entry_time, datetime) or not isinstance(exit_time, datetime):
            raise TypeError(
                "entry_time e exit_time devem ser objetos datetime; "
                f"recebeu {type(entry_time).__name__} e {type(exit_time).__name__}"
            )

        if lost_ticket:
            return self.LOST_TICKET_FEE

        if exit_time < entry_time:
            raise ValueError(
                f"exit_time ({exit_time}) não pode ser anterior a entry_time ({entry_time})"
            )

        # ── Duração total em minutos (truncado — fração de minuto não é cobrada) ──
        total_minutes = int((exit_time - entry_time).total_seconds()) // 60

        # ── Divisão em períodos de 24h ──────────────────────────────────────────
        minutes_per_day = 24 * 60
        complete_days, remaining_minutes = divmod(total_minutes, minutes_per_day)

        fee = Decimal(complete_days) * self.DAILY_LIMIT

        # ── Período parcial ─────────────────────────────────────────────────────
        if remaining_minutes > self.FREE_MINUTES:
            billable = remaining_minutes - self.FREE_MINUTES
            partial = (Decimal(billable) / Decimal("60")) * self.RATE_PER_HOUR
            fee += min(partial, self.DAILY_LIMIT)

        # ── Desconto de fim de semana (sábado=5, domingo=6) ─────────────────────
        if entry_time.weekday() in (5, 6):
            fee *= Decimal("1") - self.WEEKEND_DISCOUNT_RATE

        # ── Desconto noturno (22:00 ≤ hora < 06:00) ────────────────────────────
        if entry_time.hour >= 22 or entry_time.hour < 6:
            fee = max(Decimal("0"), fee - self.NOCTURNAL_DISCOUNT)

        return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


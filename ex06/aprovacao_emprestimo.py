def can_approve_loan(income: int | float, credit_score: int, has_debt: bool) -> bool:
    """
    Aprova um empréstimo quando:
      - (renda > 5000 E score > 700)  OU  não possui dívida

    Expressão MC/DC: (A and B) or C
      A = income > 5000
      B = credit_score > 700
      C = not has_debt
    """
    if (income > 5000 and credit_score > 700) or not has_debt:
        return True
    return False

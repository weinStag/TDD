def classifica_triangulo(a, b, c):
    """
    Classifica um triângulo dado os comprimentos inteiros dos três lados.

    Regras de validação (Robust BVA):
        - Todos os lados devem ser inteiros (não float, não str).
        - Todos os lados devem ser > 0  (fronteira: lado == 0 é inválido).
        - A soma de quaisquer dois lados deve ser MAIOR que o terceiro
          (fronteira degenerada: a + b == c é inválido).

    Returns:
        'equilátero'  — todos os lados iguais
        'isósceles'   — exatamente dois lados iguais
        'escaleno'    — todos os lados diferentes

    Raises:
        TypeError:  se qualquer lado não for int, ou se o número de
                    argumentos for diferente de 3.
        ValueError: se qualquer lado for ≤ 0, ou se os lados violarem
                    a lei da desigualdade triangular.
    """
    # Regra: tipos devem ser inteiros (bool é subclasse de int — exclui também)
    for lado in (a, b, c):
        if isinstance(lado, bool) or not isinstance(lado, int):
            raise TypeError(
                f"Todos os lados devem ser inteiros; recebeu: {type(lado).__name__}"
            )

    # Fronteira BVA: lado == 0 (boundary) e lado < 0 (just below) → inválidos
    if a <= 0 or b <= 0 or c <= 0:
        raise ValueError(
            f"Todos os lados devem ser maiores que zero; recebeu: ({a}, {b}, {c})"
        )

    # Fronteira BVA: a + b == c (degenerado) e a + b < c (impossível) → inválidos
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError(
            f"Os lados ({a}, {b}, {c}) não satisfazem a lei da desigualdade triangular"
        )

    # Classificação
    if a == b == c:
        return 'equilátero'

    if a == b or b == c or a == c:
        return 'isósceles'

    return 'escaleno'

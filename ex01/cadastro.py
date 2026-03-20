"""
Módulo de validação do cadastro para o formulário de corrida.

Regras de negócio:
    Regra 1 (Idade):    10 ≤ idade ≤ 60
    Regra 2 (Categoria): infantil (10-14), juvenil (15-17), adulto (18-60)
    Regra 3 (Tempo):    30 ≤ tempo_estimado ≤ 180 minutos
    Regra 4 (Termo):    assinou_termo deve ser True
"""


def verificarCadastro(participante: dict) -> dict:
    """
    Valida o cadastro de um participante na corrida.

    Args:
        participante: dicionário com as chaves:
            - idade (int)
            - tempo_estimado (int)  — em minutos
            - assinou_termo (bool)

    Returns:
        Dicionário com:
            - "valido"    (bool): True se todas as regras foram satisfeitas
            - "categoria" (str | None): 'infantil', 'juvenil', 'adulto' ou None
            - "erros"     (list[str]): campos que violaram alguma regra
    """
    erros = []
    categoria = None

    # Regra 1 + Regra 2 — Idade e Categoria
    idade = participante.get("idade")
    if idade is None or idade < 10 or idade > 60:
        erros.append("idade")
    elif 10 <= idade <= 14:
        categoria = "infantil"
    elif 15 <= idade <= 17:
        categoria = "juvenil"
    else:  # 18 <= idade <= 60
        categoria = "adulto"

    # Regra 3 — Tempo estimado (minutos)
    tempo = participante.get("tempo_estimado")
    if tempo is None or tempo < 30 or tempo > 180:
        erros.append("tempo_estimado")

    # Regra 4 — Assinatura do termo de responsabilidade
    if not participante.get("assinou_termo"):
        erros.append("assinou_termo")

    return {
        "valido": len(erros) == 0,
        "categoria": categoria,
        "erros": erros,
    }

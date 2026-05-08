import re


def add(numbers: str) -> int:
    """String Calculator Kata — passos 1 a 9."""
    if not numbers:
        return 0

    delimiters = [',', '\n']

    if numbers.startswith('//'):
        header, numbers = numbers.split('\n', 1)
        delimiter_part = header[2:]

        if delimiter_part.startswith('['):
            # Passos 7-9: //[delim1][delim2]...
            custom = re.findall(r'\[([^\]]+)\]', delimiter_part)
        else:
            # Passo 4: //;\n
            custom = [delimiter_part]

        # Delimitadores customizados têm precedência; vírgula e \n são mantidos
        delimiters = custom + delimiters

    # Ordena por comprimento decrescente para evitar correspondências parciais (** antes de *)
    pattern = '|'.join(re.escape(d) for d in sorted(delimiters, key=len, reverse=True))
    parts = re.split(pattern, numbers)

    nums = [int(p) for p in parts if p.strip() != '']

    negatives = [n for n in nums if n < 0]
    if negatives:
        raise ValueError(
            f"negativos não permitidos: {', '.join(str(n) for n in negatives)}"
        )

    return sum(n for n in nums if n <= 1000)

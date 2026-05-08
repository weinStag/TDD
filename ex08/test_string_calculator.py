import pytest
from ex08.string_calculator import add

# =============================================================================
# Passo 1 — até dois números separados por vírgula
# =============================================================================

def test_empty_string_returns_zero():
    assert add("") == 0


def test_single_number():
    assert add("1") == 1


def test_two_numbers():
    assert add("1,2") == 3


# =============================================================================
# Passo 2 — quantidade desconhecida de números
# =============================================================================

def test_three_numbers():
    assert add("1,2,3") == 6


def test_many_numbers():
    assert add("1,2,3,4,5") == 15


# =============================================================================
# Passo 3 — nova linha como separador
# =============================================================================

def test_newline_as_separator():
    assert add("1\n2,3") == 6


def test_only_newline_separator():
    assert add("1\n2\n3") == 6


# =============================================================================
# Passo 4 — delimitador customizado de um caractere
# =============================================================================

def test_custom_semicolon_delimiter():
    assert add("//;\n1;2") == 3


def test_custom_delimiter_single_number():
    assert add("//;\n5") == 5


def test_existing_scenarios_still_work_after_step4():
    # A linha de cabeçalho é opcional — vírgula e \n continuam funcionando
    assert add("1,2") == 3
    assert add("1\n2") == 3


# =============================================================================
# Passo 5 — números negativos lançam exceção
# =============================================================================

def test_single_negative_raises():
    # match com ^ ancora no início — mata mutante 66 (prefixo XX)
    with pytest.raises(ValueError, match=r"^negativos não permitidos"):
        add("-1,2")


def test_negative_value_in_message():
    with pytest.raises(ValueError, match="-1"):
        add("-1,2")


def test_multiple_negatives_all_in_message():
    with pytest.raises(ValueError) as exc_info:
        add("-1,-2,3")
    msg = str(exc_info.value)
    assert "negativos não permitidos" in msg
    assert "-1" in msg
    assert "-2" in msg
    # verifica separador exato entre negativos — mata mutante 65 ('XX, XX'.join)
    assert "-1, -2" in msg


def test_zero_is_not_negative():
    # zero não deve disparar exceção — mata mutantes 62 (<= 0) e 63 (< 1)
    assert add("0,1") == 1
    assert add("0") == 0
    assert add("1,2") == 3


def test_trailing_delimiter_handled():
    # re.split produz token vazio após delimitador final;
    # filtro p.strip() != '' descarta-o — mata mutante 60 (p.strip() != 'XXXX')
    assert add("1\n2\n") == 3


# =============================================================================
# Passo 6 — números maiores que 1000 são ignorados
# =============================================================================

def test_number_over_1000_ignored():
    assert add("2,1001") == 2


def test_number_exactly_1000_not_ignored():
    assert add("1000,1") == 1001


def test_only_large_numbers_returns_zero():
    assert add("1001,2000") == 0


# =============================================================================
# Passo 7 — delimitador com comprimento > 1
# =============================================================================

def test_long_delimiter():
    assert add("//[***]\n1***2***3") == 6


def test_long_delimiter_two_numbers():
    assert add("//[--]\n10--20") == 30


# =============================================================================
# Passo 8 — múltiplos delimitadores de um caractere
# =============================================================================

def test_multiple_single_char_delimiters():
    assert add("//[*][%]\n1*2%3") == 6


def test_multiple_delimiters_with_newline_still_works():
    assert add("//[*][%]\n1*2%3") == 6


# =============================================================================
# Passo 9 — múltiplos delimitadores com comprimento > 1
# =============================================================================

def test_multiple_long_delimiters():
    assert add("//[**][%%]\n1**2%%3") == 6


def test_multiple_long_delimiters_varied():
    assert add("//[***][###]\n1***2###3") == 6


def test_mixed_length_delimiters():
    assert add("//[**][%]\n4**5%6") == 15


def test_custom_delimiter_with_newline_in_numbers():
    # split('\n', 1) vs split('\n', 2): com maxsplit=2 o unpacking falha
    # quando há \n nos números após o cabeçalho — mata mutante 45
    assert add("//;\n1;2\n3") == 6


def test_overlapping_delimiter_prefix_sort_order():
    # "ab" e "a" — com ordem ascendente, "a" é testado primeiro no regex,
    # deixando "b2a3" como token inválido para int(). reverse=True garante
    # que "ab" seja testado primeiro — mata mutante 56 (reverse=False)
    assert add("//[ab][a]\n1ab2a3") == 6

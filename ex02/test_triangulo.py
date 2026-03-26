# =============================================================================
# Exercício 2 — Classificação de Triângulos: Análise de Valor Limite (BVA)
# =============================================================================
#
# Função alvo: classifica_triangulo(a, b, c)
#
# PARTIÇÕES DE EQUIVALÊNCIA + VALORES LIMITE (BVA 3-Value)
# ──────────────────────────────────────────────────────────────────────────────
# Campo      │ ID   │ Partição                     │ BVA                │Válido?
# ──────────────────────────────────────────────────────────────────────────────
# lado (n)   │ EC01 │ Abaixo do limite zero         │ n = -1 (just below)│ Não
#            │ EC02 │ No limite zero                │ n =  0 (boundary)  │ Não
#            │ EC03 │ Mínimo válido                 │ n =  1 (just above)│ Sim
# ──────────────────────────────────────────────────────────────────────────────
# desigual-  │ EC04 │ Soma menor → não é triângulo  │ a+b < c  (1,2,4)   │ Não
# dade (lei  │ EC05 │ Soma igual (fronteira deg.)   │ a+b = c  (1,2,3)   │ Não
# triangular)│ EC06 │ Soma maior → triângulo válido │ a+b > c  (2,3,4)   │ Sim
# ──────────────────────────────────────────────────────────────────────────────
# tipo       │ EC07 │ Equilátero  (a==b==c)         │ (3,3,3)            │ Sim
#            │ EC08 │ Isósceles   (exatamente 2 =)  │ (3,3,4)            │ Sim
#            │ EC09 │ Escaleno    (todos diferentes)│ (3,4,5)            │ Sim
# ──────────────────────────────────────────────────────────────────────────────
# entrada    │ EC10 │ Lados todos zero              │ (0,0,0)            │ Não
#            │ EC11 │ Tipo não-inteiro              │ (1.5,2,3)          │ Não
#            │ EC12 │ Número errado de argumentos   │ f(3,3)             │ Não
# ──────────────────────────────────────────────────────────────────────────────
#
# Myers originalmente definiu 14 categorias distintas de teste.
# Este arquivo cobre todas elas conforme os slides de BVA.
# =============================================================================

import pytest
from ex02.triangulo import classifica_triangulo


# ===========================================================================
# Cat. 1-4  — Triângulos válidos (incluindo todas as permutações isósceles)
# Slides: "Diagnostic Scorecard: Valid Triangles"
# ===========================================================================

class TestTriangulosValidos:

    # EC09 — Escaleno válido representativo
    def test_escaleno_valido(self):
        assert classifica_triangulo(3, 4, 5) == "escaleno"

    # EC07 — Equilátero válido representativo
    def test_equilatero_valido(self):
        assert classifica_triangulo(3, 3, 3) == "equilátero"

    # EC08 + permutações — Isósceles em todas as 3 configurações de posição
    # (slide: "All three permutations — critical boundary interaction check")
    @pytest.mark.parametrize("a, b, c", [
        (3, 3, 4),   # par igual nas posições a, b
        (3, 4, 3),   # par igual nas posições a, c
        (4, 3, 3),   # par igual nas posições b, c
    ])
    def test_isosceles_todas_permutacoes(self, a, b, c):
        assert classifica_triangulo(a, b, c) == "isósceles"


# ===========================================================================
# Cat. 5-7  — BVA 3-Value na fronteira "lado > 0"
#
#    │── invalid ──│── valid ──────────...
#   -1      0      1      2 ...
#  (EC01) (EC02) (EC03)
#
# Slides: "Scenario 01: Age Validation" (mesma lógica, lados aqui)
# ===========================================================================

class TestFronteiraDeLado:

    # EC01 — Just below zero boundary → inválido
    def test_lado_negativo_e_invalido(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(-1, 4, 5)

    # EC02 — At zero boundary → inválido (zero não forma triângulo)
    def test_lado_zero_e_invalido(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(0, 4, 5)

    # EC03 — Just inside valid boundary → válido
    def test_lado_um_e_valido_com_outros_adequados(self):
        # 1, 1, 1 forma equilátero mínimo válido
        assert classifica_triangulo(1, 1, 1) == "equilátero"

    # EC10 — Todos zero (fronteira absoluta mínima)
    def test_todos_os_lados_zero_sao_invalidos(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(0, 0, 0)


# ===========================================================================
# Cat. 8-11 — BVA 3-Value na lei triangular (a + b > c)
#
#  Fronteira degenerada: a + b = c  →  sombreado como invalido
#
#   a+b < c │ a+b = c │ a+b > c
#   (EC04)  │ (EC05)  │ (EC06)
# ===========================================================================

class TestFronteiraDesigualdadeTriangular:

    # EC04 — Sum of two sides less than third (triângulo impossível)
    def test_soma_menor_que_terceiro_lado_e_invalido(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(1, 2, 4)   # 1+2=3 < 4

    # EC05 — Degenerate boundary: soma exatamente igual ao terceiro lado
    def test_soma_igual_ao_terceiro_lado_e_invalido(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(1, 2, 3)   # 1+2=3 == 3  (triângulo degenerado)

    # EC06 — Just above degenerate boundary: soma maior → triângulo válido
    def test_soma_maior_que_terceiro_lado_e_valido(self):
        assert classifica_triangulo(2, 3, 4) == "escaleno"   # 2+3=5 > 4

    # Verificar a lei triangular nas outras duas combinações de lados
    @pytest.mark.parametrize("a, b, c", [
        (4, 1, 2),   # c é o menor; a > b+c
        (1, 4, 2),   # b é o maior; b > a+c
    ])
    def test_violacao_da_lei_triangular_em_qualquer_posicao(self, a, b, c):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(a, b, c)


# ===========================================================================
# Cat. 12-14 — Entradas inválidas (Robust BVA)
# Slides: "Robust BVA: Testing the Rejection"
# ===========================================================================

class TestEntradasInvalidas:

    # EC11 — Tipo não-inteiro
    def test_lado_float_e_invalido(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(1.5, 2, 3)

    def test_lado_string_e_invalido(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo("3", 3, 3)

    # EC12 — Número errado de argumentos (wrong number of inputs)
    def test_menos_de_tres_argumentos_levanta_excecao(self):
        with pytest.raises(TypeError):
            classifica_triangulo(3, 3)

    def test_mais_de_tres_argumentos_levanta_excecao(self):
        with pytest.raises(TypeError):
            classifica_triangulo(3, 3, 3, 3)


# ===========================================================================
# Casos combinados — cobertura das 14 categorias de Myers
# ===========================================================================

class TestCasosMyers:
    """
    Cobertura direta das 14 categorias definidas por Myers
    em 'The Art of Software Testing' (conforme slides).
    """

    # 1. Escaleno válido
    def test_myers_1_escaleno(self):
        assert classifica_triangulo(3, 4, 5) == "escaleno"

    # 2. Equilátero válido
    def test_myers_2_equilatero(self):
        assert classifica_triangulo(5, 5, 5) == "equilátero"

    # 3-5. Isósceles — todas as 3 permutações
    def test_myers_3_isosceles_ab(self):
        assert classifica_triangulo(3, 3, 4) == "isósceles"

    def test_myers_4_isosceles_ac(self):
        assert classifica_triangulo(3, 4, 3) == "isósceles"

    def test_myers_5_isosceles_bc(self):
        assert classifica_triangulo(4, 3, 3) == "isósceles"

    # 6. Um lado exatamente zero (fronteira absoluta mínima)
    def test_myers_6_lado_zero(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(0, 4, 5)

    # 7. Um lado negativo (just below zero boundary)
    def test_myers_7_lado_negativo(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(-1, 4, 5)

    # 8. Soma de dois lados igual ao terceiro (fronteira degenerada)
    def test_myers_8_soma_igual_ao_lado(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(1, 2, 3)

    # 9. Soma de dois lados menor que o terceiro
    def test_myers_9_soma_menor_que_lado(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(1, 2, 4)

    # 10. Todos os lados zero
    def test_myers_10_todos_zero(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(0, 0, 0)

    # 11-14. Entradas não-inteiras / quantidade incorreta
    def test_myers_11_float(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo(2.5, 3, 4)

    def test_myers_12_string(self):
        with pytest.raises((ValueError, TypeError)):
            classifica_triangulo("a", 3, 4)

    def test_myers_13_dois_argumentos(self):
        with pytest.raises(TypeError):
            classifica_triangulo(3, 3)

    def test_myers_14_quatro_argumentos(self):
        with pytest.raises(TypeError):
            classifica_triangulo(3, 3, 3, 3)

# Exercício 5 — Investigação de Ferramentas de Cobertura MC/DC

**Aluno:** Vinícius da Silva Dias

---

## 1. O que é MC/DC?

**Modified Condition/Decision Coverage (MC/DC)** é um critério de cobertura de testes  
exigido em sistemas de software críticos (aviação, medicina, automotivo).  
Foi definido no padrão **DO-178C** (aviônica) e é usado também no IEC 61508 e ISO 26262.

### 1.1 Hierarquia de cobertura

```
Cobertura de Instruções (Statement)
    ↓ mais forte
Cobertura de Decisões (Decision / Branch)
    ↓ mais forte
Cobertura de Condições (Condition)
    ↓ mais forte
MC/DC  ← critério mais rigoroso praticável
    ↓ mais forte
Cobertura de Caminhos (Path)  ← geralmente inviável
```

### 1.2 Regras do MC/DC

Para cada **decisão** (expressão booleana composta), o MC/DC exige que cada
**condição individual** demonstre que pode, **sozinha**, alterar o resultado da decisão:

| Regra | Descrição |
|-------|-----------|
| **Entry/Exit** | Cada ponto de entrada e saída deve ser executado. |
| **Decision** | Cada decisão deve ser avaliada como `True` e como `False`. |
| **Condition** | Cada condição individual deve ser `True` e `False` ao menos uma vez. |
| **Independence** | Para cada condição C, deve existir um par de casos de teste onde somente C muda e o resultado da decisão muda também. |

### 1.3 Exemplo concreto

```python
# Decisão com 3 condições independentes
def qualifica(idade, tempo, assinou):
    return idade >= 18 and tempo <= 180 and assinou
```

Para cobrir MC/DC, precisamos de pares de testes onde **cada condição provoca sozinha**
a mudança na decisão:

| TC | idade≥18 | tempo≤180 | assinou | Resultado | Par MC/DC para... |
|----|----------|-----------|---------|-----------|-------------------|
| T1 | **T**    | T         | T       | `True`    |                   |
| T2 | **F**    | T         | T       | `False`   | `idade` (T1×T2)   |
| T3 | T        | **F**      | T       | `False`   | `tempo` (T1×T3)   |
| T4 | T        | T         | **F**   | `False`   | `assinou` (T1×T4) |

**4 testes** cobrem MC/DC para 3 condições. Branch coverage exigiria mais combinações
para a mesma garantia teórica.  
> Fórmula mínima: `N + 1` casos de teste para `N` condições independentes.

---

## 2. Ferramentas de Cobertura MC/DC — Panorama

### 2.1 Python — não existe suporte MC/DC nativo

| Ferramenta | Tipo de cobertura | MC/DC? | Notas |
|------------|------------------|--------|-------|
| **coverage.py** | Statement + Branch | ❌ | Padrão da indústria Python; branch é o máximo disponível |
| **pytest-cov** | Statement + Branch | ❌ | Plugin para coverage.py |
| **mutmut** | Mutation testing | ≈ | Indiretamente força cobertura de condições |
| **cosmic-ray** | Mutation testing | ≈ | Alternativa ao mutmut |
| **instrumental** | Condition | ⚠️ | Projeto abandonado; tentativa de MC/DC em Python |
| **mcdc-py** *(experimental)* | MC/DC | ✅ parcial | Sem manutenção ativa; limitado a expressões simples |

**Conclusão para Python:** `coverage.py` com `--branch` é o teto prático disponível.  
MC/DC pleno requer instrumentação AST não disponível em ferramentas maduras para Python.

### 2.2 Outras linguagens — suporte MC/DC maduro

| Ferramenta | Linguagem | MC/DC? | Padrão suportado | Licença |
|------------|-----------|--------|------------------|---------|
| **BullseyeCoverage** | C / C++ | ✅ | DO-178C, IEC 61508 | Comercial |
| **LDRA TBvision** | C, C++, Ada, Java | ✅ | DO-178C, ISO 26262 | Comercial |
| **VectorCAST** | C / C++ | ✅ | DO-178C, IEC 61508 | Comercial |
| **Cantata** | C / C++ | ✅ | DO-178C | Comercial |
| **GCC/gcov + lcov** | C / C++ | Branch only | — | Open Source |
| **Gcovr** | C / C++ | Branch only | — | Open Source |
| **JaCoCo** | Java | Branch only | — | Open Source |
| **OpenCppCoverage** | C++ | Branch only | — | Open Source |
| **Ada CCov** | Ada | ✅ | DO-178C | Open Source |

> **Nota:** Ferramentas certificadas (LDRA, VectorCAST, BullseyeCoverage) geram relatórios
> aceitos por autoridades como FAA e ANAC para certificação de software de aviação.

### 2.3 Diferença prática: Branch vs. MC/DC

```
Expressão:  (A or B) and C

Branch Coverage exige:
  - decisão == True  ao menos uma vez  →  (T,_,T) basta
  - decisão == False ao menos uma vez  →  (F,F,_) ou (_,_,F) basta
  Total: ~2 testes

MC/DC exige adicionalmente:
  - A sozinho muda o resultado →  (T,F,T) vs (F,F,T)   par para A
  - B sozinho muda o resultado →  (F,T,T) vs (F,F,T)   par para B
  - C sozinho muda o resultado →  (T,T,T) vs (T,T,F)   par para C
  Total: mínimo 4 testes (N+1 = 3+1)
```

---

## 3. Demonstração Prática com `coverage.py` (Branch Coverage)

O código usado como exemplo é o sistema de cobrança de estacionamento  
(`ex03/estacionamento.py`), pois contém múltiplas **decisões compostas**.

### 3.1 Instalação

```bash
uv add coverage
# ou: pip install coverage pytest-cov
```

### 3.2 Execução

```bash
# Coleta de dados com branch coverage
uv run coverage run --branch -m pytest ex03/ -v

# Relatório no terminal
uv run coverage report --include="ex03/estacionamento.py" -m

# Relatório HTML (navegável)
uv run coverage html --include="ex03/estacionamento.py"
```

### 3.3 pyproject.toml — configuração persistente

```toml
[tool.coverage.run]
branch = true
source = ["ex01", "ex02", "ex03"]

[tool.coverage.report]
show_missing = true
```

---

## 4. Relatório de Cobertura — Resultado Real

### 4.1 Todos os exercícios

Executado com:
```bash
uv run coverage run --branch -m pytest ex01/ ex02/ ex03/ -q
uv run coverage report --include="ex01/*,ex02/*,ex03/*" -m
```

```
Name                          Stmts   Miss  Branch  BrPart   Cover   Missing
----------------------------------------------------------------------------
ex01\cadastro.py                 17      0      10       0    100%
ex01\test_cadastro.py            76      0       0       0    100%
ex02\__init__.py                  0      0       0       0    100%
ex02\test_triangulo.py           86      0       0       0    100%
ex02\triangulo.py                13      0      12       0    100%
ex03\__init__.py                  0      0       0       0    100%
ex03\estacionamento.py           29      0      12       0    100%
ex03\test_estacionamento.py     176      0       0       0    100%
----------------------------------------------------------------------------
TOTAL                           397      0      34       0    100%
```

**Resultado: 100% de cobertura de instruções e de branches em todos os módulos.**

### 4.2 Legenda das colunas

| Coluna | Significado |
|--------|-------------|
| `Stmts` | Total de instruções executáveis |
| `Miss` | Instruções não executadas |
| `Branch` | Total de branches identificados (cada `if/else` gera 2) |
| `BrPart` | Branches parcialmente cobertos (entrou mas não saiu, ou vice-versa) |
| `Cover` | Percentual de cobertura = `(Stmts - Miss) / Stmts × 100` |
| `Missing` | Linhas não cobertas |

### 4.3 Análise detalhada — `ex03/estacionamento.py`

```
29 instruções  |  0 não cobertas  |  12 branches  |  0 branches parciais  |  100%
```

As **12 branches** mapeiam diretamente para as **6 decisões** do método `calculate_fee`:

| Linha | Decisão | Branch True | Branch False | Cobertura |
|-------|---------|------------|-------------|-----------|
| 38 | `not isinstance(entry_time, datetime) or not isinstance(exit_time, datetime)` | ✅ | ✅ | 100% |
| 44 | `if lost_ticket` | ✅ | ✅ | 100% |
| 47 | `if exit_time < entry_time` | ✅ | ✅ | 100% |
| 60 | `if remaining_minutes > self.FREE_MINUTES` | ✅ | ✅ | 100% |
| 67 | `if entry_time.weekday() in (5, 6)` | ✅ | ✅ | 100% |
| 71 | `if entry_time.hour >= 22 or entry_time.hour < 6` | ✅ | ✅ | 100% |

---

## 5. Análise MC/DC Manual — Decisão Mais Crítica

A decisão mais complexa do código é o **desconto noturno**, com **2 condições**  
unidas por `or`:

```python
# Linha 71:
if entry_time.hour >= 22 or entry_time.hour < 6:
```

Seja:
- **A** = `entry_time.hour >= 22`
- **B** = `entry_time.hour < 6`

### Tabela de casos necessários para MC/DC

| TC | A (h≥22) | B (h<6) | Resultado (A or B) | Par MC/DC | Teste correspondente |
|----|----------|---------|--------------------|-----------|----------------------|
| T1 | T (22h)  | F       | **T**              |           | `test_22h00_e_noturno` |
| T2 | F (12h)  | F       | **F**              | A: T1×T2  | `test_07h00_nao_e_noturno` |
| T3 | F (01h)  | T       | **T**              | B: T3×T2  | `test_meia_noite_e_noturno` |

Com 3 testes (N+1 = 2+1) cobrimos MC/DC completo para essa decisão.  
A suite atual **contém todos esses casos**, satisfazendo MC/DC implicitamente.

### BVA + MC/DC — complementaridade

```
BVA identifica QUANDO testar (nos limites: 21:59, 22:00, 05:59, 06:00)
MC/DC identifica QUAIS combinações testar (cada condição deve ser independente)

Juntos, garantem que off-by-one errors E erros de lógica booleana sejam detectados.
```

---

## 6. Limitações do Branch Coverage vs. MC/DC

```python
# Exemplo de código onde branch coverage passa, mas MC/DC detecta falha:

def desconto_aplicavel(fim_de_semana: bool, noturno: bool) -> bool:
    # Bug sutil: deveria ser "or", programador escreveu "and"
    return fim_de_semana and noturno   # ← BUG

# Testes com 100% branch coverage:
assert desconto_aplicavel(True, True)   == True   # branch True ✅
assert desconto_aplicavel(False, False) == False  # branch False ✅
# Branch: 100% ✅ — BUG NÃO DETECTADO

# Testes MC/DC adicionais que detectam o bug:
assert desconto_aplicavel(True, False)  == True   # falha! retorna False ← BUG DETECTADO
assert desconto_aplicavel(False, True)  == True   # falha! retorna False ← BUG DETECTADO
```

**Este é exatamente o tipo de erro que MC/DC foi projetado para encontrar.**

---

## 7. Resumo Executivo

| Critério | Ferramentas Python | Suporte | Recomendação |
|----------|--------------------|---------|--------------|
| **Statement** | coverage.py | ✅ Maduro | Mínimo aceitável |
| **Branch** | coverage.py `--branch` | ✅ Maduro | Padrão para projetos Python |
| **Condition** | — | ❌ Sem suporte | Não disponível em ferramentas ativas |
| **MC/DC** | — | ❌ Sem suporte nativo | Fazer análise manual (como Seção 5) |
| **MC/DC (C/C++)** | BullseyeCoverage, LDRA | ✅ Certificado | Para sistemas críticos |

### Conclusão

Para Python, a abordagem mais robusta disponível é:

1. **`coverage.py --branch`** para garantir cobertura de branches (automatizado).
2. **Análise MC/DC manual** para decisões compostas críticas (como feito na Seção 5).
3. **BVA** na seleção dos valores de teste, garantindo que os pares MC/DC incidam sempre nos limiares.
4. **Mutation testing** (`mutmut`) como complemento prático para detectar condições lógicas incorretas.

> "Testing valid logic proves the system works.  
> MC/DC proves the logic itself is correct."

---

## Referências

- RTCA DO-178C — *Software Considerations in Airborne Systems and Equipment Certification*, 2011.
- FAA Advisory Circular AC 20-115D — *Airborne Software Development Assurance Using EUROCAE ED-12 and RTCA DO-178*, 2017.
- Myers, G. J. — *The Art of Software Testing*, 3ª ed., Wiley, 2011.
- [coverage.py Documentation](https://coverage.readthedocs.io/)
- [BullseyeCoverage — MC/DC](https://www.bullseye.com/coverage.html)
- [LDRA TBvision](https://ldra.com/)

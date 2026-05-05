# Relatório de Teste de Mutação — Motor de Pricing de Reservas

## 1. Resultado Inicial

Antes de melhorar os testes, havia apenas um caso de teste (`test_basic_price`) que somente
verificava `total > 0`. Resultado do mutmut na bateria inicial:

| Métrica          | Valor |
|------------------|-------|
| Total de mutantes | 37   |
| Mortos 🎉        | 12    |
| Sobreviventes 🙁 | 25    |
| **Score**        | **32%** |

---

## 2. Análise dos Mutantes Sobreviventes

### 2.1 `WEEKEND_DAYS` — mutantes 1 e 2
Substituição de membros do conjunto (`{5,6}` → `{6,6}` ou `{5,7}`). O teste original nunca
chamava `is_weekend`, então qualquer valor no conjunto passava.

### 2.2 `is_weekend` — mutante 4
`return d.weekday() in WEEKEND_DAYS` → `not in`. Inverter a lógica não era detectado porque
nenhum teste verificava o *valor exato* do surcharge.

### 2.3 `calculate_nights` — mutantes 5 e 6
- Mutante 5: `checkout <= checkin` → `checkout < checkin` (datas iguais não lançavam exceção).
- Mutante 6: mensagem da `ValueError` alterada para `"XXInvalid date rangeXX"`. O `match=` em
  `pytest.raises` usa `re.search`, então um padrão sem âncoras (`^...$`) ainda detecta a
  substring mutante como válida.

### 2.4 Fórmulas aritméticas — mutantes 9, 21, 22, 23, 25, 26, 33, 35
Mudanças de `*` para `/`, adição para subtração e semelhantes em `base`, `weekend_surcharge`,
`subtotal` e `service_fee`. Todos sobreviviam porque o único assert era `> 0` — qualquer número
positivo passava.

### 2.5 Inicialização e loop — mutantes 12, 14, 15, 16, 17, 19
- `weekend_nights = 0` → `= 1` (começa inflado).
- `while current < checkout` → `<=` (itera um dia a mais).
- `weekend_nights += 1` → `= 1`, `-= 1`, `+= 2`.
- `current.day + 1` → `+ 2` (pula um dia no loop).

### 2.6 Desconto de 7 noites — mutantes 28, 29, 30, 31, 32
- Limiar alterado: `>= 7` → `> 7`, `>= 8`.
- Operação alterada: `*= 0.9` → `= 0.9`, `/= 0.9`, `*= 1.9`.
Nenhum teste cobria o caminho do desconto.

### 2.7 Arredondamento — mutante 37
`round(total, 2)` → `round(total, 3)`. Quando o total não tem 3 casas decimais significativas,
os dois produzem o mesmo resultado.

---

## 3. Melhorias Feitas nos Testes

Foram adicionados **18 testes** (total: 19), cobrindo:

| Teste | Mutantes que mata |
|---|---|
| `test_is_weekend_saturday` | 1, 4 |
| `test_is_weekend_sunday` | 2 |
| `test_is_weekend_friday_is_not_weekend` | 4 (controle) |
| `test_calculate_nights_raises_for_equal_dates` (match `^...$`) | 5, 6 |
| `test_calculate_nights_raises_for_checkout_before_checkin` | 5, 6 |
| `test_exact_price_weekdays_only` | 9, 25, 26 |
| `test_cleaning_fee_adds_to_total` | 26 |
| `test_saturday_night_surcharge` (valor exato 120.0) | 1, 4, 12, 15, 16, 17, 21, 22, 23, 25 |
| `test_sunday_night_surcharge` | 2, 4 |
| `test_two_weekend_nights_surcharge` | 15, 19 |
| `test_friday_night_no_surcharge` | 12 |
| `test_six_nights_no_discount` (checkout = domingo) | 14, 28, 29 |
| `test_seven_nights_discount` (valor exato 666.0) | 28, 29, 30, 31, 32 |
| `test_service_fee_applied` | 33, 35 |
| `test_rounding_to_two_decimal_places` (109.13) | 37 |

**Princípio-chave**: trocar `assert total > 0` por `assert total == <valor_exato>` foi a mudança
mais impactante — eliminou dezenas de mutantes de uma vez.

Para o mutante 6, foi necessário ancorar o padrão de regex: `match=r"^Invalid date range$"` em
vez de apenas `match="Invalid date range"`, pois `re.search` faz correspondência de substring.

---

## 4. Resultado Final

| Métrica          | Antes | Depois |
|------------------|-------|--------|
| Total de mutantes | 37   | 37     |
| Mortos 🎉        | 12    | **37** |
| Sobreviventes 🙁 | 25    | **0**  |
| **Score**        | **32%** | **100%** |

---

## 5. Principais Aprendizados

1. **`assert resultado > 0` não é um teste** — verifica apenas que o código não explodiu, não que
   ele calcula corretamente. Sempre afirme o valor exato esperado.

2. **Testar casos-limite nos operadores condicionais**: um teste com exatamente **7 noites** é
   indispensável para distinguir `>= 7` de `> 7` ou `>= 8`.

3. **Testar cada componente do cálculo isoladamente**: cobrir `cleaning_fee=0` vs `cleaning_fee=50`,
   `service_fee_pct=0` vs `0.1`, e assim por diante, expõe mutações aritméticas que testes
   "integrados" deixam passar.

4. **`re.search` em `pytest.raises(match=…)` é busca por substring**: para garantir que a mensagem
   exata seja verificada, use âncoras `^` e `$` no padrão.

5. **Testar separadamente sábado e domingo**: para confirmar que *ambos* os dias do conjunto
   `WEEKEND_DAYS` estão corretos — um único teste "fim de semana" poderia não detectar a remoção
   de um dos dias.

6. **Engenharia de valores para testar arredondamento**: escolher parâmetros que gerem três casas
   decimais (ex.: `cleaning_fee=1.99`, `service_fee_pct=0.07`) permite distinguir
   `round(x, 2)` de `round(x, 3)`.

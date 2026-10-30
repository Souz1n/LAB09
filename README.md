# Laboratório 9 — Testes de Mutação

**CC8550 — Simulação e Teste de Software** · Prof. Luciano Rossi · Centro Universitário FEI · 2º semestre de 2026
**Aluno:** Gustavo Souza Alvarenga

Ambiente: Linux, Python 3.13, `pytest==9.1.1`, `pytest-cov==7.1.0`, `mutmut==3.8.0`.
Escore de mutação: **MS = mortos / (gerados − equivalentes)**.

```
lab09/
├── requirements.txt
├── ex1/  src/classificacao.py   tests/test_classificacao.py
├── ex2/  src/carrinho.py        tests/test_carrinho.py
├── ex3/  src/temperaturas.py    tests/test_temperaturas.py
└── ex4/  src/parcelamento.py    tests/test_parcelamento.py   segunda_ordem.py
```

Para reproduzir, dentro de cada pasta `exN`:

```bash
pip install -r ../requirements.txt
pytest -q --cov=src --cov-branch --cov-report=term-missing
mutmut run && mutmut results --all true
```

Os números de mutante (ex.: "mutante 7") são os do mutmut: `mutmut show <modulo>.x_<funcao>__mutmut_7`.
Os arquivos de teste entregues são as suítes **finais**; as suítes iniciais estão reproduzidas abaixo e marcadas no topo de cada arquivo.

## Resumo dos números

| Ex. | Suíte | Cobertura de ramos | Gerados | Mortos | Vivos | Equiv. | MS |
|---|---|---|---|---|---|---|---|
| 1 | inicial (2 testes) | 64% | 36 | 6 | 30 | 0 | **16,7%** |
| 1 | + fronteiras, `str(exc.value) ==` | 100% | 36 | 36 | 0 | 0 | **100%** |
| 1 | com `match="msg"` | 100% | 36 | 34 | 2 | 0 | 94,4% |
| 1 | com `match=r"^msg$"` (final) | 100% | 36 | 36 | 0 | 0 | **100%** |
| 2 | inicial (`> 0`) | 100% | 16 | 4 | 12 | 0 | **25%** |
| 2 | assert exato | 100% | 16 | 13 | 3 | 0 | 81,25% |
| 2 | + preço com centavos (final) | 100% | 16 | 16 | 0 | 0 | **100%** |
| 3 | inicial | 100% | 22 | 11 | 11 | 2 | **55%** |
| 3 | final | 100% | 22 | 20 | 2 | 2 | **100%** |
| 4 | valor-limite (final) | 100% | 27 | 26 | 1 | 1 | **100%** |

---

## Exercício 1 — Situação do aluno

Suíte inicial:

```python
def test_aprovado():
    assert classificar_aluno(8.0, 80) == "Aprovado"

def test_reprovado():
    assert classificar_aluno(3.0, 90) == "Reprovado"
```

### a) Cobertura e mutmut

- Cobertura de ramos: **64%** (linhas 3, 5, 7 e 11 nunca executadas; 4 ramos parciais).
- mutmut: **36 gerados, 6 mortos, 30 vivos** → MS = 6/36 = **16,7%**.
- Os únicos mortos são as trocas de texto nos retornos `"Aprovado"` (26–28) e `"Reprovado"` (34–36), que são exatamente os dois valores conferidos.

### b) Vivos agrupados pela causa

| Grupo | Causa | Mutantes | Qtde |
|---|---|---|---|
| **A — linha nunca executada** | mensagem de `ValueError` da média (linha 3) | 6, 7, 8, 9 | 4 |
| | mensagem de `ValueError` da presença (linha 5) | 15, 16, 17, 18 | 4 |
| | literal `"Reprovado por falta"` (linha 7) | 21, 22, 23 | 3 |
| | literal `"Recuperacao"` (linha 11) | 31, 32, 33 | 3 |
| **B — validação executada, mas sempre falsa** | nenhuma entrada inválida nem de fronteira: `or→and`, `<→<=`, `0→1`, `>→>=`, `10→11` (média) | 1, 2, 3, 4, 5 | 5 |
| | idem para presença (`0→1`, `100→101`…) | 10, 11, 12, 13, 14 | 5 |
| **C — fronteira da classificação não testada** | presença 75: `<75 → <=75`, `<75 → <76` | 19, 20 | 2 |
| | média 7,0: `>=7 → >7`, `>=7 → >=8` | 24, 25 | 2 |
| | média 5,0: `>=5 → >5`, `>=5 → >=6` | 29, 30 | 2 |

**14 vivos (grupo A) estão em linhas que a suíte nem executa** (3, 5, 7 e 11) — nenhum teste poderia matá-los. Os outros 16 estão em linhas executadas, mas os testes usam valores longe das fronteiras. Um caso curioso é o mutante 25 (`media >= 8.0`): ele sobrevive mesmo com o teste usando 8.0, porque 8.0 fica exatamente sobre a fronteira mutada (8 ≥ 8 continua verdadeiro). O teste certo é em 7.0.

### c) Testes acrescentados

Testes por valor-limite nos dois parâmetros e nas duas fronteiras de classificação, mais as entradas inválidas com a mensagem conferida por `assert str(exc.value) == "..."`:

| Entrada | Mata |
|---|---|
| média 0 e 0.5 (válidas) | 2, 3 |
| média 10 (válida) | 4 |
| média 7.0 → Aprovado; 6.9 → Recuperação | 24, 25 |
| média 5.0 → Recuperação; 4.9 → Reprovado | 29, 30, 31–33 |
| presença 0 → Reprovado por falta | 11, 12 |
| presença 100 → Aprovado | 13 |
| presença 75 → Aprovado; 74 → Reprovado por falta | 19, 20, 21–23 |
| média −0.1, −1, 10.1, **10.5** + mensagem | 1, 5 (10.5 > 10 mas não > 11), 6–9 |
| presença −1, **100.5**, 101 + mensagem | 10, 14 (100.5), 15–18 |

Resultado: **36/36 mortos, nenhum equivalente, MS = 100%**, cobertura de ramos 100%.
Nenhum mutante é equivalente: todos mudam a saída para alguma entrada válida da especificação (um valor de fronteira, um valor entre duas constantes inteiras como 10.5, ou a mensagem).

### d) `pytest.raises(ValueError, match=msg)`

Trocando `assert str(exc.value) == "Media invalida"` por `pytest.raises(ValueError, match="Media invalida")`:
**34 mortos, 2 vivos (MS = 94,4%)** — voltam a sobreviver os mutantes **7** (`"XXMedia invalidaXX"`) e **16** (`"XXPresenca invalidaXX"`).

O motivo: `match` aplica `re.search` à mensagem, ou seja, procura o padrão **em qualquer parte** do texto. `"Media invalida"` aparece dentro de `"XXMedia invalidaXX"`, então o teste passa. Os mutantes `None`, minúsculas e maiúsculas continuam mortos, porque a busca diferencia maiúsculas. O oráculo ficou mais fraco: aceita qualquer mensagem que *contenha* o texto.

Correção usada na suíte final: ancorar a regex, `match=r"^Media invalida$"` (ou `re.escape(msg)` com âncoras, se a mensagem tiver metacaracteres). Assim voltamos a **36/36, MS = 100%**.

---

## Exercício 2 — Desconto progressivo

### a) Cobertura e MS da suíte inicial (`assert total_com_desconto([10, 20, 30, 40, 50]) > 0`)

- Cobertura de ramos: **100%** (os dois lados do `if i >= 3` são executados).
- mutmut: **16 gerados, 4 mortos, 12 vivos → MS = 25%**.

Os dois números juntos mostram que a suíte **executa tudo e não verifica quase nada**. A cobertura mede só se o código rodou. O MS mostra que quase qualquer alteração no cálculo (fronteira `>=3`, fator `0.9`, `+=`→`=`, casas do `round`) passa despercebida, porque o oráculo `> 0` só detecta erros que deixam o total negativo ou que estouram exceção (mortos: `total = None`, `enumerate(None)`, `total -= preco*0.9`, `round(None, 2)`).

### b) Assert exato, mesma entrada

`assert total_com_desconto([10, 20, 30, 40, 50]) == 141.0` (10 + 20 + 30 + 36 + 45).
Restam **3 vivos** (13 mortos, MS = 81,25%):

| Mutante | Mudança | Resultado com a entrada |
|---|---|---|
| 13 | `round(total, 2)` → `round(total, None)` | `141` (int) |
| 15 | `round(total, 2)` → `round(total, )` | `141` (int) |
| 16 | `round(total, 2)` → `round(total, 3)` | `141.0` |

### c) Condição que falhou em cada vivo (RIPR)

Os três **alcançam** a mutação, porque o `return` é sempre executado. A diferença está nos passos seguintes:

- **Mutante 16 (`round(total, 3)`) — falha em infectar.** O total é 141.0, que não tem casas decimais. Arredondar para 2 ou para 3 casas dá o mesmo valor, então o estado do programa não fica diferente.
- **Mutantes 13 e 15 (`round(total)`) — falham em revelar.** Aqui há infecção e ela se propaga até a saída: a função devolve `141` (`int`) no lugar de `141.0` (`float`). Mas o oráculo `== 141.0` compara valores numéricos, e `141 == 141.0` é verdadeiro em Python. A diferença está na saída, mas o assert não olha para ela. Do ponto de vista do valor, a falha é a mesma do 16: com um total inteiro, nenhum arredondamento muda nada.

### d) Entrada que faltava

O que faltava era um **preço com centavos que, depois do desconto de 10%, gere uma terceira casa decimal**. Assim o total deixa de ser inteiro e o arredondamento para duas casas passa a ter efeito:

```python
assert total_com_desconto([10, 20, 30, 40.01]) == 96.01   # 40.01 × 0.9 = 36.009 → 96.009
```

Com essa entrada, `round(total)` dá `96`, `round(total, 3)` dá `96.009` e o original dá `96.01`. Os três mutantes morrem: **16/16, MS = 100%**.
Também acrescentei testes das fronteiras do desconto (`[]`, 3 itens, 4 itens). Eles não eram necessários para o MS, mas fixam a regra "do quarto item em diante". A cobertura continuou em 100% o tempo todo: cobertura e escore medem coisas diferentes.

---

## Exercício 3 — Temperaturas da semana

### a) Suíte inicial e vivos (`mutmut show`)

Suíte com `[21, 25, 19, 30, 22]`, `[18]` e `[30, 21]` (valor exato) e lista vazia com `pytest.raises(ValueError)` sem mensagem, para as duas funções.
Cobertura de ramos 100%; mutmut: **22 gerados, 11 mortos, 11 vivos**.

| Vivo | Mudança |
|---|---|
| `maior` 2 | `raise ValueError("lista vazia")` → `ValueError(None)` |
| `maior` 3 | → `ValueError("XXlista vaziaXX")` |
| `maior` 4 | → `ValueError("LISTA VAZIA")` |
| `maior` 7 | `for t in temps[1:]` → `temps[2:]` |
| `maior` 8 | `if t > m` → `if t >= m` |
| `dia_do_maior` 2, 3, 4 | as mesmas três trocas da mensagem |
| `dia_do_maior` 9 | `range(1, len(temps))` → `range(len(temps))` |
| `dia_do_maior` 11 | `range(1, len(temps))` → `range(2, len(temps))` |
| `dia_do_maior` 12 | `if temps[i] > temps[pos]` → `>=` |

### b) Classificação

| Vivo | Classificação | Justificativa |
|---|---|---|
| `maior` 2, 3, 4 e `dia_do_maior` 2, 3, 4 | **Não equivalentes** | A mensagem é parte do comportamento observável; a suíte só não confere o texto. |
| `maior` 7 (`temps[2:]`) | **Não equivalente** | Pula o 2º elemento: `maior([21, 30])` devolveria 21. Nenhuma lista da suíte tem o máximo na 2ª posição. |
| `maior` 8 (`>` → `>=`) | **Equivalente** | Só muda algo quando `t == m`, e então `m` recebe um valor igual ao que já tinha. O valor devolvido é o mesmo para qualquer lista.¹ |
| `dia_do_maior` 9 (`range(len)`) | **Equivalente** | Acrescenta só a iteração `i = 0`, que compara `temps[0] > temps[0]`, sempre falso; `pos` continua 0. É só uma volta a mais no laço. |
| `dia_do_maior` 11 (`range(2, …)`) | **Não equivalente** | Pula o dia 1: `dia_do_maior([21, 30])` devolveria 0 em vez de 1. |
| `dia_do_maior` 12 (`>` → `>=`) | **Não equivalente** | No empate passa a devolver o **último** dia com a maior temperatura: `dia_do_maior([30, 30])` dá 1, mas a especificação pede o primeiro (0). |

¹ A rigor, `>=` troca o objeto por outro igual. Com `[1, 1.0]` o original devolve `1` e o mutante `1.0`, mas `1 == 1.0`. Para a especificação ("a maior temperatura") os dois são a mesma temperatura, então o mutante é equivalente.

### c) Matando os não equivalentes

Testes acrescentados:

- mensagem conferida com `pytest.raises(ValueError, match=r"^lista vazia$")` nas duas funções → mata os 6 mutantes de mensagem (com âncoras, pela lição do ex. 1d);
- `maior([21, 30]) == 30` e `dia_do_maior([21, 30]) == 1` (máximo na 2ª posição) → mata `maior` 7 e `dia_do_maior` 11;
- empate: `dia_do_maior([25, 30, 30]) == 1` e `dia_do_maior([30, 30]) == 0` → mata `dia_do_maior` 12.

| | Mortos | Gerados − equivalentes | MS |
|---|---|---|---|
| Antes | 11 | 22 − 2 = 20 | **55%** (sem descontar equivalentes: 50%) |
| Depois | 20 | 20 | **100%** (sem descontar: 90,9%) |

Ficam vivos só `maior` 8 e `dia_do_maior` 9, os dois equivalentes.

### d) Por que `>` virar `>=` é equivalente numa função e não na outra

O código mutado é o mesmo; o que muda é **o que cada função devolve**:

- `maior` devolve um **valor**. No empate, `>=` substitui o máximo atual por outro de mesmo valor, e o resultado não muda. Não existe entrada que distinga os dois programas, então o mutante é equivalente.
- `dia_do_maior` devolve uma **posição**. No empate, `>=` move `pos` para o índice mais à frente, e dois dias com a mesma temperatura têm posições diferentes. Portanto a saída muda (`[30, 30]` → 1 em vez de 0). E a especificação diz explicitamente "o **primeiro** dia", então essa diferença é um defeito, não uma escolha livre.

A equivalência depende do que a função devolve e do que a especificação exige.

---

## Exercício 4 — Parcelamento

### a) Suíte por valor-limite (derivada antes de rodar ferramentas)

Partições de `n`: inválido (`n < 1`) | sem juros `[1, 3]` | com juros `[4, 12]` | inválido (`n > 12`).
Limites e vizinhos: **0 | 1, 2 | 3 | 4 | 11, 12 | 13**, com `valor = 100`:

| n | Partição | Juros | Total | Esperado |
|---|---|---|---|---|
| 0 | inválido | — | — | `ValueError("parcelas invalidas")` |
| 1 | limite inferior válido | 0 | 100 | 100.0 |
| 2 | vizinho acima | 0 | 100 | 50.0 |
| 3 | último sem juros | 0 | 100 | 33.33 |
| 4 | primeiro com juros | 0,02 | 102 | 25.5 |
| 11 | vizinho abaixo | 0,16 | 116 | 10.55 |
| 12 | limite superior válido | 0,18 | 118 | 9.83 |
| 13 | inválido | — | — | `ValueError("parcelas invalidas")` |

A mensagem é conferida com `match=r"^parcelas invalidas$"`, já ancorada. Os valores 33.33, 10.55 e 9.83 têm dízimas, então também verificam o arredondamento a duas casas.

### b) Cobertura e MS

Cobertura de ramos **100%**; mutmut: **27 gerados, 26 mortos, 1 vivo**.
Sem descontar equivalentes: 26/27 = 96,3%.

### c) Análise do vivo

O único vivo é o **mutante 9: `if n <= 3` → `if n < 3`**. Ele é **equivalente**: a mutação só muda o caminho quando `n == 3`, e nesse caso o ramo `else` calcula `juros = 0.02 * (3 − 3) = 0.0`, exatamente o mesmo juro do ramo `if`. O total e a parcela são iguais. A diferença entre `0` e `0.0` não aparece, porque `total / n` já é `float` nos dois casos. Também conferi empiricamente: comparei original e mutante para 4,8 milhões de combinações (valores inteiros, com centavos e aleatórios em ±10⁶, n de 1 a 12) e não houve nenhuma diferença.

**MS final = 26 / (27 − 1) = 100%**, sem nenhum teste a mais além da suíte de valor-limite.

### d) Mutante de segunda ordem

Combinei dois mutantes de primeira ordem que a suíte mata:

- **mutante 10:** `if n <= 3` → `if n <= 4` (morto pelo teste `n = 4`)
- **mutante 17:** `juros = 0.02 * (n - 3)` → `0.02 * (n - 4)` (morto por `n = 4`, `11` e `12`)

```python
def parcela(valor, n):
    if n < 1 or n > 12:
        raise ValueError("parcelas invalidas")
    if n <= 4:                      # mutante 10
        juros = 0
    else:
        juros = 0.02 * (n - 4)      # mutante 17
    total = valor * (1 + juros)
    return round(total / n, 2)
```

Escolhi esse par de propósito, porque os dois erros "combinam" entre si: juntos formam um programa coerente que implementa outra regra ("sem juros até 4 parcelas, 2% por parcela além da quarta"). É o tipo de engano que um programador faria de verdade.
Para reproduzir: `python segunda_ordem.py 10 17` (dentro de `ex4/`).

### e) A suíte mata o mutante de segunda ordem?

**Sim.** Três testes falham: `n = 4` (25.0 em vez de 25.5), `n = 11` (10.36 em vez de 10.55) e `n = 12` (9.67 em vez de 9.83).
Para ir além de um exemplo, o script também combina **todos** os pares de mutantes mortos em linhas diferentes (`python segunda_ordem.py --todos`): **280 mutantes de segunda ordem, 280 mortos (100%)**.

Isso ilustra o **efeito de acoplamento** (*coupling effect*): uma suíte que distingue todos os defeitos simples também detecta quase todos os defeitos complexos formados pela combinação deles. Para um defeito composto escapar, os dois erros precisariam se mascarar exatamente nas entradas testadas, e isso é raro. No nosso HOM, cada erro sozinho já muda a saída em `n = 4`, e juntos eles não se cancelam.

**Offutt (1992)**, em *Investigations of the Software Testing Coupling Effect* (ACM TOSEM, v. 1, n. 1), testou essa hipótese empiricamente. Ele gerou mutantes de segunda e terceira ordem e mostrou que suítes adequadas aos mutantes de primeira ordem também matavam mais de 99% deles. Esse resultado é a principal justificativa empírica para o teste de mutação usar só mutantes de primeira ordem, como faz o mutmut. O número de mutantes de ordem *k* cresce de forma combinatória (aqui, 280 pares contra 26 mutantes simples), mas testá-los quase não traz informação nova. Nosso experimento reproduz o resultado em pequena escala: 26 FOMs mortos levaram a 280/280 HOMs mortos.

---

## Síntese

1. **Cobertura não mede verificação.** No ex. 2, 100% de ramos conviveu com MS de 25%. No ex. 1, a suíte final tem a mesma cobertura com `==` e com `match` sem âncora, mas um escore diferente.
2. **Primeiro o oráculo, depois as entradas.** O assert exato matou 9 dos 12 vivos do ex. 2. As entradas de fronteira (valores-limite, preço com centavos, empates) mataram o resto.
3. **Equivalência depende da saída e da especificação.** O mesmo `> → >=` é equivalente em `maior` e é defeito em `dia_do_maior`. Um `<= → <` é equivalente em `parcela` porque os dois ramos coincidem em `n = 3`.
4. **Valor-limite já mata quase tudo.** No ex. 4, a suíte derivada só da especificação chegou a 100% sem nenhum ajuste. A mutação serve para mostrar o que ficou de fora; aqui, só um equivalente.

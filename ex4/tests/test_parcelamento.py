import pytest

from parcelamento import parcela

# Suíte derivada por análise de valor-limite (aula 6), antes de rodar ferramentas.
# Partições de n:  inválido (n < 1) | sem juros [1, 3] | com juros [4, 12] | inválido (n > 12)
# Limites testados: 0 | 1, 2 | 3 | 4 | 11, 12 | 13   (valor fixo = 100)
#
#   n   juros   total    parcela = round(total / n, 2)
#   1   0       100      100.0
#   2   0       100      50.0
#   3   0       100      33.33
#   4   0.02    102      25.5
#  11   0.16    116      10.55   (10.5454...)
#  12   0.18    118      9.83    (9.8333...)


@pytest.mark.parametrize("n, esperado", [
    (1, 100.0),    # limite inferior válido
    (2, 50.0),     # logo acima do limite inferior
    (3, 33.33),    # último sem juros
    (4, 25.5),     # primeiro com juros
    (11, 10.55),   # logo abaixo do limite superior
    (12, 9.83),    # limite superior válido
])
def test_parcela_limites_validos(n, esperado):
    assert parcela(100, n) == esperado


@pytest.mark.parametrize("n", [0, 13])   # logo fora de cada limite
def test_parcela_limites_invalidos(n):
    with pytest.raises(ValueError, match=r"^parcelas invalidas$"):
        parcela(100, n)

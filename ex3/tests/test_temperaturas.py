import pytest

from temperaturas import dia_do_maior, maior


# --- suíte inicial ---------------------------------------------------------
@pytest.mark.parametrize("temps, esperado", [
    ([21, 25, 19, 30, 22], 30),
    ([18], 18),
    ([30, 21], 30),
])
def test_maior(temps, esperado):
    assert maior(temps) == esperado


@pytest.mark.parametrize("temps, esperado", [
    ([21, 25, 19, 30, 22], 3),
    ([18], 0),
    ([30, 21], 0),
])
def test_dia_do_maior(temps, esperado):
    assert dia_do_maior(temps) == esperado


@pytest.mark.parametrize("funcao", [maior, dia_do_maior])
def test_lista_vazia(funcao):
    with pytest.raises(ValueError):
        funcao([])


# --- testes acrescentados (item c) -----------------------------------------
# Mensagem exata (ancorada): mata ValueError(None), "XX...XX" e "LISTA VAZIA"
# nas duas funções (maior 2-4, dia_do_maior 2-4)
@pytest.mark.parametrize("funcao", [maior, dia_do_maior])
def test_lista_vazia_mensagem(funcao):
    with pytest.raises(ValueError, match=r"^lista vazia$"):
        funcao([])


# Maior na 2ª posição: mata temps[2:] (maior 7) e range(2, ...) (dia_do_maior 11)
def test_maior_na_segunda_posicao():
    assert maior([21, 30]) == 30


def test_dia_do_maior_na_segunda_posicao():
    assert dia_do_maior([21, 30]) == 1


# Empate: a especificação pede o PRIMEIRO dia com a maior temperatura.
# Mata temps[i] >= temps[pos] (dia_do_maior 12)
def test_dia_do_maior_empate_devolve_primeiro():
    assert dia_do_maior([25, 30, 30]) == 1
    assert dia_do_maior([30, 30]) == 0


# Equivalentes (não há teste que os mate):
#   maior 8          t > m  ->  t >= m        : no empate, m recebe o mesmo valor
#   dia_do_maior 9   range(1, n) -> range(n)  : i = 0 compara temps[0] > temps[0], sempre falso

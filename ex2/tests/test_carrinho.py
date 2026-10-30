import pytest

from carrinho import total_com_desconto


def test_total_exato():
    # item (b): só o assert mudou. 10 + 20 + 30 + 40*0.9 + 50*0.9 = 141.0
    assert total_com_desconto([10, 20, 30, 40, 50]) == 141.0


# --- item (d): entradas que faltavam ---------------------------------------
def test_preco_com_centavos():
    # 40.01 * 0.9 = 36.009 -> total 96.009 -> 96.01 com duas casas.
    # Mata round(total, None) e round(total) (dariam 96) e round(total, 3) (96.009)
    assert total_com_desconto([10, 20, 30, 40.01]) == 96.01


# Fronteiras do desconto (não eram necessárias para o MS, mas fixam a especificação)
@pytest.mark.parametrize("precos, esperado", [
    ([], 0),                       # carrinho vazio
    ([10, 20, 30], 60),            # 3º item ainda sem desconto
    ([10, 20, 30, 40], 96.0),      # 4º item é o primeiro com desconto
])
def test_fronteira_do_desconto(precos, esperado):
    assert total_com_desconto(precos) == esperado

import pytest

from classificacao import classificar_aluno


# --- suíte inicial ---------------------------------------------------------
def test_aprovado():
    assert classificar_aluno(8.0, 80) == "Aprovado"


def test_reprovado():
    assert classificar_aluno(3.0, 90) == "Reprovado"


# --- testes acrescentados (item c) -----------------------------------------
# Fronteiras de média válidas: 0 e 10 são aceitas
@pytest.mark.parametrize("media, esperado", [
    (0, "Reprovado"),        # mata media <= 0 (2) e media < 1 (3)
    (0.5, "Reprovado"),      # mata media < 1 (3)
    (10, "Aprovado"),        # mata media >= 10 (4)
    (7.0, "Aprovado"),       # mata media > 7.0 (24) e media >= 8.0 (25)
    (6.9, "Recuperacao"),    # vizinho abaixo de 7
    (5.0, "Recuperacao"),    # mata media > 5.0 (29) e >= 6.0 (30); retorno (31-33)
    (4.9, "Reprovado"),      # vizinho abaixo de 5
])
def test_fronteiras_media(media, esperado):
    assert classificar_aluno(media, 80) == esperado


# Fronteiras de presença válidas
@pytest.mark.parametrize("presenca, esperado", [
    (0, "Reprovado por falta"),    # mata presenca <= 0 (11) e < 1 (12)
    (100, "Aprovado"),             # mata presenca >= 100 (13)
    (75, "Aprovado"),              # mata presenca <= 75 (19) e < 76 (20)
    (74, "Reprovado por falta"),   # vizinho abaixo de 75; retorno (21-23)
])
def test_fronteiras_presenca(presenca, esperado):
    assert classificar_aluno(8.0, presenca) == esperado


# Média inválida: -0.1 e 10.5 (10.5 mata media > 11, mutante 5)
# match usa re.search: sem ^...$ os mutantes "XX...XX" (7 e 16) sobrevivem
@pytest.mark.parametrize("media", [-0.1, -1, 10.1, 10.5])
def test_media_invalida(media):
    with pytest.raises(ValueError, match=r"^Media invalida$"):
        classificar_aluno(media, 80)


# Presença inválida: -1, 100.5 e 101 (100.5 mata presenca > 101, mutante 14)
@pytest.mark.parametrize("presenca", [-1, 100.5, 101])
def test_presenca_invalida(presenca):
    with pytest.raises(ValueError, match=r"^Presenca invalida$"):
        classificar_aluno(8.0, presenca)

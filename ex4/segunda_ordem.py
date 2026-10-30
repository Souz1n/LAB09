"""Exercício 4 (d/e): mutantes de segunda ordem montados à mão.

Uso (dentro de ex4/):
    python segunda_ordem.py            # roda o HOM escolhido (mutantes 10 + 17)
    python segunda_ordem.py 4 26       # combina outros dois mutantes pelo número do mutmut
    python segunda_ordem.py --todos    # varre todos os pares de mutantes mortos em linhas diferentes

Os números são os mesmos de `mutmut show parcelamento.x_parcela__mutmut_N`.
"""
import itertools
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# Mutantes de primeira ordem gerados pelo mutmut 3.8.0: (número, linha, original, mutado)
FOMS = {
    1: (2, "    if n < 1 or n > 12:", "    if n < 1 and n > 12:"),
    2: (2, "    if n < 1 or n > 12:", "    if n <= 1 or n > 12:"),
    3: (2, "    if n < 1 or n > 12:", "    if n < 2 or n > 12:"),
    4: (2, "    if n < 1 or n > 12:", "    if n < 1 or n >= 12:"),
    5: (2, "    if n < 1 or n > 12:", "    if n < 1 or n > 13:"),
    6: (3, '        raise ValueError("parcelas invalidas")', "        raise ValueError(None)"),
    7: (3, '        raise ValueError("parcelas invalidas")', '        raise ValueError("XXparcelas invalidasXX")'),
    8: (3, '        raise ValueError("parcelas invalidas")', '        raise ValueError("PARCELAS INVALIDAS")'),
    9: (4, "    if n <= 3:", "    if n < 3:"),  # equivalente
    10: (4, "    if n <= 3:", "    if n <= 4:"),
    11: (5, "        juros = 0", "        juros = None"),
    12: (5, "        juros = 0", "        juros = 1"),
    13: (7, "        juros = 0.02 * (n - 3)", "        juros = None"),
    14: (7, "        juros = 0.02 * (n - 3)", "        juros = 0.02 / (n - 3)"),
    15: (7, "        juros = 0.02 * (n - 3)", "        juros = 1.02 * (n - 3)"),
    16: (7, "        juros = 0.02 * (n - 3)", "        juros = 0.02 * (n + 3)"),
    17: (7, "        juros = 0.02 * (n - 3)", "        juros = 0.02 * (n - 4)"),
    18: (8, "    total = valor * (1 + juros)", "    total = None"),
    19: (8, "    total = valor * (1 + juros)", "    total = valor / (1 + juros)"),
    20: (8, "    total = valor * (1 + juros)", "    total = valor * (1 - juros)"),
    21: (8, "    total = valor * (1 + juros)", "    total = valor * (2 + juros)"),
    22: (9, "    return round(total / n, 2)", "    return round(None, 2)"),
    23: (9, "    return round(total / n, 2)", "    return round(total / n, None)"),
    24: (9, "    return round(total / n, 2)", "    return round(2)"),
    25: (9, "    return round(total / n, 2)", "    return round(total / n, )"),
    26: (9, "    return round(total / n, 2)", "    return round(total * n, 2)"),
    27: (9, "    return round(total / n, 2)", "    return round(total / n, 3)"),
}
EQUIVALENTES = {9}


def montar(ids):
    """Aplica os mutantes `ids` (em linhas diferentes) ao código original."""
    linhas = (AQUI / "src" / "parcelamento.py").read_text().splitlines()
    usadas = set()
    for k in ids:
        ln, original, mutado = FOMS[k]
        if ln in usadas:
            raise ValueError(f"mutantes na mesma linha ({ln}) não se combinam")
        assert linhas[ln - 1] == original, f"linha {ln} não confere"
        linhas[ln - 1] = mutado
        usadas.add(ln)
    return "\n".join(linhas) + "\n"


def rodar(ids, verboso=True):
    """Roda a suíte contra o mutante; devolve a lista de testes que falharam."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "src").mkdir()
        (tmp / "src" / "parcelamento.py").write_text(montar(ids))
        shutil.copytree(AQUI / "tests", tmp / "tests")
        shutil.copy(AQUI / "pyproject.toml", tmp / "pyproject.toml")
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-rf", "-p", "no:cacheprovider"],
            cwd=tmp, capture_output=True, text=True,
        )
        falhas = [l.split(" ")[1] for l in r.stdout.splitlines() if l.startswith("FAILED")]
        if verboso:
            print(montar(ids))
            print("\n".join(falhas) or "nenhum teste falhou")
        return falhas


def todos():
    mortos = [k for k in FOMS if k not in EQUIVALENTES]
    pares = [(a, b) for a, b in itertools.combinations(mortos, 2) if FOMS[a][0] != FOMS[b][0]]
    vivos = [p for p in pares if not rodar(p, verboso=False)]
    print(f"pares de mutantes mortos em linhas diferentes: {len(pares)}")
    print(f"mortos pela suíte: {len(pares) - len(vivos)}  |  vivos: {len(vivos)} {vivos}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--todos"]:
        todos()
    else:
        ids = [int(a) for a in sys.argv[1:]] or [10, 17]
        falhas = rodar(ids)
        print(f"\nHOM {'+'.join(map(str, ids))}: {'MORTO' if falhas else 'VIVO'} "
              f"({len(falhas)} teste(s) falharam)")

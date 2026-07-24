# Optimal Betting — optimální sázková strategie

Zápočtový projekt (MFF UK). Řeší klasický problém typu *gambler's ruin*
s volitelnou velikostí sázky: hráč začíná s kapitálem $C₀$ a chce v nejvýše
$N$ kolech dosáhnout cílového kapitálu $T$. V každém kole vsadí libovolnou
celočíselnou částku ze svého aktuálního kapitálu. S pravděpodobností $p$
sázku vyhraje a získá $b·(r−1)$, kde $r$ je výplatní poměr (*payout ratio*),
s pravděpodobností $1−p$ sázku prohraje a přijde o vsazenou částku. Hra
končí, jakmile hráč dosáhne kapitálu $≥ T$ (výhra), klesne na $0$ (bankrot),
nebo dojdou kola.

Cílem projektu je najít strategii sázení, která maximalizuje
pravděpodobnost dosažení cíle $T$ pomocí dynamického
programování), porovnat ji s několika heuristickými strategiemi pomocí
Monte Carlo simulací a výsledky zobrazit v interaktivní webové aplikaci.

Kompletní dokumentace je v `optimal_betting_dokumentace.docx`.

## Instalace

Vyžadován **Python 3.9+**

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` obsahuje knihovny s verzemi

## Spuštění

```bash
streamlit run app.py
```

V postranním panelu se nastaví parametry hry (kapitál, cíl, počet kol,
pravděpodobnost výhry, výplatní poměr, ...), tlačítko spustí DP výpočet
a Monte Carlo simulace všech strategií a výsledky se zobrazí jako
srovnávací tabulka metrik, grafy trajektorií kapitálu a prohledávatelná
mapa optimálních sázek.

## Struktura

- `core/models.py` — `StateSpace`, neměnný stav (kapitál, zbývající kola)
- `core/solver.py` — `BettingSolver`, Bellmanova rekurze s přesnou
  aritmetikou (`Fraction`) a memoizací
- `core/betting_map.py` — předpočítání kompletní mapy optimálních sázek
- `core/strategies/` — DP, restricted DP (hybrid), cautious, bold,
  proportional, Kelly — společné rozhraní `get_bet(state)`
- `core/main.py` — Monte Carlo simulace a agregace metrik
- `app.py` — Streamlit frontend *(generováno pomocí AI)*
- `tests/test_solver.py` — jednotkové testy solveru

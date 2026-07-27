
# Dokumentace programu: Optimal Betting Strategy

## 1. Zadání problému

Projekt se zabývá klasickým problémem *Gambler's ruin* zobecněným o volitelnou výši sázky a omezený časový horizont.

Hráč začíná s počátečním kapitálem $C_0 \in \mathbb{N}$ a jeho cílem je v nejvýše $N$ kolech dosáhnout cílového kapitálu
$T \in \mathbb{N}$ ($T > C_0$). V každém kole $k$ vsadí celočíselnou částku $b \in \{1, 2, \dots, C_k\}$. S pravděpodobností $p$ sázku vyhraje a jeho kapitál se změní na $C_k + b \cdot (r - 1)$, kde $r > 1, r \in \mathbb{Q}$ je výplatní poměr (*payout ratio*). S pravděpodobností $1 - p$ sázku prohraje a zůstane mu $C_k - b$. Hra končí okamžitě, jakmile hráč dosáhne $C_k \ge T$ (výhra), $C_k = 0$ (bankrot), nebo odehraje $N$ kol.

**Cíle projektu:**

* **Přesné DP řešení:** Pomocí dynamického programování naleznout striktně optimální strategii sázení, která maximalizuje pravděpodobnost dosažení cíle $T$.
* **Porovnání s heuristikami:** Srovnat výsledky DP vůči 5 heuristikám pomocí Monte Carlo simulací.
* **Vizualizace:** Vytvořit interaktivní webovou aplikaci pro analytický vhled do vypočtených strategií a průběhů her.

---

## 2. Uživatelská příručka

### Požadavky a spuštění

Aplikace vyžaduje `Python >= 3.10` a knihovny uvedené v `requirements.txt`.

1. Instalace závislostí: `pip install -r requirements.txt`
2. Spuštění aplikace: `streamlit run app.py`

### Ovládání aplikace

Všechny parametry simulace se nastavují v levém postranním panelu:

* **Kapitál:** Počáteční $C_0$ a cílový $T$.
* **Omezení:** Počet kol $N$.
* **Pravděpodobnosti a výplaty:** Pravděpodobnost $p$ a výplatní poměr $r$ (zadávají se jako zlomky, např. $1/2$, $2/1$, pro zachování absolutní přesnosti).
* **Strategie:** Parametr pro proporcionální strategii (% kapitálu) a počet Monte Carlo simulací (např. 10 000).
* **Determinismus DP:** Přepínač *„Preferovat větší sázky“* určuje chování DP při remíze (kdy dvě různé sázky dají identickou pravděpodobnost výhry).

Aplikace okamžitě vyhodnocuje střední hodnotu jedné sázky $EV = p \cdot r - 1$ a indikuje, zda jde o férovou, výhodnou nebo nevýhodnou hru.

### Výstupy

* **Srovnávací tabulka:** Pro všech 6 strategií zobrazuje *Win Rate*, *Pravděpodobnost bankrotu*, *Očekávaný finální kapitál* a jeho *Směrodatnou odchylku*.
* **Interaktivní graf (Plotly):** Trajektorie vývoje kapitálu v prvních 50 simulovaných hrách vybrané strategie.
* **Mapa sázek (DP Table):** Kompletní lookup tabulka zobrazující pro každý stav $(C, N_{\text{left}})$ optimalizovanou sázku a teoretickou pravděpodobnost výhry. Obsahuje filtr podle zbývajících kol.

---

## 3. Programátorská část

### Architektura

Kód projektu je důsledně rozdělen na **algoritmické jádro**, **testy** a **prezentační vrstvu**:

* **`core/`**
* `models.py` – Datové struktury (`StateSpace`)
* `solver.py` – Bellmanova rekurze a přesný DP solver v `Fraction`
* `betting_map.py` – Generátor kompletní stavové mapy
* `main.py` – Monte Carlo simulační engine
* `strategies/` – Implementace 6 strategií sázení


* **`tests/`** 
* `test_solver.py` – Pytest testovací sada pro solver


* **`app.py`** *(Generováno pomocí AI)*

> **využití AI:**
> Soubor `app.py` tvořící uživatelské rozhraní (Streamlit komponenty, Plotly grafy a styling) byl vygenerován za použití **AI** na základě specifikace rozhraní dodané z modulu `core/`.

---

### Hlavní komponenty a datové struktury

#### `core/models.py`

Stav hry je reprezentován pomocí `StateSpace` (dataclass s atributy `capital: Fraction` a `rounds_left: int`). Třída je definována jako `@dataclass(frozen=True)`, to zajišťuje immutabilitu a hashovatelnost, stavy pak slouží jako klíče v `dict` pro memoizaci.

#### `core/solver.py` – `BettingSolver`

Jádrem je Bellmanova rekurze nad diskrétním stavovým prostorem. Veškeré výpočty pravděpodobností probíhají v **racionální aritmetice** přes modul `fractions.Fraction`. Tím je dosaženo toho, že nedochází k zaokrouhlovacím chybám (floating-point).

Funkce $P(C, k)$ označuje maximální pravděpodobnost dosažení cíle $T$ z kapitálu $C$ v $k$ krocích:

* **Bázové stavy:**

$$P(C, k) = 1 \quad \text{pro } C \ge T$$


$$P(C, k) = 0 \quad \text{pro } C \le 0 \text{ nebo } k = 0 \quad (\text{pokud } C < T)$$


* **Rekurzivní krok:**

$$P(C, k) = \max_{b \in B(C)} \left( p \cdot P(C + b(r-1), k-1) + (1-p) \cdot P(C - b, k-1) \right)$$



**Ořezávání stavového prostoru:**
Množina přípustných sázek $B(C)$ je shora omezená hodnotou $\min(C, b_{\max})$, kde:


$$b_{\max} = \left\lceil \frac{T - C}{r - 1} \right\rceil$$


Sázet více, než je nutné k dosažení cíle $T$ při jediné výhře, není optimální. Toto ořezání zásadně zrychluje výpočet rekurze.

#### `core/strategies/`

Všechny strategie implementují jednotné rozhraní `get_bet(state) -> int`:

1. `DPStrategy`: Používá předpočítanou mapu z `BettingSolver`.
2. `DPModStrategy`: *Restricted DP* heuristika. Zmenšuje prohledávaný prostor sázek pouze na kandidáty nabízené strategiemi Cautious, Bold a Kelly. Vybere tu, která v DP mapě dává nejvyšší pravděpodobnost úspěchu.
3. `CautiousStrategy`: Vždy sází $b = 1$.
4. `BoldStrategy`: Sází $b = \min(C, b_{\max})$ (snaha dosáhnout $T$ v nejmenším počtu kroků).
5. `ProportionalStrategy`: Sází $b = \lfloor \alpha \cdot C \rfloor$.
6. `KellyStrategy`: Sází podle diskrétního Kellyho kritéria $f^* = \frac{p \cdot r - 1}{r - 1}$, přizpůsobeného na celočíselné sázky a omezení $T$.

#### `core/main.py`

Metoda `get_monte_carlo_stats` spouští $M$ nezávislých průchodů pro každou strategii a sbirá statistky (Win Rate, Bankruptcy Rate, Mean, StdDev).

---

### Složitost a paměťové nároky

* **Časová složitost solveru:** V nejhorším případě $\mathcal{O}(N \cdot T^2)$, díky ořezávání $b_{\max}$ a memoizaci je v výrazně nižší (blízko $\mathcal{O}(N \cdot T \log T)$).
* **Paměťová složitost:** $\mathcal{O}(N \cdot T)$ pro uložení výsledků v memoizační tabulce.

---

### Testování (`tests/test_solver.py`)

Kód obsahuje sadu jednotkových testů v `pytest`. Testují se:

* Okrajové podmínky (kapitál $0$, dosažení $T$, $N=0$).
* Malé ručně dopočítané stromy rozhodování.
* Korektnost přepínače `prefer_larger_bets` při rozstřelu shodných pravděpodobností.
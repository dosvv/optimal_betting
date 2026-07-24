# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as object_plots
from fractions import Fraction

# Import tvé simulační logiky (přesně podle tvé verze)
from core.main import get_monte_carlo_stats

# Import všech tvých strategií
from core.solver import BettingSolver
from core.betting_map import BettingMapGenerator
from core.strategies.bold import BoldStrategy
from core.strategies.cautious import CautiousStrategy
from core.strategies.DP import DPStrategy
from core.strategies.DP_modified import DPModStrategy
from core.strategies.kelly import KellyStrategy
from core.strategies.proportion import ProportionalStrategy

# Nastavení stránky na široké zobrazení
st.set_page_config(layout="wide", page_title="Optimal Betting Simulator")

st.title("📊 Optimal Betting Strategy Simulator")
st.markdown(
    "Tato aplikace porovnává teoreticky optimální strategii (Dynamické programování) s heuristickými sázkovými strategiemi pomocí Monte Carlo simulací.")

st.divider()

# --- BOČNÍ PANEL S PARAMETRY ---
st.sidebar.header("⚙️ Parametry hry")

init_capital = st.sidebar.number_input("Počáteční kapitál ($C_0$)", min_value=1, max_value=500, value=5)
target = st.sidebar.number_input("Cílový kapitál ($T$)", min_value=init_capital + 1, max_value=1000, value=max(int(init_capital) + 5, 10))
total_rounds = st.sidebar.number_input("Celkový počet kol ($N$)", min_value=1, max_value=50, value=5)

st.sidebar.subheader("Pravděpodobnost výhry")
p_num = st.sidebar.number_input("Čitatel šance na výhru", min_value=1, max_value=100, value=55)
p_den = st.sidebar.number_input("Jmenovatel šance na výhru", min_value=1, max_value=100, value=100)
prob_win = Fraction(p_num, p_den)

st.sidebar.subheader("Výplatní poměr (Payout Ratio)")
r_num = st.sidebar.number_input("Čitatel výplatního poměru", min_value=1, max_value=100, value=2)
r_den = st.sidebar.number_input("Jmenovatel výplatního poměru", min_value=1, max_value=100, value=1)
payout_ratio = Fraction(r_num, r_den)

st.sidebar.subheader("Nastavení strategií")
prop_percentage = st.sidebar.slider("Procento pro Proporcionální strategii (%)", min_value=1, max_value=100, value=20,
                                    step=1)

num_sim = st.sidebar.slider("Počet Monte Carlo simulací", min_value=1000, max_value=50000, value=10000, step=1000)

# TOGGLE: Preferovat větší sázky při shodě pravděpodobností v DP
prefer_larger = st.sidebar.toggle("Preferovat větší sázky (DP)", value=True,
                                  help="Pokud mají dvě různé sázky stejnou pravděpodobnost dosažení cíle, DP vybere tu větší (agresivnější).")

# Informační box o výhodě hry (Edge)
edge = float(prob_win * payout_ratio) - 1
if edge > 0:
    st.sidebar.success(f"Hra má pozitivní EV pro hráče (Edge: +{edge * 100:.1f}%)")
elif edge < 0:
    st.sidebar.error(f"Hra má negativní EV pro hráče (Edge: {edge * 100:.1f}%)")
else:
    st.sidebar.warning("Hra je matematicky férová (Edge: 0%)")

# --- SPANÍ A UKLÁDÁNÍ STAVU (SESSION STATE) ---
if st.sidebar.button("🚀 Spustit analýzu a simulace", use_container_width=True):
    with st.spinner("1️⃣ Krok: Počítám Dynamické programování (Zpětná rekurze)..."):
        solver = BettingSolver(target, total_rounds, prob_win, payout_ratio, prefer_larger_bets=prefer_larger)
        generator = BettingMapGenerator(solver)
        full_map = generator.generate()

        # Uložení mapy do session state pro zobrazení tabulky níže
        st.session_state["full_map"] = full_map

    with st.spinner("2️⃣ Krok: Spouštím Monte Carlo simulace strategií..."):
        # PŘESUNUTO: Full DP a Restricted DP jsou nyní na prvním místě nahoře
        strategies_list = [
            (DPStrategy(full_map), "Full DP (Absolutní optimum)"),
            (DPModStrategy(full_map, target, prob_win, payout_ratio, prefer_larger), "Restricted DP (Hybrid)"),
            (CautiousStrategy(target), "Timid Play (Fixní 1)"),
            (BoldStrategy(target, payout_ratio), "Bold Play"),
            (ProportionalStrategy(target, percentage=prop_percentage), f"Proporcionální ({prop_percentage} %)"),
            (KellyStrategy(target, payout_ratio, prob_win), "Kellyho kritérium")
        ]

        # Uložení výsledků do session_state
        st.session_state["dataset"] = get_monte_carlo_stats(
            strategies=strategies_list,
            num_sim=num_sim,
            init_capital=Fraction(init_capital),
            target=target,
            total_rounds=total_rounds,
            prob_win=prob_win,
            payout_ratio=payout_ratio
        )
        st.session_state["calculated"] = True

# --- RENDER VÝSTUPŮ ---
if st.session_state.get("calculated", False):
    dataset = st.session_state["dataset"]

    # ZOBRAZENÍ TABULKY METRIK
    st.subheader("📊 Srovnávací analýza metrik")

    table_data = []
    for name, content in dataset.items():
        metrics = content["stat"]
        table_data.append({
            "Strategie": name,
            "Win Rate (%)": f"{metrics['win_rate'] * 100:.2f}%",
            "Risk of Ruin (%)": f"{metrics['ruin_rate'] * 100:.2f}%",
            "Očekávaná hodnota (EV)": f"{metrics['expected_value']:.3f}",
            "Směrodatná odchylka": f"{metrics['std_dev']:.3f}"
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.divider()

    # INTERAKTIVNÍ GRAFY TRAJEKTORIÍ
    st.subheader("📈 Vizualizace vývoje kapitálu (Prvních 50 trajektorií)")

    # Full DP se díky pořadí v poli vybere automaticky jako první defaultní volba
    selected_strategy = st.selectbox("Zvol strategii pro zobrazení vývoje her:", list(dataset.keys()))

    histories_to_plot = dataset[selected_strategy]["data"]["histories"][:50]

    fig = object_plots.Figure()

    for i, history in enumerate(histories_to_plot):
        fig.add_trace(object_plots.Scatter(
            x=list(range(len(history))),
            y=history,
            mode='lines+markers',
            name=f"Hra {i + 1}",
            opacity=0.4,
            line=dict(width=1.5)
        ))

    fig.update_layout(
        xaxis_title="Odehraná kola",
        yaxis_title="Aktuální kapitál ($)",
        yaxis=dict(range=[-0.5, target + 1.5]),
        margin=dict(l=20, r=20, t=20, b=20),
        height=500,
        showlegend=False
    )

    fig.add_hline(y=target, line_dash="dash", line_color="green", annotation_text="Cíl (Target)")
    fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Bankrot (Ruin)")

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- NOVÁ SEKCE: VYPISOVÁNÍ MAPY SÁZEK ---
    st.subheader("🗺️ Mapa optimálních sázek (Vygenerováno pomocí DP)")
    st.markdown(
        "Přehled optimálních sázek a pravděpodobností úspěchu pro jednotlivé stavy (kapitál vs. zbývající kola) vypočítaných Bellmanovou rekurzí.")

    full_map = st.session_state["full_map"]

    map_rows = []
    for state, (prob, best_bet) in full_map.items():
        # Filtrujeme pouze aktivní stavy hry (nad nulou, pod cílem, a když zbývají kola)
        if 0 < state.capital < target and state.rounds_left > 0:
            map_rows.append({
                "Zbývající kola": int(state.rounds_left),
                "Aktuální Kapitál": float(state.capital),
                "Optimální sázka": int(best_bet),
                "Pravděpodobnost výhry z tohoto stavu": f"{float(prob) * 100:.2f}%"
            })

    if map_rows:
        df_map = pd.DataFrame(map_rows)
        # Seřadíme sestupně podle kol a vzestupně podle kapitálu pro logické čtení
        df_map = df_map.sort_values(by=["Zbývající kola", "Aktuální Kapitál"], ascending=[False, True])

        # Filtr pro zobrazení konkrétního kola
        available_rounds = sorted(df_map["Zbývající kola"].unique(), reverse=True)
        selected_round_filter = st.selectbox("Filtrovat mapu podle zbývajících kol:",
                                             ["Zobrazit vše"] + list(available_rounds))

        if selected_round_filter != "Zobrazit vše":
            df_filtered = df_map[df_map["Zbývající kola"] == selected_round_filter]
            st.dataframe(df_filtered, hide_index=True, use_container_width=True)
        else:
            st.dataframe(df_map, hide_index=True, use_container_width=True)
    else:
        st.info("Pro zadané parametry nebyla vygenerována žádná aktivní sázková mapa.")

else:
    st.info(
        "👈 Pro zobrazení výsledků nastav parametry v levém panelu a klikni na tlačítko **Spustit analýzu a simulace**.")
import json
import math
from collections import Counter

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from helpers import roll_page_layout, get_base64_of_bin_file
from plotly.subplots import make_subplots


XP_TO_NEXT_LEVEL = {3: 6, 4: 10, 5: 20, 6: 36, 7: 48, 8: 76, 9: 80, 10: 100}


def main():
    data = pd.read_csv("static_data/tier_stats.csv", header=0, index_col=0)
    chosen_data = pd.read_csv(
        "static_data/chosen_tier_stats.csv", header=0, index_col=0
    )

    with open("static_data/champions_10.json", "r") as file:
        traits = pd.DataFrame(json.load(file))

    (
        names,
        costs,
        trait_odds,
        level,
        n_champs,
        n_costs,
        chosen_odds,
        gold,
        show_next_level,
    ) = select_params_chosen(data, chosen_data, traits)

    if not names:
        # st.subheader("Select champion(s) in the settings")
        bin_str = get_base64_of_bin_file("assets/tft_t_logo.png")
        subheader = f"""
        <a src="assets/tft_t_logo.png" style="text-decoration: none; cursor: default; font-weight:600; color: white;"> <img src="data:image/png;base64,{bin_str}" width=40>
        Select desired Headliner(s) in the settings</a>"""
        st.markdown(subheader, unsafe_allow_html=True)
        draw_chart([0], [], level, gold, False, [0])
        return

    probs, probs_next_lvl = [], []
    for cost, n_champ, n_cost, trait_odd in zip(costs, n_champs, n_costs, trait_odds):
        data_cost = data[str(cost)]
        prob = trait_odd * (chosen_data.iloc[level - 1].iloc[cost - 1] / 100)
        probs.append(
            (data_cost["pool"] - n_champ)
            / (data_cost["n_champs"] * data_cost["pool"] - n_cost - n_champ)
            * chosen_odds
            * prob
        )
        if level < 10:
            prob_next_lvl = trait_odd * (chosen_data.iloc[level].iloc[cost - 1] / 100)
            probs_next_lvl.append(
                (data_cost["pool"] - n_champ)
                / (data_cost["n_champs"] * data_cost["pool"] - n_cost - n_champ)
                * chosen_odds
                * prob_next_lvl
            )

    draw_chart(probs, names, level, gold, show_next_level, probs_next_lvl)


def select_params_chosen(data, chosen_data, traits):
    # Level
    level = st.sidebar.slider(
        "Level",
        value=7,
        min_value=3,
        max_value=10,
    )

    # Gold
    gold = st.sidebar.slider("Gold", value=100, min_value=1, max_value=150)

    chosen_odds = list(chosen_data.iloc[level - 1])
    # available_costs = [i + 1 for i in range(5) if chosen_odds[i] > 0]
    # available_traits = traits[traits["cost"].isin(available_costs)]

    has_chosen = st.sidebar.checkbox("Already possess an Headliner?")
    show_next_level = st.sidebar.checkbox("Show next level odds?")

    champs = st.sidebar.multiselect(
        "Desired Headliner(s)",
        build_champ_select(traits, level),
    )
    champions = [champ.split(" - ")[0] for champ in champs]

    # names, costs, traits_odds = build_champ_info(champions, available_traits)
    names, costs, traits_odds = build_champ_info(champions, traits)

    n_champs = []
    for champ, cost in zip(names, costs):
        # Number of cards of the champion already bought
        nb_copies = data[str(cost)]["pool"]
        n_champs.append(
            st.sidebar.number_input(
                "Number of copies of %s already out" % champ,
                value=3,
                min_value=0,
                max_value=nb_copies,
            )
        )

    n_costs = {}
    for cost in np.unique(costs):
        # Number of cards of same cost already bought
        n_costs[str(cost)] = st.sidebar.number_input(
            f"Number of {cost} cost champions already out (excluding your champion)",
            value=25,
            min_value=0,
            max_value=300,
        )

    chosen_odds = 1 if not has_chosen else 0.25

    n_costs = [n_costs[str(cost)] for cost in costs]

    return (
        names,
        costs,
        traits_odds,
        level,
        n_champs,
        n_costs,
        chosen_odds,
        gold,
        show_next_level,
    )


def draw_chart(probs, names, level, gold, show_next_level, probs_next_lvl=[0]):
    gold_to_next_lvl = XP_TO_NEXT_LEVEL[level]
    any_headliners = []
    if len(names) > 1:
        prob = np.prod([1 - p for p in probs])
        any_headliners = [
            {
                "name": "Any Headliner",
                "Probability": (1 - prob**i) * 100,
                "Golds spent": i,
            }
            for i in range(0, gold, 2)
        ]
        if gold_to_next_lvl < gold and show_next_level:
            prob_next_lvl = np.prod([1 - p for p in probs_next_lvl])

            any_headliners += [
                {
                    "name": f"Any Headliner_lvl_{level + 1}",
                    "Probability": 0,
                    "Golds spent": i,
                }
                for i in range(0, gold_to_next_lvl, 2)
            ]
            any_headliners += [
                {
                    "name": f"Any Headliner_lvl_{level + 1}",
                    "Probability": (1 - prob_next_lvl ** (i - gold_to_next_lvl)) * 100,
                    "Golds spent": i,
                }
                for i in range(gold_to_next_lvl, gold, 2)
            ]

    headliners = any_headliners
    for i, (prob, name) in enumerate(zip(probs, names)):
        headliners += [
            {
                "name": name,
                "Probability": (1 - (1 - prob) ** i) * 100,
                "Golds spent": i,
            }
            for i in range(0, gold, 2)
        ]

    if gold_to_next_lvl < gold and show_next_level:
        for i, (prob, name) in enumerate(zip(probs_next_lvl, names)):
            headliners += [
                {
                    "name": name + f"_lvl_{level + 1}",
                    "Probability": 0,
                    "Golds spent": i,
                }
                for i in range(0, gold_to_next_lvl, 2)
            ]
            headliners += [
                {
                    "name": name + f"_lvl_{level + 1}",
                    "Probability": (1 - (1 - prob) ** (i - gold_to_next_lvl)) * 100,
                    "Golds spent": i,
                }
                for i in range(gold_to_next_lvl, gold, 2)
            ]

    df = pd.DataFrame(headliners)
    if not df.empty:
        fig = px.line(
            df,
            y="Probability",
            x="Golds spent",
            title="Odds to find one of the desired Headliners",
            color="name",
        )
        fig.update_layout(
            yaxis=dict(range=[0, 100]),
            height=600,
            width=1000,
            xaxis={"tickmode": "linear", "dtick": 4, "range": [0, gold]},
            hovermode="x",
            title_x=0.4,
            legend_title=None,
        )
        fig.update_traces(
            hovertemplate="Probability: <b>%{y:.2f}</b>%<br>Golds spent: <b>%{x}</b>",
            text="",
            mode="lines",
        )

        st.write(fig)


def build_champ_select(traits, level):
    out = []
    for row in traits.iterrows():
        for trait in row[1]["chosen_traits"]:
            out.append(row[1]["name"] + " - " + trait)

    return out


def build_champ_info(champions, traits):
    names = []
    costs = []
    traits_odds = []

    for champ, count in Counter(champions).items():
        names.append(champ)
        costs.append(traits.loc[traits.name == champ, "cost"].item())
        traits_odds.append(
            count / len(traits.loc[traits.name == champ, "chosen_traits"].item())
        )
    return names, costs, traits_odds

import json
import math
from collections import Counter

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from helpers import roll_page_layout, get_base64_of_bin_file
from plotly.subplots import make_subplots


def main():
    data = pd.read_csv("tier_stats.csv", header=0, index_col=0)
    chosen_data = pd.read_csv("chosen_tier_stats.csv", header=0, index_col=0)

    with open("champions.json", "r") as file:
        traits = pd.DataFrame(json.load(file))

    (
        names,
        tiers,
        trait_ratio,
        level,
        n_champs,
        n_tiers,
        chosen_odds,
    ) = select_params_chosen(data, chosen_data, traits)

    if not names:
        # st.subheader("Select champion(s) in the settings")
        bin_str = get_base64_of_bin_file("assets/tft_t_logo.png")
        subheader = f"""
        <a src="assets/tft_t_logo.png" style="text-decoration: none; cursor: default; font-weight:600; color: white;"> <img src="data:image/png;base64,{bin_str}" width=40>
        Select desired Headliner(s) in the settings</a>"""
        st.markdown(subheader, unsafe_allow_html=True)
        draw_chart([0], [])
        return

    probs = []
    for tier, n_champ, n_tier, ratio in zip(tiers, n_champs, n_tiers, trait_ratio):
        data_tier = data[str(tier)]
        prob = ratio * (chosen_data.iloc[level - 1].iloc[tier - 1] / 100)
        probs.append(
            (data_tier["pool"] - n_champ)
            / (data_tier["N_champs"] * data_tier["pool"] - n_tier - n_champ)
            * chosen_odds
            * prob
        )

    draw_chart(probs, names)


def select_params_chosen(data, chosen_data, traits):
    # Level
    level = st.sidebar.slider("Level", value=7, min_value=1, max_value=11)
    chosen_odds = list(chosen_data.iloc[level - 1])
    available_costs = [i + 1 for i in range(5) if chosen_odds[i] > 0]
    available_traits = traits[traits["cost"].isin(available_costs)]

    has_chosen = st.sidebar.checkbox("Already possess an Headliner?")

    champs = st.sidebar.multiselect(
        "Desired Headliner(s)",
        build_champ_select(available_traits, level),
    )
    champions = [champ.split(" - ")[0] for champ in champs]

    names, tiers, traits_ratio = build_champ_info(champions, available_traits)

    n_champs = []
    for champ, tier in zip(names, tiers):
        # Number of cards of the champion already bought
        nb_copies = data[str(tier)]["pool"]
        n_champs.append(
            st.sidebar.number_input(
                "Number of copies of %s already out" % champ,
                value=3,
                min_value=0,
                max_value=nb_copies,
            )
        )

    n_tiers = {}
    for tier in np.unique(tiers):
        # Number of cards of same tier already bought
        n_tiers[str(tier)] = st.sidebar.number_input(
            f"Number of {tier} cost champions already out (excluding your champion)",
            value=25,
            min_value=0,
            max_value=300,
        )

    chosen_odds = 1 if not has_chosen else 0.25

    n_tiers = [n_tiers[str(tier)] for tier in tiers]

    return names, tiers, traits_ratio, level, n_champs, n_tiers, chosen_odds


def draw_chart(probs, names):
    prob = np.prod([1 - p for p in probs])
    prb = [
        {
            "name": "Any Headliner",
            "Probability": (1 - prob**i) * 100,
            "Golds spent": i * 2,
        }
        for i in range(1, 51)
    ]
    headliners = prb
    for i, (prob, name) in enumerate(zip(probs, names)):
        headliners += [
            {
                "name": name,
                "Probability": (1 - (1 - prob) ** i) * 100,
                "Golds spent": i * 2,
            }
            for i in range(1, 51)
        ]

    df = pd.DataFrame(headliners)

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
        xaxis={"tickmode": "linear", "dtick": 4, "range": [0, 100]},
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
    tiers = []
    traits_ratio = []

    for champ, count in Counter(champions).items():
        names.append(champ)
        tiers.append(traits.loc[traits.name == champ, "cost"].item())
        traits_ratio.append(
            count / len(traits.loc[traits.name == champ, "chosen_traits"].item())
        )

    return names, tiers, traits_ratio

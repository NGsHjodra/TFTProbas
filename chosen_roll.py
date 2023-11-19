import json
import math
from collections import Counter

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from helpers import roll_page_layout, get_base64_of_bin_file
from plotly.subplots import make_subplots


XP_TO_NEXT_LEVEL = {3: 6, 4: 10, 5: 20, 6: 36, 7: 48, 8: 80, 9: 84, 10: 100}


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

    # list of tuples: (probability, nb copies in pool for desired headliner). the number of copies in pool is used to compute probability with more precision when multiple headliners are selected
    probs_pool, probs_next_lvl_pool = [], []
    for cost, n_champ, n_cost, trait_odd in zip(costs, n_champs, n_costs, trait_odds):
        data_cost = data[str(cost)]
        if (data_cost["pool"] - n_champ) < data_cost["pool"] / 2:
            probs_pool.append(0)
            if level < 10:
                probs_next_lvl_pool.append(0)
        else:
            # average number of copies in the pool of each champion of the desired cost, before draw
            avg_champ_cost_out = data_cost["pool"] - (
                (n_cost + n_champ) / data_cost["n_champs"]
            )
            # number of champions of the desired cost in the pool, before draw
            champ_cost_remain = (
                data_cost["pool"] * data_cost["n_champs"] - n_champ - n_cost
            )
            # number of remaining copies of the desired champion in the pool, before draw
            champ_remain = (data_cost["pool"] - n_champ) * trait_odd

            champ_tier_odd = chosen_data.iloc[level - 1].iloc[cost - 1] / 100
            champ_tier_odd_next_lvl = chosen_data.iloc[level].iloc[cost - 1] / 100

            probs_pool.append(
                compute_prob(
                    cost,
                    champ_remain,
                    avg_champ_cost_out,
                    champ_cost_remain,
                    champ_tier_odd,
                    data_cost["pool"],
                ),
            )
            if level < 10:
                probs_next_lvl_pool.append(
                    compute_prob(
                        cost,
                        champ_remain,
                        avg_champ_cost_out,
                        champ_cost_remain,
                        champ_tier_odd_next_lvl,
                        data_cost["pool"],
                    ),
                )

    draw_chart(
        probs_pool,
        names,
        level,
        gold,
        show_next_level,
        chosen_odds,
        probs_next_lvl_pool,
    )


"""prob to NOT find desired headliner in a draw. We use the "pity" mechanism, that prevent an headliner to be proposed twice in a row."""


def compute_prob(
    cost,
    champ_remain,
    avg_champ_cost_out,
    champ_cost_remain,
    champ_tier_odd,
    pool_for_cost,
):
    prob = (
        (
            (
                (champ_cost_remain - avg_champ_cost_out - champ_remain)
                / (champ_cost_remain - avg_champ_cost_out)
            )
            * champ_tier_odd
            + ((champ_cost_remain - champ_remain) / champ_cost_remain)
            * (1 - champ_tier_odd)
        )
        * champ_tier_odd
    ) + (1 - champ_tier_odd)
    return prob, pool_for_cost


def draw_chart(
    probs_pool,
    names,
    level,
    gold,
    show_next_level,
    chosen_odds,
    probs_next_lvl_pool=[0],
):
    from math import factorial

    gold_to_next_lvl = XP_TO_NEXT_LEVEL[level]
    any_headliners = []
    if len(names) > 1:
        prob_all = np.prod([p[0] for p in probs_pool])
        pools = [x[1] for x in probs_pool]
        # dictionnary: key = total copy in pool for desired headliner ; value = number of headliner with this pool (key)
        pools, counts = np.unique(pools, return_counts=True)
        scaling_factor_multiple_champs_in_same_pool = np.prod(
            [
                (k / (k - 1)) ** (v - 1) * (k - v) / (k - 1)
                for k, v in zip(pools, counts)
            ]
        )

        any_headliners = [
            {
                "name": "Any Headliner",
                "Probability": (
                    1
                    - (prob_all * scaling_factor_multiple_champs_in_same_pool)
                    ** (i * chosen_odds / 2)
                )
                * 100,
                "Golds spent": i,
            }
            for i in range(0, gold, 2)
        ]
        if gold_to_next_lvl < gold and show_next_level:
            prob_next_lvl_all = np.prod([p[0] for p in probs_next_lvl_pool])

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
                    "Probability": (
                        1
                        - (
                            (
                                prob_next_lvl_all
                                * scaling_factor_multiple_champs_in_same_pool
                            )
                            ** ((i * chosen_odds - gold_to_next_lvl) / 2)
                        )
                    )
                    * 100,
                    "Golds spent": i,
                }
                for i in range(gold_to_next_lvl, gold, 2)
            ]

    headliners = any_headliners
    for i, (prob_pool, name) in enumerate(zip(probs_pool, names)):
        headliners += [
            {
                "name": name,
                "Probability": (1 - prob_pool[0] ** (i * chosen_odds / 2)) * 100,
                "Golds spent": i,
            }
            for i in range(0, gold, 2)
        ]

    if gold_to_next_lvl < gold and show_next_level:
        for i, (prob_pool, name) in enumerate(zip(probs_next_lvl_pool, names)):
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
                    "Probability": (
                        1 - prob_pool[0] ** ((i * chosen_odds - gold_to_next_lvl) / 2)
                    )
                    * 100,
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
            height=550,
            width=900,
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

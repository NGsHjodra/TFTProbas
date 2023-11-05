import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from helpers import roll_page_layout
from matrix_utils import build_univariate_transition_matrix


def main():
    data = pd.read_csv("tier_stats.csv", header=0, index_col=0)

    tier, level, n_champ, n_tier, gold = select_params(data)

    # if doots != 0:
    # data.iloc[level + 1] = change_doots_odds(doots, data.iloc[
    #     level + 1].tolist())  # offset of 1 to get the odds per level in data

    data_tier = data[str(tier)]

    draw_chart(
        data_tier[str(level)] / 100,
        data_tier["pool"],
        n_champ,
        data_tier["N_champs"] * data_tier["pool"],
        n_tier,
        gold,
        tier,
    )

    st.text("\n")
    st.write(
        "**_Note_**: This calculation includes the amount of golds spent to buy a copy."
    )
    # st.write('_Example_: You have 50 golds to spend. The odd displayed to find 3 or more copies of your 4 cost champion is after a maximum of 19 rolls (you spent 12 golds buying them).')


def select_params(data):
    # Champion Tier
    tier = st.sidebar.radio(
        "Champion cost", tuple(range(1, 6)), index=3, horizontal=True
    )

    # Level
    level = st.sidebar.slider("Level", value=7, min_value=1, max_value=11)

    # Number of cards of the champion already bought
    nb_copies = data[str(tier)]["pool"]
    n_champ = st.sidebar.slider(
        "Number of your champion's copies out of pool",
        value=3,
        min_value=0,
        max_value=int(nb_copies),
    )

    # Number of cards of same tier already bought
    n_tier = st.sidebar.slider(
        f"Number of {tier} cost champions out of pool (excluding your champion)",
        value=25,
        min_value=0,
        max_value=100,
    )

    # Gold
    gold = st.sidebar.slider(
        "Amount of gold to roll", value=50, min_value=1, max_value=100
    )

    return tier, level, n_champ, n_tier, gold


def draw_chart(prob_tier, N_champ, n_champ, N_tier, n_tier, gold, cost):
    # Cumulative distribution function
    if prob_tier > 0:
        size = np.min((10, N_champ - n_champ + 1))
        P = build_univariate_transition_matrix(
            N_tier - n_tier - n_champ, N_champ - n_champ, prob_tier
        )

        P_n = [
            np.linalg.matrix_power(P, max(int(np.floor((gold - i * cost) / 2)), 0))
            for i in range(size)
        ]
        prb = pd.DataFrame(
            {
                "Proba": P_n[0][0, :][1:],
                "Probability": pd.Series(
                    [np.sum(P_n[i][0, i:]) * 100 for i in range(size)][1:]
                ).round(2),
                "Number of copies": [k for k in range(1, size)],
            }
        )
        prb = prb[prb.iloc[:, 1] > 0.05]  # keep columns > 0.05% probability

        fig2 = px.bar(
            prb,
            y="Probability",
            x="Number of copies",
            title="Odds to find your champion",
            text="Probability",
            template="plotly_dark",
        )
        fig2.update_layout(
            yaxis=dict(range=[0, 100], showgrid=False),
            height=600,
            width=1000,
            xaxis={"tickmode": "linear"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_size=15,
            title_x=0.45,
        )
        fig2.update_traces(
            hovertemplate="At least %{x}: <b>%{y:.2f}</b> %<br><extra></extra>",
            texttemplate="<b>%{text:.2f}</b> %",
            textposition="outside",
            marker_line_width=1.5,
        )

        st.write(fig2)

    else:
        st.text("You can't find this champion with these settings!")

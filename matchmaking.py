from collections import Counter

import SessionState
import streamlit as st

ORDER = 0


def page_layout(summoners):
    st.text("\n")
    st.text("\n")
    st.text(
        "Note: This tool is only useful when everyone is still alive. Indeed, you are assured to play one of the 3 players you least recently played."
    )
    st.text("\n")
    st.text("\n")
    left, right = st.columns(2)
    if not all(summoners):
        st.subheader("Please enter every summoner name in the sidebar.")
    else:
        with left:
            st.subheader("Which player have you faced this round?")
        with right:
            st.subheader("Which player can you face next?")
        st.text("\n")
        st.text("\n")


def main():
    global ORDER
    st.sidebar.title("Lobby summoner names")

    summoners = []
    for i in range(1, 8):
        summoners.append(
            st.sidebar.text_input(f"Summoner {i}", max_chars=20, value=f"")
        )
    states = {s: 0 for s in summoners}
    ss = None

    page_layout(summoners)
    if not all(summoners):
        return

    left, center, right = st.columns(3)

    with left:
        for index, s in enumerate(summoners):
            if st.button(s, key=index):  # summoner name was clicked
                ss = SessionState.get(**states)
                ORDER += 1
                setattr(ss, s, ORDER)

    with center:
        if st.button("Reset matchmaking"):
            ss = SessionState.get(**states)
            old_names = [
                s for s in ss.__dict__
            ]  # remove old names if text inputs changed in sidebar
            for name in old_names:
                delattr(ss, name)
            for s in summoners:
                setattr(ss, s, 0)
            ORDER = 0

    if not ss:
        return

    counter = Counter(ss.__dict__)

    not_matched_yet = [s[0] for s in counter.items() if s[1] == 0]
    can_match = [
        c[0] for c in counter.most_common()[:-4:-1]
    ]  # 3 players least recently played

    possibilities = set(not_matched_yet) | set(can_match)

    with right:
        for p in possibilities:
            st.markdown(f"- **{p}**")

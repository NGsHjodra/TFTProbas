# Import pages
import chosen_roll
import roll
from helpers import *

PAGES = {
    "Rolling odds": roll,
    "Headliner odds": chosen_roll,
}

st.set_page_config(
    page_title="TFT tools",
    page_icon="assets/dragonlands.png",
    layout="wide",
    initial_sidebar_state="auto",
)


# set_bg_hack("assets/set7_banner_blurred.png")


def set_css():
    #  GENERAL STYLE + DISABLE FULLSCREEN BUTTON + CHANGE PADDINGS TOP OF THE PAGE
    st.markdown(
        """
        <style>
            body {
                 text-shadow: 1px 1px 1px black;
            }
            header {
                visibility: hidden;
            }
            p {
                font-size: 18px;
            }
            button[title="View fullscreen"] {
                visibility: hidden;
            }
            .main .block-container {
                padding-top: 1.5rem;
                padding-bottom: 1.5rem;
                padding-left: 3rem;
                padding-right: 3rem;
            }
            div[data-testid="stSidebarUserContent"] {
                padding: 1.5rem;
            }
            footer {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_body():
    st.header("TFT Odds Tool - Set 10 PBE")

    github_repo = get_img_with_href(
        "assets/github.png", "https://github.com/sde-cdsp/TFTProbas", text="Project: "
    )
    credits = get_img_with_href(
        "assets/xlogo.png", "https://twitter.com/Toof_pro", text="Contact: "
    )
    st.markdown(
        """<hr style="height:2px;border:none;color:white;" /> """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(github_repo, unsafe_allow_html=True)
    with right:
        st.markdown(credits, unsafe_allow_html=True)


def set_and_run_page():
    left, right = st.columns(2)

    bin_str = get_base64_of_bin_file("assets/tft_t_logo.png")
    st.sidebar.image("assets/tft_t_logo.png", width=200)
    selection = st.sidebar.radio("", list(PAGES.keys()), index=1)
    st.sidebar.title("Settings")

    page = PAGES[selection]
    page.main()


def set_footer():
    st.write(
        "<div style='position: fixed; bottom:10px; width: 850px; font-size:13px;'>This web app isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.</div>",
        unsafe_allow_html=True,
    )


def main():
    set_css()
    set_body()
    set_and_run_page()
    set_footer()


if __name__ == "__main__":
    main()

# Import pages
import roll
import chosen_roll
from helpers import *

PAGES = {
    "Rolling odds (set 10 PBE)": roll,
    "Headliners odds (set 10 PBE)": chosen_roll,
}

st.set_page_config(page_title='TFT tools', page_icon='assets/dragonlands.png', layout='wide',
                   initial_sidebar_state='auto')

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
    
    </style>
    """,
    unsafe_allow_html=True,
)

st.header("TFT Odds Tool - Set 10")

# set_bg_hack("assets/set7_banner_blurred.png")

left, right = st.columns(2)

st.sidebar.title('Navigation')
selection = st.sidebar.radio('', list(PAGES.keys()))
page = PAGES[selection]
page.main()

github_repo = get_img_with_href('assets/github.png', 'https://github.com/sde-cdsp/TFTProbas', text="Project: ")
credits = get_img_with_href('assets/xlogo.png', 'https://twitter.com/Toof_pro', text="Contact: ")
st.text('\n')
st.markdown("""<hr style="height:2px;border:none;color:white;" /> """, unsafe_allow_html=True)

left, right = st.columns(2)
with left:
    st.markdown(github_repo, unsafe_allow_html=True)
with right:
    st.markdown(credits, unsafe_allow_html=True)

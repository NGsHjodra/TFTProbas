# Import pages
import roll
from helpers import *

PAGES = {
    "Rolling odds (patch 12.11)": roll,
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

st.header("Teamfight Tactics odds tool - Set 7")

set_bg_hack("assets/set7_banner_blurred.png")

left, right = st.columns(2)

# st.sidebar.title('Navigation')
# selection = st.sidebar.radio('', list(PAGES.keys()))
page = PAGES[list(PAGES.keys())[0]]
page.main()

github_repo = get_img_with_href('assets/github.png', 'https://github.com/sde-cdsp/TFTProbas', text="Project: ")
credits = "by [LittleToof](https://twitter.com/Toof_pro), [Pas De Bol](https://twitter.com/PasDeBolTFT) & [Jibs](https://twitter.com/jibsremy)"

st.text('\n')
st.markdown("""<hr style="height:2px;border:none;color:white;" /> """, unsafe_allow_html=True)

left, right = st.columns(2)
with left:
    st.markdown(github_repo, unsafe_allow_html=True)
with right:
    st.markdown(credits, unsafe_allow_html=True)

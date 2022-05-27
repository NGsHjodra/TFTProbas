import base64
import os

import streamlit as st


# from https://discuss.streamlit.io/t/href-on-image/9693/3
@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


@st.cache(allow_output_mutation=True)
def get_img_with_href(local_img_path, target_url, text=""):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''
        {text}
        <a href="{target_url}">
            <img src="data:image/{img_format};base64,{bin_str}" width=30/>
        </a>'''
    return html_code


def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.

    Returns
    -------
    The background.
    '''

    st.markdown(
        f"""
	   <style>
	   .main {{
	       background: url(data:image/png;base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
	       background-size: cover;
	   }}
	   </style>
	   """,
        unsafe_allow_html=True
    )


def roll_page_layout():
    st.sidebar.title("Settings")


def change_doots_odds(doots, odds):
    s1 = (odds[0] + odds[1]) / 3
    s2 = (odds[0] + odds[1] + odds[2] + s1) / 3
    s3 = (odds[3] + s1 + 1.5 * (s2 - s1) + 3 * s2) / 3

    if doots <= s1:
        out = [
            max(odds[0] - 1.5 * doots, 0),
            max(odds[1] - 1.5 * doots, 0),
            odds[2] + doots,
            odds[3] + doots,
            odds[4] + doots,
        ]

    elif doots <= s2:
        out = [
            0,
            0,
            max(odds[2] + s1 - 3 * (doots - s1), 0),
            odds[3] + s1 + 1.5 * (doots - s1),
            odds[4] + s1 + 1.5 * (doots - s1)
        ]

    else:
        out = [
            0,
            0,
            0,
            max(odds[3] + s1 + 1.5 * (s2 - s1) - 3 * (doots - s2), 0),
            min(odds[4] + s1 + 1.5 * (s2 - s1) + 3 * (doots - s2), 100)
        ]

    return [int(i) for i in out]

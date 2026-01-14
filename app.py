import re
import urllib.parse
from urllib.parse import urlparse
from difflib import SequenceMatcher
from typing import List, Dict

import feedparser
import streamlit as st


# ----------------------------
# Page
# ----------------------------
st.set_page_config(
    page_title="OPEN INSIGHT",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# Google AdSense 추가
# ----------------------------
st.markdown(
    """
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5334002072937874"
     crossorigin="anonymous"></script>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# UI (minimal, list)
# ----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap');
* { font-family: 'Pretendard', sans-serif; }
... (이후 기존 코드와 동일)

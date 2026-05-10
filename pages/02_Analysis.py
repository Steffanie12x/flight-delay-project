# 02_Analysis.py
import streamlit as st
from utils.navbar import show_navbar

# ── Seitenkonfiguration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analysis – CatchYourFlight",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("<style>[data-testid='stSidebar'],[data-testid='collapsedControl']{display:none!important}</style>", unsafe_allow_html=True)

# ── Navbar anzeigen ───────────────────────────────────────────────────────────
show_navbar()

# ── Seiteninhalt ──────────────────────────────────────────────────────────────
st.title("Analysis")
st.write("Delay pattern exploration coming soon...")

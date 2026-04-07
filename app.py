import streamlit as st          # Streamlit für die Web-Oberfläche

# Seitenkonfiguration – muss als erstes aufgerufen werden
st.set_page_config(
    page_title="ZRH Flight Delay Analyzer",    # Titel im Browser-Tab
    page_icon="✈️",                             # Icon im Browser-Tab
    layout="wide"                               # Breites Layout für mehr Platz
)

# ── CUSTOM CSS ─────────────────────────────────────────────────
st.markdown("""
    <style>
        /* Moderne Schriftart laden */
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

        /* Gesamte App */
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        /* Hauptbereich – weisser Hintergrund */
        .main {
            background-color: #FFFFFF;
        }

        /* Hauptbereich Padding */
        .main .block-container {
            padding-top: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1200px;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #F8FAFC;
            border-right: 1px solid #E2E8F0;
        }

        /* Sidebar Links */
        section[data-testid="stSidebar"] a {
            color: #475569 !important;
            font-weight: 500;
            font-size: 0.9rem;
        }

        section[data-testid="stSidebar"] a:hover {
            color: #0EA5E9 !important;
        }

        /* Alle Titel */
        h1, h2, h3 {
            font-family: 'DM Sans', sans-serif;
            font-weight: 700;
            color: #0F172A;
        }

        /* Metriken */
        [data-testid="stMetric"] {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1.2rem;
        }

        [data-testid="stMetricLabel"] {
            color: #94A3B8 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        [data-testid="stMetricValue"] {
            color: #0F172A !important;
            font-weight: 700 !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: #0EA5E9;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.8rem;
            font-family: 'DM Sans', sans-serif;
            font-weight: 600;
        }

        .stButton > button:hover {
            background-color: #0284C7;
        }

        /* Trennlinien */
        hr {
            border-color: #E2E8F0;
        }
    </style>
""", unsafe_allow_html=True)    # CSS in Streamlit einbinden

# ── HERO SECTION MIT HIMMEL-HINTERGRUND ───────────────────────
# Grosses Banner oben mit Himmel-Bild und Titel darüber
st.markdown("""
<div style='background:linear-gradient(180deg,#BAE6FD 0%,#E0F2FE 40%,#F0F9FF 70%,#FFFFFF 100%);border-radius:24px;padding:3.5rem 3rem 2.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden;'>
<div style='position:absolute;top:-30px;right:80px;width:120px;height:120px;background:radial-gradient(circle,#FDE68A 0%,#FCD34D 50%,transparent 70%);border-radius:50%;opacity:0.9;'></div>
<div style='position:absolute;top:25px;right:250px;background:white;border-radius:50px;width:120px;height:35px;opacity:0.85;box-shadow:0 4px 15px rgba(255,255,255,0.5);'></div>
<div style='position:absolute;top:12px;right:270px;background:white;border-radius:50px;width:70px;height:40px;opacity:0.85;'></div>
<div style='position:absolute;top:50px;right:450px;background:white;border-radius:50px;width:90px;height:28px;opacity:0.7;'></div>
<div style='position:absolute;top:38px;right:465px;background:white;border-radius:50px;width:55px;height:32px;opacity:0.7;'></div>
<div style='font-size:3rem;margin-bottom:0.5rem;'>✈️</div>
<h1 style='font-size:2.8rem;font-weight:700;color:#0C4A6E;margin:0;line-height:1.2;'>ZRH Flight Delay Analyzer</h1>
<p style='color:#0369A1;font-size:1.1rem;margin-top:0.5rem;font-weight:400;'>Zurich Airport · Delay Analysis & Prediction</p>
</div>
""", unsafe_allow_html=True)    # Hero-Banner mit CSS-Himmel und Wolken

# ── NAVIGATIONS-KARTEN ─────────────────────────────────────────
# Drei Karten nebeneinander für die drei Hauptbereiche
col1, col2, col3 = st.columns(3)    # Drei gleich breite Spalten

with col1:
    # Dashboard-Karte in hellblau
    st.markdown("""
<div style='background:#F0F9FF;border:1px solid #BAE6FD;border-radius:16px;padding:1.5rem;height:140px;'>
<div style='font-size:1.8rem;'>📊</div>
<h3 style='color:#0C4A6E;margin:0.5rem 0 0.3rem 0;font-size:1.1rem;'>Dashboard</h3>
<p style='color:#64748B;font-size:0.85rem;margin:0;'>Overview of delay statistics at ZRH</p>
</div>
""", unsafe_allow_html=True)

with col2:
    # Analysis-Karte in hellgrün
    st.markdown("""
<div style='background:#F0FDF4;border:1px solid #BBF7D0;border-radius:16px;padding:1.5rem;height:140px;'>
<div style='font-size:1.8rem;'>🔍</div>
<h3 style='color:#14532D;margin:0.5rem 0 0.3rem 0;font-size:1.1rem;'>Analysis</h3>
<p style='color:#64748B;font-size:0.85rem;margin:0;'>Explore delay patterns interactively</p>
</div>
""", unsafe_allow_html=True)

with col3:
    # Prediction-Karte in hellorange
    st.markdown("""
<div style='background:#FFF7ED;border:1px solid #FED7AA;border-radius:16px;padding:1.5rem;height:140px;'>
<div style='font-size:1.8rem;'>🔮</div>
<h3 style='color:#7C2D12;margin:0.5rem 0 0.3rem 0;font-size:1.1rem;'>Prediction</h3>
<p style='color:#64748B;font-size:0.85rem;margin:0;'>Predict delay risk for your flight</p>
</div>
""", unsafe_allow_html=True)

# Abstand
st.markdown("<br>", unsafe_allow_html=True)

# ── INFO ZEILE ─────────────────────────────────────────────────
# Kleine Info-Zeile unten
st.markdown("""
<p style='color:#94A3B8;font-size:0.8rem;text-align:center;'>
University of St. Gallen · Computer Science Group Project · 2026
</p>
""", unsafe_allow_html=True)    # Footer mit Uni-Info
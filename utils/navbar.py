import streamlit as st

def show_navbar():
    # ── Globales CSS-Styling ──────────────────────────────────────────────────
    # Weißer Hintergrund, schwarze Schrift, Helvetica Neue, Sidebar ausgeblendet
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* Weißer Hintergrund */
    [data-testid="stAppViewContainer"] { background-color: #ffffff; }
    [data-testid="stHeader"] { background-color: transparent; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer { visibility: hidden; }

    /* Anker-Link-Icon beim Hovern verstecken */
    a.anchor-link,
    h1 a, h2 a, h3 a, h4 a,
    [data-testid="stMarkdownContainer"] a[href^="#"],
    .stMarkdown a[href^="#"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Alle Texte schwarz */
    html, body, p, span, div, label, li, a,
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] *,
    [data-testid="stText"] *,
    [data-testid="metric-container"] *,
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricDelta"],
    .stSlider label, .stDateInput label,
    .stSelectbox label, .stTextInput label,
    [data-testid="stWidgetLabel"] *,
    [data-testid="stCaptionContainer"] *,
    [data-testid="stDataFrameResizable"] * {
        color: #111111 !important;
    }

    /* Ausnahme: Text im Hero-Bild bleibt weiß */
    .hero-text, .hero-text * {
        color: inherit !important;
    }

    /* page_link Buttons als Navbar-Links stylen */
    div[data-testid="stPageLink"] a {
        text-decoration: none !important;
        color: #111111 !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em !important;
    }
    div[data-testid="stPageLink"] a:hover { color: #3B82F6 !important; }
    div[data-testid="stPageLink"] p {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Navigationsleiste ─────────────────────────────────────────────────────
    # App-Name links, Seiten-Links rechts — breitere Spalten damit kein Text abgeschnitten wird
    nav_logo, nav_space, nav1, nav2, nav3 = st.columns([3, 3, 1.5, 1.5, 1.5])
    with nav_logo:
        st.markdown(
            "<div style='font-size:2rem; font-weight:800; padding-top:0.4rem;'>"
            "Flight Delay <span style='color:#6B7280; font-weight:400; font-size:1.5rem;'>· USA</span></div>",
            unsafe_allow_html=True
        )
    with nav1:
        # Dashboard verlinkt auf die Startseite (app.py), die das Hero-Bild enthält
        st.page_link("app.py", label="Dashboard")
    with nav2:
        st.page_link("pages/02_Analysis.py", label="Analysis")
    with nav3:
        st.page_link("pages/03_Prediction.py", label="Prediction")

    # Trennlinie unter der Navbar
    st.markdown("<hr style='border:none; border-top:1px solid #e0e0e0; margin:0 0 2rem 0;'>", unsafe_allow_html=True)

import streamlit as st

pg = st.navigation(
    [
        st.Page("home.py",                title="Home",       default=True),
        st.Page("pages/03_Prediction.py", title="Prediction"),
    ],
    position="hidden",
)
pg.run()

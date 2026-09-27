import streamlit as st

st.set_page_config(
    page_title="FloraPulse 🌱",
    page_icon="🌱",
    layout="wide",
)

# Redirect to the About page as the main landing
st.switch_page("pages/3_About.py")

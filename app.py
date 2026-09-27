"""
Entry point for Smart Garden app.

Run this file with:
    streamlit run app.py

Pages are loaded automatically from the pages/ directory in order.
"""
import streamlit as st

# Configure the page
st.set_page_config(page_title="Smart Garden", page_icon="🌱", layout="wide")

# Directly open the Welcome page on launch
st.switch_page("pages/1_Welcome.py")

# Streamlit automatically loads pages from pages/ directory
# No need to manually define pages with st.navigation()
# Just run the app and it will show all pages in sidebar
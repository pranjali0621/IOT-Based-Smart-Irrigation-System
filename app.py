"""
Entry point for the Smart Garden app.

Run this file (not the individual page files) with:
    streamlit run app.py

It stitches the pages together, in this order:
    welcomepage.py -> login.py -> signup.py -> create.py -> garden.py -> dashboard.py

`position="hidden"` keeps Streamlit's built-in page picker out of the
sidebar, so none of the pages' existing designs change -- navigation
happens only through the buttons already on each page.
"""
import streamlit as st

pages = [
    st.Page("welcomepage.py", title="Welcome", default=True),
    st.Page("login.py", title="Login"),
    st.Page("signup.py", title="Sign Up"),
    st.Page("create.py", title="Create Your Garden"),
    st.Page("garden.py", title="Garden"),
    st.Page("dashboard.py", title="Dashboard"),
]

pg = st.navigation(pages, position="hidden")
pg.run()
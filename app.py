# %%Imports ##########################################################################################
import pandas as pd
from dotenv import load_dotenv
import os

import streamlit as st
from src.login import login
from src.dashboard_eu import show_eu_grp_dashboard
#from pages.us_grp_dashboard import show_us_grp_dashboard


# %%Set up session state #############################################################################
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Render the correct page ###########################################################################

if st.session_state.page == "landing":
    st.title("Welcome to the Fitness Tracker")
    st.write("Select a group to continue:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Die Dresdner und andere"):
            st.session_state.group = "eu_grp"
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("Americans ONLY >:("):
            st.session_state.group = "us_grp"
            st.session_state.page = "login"
            st.rerun()

# Login Page
elif st.session_state.page == "login":
    login()

# Group Dashboards
elif st.session_state.page == "eu_grp_dashboard":
    #st.title("Group 1 Fitness Dashboard")
    show_eu_grp_dashboard()

elif st.session_state.page == "us_grp_dashboard":
    st.title("Group 2 Fitness Dashboard")



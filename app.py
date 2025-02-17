# %%Imports ##########################################################################################
import pandas as pd
from dotenv import load_dotenv
import os

import streamlit as st
from src.login import login
from src.dashboard_eu import show_eu_grp_dashboard, show_individual_dashboard
from src.dashboard_us import show_us_grp_dashboard
from src.data_loader import load_eu_data, load_us_data, extract_eu_data, extract_us_data



# %%Set up session state ###########################################################################
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "subpage" not in st.session_state:
    st.session_state.subpage = "group"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Group Selection ##################################################################################
if st.session_state.page == "landing":
    st.title("Welcome to the Fitness Tracker")
    st.write("Select a group to continue:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Dresden/EU Group 🏰"):
            st.session_state.group = "eu_grp"
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("USA 🗽"):
            st.session_state.group = "us_grp"
            st.session_state.page = "login"
            st.rerun()

    with col3:
        if st.button("USA 2"):
            st.session_state.group = "us_grp2"
            st.session_state.page = "login"
            st.rerun()

# Login Page #######################################################################################
elif st.session_state.page == "login":
    login()

# EU Dashboard #####################################################################################
elif st.session_state.page == "eu_grp_dashboard":
    # Load data from Google Sheets
    data_df, goals_df = load_eu_data()

    # Subpage session states
    if "ind_participant" not in st.session_state:
        st.session_state.ind_participant = data_df["Participant"].unique()[0]
    if "challenge_period" not in st.session_state:
        st.session_state.challenge_period = data_df["Challenge Period"].max()

    # Sidebar Layout
    if st.sidebar.button("Group Dashboard"):
        st.session_state.subpage = "group"
    if st.sidebar.button("Individual Dashboard"):
        st.session_state.subpage = "individual"

    # Render the correct dashboard
    if st.session_state.subpage == "group":
        show_eu_grp_dashboard(data_df, goals_df)
    elif st.session_state.subpage == "individual":
        show_individual_dashboard(data_df, goals_df)
    else:
        show_eu_grp_dashboard(data_df, goals_df)

# US Dashboard #####################################################################################
elif st.session_state.page == "us_grp_dashboard":
    show_us_grp_dashboard()

# US 2 Dashboard ###################################################################################
elif st.session_state.page == "us_grp2_dashboard":
    show_us_grp_dashboard()

# Logout ###########################################################################################
if st.session_state.page not in ["landing", "login"]: # Only show logout button if logged in
    if st.sidebar.button("Logout"):
        st.session_state.page = "landing"
        st.session_state.pop("authenticated", None)
        st.rerun()

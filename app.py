# Imports ##########################################################################################
import pandas as pd
from dotenv import load_dotenv
import os

import streamlit as st
from pages.login import login
from pages.eu_grp_dashboard import show_eu_grp_dashboard
from pages.us_grp_dashboard import show_us_grp_dashboard


# Set up session state #############################################################################
if "page" not in st.session_state:
    st.session_state.page = "landing"

# Landing Page #####################################################################################
if st.session_state.page == "landing":
    st.title("Welcome to the Fitness Tracker")
    st.write("Select a group to continue:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Die Dresdner und andere"):
            st.session_state.group = "eu_grp"
            st.session_state.page = "login"
            st.experimental_rerun()
    with col2:
        if st.button("Americans ONLY >:("):
            st.session_state.group = "us_grp"
            st.session_state.page = "login"
            st.experimental_rerun()

# Login Page #######################################################################################
elif st.session_state.page == "login":
    login()

# Group 1 Dashboard ################################################################################
elif st.session_state.page == "group1_dashboard":
    show_eu_grp_dashboard()

# Group 2 Dashboard ################################################################################
elif st.session_state.page == "group2_dashboard":
    show_us_grp_dashboard()










#%%
# Define your password
load_dotenv()
PASSWORD = os.getenv('US_APP_PASSWORD')


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Authentication logic
if not st.session_state.authenticated:
    st.title("Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()  # Force immediate rerun after successful login
        else:
            st.error("Invalid password.")
else:
    grouped = load_data()
    # Your main app content
    st.title("Welcome to the Fitness Dashboard!")
    st.write("This is where your app's content goes.")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()  # Force immediate rerun after logout

    st.title("Welcome to the Fitness Dashboard!")
    st.write("This is where your app's content goes.")

    
    st.header("Fitness Group Data")
    st.write("This is a description")

    st.data_editor(grouped)


    st.header("2. Get started with a simple bar chart 📊")

    st.write("Let's chart the US state population data from the year 2019")

    st.bar_chart(grouped,
                x='Week Start',
                y='Total')
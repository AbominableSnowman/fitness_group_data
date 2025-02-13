import streamlit as st
#from pages.filters import filter_data
#from pages.visualizations import show_progress_bar, show_grouped_bar_chart, show_line_plot
#from pages.data_loader import fetch_data

def show_us_grp_dashboard():
    st.title("Group 1 Fitness Dashboard")

    # Load data from Google Sheets
    #df = fetch_data("group1")

    # Apply filters
    #df = filter_data(df)

    # Show visualizations
    #show_progress_bar(df)
    #show_grouped_bar_chart(df)
    #show_line_plot(df)

    if st.button("Logout"):
        st.session_state.page = "landing"
        st.session_state.pop("authenticated", None)
        st.experimental_rerun()
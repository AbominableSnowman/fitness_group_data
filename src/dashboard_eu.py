import streamlit as st
from src.filters import filter_data
from src.visualizations import show_progress_bar, display_metrics
from src.data_loader import load_eu_data

def show_eu_grp_dashboard():
    st.title("Dresden Fitness Group Dashboard")

    # Load data from Google Sheets
    data_df, goals_df = load_eu_data()

    # Apply filters
    filtered_data_df, filtered_goals_df = filter_data(data_df, goals_df)

    # Show visualizations
    show_progress_bar(filtered_data_df, filtered_goals_df)
    display_metrics(filtered_data_df, filtered_goals_df)
    #show_grouped_bar_chart(filtered_data_df)
    #show_line_plot(filtered_data_df)

    if st.button("Logout"):
        st.session_state.page = "landing"
        st.session_state.pop("authenticated", None)
        st.rerun()

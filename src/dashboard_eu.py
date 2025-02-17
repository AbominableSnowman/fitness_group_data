import streamlit as st
from src.filters import filter_grp_data, filter_individual_data
from src.visualizations import (display_group_metrics, display_individual_metrics, 
                                show_progress_bar_plotly, show_line_plot_with_projection_plotly)

def show_eu_grp_dashboard(data_df, goals_df):
    st.title("Dresden Fitness Group Dashboard")
    # Apply filters
    filtered_data_df, filtered_goals_df = filter_grp_data(data_df, goals_df)

    # Show visualizations
    show_progress_bar_plotly(filtered_data_df, filtered_goals_df)
    show_line_plot_with_projection_plotly(filtered_data_df, filtered_goals_df)
    display_group_metrics(filtered_data_df, filtered_goals_df)



def show_individual_dashboard(data_df, goals_df):
    st.title("Individual Dashboard")

    # Apply filters
    filtered_data_df, filtered_goals_df = filter_individual_data(data_df, goals_df)
    filtered_data_df["Week Start"] = filtered_data_df["Week Start"].dt.date
    st.write(filtered_data_df[["Week Start", "Week", "Value"]].rename(
        columns={"Week Start": "Week Start Date", "Value": "# of Exercises"}))
    
    display_individual_metrics(filtered_data_df, filtered_goals_df)

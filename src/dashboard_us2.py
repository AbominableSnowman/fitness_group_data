import streamlit as st
from src.filters import filter_grp_data
from src.visualizations import show_progress_bar_plotly, display_group_metrics
from src.data_loader import load_us_data

def show_us_grp_dashboard():
    st.title("Fitness Dashboard")

    # Load data from Google Sheets
    data_df, goals_df = load_us_data()

    # Apply filters
    filtered_data_df, filtered_goals_df = filter_grp_data(data_df, goals_df)

    # Prep data
    cmbn_metrics = filtered_data_df[filtered_data_df["Metric"].isin(
                        ["Resistance Training", "Cardio", "Total Exercise"])]
    metric_data = cmbn_metrics.drop("Metric", axis=1).groupby(
                                ["Challenge Period", "Week", "Week Start", "Participant"]
                                ).sum().reset_index()

    # Show visualizations
    show_progress_bar_plotly(metric_data, filtered_goals_df)
    display_group_metrics(metric_data, filtered_goals_df)
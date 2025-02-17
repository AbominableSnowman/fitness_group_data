import streamlit as st
from src.filters import filter_grp_data
from src.visualizations import (show_progress_bar_plotly, display_group_metrics, 
                                show_line_plot_with_projection_plotly)
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
    
    workout_goals = filtered_goals_df[filtered_goals_df["Goal Type"].isin(
                        ["Resistance Training", "Cardio", "Total Workouts"])]
    workout_goals = workout_goals.drop("Goal Type", axis=1).groupby(
                                ["Challenge Period", "Participant"]
                                ).sum().reset_index()
    

    # Show visualizations
    show_progress_bar_plotly(metric_data, workout_goals)
    # TODO: create logic to bring in challenge duration (used in eu data but not in us data yet)
    #show_line_plot_with_projection_plotly(metric_data, workout_goals)
    display_group_metrics(metric_data, filtered_goals_df)

import streamlit as st
import pandas as pd
"""
Schema for data:

| Week Start | Challenge Period | Week | Participant | Metric | Value |

"""


def filter_data(data_df, goals_df):
    #TODO: filter in right order to avoid invalid data appearing in filter
    """Applies filters for participant and challenge period."""
    all_participants = list(data_df["Participant"].unique())
    participants = st.multiselect("Select Participants", options=all_participants, 
                                  default=all_participants)
    
    challenges = list(data_df["Challenge Period"].unique())
    challenge_period = st.selectbox("Select Challenge Period", options=challenges, 
                                    index=len(challenges) - 1)
    
    # Have to filter for challenge period first
    all_weeks = list(data_df[data_df["Challenge Period"] == challenge_period]["Week"].unique())
    weeks = st.multiselect("Select Week", options=all_weeks, default=all_weeks)

    filtered_data_df = data_df[
        (data_df["Participant"].isin(participants)) & 
        (data_df["Challenge Period"] == challenge_period) &
        (data_df["Week"].isin(weeks))
        ].dropna(axis=0, how='any').reset_index(drop=True)
    
    filtered_goals_df = goals_df[
        (goals_df["Participant"].isin(participants)) & 
        (goals_df["Challenge Period"] == challenge_period)
        ].dropna(axis=0, how='any').reset_index(drop=True)
    
    return filtered_data_df, filtered_goals_df

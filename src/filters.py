import streamlit as st
import pandas as pd
"""
Schema for data:

| Week Start | Challenge Period | Week | Participant | Metric | Value |

"""


def filter_grp_data(data_df, goals_df):
    #TODO: filter in right order to avoid invalid data appearing in filter
    """Applies filters for participant and challenge period."""
    all_participants = list(data_df["Participant"].unique())
    participants = st.multiselect("Select Participants", options=all_participants, 
                                  default=all_participants)
    
    challenges = list(data_df["Challenge Period"].unique())
    challenges.remove('')
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


def filter_individual_data(data_df, goals_df):
    """Field hierarchy: Challenge Period > Participant > Week"""
    # Make a copy of the original data
    filtered_data_df = data_df.copy()
    filtered_goals_df = goals_df.copy()
    
    # Filter by participant ########################################################################
    participants = list(filtered_data_df["Participant"].unique())
    st.session_state.ind_participant = st.selectbox("Select Participant", options=participants, 
                                  index=0)
    
    filtered_data_df = filtered_data_df[
        filtered_data_df["Participant"] == st.session_state.ind_participant
        ]

    # Filter by challenge period ###################################################################
    challenges = ["All"] + list(filtered_data_df["Challenge Period"].unique())
    challenges.remove('')
    st.session_state.challenge_period = st.selectbox("Select Challenge Period", options=challenges, 
                                    index=len(challenges) - 1)
    
    if st.session_state.challenge_period != "All":
        filtered_data_df = filtered_data_df[
            (filtered_data_df["Challenge Period"] == st.session_state.challenge_period)
            ]
    
    # Filter by week ###############################################################################
    if st.session_state.challenge_period != "All":
        weeks = list(filtered_data_df["Week"].unique())
        week = st.multiselect("Select Week", options=weeks, default=weeks)
        filtered_data_df = filtered_data_df[(filtered_data_df["Week"] == week)]
    
    # Drop any rows with missing values ############################################################
    filtered_data_df = filtered_data_df.dropna(axis=0, how='any').reset_index(drop=True)
    
    return filtered_data_df, filtered_goals_df

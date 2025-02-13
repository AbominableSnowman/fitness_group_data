import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


def show_progress_bar(data_df, goals_df):
    data_df = data_df.reset_index(drop=True).dropna(axis=0, how='any')
    data_df = data_df[["Week", "Participant", "Value"]]
    #data_df["Week"] = data_df["Week"].astype(int).astype(str)
    st.bar_chart(data_df, x="Participant", y="Value", color="Week", use_container_width=True,
                 horizontal=True)


def progress_logic(data_df, goals_df):
    # Aggregate participant progress
    progress_bar_df = data_df.groupby("Participant")["Value"].sum().reset_index()
    progress_bar_df = progress_bar_df.merge(goals_df, on="Participant", how="left")
    
    # Compute progress percentage
    progress_bar_df["Progress (%)"] = (progress_bar_df["Value"] / progress_bar_df["Goal"]) * 100
    progress_bar_df.sort_values(by="Participant", ascending=False, inplace=True)

    # Ensure no missing values
    progress_bar_df.fillna(0, inplace=True)

    # Set a max scale that allows for slight overshoot beyond 100%
    max_scale = max(110, progress_bar_df["Progress (%)"].max() + 10)

    return progress_bar_df, max_scale


def display_metrics(data_df, goals_df):
    current_average = data_df[
        ["Participant", "Value"]
        ].groupby("Participant").mean().reset_index(drop=False)
    
    if len(data_df.Week.unique()) < 2:
        last_week_average = current_average

    else:
        current_week = data_df.Week.unique()[-1]
        previous_weeks = data_df[data_df.Week != current_week]
        last_week_average = previous_weeks[
            ["Participant", "Value"]
            ].groupby("Participant").mean().reset_index(drop=False)

    current_average.rename(columns={"Value": "Current Average"}, inplace=True)
    last_week_average.rename(columns={"Value": "Last Week Average"}, inplace=True)

    metrics_df = current_average.merge(last_week_average, on="Participant", how="left")
    metrics_df.fillna(0, inplace=True)

    metrics_df["Change"] = metrics_df["Current Average"] - metrics_df["Last Week Average"]
    metrics_df.set_index("Participant", inplace=True)

    st.header("Metrics")
    st.write("Current Average (+ change from last week)")

    # Create columns dynamically based on the number of participants
    num_participants = len(metrics_df)
    cols = st.columns(num_participants)

    for idx, (participant, row) in enumerate(metrics_df.iterrows()):
        with cols[idx]:
            st.metric(participant, row["Current Average"], f"{row['Change']:.2f}")

    


    return None


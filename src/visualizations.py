import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd



####################################################################################################
def progress_logic(data_df, goals_df):
    # Aggregate participant progress
    progress_df = data_df[["Week", "Participant", "Value"]].groupby(
        ["Week", "Participant"]
        ).sum().reset_index()
    progress_df = progress_df.merge(goals_df[["Participant", "Goal"]], on="Participant", how="left")
    
    # Compute progress percentage
    progress_df["Progress (%)"] = (progress_df["Value"] / progress_df["Goal"]) * 100
    progress_df.sort_values(by=["Week", "Participant"], ascending=True, inplace=True)

    # Ensure no missing values
    progress_df.fillna(0, inplace=True)

    # Set a max scale that allows for slight overshoot beyond 100%
    max_scale = max(110, progress_df["Progress (%)"].max() + 10)

    return progress_df, max_scale


def show_progress_bar_plotly(data_df, goals_df):
    """Displays a progress bar chart using Plotly for more customization."""

    # Compute progress
    progress_bar_df, max_scale = progress_logic(data_df, goals_df)

    # Create the Plotly bar chart
    fig = px.bar(
        progress_bar_df,
        x="Progress (%)",
        y="Participant",
        color="Week",
        orientation="h",  # Horizontal bars
        text="Value",
        color_continuous_scale="Blues",  # Adjust color scheme
    )

    # Customize layout
    fig.update_layout(
        xaxis=dict(range=[0, max_scale]),  # Set max scale dynamically
        yaxis=dict(categoryorder="total ascending"),  # Order bars by progress
        title="Participant Progress Toward Goals",
        bargap=0.2,
        template="plotly_white",
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# Line Plot Rate of Change #########################################################################
def show_line_plot_with_projection_plotly(data_df, goals_df):
    """
    Creates a Plotly line plot of weekly workout numbers (from the 'Value' column)
    for each participant, starting at (0,0). Also overlays, for each participant,
    a projection line (dotted) that connects from the last actual data point to:
      - an extra point at the next week (last_week + 1) at the required projected rate,
      - and then to the challenge end week at that same rate.
    
    Parameters:
      data_df: DataFrame with columns "Week", "Participant", "Value" (weekly workouts)
      goals_df: DataFrame with columns "Challenge Period", "Duration (weeks)", 
                "Participant", "Goal"
    """
    # Create a Plotly figure
    fig = go.Figure()

    # Get a consistent color palette
    participants = list(data_df["Participant"].unique())
    palette = px.colors.qualitative.Plotly

    for idx, participant in enumerate(participants):
        color = palette[idx % len(palette)]
        # Filter and sort data for this participant
        part_data = data_df[data_df["Participant"] == participant].copy()
        part_data["Week"] = pd.to_numeric(part_data["Week"], errors="coerce")
        part_data.sort_values("Week", inplace=True)
        
        # Prepend a (0,0) point if the first week is not 0
        if part_data.empty or part_data["Week"].min() > 0:
            start_df = pd.DataFrame({"Week": [0], "Value": [0]})
            part_data = pd.concat([start_df, part_data], ignore_index=True)
        
        # Add the actual weekly data trace
        fig.add_trace(go.Scatter(
            x=part_data["Week"],
            y=part_data["Value"],
            mode="lines+markers",
            name=participant,
            legendgroup=participant,
            marker=dict(color=color),
            line=dict(color=color),
            hovertemplate="Week %{x}<br>Workouts: %{y}<extra></extra>"
        ))
        
        # Determine last week and last weekly value
        last_week = part_data["Week"].max()
        last_value = part_data.loc[part_data["Week"] == last_week, "Value"].values[0]
        
        # Get goal information for this participant
        goal_info = goals_df[goals_df["Participant"] == participant]
        if goal_info.empty:
            continue
        end_week = float(goal_info["Duration (weeks)"].iloc[0])
        goal = float(goal_info["Goal"].iloc[0])
        
        # Calculate current cumulative total and remaining weeks
        current_cumulative = part_data["Value"].sum()
        remaining_weeks = end_week - last_week
        
        # Calculate the required new weekly rate to reach the goal
        if remaining_weeks > 0:
            required_rate = (goal - current_cumulative) / remaining_weeks
        else:
            required_rate = last_value  # or set to NaN
        
        # Build the projection line:
        # First point: last actual data point (last_week, last_value)
        # Second point: next week (last_week + 1, required_rate)
        # Third point: end of challenge (end_week, required_rate)
        proj_x = [last_week, last_week + 1, end_week]
        proj_y = [last_value, required_rate, required_rate]
        
        # Add the projection line trace (without a legend entry)
        fig.add_trace(go.Scatter(
            x=proj_x,
            y=proj_y,
            mode="lines",
            name="",  # No legend entry for projection line
            showlegend=False,
            line=dict(dash="dot", color=color),
            hoverinfo="skip"
        ))
    
    # Update layout
    fig.update_layout(
        title="Weekly Workouts with New Rate Projection",
        xaxis_title="Week",
        yaxis_title="Weekly Workouts",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)


#Line Plot #########################################################################################
def prepare_cumulative_data(data_df):
    """
    Prepares a DataFrame with cumulative weekly workouts for each participant.
    Ensures that each participant's data starts at (Week 0, Cumulative 0).
    """
    # Ensure Week is numeric
    data_df["Week"] = pd.to_numeric(data_df["Week"], errors="coerce")
    
    cumulative_list = []
    # Group by Participant and compute cumulative sum of 'Value'
    for participant, group in data_df.groupby("Participant"):
        group = group.sort_values("Week")
        cum_values = group["Value"].cumsum()
        weeks = group["Week"].tolist()
        # Prepend starting point (0, 0)
        weeks = [0] + weeks
        cum_values = [0] + cum_values.tolist()
        df_part = pd.DataFrame({
            "Participant": participant,
            "Week": weeks,
            "Cumulative": cum_values
        })
        cumulative_list.append(df_part)
    
    return pd.concat(cumulative_list, ignore_index=True)

def show_line_plot_with_projection(data_df, goals_df):
    """
    Creates a line plot using Plotly with:
      - x-axis as Week,
      - y-axis as cumulative workouts (Value) starting from (0,0),
      - For each participant, a projection line (dotted) from their current cumulative value
        to the challenge end (Duration (weeks), Goal) as defined in goals_df.
    """
    # Prepare the cumulative data
    cumulative_df = prepare_cumulative_data(data_df)
    
    # Create the base line plot for actual progress using Plotly Express
    fig = px.line(
        cumulative_df, 
        x="Week", 
        y="Cumulative", 
        color="Participant", 
        markers=True,
        title="Weekly Workouts & Projections"
    )
    
    # Add projection lines for each participant
    for participant in cumulative_df["Participant"].unique():
        # Extract participant's cumulative data
        part_data = cumulative_df[cumulative_df["Participant"] == participant]
        current_week = part_data["Week"].max()
        current_cum = part_data.loc[part_data["Week"] == current_week, "Cumulative"].values[0]
        
        # Get goal and challenge duration info for the participant from goals_df
        goal_info = goals_df[goals_df["Participant"] == participant]
        if not goal_info.empty:
            end_week = goal_info["Duration (weeks)"].values[0]
            goal = goal_info["Goal"].values[0]
            
            # Add a dotted projection line trace from current progress to end-of-challenge goal
            fig.add_trace(go.Scatter(
                x=[current_week, end_week],
                y=[current_cum, goal],
                mode="lines",
                name=f"{participant} Projection",
                line=dict(dash="dot")
            ))
    
    # Optionally, adjust the x-axis range if needed:
    # fig.update_xaxes(range=[0, max(end_week, cumulative_df["Week"].max()) + 1])
    
    st.plotly_chart(fig, use_container_width=True)



####################################################################################################
def display_group_metrics(data_df, goals_df):
    # Create columns dynamically based on the number of participants
    num_participants = len(data_df["Participant"].unique())
    
    
    # Total workouts ###############################################################################
    totals_df = data_df[["Participant", "Value"]].groupby("Participant").sum().reset_index(drop=False)
    st.header("Total Workouts")
    total_cols = st.columns(num_participants)
    for idx, row in totals_df.iterrows():
        with total_cols[idx]:
            st.metric(row["Participant"], row["Value"])

    # Average weekly workouts ######################################################################
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

    st.header("Average Weekly Workouts")
    avg_cols = st.columns(num_participants)
    for idx, (participant, row) in enumerate(metrics_df.iterrows()):
        with avg_cols[idx]:
            st.metric(participant, f"{row['Current Average']:.1f}", f"{row['Change']:.2f}")

    return None



####################################################################################################

def display_individual_metrics(data_df, goals_df):
    if st.session_state.challenge_period == "All": # Metrics for entire dataset
        display_group_metrics(data_df, goals_df)
        return None
    else:
        return None
    
####################################################################################################
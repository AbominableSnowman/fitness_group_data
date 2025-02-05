# %% Imports for google sheet extract
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import os

# Imports for plotting
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import numpy as np
from cycler import cycler
from matplotlib import colors as mcolors
import datetime
import seaborn as sns


# %% Functions
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"] # Scopes for read-only access to Google Sheets


from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_credentials():
    creds = None
    # Check if token.json exists
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            print("Credentials loaded from token.json")
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # Refresh expired credentials
                print("Credentials refreshed.")
        except RefreshError:
            print("Token is invalid or revoked. Reauthorizing...")
            creds = None  # Force reauthorization

    # If no valid credentials, reauthorize
    if not creds or not creds.valid:
        print("Reauthorizing...")
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        print("New credentials saved to token.json.")

    return creds




def extract_eu_data(data_range: str, goals_range: str, token_path="./fitness_group_eu/token.json"):
    """
    Extracts data and goals from a Google Sheets document as Pandas DataFrames.
    
    Args:
        data_range (str): The range of the "Data" sheet (e.g., 'Data!A1:Z100').
        goals_range (str): The range of the "Goals" sheet (e.g., 'Goals!A1:B10').
        token_path (str): Path to the token.json file for authentication.

    Returns:
        tuple: Two Pandas DataFrames (data_df, goals_df).
    """
    sheet_id = "15rtnqKhm25KOZ0UGZ4E2jzSaClvfpD8VhZXC8Z2ZWL8"
    # Load credentials
    creds = get_credentials()
    
    try:
        # Initialize the Sheets API
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        
        # Fetch data from the "Data" sheet
        data_result = sheet.values().get(spreadsheetId=sheet_id, range=data_range).execute()
        data_values = data_result.get("values", [])
        data_df = pd.DataFrame(data_values[1:], columns=data_values[0])  # Convert to DataFrame with headers
        
        # Fetch data from the "Goals" sheet
        goals_result = sheet.values().get(spreadsheetId=sheet_id, range=goals_range).execute()
        goals_values = goals_result.get("values", [])
        goals_df = pd.DataFrame(goals_values[1:], columns=goals_values[0])  # Convert to DataFrame with headers

        for col in data_df.columns[1:]:
            data_df[col] = pd.to_numeric(data_df[col])

        for col in goals_df.columns:
            goals_df[col] = pd.to_numeric(goals_df[col])
                
        return data_df, goals_df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None


def extract_us_data():

    return None


# %% Visualization functions
def adjust_positions(names, goals, separation=2):
    # Sort names and goals based on goals in descending order
    sorted_indices = sorted(range(len(goals)),
                            key=lambda k: goals[k], reverse=True)
    sorted_names = [names[i] for i in sorted_indices]
    sorted_goals = [goals[i] for i in sorted_indices]
    # Initialize previous y-position to the maximum possible y-position
    prev_y = max(goals)
    # Initialize dictionary to hold new y-positions
    new_positions = {}
    # For each name, adjust y-position based on required separation
    for name, goal in zip(sorted_names, sorted_goals):
        if name == sorted_names[0]:
            new_y = goal
        elif prev_y - goal < separation:
            new_y = prev_y - separation
        else:
            new_y = goal
        new_positions[name] = new_y
        prev_y = new_y
    return new_positions

def weekly_plot(challenge_period, data, goals, title=None):
    # Goals
    challenge_goals = goals.set_index('Challenge Period', drop=True).drop(columns=['Duration (weeks)']).loc[challenge_period].dropna()
    # Participants
    names = challenge_goals.index.to_list()

    # Challenge Data
    challenge_period_data = data[data['Challenge Period'] == challenge_period]
    challenge_data = challenge_period_data.set_index('Week Start', drop=True)[names].T
    challenge_data.replace("", np.nan, inplace=True)
    challenge_data.dropna(axis='index', how='all', inplace=True)

    # Challenge Duration
    tot_weeks = len(challenge_data.columns)
    weeks_cmpltd = len(challenge_data.dropna(
        axis='columns', how='all', inplace=False).columns)

    # Progress
    progress = challenge_data.sum(axis=1)
    percent_completed = challenge_data.sum(axis=1) / challenge_goals * 100


    colors = sns.color_palette("husl", len(names))


    fig, ax = plt.subplots(2, 1, figsize=(12, 10))

    # Subplot 1 (top) ##############################################################################
    ax[0].bar(names, [100]*len(names),color=colors, alpha=0.4, label='Goal')
    ax[0].bar(names, percent_completed, color=colors, label='Current Progress')

    # Goal & Progress Text 
    for i in range(len(names)):
        name = names[i]
        ax[0].text(i, percent_completed.loc[name], str(progress.loc[name]), color='black',
                    ha='center', va='bottom', fontweight='bold') # Progress label
        if percent_completed[name] < 100: # Goal label
            ax[0].text(i, 100, str(challenge_goals.loc[name]), color='black',
                        ha='center', va='bottom', fontweight='bold')

    # Subplot 2 (bottom) ###########################################################################
    new_positions = adjust_positions(names, challenge_goals.values, separation=4)
    for i in range(len(names)):
        name = names[i]
        # Line Plot ############################################################
        cum_progress = challenge_data.dropna(axis='columns', inplace=False).loc[name].cumsum()
        cum_progress = pd.concat([pd.Series([0]), cum_progress], ignore_index=True)

        if weeks_cmpltd == tot_weeks: # plot star points on last week
            ax[1].plot(cum_progress, c=colors[i], label=names[i],
                        marker='o', alpha=0.5)
            ax[1].scatter(tot_weeks, cum_progress.values[-1], color=colors[i], s=150,
                            alpha=0.5, marker='*')
        else:
            ax[1].plot(cum_progress, c=colors[i], label=names[i],
                        marker='o', alpha=0.5)

        # Projection Line 
        remaining = challenge_goals[name] - progress[name] # remaining # of exercises for goal
        remaining_weeks = tot_weeks - weeks_cmpltd
        if remaining_weeks > 0:
            # Calculate require rates to achieve goal
            start_rate = challenge_goals.loc[name] / (tot_weeks)
            req_rate = remaining / remaining_weeks
            projection = [cum_progress.values[-1] + req_rate * j \
                    for j in range(remaining_weeks+1)]
            prog_lbl_color = 'r' if req_rate > start_rate else 'k'
            # Plot projection line
            ax[1].plot(range(weeks_cmpltd, tot_weeks+1),  projection,
                        c=colors[i], linestyle='dashed', alpha=0.5)
            # Plot rate labels
            y = new_positions[name]
            ax[1].text(tot_weeks+1, y, f'{req_rate:.1f}/wk\n({names[i]})', ha='right',
                        va='center', alpha=0.5, color=prog_lbl_color, fontsize=9)
            
    ################################################################################################
    # Plot formatting & Saving
    ################################################################################################
    ax[0].set_ylabel('Percent Completed (%)')
    ax[0].set_title('Current Progress vs Goal')

    if remaining_weeks == 0:
        ax[1].legend()
    ax[1].yaxis.set_minor_locator(tck.AutoMinorLocator())
    ax[1].grid(which='both', alpha=0.2)
    ax[1].set_xticks(range(tot_weeks+1))
    ax[1].set_xticklabels(range(0, tot_weeks+1))
    ax[1].set_xlabel('Week')
    ax[1].set_ylabel('Cumulative Exercises')
    ax[1].set_title('Weekly Progress and Projections')

    if title is not None:
            plt.suptitle(title, fontsize=24)

    plt.tight_layout()
    plt.show()
    return fig, ax

# %% Testing
if __name__ == "__main__":
    DATA_RANGE = "Data!A1:L86"  # Adjust range as needed
    GOALS_RANGE = "Goals!A1:K13"  # Adjust range as needed

    data_df, goals_df = extract_eu_data(DATA_RANGE, GOALS_RANGE)

    print(data_df.head())  # Preview the "Data" sheet DataFrame
    print(goals_df.head())  # Preview the "Goals" sheet DataFrame


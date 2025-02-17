# %% Imports
import pandas as pd
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import streamlit as st
from dotenv import load_dotenv


# %% Functions
def get_credentials():
    service_account_info = st.secrets.service_account_info
    account_scopes = st.secrets["gsheet_config"]["account_scopes"]
    return Credentials.from_service_account_info(service_account_info, scopes=account_scopes)

#%%


def extract_eu_data():
    data_range = st.secrets["gsheet_config"]["EU_DATA_RANGE"]
    goals_range = st.secrets["gsheet_config"]["EU_GOALS_RANGE"]
    sheet_id = st.secrets["gsheet_config"]["EU_SHEET_ID"]
    creds = get_credentials()
    try:
        # Initialize the Sheets API
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        
        # Fetch data from the "Data" sheet
        data_result = sheet.values().get(spreadsheetId=sheet_id, range=data_range).execute()
        data_values = data_result.get("values", [])
        data_df = pd.DataFrame(data_values[1:], columns=data_values[0])
        
        # Fetch data from the "Goals" sheet
        goals_result = sheet.values().get(spreadsheetId=sheet_id, range=goals_range).execute()
        goals_values = goals_result.get("values", [])
        goals_df = pd.DataFrame(goals_values[1:], columns=goals_values[0])  
                
        return data_df, goals_df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
    
def clean_and_transform_eu_data(data_df, goals_df):
    """
    Input schema for data_df:
    | Week Start | Challenge Period | Week | Participant 1 | Participant 2 | ... | Participant N |

    End schema for melted_data:
    | Week Start | Challenge Period | Week | Participant | Metric | Value |
    
    End schema for melted_goals:
    | Challenge Period | Duration (weeks) | Participant | Goal |
    """
    # EU Data - Type conversion
    fields = ["Week Start", "Challenge Period", "Week"]
    participants = [ele for ele in data_df.columns if ele not in fields]

    data_df.dropna(axis=0, how="any", subset=fields, inplace=True)
    data_df["Week Start"] = pd.to_datetime(data_df["Week Start"], format="%Y-%m-%d")
    data_df["Challenge Period"] = data_df["Challenge Period"].astype(str)
    data_df["Week"] = data_df["Week"].astype(str)
    
    for col in participants: # Participant columns
        data_df[col] = pd.to_numeric(data_df[col])

    # EU Goals - Type conversion
    goals_df["Challenge Period"] = goals_df["Challenge Period"].astype(str)
    goals_df["Duration (weeks)"] = pd.to_numeric(goals_df["Duration (weeks)"])
    other_goal_cols = [ele for ele in goals_df.columns if ele not in ["Challenge Period",
                                                                      "Duration (weeks)"]]
    for col in other_goal_cols: # Participant columns
        goals_df[col] = pd.to_numeric(goals_df[col])

    melted_data = data_df.melt(id_vars=["Week Start", "Challenge Period", "Week"], 
                               var_name="Participant", value_name="Value").dropna(axis=0, 
                                                                                  how="any")
    
    melted_data["Metric"] = "Total Exercise"
    melted_data = melted_data[["Week Start", "Challenge Period", "Week", 
                               "Participant", "Metric", "Value"]]
    

    melted_goals = goals_df.melt(id_vars=["Challenge Period", "Duration (weeks)"], 
                                 var_name="Participant", value_name="Goal").dropna(axis=0, 
                                                                                   how="any")

    return melted_data, melted_goals

@st.cache_data
def load_eu_data():
    data_df, goals_df = extract_eu_data()
    melted_data, melted_goals = clean_and_transform_eu_data(data_df, goals_df)
    return melted_data, melted_goals


#%%
def extract_us_data():
    data_range = st.secrets["gsheet_config"]["US_DATA_RANGE"]
    goals_range = st.secrets["gsheet_config"]["US_GOALS_RANGE"]

    sheet_id = st.secrets["gsheet_config"]["US_SHEET_ID"]
    creds = get_credentials()
    try:
        # Initialize the Sheets API
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        
        # Fetch data from the "Data" sheet
        data_result = sheet.values().get(spreadsheetId=sheet_id, range=data_range).execute()
        data_values = data_result.get("values", [])
        data_df = pd.DataFrame(data_values[1:], columns=data_values[0])
        
        # Fetch data from the "Goals" sheet
        goals_result = sheet.values().get(spreadsheetId=sheet_id, range=goals_range).execute()
        goals_values = goals_result.get("values", [])
        goals_df = pd.DataFrame(goals_values[1:], columns=goals_values[0])  
                
        return data_df, goals_df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
    return None

#%%

def clean_and_transform_us_data(data_df, goals_df):
    # Data
    cleaned_data = data_df.copy()
    cleaned_goals = goals_df.copy()

    cleaned_data["Value"] = cleaned_data["Value"].astype(float)
    cleaned_data["Week Start"] = pd.to_datetime(cleaned_data["Week Start"])

    # Goal data
    cleaned_goals["Goal"] = cleaned_goals["Goal"].astype(float)

    return cleaned_data, cleaned_goals


@st.cache_data
def load_us_data():
    data_df, goals_df = extract_us_data()
    cleaned_data, cleaned_goals = clean_and_transform_us_data(data_df, goals_df)
    return cleaned_data, cleaned_goals




def clean_and_transform_us_data_old(data_df, goals_df):
    # Data
    data_df = data_df[["Challenge", "Week", "Week Start", "Participant", 
                       "Cardio", "Resistance Training", "Steps", "Weight", 
                       "Distance (miles)", "Alcohol"]]

    melted_df = data_df.melt(id_vars=["Challenge", "Week", "Participant", "Week Start"], 
                             var_name="Metric", value_name="Value")
    melted_df = melted_df.sort_values(by=["Week Start", "Challenge", "Week", "Participant"], 
                                      axis=0).reset_index(drop=True)

    # Goals
    melted_goals = goals_df.melt(id_vars=["Challenge", "Participant"], 
                                 var_name="Goal Type", value_name="Goal")
    melted_goals.sort_values(by=["Challenge", "Participant", "Goal Type"], axis=0, inplace=True)
    melted_goals.reset_index(drop=True, inplace=True)

    return melted_df, melted_goals
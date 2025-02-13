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
    data_df["Week Start"] = pd.to_datetime(data_df["Week Start"])
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

    return None

def clean_and_transform_us_data():
    return None

# @st.cache_data
def load_us_data():
    return None
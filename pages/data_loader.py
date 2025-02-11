# %% Imports
import pandas as pd
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import streamlit as st
from dotenv import load_dotenv


# %% Functions
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = "../credentials/service-account-key.json"

def get_credentials():
    return Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def extract_eu_data():
    # Load variables and credentials
    data_range = os.getenv("EU_DATA_RANGE")
    goals_range = os.getenv("EU_GOALS_RANGE")
    sheet_id = os.getenv("EU_SHEET_ID")
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

        # EU Data - Type conversion
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


# %% Load data
@st.cache_data
def load_data():
    df = pd.read_excel('../DATA/fitness_groups/old_data/data_us.xlsx')
    df = df[['Participant', 'Week Start', 'Cardio',
        'Resistance Training', 'Steps', 'Weight',
        'Distance (miles)', 'Alcohol']].dropna(axis='index',how='any')

    grouped = df[['Participant', 'Week Start', 'Cardio', 
        'Resistance Training']].groupby(['Participant', 'Week Start']).sum().sum(axis='columns')

    grouped = grouped.reset_index().rename(columns={0:'Total'})

    return grouped



# %%
if __name__ == 'main':
    from dotenv import load_dotenv
    # Load environment variables
    load_dotenv()
    data_df, goals_df = extract_eu_data()



# %%

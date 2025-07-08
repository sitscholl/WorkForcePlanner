import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import streamlit as st

from typing import Optional, Dict
import os

from .base import BaseRawDataPipeline

GOOGLE_SHEETS_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

COLUMN_MAPPING = {
    "Wiesenabschnitt": "Field",
    "Sorte": "Variety",
    "Jahr": "Year",
    "Pflanzalter": "Tree Age",
    "Baumhöhe": "Tree Height",
    "Pflückgänge": "Harvest rounds",
    "Vor Zupfen [n/Wiese]": "Count Zupfen",
    "Nach Zupfen [n/Wiese]": "Count Ernte",
    "Zupfen [h]": "Hours Zupfen",
    "Ernte [h]": "Hours Ernte",
    #"_Zupfen [h]": "_Hours Zupfen",
    #"_Ernte [h]": "_Hours Ernte"
}

class GoogleSheetsHandler(BaseRawDataPipeline):
    """Handle Google Sheets data loading"""
    
    def __init__(self):
        self.client = None
        self.credentials = None

    def transform(self, raw_data) -> pd.DataFrame:

        try:
            # Convert to DataFrame
            df = pd.DataFrame(raw_data)
                       
            # Rename columns to standard names
            df = df.rename(columns=COLUMN_MAPPING)
            df = df[list(COLUMN_MAPPING.values())].copy()

            #Transform to numeric
            for col in ['Tree Height', 'Hours Zupfen', 'Hours Ernte', 'Count Zupfen', 'Count Ernte']:
                df[col] = pd.to_numeric(df[col])
                        
            # Remove rows with invalid data
            #df = df.dropna(subset=['field_name', 'required_hours'])
            #df = df[df['required_hours'] > 0]
            
            if df.empty:
                st.warning("No valid field data found after cleaning")
                return None
            
            return df
            
        except Exception as e:
            st.error(f"Error transforming gsheets data: {str(e)}")
            return None

    def load(self, spreadsheet_url: str, worksheet_name: str = None) -> Optional[pd.DataFrame]:
        try:
            if self.client is None:
                st.error("Google Sheets client not initialized")
                st.stop()
            
            # Extract spreadsheet ID from URL if needed
            if 'docs.google.com' in spreadsheet_url:
                spreadsheet_id = spreadsheet_url.split('/d/')[1].split('/')[0]
            else:
                spreadsheet_id = spreadsheet_url
            
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Get the worksheet
            if worksheet_name:
                worksheet = spreadsheet.worksheet(worksheet_name)
            else:
                worksheet = spreadsheet.get_worksheet(0)  # First worksheet
            
            # Get all values
            data = worksheet.get_all_records()
            
            if not data:
                st.warning("No data found in the spreadsheet")
                return None

            return data
                
        except Exception as e:
            st.error(f"Error loading data from Google Sheets: {str(e)}")
            st.stop()
            
    def setup_credentials_from_file(self, credentials_file: str) -> bool:
        """
        Setup Google Sheets credentials from file
        
        Args:
            credentials_file: Path to credentials JSON file
            
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            if not os.path.exists(credentials_file):
                st.error(f"Credentials file '{credentials_file}' does not exist.")
                st.stop()
                
            self.credentials = Credentials.from_service_account_file(
                credentials_file, scopes=GOOGLE_SHEETS_SCOPES
            )
            
            self.client = gspread.authorize(self.credentials)

            # st.success('Loaded gsheets credentials from file!')
            
        except Exception as e:
            st.error(f"Error setting up credentials from file: {str(e)}")
            return False
            
    def get_spreadsheet_info(self, spreadsheet_url: str) -> Optional[Dict]:
        """
        Get information about a spreadsheet
        
        Args:
            spreadsheet_url: URL or ID of the Google Spreadsheet
            
        Returns:
            dict: Information about the spreadsheet or None if error
        """
        try:
            if self.client is None:
                st.error("Google Sheets client not initialized")
                st.stop()
            
            # Extract spreadsheet ID from URL if needed
            if 'docs.google.com' in spreadsheet_url:
                spreadsheet_id = spreadsheet_url.split('/d/')[1].split('/')[0]
            else:
                spreadsheet_id = spreadsheet_url
            
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Get worksheet names
            worksheets = [ws.title for ws in spreadsheet.worksheets()]
            
            return {
                'title': spreadsheet.title,
                'worksheets': worksheets,
                'url': spreadsheet.url
            }
            
        except Exception as e:
            st.error(f"Error getting spreadsheet info: {str(e)}")
            return None

if __name__ == '__main__':
    gsheets = GoogleSheetsHandler()
    gsheets.setup_credentials_from_file('gsheets_creds.json')
    field_data = gsheets.run(
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1l8lHoWk1VBZ0tzLOQ6JXGxVbD7B37CIN2xbysK_JDCA/edit", 
        worksheet_name = "Wiesen"
        )
    

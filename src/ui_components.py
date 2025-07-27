import streamlit as st
import pandas as pd

from datetime import datetime

def render_sidebar(config):
    """Render the sidebar with current configuration settings.
    
    This function displays the current settings from the config file in a nicely
    formatted way in the sidebar. It can be imported and used across all pages of the app.
    
    Args:
        config (dict): The configuration dictionary loaded from config.yaml
    """
    with st.sidebar:
        st.title("Current Settings")
        
        # General Settings Section
        st.subheader("General Settings")
        st.info(f"**Year:** {config.get('year', 'Not set')}")
        st.info(f"**Model:** {config.get('param_name', 'Not set')}")

        start_date = config.get('start_date', {})
        st.subheader(f"**Start Dates:**")
        for group, date in start_date.items():
            st.info(f"**{group.capitalize()}:** {date}")
        
        # Google Sheets Section
        if 'gsheets' in config:
            with st.expander("Google Sheets"):
                st.write(f"**Worksheet:** {config['gsheets'].get('worksheet_name', 'Not set')}")
                
                # Show truncated URL for better display
                url = config['gsheets'].get('spreadsheet_url', '')
                if url:
                    display_url = url[:30] + '...' if len(url) > 30 else url
                    st.write(f"**URL:** {display_url}")
        
        # Model Information Section
        model_name = config.get('param_name')
        if model_name and model_name in config:
            with st.expander(f"{model_name} Model Details"):
                # Show target
                st.write(f"**Target:** {config['models'][model_name].get('target', 'Not set')}")
                
                # Show predictors in a compact way
                predictors = config['models'][model_name].get('predictors', [])
                if predictors:
                    st.write("**Predictors:**")
                    for pred in predictors:
                        st.write(f"- {pred}")
                
                # Show CV method
                st.write(f"**CV Method:** {config['models'][model_name].get('cv_method', 'Not set')}")
        
        # Add a link to the settings page
        st.divider()
        st.write("Need to change settings? [Go to Settings Page](/Settings)")

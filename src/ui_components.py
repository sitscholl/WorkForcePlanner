import streamlit as st

from datetime import datetime

def render_parameter_selection():
    with st.sidebar:
        param_name = st.selectbox("What would you like to model", ("Ernte", "Zupfen"), key = 'param_name')
        year = st.number_input("Year", value=datetime.now().year, min_value=2020, key = 'model_year')
        start_date = st.date_input("Starting date", value=datetime(2025, 9, 1), key = 'work_start_date')
    
    return param_name, year, start_date

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
        st.info(f"**Start Date:** {config.get('start_date', 'Not set')}")
        st.info(f"**Model:** {config.get('param_name', 'Not set')}")
        
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
                st.write(f"**Target:** {config[model_name].get('target', 'Not set')}")
                
                # Show predictors in a compact way
                predictors = config[model_name].get('predictors', [])
                if predictors:
                    st.write("**Predictors:**")
                    for pred in predictors:
                        st.write(f"- {pred}")
                
                # Show CV method
                st.write(f"**CV Method:** {config[model_name].get('cv_method', 'Not set')}")
        
        # Add a link to the settings page
        st.divider()
        st.write("Need to change settings? [Go to Settings Page](/Settings)")
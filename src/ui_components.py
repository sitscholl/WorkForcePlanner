import streamlit as st

from datetime import datetime

def render_parameter_selection():
    with st.sidebar:
        param_name = st.selectbox("What would you like to model", ("Ernte", "Zupfen"), key = 'param_name')
        year = st.number_input("Year", value=datetime.now().year, min_value=2020, key = 'model_year')
        start_date = st.date_input("Starting date", value=datetime(2025, 9, 1), key = 'work_start_date')
    
    return param_name, year, start_date
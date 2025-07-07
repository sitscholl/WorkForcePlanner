import streamlit as st

from pathlib import Path
from datetime import datetime, time

from src.config import load_config
from src.utils import load_data, clean_data, load_workforce, train_model
from src.planner.scheduler import schedule_field_work
from src.plot import create_timeline_chart

# --- Select Parameters ---
param_name = st.selectbox(
    "What would you like to model",
    ("Ernte", "Zupfen"),
)
year = st.number_input(
    label = 'Which year would you like to model?', 
    value = datetime.now().year, 
    min_value = 2020, 
    step = 1)
start_date = st.date_input('Starting date for work', value = datetime(2025, 9, 1, 8, 0))
start_date = datetime.combine(start_date, time(hour = 8))

st.session_state.param_name = param_name
st.session_state.year = year

# --- Load configuration ---
if 'config' not in st.session_state:
    st.session_state.config = load_config('config.yaml')

# --- Load data and model ---
if 'data' not in st.session_state:
    with st.spinner("Loading data from google sheets..."):
        data_raw = load_data(st.session_state.config, param_name)
        data_clean = clean_data(data_raw, st.session_state.config, param_name)
        st.session_state.data = data_clean
        st.session_state.data_raw = data_raw

if 'predictor' not in st.session_state:
    with st.spinner("Training model..."):
        predictor = train_model(st.session_state.config, param_name, st.session_state.data)
        st.session_state.predictor = predictor

# --- Predict ---
data_to_predict = st.session_state.data_raw.loc[st.session_state.data_raw['Year'] == year]
data_to_predict = clean_data(data_to_predict, st.session_state.config, param_name, include_target=False)
if data_to_predict.empty:
    st.error('No data available for the selected year.')
data_to_predict['predicted_hours'] = st.session_state.predictor.predict(data_to_predict)
st.session_state.data_to_predict = data_to_predict

# --- Load workforce ---
workforce_file = Path(st.session_state.config['workforce_file'])
if 'workforce' not in st.session_state:
    st.session_state.workforce = load_workforce(workforce_file)

schedule_df = schedule_field_work(
        field_table=st.session_state.data_to_predict,
        workforce=st.session_state.workforce,
        start_date=start_date,
        field_order_column='Field',
        hours_column='predicted_hours'
        )

timeline_fig = create_timeline_chart(schedule_df, datetime.now())
st.plotly_chart(timeline_fig, use_container_width=True)
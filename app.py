import streamlit as st

from pathlib import Path
from datetime import datetime

from src.config import load_config
from src.utils import load_data_and_train_model, load_workforce
from src.planner.scheduler import schedule_field_work
from src.plot import create_timeline_chart

# --- Select Parameter ---
param_name =  st.selectbox(
    "What would you like to model",
    ("Ernte", "Zupfen"),
)
st.session_state.param_name = param_name

# --- Load configuration ---
if 'config' not in st.session_state:
    st.session_state.config = load_config('config.yaml')

# --- Load data and model ---
if 'predictor' not in st.session_state or 'data' not in st.session_state:
    with st.spinner("Loading data and training model..."):
        predictor, data = load_data_and_train_model(st.session_state.config, param_name)
        st.session_state.predictor = predictor
        st.session_state.data = data

# --- Load workforce ---
workforce_file = Path(st.session_state.config['workforce_file'])
if 'workforce' not in st.session_state:
    st.session_state.workforce = load_workforce(workforce_file)

schedule_df = schedule_field_work(
        field_table=st.session_state.data,
        workforce=st.session_state.workforce,
        start_date=datetime(2025, 9, 1, 8, 0),
        field_order_column='Field',
        hours_column='predicted_hours'
        )

timeline_fig = create_timeline_chart(schedule_df, datetime(2025, 9, 10, 10, 0))
st.plotly_chart(timeline_fig, use_container_width=True)
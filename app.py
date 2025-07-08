import streamlit as st

from datetime import datetime

from src.app_state import load_config, load_workforce, load_and_clean_data, get_trained_model, get_predictions
from src.planner.scheduler import schedule_field_work
from src.plot import create_timeline_chart
from src.ui_components import render_sidebar

# Set page title
st.set_page_config(page_title="Workforce Planner", page_icon="📊")
st.title("Workforce Planner")

# --- Load  ---
config = load_config("config.yaml")

# --- Render Sidebar ---
render_sidebar(config)

# --- Load Data and Models ---
workforce = load_workforce(config)
data_raw, data_clean = load_and_clean_data(config, config['param_name'])
model = get_trained_model(config, config['param_name'], data_clean)
predictions = get_predictions(config, config['param_name'], model, data_raw, config['year'])

# --- Main Content ---
st.header(f"Schedule for {config['year']}")
st.write(f"Using model: {config['param_name']}")

# --- Schedule ---
schedule_df = schedule_field_work(
        field_table=predictions,
        workforce=workforce,
        start_date=config['start_date'],
        field_order_column='Field',
        hours_column='predicted_hours'
        )

timeline_fig = create_timeline_chart(schedule_df, datetime.now())
st.plotly_chart(timeline_fig, use_container_width=True)
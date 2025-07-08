import streamlit as st

from datetime import datetime

from src.app_state import load_config, load_workforce, load_and_clean_data, get_trained_model, get_predictions
from src.planner.scheduler import schedule_field_work
from src.plot import create_timeline_chart
from src.ui_components import render_parameter_selection

# --- Select Parameters ---
param_name, year, start_date = render_parameter_selection()

# --- Load  ---
config = load_config("config.yaml")
workforce = load_workforce(config)
data_raw, data_clean = load_and_clean_data(config, param_name)
model = get_trained_model(config, param_name, data_clean)
predictions = get_predictions(config, param_name, model, data_raw, year)

# --- Schedule ---
schedule_df = schedule_field_work(
        field_table=predictions,
        workforce=workforce,
        start_date=start_date,
        field_order_column='Field',
        hours_column='predicted_hours'
        )

st.markdown('---')
st.subheader("📆 Labour Timeline")
timeline_fig = create_timeline_chart(schedule_df, datetime.now())
st.plotly_chart(timeline_fig, use_container_width=True)

st.markdown('---')
st.subheader("💾 Fields Data")
st.dataframe(schedule_df)
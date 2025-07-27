import streamlit as st

from datetime import datetime

from src.app_state import load_config, load_workforce, load_and_clean_data, get_trained_model, get_predictions, load_field_collection
from src.planner.scheduler import schedule_field_work
from src.plot import create_timeline_chart
from src.ui_components import render_sidebar

# Set page title
st.set_page_config(page_title="Workforce Planner", page_icon="📊")
st.title("Workforce Planner")

# --- Load  ---
config = load_config("config.yaml")
st.header(f"Schedule for {config['year']}")
st.write(f"Using model: {config['param_name']}")

# --- Render Sidebar ---
render_sidebar(config)

# --- Load Data and Models ---
workforce = load_workforce(config)
if len(workforce.get_workers()) == 0:
        st.warning("No workers available. Please update the workforce data.")
        st.stop()
field_collection = load_field_collection(config)
if len(field_collection.get_fields()) == 0:
        st.warning("No fields available. Please update the FieldCollection data.")
        st.stop()

data_raw, data_clean = load_and_clean_data(config, config['param_name'])
model = get_trained_model(config, config['param_name'], data_clean)
predictions = get_predictions(config, config['param_name'], model, data_raw, config['year'])
predictions_config = field_collection.apply_field_config(predictions)

# --- Main Content ---

# --- Schedule ---
# Convert start_date strings to datetime objects if they're in dictionary format
start_dates = config['start_date']
if isinstance(start_dates, dict):
    # Convert string dates to datetime objects
    start_dates_converted = {}
    for group, date_str in start_dates.items():
        if isinstance(date_str, str):
            start_dates_converted[group] = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            start_dates_converted[group] = date_str
    start_dates = start_dates_converted

schedule_df = schedule_field_work(
        field_table=predictions_config,
        workforce=workforce,
        start_date=start_dates,
        field_order_column='Field',
        group_name='Variety Group',
        hours_column='predicted_hours'
        )

st.markdown('---')
st.subheader("📆 Labour Timeline")
group_names = list(schedule_df['Variety Group'].unique())
tabs = st.tabs(group_names)
for tab, group_name in zip(tabs, group_names):
    with tab:
        group_data = schedule_df[schedule_df['Variety Group'] == group_name]
        timeline_fig = create_timeline_chart(group_data, datetime.now())
        st.plotly_chart(timeline_fig, use_container_width=True)
st.markdown('---')
st.subheader("💾 Fields Data")
st.dataframe(schedule_df)

st.markdown('---')
with st.expander("Raw data"):
        st.dataframe(data_raw.loc[data_raw['Year'] == config['year']])
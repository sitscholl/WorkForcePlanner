import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

from pathlib import Path

from src.app_state import load_config, load_workforce
from src.worker import Worker, Workforce
from src.ui_components import render_sidebar

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Set page title
st.set_page_config(page_title="Workforce Management", page_icon="👥")
st.title("Workforce Management")

# --- Load  ---
config = load_config("config/config.yaml")

# --- Render Sidebar ---
render_sidebar(config)

workforce = load_workforce(config)
workforce_file = Path("config", f"Workforce_{config['year']}.yaml")

# --- Manual Load from Uploaded YAML (overwrites current) ---
st.header("Persistence")
uploaded_file = st.file_uploader("Load Workforce from YAML", type=["yaml", "yml"])
if uploaded_file is not None:
    with open(workforce_file, "wb") as f:
        f.write(uploaded_file.read())
    workforce = Workforce.load(filename = workforce_file)
    st.success("Workforce loaded from YAML!")
    workforce.save(workforce_file)

# --- Download current workforce ---
if workforce_file.exists():
    with open(workforce_file, "rb") as f:
        st.download_button(
            label="Download Current Workforce YAML",
            data=f,
            file_name="workforce.yaml",
            mime="application/x-yaml"
        )

# --- Add Worker ---
st.header("Add New Worker")
with st.form("add_worker_form"):
    new_name = st.text_input("Name")
    new_start_date = st.date_input("Start Date")
    new_end_date = st.date_input("End Date")
    new_work_days = st.multiselect("Working Days", options=DAYS_OF_WEEK, default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    new_work_hours = st.number_input("Hours Per Day", min_value=1.0, max_value=24.0, value=9.0, step=0.5)
    new_payment = st.number_input("Payment", min_value = 0.0, step = .5)
    submitted = st.form_submit_button("Add Worker")
    if submitted:
        if new_name and new_work_hours and new_work_days and new_payment:
            worker = Worker(
                name = new_name, 
                start_date = new_start_date,
                end_date = new_end_date,
                work_hours = new_work_hours, 
                work_days = new_work_days, 
                payment=new_payment, 
            )
            workforce.add_worker(worker)
            workforce.save(workforce_file)
            st.success(f"Added worker: {new_name}")
            st.rerun()  # Force rerun to refresh the worker list
        else:
            st.error("Please fill in all fields.")

# --- List and Modify Workers ---
st.header("Current Workforce")
workers = workforce.get_workers()
if not workers:
    st.info("No workers in the workforce.")
else:
    for i, worker in enumerate(workers):
        # Use a combination of index and name for more stability
        worker_key = f"{i}_{worker.name}"
        with st.expander(f"Worker: {worker.name}"):
            new_name = st.text_input("Name", value=worker.name, key=f'update_name_{worker_key}')
            new_start_date = st.date_input("Start Date", value = worker.start_date, key=f'update_start_date_{worker_key}')
            new_end_date = st.date_input("End Date", value = worker.end_date, key=f'update_end_date_{worker_key}')
            new_work_days = st.multiselect(
                "Working Days",
                options=DAYS_OF_WEEK,
                default=worker.work_days,  # Use the worker's current days
                key=f'update_work_days_{worker_key}'
            )
            new_work_hours = st.number_input(
                "Hours Per Day",
                min_value=1.0,
                max_value=24.0,
                value=float(worker.work_hours),  # Use the worker's current hours
                step=0.5,
                key=f'update_work_hours_{worker_key}'
            )
            new_payment = st.number_input("Payment", min_value = 0.0, step = .5, value=float(worker.payment), key=f'update_payment_{worker_key}')
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_{worker_key}"):
                    updated_worker = Worker(
                        name=new_name,
                        start_date = new_start_date,
                        end_date = new_end_date,
                        work_hours=new_work_hours,
                        work_days=new_work_days,
                        payment=new_payment,
                    )
                    workforce.update_worker(worker.name, updated_worker)
                    workforce.save(workforce_file)
                    st.success(f"Updated worker {worker.name}")
                    st.rerun()  # Force rerun to refresh the worker list
            with col2:
                if st.button("Remove", key=f"remove_{worker_key}"):
                    workforce.remove_worker(worker.name)
                    workforce.save(workforce_file)
                    st.warning(f"Removed worker {worker.name}")
                    st.rerun()  # Force rerun to refresh the worker list

# --- Daily Work Hours Visualization ---
st.header("Daily Work Hours Overview")
workers = workforce.get_workers()

if workers:
    # Find the date range across all workers
    start_dates = [worker.start_date.date() if hasattr(worker.start_date, 'date') else worker.start_date for worker in workers]
    end_dates = [worker.end_date.date() if hasattr(worker.end_date, 'date') else worker.end_date for worker in workers]
    
    overall_start = min(start_dates)
    overall_end = max(end_dates)
    
    # Generate all dates in the range
    dates = []
    daily_hours = []
    current_date = overall_start
    
    while current_date <= overall_end:
        dates.append(current_date)
        daily_hours.append(workforce.get_daily_work_hours(current_date))
        current_date += timedelta(days=1)
    
    # Create DataFrame for Plotly
    df = pd.DataFrame({
        'Date': dates,
        'Daily Work Hours': daily_hours
    })
    
    # Create the bar plot
    fig = px.bar(
        df, 
        x='Date', 
        y='Daily Work Hours',
        title='Daily Work Hours Over Time',
        labels={'Daily Work Hours': 'Total Daily Work Hours'},
        color='Daily Work Hours',
        color_continuous_scale='viridis'
    )
    
    # Customize the layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Daily Work Hours",
        showlegend=False,
        height=500
    )
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Display some summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Days", len(dates))
    with col2:
        st.metric("Average Daily Hours", f"{sum(daily_hours) / len(daily_hours):.1f}")
    with col3:
        st.metric("Peak Daily Hours", max(daily_hours))
        
else:
    st.info("Add workers to see the daily work hours visualization.")
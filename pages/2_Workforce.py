import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

from pathlib import Path

from src.app_state import load_config, load_workforce
from src.worker import Worker, Workforce, WorkPeriod
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
    new_payment = st.number_input("Payment", min_value=0.0, step=0.5)
    
    st.subheader("Initial Work Period")
    new_start_date = st.date_input("Start Date")
    new_end_date = st.date_input("End Date")
    new_work_days = st.multiselect("Working Days", options=DAYS_OF_WEEK, default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    new_work_hours = st.number_input("Hours Per Day", min_value=1.0, max_value=24.0, value=9.0, step=0.5)
    
    submitted = st.form_submit_button("Add Worker")
    if submitted:
        if new_name and new_work_hours and new_work_days and new_payment is not None:
            # Create initial work period
            initial_work_period = WorkPeriod(
                start_date=datetime.combine(new_start_date, datetime.min.time()),
                end_date=datetime.combine(new_end_date, datetime.min.time()),
                work_hours=new_work_hours,
                work_days=new_work_days
            )
            
            worker = Worker(
                name=new_name,
                work_periods=[initial_work_period],
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
            # Basic worker info
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name", value=worker.name, key=f'update_name_{worker_key}')
            with col2:
                new_payment = st.number_input("Payment", min_value=0.0, step=0.5, value=float(worker.payment or 0), key=f'update_payment_{worker_key}')
            
            # Work periods management
            st.subheader("Work Periods")
            
            # Display existing work periods
            if worker.work_periods:
                for period_idx, period in enumerate(worker.work_periods):
                    period_key = f"{worker_key}_period_{period_idx}"
                    with st.container():
                        st.write(f"**Period {period_idx + 1}:**")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            period_start = st.date_input(
                                "Start Date", 
                                value=period.start_date.date(), 
                                key=f'period_start_{period_key}'
                            )
                        with col2:
                            period_end = st.date_input(
                                "End Date", 
                                value=period.end_date.date(), 
                                key=f'period_end_{period_key}'
                            )
                        with col3:
                            period_hours = st.number_input(
                                "Hours/Day", 
                                min_value=1.0, 
                                max_value=24.0, 
                                value=float(period.work_hours), 
                                step=0.5,
                                key=f'period_hours_{period_key}'
                            )
                        with col4:
                            if st.button("Remove Period", key=f'remove_period_{period_key}'):
                                worker.remove_work_period(period_idx)
                                workforce.save(workforce_file)
                                st.success(f"Removed work period {period_idx + 1}")
                                st.rerun()
                        
                        period_days = st.multiselect(
                            "Working Days",
                            options=DAYS_OF_WEEK,
                            default=period.work_days,
                            key=f'period_days_{period_key}'
                        )
                        
                        # Update period button
                        if st.button("Update Period", key=f'update_period_{period_key}'):
                            try:
                                updated_period = WorkPeriod(
                                    start_date=datetime.combine(period_start, datetime.min.time()),
                                    end_date=datetime.combine(period_end, datetime.min.time()),
                                    work_hours=period_hours,
                                    work_days=period_days
                                )
                                worker.work_periods[period_idx] = updated_period
                                worker.work_periods.sort(key=lambda p: p.start_date)
                                workforce.save(workforce_file)
                                st.success(f"Updated work period {period_idx + 1}")
                                st.rerun()
                            except ValueError as e:
                                st.error(f"Error updating work period: {e}")
                        
                        st.divider()
            else:
                st.info("No work periods defined for this worker.")
            
            # Add new work period
            with st.expander("Add New Work Period"):
                add_period_key = f"add_period_{worker_key}"
                
                col1, col2 = st.columns(2)
                with col1:
                    add_start_date = st.date_input("Start Date", key=f'add_start_{add_period_key}')
                with col2:
                    add_end_date = st.date_input("End Date", key=f'add_end_{add_period_key}')
                
                col1, col2 = st.columns(2)
                with col1:
                    add_work_hours = st.number_input("Hours Per Day", min_value=1.0, max_value=24.0, value=9.0, step=0.5, key=f'add_hours_{add_period_key}')
                with col2:
                    add_work_days = st.multiselect("Working Days", options=DAYS_OF_WEEK, default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], key=f'add_days_{add_period_key}')
                
                if st.button("Add Work Period", key=f'add_period_btn_{add_period_key}'):
                    if add_work_days and add_work_hours:
                        try:
                            new_period = WorkPeriod(
                                start_date=datetime.combine(add_start_date, datetime.min.time()),
                                end_date=datetime.combine(add_end_date, datetime.min.time()),
                                work_hours=add_work_hours,
                                work_days=add_work_days
                            )
                            worker.add_work_period(new_period)
                            workforce.save(workforce_file)
                            st.success("Added new work period")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Error adding work period: {e}")
                    else:
                        st.error("Please fill in all fields for the work period.")
            
            # Worker actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Update Worker Info", key=f"update_{worker_key}"):
                    # Update basic worker info (name and payment)
                    worker.name = new_name
                    worker.payment = new_payment
                    workforce.save(workforce_file)
                    st.success(f"Updated worker {worker.name}")
                    st.rerun()
            
            with col2:
                if st.button("Remove Worker", key=f"remove_{worker_key}"):
                    workforce.remove_worker(worker.name)
                    workforce.save(workforce_file)
                    st.warning(f"Removed worker {worker.name}")
                    st.rerun()
            
            with col3:
                # Show work periods summary
                if st.button("Show Summary", key=f"summary_{worker_key}"):
                    st.info(worker.get_work_periods_summary())

# --- Daily Work Hours Visualization ---
st.header("Daily Work Hours Overview")
workers = workforce.get_workers()

if workers:
    # Find the date range across all workers
    overall_start, overall_end = workforce.get_employment_date_range()
    
    if overall_start and overall_end:
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
        st.info("No work periods defined for any workers.")
        
else:
    st.info("Add workers to see the daily work hours visualization.")
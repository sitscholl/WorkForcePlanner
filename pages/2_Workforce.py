import streamlit as st

from pathlib import Path

from src.worker import Worker, Workforce

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
workforce_file = Path(st.session_state.config['workforce_file'])

def save_workforce():
    st.session_state.workforce.save(workforce_file)

def get_workers():
    return st.session_state.workforce.get_workers()

st.title("Workforce Management")

# --- Manual Load from Uploaded YAML (overwrites current) ---
st.header("Persistence")
uploaded_file = st.file_uploader("Load Workforce from YAML", type=["yaml", "yml"])
if uploaded_file is not None:
    with open(workforce_file, "wb") as f:
        f.write(uploaded_file.read())
    st.session_state.workforce = Workforce.load(filename = workforce_file)
    st.success("Workforce loaded from YAML!")
    save_workforce()

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
    new_payment = st.text_input("Payment")
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
            st.session_state.workforce.add_worker(worker)
            save_workforce()
            st.success(f"Added worker: {new_name}")
            st.rerun()  # Force rerun to refresh the worker list
        else:
            st.error("Please fill in all fields.")

# --- List and Modify Workers ---
st.header("Current Workforce")
workers = get_workers()
if not workers:
    st.info("No workers in the workforce.")
else:
    for i, worker in enumerate(workers):
        with st.expander(f"Worker: {worker.name}"):
            new_name = st.text_input("Name", value=worker.name, key=f'update_name_{i}')
            new_start_date = st.date_input("Start Date", value = worker.start_date, key=f'update_start_date{i}')
            new_end_date = st.date_input("End Date", value = worker.end_date, key=f'update_end_date_{i}')
            new_work_days = st.multiselect(
                "Working Days",
                options=DAYS_OF_WEEK,
                default=worker.work_days,  # Use the worker's current days
                key=f'update_work_days_{i}'
            )
            new_work_hours = st.number_input(
                "Hours Per Day",
                min_value=1.0,
                max_value=24.0,
                value=float(worker.work_hours),  # Use the worker's current hours
                step=0.5,
                key=f'update_work_hours_{i}'
            )
            new_payment = st.text_input("Payment", value=worker.payment, key=f'update_payment_{i}')
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_{i}"):
                    updated_worker = Worker(
                        name=new_name,
                        start_date = new_start_date,
                        end_date = new_end_date,
                        work_hours=new_work_hours,
                        work_days=new_work_days,
                        payment=new_payment,
                    )
                    st.session_state.workforce.update_worker(worker.name, updated_worker)
                    save_workforce()
                    st.success(f"Updated worker {worker.name}")
                    st.rerun()  # Force rerun to refresh the worker list
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.workforce.remove_worker(worker.name)
                    save_workforce()
                    st.warning(f"Removed worker {worker.name}")
                    st.rerun()
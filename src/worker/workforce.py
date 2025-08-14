import yaml
import streamlit as st

from pathlib import Path

class Workforce:
    def __init__(self):
        self.workers = []

    def add_worker(self, worker):
        if worker.name in [w.name for w in self.workers]:
            raise ValueError(f"Worker with name '{worker.name}' already exists in the workforce.")
        self.workers.append(worker)

    def get_workers(self):
        return self.workers

    def update_worker(self, name, worker):
        for i, w in enumerate(self.workers):
            if w.name == name:
                # Replace the worker at the same position to maintain order
                self.workers[i] = worker
                return
        raise ValueError(f"Worker with name '{name}' not found in the workforce.")

    def remove_worker(self, name):
        for i, w in enumerate(self.workers):
            if w.name == name:
                self.workers.pop(i)
                return
        raise ValueError(f"Worker with name '{name}' not found in the workforce.")

    def get_daily_work_hours(self, date):
        total_hours = 0
        for worker in self.workers:
            total_hours += worker.get_daily_work_hours(date)
        return total_hours

    def get_daily_worker_count(self, date):
        workers_on_date = []
        for worker in self.workers:
            hours = worker.get_daily_work_hours(date)
            if hours > 0:
                workers_on_date.append((worker, hours))
        
        if len(workers_on_date) == 0:
            return 0
            
        max_hours_on_date = max([hours for _, hours in workers_on_date])
        worker_count = sum([hours / max_hours_on_date for _, hours in workers_on_date])
        return worker_count
    
    def get_workers_for_date(self, date):
        """Get all workers who are working on a specific date with their hours"""
        workers_on_date = []
        for worker in self.workers:
            hours = worker.get_daily_work_hours(date)
            if hours > 0:
                workers_on_date.append({
                    'worker': worker,
                    'hours': hours
                })
        return workers_on_date
    
    def get_employment_date_range(self):
        """Get the overall employment date range for all workers"""
        if not self.workers:
            return None, None
        
        all_start_dates = []
        all_end_dates = []
        
        for worker in self.workers:
            start_date, end_date = worker.get_employment_date_range()
            if start_date and end_date:
                all_start_dates.append(start_date)
                all_end_dates.append(end_date)
        
        if not all_start_dates or not all_end_dates:
            return None, None
        
        return min(all_start_dates), max(all_end_dates)

    def save(self, filename='workers.yaml'):
        # Convert Pydantic models to dictionaries, excluding the workforce field
        workers_data = [worker.model_dump(exclude={'workforce'}) for worker in self.workers]

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        # Save to YAML file
        with open(filename, 'w') as file:
            yaml.dump(workers_data, file, default_flow_style=False, indent=2)
    
    def load(self, filename='workers.yaml'):
        """Load workers from a YAML file"""
        from .worker import Worker  # Import here to avoid circular imports

        try:
            with open(filename, 'r') as file:
                workers_data = yaml.safe_load(file)

            # Clear existing workers
            self.workers = []

            # Handle empty or None data
            if not workers_data:
                return

            # Create Worker instances from the loaded data
            for worker_data in workers_data:
                # Remove the workforce field from data since it will be set automatically
                worker_data_copy = worker_data.copy()

                # Create worker with this workforce instance
                worker = Worker(**worker_data_copy)
                self.add_worker(worker)

        except FileNotFoundError:
            st.warning(f"File {filename} not found. Starting with empty workforce.")
            self.workers = []
        except Exception as e:
            st.error(f"Error loading workers from {filename}: {e}")
            st.stop()
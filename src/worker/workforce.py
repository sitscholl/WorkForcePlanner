import yaml
import streamlit as st

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
        for w in self.workers:
            if w.name == name:
                self.remove_worker(name)
                self.add_worker(worker)
                return
        raise ValueError(f"Worker with name '{worker.name}' not found in the workforce.")

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
            if worker.get_daily_work_hours(date) > 0:
                workers_on_date.append(worker)
        
        if len(workers_on_date) == 0:
            return 0
            
        max_hours_on_date = max([i.work_hours for i in workers_on_date])
        worker_count = sum([i.work_hours / max_hours_on_date for i in workers_on_date])
        return worker_count

    def save(self, filename='workers.yaml'):
        # Convert Pydantic models to dictionaries, excluding the workforce field
        workers_data = [worker.model_dump(exclude={'workforce'}) for worker in self.workers]

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
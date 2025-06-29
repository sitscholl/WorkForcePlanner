import yaml

class Workforce:
    def __init__(self):
        self.workers = []

    def add_worker(self, worker):
        self.workers.append(worker)

    def get_workers(self):
        return self.workers

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
                if 'workforce' in worker_data_copy:
                    del worker_data_copy['workforce']
                
                # Create worker with this workforce instance
                worker = Worker(workforce=self, **worker_data_copy)
                # Note: Worker's __post_init__ will automatically add itself to this workforce
                
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with empty workforce.")
        except Exception as e:
            print(f"Error loading workers from {filename}: {e}")
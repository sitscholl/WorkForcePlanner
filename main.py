from src.worker import Worker, Workforce

def main():
    workforce = Workforce()

    worker1 = Worker(name="Gabriel", work_hours=9, work_days=['mon'], workforce=workforce)
    worker2 = Worker(name="Sophia", work_hours=8, work_days=['tue'], workforce=workforce)

    print("Workers in workforce:")
    for worker in workforce.get_workers():
        print(f"- {worker.name}: {worker.work_hours} hours on {worker.work_days}")
    
    # Save workers to YAML file
    print("\nSaving workers to 'workers.yaml'...")
    workforce.save('workers.yaml')
    print("Workers saved successfully!")
    
    # Demonstrate loading (optional)
    print("\nTesting load functionality...")
    new_workforce = Workforce()
    new_workforce.load('workers.yaml')
    print("Loaded workers:")
    for worker in new_workforce.get_workers():
        print(f"- {worker.name}: {worker.work_hours} hours on {worker.work_days}")


if __name__ == "__main__":
    main()
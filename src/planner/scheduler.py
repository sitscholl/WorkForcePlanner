import pandas as pd
import streamlit as st
from datetime import date, time, datetime, timedelta

def schedule_field_work(field_table, workforce, start_date, field_order_column='field_name', hours_column='total_hours', harvest_round_column='Harvest Round'):
    """
    Schedule field work based on available workforce hours.
    
    Parameters:
    - field_table: DataFrame with fields and their required hours
    - workforce: Object with get_daily_work_hours(date) method
    - start_date: datetime object for when work should start
    - field_order_column: column name that defines field order
    - hours_column: column name with total hours required per field
    
    Returns:
    - DataFrame with field_name, start_datetime, end_datetime, total_hours
    """
    field_table = field_table.copy()
    results = []

    if isinstance(start_date, date):
        start_date = datetime.combine(start_date, time(hour=8))
    current_datetime = start_date
    current_date = current_datetime.date()

    remaining_daily_capacity = workforce.get_daily_work_hours(current_date)
    daily_worker_count = workforce.get_daily_worker_count(current_date)
    
    # The field_table is already ordered according to the harvest_round_order from apply_fields_config
    for _, field_row in field_table.iterrows():
        field_name = field_row[field_order_column]
        required_hours = field_row[hours_column]
        harvest_round = field_row[harvest_round_column]
        field_start = current_datetime
        remaining_hours = required_hours
        
        while remaining_hours > 0:
            # Check if we've moved to a new day
            if current_datetime.date() != current_date:
                current_date = current_datetime.date()
                remaining_daily_capacity = workforce.get_daily_work_hours(current_date)
                daily_worker_count = workforce.get_daily_worker_count(current_date)
            
            if remaining_daily_capacity <= 0 or daily_worker_count == 0:
                # No work capacity this day, move to next day
                current_datetime = datetime.combine(current_date + timedelta(days=1), start_date.time())
                # Safety exit to avoid infinite loop if no workers available anymore
                if current_datetime.timetuple().tm_yday == 365:
                    st.warning('Could not finish all fields within the year. Please review the workforce or field requirements.')
                    return pd.DataFrame(results)

                continue
            
            # Work as many hours as possible today
            hours_to_work = min(remaining_hours, remaining_daily_capacity)
            elapsed_time = hours_to_work / daily_worker_count

            # Advance time
            current_datetime += timedelta(hours=elapsed_time)
            remaining_hours -= hours_to_work
            remaining_daily_capacity -= hours_to_work
        
        field_end = round_to_nearest_hour(current_datetime)
        results.append({
            'Field': field_name,
            'start_date': field_start,
            'end_date': field_end,
            'total_hours': required_hours,
            'Harvest round': harvest_round
        })
        print(f"Finished field {field_name} (round {harvest_round}) on {field_end}")

        # Use rounded end time as start for next field
        current_datetime = field_end
    
    return pd.DataFrame(results)

def round_to_nearest_hour(dt):
    """Round a datetime object to the nearest hour."""
    if dt.minute >= 30 or (dt.minute == 29 and dt.second >= 30):
        dt = dt.replace(second=0, microsecond=0, minute=0) + timedelta(hours=1)
    else:
        dt = dt.replace(second=0, microsecond=0, minute=0)
    return dt

if __name__ == '__main__':
    from src.config import load_config
    from src.utils import load_data_and_train_model, load_workforce
    from pathlib import Path

    config = load_config('config.yaml')
    predictor, data = load_data_and_train_model(config)
    workforce = load_workforce(Path(config['workforce_file']))

    # Example usage:
    schedule_df = schedule_field_work(
        field_table=data,
        workforce=workforce,
        start_date=datetime(2025, 9, 1, 8, 0),  # Start September 1st at 8 AM
        field_order_column='Field',
        hours_column='predicted_hours'
        )

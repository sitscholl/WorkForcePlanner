import pandas as pd
import streamlit as st
from datetime import date, time, datetime, timedelta

def schedule_field_work(
        field_table,
        workforce,
        start_date,
        field_order_column='field_name',
        group_name = 'Variety Group',
        hours_column='total_hours',
        harvest_round_column='Harvest Round'
    ):
    """
    Schedule field work based on available workforce hours with support for different start dates per variety group.

    Parameters:
    - field_table: DataFrame with fields and their required hours. Must contain a column specified by 'group_name'
                   that contains variety group information (e.g., 'frühsorte', 'hauptsorte', 'spätsorte')
    - workforce: Object with get_daily_work_hours(date) and get_daily_worker_count(date) methods
    - start_date: Either:
                  * dict with datetime objects for each group in group_name (e.g., {'frühsorte': datetime(2025,8,24), 'hauptsorte': datetime(2025,9,17)})
                  * single datetime/date object for all groups (backward compatibility)
    - field_order_column: column name that defines field order
    - group_name: column name that contains variety group information
    - hours_column: column name with total hours required per field
    - harvest_round_column: column name with harvest round information

    Returns:
    - DataFrame with columns: Field, start_date, end_date, total_hours, Harvest round, Variety Group

    Example usage:
    ```python
    start_dates = {
        'frühsorte': datetime(2025, 8, 24),
        'hauptsorte': datetime(2025, 9, 17),
        'spätsorte': datetime(2025, 10, 17)
    }
    schedule_df = schedule_field_work(
        field_table=fields_df,
        workforce=workforce_obj,
        start_date=start_dates,
        group_name='Variety Group'
    )
    ```
    """
    field_table = field_table.copy()
    all_results = []

    # Handle single start_date for backward compatibility
    if not isinstance(start_date, dict):
        # Convert single date to dict for all groups
        unique_groups = field_table[group_name].unique()
        if isinstance(start_date, date):
            start_date = datetime.combine(start_date, time(hour=8))
        start_date_dict = {group: start_date for group in unique_groups}
    else:
        start_date_dict = start_date.copy()
        # Convert any date objects to datetime objects
        for group, date_val in start_date_dict.items():
            if isinstance(date_val, date) and not isinstance(date_val, datetime):
                start_date_dict[group] = datetime.combine(date_val, time(hour=8))

    # Group fields by variety group
    grouped_fields = field_table.groupby(group_name)

    # Track the latest end time across all groups to avoid overlapping work
    global_current_datetime = None

    # Process each group separately
    for group, group_fields in grouped_fields:
        if group not in start_date_dict:
            st.warning(f"No start date specified for group '{group}'. Skipping this group.")
            continue

        group_start_date = start_date_dict[group]

        # Ensure we don't start before the global current time (to avoid overlapping work)
        if global_current_datetime is not None:
            current_datetime = max(group_start_date, global_current_datetime)
        else:
            current_datetime = group_start_date

        current_date = current_datetime.date()
        remaining_daily_capacity = workforce.get_daily_work_hours(current_date)
        daily_worker_count = workforce.get_daily_worker_count(current_date)

        # The field_table is already ordered according to the harvest_round_order from apply_fields_config
        for _, field_row in group_fields.iterrows():
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
                    current_datetime = datetime.combine(current_date + timedelta(days=1), group_start_date.time())
                    # Safety exit to avoid infinite loop if no workers available anymore
                    if current_datetime.timetuple().tm_yday == 365:
                        st.warning('Could not finish all fields within the year. Please review the workforce or field requirements.')
                        return pd.DataFrame(all_results)

                    continue

                # Work as many hours as possible today
                hours_to_work = min(remaining_hours, remaining_daily_capacity)
                elapsed_time = hours_to_work / daily_worker_count

                # Advance time
                current_datetime += timedelta(hours=elapsed_time)
                remaining_hours -= hours_to_work
                remaining_daily_capacity -= hours_to_work

            field_end = round_to_nearest_hour(current_datetime)
            all_results.append({
                'Field': field_name,
                'start_date': field_start,
                'end_date': field_end,
                'total_hours': required_hours,
                'Harvest round': harvest_round,
                'Variety Group': group
            })
            print(f"Finished field {field_name} (group {group}, round {harvest_round}) on {field_end}")

            # Use rounded end time as start for next field
            current_datetime = field_end

        # Update global current time to the end of this group's work
        global_current_datetime = current_datetime

    return pd.DataFrame(all_results)

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

    config = load_config('config/config.yaml')
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

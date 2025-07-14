import streamlit as st
import pandas as pd

from datetime import datetime

def render_parameter_selection():
    with st.sidebar:
        param_name = st.selectbox("What would you like to model", ("Ernte", "Zupfen"), key = 'param_name')
        year = st.number_input("Year", value=datetime.now().year, min_value=2020, key = 'model_year')
        start_date = st.date_input("Starting date", value=datetime(2025, 9, 1), key = 'work_start_date')
    
    return param_name, year, start_date

def render_sidebar(config):
    """Render the sidebar with current configuration settings.
    
    This function displays the current settings from the config file in a nicely
    formatted way in the sidebar. It can be imported and used across all pages of the app.
    
    Args:
        config (dict): The configuration dictionary loaded from config.yaml
    """
    with st.sidebar:
        st.title("Current Settings")
        
        # General Settings Section
        start_date = config.get('start_date')
        if start_date:
            start_date = start_date.strftime("%Y-%m-%d")
        else:
            start_date = 'Not set'
        st.subheader("General Settings")
        st.info(f"**Year:** {config.get('year', 'Not set')}")
        st.info(f"**Start Date:** {start_date}")
        st.info(f"**Model:** {config.get('param_name', 'Not set')}")
        
        # Google Sheets Section
        if 'gsheets' in config:
            with st.expander("Google Sheets"):
                st.write(f"**Worksheet:** {config['gsheets'].get('worksheet_name', 'Not set')}")
                
                # Show truncated URL for better display
                url = config['gsheets'].get('spreadsheet_url', '')
                if url:
                    display_url = url[:30] + '...' if len(url) > 30 else url
                    st.write(f"**URL:** {display_url}")
        
        # Model Information Section
        model_name = config.get('param_name')
        if model_name and model_name in config:
            with st.expander(f"{model_name} Model Details"):
                # Show target
                st.write(f"**Target:** {config[model_name].get('target', 'Not set')}")
                
                # Show predictors in a compact way
                predictors = config[model_name].get('predictors', [])
                if predictors:
                    st.write("**Predictors:**")
                    for pred in predictors:
                        st.write(f"- {pred}")
                
                # Show CV method
                st.write(f"**CV Method:** {config[model_name].get('cv_method', 'Not set')}")
        
        # Add a link to the settings page
        st.divider()
        st.write("Need to change settings? [Go to Settings Page](/Settings)")


def field_order_interface(field_names):
    """
    Create an interface for reordering field priorities
    
    Args:
        field_names: List of field names
        
    Returns:
        List[str]: Reordered field names
    """
    
    if not field_names:
        st.info("No fields available to order.")
        return []
    
    st.subheader("Field Priority Order")
    st.write("Drag and drop to reorder fields by priority (top = first to work on):")
       
    # Use session state to maintain order
    if 'field_order' not in st.session_state:
        st.session_state.field_order = field_names.copy()
    
    # Ensure all fields from field_names are in session state
    for field in field_names:
        if field not in st.session_state.field_order:
            st.session_state.field_order.append(field)
    
    # Remove fields that are no longer in field_names
    st.session_state.field_order = [
        field for field in st.session_state.field_order if field in field_names
    ]
    
    # Display current order with move up/down buttons
    for i, field in enumerate(st.session_state.field_order):
        col1, col2, col3, col4 = st.columns([0.1, 0.6, 0.15, 0.15], gap = 'small')
        
        with col1:
            st.write(f"{i+1}.")
        
        with col2:
            st.write(field)
        
        with col3:
            if i > 0:
                if st.button("↑", key=f"up_{i}"):
                    # Move up
                    st.session_state.field_order[i], st.session_state.field_order[i-1] = \
                        st.session_state.field_order[i-1], st.session_state.field_order[i]
                    st.rerun()
        
        with col4:
            if i < len(st.session_state.field_order) - 1:
                if st.button("↓", key=f"down_{i}"):
                    # Move down
                    st.session_state.field_order[i], st.session_state.field_order[i+1] = \
                        st.session_state.field_order[i+1], st.session_state.field_order[i]
                    st.rerun()
    
    return st.session_state.field_order.copy()

def field_specific_settings(field_name, fields_config, field_data):
    """
    Create field-specific settings interface
    
    Args:
        field_name (str): Name of the field
        fields_config (dict): Fields configuration dictionary
        field_data (pd.DataFrame): Field data for determining defaults
        
    Returns:
        dict: Field settings
    """
    
    st.write(f"Configure settings for: **{field_name}**")
    
    # Initialize field-specific config if not exists
    if field_name not in fields_config:
        fields_config[field_name] = {}
    
    # Get field data for this specific field
    field_specific_data = field_data[field_data["Field"] == field_name]
    
    # Harvest rounds setting
    default_rounds = 1
    if not field_specific_data.empty and "Harvest rounds" in field_specific_data.columns:
        try:
            # Use the most recent year's value as default
            latest_year_data = field_specific_data.sort_values("Year", ascending=False).iloc[0]
            if "Harvest rounds" in latest_year_data and not pd.isna(latest_year_data["Harvest rounds"]):
                default_rounds = int(latest_year_data["Harvest rounds"])
        except (ValueError, TypeError, IndexError) as e:
            st.warning(f"Could not determine default harvest rounds for {field_name}: {e}")
            default_rounds = 1
    
    # Use the configured value if it exists, otherwise use the default
    current_value = fields_config[field_name].get("harvest_rounds", default_rounds)
    
    # Ensure current_value is an integer
    try:
        current_value = int(current_value)
    except (ValueError, TypeError):
        current_value = default_rounds
    
    harvest_rounds = st.number_input(
        "Harvest Rounds",
        min_value=1,
        max_value=10,
        value=current_value,
        key=f"{field_name}_harvest_rounds",
        help="Number of harvest rounds for this field"
    )

    return {'harvest_rounds': harvest_rounds}


def harvest_round_order_interface(fields_config):
    """
    Create an interface for ordering all field-harvest round combinations using an editable dataframe
    
    Args:
        fields_config (dict): Fields configuration dictionary
        
    Returns:
        list: Ordered list of dictionaries with field and round keys
    """
    st.subheader("Harvest Round Order")
    st.write("Enter the order number for each field-harvest round combination:")
    
    # Generate all field-harvest round combinations
    field_harvest_combinations = []
    for field_name, field_config in fields_config.items():
        if field_name == 'field_order' or field_name == 'harvest_round_order':
            continue
            
        harvest_rounds = field_config.get('harvest_rounds', 1)
        try:
            harvest_rounds = int(harvest_rounds)
        except (ValueError, TypeError):
            harvest_rounds = 1
            
        for round_num in range(1, harvest_rounds + 1):
            field_harvest_combinations.append({"field": field_name, "round": round_num})
    
    # If no combinations, return empty list
    if not field_harvest_combinations:
        st.info("No field-harvest round combinations available.")
        return []
    
    # Initialize session state for the order if it doesn't exist
    if 'harvest_round_order' not in st.session_state:
        # Check if there's an existing order in the config
        if 'harvest_round_order' in fields_config and fields_config['harvest_round_order']:
            # Convert existing order to the new dictionary format if needed
            ordered_combinations = []
            for i, item in enumerate(fields_config['harvest_round_order']):
                if isinstance(item, tuple) or isinstance(item, list):
                    # Convert tuple/list to dict
                    ordered_combinations.append({"field": item[0], "round": item[1], "order": i + 1})
                elif isinstance(item, dict) and "field" in item and "round" in item:
                    # Already in the right format, add order
                    item_with_order = item.copy()
                    item_with_order["order"] = i + 1
                    ordered_combinations.append(item_with_order)
                else:
                    # Skip invalid items
                    continue
            st.session_state.harvest_round_order = ordered_combinations
        else:
            # Initialize with current field order and consecutive harvest rounds
            ordered_combinations = []
            order_counter = 1
            
            for field_name in fields_config.get('field_order', []):
                if field_name in fields_config:
                    harvest_rounds = fields_config[field_name].get('harvest_rounds', 1)
                    try:
                        harvest_rounds = int(harvest_rounds)
                    except (ValueError, TypeError):
                        harvest_rounds = 1
                        
                    for round_num in range(1, harvest_rounds + 1):
                        ordered_combinations.append({"field": field_name, "round": round_num, "order": order_counter})
                        order_counter += 1
            
            # Add any combinations not in the current order
            for combo in field_harvest_combinations:
                if not any(existing["field"] == combo["field"] and existing["round"] == combo["round"] 
                          for existing in ordered_combinations):
                    combo_with_order = combo.copy()
                    combo_with_order["order"] = order_counter
                    ordered_combinations.append(combo_with_order)
                    order_counter += 1
                    
            st.session_state.harvest_round_order = ordered_combinations
    
    # Ensure all combinations are in session state with an order value
    current_combo_set = {(item["field"], item["round"]) for item in st.session_state.harvest_round_order}
    max_order = max([item["order"] for item in st.session_state.harvest_round_order], default=0)
    
    for combo in field_harvest_combinations:
        if (combo["field"], combo["round"]) not in current_combo_set:
            max_order += 1
            combo_with_order = combo.copy()
            combo_with_order["order"] = max_order
            st.session_state.harvest_round_order.append(combo_with_order)
    
    # Remove combinations that are no longer valid
    valid_combo_set = {(item["field"], item["round"]) for item in field_harvest_combinations}
    st.session_state.harvest_round_order = [
        combo for combo in st.session_state.harvest_round_order 
        if (combo["field"], combo["round"]) in valid_combo_set
    ]
    
    # Create a dataframe from the current order
    df = pd.DataFrame(st.session_state.harvest_round_order)
    
    # Rename columns for display
    display_df = df.copy()
    display_df.columns = ["Field", "Round", "Order"]
    
    # Define a callback function to handle changes
    def on_change():
        # Get the edited data
        edited_data = st.session_state.harvest_round_editor
        
        # Check if there are edited rows
        if 'edited_rows' in edited_data and edited_data['edited_rows']:
            # First, collect all the changes
            changes = []
            
            # Process each edited row
            for row_idx, edits in edited_data['edited_rows'].items():
                # Convert row_idx to integer (it's a string in the edited_data)
                row_idx = int(row_idx)
                
                # Only process if the Order column was changed
                if 'Order' in edits:
                    # Get the original row from the display dataframe
                    original_row = display_df.iloc[row_idx]
                    field = original_row['Field']
                    round_num = original_row['Round']
                    new_order = edits['Order']
                    
                    # Find the corresponding item in session state
                    for i, item in enumerate(st.session_state.harvest_round_order):
                        if item['field'] == field and item['round'] == round_num:
                            current_order = item['order']
                            if new_order != current_order:
                                changes.append({
                                    "index": i,
                                    "field": field,
                                    "round": round_num,
                                    "old_order": current_order,
                                    "new_order": new_order
                                })
                            break
            
            # Process changes one by one, starting with the ones that decrease order values
            # (to avoid conflicts when shifting)
            changes.sort(key=lambda x: (x["new_order"], -x["old_order"]))
            
            for change in changes:
                i = change["index"]
                new_order = change["new_order"]
                
                # Check if the new order already exists in other items
                conflicts = [j for j, item in enumerate(st.session_state.harvest_round_order) 
                            if item["order"] == new_order and j != i]
                
                if conflicts:
                    # Shift all items with order >= new_order (except the current one) up by 1
                    for j, item in enumerate(st.session_state.harvest_round_order):
                        if j != i and item["order"] >= new_order:
                            item["order"] += 1
                
                # Now set the new order for the current item
                st.session_state.harvest_round_order[i]["order"] = new_order
            
            # Sort the combinations by the order value
            st.session_state.harvest_round_order.sort(key=lambda x: x["order"])
            
            # Normalize the order values to be consecutive integers starting from 1
            for i, item in enumerate(st.session_state.harvest_round_order):
                item["order"] = i + 1
                
            # Trigger a rerun to update the UI
            st.rerun()
    
    # Create an editable dataframe with the callback
    edited_df = st.data_editor(
        display_df,
        column_config={
            "Field": st.column_config.TextColumn("Field", disabled=True),
            "Round": st.column_config.NumberColumn("Harvest Round", disabled=True),
            "Order": st.column_config.NumberColumn("Order", min_value=1, step=1)
        },
        hide_index=True,
        key="harvest_round_editor",
        on_change=on_change
    )
    
    # Create a clean version without the order field for returning
    clean_order = []
    for item in st.session_state.harvest_round_order:
        clean_item = {"field": item["field"], "round": item["round"]}
        clean_order.append(clean_item)
    
    return clean_order
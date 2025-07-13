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
        st.subheader("General Settings")
        st.info(f"**Year:** {config.get('year', 'Not set')}")
        st.info(f"**Start Date:** {config.get('start_date', 'Not set')}")
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
    Create an interface for ordering all field-harvest round combinations
    
    Args:
        fields_config (dict): Fields configuration dictionary
        
    Returns:
        list: Ordered list of dictionaries with field and round keys
    """
    st.subheader("Harvest Round Order")
    st.write("Drag and drop to reorder field harvest rounds (top = first to work on):")
    
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
    
    # Use session state to maintain order
    if 'harvest_round_order' not in st.session_state:
        # Check if there's an existing order in the config
        if 'harvest_round_order' in fields_config and fields_config['harvest_round_order']:
            # Convert existing order to the new dictionary format if needed
            ordered_combinations = []
            for item in fields_config['harvest_round_order']:
                if isinstance(item, tuple) or isinstance(item, list):
                    # Convert tuple/list to dict
                    ordered_combinations.append({"field": item[0], "round": item[1]})
                elif isinstance(item, dict) and "field" in item and "round" in item:
                    # Already in the right format
                    ordered_combinations.append(item)
                else:
                    # Skip invalid items
                    continue
            st.session_state.harvest_round_order = ordered_combinations
        else:
            # Initialize with current field order and consecutive harvest rounds
            ordered_combinations = []
            for field_name in fields_config.get('field_order', []):
                if field_name in fields_config:
                    harvest_rounds = fields_config[field_name].get('harvest_rounds', 1)
                    try:
                        harvest_rounds = int(harvest_rounds)
                    except (ValueError, TypeError):
                        harvest_rounds = 1
                        
                    for round_num in range(1, harvest_rounds + 1):
                        ordered_combinations.append({"field": field_name, "round": round_num})
            
            # Add any combinations not in the current order
            for combo in field_harvest_combinations:
                if not any(existing["field"] == combo["field"] and existing["round"] == combo["round"] 
                          for existing in ordered_combinations):
                    ordered_combinations.append(combo)
                    
            st.session_state.harvest_round_order = ordered_combinations
    
    # Ensure all combinations are in session state
    current_combo_set = {(item["field"], item["round"]) for item in st.session_state.harvest_round_order}
    
    for combo in field_harvest_combinations:
        if (combo["field"], combo["round"]) not in current_combo_set:
            st.session_state.harvest_round_order.append(combo)
    
    # Remove combinations that are no longer valid
    valid_combo_set = {(item["field"], item["round"]) for item in field_harvest_combinations}
    st.session_state.harvest_round_order = [
        combo for combo in st.session_state.harvest_round_order 
        if (combo["field"], combo["round"]) in valid_combo_set
    ]
    
    # Display current order with move up/down buttons
    for i, combo in enumerate(st.session_state.harvest_round_order):
        field_name = combo["field"]
        round_num = combo["round"]
        
        col1, col2, col3, col4, col5 = st.columns([0.1, 0.4, 0.2, 0.15, 0.15], gap='small')
        
        with col1:
            st.write(f"{i+1}.")
        
        with col2:
            st.write(field_name)
            
        with col3:
            st.write(f"Round {round_num}")
        
        with col4:
            if i > 0:
                if st.button("↑", key=f"up_harvest_{i}"):
                    # Move up
                    st.session_state.harvest_round_order[i], st.session_state.harvest_round_order[i-1] = \
                        st.session_state.harvest_round_order[i-1], st.session_state.harvest_round_order[i]
                    st.rerun()
        
        with col5:
            if i < len(st.session_state.harvest_round_order) - 1:
                if st.button("↓", key=f"down_harvest_{i}"):
                    # Move down
                    st.session_state.harvest_round_order[i], st.session_state.harvest_round_order[i+1] = \
                        st.session_state.harvest_round_order[i+1], st.session_state.harvest_round_order[i]
                    st.rerun()
    
    return st.session_state.harvest_round_order.copy()
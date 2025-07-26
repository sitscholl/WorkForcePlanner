import streamlit as st
import yaml
import datetime

from src.app_state import save_config, load_config, load_data, CONFIG_PATH
from src.ui_components import render_sidebar, field_order_interface, field_specific_settings, harvest_round_order_interface

# Set page title
st.set_page_config(page_title="Settings", page_icon="⚙️")
st.title("Settings")
st.write("Configure application settings and save them to config.yaml")

# Load current configuration
config = load_config(CONFIG_PATH)

# Initialize fields_config if it doesn't exist
if "fields_config" not in config:
    config["fields_config"] = {}

# Render sidebar
render_sidebar(config)

# Create tabs for different configuration sections
tabs = st.tabs(["General", "Google Sheets", "Models", "Fields"])

# General settings tab
with tabs[0]:
    st.header("General Settings")
    
    # Year setting
    config["year"] = st.number_input(
        "Year", 
        min_value=2020, 
        max_value=2030, 
        value=int(config.get("year", 2025)),
        help="The year for scheduling"
    )
    
    # Start date setting
    start_date_str = config.get("start_date", "2025-09-01")
    if isinstance(start_date_str, datetime.datetime) or isinstance(start_date_str, datetime.date):
        start_date_str = start_date_str.strftime("%Y-%m-%d")
    start_date = st.date_input(
        "Start Date",
        value=None if not start_date_str else datetime.datetime.strptime(start_date_str.split(" ")[0], "%Y-%m-%d"),
        help="The start date for scheduling"
    )
    config["start_date"] = str(start_date)
    
    # Workforce file setting
    config["workforce_file"] = st.text_input(
        "Workforce File",
        value=config.get("workforce_file", "workforce.yaml"),
        help="Path to the workforce configuration file"
    )
    
    # Parameter name setting
    config["param_name"] = st.text_input(
        "Default Parameter Name",
        value=config.get("param_name", "Ernte"),
        help="Default parameter name to use in the application"
    )

# Google Sheets settings tab
with tabs[1]:
    st.header("Google Sheets Integration")
    
    if "gsheets" not in config:
        config["gsheets"] = {}
    
    # Credentials file
    config["gsheets"]["credentials_file"] = st.text_input(
        "Credentials File",
        value=config["gsheets"].get("credentials_file", "gsheets_creds.json"),
        help="Path to Google Sheets API credentials file"
    )
    
    # Spreadsheet URL
    config["gsheets"]["spreadsheet_url"] = st.text_input(
        "Spreadsheet URL",
        value=config["gsheets"].get("spreadsheet_url", ""),
        help="URL of the Google Spreadsheet"
    )
    
    # Worksheet name
    config["gsheets"]["worksheet_name"] = st.text_input(
        "Worksheet Name",
        value=config["gsheets"].get("worksheet_name", "Wiesen"),
        help="Name of the worksheet in the spreadsheet"
    )

# Models settings tab
with tabs[2]:
    st.header("Model Configuration")
    
    # Create subtabs for each model
    model_names = [key for key in config.keys() if key not in ["year", "start_date", "workforce_file", "gsheets", "param_name", "fields_config"]]
    
    if not model_names:
        st.warning("No model configurations found in config.yaml")
    else:
        model_tabs = st.tabs(model_names)
        
        for i, model_name in enumerate(model_names):
            with model_tabs[i]:
                st.subheader(f"{model_name} Model")
                
                if model_name not in config:
                    config[model_name] = {}
                
                # Model class
                config[model_name]["class"] = st.text_input(
                    "Model Class",
                    value=config[model_name].get("class", "src.model.linear_regression.LinearRegressionPredictor"),
                    key=f"{model_name}_class",
                    help="Fully qualified class name for the model"
                )
                
                # Target column
                config[model_name]["target"] = st.text_input(
                    "Target Column",
                    value=config[model_name].get("target", f"Hours {model_name}"),
                    key=f"{model_name}_target",
                    help="Target column for prediction"
                )
                
                # Predictors
                predictors_str = ", ".join(config[model_name].get("predictors", []))
                new_predictors = st.text_input(
                    "Predictors (comma-separated)",
                    value=predictors_str,
                    key=f"{model_name}_predictors",
                    help="Comma-separated list of predictor columns"
                )
                config[model_name]["predictors"] = [p.strip() for p in new_predictors.split(",") if p.strip()]
                
                # Cross-validation method
                config[model_name]["cv_method"] = st.selectbox(
                    "Cross-Validation Method",
                    options=["group_kfold", "kfold", "stratified_kfold", "time_series_split"],
                    index=0 if "cv_method" not in config[model_name] else 
                          ["group_kfold", "kfold", "stratified_kfold", "time_series_split"].index(config[model_name]["cv_method"]),
                    key=f"{model_name}_cv_method",
                    help="Method for cross-validation"
                )
                
                # CV parameters
                st.subheader("Cross-Validation Parameters")
                
                if "cv_params" not in config[model_name]:
                    config[model_name]["cv_params"] = {}
                
                if config[model_name]["cv_method"] == "group_kfold":
                    config[model_name]["cv_params"]["group_column"] = st.text_input(
                        "Group Column",
                        value=config[model_name]["cv_params"].get("group_column", "Year"),
                        key=f"{model_name}_group_column",
                        help="Column to use for grouping in group k-fold"
                    )
                
                config[model_name]["cv_params"]["n_splits"] = st.number_input(
                    "Number of Splits",
                    min_value=-1,
                    max_value=20,
                    value=int(config[model_name]["cv_params"].get("n_splits", 5)),
                    key=f"{model_name}_n_splits",
                    help="Number of splits for cross-validation (-1 for leave-one-out)"
                )

    # Add new model section
    st.header("Add New Model")
    new_model_name = st.text_input("New Model Name", key="new_model_name")
    add_model = st.button("Add Model")

    if add_model and new_model_name:
        if new_model_name in config:
            st.error(f"Model '{new_model_name}' already exists!")
        else:
            # Create a new model configuration with default values
            config[new_model_name] = {
                "class": "src.model.linear_regression.LinearRegressionPredictor",
                "target": f"Hours {new_model_name}",
                "predictors": ["Variety", "Count"],
                "cv_method": "group_kfold",
                "cv_params": {
                    "group_column": "Year",
                    "n_splits": 5
                }
            }
            st.success(f"Model '{new_model_name}' added! Please save changes to persist.")
            st.rerun()

# Save changes button
st.header("Save Changes")
if st.button("Save Configuration", type="primary"):
    if save_config(config, CONFIG_PATH):
        st.success("Configuration saved successfully!")
        # Clear the cache to ensure the app uses the new configuration
        st.cache_data.clear()
    else:
        st.error("Failed to save configuration.")

# Show current configuration
with st.expander("View Current Configuration"):
    st.code(yaml.dump(config, default_flow_style=False, sort_keys=False), language="yaml")
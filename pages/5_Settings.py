import streamlit as st
import yaml
import datetime

from src.app_state import save_config, load_config, CONFIG_PATH
from src.ui_components import render_sidebar

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
tabs = st.tabs(["General", "Google Sheets", "Models"])

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

    # Parameter name setting
    config["param_name"] = st.text_input(
        "Parameter Name",
        value=config.get("param_name", "Ernte"),
        help="Parameter name to use in the application"
    )
    
    # Start date setting
    start_date_dict = config.get("start_date", {})
    st.subheader('Start Dates')
    for group, start_date in start_date_dict.items():
        if isinstance(start_date, datetime.datetime) or isinstance(start_date, datetime.date):
            start_date = start_date.strftime("%Y-%m-%d")
        start_date = st.date_input(
            f"{group}",
            value=None if not start_date else datetime.datetime.strptime(start_date.split(" ")[0], "%Y-%m-%d"),
            help="The start date for scheduling",
            key = f"start_date_{group}"
        )
        config["start_date"][group] = str(start_date)
        
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
    model_names = list(config.get('models', {}).keys())
    
    if not model_names:
        st.warning("No model configurations found in config.yaml")
    else:
        model_tabs = st.tabs(model_names)
        
        for i, model_name in enumerate(model_names):
            with model_tabs[i]:
                st.subheader(f"{model_name} Model")
                
                if model_name not in config['models']:
                    config['models'][model_name] = {}
                
                # Model class
                config['models'][model_name]["class"] = st.text_input(
                    "Model Class",
                    value=config['models'][model_name].get("class", "src.model.linear_regression.LinearRegressionPredictor"),
                    key=f"{model_name}_class",
                    help="Fully qualified class name for the model"
                )
                
                # Target column
                config['models'][model_name]["target"] = st.text_input(
                    "Target Column",
                    value=config['models'][model_name].get("target", f"Hours {model_name}"),
                    key=f"{model_name}_target",
                    help="Target column for prediction"
                )
                
                # Predictors
                predictors_str = ", ".join(config['models'][model_name].get("predictors", []))
                new_predictors = st.text_input(
                    "Predictors (comma-separated)",
                    value=predictors_str,
                    key=f"{model_name}_predictors",
                    help="Comma-separated list of predictor columns"
                )
                config['models'][model_name]["predictors"] = [p.strip() for p in new_predictors.split(",") if p.strip()]
                
                # Cross-validation method
                config['models'][model_name]["cv_method"] = st.selectbox(
                    "Cross-Validation Method",
                    options=["group_kfold", "kfold", "stratified_kfold", "time_series_split"],
                    index=0 if "cv_method" not in config['models'][model_name] else 
                          ["group_kfold", "kfold", "stratified_kfold", "time_series_split"].index(config['models'][model_name]["cv_method"]),
                    key=f"{model_name}_cv_method",
                    help="Method for cross-validation"
                )
                
                # CV parameters
                st.subheader("Cross-Validation Parameters")
                
                if "cv_params" not in config['models'][model_name]:
                    config['models'][model_name]["cv_params"] = {}
                
                if config['models'][model_name]["cv_method"] == "group_kfold":
                    config['models'][model_name]["cv_params"]["group_column"] = st.text_input(
                        "Group Column",
                        value=config['models'][model_name]["cv_params"].get("group_column", "Year"),
                        key=f"{model_name}_group_column",
                        help="Column to use for grouping in group k-fold"
                    )
                
                config['models'][model_name]["cv_params"]["n_splits"] = st.number_input(
                    "Number of Splits",
                    min_value=-1,
                    max_value=20,
                    value=int(config['models'][model_name]["cv_params"].get("n_splits", 5)),
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
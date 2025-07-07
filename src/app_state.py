import streamlit as st
import yaml
import importlib

from pathlib import Path

from .data import GoogleSheetsHandler
from .worker import Workforce

@st.cache_data
def load_config(file):
    try:
        with open(file, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        st.error(f"Error reading config file: {str(e)}")
        st.stop()

def load_workforce(config):
    
    workforce_file = Path(config['workforce_file'])

    if workforce_file.exists():
        workforce = Workforce()
        workforce.load(filename = workforce_file)
        return workforce
    return Workforce()

def load_model_class(config, param_name):
    try:
        # Get the full class path
        class_path = config[param_name]['class']

        # Split module path and class name
        module_path, class_name = class_path.rsplit('.', 1)

        # Import the module and get the class
        module = importlib.import_module(module_path)
        model_class = getattr(module, class_name)

        return model_class
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import {class_path}: {e}")
    except KeyError as e:
        raise KeyError(f"Missing config key: {e}")

@st.cache_data
def load_data(config):
    gsheets = GoogleSheetsHandler()
    gsheets.setup_credentials_from_file(config['gsheets']['credentials_file'])
    field_data = gsheets.run(
        spreadsheet_url=config['gsheets']['spreadsheet_url'], 
        worksheet_name=config['gsheets']['worksheet_name']
    )

    return field_data

def clean_data(data, config, param_name, include_target = True):
    if include_target:
        return data.dropna(subset=[config[param_name]['target']] + config[param_name]['predictors'])
    else:
        return data.dropna(subset=config[param_name]['predictors'])

@st.cache_data
def load_and_clean_data(config, param_name, include_target = True):
    data_raw = load_data(config)
    data_clean = clean_data(data_raw, config, param_name, include_target)
    return data_raw, data_clean

@st.cache_resource
def get_trained_model(config, param_name, data):
    model = load_model_class(config, param_name)
    predictor = model()
    _ = predictor.train(
        data=data,
        target_column=config[param_name]['target'],
        feature_columns=config[param_name]['predictors'],
        cv_method=config[param_name]['cv_method'],
        cv_params=config[param_name]['cv_params']
    )

    return predictor

def get_predictions(config, param_name, model, data, year):

    data_to_predict = data.loc[data['Year'] == year]
    data_to_predict = clean_data(data_to_predict, config, param_name, include_target=False)

    if data_to_predict.empty:
        st.error('No data available for the selected year.')
        st.stop()

    try:
        data_to_predict['predicted_hours'] = model.predict(data_to_predict)
    except Exception as e:
        st.error(f"Error during prediction: {str(e)}")
        st.stop()

    return data_to_predict



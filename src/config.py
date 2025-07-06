import yaml
import streamlit as st

import importlib

def load_config(file):
    try:
        with open(file, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        st.error(f"Error reading config file: {str(e)}")

def load_model_class(config):
    try:
        # Get the full class path
        class_path = config['model']['class']

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
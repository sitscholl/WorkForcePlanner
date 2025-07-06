import streamlit as st

from pathlib import Path

from src.config import load_config
from src.utils import load_data_and_train_model, load_workforce

# --- Load configuration ---
if 'config' not in st.session_state:
    st.session_state.config = load_config('config.yaml')

# --- Load data and model ---
if 'predictor' not in st.session_state or 'data' not in st.session_state:
    with st.spinner("Loading data and training model..."):
        predictor, data = load_data_and_train_model(st.session_state.config)
        st.session_state.predictor = predictor
        st.session_state.data = data

# --- Load workforce ---
workforce_file = Path(st.session_state.config['workforce_file'])
if 'workforce' not in st.session_state:
    st.session_state.workforce = load_workforce(workforce_file)

# --- Predict working hours ---
st.session_state.data['predicted_hours'] = st.session_state.predictor.predict(st.session_state.data)

# --- Calculate start and end days ---

# --- Display Timeline ---
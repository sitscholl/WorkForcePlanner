import streamlit as st
import yaml

from pathlib import Path

from src.app_state import load_config, load_field_collection
from src.ui_components import render_sidebar
from src.fields.field import Field
from src.fields.field_collection import FieldCollection


# Set page title
st.set_page_config(page_title="Field Management", page_icon="🗃")
st.title("Field Management")

# --- Load  ---
config = load_config("config.yaml")

# --- Render Sidebar ---
render_sidebar(config)

field_collection = load_field_collection(config)
fields_file = Path(config.get('field_collection_file', 'FieldsCollection.yaml'))

# --- Manual Load from Uploaded YAML (overwrites current) ---
st.header("Persistence")
uploaded_file = st.file_uploader("Load Fields from YAML", type=["yaml", "yml"])
if uploaded_file is not None:
    with open(fields_file, "wb") as f:
        f.write(uploaded_file.read())
    st.success("Fields loaded from uploaded file.")
    field_collection.load(fields_file)

with st.form("Add Field"):
    new_field_name = st.text_input("Field Name")
    new_variety = st.text_input("Variety")
    new_order = st.number_input("Order", min_value=1, step=1, value=1)
    submitted = st.form_submit_button("Add Field")
    if submitted:
        try:
            field = Field(Field=new_field_name, Variety=new_variety, Order=new_order)
            field_collection.add_field(field)
            field_collection.save(fields_file)
            st.success(f"Field '{new_field_name}' added.")
        except Exception as e:
            st.error(str(e))

fields = field_collection.get_fields()

st.subheader("Existing Fields")
for i, field in enumerate(fields):
    with st.expander(f"{field.Field} ({field.Variety})"):
        col1, col2 = st.columns(2)
        with col1:
            updated_name = st.text_input(f"Name {i}", value=field.Field, key=f"name_{i}")
            updated_variety = st.text_input(f"Variety {i}", value=field.Variety, key=f"variety_{i}")
            updated_order = st.number_input(f"Order {i}", value=field.Order if field.Order is not None else 0, key=f"order_{i}")
            if st.button(f"Update {i}"):
                try:
                    updated_field = Field(Field=updated_name, Variety=updated_variety, Order=updated_order)
                    field_collection.update_field(field.Field, field.Variety, updated_field)
                    field_collection.save(fields_file)
                    st.success(f"Field '{updated_name}' updated.")
                except Exception as e:
                    st.error(str(e))
        with col2:
            if st.button(f"Remove {i}"):
                try:
                    field_collection.remove_field(field.Field, field.Variety)
                    field_collection.save(fields_file)
                    st.success(f"Field '{field.Field}' removed.")
                except Exception as e:
                    st.error(str(e))

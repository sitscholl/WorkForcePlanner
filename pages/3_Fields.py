import streamlit as st

from pathlib import Path

from src.app_state import load_config, load_field_collection
from src.ui_components import render_sidebar
from src.fields.field import Field
from src.fields.field_collection import FieldCollection


# Set page title
st.set_page_config(page_title="Field Management", page_icon="🗃")
st.title("Field Management")

# --- Load  ---
config = load_config("config/config.yaml")

# --- Render Sidebar ---
render_sidebar(config)

field_collection = load_field_collection(config)
fields_file = Path("config", f"field_collection_{config['year']}.yaml")

# --- Manual Load from Uploaded YAML (overwrites current) ---
st.header("Persistence")
uploaded_file = st.file_uploader("Load Fields from YAML", type=["yaml", "yml"])
if uploaded_file is not None:
    with open(fields_file, "wb") as f:
        f.write(uploaded_file.read())
    st.success("Fields loaded from uploaded file.")
    field_collection.load(fields_file)

# --- Download current fields ---
if fields_file.exists():
    with open(fields_file, "rb") as f:
        st.download_button(
            label="Download Current Fields YAML",
            data=f,
            file_name="fields.yaml",
            mime="application/x-yaml"
        )

# --- Add Field ---
st.header("Add New Field")
with st.form("add_field_form"):
    new_field_name = st.text_input("Field Name")
    new_variety = st.text_input("Variety")
    new_harvest_round = st.number_input("Harvest Round", min_value=1, step=1, value=1, help="Harvest round number (e.g., 1 for first harvest, 2 for second harvest)")

    # Show current number of fields and suggest default order
    current_field_count = len(field_collection.get_fields())
    st.info(f"Current number of fields: {current_field_count}. New field will be inserted at the specified position.")

    new_order = st.number_input(
        "Order (Position)",
        min_value=1,
        max_value=current_field_count + 1,
        step=1,
        value=current_field_count + 1,
        help="Position where this field should be inserted. Existing fields will be shifted down if necessary."
    )
    submitted = st.form_submit_button("Add Field")
    if submitted:
        if new_field_name and new_variety:
            try:
                field = Field(field=new_field_name, variety=new_variety, harvest_round=new_harvest_round, order=new_order)
                field_collection.add_field(field)
                field_collection.save(fields_file)
                st.success(f"Field '{new_field_name}' ({new_variety}) - Round {new_harvest_round} added at position {new_order}.")
                st.rerun()  # Force rerun to refresh the field list
            except Exception as e:
                st.error(str(e))
        else:
            st.error("Please fill in Field Name and Variety.")

# --- List and Modify Fields ---
st.header("Current Fields")
fields = field_collection.get_fields()
if not fields:
    st.info("No fields in the collection.")
else:
    # Show fields in a table format for better overview
    st.subheader("Field Overview")
    st.table(field_collection.to_dataframe())

    st.subheader("Edit Fields")
    for i, field in enumerate(fields):
        with st.expander(f"#{field.order}: {field.field} ({field.variety}) - Round {field.harvest_round}"):
            updated_name = st.text_input("Field Name", value=field.field, key=f"name_{i}")
            updated_variety = st.text_input("Variety", value=field.variety, key=f"variety_{i}")
            updated_harvest_round = st.number_input("Harvest Round", value=field.harvest_round, min_value=1, step=1, key=f"harvest_round_{i}", help="Harvest round number")

            # Show current position and allow reordering
            current_order = field.order if field.order is not None else i + 1
            updated_order = st.number_input(
                "Order (Position)",
                value=current_order,
                min_value=1,
                max_value=len(fields),
                step=1,
                key=f"order_{i}",
                help="Change position to reorder this field. Other fields will be shifted accordingly."
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_{i}"):
                    try:
                        updated_field = Field(field=updated_name, variety=updated_variety, harvest_round=updated_harvest_round, order=updated_order)
                        field_collection.update_field(field.field, field.variety, field.harvest_round, updated_field)
                        field_collection.save(fields_file)
                        st.success(f"Field '{updated_name}' updated.")
                        st.rerun()  # Force rerun to refresh the field list
                    except Exception as e:
                        st.error(str(e))
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    try:
                        field_collection.remove_field(field.field, field.variety, field.harvest_round)
                        field_collection.save(fields_file)
                        st.warning(f"Field '{field.field}' ({field.variety}) - Round {field.harvest_round} removed.")
                        st.rerun()  # Force rerun to refresh the field list
                    except Exception as e:
                        st.error(str(e))
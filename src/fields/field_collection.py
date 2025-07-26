import yaml
import streamlit as st

class FieldCollection:
    def __init__(self):
        self.fields = []

    def _update_field_order(self):
        """Update field order to be sequential starting from 1"""
        for i, field in enumerate(self.fields):
            field.order = i + 1

    def add_field(self, field):
        """Add a field at the specified order position, shifting other fields as needed"""
        # Uniqueness is now based on both field name and variety
        for f in self.fields:
            if f.field == field.field and f.variety == field.variety:
                raise ValueError(f"Field with name '{field.field}' and variety '{field.variety}' already exists.")

        # Handle None order - append to end
        if field.order is None:
            field.order = len(self.fields) + 1
            self.fields.append(field)
        else:
            # Ensure order is within valid range
            target_position = max(1, min(field.order, len(self.fields) + 1))
            
            # Insert at the specified position (convert to 0-based index)
            insert_index = target_position - 1
            self.fields.insert(insert_index, field)
        
        # Renumber all fields to maintain sequential order
        self._update_field_order()

    def get_fields(self):
        return self.fields

    def update_field(self, field_name, variety, new_field):
        """Update an existing field, handling order changes properly"""
        # Find the field to update
        old_field_index = None
        for idx, f in enumerate(self.fields):
            if f.field == field_name and f.variety == variety:
                old_field_index = idx
                break
        
        if old_field_index is None:
            raise ValueError(f"Field with name '{field_name}' and variety '{variety}' not found.")
        
        # Check for uniqueness (excluding the field being updated)
        for idx, f in enumerate(self.fields):
            if idx != old_field_index and f.field == new_field.field and f.variety == new_field.variety:
                raise ValueError(f"Field with name '{new_field.field}' and variety '{new_field.variety}' already exists.")
        
        # Remove the old field
        old_field = self.fields.pop(old_field_index)
        
        # Handle None order - keep at end
        if new_field.order is None:
            new_field.order = len(self.fields) + 1
            self.fields.append(new_field)
        else:
            # Ensure order is within valid range
            target_position = max(1, min(new_field.order, len(self.fields) + 1))
            
            # Insert at the specified position (convert to 0-based index)
            insert_index = target_position - 1
            self.fields.insert(insert_index, new_field)
        
        # Renumber all fields to maintain sequential order
        self._update_field_order()

    def remove_field(self, field_name, variety):
        for idx, f in enumerate(self.fields):
            if f.field == field_name and f.variety == variety:
                del self.fields[idx]
                self._update_field_order()
                return
        raise ValueError(f"Field with name '{field_name}' and variety '{variety}' not found.")

    def save(self, filename='FieldsCollection.yaml'):
        # Convert Pydantic models to dictionaries, excluding the workforce field
        fields_data = [field.model_dump() for field in self.fields]

        # Save to YAML file
        with open(filename, 'w') as file:
            yaml.dump(fields_data, file, default_flow_style=False, indent=2)
    
    def load(self, filename='FieldsCollection.yaml'):
        try:
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)
                if data is None:
                    return
            # Import Field here to avoid circular import
            from .field import Field
            self.fields = [Field(**item) for item in data]
            # Ensure proper ordering after loading
            self._update_field_order()
        except FileNotFoundError:
            st.warning(f"File {filename} not found. Starting with empty fields.")
            self.fields = []
        except Exception as e:
            st.error(f"Error loading fields from {filename}: {e}")
            st.stop()
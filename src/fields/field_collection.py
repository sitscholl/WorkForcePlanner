import yaml

class FieldCollection:
    def __init__(self):
        self.fields = []

    def add_field(self, field):
        # Uniqueness is now based on both field name and variety
        for f in self.fields:
            if f.field == field.field and f.variety == field.variety:
                raise ValueError(f"Field with name '{field.field}' and variety '{field.variety}' already exists.")
        self.fields.append(field)

    def get_fields(self):
        return self.fields

    def update_field(self, field_name, variety, new_field):
        for idx, f in enumerate(self.fields):
            if f.field == field_name and f.variety == variety:
                self.fields[idx] = new_field
                return
        raise ValueError(f"Field with name '{field_name}' and variety '{variety}' not found.")

    def remove_field(self, field_name, variety):
        for idx, f in enumerate(self.fields):
            if f.field == field_name and f.variety == variety:
                del self.fields[idx]
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
        except FileNotFoundError:
            st.warning(f"File {filename} not found. Starting with empty fields.")
            self.fields = []
        except Exception as e:
            st.error(f"Error loading fields from {filename}: {e}")
            st.stop()
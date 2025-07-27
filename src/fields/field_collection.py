import yaml
import streamlit as st
import pandas as pd

from pathlib import Path

class FieldCollection:
    def __init__(self):
        self.fields = []

    def _update_field_order(self):
        """Update field order to be sequential starting from 1"""
        for i, field in enumerate(self.fields):
            field.order = i + 1

    def add_field(self, field):
        """Add a field at the specified order position, shifting other fields as needed"""
        # Uniqueness is now based on field name, variety, and harvest round
        for f in self.fields:
            if f.field == field.field and f.variety == field.variety and f.harvest_round == field.harvest_round:
                raise ValueError(f"Field with name '{field.field}', variety '{field.variety}', and harvest round {field.harvest_round} already exists.")

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

    def update_field(self, field_name, variety, harvest_round, new_field):
        """Update an existing field, handling order changes properly"""
        # Find the field to update
        old_field_index = None
        for idx, f in enumerate(self.fields):
            if f.field == field_name and f.variety == variety and f.harvest_round == harvest_round:
                old_field_index = idx
                break
        
        if old_field_index is None:
            raise ValueError(f"Field with name '{field_name}', variety '{variety}', and harvest round {harvest_round} not found.")
        
        # Check for uniqueness (excluding the field being updated)
        for idx, f in enumerate(self.fields):
            if idx != old_field_index and f.field == new_field.field and f.variety == new_field.variety and f.harvest_round == new_field.harvest_round:
                raise ValueError(f"Field with name '{new_field.field}', variety '{new_field.variety}', and harvest round {new_field.harvest_round} already exists.")
        
        # Remove the old field
        self.fields.pop(old_field_index)

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

    def remove_field(self, field_name, variety, harvest_round):
        for idx, f in enumerate(self.fields):
            if f.field == field_name and f.variety == variety and f.harvest_round == harvest_round:
                del self.fields[idx]
                self._update_field_order()
                return
        raise ValueError(f"Field with name '{field_name}', variety '{variety}', and harvest round {harvest_round} not found.")

    def save(self, filename='FieldsCollection.yaml'):
        # Convert Pydantic models to dictionaries, excluding the workforce field
        fields_data = [field.model_dump() for field in self.fields]

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

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

    def to_dataframe(self):
        field_data = []
        for field in self.fields:
            field_data.append({
                "Order": field.order,
                "Field": field.field,
                "Variety": field.variety,
                "Harvest Round": field.harvest_round
            })
        return pd.DataFrame(field_data)

    def apply_field_config(self, fields_table):
        """
        Apply field configuration to expand table with harvest rounds and preserve order

        Args:
            fields_table (pd.DataFrame): Original fields table with predicted_hours

        Returns:
            pd.DataFrame: Expanded table with harvest rounds, ordered according to FieldCollection
        """
        if not self.fields:
            # Return empty DataFrame with same structure plus Harvest Round column
            result_df = fields_table.copy()
            result_df['Harvest Round'] = 1
            return result_df.iloc[0:0]

        # Get collection data as DataFrame
        collection_df = self.to_dataframe()

        # Create expanded rows based on the field collection order
        expanded_rows = []

        # Normalize case for matching
        fields_table_normalized = fields_table.copy()
        fields_table_normalized['Field'] = fields_table_normalized['Field'].str.lower()
        fields_table_normalized['Variety'] = fields_table_normalized['Variety'].str.lower()

        # Calculate total harvest rounds per field-variety combination
        harvest_counts = {}
        for field in self.fields:
            key = (field.field.lower(), field.variety.lower())
            if key not in harvest_counts:
                harvest_counts[key] = 0
            harvest_counts[key] = max(harvest_counts[key], field.harvest_round)

        # Process each field in the collection (preserving order)
        for field in self.fields:
            field_name_lower = field.field.lower()
            variety_lower = field.variety.lower()

            # Find matching row in fields_table
            matching_rows = fields_table_normalized[
                (fields_table_normalized['Field'] == field_name_lower) &
                (fields_table_normalized['Variety'] == variety_lower)
            ]

            if matching_rows.empty:
                st.warning(f"Field '{field.field}' with variety '{field.variety}' not found in the table.")
                continue  # Skip if field not found in table

            # Get the first matching row (should be unique per field-variety)
            field_row = matching_rows.iloc[0].copy()

            # Get total harvest rounds for this field-variety combination
            total_harvest_rounds = harvest_counts[(field_name_lower, variety_lower)]

            # Create row for this specific harvest round
            row_dict = field_row.to_dict()
            row_dict['Order'] = field.order
            row_dict['Field'] = field.field  # Restore original case
            row_dict['Variety'] = field.variety  # Restore original case
            row_dict['Harvest Round'] = field.harvest_round

            # Divide predicted hours by total harvest rounds for this field
            if 'predicted_hours' in row_dict and row_dict['predicted_hours'] is not None:
                row_dict['predicted_hours'] = row_dict['predicted_hours'] / total_harvest_rounds

            expanded_rows.append(row_dict)

        # Create new dataframe with expanded rows
        if expanded_rows:
            result_df = pd.DataFrame(expanded_rows)
            # Sort by order to maintain the sequence from FieldCollection
            result_df = result_df.sort_values('Order').reset_index(drop=True)
            return result_df
        else:
            # Return empty DataFrame with same structure plus required columns
            result_df = fields_table.copy()
            result_df['Harvest Round'] = 1
            result_df['Order'] = None
            return result_df.iloc[0:0]
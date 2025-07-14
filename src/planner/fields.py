
import pandas as pd
import streamlit as st

def apply_fields_config(fields_table, fields_config):
    """
    Apply field configuration to expand table with harvest rounds
    
    Args:
        fields_table (pd.DataFrame): Original fields table
        fields_config (dict): Fields configuration with field_order and field settings
        
    Returns:
        pd.DataFrame: Expanded table with harvest rounds
    """
    # Create expanded table with rows for each harvest round
    expanded_rows = []

    if fields_config is None:
        st.warning('No fields configuration provided. Schedule cannot be generated. Configure field order in Settings first.')
    
    # Check if we have a custom harvest round order
    if fields_config is not None and "harvest_round_order" in fields_config and fields_config["harvest_round_order"]:
        # Use the custom harvest round order
        for item in fields_config["harvest_round_order"]:
            # Extract field name and round number from the item
            field_name = item["field"]
            round_num = item["round"]
            harvest_rounds = max([i['round'] for i in fields_config["harvest_round_order"] if i['field'] == field_name])
                
            # Get the field row from the original table
            field_rows = fields_table[fields_table['Field'] == field_name]
            
            if field_rows.empty:
                continue  # Skip if field not found in table
            
            # Create a copy of the field row with the specified harvest round
            for _, field_row in field_rows.iterrows():
                row_dict = field_row.to_dict()
                row_dict['Harvest Round'] = round_num
                row_dict['predicted_hours'] = row_dict['predicted_hours'] / harvest_rounds
                expanded_rows.append(row_dict)

    # Create new dataframe with expanded rows
    if expanded_rows:
        return pd.DataFrame(expanded_rows)
    else:
        # Return empty DataFrame with same columns as input plus Harvest Round
        result_df = fields_table.copy()
        result_df['Harvest Round'] = 1
        return result_df.iloc[0:0]  # Return empty DataFrame with correct structure
    
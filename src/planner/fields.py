
import pandas as pd

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

    for field_name in fields_config.get('field_order', []):
        # Get harvest rounds for this field, default to 1 if not configured
        field_config = fields_config.get(field_name, {})
        harvest_rounds = field_config.get('harvest_rounds', 1)
        
        # Ensure harvest_rounds is an integer
        try:
            harvest_rounds = int(harvest_rounds)
        except (ValueError, TypeError):
            harvest_rounds = 1
        
        # Get the field row from the original table
        field_rows = fields_table[fields_table['Field'] == field_name]
        
        if field_rows.empty:
            continue  # Skip if field not found in table
        
        # For each harvest round, create a copy of the field row
        for round_num in range(1, harvest_rounds + 1):
            for _, field_row in field_rows.iterrows():
                row_dict = field_row.to_dict()
                row_dict['Harvest Round'] = round_num
                expanded_rows.append(row_dict)

    # Create new dataframe with expanded rows
    if expanded_rows:
        return pd.DataFrame(expanded_rows)
    else:
        # Return empty DataFrame with same columns as input plus Harvest Round
        result_df = fields_table.copy()
        result_df['Harvest Round'] = 1
        return result_df.iloc[0:0]  # Return empty DataFrame with correct structure
    
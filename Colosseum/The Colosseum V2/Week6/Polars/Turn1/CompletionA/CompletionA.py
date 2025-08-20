import polars as pl
import json

def fill_missing_params(df):
    """
    Fill missing parameters in item_params based on parameter_fields.
    If a field is in parameter_fields but not in item_params, add it with an empty string.
    """
    # Define a function to process each row
    def process_row(parameter_fields, item_params):
        # Parse JSON strings if they are strings
        if isinstance(parameter_fields, str):
            parameter_fields = json.loads(parameter_fields)
        if isinstance(item_params, str):
            item_params = json.loads(item_params)
        
        # Ensure item_params contains all fields from parameter_fields
        for field in parameter_fields:
            if field not in item_params:
                item_params[field] = ""
        
        return json.dumps(item_params)
    
    # Apply the function to each row
    return df.with_column(
        pl.struct(["parameter_fields", "item_params"])
        .apply(lambda x: process_row(x["parameter_fields"], x["item_params"]))
        .alias("item_params")
    )

# Example usage:
# Assuming df is your existing Polars DataFrame with parameter_fields and item_params columns
# df = fill_missing_params(df)
import polars as pl

def fill_missing_params(df):
    """
    Fill missing parameters in item_params based on parameter_fields.
    If a field is in parameter_fields but not in item_params, add it with an empty string.
    """
    # Define a function to process each row
    def process_row(parameter_fields, item_params):
        # Make a copy to avoid modifying the original
        item_params_updated = item_params.copy()
        
        # Ensure item_params contains all fields from parameter_fields
        for field in parameter_fields:
            if field not in item_params_updated:
                item_params_updated[field] = ""
        
        return item_params_updated
    
    # Apply the function to each row
    return df.with_column(
        pl.struct(["parameter_fields", "item_params"])
        .apply(lambda x: process_row(x["parameter_fields"], x["item_params"]))
        .alias("item_params")
    )

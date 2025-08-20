import polars as pl

# Example dataframe similar to your structure
df = pl.DataFrame({
    "parameter_fields": [
        ["color", "gender", "sub_brand", "mrp", "main_size", "style_description", "fit", "category", "final_ssn", "sub_gender", "brand", "sleeves"]
    ],
    "item_params": [
        {
            "fit": "RE06",
            "color": "NA",
            "gender": "ME",
            "category": "AP",
            "final_ssn": "AW23",
            "sub_brand": "NA",
            "sub_gender": "AD",
            "mrp": "2499",
            "brand": "FLM",
            "sleeves": "NA",
            "main_size": "36",
            "style_description": "5POCKETDENIM"
        }
    ]
})

# Define a function to update item_params
def fill_missing_params(parameter_fields, item_params):
    return {
        key: item_params.get(key, "")
        for key in parameter_fields
    }

# Apply the above function to each row
df = df.with_columns(
    pl.struct("parameter_fields", "item_params")
      .map_elements(lambda x: fill_missing_params(x["parameter_fields"], x["item_params"]))
      .alias("item_params")
)

print(df)

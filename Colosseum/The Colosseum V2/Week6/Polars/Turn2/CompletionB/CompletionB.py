import polars as pl

# Sample polars DataFrame
df = pl.DataFrame({
    "parameter_fields": [
        ["color", "gender", "sub_brand", "mrp", "main_size", "style_description", 
         "fit", "category", "final_ssn", "sub_gender", "brand", "sleeves"]
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

def update_item_params(df):
    def update_params(fields, params):
        for field in fields:
            if field not in params:
                params[field] = ""
        return params
    
    return df.with_columns(
        pl.struct(["parameter_fields", "item_params"])
          .apply(lambda x: update_params(x["parameter_fields"], x["item_params"])).alias("item_params")
    )

updated_df = update_item_params(df)
print(updated_df)

# ideal_completion.py

import pandas as pd

# Function to replicate rows
def replicate_rows(df1, df2, array):
    # Create an empty DataFrame to store the results
    result = pd.DataFrame(columns=df1.columns)
    
    # Loop through each row in df1
    for idx, row in df1.iterrows():
        # Check if the row has 'Total' in the specified columns
        if all(row[col] == 'Total' for col in array):
            # For each unique combination in df2
            for _, df2_row in df2.iterrows():
                # Create a new row by replacing 'Total' with the corresponding value from df2
                new_row = row.copy()
                for col in array:
                    new_row[col] = df2_row[col]
                # Append the new row to the result DataFrame
                result = result._append(new_row, ignore_index=True)
        else:
            # If the row doesn't contain 'Total', just add it to the result DataFrame
            result = result._append(row, ignore_index=True)
    
    return result
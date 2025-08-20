import hashlib
import pandas as pd
from datetime import datetime

def is_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except:
        return False

# MD5 hashing function
def generate_md5(line):
    return hashlib.md5(line.encode('utf-8')).hexdigest()

def process_records(input_df, database_df):
    updated_records = []

    for index, row in input_df.iterrows():
        row_list = row.tolist()
        record_str = ','.join(map(str, row_list))
        record_hash = generate_md5(record_str)

        # Skip processing if hash exists
        if record_hash in database_df['ID'].values:
            continue  

        bank_pattern = detect_bank_pattern(row_list)
        new_record = {"ID": record_hash}

        if bank_pattern == "MetroBank Credit":
            new_record.update({
                "Record": len(database_df) + 1,
                "Date Purchased": row_list[0],
                "Figure": row_list[1],
                "Description": row_list[2],
                "Type": "CreditCard"
            })
            print("Processed MetroBank Credit record.")

        elif bank_pattern == "MetroBank Debit":
            date_purchased = extract_date_from_description(row_list[2])
            new_record.update({
                "Record": len(database_df) + 1,
                "Date Committed": row_list[0],
                "Figure": row_list[1],
                "Description": row_list[2],
                "Balance": row_list[3],
                "Date Purchased": date_purchased,
                "Type": "DebitCard"
            })
            print("Processed MetroBank Debit record.")

        elif bank_pattern == "HSBC Credit":
            new_record.update({
                "Record": len(database_df) + 1,
                "Date Purchased": row_list[3],
                "Figure": row_list[2],
                "Description": row_list[1],
                "Type": "CreditCard"
            })
            print("Processed HSBC Credit record.")

        elif bank_pattern == "HSBC Debit":
            date_purchased = extract_date_from_description(row_list[1])
            new_record.update({
                "Record": len(database_df) + 1,
                "Balance": row_list[0],
                "Description": row_list[1],
                "Figure": row_list[2],
                "Date Committed": row_list[3],
                "Date Purchased": date_purchased,
                "Type": "DebitCard"
            })
            print("Processed HSBC Debit record.")

        updated_records.append(new_record)

    updated_df = pd.DataFrame(updated_records)
    database_df = pd.concat([database_df, updated_df], ignore_index=True)
    return database_df

def extract_date_from_description(description):
    for word in description.split():
        if is_date(word):
            return word
    return None  # Fallback if no date found

def detect_bank_pattern(row):
    # Ensure there are enough columns
    if len(row) < 4:
        return None

    # MetroBank Credit check
    if (is_date(str(row[0])) and pd.api.types.is_number(row[1]) and isinstance(row[2], str)):
        return "MetroBank Credit"

    # MetroBank Debit check
    if (is_date(str(row[0])) and pd.api.types.is_number(row[1]) and isinstance(row[2], str) and 
        pd.api.types.is_number(row[3])):
        return "MetroBank Debit"

    # HSBC Credit check
    if (is_date(str(row[3])) and pd.api.types.is_number(row[2]) and isinstance(row[1], str) and pd.isna(row[0])):
        return "HSBC Credit"

    # HSBC Debit check
    if (is_date(str(row[3])) and pd.api.types.is_number(row[2]) and isinstance(row[1], str) and 
        pd.api.types.is_number(row[0])):
        return "HSBC Debit"

    return None

# Usage example
database_df = pd.read_csv("database.csv").fillna('')
input_df = pd.read_csv("input.csv").fillna('')
database_df = process_records(input_df, database_df)
database_df.to_csv("database.csv", index=False)
print("Records processing completed.")

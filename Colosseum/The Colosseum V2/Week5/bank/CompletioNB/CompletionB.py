import hashlib
import pandas as pd
import datetime
import re


def generate_md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()


def process_bank_records(df):
    # Loop through each row in the input DataFrame
    for index, row in df.iterrows():
        row_list = row.tolist()
        hash_value = generate_md5_hash(str(row_list))

        # Skip the record if it already exists
        if hash_value in database_df['ID'].values:
            print(f"Record {index} already exists. Skipping...")
            continue

        bank_pattern = detect_bank_pattern(row_list)
        if not bank_pattern:
            print(f"Row {index} does not match any expected pattern.")
            continue

        new_record = transform_record(index, row_list, hash_value, bank_pattern)
        add_to_database(new_record)


def detect_bank_pattern(row):
    if len(row) < 4:
        return None

    if (is_date(str(row[0])) and
            isinstance(row[1], str) and 
            pd.api.types.is_number(row[2])):
        if pd.isna(row[3]):
            return "CommonWealth Credit"
        elif isinstance(row[3], (float, int)):
            return "CommonWealth Debit"

    if (is_date(str(row[3])) and
            pd.api.types.is_number(row[2]) and
            isinstance(row[1], str) and pd.isna(row[0])):
        return "NAB Credit"
    elif (is_date(str(row[3])) and
            pd.api.types.is_number(row[2]) and
            isinstance(row[1], str) and
            pd.api.types.is_number(row[0])):
        return "NAB Debit"

    return None


def transform_record(index, row, record_id, pattern):
    mappings = {
        "CommonWealth Credit": {
            "Date Purchased": row[0],
            "Figure": row[1],
            "Description": row[2],
            "Type": "CreditCard",
        },
        "CommonWealth Debit": {
            "Date Purchased": extract_date(row[2]),
            "Date Committed": row[0],
            "Figure": row[1],
            "Description": row[2],
            "Balance": row[3],
            "Type": "DebitCard",
        },
        "NAB Credit": {
            "Date Purchased": row[3],
            "Figure": row[2],
            "Description": row[1],
            "Type": "CreditCard",
        },
        "NAB Debit": {
            "Date Purchased": extract_date(row[1]),
            "Date Committed": row[3],
            "Figure": row[2],
            "Description": row[1],
            "Balance": row[0],
            "Type": "DebitCard",
        }
    }

    # Create a new record based on the transformation mapping
    record = {
        'Record': index + 1,
        'ID': record_id,
        'BANK': pattern.split()[0],
        **mappings.get(pattern, {})
    }
    return record


def add_to_database(record):
    global database_df

    # Append to DataFrame
    database_df = pd.concat([database_df, pd.DataFrame([record])], ignore_index=True)
    print(f"Added record: {record}")

    # Save database to file
    database_df.to_csv("database.csv", index=False)


def is_date(string):
    try:
        datetime.datetime.strptime(string.strip(), '%d/%m/%Y')
        return True
    except ValueError:
        return False


def extract_date(description):
    date_match = re.search(r"(\d{2}/\d{2}/\d{4})", description)
    return date_match.group(1) if date_match else ""


# Load existing database
database_df = pd.read_csv('database.csv').fillna('')

# Sample input data
df = pd.DataFrame([
    ['12/05/2024', '50', 'Groceries', 100],
    ['15/05/2024', '60', 'Clothes', None],
    ['19/07/2024', '150', 'Loan', None],
    [None, '200', 'Description', '21/05/2023']
], columns=['Column 1', 'Column 2', 'Column 3', 'Column 4'])

process_bank_records(df)

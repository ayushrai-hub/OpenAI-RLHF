import hashlib
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_mock_data():
    # Generate dates for the last 30 days
    end_date = datetime.now()
    dates = [(end_date - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
    
    # Sample descriptions for transactions
    descriptions = [
        "AMAZON RETAIL",
        "WALMART GROCERY",
        "NETFLIX SUBSCRIPTION",
        "UBER RIDE",
        "STARBUCKS COFFEE",
        "TARGET STORE",
        "CHEVRON GAS",
        "SPOTIFY PREMIUM",
        "DOORDASH DELIVERY",
        "HOME DEPOT"
    ]
    
    # Generate MetroBank Credit records
    metro_credit = pd.DataFrame({
        'date': random.sample(dates, 5),
        'amount': [round(random.uniform(10, 500), 2) for _ in range(5)],
        'description': random.sample(descriptions, 5),
        'balance': ['' for _ in range(5)]  # Empty balance for credit
    })
    
    # Generate MetroBank Debit records
    metro_debit = pd.DataFrame({
        'date': random.sample(dates, 5),
        'amount': [round(random.uniform(10, 500), 2) for _ in range(5)],
        'description': [f"{desc} {random.choice(dates)}" for desc in random.sample(descriptions, 5)],
        'balance': [round(random.uniform(1000, 5000), 2) for _ in range(5)]
    })
    
    # Generate HSBC Credit records
    hsbc_credit = pd.DataFrame({
        'balance': ['' for _ in range(5)],  # Empty balance for credit
        'description': random.sample(descriptions, 5),
        'amount': [round(random.uniform(10, 500), 2) for _ in range(5)],
        'date': random.sample(dates, 5)
    })
    
    # Generate HSBC Debit records
    hsbc_debit = pd.DataFrame({
        'balance': [round(random.uniform(1000, 5000), 2) for _ in range(5)],
        'description': [f"{desc} {random.choice(dates)}" for desc in random.sample(descriptions, 5)],
        'amount': [round(random.uniform(10, 500), 2) for _ in range(5)],
        'date': random.sample(dates, 5)
    })
    
    # Create empty database DataFrame with required columns
    database_df = pd.DataFrame(columns=[
        'ID', 'Record', 'Date Purchased', 'Figure', 
        'Description', 'Type', 'Date Committed', 'Balance'
    ])
    
    return metro_credit, metro_debit, hsbc_credit, hsbc_debit, database_df

def is_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except:
        return False

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
    return None

def detect_bank_pattern(row):
    if len(row) < 4:
        return None
        
    # MetroBank Credit check
    if (is_date(str(row[0])) and isinstance(row[1], (int, float)) and 
        isinstance(row[2], str) and pd.isna(row[3])):
        return "MetroBank Credit"
        
    # MetroBank Debit check
    if (is_date(str(row[0])) and isinstance(row[1], (int, float)) and 
        isinstance(row[2], str) and isinstance(row[3], (int, float))):
        return "MetroBank Debit"
        
    # HSBC Credit check
    if (is_date(str(row[3])) and isinstance(row[2], (int, float)) and 
        isinstance(row[1], str) and pd.isna(row[0])):
        return "HSBC Credit"
        
    # HSBC Debit check
    if (is_date(str(row[3])) and isinstance(row[2], (int, float)) and 
        isinstance(row[1], str) and isinstance(row[0], (int, float))):
        return "HSBC Debit"
        
    return None

# Generate mock data
metro_credit, metro_debit, hsbc_credit, hsbc_debit, database_df = generate_mock_data()

# Process each type of transaction
print("\nProcessing MetroBank Credit transactions...")
database_df = process_records(metro_credit, database_df)

print("\nProcessing MetroBank Debit transactions...")
database_df = process_records(metro_debit, database_df)

print("\nProcessing HSBC Credit transactions...")
database_df = process_records(hsbc_credit, database_df)

print("\nProcessing HSBC Debit transactions...")
database_df = process_records(hsbc_debit, database_df)

# Display results
print("\nFinal database contents:")
print(database_df)

# Optional: Save to CSV
database_df.to_csv("processed_transactions.csv", index=False)
print("\nResults saved to 'processed_transactions.csv'")
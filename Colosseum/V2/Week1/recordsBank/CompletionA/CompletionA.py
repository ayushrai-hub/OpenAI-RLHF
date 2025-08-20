def process_bank_row(self, row):
    pattern = self.detect_bank_pattern(row)
    if pattern == "BankTwo Credit":
        return self.process_banktwo_credit(row)
    elif pattern == "BankTwo Debit":
        return self.process_banktwo_debit(row)
    else:
        print(f"Row does not match any expected pattern: {row}")
        return None

def process_banktwo_credit(self, row):
    line = ','.join(map(str, row))
    line_hash = hashlib.md5(line.encode()).hexdigest()
    
    if line_hash in self.database_df['ID'].values:
        print(f"Duplicate record found: {line}")
        return None
    
    new_record = {
        'ID': line_hash,
        'Record': len(self.database_df) + 1,
        'Date Purchased': row[3],
        'Amount': row[2],
        'Explanation': row[1],
        'Type': 'CreditCard',
        'BANK': 'BankTwo'
    }
    return new_record

def process_banktwo_debit(self, row):
    line = ','.join(map(str, row))
    line_hash = hashlib.md5(line.encode()).hexdigest()
    
    if line_hash in self.database_df['ID'].values:
        print(f"Duplicate record found: {line}")
        return None
    
    date_purchased = self.extract_date_from_explanation(row[1])
    
    new_record = {
        'ID': line_hash,
        'Record': len(self.database_df) + 1,
        'Balance': row[0],
        'Explanation': row[1],
        'Amount': row[2],
        'Date Processed': row[3],
        'Date Purchased': date_purchased,
        'Type': 'DebitCard',
        'BANK': 'BankTwo'
    }
    return new_record

def extract_date_from_explanation(self, explanation):
    # This is a placeholder. You'll need to implement the actual date extraction logic
    # based on the format of dates in the explanation field.
    return ''

def load_records(self):
    filepath = filedialog.askopenfilename(
        title="Select a bank record file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )

    if not filepath:
        print("No file selected.")
        return

    try:
        input_df = pd.read_csv(filepath)
        print(f"File loaded successfully with {len(input_df)} rows.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load the file: {e}")
        return

    file_hash = self.generate_md5_hash_of_file(filepath)
    print(f"MD5 hash of file: {file_hash}")

    new_records = []
    for index, row in input_df.iterrows():
        row_list = row.tolist()
        print(f"Processing Row {index}: {row_list}")

        new_record = self.process_bank_row(row_list)
        if new_record:
            new_records.append(new_record)

    if new_records:
        new_df = pd.DataFrame(new_records)
        self.database_df = pd.concat([self.database_df, new_df], ignore_index=True)
        self.database_df.to_csv(self.database_filename, index=False)
        self.refresh_tree_view()
        print(f"Added {len(new_records)} new records to the database.")
    else:
        print("No new records were added.")

    print("File processing completed.")

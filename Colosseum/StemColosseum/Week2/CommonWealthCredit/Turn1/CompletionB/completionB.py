import re
def load_records(self):
    filepath = filedialog.askopenfilename(
        title="Select a bank record file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )

    if not filepath:
        print("No file selected.")
        return

    try:
        input_df = pd.read_csv(filepath, header=None)  # Assumed no header
        print(f"File loaded successfully with {len(input_df)} rows.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load the file: {e}")
        return

    for index, row in input_df.iterrows():
        row_list = row.tolist()
        print(f"Row {index}: {row_list}")

        bank_pattern = self.detect_bank_pattern(row_list)
        if bank_pattern == "CommonWealth Credit":
            self.process_commonwealth_credit(row_list)
        elif bank_pattern == "CommonWealth Debit":
            self.process_commonwealth_debit(row_list)
        elif bank_pattern == "NAB Credit":
            self.process_nab_credit(row_list)
        elif bank_pattern == "NAB Debit":
            self.process_nab_debit(row_list)
        else:
            print(f"Row {index} does not match any expected pattern.")

    print("File processing completed.")


def detect_bank_pattern(self, row):
    # Include logic to detect all four patterns:
    if len(row) >= 4:
        # For CommonWealth patterns
        if isinstance(row[0], str) and \
           pd.api.types.is_number(row[1]) and \
           isinstance(row[2], str):
            
            if len(row) == 3:
                return "CommonWealth Credit"
            elif len(row) == 4:
                return "CommonWealth Debit"
        
        # For NAB patterns
        if pd.isna(row[0]) and isinstance(row[1], str) and \
           pd.api.types.is_number(row[2]) and is_date(str(row[3])):
            return "NAB Credit"
        elif pd.api.types.is_number(row[0]) and isinstance(row[1], str) and \
             pd.api.types.is_number(row[2]) and is_date(str(row[3])):
            return "NAB Debit"
    return None


def process_commonwealth_credit(self, row):
    line_hash = hashlib.md5(','.join(map(str, row)).encode()).hexdigest()
    if line_hash in self.database_df['ID'].values:
        print("Record already exists. Skipping.")
        return
    
    new_record = {
        "Record": self.get_next_record_number(),
        "Date Purchased": row[0],
        "Date Committed": "",
        "Figure": row[1],
        "Description": row[2],
        "Balance": "",
        "Category": "",
        "Sub-Category": "",
        "ID": line_hash,
        "BANK": "CommonWealth",
        "Type": "CreditCard",
        "Comments": ""
    }
    
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)
    print(f"Added new CommonWealth Credit record: {new_record}")

def process_commonwealth_debit(self, row):
    line_hash = hashlib.md5(','.join(map(str, row)).encode()).hexdigest()
    if line_hash in self.database_df['ID'].values:
        print("Record already exists. Skipping.")
        return
    
    # Extract date from Column 3 description if possible
    date_purchased = self.extract_date_from_description(row[2])
    
    new_record = {
        "Record": self.get_next_record_number(),
        "Date Purchased": date_purchased,
        "Date Committed": row[0],
        "Figure": row[1],
        "Description": row[2],
        "Balance": row[3],
        "Category": "",
        "Sub-Category": "",
        "ID": line_hash,
        "BANK": "CommonWealth",
        "Type": "DebitCard",
        "Comments": ""
    }
    
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)
    print(f"Added new CommonWealth Debit record: {new_record}")


def process_nab_credit(self, row):
    line_hash = hashlib.md5(','.join(map(str, row)).encode()).hexdigest()
    if line_hash in self.database_df['ID'].values:
        print("Record already exists. Skipping.")
        return
    
    new_record = {
        "Record": self.get_next_record_number(),
        "Date Purchased": row[3],
        "Date Committed": "",
        "Figure": row[2],
        "Description": row[1],
        "Balance": "",
        "Category": "",
        "Sub-Category": "",
        "ID": line_hash,
        "BANK": "NAB",
        "Type": "CreditCard",
        "Comments": ""
    }
    
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)
    print(f"Added new NAB Credit record: {new_record}")


def process_nab_debit(self, row):
    line_hash = hashlib.md5(','.join(map(str, row)).encode()).hexdigest()
    if line_hash in self.database_df['ID'].values:
        print("Record already exists. Skipping.")
        return
    
    # Extract date from Column 2 description if possible
    date_purchased = self.extract_date_from_description(row[1])
    
    new_record = {
        "Record": self.get_next_record_number(),
        "Date Purchased": date_purchased,
        "Date Committed": row[3],
        "Figure": row[2],
        "Description": row[1],
        "Balance": row[0],
        "Category": "",
        "Sub-Category": "",
        "ID": line_hash,
        "BANK": "NAB",
        "Type": "DebitCard",
        "Comments": ""
    }
    
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)
    print(f"Added new NAB Debit record: {new_record}")

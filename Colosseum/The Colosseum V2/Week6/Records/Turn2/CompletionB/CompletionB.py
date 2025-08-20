

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

    for index, row in input_df.iterrows():
        row_list = row.tolist()
        bank_pattern = self.detect_bank_pattern(row_list)
        line_hash = hashlib.md5(str(row_list).encode()).hexdigest()

        if line_hash in self.database_df['ID'].values:
            print(f"Row {index}: Duplicate found. Skipping.")
            continue  # Duplicate record, skip

        if bank_pattern == "MetroBank Credit":
            print(f"Row {index}: MetroBank Credit processed.")
            self.process_metrobank_credit(row_list, line_hash)
        elif bank_pattern == "MetroBank Debit":
            print(f"Row {index}: MetroBank Debit processed.")
            self.process_metrobank_debit(row_list, line_hash)
        elif bank_pattern == "HSBC Credit":
            print(f"Row {index}: HSBC Credit processed.")
            self.process_hsbc_credit(row_list, line_hash)
        elif bank_pattern == "HSBC Debit":
            print(f"Row {index}: HSBC Debit processed.")
            self.process_hsbc_debit(row_list, line_hash)
        else:
            print(f"Row {index}: No matching pattern found. Skipping.")

    self.database_df.to_csv(self.database_filename, index=False)
    self.refresh_tree_view()
def detect_bank_pattern(self, row):
    if len(row) < 4:
        return None
    # HSBC Credit
    if (is_date(str(row[3])) and pd.api.types.is_number(row[2]) and isinstance(row[1], str) and pd.isna(row[0])):
        return "HSBC Credit"
    # HSBC Debit
    if (is_date(str(row[3])) and pd.api.types.is_number(row[2]) and isinstance(row[1], str) and pd.api.types.is_number(row[0])):
        return "HSBC Debit"
    # MetroBank Credit (assuming date in col[0], number col[1], string col[2])
    if (is_date(str(row[0])) and pd.api.types.is_number(row[1]) and isinstance(row[2], str)):
        return "MetroBank Credit"
    # MetroBank Debit (assuming date col[0], number col[1], string col[2], number balance col[3])
    if (is_date(str(row[0])) and pd.api.types.is_number(row[1]) and isinstance(row[2], str) and pd.api.types.is_number(row[3])):
        return "MetroBank Debit"
    
    return None
def process_metrobank_credit(self, row, line_hash):
    record = {
        "Record": len(self.database_df) + 1,
        "Date Purchased": row[0],
        "Figure": row[1],
        "Description": row[2],
        "Type": "CreditCard",
        "ID": line_hash,
        "BANK": "MetroBank"
    }
    self.database_df = self.database_df.append(record, ignore_index=True)

def process_metrobank_debit(self, row, line_hash):
    date_purchased = extract_date_from_description(row[2])
    record = {
        "Record": len(self.database_df) + 1,
        "Date Committed": row[0],
        "Figure": row[1],
        "Description": row[2],
        "Balance": row[3],
        "Date Purchased": date_purchased,
        "Type": "DebitCard",
        "ID": line_hash,
        "BANK": "MetroBank"
    }
    self.database_df = self.database_df.append(record, ignore_index=True)

def process_hsbc_credit(self, row, line_hash):
    record = {
        "Record": len(self.database_df) + 1,
        "Date Purchased": row[3],
        "Figure": row[2],
        "Description": row[1],
        "Type": "CreditCard",
        "ID": line_hash,
        "BANK": "HSBC"
    }
    self.database_df = self.database_df.append(record, ignore_index=True)

def process_hsbc_debit(self, row, line_hash):
    date_purchased = extract_date_from_description(row[1])
    record = {
        "Record": len(self.database_df) + 1,
        "Balance": row[0],
        "Description": row[1],
        "Figure": row[2],
        "Date Committed": row[3],
        "Date Purchased": date_purchased,
        "Type": "DebitCard",
        "ID": line_hash,
        "BANK": "HSBC"
    }
    self.database_df = self.database_df.append(record, ignore_index=True)
def is_date(string):
    try:
        datetime.datetime.strptime(string, '%Y-%m-%d')  # adjust date format if needed
        return True
    except ValueError:
        return False

def extract_date_from_description(description):
    # Assuming description contains a date in 'YYYY-MM-DD' format.
    import re
    match = re.search(r'\d{4}-\d{2}-\d{2}', description)
    if match:
        return match.group(0)
    return ''

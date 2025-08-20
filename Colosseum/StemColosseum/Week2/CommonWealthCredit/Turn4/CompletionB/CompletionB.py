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
        print(f"Row {index}: {row_list}")

        if self.is_commonwealth_credit(row_list):
            self.process_commonwealth_credit(row_list)
        elif self.is_commonwealth_debit(row_list):
            self.process_commonwealth_debit(row_list)
        elif self.is_nab_credit(row_list):
            self.process_nab_credit(row_list)
        elif self.is_nab_debit(row_list):
            self.process_nab_debit(row_list)
        else:
            print(f"Row {index} does not match any expected pattern. Skipping this row.")

    self.refresh_tree_view()
    print("File processing completed.")


### Pattern Detection Functions


def detect_bank_pattern(self, row):
    if self.is_commonwealth_credit(row):
        return "CommonWealth Credit"
    elif self.is_commonwealth_debit(row):
        return "CommonWealth Debit"
    elif self.is_nab_credit(row):
        return "NAB Credit"
    elif self.is_nab_debit(row):
        return "NAB Debit"
    return None

def is_commonwealth_credit(self, row):
    return len(row) > 3 and "CommonWealth Credit" in row

def is_commonwealth_debit(self, row):
    return len(row) > 3 and "CommonWealth Debit" in row

def is_nab_credit(self, row):
    return len(row) > 3 and "NAB Credit" in row

def is_nab_debit(self, row):
    return len(row) > 3 and "NAB Debit" in row


### Processing Functions


def process_commonwealth_credit(self, row):
    record_id = hashlib.md5(str(row).encode()).hexdigest()
    if record_id in self.database_df['ID'].values:
        print("Record exists. Skipping.")
        return

    new_record = {
        "Record": record_id,
        "Date Purchased": row[0],
        "Figure": row[1],
        "Description": row[2],
        "Type": "CreditCard",
        "ID": record_id,
        "BANK": "CommonWealth"
    }
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)

def process_commonwealth_debit(self, row):
    record_id = hashlib.md5(str(row).encode()).hexdigest()
    if record_id in self.database_df['ID'].values:
        print("Record exists. Skipping.")
        return

    new_record = {
        "Record": record_id,
        "Date Committed": row[0],
        "Figure": row[1],
        "Description": row[2],
        "Balance": row[3],
        "Date Purchased": self.extract_date_from_description(row[2]),
        "Type": "DebitCard",
        "ID": record_id,
        "BANK": "CommonWealth"
    }
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)

def process_nab_credit(self, row):
    record_id = hashlib.md5(str(row).encode()).hexdigest()
    if record_id in self.database_df['ID'].values:
        print("Record exists. Skipping.")
        return

    new_record = {
        "Record": record_id,
        "Date Purchased": row[3],
        "Figure": row[2],
        "Description": row[1],
        "Type": "CreditCard",
        "ID": record_id,
        "BANK": "NAB"
    }
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)

def process_nab_debit(self, row):
    record_id = hashlib.md5(str(row).encode()).hexdigest()
    if record_id in self.database_df['ID'].values:
        print("Record exists. Skipping.")
        return

    new_record = {
        "Record": record_id,
        "Balance": row[0],
        "Description": row[1],
        "Figure": row[2],
        "Date Committed": row[3],
        "Date Purchased": self.extract_date_from_description(row[1]),
        "Type": "DebitCard",
        "ID": record_id,
        "BANK": "NAB"
    }
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)


### Helper Function for Date Extraction


def extract_date_from_description(self, description):
    match = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', description)
    return match.group(0) if match else ""

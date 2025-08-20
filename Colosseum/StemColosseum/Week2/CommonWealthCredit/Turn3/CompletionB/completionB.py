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

        # Compute MD5 hash of the line
        line_string = ','.join(str(x) for x in row_list)
        line_hash = hashlib.md5(line_string.encode('utf-8')).hexdigest()

        # Check if line_hash exists in ID field
        if line_hash in self.database_df['ID'].values:
            print(f"Record with ID {line_hash} already exists. Skipping.")
            continue  # Skip to next record

        # Detect bank pattern
        bank_pattern = self.detect_bank_pattern(row_list)

        # Get next record number
        new_record_number = self.get_next_record_number()

        if bank_pattern == "CommonWealth Credit":
            print("Processing CommonWealth Credit record.")
            new_record = self.process_commonwealth_credit(row_list, line_hash, new_record_number)
            self.database_df = self.database_df.append(new_record, ignore_index=True)
        elif bank_pattern == "CommonWealth Debit":
            print("Processing CommonWealth Debit record.")
            new_record = self.process_commonwealth_debit(row_list, line_hash, new_record_number)
            self.database_df = self.database_df.append(new_record, ignore_index=True)
        elif bank_pattern == "NAB Credit":
            print("Processing NAB Credit record.")
            new_record = self.process_nab_credit(row_list, line_hash, new_record_number)
            self.database_df = self.database_df.append(new_record, ignore_index=True)
        elif bank_pattern == "NAB Debit":
            print("Processing NAB Debit record.")
            new_record = self.process_nab_debit(row_list, line_hash, new_record_number)
            self.database_df = self.database_df.append(new_record, ignore_index=True)
        else:
            print(f"Row {index} does not match any expected pattern. Skipping.")

    # Save the database back to the CSV
    self.database_df.to_csv(self.database_filename, index=False)
    self.refresh_tree_view()

    print("File processing completed.")

def get_next_record_number(self):
    if self.database_df.empty:
        return 1
    else:
        return self.database_df['Record'].max() + 1


def process_commonwealth_credit(self, row_list, line_hash, new_record_number):
    new_record = {
        "Record": new_record_number,
        "Date Purchased": row_list[0],
        "Date Committed": "",
        "Figure": row_list[1],
        "Description": row_list[2],
        "Balance": "",
        "Category": "",
        "Sub-Category": "",
        "ID": line_hash,
        "BANK": "CommonWealth",
        "Type": "CreditCard",
        "Comments": ""
    }
    return new_record


def process_commonwealth_debit(self, row_list, line_hash, new_record_number):
    # Extract date from Description (Column 3)
    description = row_list[2]
    date_purchased = self.extract_date_from_string(description)

    new_record = {
        "Record": new_record_number,
        "Date Purchased": date_purchased,
        "Date Committed": row_list[0],
        "Figure": row_list[1],
        "Description": description,
        "Balance": row_list[3],
        "Category": "",
        "Sub-Category": "",
        "ID": line_hash,
        "BANK": "CommonWealth",
        "Type": "DebitCard",
        "Comments": ""
    }
    return new_record


def process_nab_credit(self, row_list, line_hash, new_record_number):
    new_record = {
        "Record": new_record_number,
        "Date Purchased": row_list[3],
        "Date Committed": "",
        "Figure": row_list[2],
        "Description": row_list[1],
        "Balance": "",
        "Category": "",
        "Sub-Category": "",
        "ID": line_hash,
        "BANK": "NAB",
        "Type": "CreditCard",
        "Comments": ""
    }
    return new_record
def process_nab_debit(self, row_list, line_hash, new_record_number):
    # Extract date from Description (Column 2)
    description = row_list[1]
    date_purchased = self.extract_date_from_string(description)

    new_record = {
        "Record": new_record_number,
        "Date Purchased": date_purchased,
        "Date Committed": row_list[3],
        "Figure": row_list[2],
        "Description": description,
        "Balance": row_list[0],
        "Category": "",
        "Sub-Category": "",
        "ID": line_hash,
        "BANK": "NAB",
        "Type": "DebitCard",
        "Comments": ""
    }
    return new_record
def detect_bank_pattern(self, row_list):
    if len(row_list) < 3:
        return None

    # Check for CommonWealth Credit
    if self.is_date(row_list[0]) and self.is_number(row_list[1]) and isinstance(row_list[2], str):
        return "CommonWealth Credit"
    # Check for CommonWealth Debit
    elif len(row_list) >= 4 and self.is_date(row_list[0]) and self.is_number(row_list[1]) and isinstance(row_list[2], str) and self.is_number(row_list[3]):
        return "CommonWealth Debit"
    # Check for NAB Credit
    elif len(row_list) >= 4 and self.is_date(row_list[3]) and self.is_number(row_list[2]) and isinstance(row_list[1], str):
        return "NAB Credit"
    # Check for NAB Debit
    elif len(row_list) >= 4 and self.is_number(row_list[0]) and isinstance(row_list[1], str) and self.is_number(row_list[2]) and self.is_date(row_list[3]):
        return "NAB Debit"
    else:
        return None
def is_date(self, string):
    from dateutil.parser import parse
    try:
        parse(str(string), dayfirst=True)
        return True
    except (ValueError, TypeError):
        return False

def is_number(self, value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
def extract_date_from_string(self, text):
    import re
    date_regex = r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"
    match = re.search(date_regex, text)
    if match:
        return match.group(0)
    else:
        return ''

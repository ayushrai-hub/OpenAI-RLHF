import pandas as pd
import regex as re
def generate_md5_hash_of_record(self, row):
        record_string = ''.join([str(item) for item in row])
        return hashlib.md5(record_string.encode()).hexdigest()
def record_exists(self, record_hash):
        return self.database_df['ID'].str.contains(record_hash).any()

def add_new_record(self, new_record):
        self.database_df = self.database_df.append(new_record, ignore_index=True)
        self.save_database_to_file()


def save_database_to_file(self):
        self.database_df.to_csv(self.database_filename, index=False)
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

        # Process each row
        for index, row in input_df.iterrows():
            row_list = row.tolist()
            print(f"Processing Row {index}: {row_list}")

            record_hash = self.generate_md5_hash_of_record(row_list)
            if self.record_exists(record_hash):
                print("Record already exists. Skipping.")
                continue

            bank_pattern = self.detect_bank_pattern(row_list)
            if bank_pattern == "CommonWealth Credit":
                self.process_commonwealth_credit(row_list, record_hash)
            elif bank_pattern == "CommonWealth Debit":
                self.process_commonwealth_debit(row_list, record_hash)
            elif bank_pattern == "NAB Credit":
                self.process_nab_credit(row_list, record_hash)
            elif bank_pattern == "NAB Debit":
                self.process_nab_debit(row_list, record_hash)
            else:
                print(f"Row {index} does not match any expected pattern. Skipping.")


def process_commonwealth_credit(self, row, record_id):
        new_record = {
            "Record": self.get_next_record_number(),
            "Date Purchased": row[0],
            "Figure": row[1],
            "Description": row[2],
            "Balance": "",
            "Category": "",
            "Sub-Category": "",
            "ID": record_id,
            "BANK": "CommonWealth",
            "Type": "CreditCard"
        }
        self.add_new_record(new_record)

def process_commonwealth_debit(self, row, record_id):
        # Extract date from description (Column 3)
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
            "ID": record_id,
            "BANK": "CommonWealth",
            "Type": "DebitCard"
        }
        self.add_new_record(new_record)
    

def extract_date_from_description(self, description):
        # Assuming dates in the description are in DD/MM/YYYY format
        match = re.search(r"\d{2}/\d{2}/\d{4}", description)
        return match.group(0) if match else ""


def process_nab_credit(self, row, record_id):
        new_record = {
            "Record": self.get_next_record_number(),
            "Date Purchased": row[3],
            "Figure": row[2],
            "Description": row[1],
            "Balance": "",
            "Category": "",
            "Sub-Category": "",
            "ID": record_id,
            "BANK": "NAB",
            "Type": "CreditCard"
        }
        self.add_new_record(new_record)


def process_nab_debit(self, row, record_id):
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
            "ID": record_id,
            "BANK": "NAB",
            "Type": "DebitCard"
        }
        self.add_new_record(new_record)




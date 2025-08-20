import hashlib
import pandas as pd
import re

class Interface1(ttk.Frame):

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
            combined_row_str = " ".join(map(str, row_list))  # Combine row into a single string
            row_md5 = hashlib.md5(combined_row_str.encode('utf-8')).hexdigest()

            if row_md5 in self.database_df['ID'].values:
                continue  # Skip record if ID already exists

            bank_pattern = self.detect_bank_pattern(row_list)
            if bank_pattern == "CommonWealth Credit":
                self.process_commonwealth_credit(row_list, row_md5)
            elif bank_pattern == "CommonWealth Debit":
                self.process_commonwealth_debit(row_list, row_md5)
            elif bank_pattern == "NAB Credit":
                self.process_nab_credit(row_list, row_md5)
            elif bank_pattern == "NAB Debit":
                self.process_nab_debit(row_list, row_md5)

        self.database_df.to_csv(self.database_filename, index=False)
        self.refresh_tree_view()

    def process_commonwealth_credit(self, row, record_id):
        new_record = {
            "Record": self.get_next_record_number(),
            "Date Purchased": row[0],
            "Figure": row[1],
            "Description": row[2],
            "Type": "CreditCard",
            "ID": record_id,
            "BANK": "CommonWealth"
        }
        self.database_df = self.database_df.append(new_record, ignore_index=True)

    def process_commonwealth_debit(self, row, record_id):
        # Extract the "Date Purchased" from Column 3
        date_purchased = self.extract_date_from_string(row[2])

        new_record = {
            "Record": self.get_next_record_number(),
            "Date Commited": row[0],
            "Figure": row[1],
            "Description": row[2],
            "Balance": row[3],
            "Type": "DebitCard",
            "Date Purchased": date_purchased,
            "ID": record_id,
            "BANK": "CommonWealth"
        }
        self.database_df = self.database_df.append(new_record, ignore_index=True)

    def process_nab_credit(self, row, record_id):
        new_record = {
            "Record": self.get_next_record_number(),
            "Date Purchased": row[3],
            "Figure": row[2],
            "Description": row[1],
            "Type": "CreditCard",
            "ID": record_id,
            "BANK": "NAB"
        }
        self.database_df = self.database_df.append(new_record, ignore_index=True)

    def process_nab_debit(self, row, record_id):
        # Extract the "Date Purchased" from Column 2
        date_purchased = self.extract_date_from_string(row[1])

        new_record = {
            "Record": self.get_next_record_number(),
            "Balance": row[0],
            "Description": row[1],
            "Figure": row[2],
            "Date Commited": row[3],
            "Type": "DebitCard",
            "Date Purchased": date_purchased,
            "ID": record_id,
            "BANK": "NAB"
        }
        self.database_df = self.database_df.append(new_record, ignore_index=True)

    def extract_date_from_string(self, text):
        # Simple function to extract the first date found in a string
        match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        return match.group(1) if match else ""

    def get_next_record_number(self):
        return len(self.database_df) + 1
    
# Note: Ensure necessary imports like `re` above are present when binding this into your existing code.

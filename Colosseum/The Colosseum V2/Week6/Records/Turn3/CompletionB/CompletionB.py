def generate_md5_hash_of_line(self, line):
    line_str = ','.join(map(str, line))
    return hashlib.md5(line_str.encode()).hexdigest()
def load_records(self):
    filepath = filedialog.askopenfilename(
        title="Select a bank record file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )

    if not filepath:
        print("No file selected.")
        return

    try:
        input_df = pd.read_csv(filepath, header=None)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load the file: {e}")
        return

    for index, row in input_df.iterrows():
        row_list = row.tolist()
        
        bank_pattern = self.detect_bank_pattern(row_list)

        row_md5 = self.generate_md5_hash_of_line(row_list)

        if row_md5 in self.database_df["ID"].values:
            continue  # Duplicate found, skipping

        if bank_pattern == "MetroBank Credit":
            new_record = {
                "Record": row_md5,
                "Date Purchased": row_list[0],
                "Figure": row_list[1],
                "Description": row_list[2],
                "Type": "CreditCard",
                "ID": row_md5,
                "BANK": "MetroBank"
            }

        elif bank_pattern == "MetroBank Debit":
            date_purchased = self.extract_date_from_string(row_list[2])
            new_record = {
                "Record": row_md5,
                "Date Committed": row_list[0],
                "Figure": row_list[1],
                "Description": row_list[2],
                "Balance": row_list[3],
                "Date Purchased": date_purchased,
                "Type": "DebitCard",
                "ID": row_md5,
                "BANK": "MetroBank"
            }

        elif bank_pattern == "HSBC Credit":
            new_record = {
                "Record": row_md5,
                "Date Purchased": row_list[3],
                "Figure": row_list[2],
                "Description": row_list[1],
                "Type": "CreditCard",
                "ID": row_md5,
                "BANK": "HSBC"
            }

        elif bank_pattern == "HSBC Debit":
            date_purchased = self.extract_date_from_string(row_list[1])
            new_record = {
                "Record": row_md5,
                "Balance": row_list[0],
                "Description": row_list[1],
                "Figure": row_list[2],
                "Date Committed": row_list[3],
                "Date Purchased": date_purchased,
                "Type": "DebitCard",
                "ID": row_md5,
                "BANK": "HSBC"
            }

        else:
            print(f"Row {index} unrecognized pattern. Skipping.")
            continue

        self.database_df = pd.concat([self.database_df, pd.DataFrame([new_record])], ignore_index=True)

    self.database_df.to_csv(self.database_filename, index=False)
    self.refresh_tree_view()
def detect_bank_pattern(self, row):
    if len(row) >= 4:
        if is_date(row[0]) and is_float(row[1]) and isinstance(row[2], str) and pd.isna(row[3]):
            return "MetroBank Credit"
        elif is_date(row[0]) and is_float(row[1]) and isinstance(row[2], str) and is_float(row[3]):
            return "MetroBank Debit"
        elif pd.isna(row[0]) and isinstance(row[1], str) and is_float(row[2]) and is_date(row[3]):
            return "HSBC Credit"
        elif is_float(row[0]) and isinstance(row[1], str) and is_float(row[2]) and is_date(row[3]):
            return "HSBC Debit"
    return None
def is_date(string):
    try:
        pd.to_datetime(string)
        return True
    except:
        return False

def is_float(val):
    try:
        float(val)
        return True
    except:
        return False

def extract_date_from_string(self, text):
    dates_found = pd.to_datetime(text, errors='coerce')
    if pd.isna(dates_found):
        return ""
    return dates_found.strftime('%Y-%m-%d')

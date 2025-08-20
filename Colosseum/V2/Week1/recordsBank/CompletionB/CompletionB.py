def process_bank_row(self, row, bank_pattern):
    # Create a string representation of the row for hashing
    row_str = ''.join([str(x) for x in row])
    row_hash = hashlib.md5(row_str.encode()).hexdigest()

    # Check if this record already exists
    if row_hash in self.database_df['ID'].values:
        print(f"Duplicate record found with hash: {row_hash}")
        return

    # Create a new record dictionary with default empty values
    new_record = {
        "Record": len(self.database_df) + 1,
        "Date Purchased": "",
        "Date Processed": "",
        "Amount": "",
        "Explanation": "",
        "Balance": "",
        "Category": "",
        "Sub-Category": "",
        "ID": row_hash,
        "BANK": "BankOne" if "BankOne" in bank_pattern else "BankTwo",
        "Type": "",
        "Comments": ""
    }

    if bank_pattern == "BankOne Credit":
        new_record.update({
            "Date Purchased": row[0],
            "Amount": row[1],
            "Explanation": row[2],
            "Type": "CreditCard"
        })

    elif bank_pattern == "BankOne Debit":
        new_record.update({
            "Date Processed": row[0],
            "Amount": row[1],
            "Explanation": row[2],
            "Balance": row[3],
            "Date Purchased": extract_date_from_string(row[2]),  # You'll need to implement this function
            "Type": "DebitCard"
        })

    elif bank_pattern == "BankTwo Credit":
        new_record.update({
            "Date Purchased": row[3],
            "Amount": row[2],
            "Explanation": row[1],
            "Type": "CreditCard"
        })

    elif bank_pattern == "BankTwo Debit":
        new_record.update({
            "Balance": row[0],
            "Explanation": row[1],
            "Amount": row[2],
            "Date Processed": row[3],
            "Date Purchased": extract_date_from_string(row[1]),  # You'll need to implement this function
            "Type": "DebitCard"
        })

    # Add the new record to the database
    self.database_df = pd.concat([self.database_df, pd.DataFrame([new_record])], ignore_index=True)
    
    # Save the updated database
    self.database_df.to_csv(self.database_filename, index=False)
    
    # Refresh the treeview
    self.refresh_tree_view()

def extract_date_from_string(text):
    """
    Helper function to extract date from explanation string
    You'll need to implement the logic based on your specific date format
    """
    # This is a placeholder - implement according to your date format
    try:
        # Add your date extraction logic here
        return ""  # Return extracted date
    except:
        return ""

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
        print(f"Processing row {index}: {row_list}")

        bank_pattern = self.detect_bank_pattern(row_list)
        if bank_pattern:
            self.process_bank_row(row_list, bank_pattern)
        else:
            print(f"Row {index} does not match any expected pattern.")

    print("File processing completed.")

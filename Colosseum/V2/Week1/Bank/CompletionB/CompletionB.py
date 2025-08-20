def process_record(self, row, bank_type):
    # Create a string representation of the row for MD5 hashing
    row_string = ''.join(map(str, row))
    row_hash = hashlib.md5(row_string.encode()).hexdigest()
    
    # Check if this record already exists
    if row_hash in self.database_df['ID'].values:
        print(f"Record with hash {row_hash} already exists. Skipping...")
        return

    new_record = {}
    
    if bank_type == "MetroBank Credit":
        new_record = {
            'ID': row_hash,
            'Record': len(self.database_df) + 1,
            'Date Purchased': row[0],
            'Figure': row[1],
            'Description': row[2],
            'Type': 'CreditCard',
            'BANK': 'MetroBank'
        }
    
    elif bank_type == "MetroBank Debit":
        purchase_date = self.extract_date_from_description(row[2])
        new_record = {
            'ID': row_hash,
            'Record': len(self.database_df) + 1,
            'Date Committed': row[0],
            'Date Purchased': purchase_date,
            'Figure': row[1],
            'Description': row[2],
            'Balance': row[3],
            'Type': 'DebitCard',
            'BANK': 'MetroBank'
        }
    
    elif bank_type == "HSBC Credit":
        new_record = {
            'ID': row_hash,
            'Record': len(self.database_df) + 1,
            'Date Purchased': row[3],
            'Figure': row[2],
            'Description': row[1],
            'Type': 'CreditCard',
            'BANK': 'HSBC'
        }
    
    elif bank_type == "HSBC Debit":
        purchase_date = self.extract_date_from_description(row[1])
        new_record = {
            'ID': row_hash,
            'Record': len(self.database_df) + 1,
            'Balance': row[0],
            'Description': row[1],
            'Figure': row[2],
            'Date Committed': row[3],
            'Date Purchased': purchase_date,
            'Type': 'DebitCard',
            'BANK': 'HSBC'
        }

    # Add the new record to the database
    self.database_df = pd.concat([self.database_df, pd.DataFrame([new_record])], ignore_index=True)
    self.save_database()
    self.refresh_tree_view()

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
        
        # Detect bank type from filename or content pattern
        bank_type = self.detect_bank_type(filepath, input_df)
        
        for index, row in input_df.iterrows():
            self.process_record(row, bank_type)
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process the file: {e}")
        return

def detect_bank_type(self, filepath, df):
    # This is a placeholder - you'll need to implement the actual logic
    # to detect the bank type based on your specific requirements
    filename = os.path.basename(filepath).lower()
    if "hsbc" in filename:
        if self.is_credit_format(df):
            return "HSBC Credit"
        return "HSBC Debit"
    elif "metrobank" in filename:
        if self.is_credit_format(df):
            return "MetroBank Credit"
        return "MetroBank Debit"
    return None

def extract_date_from_description(self, description):
    # Implement your date extraction logic here
    # This is just a placeholder
    try:
        # Add your date extraction logic
        return None
    except:
        return None

def save_database(self):
    self.database_df.to_csv(self.database_filename, index=False)

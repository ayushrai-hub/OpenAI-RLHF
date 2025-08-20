def is_date(date_string):
    """Check if a string can be parsed as a date."""
    try:
        # Try multiple date formats
        for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y']:
            try:
                datetime.datetime.strptime(date_string, fmt)
                return True
            except ValueError:
                continue
        return False
    except Exception:
        return False

def extract_date_from_explanation(explanation):
    """Extract date from explanation text if available."""
    try:
        # Look for common date patterns in the explanation
        import re
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})', str(explanation))
        if date_match:
            date_str = date_match.group(0)
            # Try to convert to a standard format
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%m/%d/%y']:
                try:
                    date_obj = datetime.datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%m/%d/%Y')
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error extracting date: {e}")
    return ""

def detect_bank_pattern(self, row):
    """Detect which bank and transaction type the row belongs to."""
    # Ensure row has enough columns
    if len(row) < 4:
        return None
    
    # Check for BankOne Credit pattern
    if (is_date(str(row[0])) and 
        pd.api.types.is_number(row[1]) and 
        isinstance(row[2], str)):
        return "BankOne Credit"
    
    # Check for BankOne Debit pattern
    elif (is_date(str(row[0])) and 
          pd.api.types.is_number(row[1]) and 
          isinstance(row[2], str) and 
          pd.api.types.is_number(row[3])):
        return "BankOne Debit"
    
    # Check for BankTwo Credit pattern
    elif (is_date(str(row[3])) and 
          pd.api.types.is_number(row[2]) and 
          isinstance(row[1], str) and 
          pd.isna(row[0])):
        return "BankTwo Credit"
    
    # Check for BankTwo Debit pattern
    elif (is_date(str(row[3])) and 
          pd.api.types.is_number(row[2]) and 
          isinstance(row[1], str) and 
          pd.api.types.is_number(row[0])):
        return "BankTwo Debit"
    
    return None

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

    records_processed = 0
    duplicates_found = 0

    for index, row in input_df.iterrows():
        row_list = row.tolist()
        print(f"Processing row {index}: {row_list}")

        # Process the row and get result
        result = self.process_bank_row(row_list)
        if result == "duplicate":
            duplicates_found += 1
        elif result == "processed":
            records_processed += 1

    # Save database after processing all rows
    self.database_df.to_csv(self.database_filename, index=False)
    self.refresh_tree_view()
    
    messagebox.showinfo("Processing Complete", 
                        f"File processed successfully.\n"
                        f"New records: {records_processed}\n"
                        f"Duplicates skipped: {duplicates_found}")

def process_bank_row(self, row):
    """Process a row based on its detected bank pattern."""
    pattern = self.detect_bank_pattern(row)
    
    if not pattern:
        print(f"Row does not match any expected pattern: {row}")
        return "no_pattern"
    
    # Create a MD5 hash of the row as a unique identifier
    row_hash = hashlib.md5(str(row).encode()).hexdigest()
    
    # Check if this hash already exists in our database
    if row_hash in self.database_df['ID'].values:
        print(f"Duplicate record found with ID: {row_hash}")
        return "duplicate"
    
    # Create a new record based on the pattern
    new_record = {}
    new_record['ID'] = row_hash
    new_record['BANK'] = "BankOne" if pattern.startswith("BankOne") else "BankTwo"
    
    if pattern == "BankOne Credit":
        new_record['Type'] = "CreditCard"
        new_record['Date Purchased'] = row[0]
        new_record['Amount'] = row[1]
        new_record['Explanation'] = row[2]
        new_record['Record'] = len(self.database_df) + 1
    
    elif pattern == "BankOne Debit":
        new_record['Type'] = "DebitCard"
        new_record['Date Processed'] = row[0]
        new_record['Amount'] = row[1]
        new_record['Explanation'] = row[2]
        new_record['Balance'] = row[3]
        new_record['Date Purchased'] = extract_date_from_explanation(row[2])
        new_record['Record'] = len(self.database_df) + 1
    
    elif pattern == "BankTwo Credit":
        new_record['Type'] = "CreditCard"
        new_record['Date Purchased'] = row[3]
        new_record['Amount'] = row[2]
        new_record['Explanation'] = row[1]
        new_record['Record'] = len(self.database_df) + 1
    
    elif pattern == "BankTwo Debit":
        new_record['Type'] = "DebitCard"
        new_record['Balance'] = row[0]
        new_record['Explanation'] = row[1]
        new_record['Amount'] = row[2]
        new_record['Date Processed'] = row[3]
        new_record['Date Purchased'] = extract_date_from_explanation(row[1])
        new_record['Record'] = len(self.database_df) + 1
    
    # Add the new record to the database
    self.database_df = self.database_df.append(new_record, ignore_index=True)
    print(f"Added new record: {new_record}")
    return "processed"

def refresh_tree_view(self):
    """Refresh the treeview to display current database."""
    # Clear existing items
    for item in self.tree.get_children():
        self.tree.delete(item)
    
    # Add rows from the database
    for idx, row in self.database_df.iterrows():
        values = [
            row.get('Record', ''),
            row.get('Date Purchased', ''),
            row.get('Date Processed', ''),
            row.get('Amount', ''),
            row.get('Explanation', ''),
            row.get('Balance', ''),
            row.get('Category', ''),
            row.get('Sub-Category', ''),
            row.get('Comments', '')
        ]
        self.tree.insert('', 'end', values=values)

def update_icon_state_based_on_selection(self, event):
    """Update the icon based on selected record's type."""
    selected_items = self.tree.selection()
    if not selected_items:
        self.icon_label.configure(image='')
        return
    
    # Get the selected item's ID (which is the first column)
    item_id = selected_items[0]
    record_id = self.tree.item(item_id, 'values')[0]
    
    # Find the type of this record in the database
    try:
        record_type = self.database_df.loc[self.database_df['Record'] == int(record_id), 'Type'].values[0]
        if record_type == "CreditCard":
            self.icon_label.configure(image=self.icon_credit)
        elif record_type == "DebitCard":
            self.icon_label.configure(image=self.icon_debit)
        else:
            self.icon_label.configure(image='')
    except (IndexError, ValueError):
        self.icon_label.configure(image='')

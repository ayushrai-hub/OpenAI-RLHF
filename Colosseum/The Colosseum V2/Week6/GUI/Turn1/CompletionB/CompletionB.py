
def is_date(self, string):
    try:
        datetime.datetime.strptime(string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def detect_bank_pattern(self, row):
    if len(row) < 4:
        return None

    c1, c2, c3, c4 = row[0], row[1], row[2], row[3]

    if self.is_date(str(c1)) and isinstance(c2, (int, float)) and isinstance(c3, str) and pd.isna(c4):
        return "BankOne Credit"
    if self.is_date(str(c1)) and isinstance(c2, (int, float)) and isinstance(c3, str) and isinstance(c4, (int, float)):
        return "BankOne Debit"
    if pd.isna(c1) and isinstance(c2, str) and isinstance(c3, (int, float)) and self.is_date(str(c4)):
        return "BankTwo Credit"
    if isinstance(c1, (int, float)) and isinstance(c2, str) and isinstance(c3, (int, float)) and self.is_date(str(c4)):
        return "BankTwo Debit"
    return None

def hash_row(self, row):
    row_str = '|'.join([str(cell) for cell in row])
    return hashlib.md5(row_str.encode()).hexdigest()

def process_bank_row(self, row):
    pattern = self.detect_bank_pattern(row)
    row_hash = self.hash_row(row)

    if row_hash in self.database_df['ID'].values:
        print(f"Duplicate record found: {row}")
        return

    if pattern == "BankOne Credit":
        new_record = {
            "Record": len(self.database_df) + 1,
            "Date Purchased": row[0],
            "Date Processed": "",
            "Amount": row[1],
            "Explanation": row[2],
            "Balance": "",
            "Category": "",
            "Sub-Category": "",
            "Comments": "",
            "ID": row_hash,
            "BANK": "BankOne",
            "Type": "CreditCard"
        }

    elif pattern == "BankOne Debit":
        date_part = row[2].split()[0] if row[2] else ""
        new_record = {
            "Record": len(self.database_df) + 1,
            "Date Purchased": date_part,
            "Date Processed": row[0],
            "Amount": row[1],
            "Explanation": row[2],
            "Balance": row[3],
            "Category": "",
            "Sub-Category": "",
            "Comments": "",
            "ID": row_hash,
            "BANK": "BankOne",
            "Type": "DebitCard"
        }

    elif pattern == "BankTwo Credit":
        new_record = {
            "Record": len(self.database_df) + 1,
            "Date Purchased": row[3],
            "Date Processed": "",
            "Amount": row[2],
            "Explanation": row[1],
            "Balance": "",
            "Category": "",
            "Sub-Category": "",
            "Comments": "",
            "ID": row_hash,
            "BANK": "BankTwo",
            "Type": "CreditCard"
        }

    elif pattern == "BankTwo Debit":
        date_part = row[1].split()[0] if row[1] else ""
        new_record = {
            "Record": len(self.database_df) + 1,
            "Date Purchased": date_part,
            "Date Processed": row[3],
            "Amount": row[2],
            "Explanation": row[1],
            "Balance": row[0],
            "Category": "",
            "Sub-Category": "",
            "Comments": "",
            "ID": row_hash,
            "BANK": "BankTwo",
            "Type": "DebitCard"
        }

    else:
        print(f"No matching bank pattern for row: {row}")
        return

    self.database_df = pd.concat([self.database_df, pd.DataFrame([new_record])], ignore_index=True)
    self.database_df.to_csv(self.database_filename, index=False)
    print(f"Processed and saved record: {new_record}")

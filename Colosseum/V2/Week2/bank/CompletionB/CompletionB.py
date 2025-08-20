import pandas as pd
# Changes in detect_bank_pattern method:
def detect_bank_pattern(self, row):
    if len(row) == 3:
        return "CommonWealth Credit"
    elif len(row) == 4:
        # Check NAB pattern first, fallback to CommonWealth otherwise
        if (is_date(str(row[3])) and
            pd.api.types.is_number(row[2]) and
            isinstance(row[1], str) and
            pd.isna(row[0])):
            return "NAB Credit"
        elif (is_date(str(row[3])) and
            pd.api.types.is_number(row[2]) and
            isinstance(row[1], str) and
            pd.api.types.is_number(row[0])):
            return "NAB Debit"
        else:
            return "CommonWealth Debit"
    else:
        return None
# Modify load_records method to handle the placeholders:
for index, row in input_df.iterrows():
    row_list = row.tolist()
    bank_pattern = self.detect_bank_pattern(row_list)

    if bank_pattern == "CommonWealth Credit":
        line_md5 = self.generate_md5_hash_of_line(row_list)
        if line_md5 in self.database_df['ID'].values:
            continue  # Skip if record exists
        else:
            # Create new CommonWealth Credit record
            record_id = line_md5
            record_number = self.get_next_record_number()
            new_record = {
                "Record": record_number,
                "Date Purchased": row_list[0],  # Column 1
                "Date Committed": "",
                "Figure": row_list[1],          # Column 2
                "Description": row_list[2],     # Column 3
                "Balance": "",
                "Category": "",
                "Sub-Category": "",
                "ID": record_id,
                "BANK": "CommonWealth",
                "Type": "CreditCard",
                "Comments": ""
            }
            self.database_df = self.database_df.append(new_record, ignore_index=True)
            self.database_df.to_csv(self.database_filename, index=False)

    elif bank_pattern == "CommonWealth Debit":
        line_md5 = self.generate_md5_hash_of_line(row_list)
        if line_md5 in self.database_df['ID'].values:
            continue  # Skip if record exists
        else:
            # Create new CommonWealth Debit record
            record_id = line_md5
            record_number = self.get_next_record_number()
            description = row_list[2]
            date_purchased = self.extract_date_from_description(description) or ""
            new_record = {
                "Record": record_number,
                "Date Purchased": date_purchased, # Date extracted from Description
                "Date Committed": row_list[0],    # Column 1
                "Figure": row_list[1],            # Column 2
                "Description": description,       # Column 3
                "Balance": row_list[3],           # Column 4
                "Category": "",
                "Sub-Category": "",
                "ID": record_id,
                "BANK": "CommonWealth",
                "Type": "DebitCard",
                "Comments": ""
            }
            self.database_df = self.database_df.append(new_record, ignore_index=True)
            self.database_df.to_csv(self.database_filename, index=False)

    elif bank_pattern == "NAB Credit":
        line_md5 = self.generate_md5_hash_of_line(row_list)
        if line_md5 in self.database_df['ID'].values:
            continue  # Skip if record exists
        else:
            # Create new NAB Credit record
            record_id = line_md5
            record_number = self.get_next_record_number()
            new_record = {
                "Record": record_number,
                "Date Purchased": row_list[3],     # Column 4
                "Date Committed": "",
                "Figure": row_list[2],             # Column 3
                "Description": row_list[1],        # Column 2
                "Balance": "",
                "Category": "",
                "Sub-Category": "",
                "ID": record_id,
                "BANK": "NAB",
                "Type": "CreditCard",
                "Comments": ""
            }
            self.database_df = self.database_df.append(new_record, ignore_index=True)
            self.database_df.to_csv(self.database_filename, index=False)

    elif bank_pattern == "NAB Debit":
        line_md5 = self.generate_md5_hash_of_line(row_list)
        if line_md5 in self.database_df['ID'].values:
            continue  # Skip if record exists
        else:
            # Create new NAB Debit record
            record_id = line_md5
            record_number = self.get_next_record_number()
            description = row_list[1]
            date_purchased = self.extract_date_from_description(description) or ""
            new_record = {
                "Record": record_number,
                "Date Purchased": date_purchased,  # Date extracted from Description
                "Date Committed": row_list[3],     # Column 4
                "Figure": row_list[2],             # Column 3
                "Description": description,        # Column 2
                "Balance": row_list[0],            # Column 1
                "Category": "",
                "Sub-Category": "",
                "ID": record_id,
                "BANK": "NAB",
                "Type": "DebitCard",
                "Comments": ""
            }
            self.database_df = self.database_df.append(new_record, ignore_index=True)
            self.database_df.to_csv(self.database_filename, index=False)
    else:
        print(f"No recognized bank pattern for row {index}. Skipping.")

# Additional methods added or updated:
def generate_md5_hash_of_line(self, line):
    line_str = ",".join(str(x) for x in line)
    return hashlib.md5(line_str.encode('utf-8')).hexdigest()

def get_next_record_number(self):
    if self.database_df.empty:
        return 1
    else:
        return self.database_df['Record'].max() + 1

def extract_date_from_description(self, description):
    pattern = re.compile(r"(\d{2}/\d{2}/\d{4})")
    match = pattern.search(description)
    if match:
        return match.group(1)
    return None


import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
import tkinter as tk
from tkinter import messagebox, filedialog, PhotoImage
import pandas as pd
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import hashlib
import os, datetime

class Interface1(ttk.Frame):
    def __init__(self, master=None):  # Fixed syntax error from 'init' to '__init__'
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()

    # ... (Other methods like create_widgets, initialize_or_load_database, etc., remain unchanged)

    def load_records(self):
        filepath = filedialog.askopenfilename(
            title="Select a bank record file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))  # Fixed filetypes syntax
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

        for index, row in input_df.iterrows():
            row_list = row.tolist()
            print(f"Row {index}: {row_list}")

            bank_pattern = self.detect_bank_pattern(row_list)
            if bank_pattern == "MetroBank Credit":
                print("Credit MetroBank routine triggered.")
                line_str = ','.join(map(str, row_list))
                line_hash = hashlib.md5(line_str.encode()).hexdigest()
                
                if line_hash in self.database_df['ID'].values:
                    print(f"Row {index} already exists with ID {line_hash}. Skipping.")
                    continue
                
                new_record = {
                    'ID': line_hash,
                    'Record': line_str,
                    'Date Purchased': row[0],
                    'Figure': row[1],
                    'Description': row[2],
                    'Type': 'CreditCard',
                    'BANK': 'MetroBank Credit',
                    'Date Committed': '',
                    'Balance': '',
                    'Category': '',
                    'Sub-Category': '',
                    'Comments': ''
                }
                self.database_df = pd.concat([self.database_df, pd.DataFrame([new_record])], ignore_index=True)

            elif bank_pattern == "MetroBank Debit":
                print("Debit MetroBank routine triggered.")
                line_str = ','.join(map(str, row_list))
                line_hash = hashlib.md5(line_str.encode()).hexdigest()
                
                if line_hash in self.database_df['ID'].values:
                    print(f"Row {index} already exists with ID {line_hash}. Skipping.")
                    continue
                
                # Derive Date Purchased from Column 3 (Description) - assuming it contains a date string
                derived_date = self.extract_date_from_description(row[2]) if isinstance(row[2], str) else ''
                
                new_record = {
                    'ID': line_hash,
                    'Record': line_str,
                    'Date Committed': row[0],
                    'Figure': row[1],
                    'Description': row[2],
                    'Balance': row[3],
                    'Date Purchased': derived_date,
                    'Type': 'DebitCard',
                    'BANK': 'MetroBank Debit',
                    'Category': '',
                    'Sub-Category': '',
                    'Comments': ''
                }
                self.database_df = pd.concat([self.database_df, pd.DataFrame([new_record])], ignore_index=True)

            elif bank_pattern == "HSBC Credit":
                print("Credit HSBC routine triggered.")
                line_str = ','.join(map(str, row_list))
                line_hash = hashlib.md5(line_str.encode()).hexdigest()
                
                if line_hash in self.database_df['ID'].values:
                    print(f"Row {index} already exists with ID {line_hash}. Skipping.")
                    continue
                
                new_record = {
                    'ID': line_hash,
                    'Record': line_str,
                    'Date Purchased': row[3],
                    'Figure': row[2],
                    'Description': row[1],
                    'Type': 'CreditCard',
                    'BANK': 'HSBC Credit',
                    'Date Committed': '',
                    'Balance': '',
                    'Category': '',
                    'Sub-Category': '',
                    'Comments': ''
                }
                self.database_df = pd.concat([self.database_df, pd.DataFrame([new_record])], ignore_index=True)

            elif bank_pattern == "HSBC Debit":
                print("Debit HSBC routine triggered.")
                line_str = ','.join(map(str, row_list))
                line_hash = hashlib.md5(line_str.encode()).hexdigest()
                
                if line_hash in self.database_df['ID'].values:
                    print(f"Row {index} already exists with ID {line_hash}. Skipping.")
                    continue
                
                # Derive Date Purchased from Column 2 (Description) - assuming it contains a date string
                derived_date = self.extract_date_from_description(row[1]) if isinstance(row[1], str) else ''
                
                new_record = {
                    'ID': line_hash,
                    'Record': line_str,
                    'Balance': row[0],
                    'Description': row[1],
                    'Figure': row[2],
                    'Date Committed': row[3],
                    'Date Purchased': derived_date,
                    'Type': 'DebitCard',
                    'BANK': 'HSBC Debit',
                    'Category': '',
                    'Sub-Category': '',
                    'Comments': ''
                }
                self.database_df = pd.concat([self.database_df, pd.DataFrame([new_record])], ignore_index=True)

            else:
                print(f"Row {index} does not match any expected pattern. File is invalid or does not contain recognized bank data.")

        self.database_df.to_csv(self.database_filename, index=False)
        self.refresh_tree_view()
        print("File processing completed.")

    def extract_date_from_description(self, description):
        # Helper method to extract a date from a description string (customize as needed)
        # This is a placeholder; you’d need to define how dates are embedded in descriptions
        try:
            # Example: Assuming format like "Payment on 2023-01-15"
            for part in description.split():
                if is_date(part):
                    return part
            return ''
        except Exception:
            return ''

    def detect_bank_pattern(self, row):
        # Ensure row has at least 4 columns
        if len(row) < 4:
            return None

        # Debugging prints
        print(f"Date check for {row[3]}: {is_date(str(row[3]))}")
        print(f"Number check for {row[2]}: {pd.api.types.is_number(row[2])}")
        print(f"String check for {row[1]}: {isinstance(row[1], str)}")
        print(f"Blank check for {row[0]}: {pd.isna(row[0])}")

        # Check for HSBC patterns (as provided in original code)
        if (is_date(str(row[3])) and pd.api.types.is_number(row[2]) and isinstance(row[1], str) and pd.isna(row[0])):
            return "HSBC Credit"
        elif (is_date(str(row[3])) and pd.api.types.is_number(row[2]) and isinstance(row[1], str) and pd.api.types.is_number(row[0])):
            return "HSBC Debit"

        # Add MetroBank patterns (customized based on your logic)
        if (is_date(str(row[0])) and pd.api.types.is_number(row[1]) and isinstance(row[2], str)):
            return "MetroBank Credit"
        elif (is_date(str(row[0])) and pd.api.types.is_number(row[1]) and isinstance(row[2], str) and pd.api.types.is_number(row[3])):
            return "MetroBank Debit"

        return None

    # Placeholder for is_date helper function (since it wasn’t provided in your code)
    def is_date(self, string):
        try:
            datetime.datetime.strptime(string, '%Y-%m-%d')  # Adjust format as per your data
            return True
        except ValueError:
            return False

    # ... (Other methods like treeview_sort_column, refresh_tree_view, etc., remain unchanged)

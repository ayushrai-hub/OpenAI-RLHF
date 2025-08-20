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

# Helper function to check if a string can be interpreted as a date.
def is_date(s):
    try:
        pd.to_datetime(s)
        return True
    except Exception:
        return False

class Interface1(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.style = Style("litera")

        # Load icons
        self.icon_debit = PhotoImage(file='./lib/icon_debit.png')
        self.icon_credit = PhotoImage(file='./lib/icon_credit.png')

        self.tree_style = ttk.Style()
        self.tree_style.configure("Treeview.Heading", font=("Calibri", 8, "bold"))
        self.tree_style.configure("Treeview", rowheight=17)
        self.tree_style.map("Treeview", background=[("selected", "#2574D3")], foreground=[("selected", "white")])
        self.tree_style.configure("Treeview", background="#F3F3F3", fieldbackground="#F3F3F3")

        load_button = ttk.Button(self, text="Load Bank Records", bootstyle=INFO, command=self.load_records)
        load_button.pack(fill=X, padx=10, pady=10)

        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X, padx=10, pady=2)

        input_frame = ttk.Frame(self)
        input_frame.pack(fill=X, padx=10, pady=10)
        ttk.Label(input_frame, bootstyle="secondary", text="🔍").pack(side=LEFT, padx=5)
        ttk.Entry(input_frame).pack(side=LEFT, fill=X, expand=True, padx=5)
        ttk.Checkbutton(input_frame, text="Show Uncategorized Records Only").pack(side=LEFT, padx=5)

        # Label to display the icon
        self.icon_label = ttk.Label(input_frame)
        self.icon_label.pack(side=LEFT, padx=5)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Exclude ID, BANK, and TYPE from columns shown in the tree view
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Record", "Date Purchased", "Date Processed", "Amount", "Explanation", "Balance", "Category", "Sub-Category", "Comments"),
            show="headings",
            bootstyle=INFO
        )

        column_widths = [5, 10, 10, 7, 70, 7, 10, 10, 10]
        for col, width in zip(self.tree["columns"], column_widths):
            self.tree.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False))
            self.tree.column(col, width=width * 8, anchor=tk.CENTER)

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.update_icon_state_based_on_selection)

        # Load data (or create a new database)
        self.database_filename = "database.csv"
        self.initialize_or_load_database()

    def initialize_or_load_database(self):
        if os.path.exists(self.database_filename):
            self.database_df = pd.read_csv(self.database_filename).fillna('')
        else:
            self.database_df = pd.DataFrame(columns=[
                "Record", "Date Purchased", "Date Processed", "Amount", "Explanation", 
                "Balance", "Category", "Sub-Category", "ID", "BANK", "Type", "Comments"
            ])
            self.database_df.to_csv(self.database_filename, index=False)
            print("Database file not found. Created a new one.")

        if not self.database_df['ID'].is_unique:
            print("Warning: Duplicate IDs found in the DataFrame.")
        self.refresh_tree_view()

    def treeview_sort_column(self, treeview, col, reverse):
        l = [(treeview.set(k, col), k) for k in treeview.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            treeview.move(k, '', index)

        treeview.heading(col, command=lambda: self.treeview_sort_column(treeview, col, not reverse))

    def generate_md5_hash_of_file(self, filepath):
        with open(filepath, "rb") as file:
            file_content = file.read()
        return hashlib.md5(file_content).hexdigest()

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

        # You might want to also use the file hash for logging if needed.
        file_hash = self.generate_md5_hash_of_file(filepath)
        print(f"MD5 hash of file: {file_hash}")

        for index, row in input_df.iterrows():
            row_list = row.tolist()
            print(f"Row {index}: {row_list}")
            pattern = self.detect_bank_pattern(row_list)
            if not pattern:
                print(f"Row {index} does not match any expected pattern. Skipping.")
                continue

            self.process_bank_row(row_list, pattern)

        # Save database after processing
        self.database_df.to_csv(self.database_filename, index=False)
        print("File processing completed.")
        self.refresh_tree_view()

    def detect_bank_pattern(self, row):
        """
        Returns one of the following strings based on the record structure:
         - "BankOne Credit" : Three-column records
         - "BankOne Debit"  : Four-column records where Column 1 is a date (or can be parsed as one)
         - "BankTwo Credit" : Four-column records where Column 1 is blank/NaN, Column 2 is text, Column 3 is numeric and Column 4 is a date
         - "BankTwo Debit"  : Four-column records where Column 1 is numeric (balance), Column 2 is text (and contains a date), Column 3 is numeric and Column 4 is a date
        """
        # For safety, ensure row is a list
        if not isinstance(row, list):
            row = list(row)
        col_count = len(row)

        if col_count == 3:
            # Assume BankOne Credit
            return "BankOne Credit"
        elif col_count == 4:
            # Test for BankOne Debit: if first column looks like a date
            if is_date(str(row[0])):
                return "BankOne Debit"
            else:
                # Test for BankTwo Credit: first column should be NaN/empty and last column is a date
                if (pd.isna(row[0]) or str(row[0]).strip() == "") and isinstance(row[1], str) and (isinstance(row[2], (int, float)) or pd.api.types.is_numeric_dtype(type(row[2]))) and is_date(str(row[3])):
                    return "BankTwo Credit"
                # Test for BankTwo Debit: first column numeric, second text and containing a date, third numeric, fourth date.
                if (isinstance(row[0], (int, float)) or pd.api.types.is_numeric_dtype(type(row[0]))) and isinstance(row[1], str) and (isinstance(row[2], (int, float)) or pd.api.types.is_numeric_dtype(type(row[2]))) and is_date(str(row[3])):
                    return "BankTwo Debit"
        return None

    def process_bank_row(self, row, pattern):
        """
        Process the row based on the detected bank pattern.
        First check if the record (by md5 hash of its row) is already processed.
        If not, create a new record in the database with fields mapped per the specification.
        """
        # Compute a hash of the row (using its string representation)
        row_str = "|".join(str(item) for item in row)
        row_hash = hashlib.md5(row_str.encode('utf-8')).hexdigest()

        # If hash already exists in the database, skip processing this row.
        if row_hash in self.database_df['ID'].values:
            print("Duplicate record detected. Skipping.")
            return

        # Create an empty new record (dictionary) with all expected fields.
        new_record = {
            "Record": "",            # You can set a sequential record id or similar here.
            "Date Purchased": "",
            "Date Processed": "",
            "Amount": "",
            "Explanation": "",
            "Balance": "",
            "Category": "",
            "Sub-Category": "",
            "ID": row_hash,
            "BANK": "",
            "Type": "",
            "Comments": ""
        }

        # Process according to the pattern.
        if pattern == "BankOne Credit":
            # BankOne Credit:
            #   Column 1 -> Date Purchased
            #   Column 2 -> Amount
            #   Column 3 -> Explanation
            #   Type = "CreditCard"
            new_record["Date Purchased"] = row[0]
            new_record["Amount"] = row[1]
            new_record["Explanation"] = row[2]
            new_record["Type"] = "CreditCard"
            new_record["BANK"] = "BankOne"

        elif pattern == "BankOne Debit":
            # BankOne Debit:
            #   Column 1 -> Date Processed
            #   Column 2 -> Amount
            #   Column 3 -> Explanation
            #   Column 4 -> Balance
            #   Extract date part from Column 3 and put in Date Purchased
            new_record["Date Processed"] = row[0]
            new_record["Amount"] = row[1]
            new_record["Explanation"] = row[2]
            new_record["Balance"] = row[3]
            # Assuming that the explanation field contains a date portion at the beginning,
            # we try to extract it. For example, if Explanation starts with a date string:
            try:
                dt = pd.to_datetime(str(row[2]), errors='coerce')
                if pd.notnull(dt):
                    new_record["Date Purchased"] = dt.strftime("%Y-%m-%d")
            except Exception:
                new_record["Date Purchased"] = ""
            new_record["Type"] = "DebitCard"
            new_record["BANK"] = "BankOne"

        elif pattern == "BankTwo Credit":
            # BankTwo Credit:
            #   Column 4 -> Date Purchased
            #   Column 3 -> Amount
            #   Column 2 -> Explanation
            #   Type = "CreditCard"
            new_record["Date Purchased"] = row[3]
            new_record["Amount"] = row[2]
            new_record["Explanation"] = row[1]
            new_record["Type"] = "CreditCard"
            new_record["BANK"] = "BankTwo"

        elif pattern == "BankTwo Debit":
            # BankTwo Debit:
            #   Column 1 -> Balance
            #   Column 2 -> Explanation
            #   Column 3 -> Amount
            #   Column 4 -> Date Processed
            #   Extract date part from Column 2 and put in Date Purchased
            new_record["Balance"] = row[0]
            new_record["Explanation"] = row[1]
            new_record["Amount"] = row[2]
            new_record["Date Processed"] = row[3]
            # Try to extract a date from the Explanation field (Column 2).
            try:
                # For example, assume the explanation begins with a date
                dt = pd.to_datetime(row[1].split()[0], errors='coerce')
                if pd.notnull(dt):
                    new_record["Date Purchased"] = dt.strftime("%Y-%m-%d")
            except Exception:
                new_record["Date Purchased"] = ""
            new_record["Type"] = "DebitCard"
            new_record["BANK"] = "BankTwo"

        else:
            print("Unexpected bank pattern. Skipping record.")
            return

        # Optionally, assign a new sequential record number or other unique identifier.
        new_record["Record"] = str(len(self.database_df) + 1)

        # Append the new record to the DataFrame.
        self.database_df = self.database_df.append(new_record, ignore_index=True)
        print(f"Processed new record with hash {row_hash} for pattern {pattern}.")

    def refresh_tree_view(self):
        # Clear current tree contents
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Insert rows from the DataFrame
        for index, row in self.database_df.iterrows():
            self.tree.insert("", "end", values=(
                row["Record"],
                row["Date Purchased"],
                row["Date Processed"],
                row["Amount"],
                row["Explanation"],
                row["Balance"],
                row["Category"],
                row["Sub-Category"],
                row["Comments"]
            ))

    def update_icon_state_based_on_selection(self, event):
        # Placeholder: update the icon based on the selected record’s Type
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        # For example, if Type is DebitCard, show debit icon; else, show credit icon.
        # (Here you might look up the record in self.database_df to decide.)
        # This is just a placeholder implementation.
        record_index = int(item["values"][0]) - 1  # Assuming record number starts at 1
        record_type = self.database_df.iloc[record_index]["Type"]
        if record_type == "DebitCard":
            self.icon_label.configure(image=self.icon_debit)
        else:
            self.icon_label.configure(image=self.icon_credit)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bank Records Manager")
    app = Interface1(master=root)
    app.mainloop()

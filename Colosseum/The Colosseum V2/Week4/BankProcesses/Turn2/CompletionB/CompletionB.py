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
import os
import datetime

class Interface1(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Set up the style (in this example, using "litera" style)
        self.style = Style("litera")

        # Load icons
        self.icon_debit = PhotoImage(file='./lib/icon_debit.png')
        self.icon_credit = PhotoImage(file='./lib/icon_credit.png')

        # Configure the Treeview style
        self.tree_style = ttk.Style()
        self.tree_style.configure("Treeview.Heading", font=("Calibri", 8, "bold"))
        self.tree_style.configure("Treeview", rowheight=17)
        self.tree_style.map("Treeview", background=[("selected", "#2574D3")], foreground=[("selected", "white")])
        self.tree_style.configure("Treeview", background="#F3F3F3", fieldbackground="#F3F3F3")

        # Load Bank Records button
        load_button = ttk.Button(self, text="Load Bank Records", bootstyle=INFO, command=self.load_records)
        load_button.pack(fill=X, padx=10, pady=10)

        # Separator
        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X, padx=10, pady=2)

        # Input frame (for any filters or additional settings)
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=X, padx=10, pady=10)
        ttk.Label(input_frame, bootstyle="secondary", text="🔍").pack(side=LEFT, padx=5)
        ttk.Entry(input_frame).pack(side=LEFT, fill=X, expand=True, padx=5)
        ttk.Checkbutton(input_frame, text="Show Uncategorized Records Only").pack(side=LEFT, padx=5)

        # Icon label (optional, for UI)
        self.icon_label = ttk.Label(input_frame)
        self.icon_label.pack(side=LEFT, padx=5)

        # Treeframe for displaying records
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Create Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Record", "Date Purchased", "Date Processed", "Amount", "Explanation", "Balance", "Category", "Sub-Category", "ID", "BANK", "Type", "Comments"),
            show="headings",
            bootstyle=INFO
        )

        # Set column headings and widths
        column_widths = [5, 10, 10, 7, 70, 7, 10, 10, 10, 12, 12, 10]
        for col, width in zip(self.tree["columns"], column_widths):
            self.tree.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False))
            self.tree.column(col, width=width * 8, anchor=tk.CENTER)

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.update_icon_state_based_on_selection)

        # Load data from CSV
        self.database_filename = "database.csv"
        self.initialize_or_load_database()

    def initialize_or_load_database(self):
        """ Load the existing CSV database if present, otherwise create a new one. """
        if os.path.exists(self.database_filename):
            self.database_df = pd.read_csv(self.database_filename).fillna('')
        else:
            # Create a new DataFrame with the necessary columns
            self.database_df = pd.DataFrame(columns=[
                "Record", "Date Purchased", "Date Processed", "Amount", "Explanation",
                "Balance", "Category", "Sub-Category", "ID", "BANK", "Type", "Comments"
            ])
            self.database_df.to_csv(self.database_filename, index=False)
            print("Database file not found. Created a new one.")

        # Validate the 'ID' field is unique if needed
        if not self.database_df['ID'].is_unique:
            print("Warning: Duplicate IDs found in the DataFrame.")

        self.refresh_tree_view()

    def refresh_tree_view(self):
        """ Refresh the treeview to show the latest data. """
        # Clear the existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert data from the database
        for _, row in self.database_df.iterrows():
            self.tree.insert("", "end", values=(
                row["Record"],
                row["Date Purchased"],
                row["Date Processed"],
                row["Amount"],
                row["Explanation"],
                row["Balance"],
                row["Category"],
                row["Sub-Category"],
                row["ID"],
                row["BANK"],
                row["Type"],
                row["Comments"]
            ))

    def treeview_sort_column(self, treeview, col, reverse):
        """ Sort treeview columns when the heading is clicked. """
        l = [(treeview.set(k, col), k) for k in treeview.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            treeview.move(k, '', index)

        treeview.heading(col, command=lambda: self.treeview_sort_column(treeview, col, not reverse))

    def update_icon_state_based_on_selection(self, event):
        """ Update the icon label or other UI elements based on selection. """
        # (Insert logic if needed)
        pass

    def load_records(self):
        """ Handle the 'Load Bank Records' button: open file dialog, read CSV, process each row. """
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

        # For demonstration, simply process each row with our bank logic
        for index, row in input_df.iterrows():
            self.process_bank_row(row)

        # Refresh the Treeview to show processed data
        self.refresh_tree_view()
        print("File processing completed.")

    def process_bank_row(self, row):
        """ Determine bank pattern and process the row accordingly. """
        pattern = self.detect_bank_pattern(row)
        if pattern == "BankOne Credit":
            self._process_bank_one_credit(row)
        elif pattern == "BankOne Debit":
            self._process_bank_one_debit(row)
        elif pattern == "BankTwo Credit":
            self._process_bank_two_credit(row)
        elif pattern == "BankTwo Debit":
            self._process_bank_two_debit(row)
        else:
            print("Unrecognized bank pattern or insufficient data. Row skipped.")

    def detect_bank_pattern(self, row):
        """
        Detect which bank pattern the row matches.

        This is a simplified example. Adapt the logic to match your actual CSV structure and
        the rules for each bank.
        """
        if len(row) < 4:
            return None

        # Example checks (use your own criteria)
        date3 = self._is_date(str(row[3]))
        num2 = self._is_number(row[2])
        str1 = isinstance(row[1], str)
        na0 = pd.isna(row[0])
        num0 = self._is_number(row[0])

        # BankTwo Credit/ Debit (as in your snippet)
        if date3 and num2 and str1 and na0:
            return "BankTwo Credit"
        elif date3 and num2 and str1 and num0:
            return "BankTwo Debit"

        # BankOne might have a similar pattern. For illustration:
        # (Adjust the conditions as needed for your CSV layout.)
        if na0 and date3 and num2 and str1:
            return "BankOne Credit"
        elif num0 and date3 and num2 and str1:
            return "BankOne Debit"

        return None

    def _process_bank_one_credit(self, row):
        """
        BankOne Credit logic:
          1) Execute the MD5 hash on the row and verify if it exists in the ID field.
          2) If yes, skip. If no, create a new record.
          3) Copy column1 to Date Purchased, column2 to Amount, column3 to Explanation.
          4) Set 'Type' = 'CreditCard'.
        """
        row_str = "".join(str(x) for x in row)
        file_hash = hashlib.md5(row_str.encode()).hexdigest()

        if file_hash in self.database_df["ID"].values:
            return  # Already processed

        new_record = {
            "Record": "New record",
            "Date Purchased": row[0],
            "Amount": row[1],
            "Explanation": row[2],
            "Type": "CreditCard",
            "ID": file_hash
        }

        self.database_df = self.database_df.append(new_record, ignore_index=True)
        self.database_df.to_csv(self.database_filename, index=False)

    def _process_bank_one_debit(self, row):
        """
        BankOne Debit logic:
          1) Execute the MD5 hash on the row and verify if it exists in the ID field.
          2) If yes, skip. If no, create a new record.
          3) Copy column1 to Date Processed, column2 to Amount, column3 to Explanation, column4 to Balance.
          4) Copy the date part of column3 to Date Purchased.
          5) Set 'Type' = 'DebitCard'.
        """
        row_str = "".join(str(x) for x in row)
        file_hash = hashlib.md5(row_str.encode()).hexdigest()

        if file_hash in self.database_df["ID"].values:
            return  # Already processed

        date_processed = row[0]
        amount = row[1]
        explanation = row[2]
        balance = row[3]
        # Extract the date part from column 3 if applicable
        date_purchased = self._extract_date_part(row[2])

        new_record = {
            "Record": "New record",
            "Date Processed": date_processed,
            "Amount": amount,
            "Explanation": explanation,
            "Balance": balance,
            "Date Purchased": date_purchased,
            "Type": "DebitCard",
            "ID": file_hash
        }

        self.database_df = self.database_df.append(new_record, ignore_index=True)
        self.database_df.to_csv(self.database_filename, index=False)

    def _process_bank_two_credit(self, row):
        """
        BankTwo Credit logic:
          1) Execute the MD5 hash on the row and verify if it exists in the ID field.
          2) If yes, skip. If no, create a new record.
          3) Copy column4 -> Date Purchased, column3 -> Amount, column2 -> Explanation.
          4) Set 'Type' = 'CreditCard'.
        """
        row_str = "".join(str(x) for x in row)
        file_hash = hashlib.md5(row_str.encode()).hexdigest()

        if file_hash in self.database_df["ID"].values:
            return  # Already processed

        new_record = {
            "Record": "New record",
            "Date Purchased": row[3],
            "Amount": row[2],
            "Explanation": row[1],
            "Type": "CreditCard",
            "ID": file_hash
        }

        self.database_df = self.database_df.append(new_record, ignore_index=True)
        self.database_df.to_csv(self.database_filename, index=False)

    def _process_bank_two_debit(self, row):
        """
        BankTwo Debit logic:
          1) Execute the MD5 hash on the row and verify if it exists in the ID field.
          2) If yes, skip. If no, create a new record.
          3) Copy column1 -> Balance, column2 -> Explanation, column3 -> Amount, column4 -> Date Processed.
          4) Copy the date part of column2 to Date Purchased.
          5) Set 'Type' = 'DebitCard'.
        """
        row_str = "".join(str(x) for x in row)
        file_hash = hashlib.md5(row_str.encode()).hexdigest()

        if file_hash in self.database_df["ID"].values:
            return  # Already processed

        balance = row[0]
        explanation = row[1]
        amount = row[2]
        date_processed = row[3]
        date_purchased = self._extract_date_part(row[1])

        new_record = {
            "Record": "New record",
            "Balance": balance,
            "Explanation": explanation,
            "Amount": amount,
            "Date Processed": date_processed,
            "Date Purchased": date_purchased,
            "Type": "DebitCard",
            "ID": file_hash
        }

        self.database_df = self.database_df.append(new_record, ignore_index=True)
        self.database_df.to_csv(self.database_filename, index=False)

    def _extract_date_part(self, value):
        """
        Extract the date portion (YYYY-MM-DD) from a datetime string, if present.
        For example, '2023-03-15 12:34:56' -> '2023-03-15'.
        """
        try:
            dt = datetime.datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            # Fall back to returning the original if parsing fails
            return str(value)

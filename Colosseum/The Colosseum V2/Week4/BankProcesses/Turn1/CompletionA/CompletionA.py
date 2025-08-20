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
        self.database_filename = "database.csv"
        self.initialize_or_load_database()

    def create_widgets(self):
        self.style = Style("litera")
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
        self.icon_label = ttk.Label(input_frame)
        self.icon_label.pack(side=LEFT, padx=5)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
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

    def initialize_or_load_database(self):
        default_columns = [
            "Record", "Date Purchased", "Date Processed", "Amount", "Explanation",
            "Balance", "Category", "Sub-Category", "ID", "BANK", "Type", "Comments"
        ]
        if os.path.exists(self.database_filename):
            self.database_df = pd.read_csv(self.database_filename).fillna('')
            for col in default_columns:
                if col not in self.database_df.columns:
                    self.database_df[col] = ''
        else:
            self.database_df = pd.DataFrame(columns=default_columns)
            self.database_df.to_csv(self.database_filename, index=False)
        self.refresh_tree_view()

    def treeview_sort_column(self, treeview, col, reverse):
        l = [(treeview.set(k, col), k) for k in treeview.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            treeview.move(k, '', index)
        treeview.heading(col, command=lambda: self.treeview_sort_column(treeview, col, not reverse))

    def generate_md5_hash_of_file(self, filepath):
        with open(filepath, "rb") as file:
            return hashlib.md5(file.read()).hexdigest()

    def update_icon_state_based_on_selection(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0], 'values')
            transaction_type = item_values[9] if len(item_values) > 9 else ''
            if transaction_type == 'DebitCard':
                self.icon_label.config(image=self.icon_debit)
            elif transaction_type == 'CreditCard':
                self.icon_label.config(image=self.icon_credit)
            else:
                self.icon_label.config(image='')

    def refresh_tree_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        visible_columns = ["Record", "Date Purchased", "Date Processed", "Amount", "Explanation", "Balance", "Category", "Sub-Category", "Comments"]
        for index, row in self.database_df.iterrows():
            values = [row[col] if not pd.isna(row[col]) else '' for col in visible_columns]
            self.tree.insert('', 'end', values=values)

    def detect_bank_pattern(self, row):
        row_length = len(row)
        if row_length >= 4:
            col3_date = self.is_date(str(row[3]))
            col2_num = pd.api.types.is_number(row[2])
            col1_str = isinstance(row[1], str)
            col0 = row[0]
            if pd.isna(col0) or col0 == '':
                col0_empty = True
            else:
                col0_empty = False
            if col3_date and col2_num and col1_str and col0_empty:
                return "BankTwo Credit"
            elif col3_date and col2_num and col1_str and pd.api.types.is_number(col0):
                return "BankTwo Debit"
        if row_length >= 3:
            col0_date = self.is_date(str(row[0]))
            col1_num = pd.api.types.is_number(row[1])
            col2_str = isinstance(row[2], str)
            if col0_date and col1_num and col2_str:
                return "BankOne Credit"
        if row_length >= 4:
            col0_date = self.is_date(str(row[0]))
            col1_num = pd.api.types.is_number(row[1])
            col2_str = isinstance(row[2], str)
            col3_num = pd.api.types.is_number(row[3])
            if col0_date and col1_num and col2_str and col3_num:
                return "BankOne Debit"
        return None

    def is_date(self, s):
        try:
            pd.to_datetime(s)
            return True
        except:
            return False

    def process_bank_row(self, row, line_md5, bank_pattern):
        new_record = {
            'ID': line_md5, 'BANK': bank_pattern.split()[0],
            'Type': 'CreditCard' if 'Credit' in bank_pattern else 'DebitCard',
            'Record': '', 'Date Purchased': '', 'Date Processed': '', 'Amount': '',
            'Explanation': '', 'Balance': '', 'Category': '', 'Sub-Category': '', 'Comments': ''
        }
        try:
            if bank_pattern == "BankOne Credit":
                new_record.update({
                    'Date Purchased': row[0],
                    'Amount': row[1],
                    'Explanation': row[2]
                })
            elif bank_pattern == "BankOne Debit":
                date_part = str(row[2]).split()[0] if isinstance(row[2], str) else ''
                new_record.update({
                    'Date Processed': row[0],
                    'Amount': row[1],
                    'Explanation': row[2],
                    'Balance': row[3],
                    'Date Purchased': date_part if self.is_date(date_part) else ''
                })
            elif bank_pattern == "BankTwo Credit":
                new_record.update({
                    'Date Purchased': row[3],
                    'Amount': row[2],
                    'Explanation': row[1]
                })
            elif bank_pattern == "BankTwo Debit":
                date_part = str(row[1]).split()[0] if isinstance(row[1], str) else ''
                new_record.update({
                    'Balance': row[0],
                    'Explanation': row[1],
                    'Amount': row[2],
                    'Date Processed': row[3],
                    'Date Purchased': date_part if self.is_date(date_part) else ''
                })
            return new_record
        except IndexError:
            return None

    def load_records(self):
        filepath = filedialog.askopenfilename(filetypes=(("CSV files", "*.csv"),))
        if not filepath:
            return
        try:
            input_df = pd.read_csv(filepath).fillna('')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            return

        existing_ids = self.database_df['ID'].tolist() if 'ID' in self.database_df.columns else []
        new_records = []

        for _, row in input_df.iterrows():
            row_list = row.fillna('').tolist()
            line_str = ','.join(map(str, row_list))
            line_md5 = hashlib.md5(line_str.encode('utf-8')).hexdigest()
            if line_md5 in existing_ids:
                continue
            bank_pattern = self.detect_bank_pattern(row_list)
            if not bank_pattern:
                continue
            new_record = self.process_bank_row(row_list, line_md5, bank_pattern)
            if new_record:
                new_records.append(new_record)

        if new_records:
            new_df = pd.DataFrame(new_records)
            self.database_df = pd.concat([self.database_df, new_df], ignore_index=True, sort=False)
            self.database_df.to_csv(self.database_filename, index=False)
            self.refresh_tree_view()

if __name__ == "__main__":
    root = ttk.Window()
    Interface1(root)
    root.mainloop()

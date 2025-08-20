import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from tkinter import messagebox
from datetime import datetime

class MyApp(tk.Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.title("Financial Transactions Viewer")
        self.geometry("1300x600")
        self.flat_categories = []

        self.style = ttk.Style()
        self.style.theme_use("clam")

        classic_bg = "#F5F5F5"
        btn_bg = "#D3D3D3"
        btn_fg = "maroon"
        treeview_bg = "#FFFFFF"
        treeview_field_bg = "#F5F5F5"
        selected_bg = "#C0C0C0"

        self.style.configure("Treeview", background=treeview_bg, foreground="black",
                             rowheight=25, fieldbackground=treeview_field_bg)
        self.style.map("Treeview", background=[('selected', selected_bg)])
        self.style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'), background=classic_bg)
        self.style.configure("TButton", font=('Calibri', 10, 'bold'), background=btn_bg, foreground=btn_fg)
        self.style.configure("TCombobox", fieldbackground=treeview_field_bg, background="white")

        self.shared_widgets = []
        self.data_widgets = []
        self.graph_widgets = []

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Shared widgets (visible in both views)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)

        load_button = ttk.Button(button_frame, text="Import Transaction Records", command=self.load_records, style="TButton")
        load_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        show_graph_button = ttk.Button(button_frame, text="Show Graph", command=self.show_graph, style="TButton")
        show_graph_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', padx=2, pady=2)

        # Store shared widgets for clarity
        self.shared_widgets.extend([load_button, show_graph_button, separator])

        # Data interface widgets (visible only in Data view)
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(pady=10, fill=tk.X)
        
        search_var = tk.StringVar()
        search_box = ttk.Entry(search_frame, textvariable=search_var, width=50)
        search_box.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        search_box.insert(0, "Search Transactions...")
        search_box.bind("<FocusIn>", lambda args: search_box.delete('0', 'end') if search_var.get() == "Search Transactions..." else None)
        search_box.bind("<FocusOut>", lambda args: search_box.insert(0, "Search Transactions...") if not search_var.get() else None)

        uncategorized_var = tk.BooleanVar()
        uncategorized_check = ttk.Checkbutton(search_frame, text="Uncategorized Only", variable=uncategorized_var)
        uncategorized_check.grid(row=0, column=1, sticky="w")

        self.tree = ttk.Treeview(main_frame, columns=("Transaction", "Purchase Date", "Post Date", "Amount", "Details", "Balance"), 
                                 show="headings", style="Treeview")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(main_frame, textvariable=self.category_var, style="TCombobox")
        self.category_combobox.pack(pady=2, fill=tk.X)
        self.category_combobox.bind('<KeyRelease>', self.filter_category_options)

        categorize_button = ttk.Button(main_frame, text="Assign Category", style="TButton")
        categorize_button.pack(pady=2, fill=tk.X)

        # Store Data interface widgets
        self.data_widgets.extend([
            search_frame, search_box, uncategorized_check, self.tree,
            self.category_combobox, categorize_button
        ])

        # Graph interface widgets (initially hidden, placeholder for actual graph widgets)
        self.graph_label = ttk.Label(main_frame, text="Graph will be displayed here", font=('Calibri', 16))
        self.graph_widgets.append(self.graph_label)

    def read_categories(self, filepath):
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            headers = df.columns.tolist()
            categories = {header: [] for header in headers}
            for index, row in df.iterrows():
                for header in headers:
                    item = row[header]
                    if pd.notnull(item):
                        categories[header].append(item)
            self.flat_categories = [f"{header} > {item}" for header, items in categories.items() for item in items]

    def filter_category_options(self, event=None):
        current_input = self.category_var.get().lower()
        filtered_options = [
            option for option in self.flat_categories if current_input in option.lower()
        ]
        self.category_combobox['values'] = filtered_options
        if current_input and filtered_options:
            self.category_combobox.event_generate('<Down>')

    def load_records(self):
        filepath = './database.csv'
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            self.tree.delete(*self.tree.get_children())
            if not df.empty and len(df.columns) >= 8:
                for _, row in df.iterrows():
                    self.tree.insert("", "end", values=(
                        row['Transaction'], row['Purchase Date'], row['Post Date'], 
                        row['Amount'], row['Details'], row['Balance']
                    ))
                messagebox.showinfo("Success", "Records loaded successfully.")
            else:
                messagebox.showwarning("Warning", "CSV is empty or incorrectly formatted.")
        else:
            messagebox.showerror("Error", "File not found.")

    def show_graph(self):
        # Hide Data interface widgets
        for widget in self.data_widgets:
            widget.pack_forget()

        # Display Graph interface widgets
        for widget in self.graph_widgets:
            widget.pack(pady=10, fill=tk.BOTH, expand=True)

        messagebox.showinfo("Information", "Switched to Graph view.")

def main():
    app = MyApp()
    app.read_categories('./categories.csv')
    app.mainloop()

if __name__ == "__main__":
    main()

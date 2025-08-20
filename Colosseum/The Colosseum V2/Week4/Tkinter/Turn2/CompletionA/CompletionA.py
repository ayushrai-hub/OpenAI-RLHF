import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from tkinter import messagebox
from datetime import datetime

class DataView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(pady=10, fill=tk.X)

        search_var = tk.StringVar()
        self.search_box = ttk.Entry(search_frame, textvariable=search_var, width=50)
        self.search_box.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_box.insert(0, "Search Transactions...")
        self.search_box.bind("<FocusIn>", lambda e: self.search_box.delete('0', 'end') if search_var.get() == "Search Transactions..." else None)
        self.search_box.bind("<FocusOut>", lambda e: self.search_box.insert(0, "Search Transactions...") if not search_var.get() else None)

        self.uncategorized_var = tk.BooleanVar()
        self.uncategorized_check = ttk.Checkbutton(search_frame, text="Uncategorized Only", variable=self.uncategorized_var)
        self.uncategorized_check.grid(row=0, column=1, sticky="w")

        self.tree = ttk.Treeview(self, columns=("Transaction", "Purchase Date", "Post Date", "Amount", "Details", "Balance"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self, textvariable=self.category_var)
        self.category_combobox.pack(pady=2, fill=tk.X)
        self.category_combobox.bind('<KeyRelease>', self.filter_category_options)

        self.categorize_button = ttk.Button(self, text="Assign Category")
        self.categorize_button.pack(pady=2, fill=tk.X)

    def filter_category_options(self, event=None):
        current_input = self.category_var.get().lower()
        filtered_options = []
        for option in self.app.flat_categories:
            try:
                _, sub_category = option.split(" > ", 1)
                if current_input in sub_category.lower():
                    filtered_options.append(option)
            except ValueError:
                continue
        self.category_combobox['values'] = filtered_options
        if current_input and filtered_options:
            self.category_combobox.event_generate('<Down>')

class GraphView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ttk.Label(self, text="Graph View (Functionality to be implemented)")
        self.label.pack(pady=20, expand=True)

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Financial Transactions Viewer")
        self.geometry("1300x600")
        self.flat_categories = []
        self.configure_styles()
        self.create_widgets()

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'), background="#F5F5F5")
        self.style.configure("TButton", font=('Calibri', 10, 'bold'), background="#D3D3D3", foreground="maroon")
        self.style.configure("TCombobox", fieldbackground="#F5F5F5", background="white")

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)

        ttk.Button(button_frame, text="Import Transaction Records", command=self.load_records).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(button_frame, text="Show Graph", command=self.show_graph).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=2)

        view_container = ttk.Frame(main_frame)
        view_container.pack(fill=tk.BOTH, expand=True)

        self.data_view = DataView(view_container, self)
        self.graph_view = GraphView(view_container)
        self.data_view.grid(row=0, column=0, sticky="nsew")
        self.graph_view.grid(row=0, column=0, sticky="nsew")
        self.graph_view.grid_remove()

    def read_categories(self, filepath):
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            self.flat_categories = [f"{header} > {item}" for header in df.columns for item in df[header].dropna()]

    def load_records(self):
        filepath = './database.csv'
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if not df.empty and len(df.columns) >= 8:
                self.data_view.tree.delete(*self.data_view.tree.get_children())
                for _, row in df.iterrows():
                    self.data_view.tree.insert("", "end", values=(row['Transaction'], row['Purchase Date'], row['Post Date'], row['Amount'], row['Details'], row['Balance']))
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                messagebox.showinfo("Information", f"File last saved: {mod_time}\nTotal records: {len(df)}\nUncategorized: {len(df[df['Entity'].isna()])}")
            else:
                messagebox.showwarning("Warning", "Invalid CSV format")
        else:
            messagebox.showerror("Error", "Database file not found")

    def show_graph(self):
        self.data_view.grid_remove()
        self.graph_view.grid()

def main():
    app = MyApp()
    app.read_categories('./categories.csv')
    app.mainloop()

if __name__ == "__main__":
    main()

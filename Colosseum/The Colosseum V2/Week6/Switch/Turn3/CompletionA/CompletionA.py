import tkinter as tk
from tkinter import ttk, messagebox
import os
import pandas as pd
from datetime import datetime

class MyApp(tk.Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.title("Financial Transactions Viewer")
        self.geometry("1300x600")
        self.flat_categories = []

        # Setup styles
        self.style_setup()
        
        # Create shared and view-specific widgets
        self.create_shared_widgets()
        self.create_data_view_widgets()
        self.create_graph_view_widgets()

        # Initially show data view
        self.show_data_view()

    def style_setup(self):
        classic_bg = "#F5F5F5"
        btn_bg = "#D3D3D3"
        btn_fg = "maroon"
        treeview_bg = "#FFFFFF"
        treeview_field_bg = "#F5F5F5"
        selected_bg = "#C0C0C0"

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("Treeview", background=treeview_bg, foreground="black",
                             rowheight=25, fieldbackground=treeview_field_bg)
        self.style.map("Treeview", background=[('selected', selected_bg)])

        self.style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'), background=classic_bg)
        self.style.configure("TButton", font=('Calibri', 10, 'bold'), background=btn_bg, foreground=btn_fg)
        self.style.configure("TCombobox", fieldbackground=treeview_field_bg, background="white")

    def create_shared_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10, fill=tk.X)

        self.load_button = ttk.Button(button_frame, text="Import Transaction Records", command=self.load_records)
        self.load_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.show_graph_button = ttk.Button(button_frame, text="Show Graph", command=self.toggle_view)
        self.show_graph_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Separator
        self.separator = ttk.Separator(self.main_frame, orient='horizontal')
        self.separator.pack(fill='x', padx=2, pady=2)

    def create_data_view_widgets(self):
        # Container for data-specific widgets
        self.data_frame = ttk.Frame(self.main_frame)

        # Search frame
        search_frame = ttk.Frame(self.data_frame)
        search_frame.pack(pady=10, fill=tk.X)

        self.search_var = tk.StringVar()
        self.search_box = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_box.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_box.insert(0, "Search Transactions...")
        self.search_box.bind("<FocusIn>", lambda e: self.search_box.delete(0, 'end') if self.search_var.get() == "Search Transactions..." else None)
        self.search_box.bind("<FocusOut>", lambda e: self.search_box.insert(0, "Search Transactions...") if not self.search_var.get() else None)

        self.uncategorized_var = tk.BooleanVar()
        self.uncategorized_check = ttk.Checkbutton(search_frame, text="Uncategorized Only", variable=self.uncategorized_var)
        self.uncategorized_check.grid(row=0, column=1, sticky="w")

        # Treeview for data
        self.tree = ttk.Treeview(self.data_frame, columns=("Transaction", "Purchase Date", "Post Date", "Amount", "Details", "Balance"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Category combobox
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.data_frame, textvariable=self.category_var)
        self.category_combobox.pack(pady=2, fill=tk.X)
        self.category_combobox.bind('<KeyRelease>', self.filter_category_options)

        # Categorize button
        self.categorize_button = ttk.Button(self.data_frame, text="Assign Category")
        self.categorize_button.pack(pady=2, fill=tk.X)

    def create_graph_view_widgets(self):
        # Container for graph view widgets
        self.graph_frame = ttk.Frame(self.main_frame)

        # Placeholder for graph view (to be implemented)
        graph_label = ttk.Label(
            self.graph_frame, text="Graph View Area\n(Implementation Placeholder)",
            font=('Calibri', 16), foreground="gray"
        )
        graph_label.pack(expand=True)

    def toggle_view(self):
        if self.data_frame.winfo_ismapped():
            self.show_graph_view()
        else:
            self.show_data_view()

    def show_data_view(self):
        self.graph_frame.pack_forget()
        self.data_frame.pack(fill=tk.BOTH, expand=True)
        self.show_graph_button.config(text="Show Graph")

    def show_graph_view(self):
        self.data_frame.pack_forget()
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        self.show_graph_button.config(text="Show Data")

    def read_categories(self, filepath):
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            headers = df.columns.tolist()
            categories = {header: [] for header in headers}
            for _, row in df.iterrows():
                for header in headers:
                    item = row[header]
                    if pd.notnull(item):
                        categories[header].append(item)
            self.flat_categories = [f"{header} > {item}" for header, items in categories.items() for item in items]

    def filter_category_options(self, event=None):
        current_input = self.category_var.get().lower()
        filtered_options = [
            option for option in self.flat_categories
            if current_input in option.split(" > ", 1)[-1].lower()
        ]
        self.category_combobox['values'] = filtered_options
        if current_input and filtered_options:
            self.category_combobox.event_generate('<Down>')

    def load_records(self):
        filepath = './database.csv'
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if not df.empty and len(df.columns) >= 8:
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                total_records = len(df)
                unassigned_records = len(df[df['Entity'].isnull()])
                self.tree.delete(*self.tree.get_children())  # Clear existing data
                for _, row in df.iterrows():
                    self.tree.insert("", "end", values=(
                        row['Transaction'], row['Purchase Date'], row['Post Date'],
                        row['Amount'], row['Details'], row['Balance']
                    ))
                messagebox.showinfo(
                    "Information",
                    f"The file was last saved on {mod_time} and contains {total_records} records, "
                    f"with {unassigned_records} uncategorized."
                )
            else:
                messagebox.showwarning("Warning", "The CSV file is either empty or lacks necessary columns.")
        else:
            messagebox.showerror("Error", "Database file could not be located.")

def main():
    app = MyApp()
    app.read_categories('./categories.csv')
    app.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from tkinter import messagebox
from datetime import datetime

class App(tk.Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.title("Modern Bank Records")
        self.geometry("1300x600")
        self.flat_categories = [] 

        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use a classic theme

        self.create_widgets()
        
    def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons Frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(pady=10, fill=tk.X)

        # Shared Widgets
        self.load_btn = ttk.Button(self.buttons_frame, text="Load Bank Records", command=self.load_records)
        self.load_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.show_chart_btn = ttk.Button(self.buttons_frame, text="Show Chart", command=self.show_plotting_interface)
        self.show_chart_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.menu_separator = ttk.Separator(self.main_frame, orient='horizontal')
        self.menu_separator.pack(fill='x', padx=2, pady=2)

        # --- Records Interface Widgets ---
        self.records_frame = ttk.Frame(self.main_frame)
        self.records_frame.pack(fill=tk.BOTH, expand=True)
  
        self.search_var = tk.StringVar()
        self.search_input = ttk.Entry(self.records_frame, textvariable=self.search_var, width=50)  
        self.search_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_input.insert(0, "Search Records...")
        self.search_input.bind("<FocusIn>", lambda args: self.search_input.delete(0, 'end') if self.search_var.get() == "Search Records..." else None)

        self.uncategorized_var = tk.BooleanVar()
        self.uncategorized_checkbox = ttk.Checkbutton(self.records_frame, text="Uncategorized Only", variable=self.uncategorized_var)
        self.uncategorized_checkbox.grid(row=0, column=1, sticky="w")

        self.tree = ttk.Treeview(self.records_frame, columns=("Record", "Date Purchased", "Date Committed", "Figure", "Description", "Balance"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.records_frame, textvariable=self.category_var)
        self.category_combobox.pack(pady=2, fill=tk.X)
        self.category_combobox.bind('<KeyRelease>', self.filter_category_options)

        self.categorize_btn = ttk.Button(self.records_frame, text="Categorize Record")
        self.categorize_btn.pack(pady=2, fill=tk.X)

        # --- Plotting Interface Widgets ---
        self.plotting_frame = ttk.Frame(self.main_frame)
        
        self.chart_label = ttk.Label(self.plotting_frame, text="Placeholder for Chart")
        self.chart_label.pack(pady=10)
    
    def filter_category_options(self, event=None):
        current_input = self.category_var.get().lower()
        filtered_options = [option for option in self.flat_categories if current_input in option.lower()]
        self.category_combobox['values'] = filtered_options
    
    def load_records(self):
        messagebox.showinfo("Info", "Load functionality to be implemented")

    def read_categories(self, filepath):
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            self.flat_categories = [f"{header} > {item}" for header in df.columns for item in df[header].dropna()]

    def show_records_interface(self):
        self.plotting_frame.pack_forget()
        self.records_frame.pack(fill=tk.BOTH, expand=True)
        self.show_chart_btn.config(command=self.show_plotting_interface)
    
    def show_plotting_interface(self):
        self.records_frame.pack_forget()
        self.plotting_frame.pack(fill=tk.BOTH, expand=True)
        self.show_chart_btn.config(command=self.show_records_interface)

def main():
    app = App()
    app.read_categories('./categories.csv')
    app.show_records_interface()
    app.mainloop()

if __name__ == "__main__":
    main()

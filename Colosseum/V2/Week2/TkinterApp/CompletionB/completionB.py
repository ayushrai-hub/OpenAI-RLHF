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

        # Classic and subtle colors
        classic_bg = "#F5F5F5"  # Soft light grey background for a classic look
        button_bg = "#D3D3D3"  # Grey for buttons, gives a more professional look
        button_fg = "maroon"  # button text color
        treeview_bg = "#FFFFFF"  # White background for the treeview
        treeview_field_bg = "#F5F5F5"  # Very light grey for fields, less harsh than pure white
        selected_bg = "#C0C0C0"  # Light grey for selected items, subtle selection color

        # Configure the style for the Treeview
        self.style.configure("Treeview", background=treeview_bg, foreground="black",
                             rowheight=25, fieldbackground=treeview_field_bg)
        self.style.map("Treeview", background=[('selected', selected_bg)])

        # Configure the style for the Treeview Heading
        self.style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'), background=classic_bg)

        # Configure the style for the Buttons
        self.style.configure("TButton", font=('Calibri', 10, 'bold'), background=button_bg, foreground=button_fg)

        # Configure the style for the Combobox
        self.style.configure("TCombobox", fieldbackground=treeview_field_bg, background="white")

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons frame (Shared elements)
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=10, fill=tk.X)

        # Shared Buttons
        self.load_btn = ttk.Button(buttons_frame, text="Load Bank Records", command=self.load_records, style="TButton")
        self.load_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.show_chart_btn = ttk.Button(buttons_frame, text="Show Chart", command=self.show_chart, style="TButton")
        self.show_chart_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Shared separator line
        self.menu_separator = ttk.Separator(main_frame, orient='horizontal')
        self.menu_separator.pack(fill='x', padx=2, pady=2)

        # **Records Interface Elements**
        self.records_ui(main_frame)
        
        # **Plotting Interface Elements** (Currently just a placeholder)
        self.plotting_frame = ttk.Frame(main_frame)

        # Placeholder plotting widget (just to demonstrate toggling)
        self.plotting_label = ttk.Label(self.plotting_frame, text="This is where the chart will be displayed.")
        self.plotting_label.pack(pady=20)

        # Initially show the Records interface
        self.show_records_interface()

    def records_ui(self, main_frame):
        # Frame for search input and checkbox
        self.search_frame = ttk.Frame(main_frame)
        self.search_frame.pack(pady=10, fill=tk.X)

        # Search box with placeholder
        search_var = tk.StringVar()
        self.search_input = ttk.Entry(self.search_frame, textvariable=search_var, width=50)  # Adjusted width
        self.search_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_input.insert(0, "Search Records...")
        self.search_input.bind("<FocusIn>", lambda args: self.search_input.delete('0', 'end') if search_var.get() == "Search Records..." else None)
        self.search_input.bind("<FocusOut>", lambda args: self.search_input.insert(0, "Search Records...") if not search_var.get() else None)

        # Checkbox for "Uncategorized Only"
        self.uncategorized_var = tk.BooleanVar()
        self.uncategorized_checkbox = ttk.Checkbutton(self.search_frame, text="Uncategorized Only", variable=self.uncategorized_var)
        self.uncategorized_checkbox.grid(row=0, column=1, sticky="w")

        # Treeview
        self.tree = ttk.Treeview(main_frame, columns=("Record", "Date Purchased", "Date Committed", "Figure", "Description", "Balance"), show="headings", style="Treeview")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Initialize the category dropdown box to work with filtering
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(main_frame, textvariable=self.category_var, style="TCombobox")
        self.category_combobox.pack(pady=2, fill=tk.X)
        self.category_combobox.bind('<KeyRelease>', self.filter_category_options)

        # Categorize Record Button
        self.categorize_btn = ttk.Button(main_frame, text="Categorize Record", style="TButton")
        self.categorize_btn.pack(pady=2, fill=tk.X)

    def show_records_interface(self):
        # Show records-related elements
        self.search_frame.pack(pady=10, fill=tk.X)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)
        self.category_combobox.pack(pady=2, fill=tk.X)
        self.categorize_btn.pack(pady=2, fill=tk.X)
        # Hide plotting frame
        self.plotting_frame.pack_forget()

    def show_plotting_interface(self):
        # Hide records-related elements
        self.search_frame.pack_forget()
        self.tree.pack_forget()
        self.category_combobox.pack_forget()
        self.categorize_btn.pack_forget()
        # Show plotting frame
        self.plotting_frame.pack(fill=tk.BOTH, expand=True)

    def load_records(self):
        filepath = './database.csv'
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if not df.empty and len(df.columns) >= 8:
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                total_records = len(df)
                unassigned_records = len(df[df['Entity'].isnull()])
                messagebox.showinfo("Info", f"The file you had been working on was last saved on {modified_time} and has {total_records} and {unassigned_records} (%) of Uncategorized records.")
                # Load records into the Treeview
                for _, row in df.iterrows():
                    self.tree.insert("", "end", values=(row['Record'], row['Date Purchased'], row['Date Committed'], row['Figure'], row['Description'], row['Balance']))
            else:
                messagebox.showwarning("Warning", "The CSV file is empty or does not contain the required columns.")
        else:
            messagebox.showerror("Error", "Database file not found.")

    def filter_category_options(self, event=None):
        current_input = self.category_var.get().lower()
        filtered_options = []
        for option in self.flat_categories:
            try:
                category, sub_category = option.split(" > ", 1)
            except ValueError:
                continue
            if current_input in sub_category.lower():
                filtered_options.append(option)
        self.category_combobox['values'] = filtered_options
        if current_input and filtered_options:
            self.category_combobox.event_generate('<Down>')

    def show_chart(self):
        # Placeholder for chart display functionality
        # Switch to the Plotting interface for now
        self.show_plotting_interface()

    def read_categories(self, filepath):
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            headers = df.columns.tolist()
            categories = {header: [] for header in headers}
            for index, row in df.iterrows():
                for header in headers:
                    item = row[header]
                    if pd.notnull(item):  # Check if the cell is not empty
                        categories[header].append(item)
            self.flat_categories = [f"{header} > {item}" for header, items in categories.items() for item in items]

def main():
    app = App()
    app.read_categories('./categories.csv')  # Assuming you have a categories.csv
    app.mainloop()

if __name__ == "__main__":
    main()

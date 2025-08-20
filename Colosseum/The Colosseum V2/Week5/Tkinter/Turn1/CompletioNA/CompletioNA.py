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
        classic_bg = "#F5F5F5"  
        button_bg = "#D3D3D3"  
        button_fg = "maroon"  
        treeview_bg = "#FFFFFF"  
        treeview_field_bg = "#F5F5F5"  
        selected_bg = "#C0C0C0"

        # Style configurations
        self.style.configure("Treeview", background=treeview_bg, foreground="black",
                             rowheight=25, fieldbackground=treeview_field_bg)
        self.style.map("Treeview", background=[('selected', selected_bg)])
        self.style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'), background=classic_bg)
        self.style.configure("TButton", font=('Calibri', 10, 'bold'), background=button_bg, foreground=button_fg)
        self.style.configure("TCombobox", fieldbackground=treeview_field_bg, background="white")

        # Initialize object tracking lists
        self.shared_objects = []
        self.records_objects = []
        self.plotting_objects = []

        self.create_widgets()
        self.show_records_interface()  # Default view

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=10, fill=tk.X)

        # Shared Objects (Buttons & Separator)
        load_btn = ttk.Button(buttons_frame, text="Load Bank Records", command=self.load_records)
        load_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        show_chart_btn = ttk.Button(buttons_frame, text="Show Chart", command=self.show_plotting_interface)
        show_chart_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        menu_separator = ttk.Separator(main_frame, orient='horizontal')
        menu_separator.pack(fill='x', padx=2, pady=2)

        # Track shared objects
        self.shared_objects.extend([load_btn, show_chart_btn, menu_separator])

        # Records Interface Objects
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(pady=10, fill=tk.X)
        search_var = tk.StringVar()
        search_input = ttk.Entry(search_frame, textvariable=search_var, width=50)
        search_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        search_input.insert(0, "Search Records...")
        uncategorized_var = tk.BooleanVar()
        uncategorized_checkbox = ttk.Checkbutton(search_frame, text="Uncategorized Only", variable=uncategorized_var)
        uncategorized_checkbox.grid(row=0, column=1, sticky="w")

        self.tree = ttk.Treeview(main_frame, columns=("Record", "Date Purchased", "Date Committed", 
                                                      "Figure", "Description", "Balance"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(main_frame, textvariable=self.category_var)
        self.category_combobox.pack(pady=2, fill=tk.X)

        categorize_btn = ttk.Button(main_frame, text="Categorize Record")
        categorize_btn.pack(pady=2, fill=tk.X)

        # Track Records objects
        self.records_objects.extend([
            search_frame, search_input, uncategorized_checkbox, self.tree, 
            self.category_combobox, categorize_btn
        ])

        # Plotting Interface Objects (Example Placeholder Label)
        chart_label = ttk.Label(main_frame, text="Plotting Interface Placeholder: Chart will be displayed here.")
        chart_label.pack(pady=20, fill=tk.X)

        # Track Plotting objects
        self.plotting_objects.append(chart_label)

    def clear_objects(self):
        for obj in self.records_objects + self.plotting_objects:
            obj.pack_forget()

    def show_records_interface(self):
        self.clear_objects()
        for obj in self.records_objects:
            obj.pack(pady=5, fill=tk.X)

    def show_plotting_interface(self):
        self.clear_objects()
        for obj in self.plotting_objects:
            obj.pack(pady=20, fill=tk.X)

    def load_records(self):
        filepath = './database.csv'
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if not df.empty and len(df.columns) >= 8:
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                total_records = len(df)
                unassigned_records = len(df[df['Entity'].isnull()])
                messagebox.showinfo("Info", 
                                    f"File last saved on {modified_time} "
                                    f"with {total_records} and {unassigned_records} (%) uncategorized records.")
                for item in self.tree.get_children():
                    self.tree.delete(item)
                for _, row in df.iterrows():
                    self.tree.insert("", "end", values=(
                        row['Record'], row['Date Purchased'], row['Date Committed'], 
                        row['Figure'], row['Description'], row['Balance']
                    ))
            else:
                messagebox.showwarning("Warning", "CSV is empty or missing columns.")
        else:
            messagebox.showerror("Error", "Database not found.")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()

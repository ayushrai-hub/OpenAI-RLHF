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

        # Colors
        classic_bg = "#F5F5F5"
        btn_bg = "#D3D3D3"
        btn_fg = "maroon"
        treeview_bg = "#FFFFFF"
        treeview_field_bg = "#F5F5F5"
        selected_bg = "#C0C0C0"

        # Configure styles
        self.style.configure("Treeview", background=treeview_bg, foreground="black",
                             rowheight=25, fieldbackground=treeview_field_bg)
        self.style.map("Treeview", background=[('selected', selected_bg)])

        self.style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'), background=classic_bg)

        self.style.configure("TButton", font=('Calibri', 10, 'bold'), background=btn_bg, foreground=btn_fg)
        self.style.configure("TCombobox", fieldbackground=treeview_field_bg, background="white")

        # Create main frames for Data and Graph
        self.create_frames()
        self.create_widgets()

        # Load categories from CSV
        self.read_categories('./categories.csv')

    def create_frames(self):
        """
        Create separate frames for Data and Graph views.
        The Data frame includes the common items for data-only view,
        while the Graph frame includes the common items for the graph view.
        """
        # Frame for Data
        self.data_frame = ttk.Frame(self)
        
        # Frame for Graph
        self.graph_frame = ttk.Frame(self)

    def create_widgets(self):
        """
        Create the layout of the main window, including:
        - Two buttons (Import Transaction Records, Show Graph) in a shared frame
        - A horizontal divider in both Data and Graph views
        - The Data interface (search box, uncategorized check, tree, category combobox, categorize button)
        - The Graph interface (import button, show graph button, horizontal divider, graph placeholder)
        """
        # Main container to hold Data and Graph
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # A top frame for shared buttons and divider
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)

        # Shared buttons (Import Transaction Records and Show Graph) appear in both Data and Graph
        self.import_button_data = ttk.Button(button_frame, text="Import Transaction Records",
                                            command=self.load_records, style="TButton")
        self.import_button_data.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.show_graph_button_data = ttk.Button(button_frame, text="Show Graph",
                                               command=self.show_graph, style="TButton")
        self.show_graph_button_data.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Horizontal divider in the main frame (shared)
        self.separator = ttk.Separator(main_frame, orient='horizontal')
        self.separator.pack(fill='x', padx=2, pady=2)

        # ------------------------------------------------------
        # Data-only interface (only relevant for Data view)
        # ------------------------------------------------------
        self.data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Search and filter widgets
        search_frame = ttk.Frame(self.data_frame)
        search_frame.pack(pady=10, fill=tk.X)

        self.search_var = tk.StringVar()
        self.search_box = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_box.grid(row=0, column=0, sticky="ew", padx=(0,5))
        self.search_box.insert(0, "Search Transactions...")
        self.search_box.bind("<FocusIn>", lambda e: self.on_search_focus_in(self.search_box, self.search_var))
        self.search_box.bind("<FocusOut>", lambda e: self.on_search_focus_out(self.search_box, self.search_var))

        self.uncategorized_var = tk.BooleanVar()
        self.uncategorized_check = ttk.Checkbutton(search_frame, text="Uncategorized Only",
                                                  variable=self.uncategorized_var)
        self.uncategorized_check.grid(row=0, column=1, sticky="w")

        # Data Treeview (main data view)
        self.tree = ttk.Treeview(self.data_frame, columns=("Transaction", "Purchase Date",
                                                          "Post Date", "Amount", "Details", "Balance"),
                                 show="headings", style="Treeview")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Category combobox
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.data_frame, textvariable=self.category_var, style="TCombobox")
        self.category_combobox.pack(pady=2, fill=tk.X)
        self.category_combobox.bind('<KeyRelease>', self.filter_category_options)

        # Assign category button
        self.categorize_button = ttk.Button(self.data_frame, text="Assign Category", style="TButton")
        self.categorize_button.pack(pady=2, fill=tk.X)

        # ------------------------------------------------------
        # Graph interface (only relevant for Graph view)
        # ------------------------------------------------------
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Import button in the graph interface (shared with data view)
        self.import_button_graph = ttk.Button(self.graph_frame, text="Import Transaction Records",
                                             command=self.load_records, style="TButton")
        self.import_button_graph.pack(side=tk.TOP, expand=True, fill=tk.X, padx=5, pady=5)

        # Show Graph button in the graph interface (shared)
        self.show_graph_button_graph = ttk.Button(self.graph_frame, text="Show Graph",
                                                command=self.show_graph, style="TButton")
        self.show_graph_button_graph.pack(side=tk.TOP, expand=True, fill=tk.X, padx=5, pady=5)

        # Horizontal divider in the graph interface
        self.separator_graph = ttk.Separator(self.graph_frame, orient='horizontal')
        self.separator_graph.pack(fill='x', padx=2, pady=2)

        # Placeholder for the graph content
        self.graph_placeholder = ttk.Label(self.graph_frame, text="Graph Placeholder", font=('Calibri', 14))
        self.graph_placeholder.pack(pady=10, fill=tk.BOTH, expand=True)

        # ------------------------------------------------------
        # By default, show the Data interface
        # ------------------------------------------------------
        self.show_data_view()

    def show_data_view(self):
        """
        Show the Data interface (data_frame) and hide the Graph interface (graph_frame).
        """
        self.data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.graph_frame.pack_forget()

    def show_graph_view(self):
        """
        Show the Graph interface (graph_frame) and hide the Data interface (data_frame).
        """
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.data_frame.pack_forget()

    def show_graph(self):
        """
        When the user clicks 'Show Graph', hide the Data interface and show the Graph interface.
        The shared objects remain visible in both views.
        """
        self.show_graph_view()

    def on_search_focus_in(self, entry, var):
        if entry.get() == "Search Transactions...":
            entry.delete(0, tk.END)

    def on_search_focus_out(self, entry, var):
        if not entry.get():
            entry.insert(0, "Search Transactions...")

    def read_categories(self, filepath):
        """
        Read categories from a CSV file to build a list of (header, value) pairs for filtering.
        """
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if not df.empty:
                self.flat_categories = []
                for col in df.columns:
                    # Collect non-null items in each column
                    for item in df[col].dropna():
                        self.flat_categories.append(f"{col} > {item}")
        else:
            # No categories file found
            print("Categories file not found.")

    def filter_category_options(self, event=None):
        """
        Filter the category combobox options as the user types, matching sub-categories.
        """
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

    def load_records(self):
        """
        Load transaction records from CSV and display them in the Data interface's treeview.
        """
        filepath = './database.csv'
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if not df.empty and len(df.columns) >= 8:
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                total_records = len(df)
                unassigned_records = len(df[df['Entity'].isnull()])
                messagebox.showinfo("Information",
                                    f"The file you were working on was last saved on {mod_time} and "
                                    f"contains {total_records} records, with {unassigned_records} uncategorized.")

                for _, row in df.iterrows():
                    self.tree.insert("", "end", values=(row['Transaction'], row['Purchase Date'], 
                                                      row['Post Date'], row['Amount'], row['Details'], row['Balance']))
            else:
                messagebox.showwarning("Warning",
                                       "The CSV file is either empty or lacks the necessary columns.")
        else:
            messagebox.showerror("Error", "Database file could not be located.")

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()

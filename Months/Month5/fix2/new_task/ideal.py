import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime

class BloodBankSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Blood Bank Management System")
        self.root.geometry("800x600")
        
        # Initialize database
        self.init_database()
        
        # Start with login frame
        self.show_login_frame()

    def init_database(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="bloodbank"
            )
            cursor = conn.cursor()
            
            # Create blood_request table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blood_request (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fullname VARCHAR(100),
                    bloodtype VARCHAR(5),
                    quantity INT,
                    purpose VARCHAR(255),
                    location VARCHAR(100),
                    request_date DATE,
                    status VARCHAR(20) DEFAULT 'In Process'
                )
            """)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to initialize database: {err}")

    def show_login_frame(self):
        # Clear current window
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Username:").grid(row=0, column=0, pady=5)
        username_entry = tk.Entry(frame)
        username_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Password:").grid(row=1, column=0, pady=5)
        password_entry = tk.Entry(frame, show="*")
        password_entry.grid(row=1, column=1, pady=5)

        tk.Button(frame, text="Login", command=lambda: self.login(username_entry.get(), password_entry.get())).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Register", command=self.show_register_frame).grid(row=3, column=0, columnspan=2)

    def show_register_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Username:").grid(row=0, column=0, pady=5)
        username_entry = tk.Entry(frame)
        username_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Password:").grid(row=1, column=0, pady=5)
        password_entry = tk.Entry(frame, show="*")
        password_entry.grid(row=1, column=1, pady=5)

        role_var = tk.StringVar(value="User")
        tk.Radiobutton(frame, text="User", variable=role_var, value="User").grid(row=2, column=0)
        tk.Radiobutton(frame, text="Admin", variable=role_var, value="Admin").grid(row=2, column=1)

        tk.Button(frame, text="Register", command=lambda: self.register(username_entry.get(), password_entry.get(), role_var.get())).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Back to Login", command=self.show_login_frame).grid(row=4, column=0, columnspan=2)

    def login(self, username, password):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="", database="bloodbank")
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()
            conn.close()

            if result:
                if result[0] == "Admin":
                    self.show_admin_dashboard()
                else:
                    self.show_user_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Login failed: {err}")

    def register(self, username, password, role):
        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="", database="bloodbank")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                         (username, password, role))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration successful")
            self.show_login_frame()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Registration failed: {err}")

    def show_user_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20)

        tk.Button(frame, text="Request Blood", command=self.show_blood_request_form).pack(pady=5)
        tk.Button(frame, text="View Blood Inventory", command=self.show_blood_inventory).pack(pady=5)
        tk.Button(frame, text="View My Requests", command=self.show_my_requests).pack(pady=5)
        tk.Button(frame, text="Logout", command=self.show_login_frame).pack(pady=20)

    def show_admin_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20)

        tk.Button(frame, text="View All Requests", command=self.show_all_requests).pack(pady=5)
        tk.Button(frame, text="Manage Blood Inventory", command=self.show_inventory_management).pack(pady=5)
        tk.Button(frame, text="View Donors", command=self.show_donors).pack(pady=5)
        tk.Button(frame, text="Logout", command=self.show_login_frame).pack(pady=20)

    def show_blood_request_form(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Full Name:").grid(row=0, column=0, pady=5)
        name_entry = tk.Entry(frame)
        name_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Blood Type:").grid(row=1, column=0, pady=5)
        blood_type = ttk.Combobox(frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        blood_type.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Quantity (units):").grid(row=2, column=0, pady=5)
        quantity_entry = tk.Entry(frame)
        quantity_entry.grid(row=2, column=1, pady=5)

        tk.Label(frame, text="Purpose:").grid(row=3, column=0, pady=5)
        purpose = ttk.Combobox(frame, values=["Surgery", "Accident", "Anemia", "Cancer Treatment", "Other"])
        purpose.grid(row=3, column=1, pady=5)

        tk.Button(frame, text="Submit Request", 
                 command=lambda: self.submit_blood_request(
                     name_entry.get(), blood_type.get(), 
                     quantity_entry.get(), purpose.get())).grid(row=4, column=0, columnspan=2, pady=10)
        
        tk.Button(frame, text="Back", command=self.show_user_dashboard).grid(row=5, column=0, columnspan=2)

    def submit_blood_request(self, name, blood_type, quantity, purpose):
        try:
            quantity = int(quantity)
            if not all([name, blood_type, quantity, purpose]):
                messagebox.showerror("Error", "Please fill all fields")
                return

            conn = mysql.connector.connect(host="localhost", user="root", password="", database="bloodbank")
            cursor = conn.cursor()

            # Check blood availability
            cursor.execute("SELECT quantity FROM blood_inventory WHERE blood_type = %s", (blood_type,))
            available = cursor.fetchone()

            if not available or available[0] < quantity:
                # Find nearby donors
                cursor.execute("SELECT fullname, contact FROM donors WHERE blood_type = %s", (blood_type,))
                donors = cursor.fetchall()
                
                status = "Denied"
                if donors:
                    donor_msg = "Nearby donors available:\n" + "\n".join([f"{d[0]}: {d[1]}" for d in donors])
                    messagebox.showinfo("Blood Unavailable", donor_msg)
                else:
                    messagebox.showerror("Error", "Blood unavailable and no donors found")
            else:
                status = "In Process"

            # Insert request
            cursor.execute("""
                INSERT INTO blood_request 
                (fullname, bloodtype, quantity, purpose, request_date, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, blood_type, quantity, purpose, datetime.now().date(), status))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Request submitted successfully")
            self.show_user_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Request failed: {err}")

    def show_blood_inventory(self):
        self.show_data_table("SELECT blood_type, quantity FROM blood_inventory", 
                            ["Blood Type", "Quantity Available"])

    def show_my_requests(self):
        self.show_data_table("""
            SELECT fullname, bloodtype, quantity, purpose, request_date, status 
            FROM blood_request
        """, ["Name", "Blood Type", "Quantity", "Purpose", "Date", "Status"])

    def show_all_requests(self):
        self.show_data_table("""
            SELECT id, fullname, bloodtype, quantity, purpose, request_date, status 
            FROM blood_request
        """, ["ID", "Name", "Blood Type", "Quantity", "Purpose", "Date", "Status"])

    def show_data_table(self, query, columns):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Create Treeview
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Fetch and display data
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="", database="bloodbank")
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch data: {err}")

        # Back button
        tk.Button(frame, text="Back", command=self.show_admin_dashboard).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = BloodBankSystem(root)
    root.mainloop()
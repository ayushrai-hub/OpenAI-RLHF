
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime, timedelta

class SecurityManager:
    def __init__(self):
        self.credentials = {}
        self.load_or_create_credentials()

    def load_or_create_credentials(self):
        # Hardcoded credentials for demonstration
        self.credentials = {
            "staff": {"user_key": "12345", "password": "staffsecret"},
            "pupil": {"user_key": "67890", "password": "pupilpass"}
        }

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_user(self, user_key, password, is_staff):
        user_type = "staff" if is_staff else "pupil"
        if user_key == self.credentials[user_type]["user_key"] and password == self.credentials[user_type]["password"]:
            return True
        return False

class MessageBoard:
    def __init__(self, primary_win):
        self.primary_win = primary_win
        self.security_manager = SecurityManager()
        self.setup_interface()

    def setup_interface(self):
        self.primary_win.title("Access")
        self.primary_win.configure(bg='light green')
        self.primary_win.attributes('-fullscreen', True)

        label = tk.Label(self.primary_win, text="Select User Category:", font=('Arial', 14), bg='light green')
        label.pack(pady=20)
        pupil_button = tk.Button(self.primary_win, text="Pupil", command=lambda: self.authenticate(False), font=('Arial', 12))
        pupil_button.pack(pady=10)
        staff_button = tk.Button(self.primary_win, text="Staff", command=lambda: self.authenticate(True), font=('Arial', 12))
        staff_button.pack(pady=10)

    def authenticate(self, is_staff):
        user_key = simpledialog.askstring("User Key", "Enter your user key:", parent=self.primary_win)
        password = simpledialog.askstring("Password", "Enter your password:", show='*', parent=self.primary_win)

        if self.security_manager.verify_user(user_key, password, is_staff):
            self.launch_message_board(user_key, is_staff)
        else:
            messagebox.showerror("Error", "Invalid credentials", parent=self.primary_win)

    def launch_message_board(self, user_key, is_staff):
        self.primary_win.destroy()
        secondary_win = tk.Tk()
        MessageBoardInterface(secondary_win, user_key, is_staff)

class MessageBoardInterface:
    def __init__(self, primary_win, user_key, is_staff):
        self.primary_win = primary_win
        self.user_key = user_key
        self.is_staff = is_staff
        self.announcements = []
        self.setup_interface()

    def setup_interface(self):
        self.primary_win.title("DARTMOUTH INSTITUTE MESSAGE BOARD")
        self.primary_win.configure(bg='light green')
        self.primary_win.attributes('-fullscreen', True)

        header_label = tk.Label(self.primary_win, text="DARTMOUTH INSTITUTE MESSAGE BOARD", font=('Arial', 18, 'bold'), bg='light green')
        header_label.pack(pady=20)

        self.announcement_listbox = tk.Listbox(self.primary_win, width=80, height=20, bg='light green', fg='black', font=('Arial', 12))
        self.announcement_listbox.pack(pady=10)

        if self.is_staff:
            self.setup_staff_interface()
        self.load_initial_announcements()
        self.refresh_announcement_list()
        self.verify_expired_announcements()

    def setup_staff_interface(self):
        panel = tk.Frame(self.primary_win, bg='light green')
        panel.pack(pady=10)

        self.announcement_entry = tk.Entry(panel, width=50, font=('Arial', 12))
        self.announcement_entry.pack(side=tk.LEFT, padx=10)

        date_label = tk.Label(panel, text="Date (DD/MM/YYYY):", font=('Arial', 12), bg='light green')
        date_label.pack(side=tk.LEFT, padx=10)
        self.date_entry = tk.Entry(panel, width=20, font=('Arial', 12))
        self.date_entry.pack(side=tk.LEFT, padx=10)
        self.date_entry.insert(0, "DD/MM/YYYY")

        time_label = tk.Label(panel, text="Time (HH:MM AM/PM):", font=('Arial', 12), bg='light green')
        time_label.pack(side=tk.LEFT, padx=10)
        self.time_entry = tk.Entry(panel, width=20, font=('Arial', 12))
        self.time_entry.pack(side=tk.LEFT, padx=10)
        self.time_entry.insert(0, "HH:MM AM/PM")

        insert_button = tk.Button(panel, text="Insert Announcement", command=self.add_announcement, font=('Arial', 12))
        insert_button.pack(side=tk.LEFT)

        task_panel = tk.Frame(self.primary_win, bg='light green')
        task_panel.pack(pady=10)

        swap_view_button = tk.Button(task_panel, text="Switch to Pupil View", command=self.swap_view, font=('Arial', 12))
        swap_view_button.pack(side=tk.LEFT, padx=10)

        delete_button = tk.Button(task_panel, text="Delete Announcement", command=self.delete_announcement, font=('Arial', 12))
        delete_button.pack(side=tk.RIGHT, padx=10)

    def load_initial_announcements(self):
        starting_announcements = [("Staff Meeting", datetime.now() + timedelta(minutes=5)),
                                  ("Pupil Event", datetime.now() + timedelta(minutes=10))]
        for announcement, expiry in starting_announcements:
            self.add_announcement_to_list(announcement, expiry)

    def add_announcement_to_list(self, announcement, expiry, from_entry=False):
        formatted = f"{announcement} (Expires at {expiry.strftime('%I:%M %p on %d %b %Y')})"
        self.announcements.append((announcement, expiry))
        self.refresh_announcement_list()

    def add_announcement(self):
        announcement = self.announcement_entry.get()
        date_string = self.date_entry.get()
        time_string = self.time_entry.get()

        try:
            expiry = datetime.strptime(f"{date_string} {time_string}", "%d/%m/%Y %I:%M %p")
            self.add_announcement_to_list(announcement, expiry, from_entry=True)
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid date or time format.")

    def modify_announcement(self):
        pass

    def delete_announcement(self):
        selected_index = self.announcement_listbox.curselection()
        if selected_index:
            del self.announcements[selected_index[0]]
            self.refresh_announcement_list()

    def swap_view(self):
        pass

    def refresh_announcement_list(self):
        self.announcement_listbox.delete(0, tk.END)
        for announcement, expiry in self.announcements:
            formatted = f"{announcement} (Expires at {expiry.strftime('%I:%M %p on %d %b %Y')})"
            self.announcement_listbox.insert(tk.END, formatted)

    def verify_expired_announcements(self):
        now = datetime.now()
        self.announcements = [(a, e) for a, e in self.announcements if e > now]
        self.refresh_announcement_list()
        self.primary_win.after(60000, self.verify_expired_announcements)
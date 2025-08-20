# ideal_completion.py

import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime, timedelta
import hashlib
import json
import os

class SecurityManager:
    def __init__(self):
        self.user_credentials = {
            'staff': {
                'admin': self.hash_password('staffsecret')
            },
            'pupil': {
                '12345': self.hash_password('pupilpass')
            }
        }
        self.load_or_create_credentials()
    
    def load_or_create_credentials(self):
        try:
            if os.path.exists('credentials.json'):
                with open('credentials.json', 'r') as f:
                    self.user_credentials = json.load(f)
            else:
                with open('credentials.json', 'w') as f:
                    json.dump(self.user_credentials, f)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to manage credentials: {str(e)}")
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, user_key, password, is_staff):
        try:
            if not user_key:
                raise ValueError("User key cannot be empty")
            if not is_staff and not user_key.isdigit():
                raise ValueError("Pupil ID must be numeric")
                
            user_type = 'staff' if is_staff else 'pupil'
            stored_hash = self.user_credentials[user_type].get(user_key)
            return stored_hash == self.hash_password(password)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

class MessageBoard:
    def __init__(self, primary_win):
        self.primary_win = primary_win
        self.primary_win.title("Access")
        self.primary_win.configure(bg='light green')
        self.primary_win.attributes('-fullscreen', True)
        self.security = SecurityManager()
        self.setup_interface()
    
    def setup_interface(self):
        label = tk.Label(self.primary_win, 
                        text="Select User Category:", 
                        font=('Arial', 14), 
                        bg='light green')
        label.pack(pady=20)
        
        pupil_button = tk.Button(self.primary_win, 
                                text="Pupil", 
                                command=lambda: self.authenticate(False),
                                font=('Arial', 12))
        pupil_button.pack(pady=10)
        
        staff_button = tk.Button(self.primary_win, 
                                text="Staff", 
                                command=lambda: self.authenticate(True),
                                font=('Arial', 12))
        staff_button.pack(pady=10)
    
    def authenticate(self, is_staff):
        try:
            user_key = simpledialog.askstring("User Key", "Enter your user key:", 
                                            parent=self.primary_win)
            if not user_key:
                return
            
            secret_word = simpledialog.askstring("Secret Word", "Enter your secret word:", 
                                               show='*', parent=self.primary_win)
            if not secret_word:
                return
            
            if self.security.verify_user(user_key, secret_word, is_staff):
                self.primary_win.destroy()
                self.launch_message_board(user_key, is_staff)
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def launch_message_board(self, user_key, is_staff):
        secondary_win = tk.Tk()
        secondary_win.title("DARTMOUTH INSTITUTE MESSAGE BOARD")
        secondary_win.configure(bg='light green')
        secondary_win.attributes('-fullscreen', True)
        MessageBoardInterface(secondary_win, user_key, is_staff)

class MessageBoardInterface:
    def __init__(self, primary_win, user_key, is_staff):
        self.primary_win = primary_win
        self.user_key = user_key
        self.is_staff = is_staff
        self.announcements = []
        self.setup_interface()
        self.load_initial_announcements()
        self.verify_expired_announcements()
    
    def setup_interface(self):
        # Header
        self.header_label = tk.Label(self.primary_win, 
                                   text="DARTMOUTH INSTITUTE MESSAGE BOARD",
                                   font=('Arial', 18, 'bold'), 
                                   bg='light green')
        self.header_label.pack(pady=20)
        
        # Announcements List
        self.announcement_listbox = tk.Listbox(self.primary_win, 
                                             width=80, height=20,
                                             font=('Arial', 12),
                                             bg='light green')
        self.announcement_listbox.pack(pady=10)
        
        if self.is_staff:
            self.setup_staff_interface()
        
        # Close Button
        self.signout_button = tk.Button(self.primary_win, 
                                      text="Close",
                                      command=self.signout,
                                      font=('Arial', 12),
                                      bg='red', fg='white')
        self.signout_button.pack(pady=10)
    
    def setup_staff_interface(self):
        # User Label
        self.user_tag_label = tk.Label(self.primary_win, 
                                     text=f"Signed in as: {self.user_key}",
                                     font=('Arial', 12), 
                                     bg='light green')
        self.user_tag_label.pack(pady=5)
        
        # Announcement Entry Panel
        self.panel = tk.Frame(self.primary_win, bg='light green')
        self.panel.pack(pady=10)
        
        # Announcement Entry
        self.announcement_entry = tk.Entry(self.panel, width=50, font=('Arial', 12))
        self.announcement_entry.pack(side=tk.LEFT, padx=10)
        
        # Date Entry
        tk.Label(self.panel, text="Date (DD/MM/YYYY):", 
                font=('Arial', 12), bg='light green').pack(side=tk.LEFT, padx=10)
        self.datefield_entry = tk.Entry(self.panel, width=15, font=('Arial', 12))
        self.datefield_entry.pack(side=tk.LEFT, padx=10)
        self.datefield_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        # Time Entry
        tk.Label(self.panel, text="Time (HH:MM AM/PM):", 
                font=('Arial', 12), bg='light green').pack(side=tk.LEFT, padx=10)
        self.timefield_entry = tk.Entry(self.panel, width=15, font=('Arial', 12))
        self.timefield_entry.pack(side=tk.LEFT, padx=10)
        self.timefield_entry.insert(0, datetime.now().strftime('%I:%M %p'))
        
        # Control Buttons Panel
        self.task_panel = tk.Frame(self.primary_win, bg='light green')
        self.task_panel.pack(pady=10)
        
        # Control Buttons
        self.insert_button = tk.Button(self.task_panel, text="Insert Announcement",
                                     command=self.add_announcement, font=('Arial', 12))
        self.insert_button.pack(side=tk.LEFT, padx=10)
        
        self.modify_button = tk.Button(self.task_panel, text="Modify Selected",
                                     command=self.modify_announcement, font=('Arial', 12))
        self.modify_button.pack(side=tk.LEFT, padx=10)
        
        self.delete_button = tk.Button(self.task_panel, text="Delete Selected",
                                     command=self.delete_announcement, font=('Arial', 12))
        self.delete_button.pack(side=tk.LEFT, padx=10)
        
        self.swap_view_button = tk.Button(self.task_panel, text="Switch to Pupil View",
                                        command=self.swap_view, font=('Arial', 12))
        self.swap_view_button.pack(side=tk.LEFT, padx=10)
    
    def load_initial_announcements(self):
        initial = [
            ("Staff Conference at 11 AM", datetime.now() + timedelta(minutes=2)),
            ("Workshop on AI in Learning", datetime.now() + timedelta(minutes=5))
        ]
        for text, expiry in initial:
            self.add_announcement_to_list(text, expiry)
    
    def add_announcement_to_list(self, announcement, expiry, from_entry=False):
        self.announcements.append({
            'text': announcement,
            'expiry': expiry,
            'user': self.user_key if from_entry else 'System'
        })
        self.refresh_announcement_list()
    
    def add_announcement(self):
        try:
            text = self.announcement_entry.get().strip()
            date_str = self.datefield_entry.get().strip()
            time_str = self.timefield_entry.get().strip()
            
            if not all([text, date_str, time_str]):
                raise ValueError("All fields are required")
            
            expiry = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %I:%M %p")
            if expiry <= datetime.now():
                raise ValueError("Expiry time must be in the future")
            
            self.add_announcement_to_list(text, expiry, True)
            self.announcement_entry.delete(0, tk.END)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def modify_announcement(self):
        selection = self.announcement_listbox.curselection()
        if not selection:
            messagebox.showwarning("Error", "Please select an announcement to modify")
            return
            
        idx = selection[0]
        announcement = self.announcements[idx]
        
        new_text = simpledialog.askstring("Modify Announcement", 
                                        "Edit announcement:",
                                        initialvalue=announcement['text'])
        if new_text:
            announcement['text'] = new_text.strip()
            self.refresh_announcement_list()
    
    def delete_announcement(self):
        selection = self.announcement_listbox.curselection()
        if not selection:
            messagebox.showwarning("Error", "Please select an announcement to delete")
            return
            
        idx = selection[0]
        del self.announcements[idx]
        self.refresh_announcement_list()
    
    def swap_view(self):
        if self.is_staff:
            for widget in [self.announcement_entry, self.datefield_entry, 
                         self.timefield_entry, self.insert_button, 
                         self.delete_button, self.modify_button]:
                widget.config(state=tk.DISABLED)
            self.swap_view_button.config(text="Switch to Staff View")
        else:
            for widget in [self.announcement_entry, self.datefield_entry, 
                         self.timefield_entry, self.insert_button, 
                         self.delete_button, self.modify_button]:
                widget.config(state=tk.NORMAL)
            self.swap_view_button.config(text="Switch to Pupil View")
        
        self.is_staff = not self.is_staff
        self.refresh_announcement_list()
    
    def refresh_announcement_list(self):
        self.announcement_listbox.delete(0, tk.END)
        current_time = datetime.now()
        
        for announcement in self.announcements:
            if announcement['expiry'] > current_time:
                text = f"{announcement['text']} (Expires: {announcement['expiry'].strftime('%I:%M %p on %d %b %Y')})"
                if self.is_staff:
                    text += f" - {announcement['user']}"
                self.announcement_listbox.insert(tk.END, text)
    
    def verify_expired_announcements(self):
        current_time = datetime.now()
        self.announcements = [a for a in self.announcements 
                            if a['expiry'] > current_time]
        self.refresh_announcement_list()
        self.primary_win.after(60000, self.verify_expired_announcements)
    
    def signout(self):
        self.primary_win.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MessageBoard(root)
    root.mainloop()
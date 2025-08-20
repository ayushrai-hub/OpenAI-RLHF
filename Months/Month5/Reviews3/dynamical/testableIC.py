import tkinter as tk
from tkinter import messagebox

class MealDeliveryAdviceSystem:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.title("Meal Delivery Advice System")
        self.main_window.geometry("600x400")
        self.main_window.configure(bg="#f0f9ea")  # Set background color

        # Welcome Label
        self.greeting_label = tk.Label(main_window, text="Welcome to Meal Delivery Advice System", font=("Arial", 18), bg="#f0f9ea", fg="#333333")
        self.greeting_label.pack(pady=20)

        # Text Box for User Query
        self.query_prompt = tk.Label(main_window, text="Type your question:", font=("Arial", 12), bg="#f0f9ea", fg="#333333")
        self.query_prompt.pack(pady=10)

        self.query_input = tk.Entry(main_window, width=50, font=("Arial", 12), bd=2, relief="solid")
        self.query_input.pack(pady=5)

        self.ask_button = tk.Button(main_window, text="Ask", command=self.pose_question, bg="#8BC34A", fg="white", bd=2, relief="raised")
        self.ask_button.pack(pady=10)

        # Frame for displaying inquiries and solutions
        self.solution_frame = tk.LabelFrame(main_window, text="Inquiry & Solution", font=("Arial", 12), bg="#f0f9ea", fg="#333333", padx=10, pady=10)
        self.solution_frame.pack(pady=20, fill="both", expand="yes")

        self.question_label = tk.Label(self.solution_frame, text="", font=("Arial", 12), bg="#f0f9ea", fg="#333333")
        self.question_label.pack(pady=5)

        self.solution_label = tk.Label(self.solution_frame, text="", font=("Arial", 12), bg="#f0f9ea", fg="#333333")
        self.solution_label.pack(pady=5)

        # Inquiries and Solutions
        self.inquiries = [
            "What are the delivery fees?",
            "Do you offer free delivery for a certain order total?",
            "What is the average delivery time?",
            "Is it possible to schedule a delivery for later?",
            "Which payment options are available?",
        ]

        self.solutions = [
            "Delivery fees are determined by the restaurant and area, typically ranging from $2 to $5.",
            "Yes, services might offer free delivery on orders above a threshold, often $20 or higher.",
            "Time frames for delivery are distance-based, typically 30 to 60 minutes.",
            "Usually, there's an option to schedule your delivery during checkout.",
            "Common payment options include cards, PayPal, and sometimes cash.",
        ]

    def pose_question(self):
        user_query = self.query_input.get().strip().lower()
        if not user_query:
            messagebox.showwarning("Input Required", "Please enter a question before clicking 'Ask'.")
            return

        user_query = user_query.lower()

        solution = None
        for i, inquiry in enumerate(self.inquiries):
            if all(keyword in user_query for keyword in inquiry.lower().split()):
                self.question_label.config(text=f"Inquiry: {inquiry}")
                self.solution_label.config(text=f"Solution: {self.solutions[i]}")
                return

        self.question_label.config(text="")  # Clear if not found
        self.solution_label.config(text="Sorry, I can't find an answer to that query.")

if __name__ == "__main__":
    main_window = tk.Tk()
    application = MealDeliveryAdviceSystem(main_window)
    main_window.mainloop()

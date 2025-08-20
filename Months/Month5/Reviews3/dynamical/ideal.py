#ideal_completion.py
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

        self.ask_button = tk.Button(main_window, text="Ask", command=self.respond_to_question, bg="#8BC34A", fg="white", bd=2, relief="raised")
        self.ask_button.pack(pady=10)

        # Questions and Responses
        self.inquiries = [
            "What are the delivery fees?",
            "Do you offer free delivery for a certain order total?",
            "What is the average delivery time?",
            "Is it possible to schedule a delivery for later?",
            "Which payment options are available?",
            "Can delivery be paid in cash?",
            "Are there any promotional discounts?",
            "What's the process for using a promo code on my order?",
            "How should I handle a delivery delay?",
            "Is real-time order tracking possible?",
            "What are the steps to cancel an order?",
            "Do I receive a refund on order cancellation?",
            "How to report incorrect or missing items in my order?",
            "How do I get in touch with customer support?",
            "What about vegetarian or vegan options?",
            "Can I personalize my order, like no onions or extra sauce?",
            "Will the food be packed securely to avoid spills?",
            "Are there any costs for packaging?",
            "What eco-friendly packaging choices exist?",
            "Is it easy to reorder from my history?",
            "Is tipping the delivery person required?",
            "How much tipping is appropriate for the delivery?",
            "What happens if I'm out when the delivery arrives?",
            "Can the delivery address be changed after the order?",
            "Is contactless delivery an option?",
            "What if an item I've ordered is unavailable?",
            "Do meal deals for families or combos exist?",
            "Can a single order be placed from different restaurants?",
            "Are loyalty points earned from regular orders?",
            "Can I view a menu in another language?",
            "How can I verify if a restaurant is delivering?",
            "Is alcohol delivery permitted?",
            "What safety practices are undertaken during delivery?",
            "Is there an option for automatically scheduled deliveries?",
            "What if my address is difficult for the delivery person to locate?",
            "Are there special deals during festive seasons?",
            "How can I submit a review or feedback?",
            "Is pickup instead of delivery available as an option?",
            "How should I react to a package arriving damaged?",
            "Where can I find gluten-free choices?",
            "What indicates a restaurant's health standards?",
            "Is ordering for a large event possible?",
            "What should I do when I have food allergies?",
            "Are there special meals for children?",
            "What occurs if the delivery is slower than expected?",
            "Is it possible to order ahead for a future date?",
            "Does a subscription service exist for routine orders?",
            "How to act if payment does not go through?",
            "Can I provide specific directions for delivery?",
            "What time is ideal to place orders to avoid wait times?"
        ]

        self.solutions = [
            "Delivery fees are determined by the restaurant and area, typically ranging from $2 to $5.",
            "Yes, services might offer free delivery on orders above a threshold, often $20 or higher.",
            "Time frames for delivery are distance-based, typically 30 to 60 minutes.",
            "Usually, there's an option to schedule your delivery during checkout.",
            "Common payment options include cards, PayPal, and sometimes cash.",
            "Cash payment is an option, depending on each restaurant and service.",
            "Check online platforms or apps for current vouchers or promos.",
            "Redeem coupon codes at checkout in the designated area.",
            "If delayed, reach out to support for further steps or compensation.",
            "Most services offer real-time tracking using their application.",
            "Orders can often be canceled directly or through support, within an allowed time.",
            "Refunds are typically processed back within a few days but depend on the terms.",
            "File a complaint with support to correct the order immediately.",
            "Contact support via the app or webpage via call, chat, or email.",
            "Options for vegans and vegetarians are available through menu filters.",
            "Customization like extra toppings or removal is allowed by most services.",
            "Packages are generally ensured to prevent spills with tamper-proof seals.",
            "Packaging is free with some orders, yet might come with a fee.",
            "Eco alternatives are part of some service and restaurant offerings.",
            "Easily reorder previous meals through your account history.",
            "While not obligatory, a tip of 10-15% is a regular courtesy.",
            "Typical tips vary from $2 to $5 based on the order and effort.",
            "Briefly contact you, or leave the meal in a safe spot if you're absent.",
            "To update your address, connect with support urgently.",
            "Yes, for safety many provide a contactless drop-off option.",
            "Substitutes or a refund follow stock shortages.",
            "Meal packages or family deals are commonly offered at discounts.",
            "Multiple orders might accrue extra charges.",
            "Loyalty programs could provide points and discounts for frequent patrons.",
            "Adjust preferences for language on apps or websites.",
            "The platform tells you when businesses are open for orders.",
            "If allowed by the establishment and service, yes.",
            "Contactless delivery, sanitation, and more are key safety policies.",
            "Arrange routine deliveries for regularity with service if desired.",
            "They might ring for more directions.",
            "Festivals may bring exclusive offers; check the app for more.",
            "Feedback forms are available post-purchase through platforms.",
            "Select pickup at checkout instead of delivery.",
            "For faulty packages, reach out for a replacement or refund.",
            "Menus often include gluten-free options, just use filters.",
            "Look for restaurant ratings or health reviews within apps.",
            "Catering options are often available on larger requests.",
            "Share any allergies in order specifics or to the restaurant staff.",
            "Kids’ meals are generally on the menu at a reduced rate.",
            "Delayed deliveries warrant support contact for updates or credits.",
            "Pre-orders for coming events are often possible during checkout.",
            "Subscriptions may allow frequent deliverers extra perks or free shipping.",
            "Try alternative methods if immediate problems arise with payment.",
            "Provide necessary instructions during purchase proceedings.",
            "Ordering outside peak times, like late afternoons, can lessen delay."
        ]

    def respond_to_question(self):
        user_query = self.query_input.get().strip().lower()
        if not user_query:
            messagebox.showwarning("Input Required", "Please enter a question before clicking 'Ask'.")
            return

        # Normalize the user query for matching
        user_query = user_query.lower()

        # Find the closest matching question
        response = None
        for i, inquiry in enumerate(self.inquiries):
            # Simple keyword matching
            if all(keyword in user_query for keyword in inquiry.lower().split()):
                response = f"Q: {self.inquiries[i]}\nA: {self.solutions[i]}"
                break

        if response:
            messagebox.showinfo("Solution", response)
        else:
            messagebox.showwarning("Not Found", "Sorry, I can't find an answer to that query.")

if __name__ == "__main__":
    main_window = tk.Tk()
    application = MealDeliveryAdviceSystem(main_window)
    main_window.mainloop()


import random
import time
from tkinter import Tk, Label, StringVar, ttk

class QuizMaster:
    def __init__(self, master, vocab):
        self.master = master
        self.vocab = vocab
        self.total_words = len(vocab)

        self.current_word = None
        self.correct_answers = 0
        self.wrong_answers = 0
        self.start_time = time.time()

        self.input_var = StringVar()

        self.setup_gui()

    def setup_gui(self):
        self.master.title("Quiz Master Game")

        self.hint_label = Label(self.master, text="", font=("Helvetica", 14))
        self.hint_label.pack(pady=10)

        self.prompt_label = Label(self.master, text="Type the word:", font=("Helvetica", 12))
        self.prompt_label.pack(pady=5)

        self.entry_box = ttk.Entry(self.master, textvariable=self.input_var, font=("Helvetica", 12))
        self.entry_box.pack(pady=5)
        self.entry_box.bind("<Return>", lambda event: self.validate_input())  # Bind Enter key to validate_input

        self.verify_button = ttk.Button(self.master, text="Verify", command=self.validate_input)
        self.verify_button.pack(pady=5)

        self.stats_display = Label(self.master, text="", font=("Helvetica", 12))
        self.stats_display.pack(pady=10)

        self.refresh_display()

    def select_word(self):
        word_pair = random.choice(list(self.vocab.items()))
        return word_pair

    def refresh_display(self):
        if self.vocab:
            self.current_word, hint = self.select_word()
            self.hint_label.config(text=f"Hint: {hint}")
            self.input_var.set("")  # Clear the word entry
        else:
            self.hint_label.config(text="Bravo! You've guessed all the words.")
            self.prompt_label.pack_forget()
            self.entry_box.pack_forget()
            self.verify_button.pack_forget()

        remaining_words = len(self.vocab)
        elapsed_time = time.time() - self.start_time
        self.stats_display.config(text=f"Correct: {self.correct_answers} | Incorrect: {self.wrong_answers} | Percent: {self.compute_accuracy():.2f}% | Time: {elapsed_time:.2f}s | Words Remaining: {remaining_words}")

    def validate_input(self, event=None):  # Event parameter added for binding
        user_input = self.entry_box.get().strip().lower()
        correct_word = self.current_word.strip().lower()
        if user_input == correct_word:
            print("Well done!")
            self.correct_answers += 1
            del self.vocab[self.current_word]
            self.refresh_display()
        else:
            print("Try again!")
            self.wrong_answers += 1

    def compute_accuracy(self):
        total_attempts = self.correct_answers + self.wrong_answers
        if total_attempts == 0:
            return 0
        return (self.correct_answers / total_attempts) * 100

def main():
    app = Tk()
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12))
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TEntry", font=("Helvetica", 12))

    vocab = {
        "Python": "A high-level programming language.",
        "Java": "A general-purpose programming language.",
        "HTML": "The standard markup language for creating web pages."
    }

    game_instance = QuizMaster(app, vocab)
    app.mainloop()

if __name__ == "__main__":
    main()

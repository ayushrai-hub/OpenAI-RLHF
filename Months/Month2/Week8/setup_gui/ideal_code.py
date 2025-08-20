import random
import time
from tkinter import Tk, Label, StringVar, ttk
from difflib import SequenceMatcher

class QuizMaster:
    def __init__(self, master, vocab):
        self.master = master
        self.vocab = vocab
        self.total_words = len(vocab)
        self.current_word = None
        self.correct_answers = 0
        self.wrong_answers = 0
        self.start_time = time.time()
        self.word_start_time = 0
        self.difficulty = 'normal'
        self.setup_gui()

    def setup_gui(self):
        self.master.title("Enhanced Quiz Master Game")
        self.master.configure(bg='#f0f0f0')

        self.hint_label = Label(self.master, text="", font=("Helvetica", 14), bg='#f0f0f0')
        self.hint_label.pack(pady=10)

        self.prompt_label = Label(self.master, text="Type the word:", font=("Helvetica", 12), bg='#f0f0f0')
        self.prompt_label.pack(pady=5)

        self.input_var = StringVar()
        self.entry_box = ttk.Entry(self.master, textvariable=self.input_var, font=("Helvetica", 12))
        self.entry_box.pack(pady=5)
        self.entry_box.bind("<Return>", self.validate_input)

        self.verify_button = ttk.Button(self.master, text="Verify", command=self.validate_input)
        self.verify_button.pack(pady=5)

        self.hint_button = ttk.Button(self.master, text="Reveal Hint", command=self.reveal_hint)
        self.hint_button.pack(pady=5)

        self.stats_display = Label(self.master, text="", font=("Helvetica", 12), bg='#f0f0f0')
        self.stats_display.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.refresh_display()

    def select_word(self):
        word_pair = random.choice(list(self.vocab.items()))
        return word_pair

    def refresh_display(self):
        if self.vocab:
            self.current_word, hint = self.select_word()
            self.hint_label.config(text="Hint: " + '*' * len(hint))
            self.input_var.set("")
            self.word_start_time = time.time()
        else:
            self.end_game()

        remaining_words = len(self.vocab)
        elapsed_time = time.time() - self.start_time
        accuracy = self.compute_accuracy()
        
        self.stats_display.config(text=f"Correct: {self.correct_answers} | Incorrect: {self.wrong_answers} | "
                                       f"Accuracy: {accuracy:.2f}% | Time: {elapsed_time:.2f}s | "
                                       f"Words Remaining: {remaining_words}")
        
        self.progress_bar["value"] = (self.total_words - remaining_words) / self.total_words * 100

    def validate_input(self, event=None):
        user_input = self.entry_box.get().strip().lower()
        correct_word = self.current_word.strip().lower()
        
        similarity = SequenceMatcher(None, user_input, correct_word).ratio()
        
        if similarity > 0.8:  # Allow for slight typos
            self.correct_answers += 1
            self.entry_box.config(style="Correct.TEntry")
            del self.vocab[self.current_word]
        else:
            self.wrong_answers += 1
            self.entry_box.config(style="Incorrect.TEntry")

        self.master.after(1000, self.reset_entry_style)  # Reset style after 1 second
        self.refresh_display()

    def reset_entry_style(self):
        self.entry_box.config(style="TEntry")

    def reveal_hint(self):
        _, hint = self.vocab[self.current_word]
        revealed = len([c for c in self.hint_label.cget("text") if c != '*'])
        if revealed < len(hint):
            new_hint = hint[:revealed+1] + '*' * (len(hint) - revealed - 1)
            self.hint_label.config(text=f"Hint: {new_hint}")

    def compute_accuracy(self):
        total_attempts = self.correct_answers + self.wrong_answers
        return (self.correct_answers / total_attempts * 100) if total_attempts > 0 else 0

    def end_game(self):
        self.hint_label.config(text="Congratulations! You've completed all words.")
        for widget in (self.prompt_label, self.entry_box, self.verify_button, self.hint_button):
            widget.pack_forget()

def main():
    app = Tk()
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12))
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TEntry", font=("Helvetica", 12))
    style.configure("Correct.TEntry", foreground="green")
    style.configure("Incorrect.TEntry", foreground="red")

    vocab = {
        "Python": "A high-level programming language",
        "Java": "A general-purpose programming language",
        "HTML": "The standard markup language for creating web pages",
        "Algorithm": "A step-by-step procedure for solving a problem",
        "Database": "An organized collection of data stored electronically"
    }

    game_instance = QuizMaster(app, vocab)
    app.mainloop()

if __name__ == "__main__":
    main()
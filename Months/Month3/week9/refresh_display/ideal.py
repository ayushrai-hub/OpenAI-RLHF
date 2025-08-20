import random
import time
from tkinter import Tk, Label, StringVar, ttk, messagebox, IntVar

class QuizMaster:
    def __init__(self, master, vocab):
        self.master = master
        self.vocab = vocab
        self.total_words = len(vocab)
        self.difficulty = StringVar(value="Medium")
        self.time_limit = IntVar(value=0)  # 0 means no time limit

        self.current_word = None
        self.correct_answers = 0
        self.wrong_answers = 0
        self.start_time = time.time()
        self.word_start_time = time.time()

        self.setup_gui()

    def setup_gui(self):
        self.master.title("Enhanced Quiz Master Game")
        self.master.geometry("400x500")

        # Difficulty selector
        ttk.Label(self.master, text="Difficulty:").pack(pady=5)
        ttk.Combobox(self.master, textvariable=self.difficulty, 
                     values=["Easy", "Medium", "Hard"]).pack(pady=5)

        # Time limit entry
        ttk.Label(self.master, text="Time Limit (seconds, 0 for no limit):").pack(pady=5)
        ttk.Entry(self.master, textvariable=self.time_limit).pack(pady=5)

        # Start button
        ttk.Button(self.master, text="Start Game", command=self.start_game).pack(pady=10)

        self.game_frame = ttk.Frame(self.master)
        self.game_frame.pack(fill="both", expand=True)

        self.hint_label = Label(self.game_frame, text="", font=("Helvetica", 14))
        self.hint_label.pack(pady=10)

        self.prompt_label = Label(self.game_frame, text="Type the word:", font=("Helvetica", 12))
        self.prompt_label.pack(pady=5)

        self.input_var = StringVar()
        self.entry_box = ttk.Entry(self.game_frame, textvariable=self.input_var, font=("Helvetica", 12))
        self.entry_box.pack(pady=5)
        self.entry_box.bind("<Return>", self.validate_input)

        self.verify_button = ttk.Button(self.game_frame, text="Verify", command=self.validate_input)
        self.verify_button.pack(pady=5)

        self.stats_display = Label(self.game_frame, text="", font=("Helvetica", 12))
        self.stats_display.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.game_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.game_frame.pack_forget()  # Hide the game frame initially

    def start_game(self):
        self.game_frame.pack(fill="both", expand=True)
        self.refresh_display()

    def select_word(self):
        difficulty_factor = {"Easy": 0.7, "Medium": 1.0, "Hard": 1.3}
        words = list(self.vocab.items())
        words.sort(key=lambda x: len(x[0]) * difficulty_factor[self.difficulty.get()])
        split_point = int(len(words) * 0.7)  # Select from top 70% based on difficulty
        return random.choice(words[:split_point])

    def refresh_display(self):
        if self.vocab:
            self.current_word, hint = self.select_word()
            self.hint_label.config(text=f"Hint: {hint}")
            self.input_var.set("")
            self.word_start_time = time.time()
            self.update_progress_bar()
        else:
            self.end_game()

        remaining_words = len(self.vocab)
        elapsed_time = time.time() - self.start_time
        self.stats_display.config(text=f"Correct: {self.correct_answers} | Incorrect: {self.wrong_answers} | "
                                       f"Accuracy: {self.compute_accuracy():.2f}% | "
                                       f"Time: {elapsed_time:.2f}s | Remaining: {remaining_words}")

    def validate_input(self, event=None):
        from difflib import SequenceMatcher
        user_input = self.entry_box.get().strip().lower()
        correct_word = self.current_word.strip().lower()
        similarity = SequenceMatcher(None, user_input, correct_word).ratio()

        if similarity > 0.8:  # Allow for slight typos
            self.give_feedback("Correct!", "green")
            self.correct_answers += 1
            del self.vocab[self.current_word]
            self.add_score(similarity)
        else:
            self.give_feedback("Incorrect. Try again!", "red")
            self.wrong_answers += 1

        self.refresh_display()

    def give_feedback(self, message, color):
        self.hint_label.config(text=message, fg=color)
        self.master.after(1000, self.refresh_display)  # Reset after 1 second

    def add_score(self, similarity):
        time_taken = time.time() - self.word_start_time
        difficulty_bonus = {"Easy": 1, "Medium": 1.5, "Hard": 2}[self.difficulty.get()]
        score = int((similarity * 100) * difficulty_bonus / time_taken)
        print(f"Word score: {score}")  # You can display this in the GUI if desired

    def compute_accuracy(self):
        total_attempts = self.correct_answers + self.wrong_answers
        return (self.correct_answers / total_attempts * 100) if total_attempts > 0 else 0

    def update_progress_bar(self):
        progress = (self.total_words - len(self.vocab)) / self.total_words * 100
        self.progress_bar["value"] = progress

    def end_game(self):
        self.hint_label.config(text="Congratulations! You've completed all words.", fg="green")
        self.prompt_label.pack_forget()
        self.entry_box.pack_forget()
        self.verify_button.pack_forget()
        messagebox.showinfo("Game Over", f"Final Score: {self.compute_accuracy():.2f}%")

def main():
    app = Tk()
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12))
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TEntry", font=("Helvetica", 12))

    vocab = {
        "Python": "A high-level programming language.",
        "Java": "A general-purpose programming language.",
        "HTML": "The standard markup language for creating web pages.",
        "Algorithm": "A step-by-step procedure for solving a problem.",
        "Database": "An organized collection of data.",
        "Network": "A group of interconnected computers.",
        "Encryption": "The process of encoding information.",
        "Framework": "A platform for developing software applications.",
        "Interface": "A point of interaction between components.",
        "Variable": "A storage location paired with an associated symbolic name."
    }

    game_instance = QuizMaster(app, vocab)
    app.mainloop()

if __name__ == "__main__":
    main()
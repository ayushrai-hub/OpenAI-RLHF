import random

class State:
    def __init__(self, name, on_enter=None):
        self.name = name
        self.on_enter = on_enter

    def enter(self):
        if self.on_enter:
            return self.on_enter()

class StateMachine:
    def __init__(self, initial_state):
        self.current_state = initial_state

    def transition_to(self, next_state):
        self.current_state = next_state
        return self.current_state.enter()

class NumberGuessingGame:
    def __init__(self, min_num=1, max_num=100):
        self.min_num = min_num
        self.max_num = max_num
        self.random_number = random.randint(min_num, max_num)
        self.attempts = 0
        self.max_attempts = 10
        
        self.waiting_for_input_state = State("Waiting for Input", self.get_user_input)
        self.check_guess_state = State("Check Guess", self.check_guess)
        self.end_state = State("End", self.end_game)
        
        self.sm = StateMachine(self.waiting_for_input_state)
        self.user_input = None

    def get_user_input(self):
        self.user_input = input(f"Guess the number between {self.min_num} and {self.max_num} (or type 'quit' to exit): ")
        return self.check_guess_state

    def check_guess(self):
        if self.user_input is None:
            return self.waiting_for_input_state

        self.attempts += 1
        if self.user_input.lower() == 'quit':
            return self.end_state

        try:
            guess = int(self.user_input)
            if guess < self.min_num or guess > self.max_num:
                print(f"Please enter a number between {self.min_num} and {self.max_num}.")
            elif guess == self.random_number:
                print(f"Congratulations! You guessed the correct number in {self.attempts} attempts.")
                return self.end_state
            elif guess < self.random_number:
                print("Your guess is too low.")
            else:
                print("Your guess is too high.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

        if self.attempts >= self.max_attempts:
            print(f"You've reached the maximum number of attempts. The correct number was {self.random_number}.")
            return self.end_state

        return self.waiting_for_input_state

    def end_game(self):
        print("Game Over. Thank you for playing!")
        return None

    def play(self):
        print(f"Welcome to the Number Guessing Game! Try to guess the number between {self.min_num} and {self.max_num}.")
        print(f"You have {self.max_attempts} attempts.")
        next_state = self.sm.current_state
        while next_state:
            next_state = self.sm.transition_to(next_state)

if __name__ == "__main__":
    game = NumberGuessingGame()
    game.play()
import random

class State:
    def __init__(self, name, on_enter=None):
        self.name = name
        self.on_enter = on_enter

    def enter(self):
        if self.on_enter:
            return self.on_enter()

class NumberGuessingGame:
    def __init__(self, min_num: int = 1, max_num: int = 100) -> None:
        self.random_number = random.randint(min_num, max_num)
        self.user_input = None
        self.waiting_for_input_state = State("Waiting for Input", self.get_user_input)
        self.check_guess_state = State("Check Guess", self.check_guess)
        self.end_state = State("End", self.end_game)
        self.state_machine = self.waiting_for_input_state

    def get_user_input(self) -> State:
        self.user_input = input("Guess the number (or type 'quit' to exit): ")
        return self.check_guess_state

    def check_guess(self) -> State:
        if self.user_input.lower() == 'quit':
            return self.end_state
        elif int(self.user_input) == self.random_number:
            print("Congratulations! You guessed the correct number.")
            return self.end_state
        elif int(self.user_input) < self.random_number:
            print("Your guess is too low.")
            return self.waiting_for_input_state
        else:
            print("Your guess is too high.")
            return self.waiting_for_input_state

    def end_game(self) -> None:
        print("Game Over. Thank you for playing!")

    def play(self) -> None:
        while self.state_machine != self.end_state:
            self.state_machine = self.state_machine.enter()

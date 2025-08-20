# Define the quiz questions, options, and correct answers
quiz = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "Rome", "London", "Madrid"],
        "answer": "Paris"
    },
    {
        "question": "What is the capital of Italy?",
        "options": ["Berlin", "Rome", "Madrid", "Lisbon"],
        "answer": "Rome"
    },
    {
        "question": "What is the largest planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "answer": "Jupiter"
    },
    {
        "question": "Which ocean is the largest?",
        "options": ["Atlantic", "Pacific", "Indian", "Arctic"],
        "answer": "Pacific"
    },
    {
        "question": "Who wrote the play 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Leo Tolstoy"],
        "answer": "William Shakespeare"
    },
    {
        "question": "What is the chemical symbol for Gold?",
        "options": ["Go", "Au", "Ag", "Gc"],
        "answer": "Au"
    },
    {
        "question": "What is the square root of 81?",
        "options": ["7", "8", "9", "10"],
        "answer": "9"
    },
    {
        "question": "Which country is known as the Land of Rising Sun?",
        "options": ["China", "Spain", "Japan", "India"],
        "answer": "Japan"
    },
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4"
    },
    {
        "question": "What does HTTP stand for?",
        "options": ["Hyper Tools Transfer Protocol", "Hyper Text Transfer Protocol", "Hyper Theorem Text Protocol", "None of the above"],
        "answer": "Hyper Text Transfer Protocol"
    }
]

correct_count = 0  # To keep track of the number of correct answers

# Iterate over each question in the quiz
for i, q in enumerate(quiz):
    print(f"Question {i + 1}: {q['question']}")
    # Print the options
    for idx, option in enumerate(q['options']):
        print(f"{idx + 1}. {option}")
    # Get the user's answer
    user_answer = input("Your answer (enter the number of the option): ")
    # Check if the user's answer is correct
    try:
        selected_option = int(user_answer)
        if selected_option < 1 or selected_option > len(q['options']):
            print("Invalid option. Please select a valid option.")
        else:
            if q['options'][selected_option - 1] == q['answer']:
                print("Correct!")
                correct_count += 1
            else:
                print(f"Incorrect! The correct answer is: {q['answer']}")
    except ValueError:
        print("Invalid input. Please enter a number.")
    print()  # Blank line for better readability

# After finishing the quiz
print(f"Quiz complete! You got {correct_count} out of {len(quiz)} correct.")

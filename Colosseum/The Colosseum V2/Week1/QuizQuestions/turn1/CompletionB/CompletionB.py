import random

# List of questions, each with a question, options, and the correct answer
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "Rome", "London", "Madrid"],
        "answer": "Paris"
    },
    {
        "question": "What is the capital of Italy?",
        "options": ["Paris", "Rome", "London", "Madrid"],
        "answer": "Rome"
    },
    {
        "question": "What is the capital of Spain?",
        "options": ["Paris", "Rome", "London", "Madrid"],
        "answer": "Madrid"
    },
    {
        "question": "What is the capital of United Kingdom?",
        "options": ["Paris", "Rome", "London", "Madrid"],
        "answer": "London"
    },
    {
        "question": "What is the capital of Japan?",
        "options": ["Tokyo", "Rome", "Beijing", "Seoul"],
        "answer": "Tokyo"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Mars"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "answer": "Pacific"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "Jane Austen", "Shakespeare", "Hemingway"],
        "answer": "Shakespeare"
    },
    {
        "question": "How many continents are there?",
        "options": ["5", "6", "7", "8"],
        "answer": "7"
    },
    {
        "question": "What is the capital of Australia?",
        "options": ["Canberra", "Sydney", "Melbourne", "Perth"],
        "answer": "Canberra"
    }
]

# Shuffle the questions to make the quiz random
random.shuffle(questions)

# Counter for correct answers
correct_answers = 0

# Ask each question to the user
for question in questions:
    print(question["question"])
    for i, option in enumerate(question["options"], 1):
        print(f"{i}. {option}")
    
    user_answer = input("Enter the number of your answer: ")
    
    # Check if the answer is correct
    if question["options"][int(user_answer) - 1] == question["answer"]:
        correct_answers += 1

# Display the final score
print(f"\nYou got {correct_answers} out of {len(questions)} questions correct!")

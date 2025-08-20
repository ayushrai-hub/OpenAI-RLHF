questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "Rome", "London", "Madrid"],
        "answer": "Paris"
    },
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4"
    },
    {
        "question": "Which animal is known as the 'King of the Jungle'?",
        "options": ["Lion", "Elephant", "Tiger", "Bear"],
        "answer": "Lion"
    },
    {
        "question": "Who wrote the play Romeo and Juliet?",
        "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"],
        "answer": "William Shakespeare"
    },
    {
        "question": "What is the largest planet in our solar system?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "answer": "Jupiter"
    },
    {
        "question": "Which gas is essential for human survival?",
        "options": ["Oxygen", "Hydrogen", "Carbon Dioxide", "Nitrogen"],
        "answer": "Oxygen"
    },
    {
        "question": "Who was the first president of the United States?",
        "options": ["Thomas Jefferson", "Abraham Lincoln", "George Washington", "John Adams"],
        "answer": "George Washington"
    },
    {
        "question": "What is the chemical symbol for water?",
        "options": ["O2", "H2O", "CO2", "NaCl"],
        "answer": "H2O"
    },
    {
        "question": "Which country is known as the Land of the Rising Sun?",
        "options": ["China", "Japan", "South Korea", "Thailand"],
        "answer": "Japan"
    },
    {
        "question": "What is the process called when a liquid turns into gas?",
        "options": ["Condensation", "Evaporation", "Melting", "Freezing"],
        "answer": "Evaporation"
    }
]

correct_answers = 0

for q in questions:
    print(f"Q: {q['question']}")
    for idx, option in enumerate(q['options'], 1):
        print(f"{idx}. {option}")
    user_answer = input("Your answer (enter the option number): ")
    try:
        user_answer = int(user_answer)
        if q['options'][user_answer - 1] == q['answer']:
            print("Correct!")
            correct_answers += 1
        else:
            print(f"Incorrect. The correct answer is: {q['answer']}")
    except (ValueError, IndexError):
        print(f"Invalid input. The correct answer is: {q['answer']}")
    print()

print(f"Quiz completed! You got {correct_answers} out of {len(questions)} correct answers.")

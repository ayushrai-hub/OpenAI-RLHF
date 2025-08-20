questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "Rome", "London", "Madrid"],
        "answer": "Paris"
    },
    {
        "question": "What is the capital of Italy?",
        "options": ["Berlin", "Rome", "Madrid", "Tokyo"],
        "answer": "Rome"
    },
    {
        "question": "What is the capital of Japan?",
        "options": ["Beijing", "Seoul", "Tokyo", "Bangkok"],
        "answer": "Tokyo"
    },
    {
        "question": "What is the capital of Spain?",
        "options": ["Lisbon", "Paris", "Madrid", "Berlin"],
        "answer": "Madrid"
    },
    {
        "question": "What is the capital of Germany?",
        "options": ["Vienna", "Berlin", "Zurich", "Oslo"],
        "answer": "Berlin"
    },
    {
        "question": "What is the capital of Australia?",
        "options": ["Sydney", "Melbourne", "Canberra", "Perth"],
        "answer": "Canberra"
    },
    {
        "question": "What is the capital of Canada?",
        "options": ["Toronto", "Vancouver", "Ottawa", "Montreal"],
        "answer": "Ottawa"
    },
    {
        "question": "What is the capital of Brazil?",
        "options": ["Santiago", "Lima", "Brasília", "Buenos Aires"],
        "answer": "Brasília"
    },
    {
        "question": "What is the capital of Russia?",
        "options": ["Moscow", "Saint Petersburg", "Novosibirsk", "Irkutsk"],
        "answer": "Moscow"
    },
    {
        "question": "What is the capital of India?",
        "options": ["Mumbai", "Chennai", "Delhi", "Kolkata"],
        "answer": "Delhi"
    }
]

correct_answers = 0

for q in questions:
    print(q["question"])
    for i, option in enumerate(q["options"], 1):
        print(f"{i}. {option}")
    answer = input("Your answer: ")
    if answer.strip().lower() == q["answer"].lower():
        correct_answers += 1

print(f"You got {correct_answers} out of {len(questions)} correct!")


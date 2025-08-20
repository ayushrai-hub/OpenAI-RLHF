def average_marks():
    marks = []
    for i in range(5):
        mark = float(input(f"Enter mark for subject {i+1}: "))
        marks.append(mark)
    average = sum(marks) / len(marks)
    print("The average mark is:", average)
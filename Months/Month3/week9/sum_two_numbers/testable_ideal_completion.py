
import math

def sum_two_numbers():
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))
    sum = num1 + num2
    print("The sum of {} and {} is {}".format(num1, num2, sum))

def calculate_circle_area():
    radius = float(input("Enter the radius of the circle: "))
    area = math.pi * (radius ** 2)
    print("The area of the circle with radius {} is {:.2f}".format(radius, area))

def sum_of_digits():
    number = int(input("Enter a number: "))
    sum_of_digits = 0
    while number > 0:
        digit = number % 10
        sum_of_digits += digit
        number //= 10
    print("The sum of digits is:", sum_of_digits)

def expression_evaluation():
    result = 2 + 4**2 / 4 - (5 - 3)
    print("The result of the expression is:", result)

def type_conversion():
    int_value = 5
    float_value = 7.5
    int_to_float = float(int_value)
    float_to_int = int(float_value)
    print("Integer to float:", int_to_float)
    print("Float to integer:", float_to_int)

def average_marks():
    marks = []
    for i in range(5):
        mark = float(input(f"Enter mark for subject {i+1}: "))
        marks.append(mark)
    average = sum(marks) / len(marks)
    print("The average mark is:", average)

def salary_promotion():
    initial_salary = 35000
    increment = 10 / 100
    new_salary = initial_salary + (initial_salary * increment)
    print("The current salary after promotion is:", new_salary)

def maximum_of_three():
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))
    num3 = float(input("Enter third number: "))
    maximum = max(num1, num2, num3)
    print("The maximum of the three numbers is:", maximum)

def data_type_identification():
    user_input = input("Enter something: ")
    if user_input.isdigit():
        data_type = "integer"
    elif user_input.replace('.', '', 1).isdigit() and user_input.count('.') < 2:
        data_type = "float"
    else:
        data_type = "string"
    print("The data type of the input is:", data_type)

def implicit_explicit_conversion():
    num_int = 10
    num_float = 12.5
    result = num_int + num_float
    print("Result after implicit type conversion:", result)
    print("Data type of result:", type(result))
    num_str = "123"
    num_str_to_int = int(num_str)
    print("Result after explicit type conversion:", num_str_to_int)
    print("Data type of result:", type(num_str_to_int))

def arithmetic_operators():
    a = 10
    b = 3
    print("Addition:", a + b)
    print("Subtraction:", a - b)
    print("Multiplication:", a * b)
    print("Division:", a / b)
    print("Modulus:", a % b)
    print("Exponentiation:", a ** b)
    print("Floor Division:", a // b)

def comparative_logical_operators():
    a = 5
    b = 10
    c = 5
    print("a == b:", a == b)
    print("a != b:", a != b)
    print("a > c:", a > c)
    print("a < b:", a < b)
    print("a >= c:", a >= c)
    print("a <= b:", a <= b)
    print("a == c and b > c:", a == c and b > c)
    print("a == b or b > a:", a == b or b > a)
    print("not a == b:", not a == b)

def assignment_bitwise_operators():
    a = 10
    a += 5
    print("a after a += 5:", a)
    a &= 6
    print("a after a &= 6:", a)

def membership_identity_operators():
    lst = [1, 2, 3, 4]
    print("Is 3 in the list?", 3 in lst)
    print("Is 5 not in the list?", 5 not in lst)
    x = 5
    y = 5
    print("x is y:", x is y)
    print("x is not y:", x is not y)

if __name__ == "__main__":
    sum_two_numbers()
    calculate_circle_area()
    sum_of_digits()
    expression_evaluation()
    type_conversion()
    average_marks()
    salary_promotion()
    maximum_of_three()
    data_type_identification()
    implicit_explicit_conversion()
    arithmetic_operators()
    comparative_logical_operators()
    assignment_bitwise_operators()
    membership_identity_operators()

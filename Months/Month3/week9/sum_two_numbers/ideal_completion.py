#ideal_completion.py

import math
# 1. Script to sum two user-input numbers
def sum_two_numbers():
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    # Calculate sum
    sum = num1 + num2

    #show the sum
    print(f"The sum of {num1} and {num2} is {sum}")

    #Expected Output:
    """
    The sum of 5.0 and 3.0 is 8.0
    """

#2. Area of a Circle
import math
def calculate_circle_area():


    # Script to compute a circle's area
    radius = float(input())

    # Compute area
    area = math.pi * (radius ** 2)

    # Show the area
    print(f"The area of the circle with radius {radius:.1f} is {area:.2f}")

    #Expected Output:
    """
    The area of the circle with radius 5.0 is 78.54
    """
# 3. Script to sum digits of a specified number
def sum_of_digits():
    number = int(input())
    sum_of_digits = sum(int(digit) for digit in str(number))

    # Show the digit sum
    print("The sum of digits is:", sum_of_digits)

    #Expected Output:
    """
    The sum of digits is: 6
    """
# 4. Script to evaluate the expression
def expression_evaluation():
    
    result = 2 + 4**2 / 4 - (5 - 3)

    # Show the result
    print("The result of the expression is:", result)

    #Expected Output:
    """
    The result of the expression is: 4.0
    """
# 5. Script to switch between int and float
def type_conversion():
    int_value = 5
    float_value = 7.5

    # Convert types
    int_to_float = float(int_value)
    float_to_int = int(float_value)

    # Show conversions
    print("Integer to float:", int_to_float)
    print("Float to integer:", float_to_int)

    #Expected Output:
    """
    Integer to float: 5.0\nFloat to integer: 7
    """
# 6. Script to compute the average of marks in five subjects
def average_marks():
    marks = []
    for i in range(5):
        mark = float(input())
        marks.append(mark)

    average = sum(marks) / len(marks)

    # Show the average
    print(f"The average mark is: {average:.1f}")

    #Expected Output:
    """
    The average mark is: 85.0
    """
# 7. Script to compute the new salary post-promotion
def salary_promotion(): 
    initial_salary = 35000
    increment = 10 / 100

    # Compute new salary
    new_salary = initial_salary + (initial_salary * increment)

    # Show the new salary
    print("The current salary after promotion is:", new_salary)

    #Expected Output:
    """
    The current salary after promotion is: 38500.0
    """
# 8. Script to determine the maximum of three numbers
def maximum_of_three():
    num1 = float(input())
    num2 = float(input())
    num3 = float(input())

    # Determine maximum
    maximum = max(num1, num2, num3)

  
    print(f"The maximum of the three numbers is: {maximum}")

    #Expected Output:
    """
    The maximum of the three numbers is: 20.0
    """
# 9. Script to determine the data type of a given input
def data_type_identification():
    user_input = input()

    # Identify data type
    if user_input.isdigit():
        data_type = "integer"
    elif user_input.replace('.', '', 1).isdigit() and user_input.count('.') == 1:
        data_type = "float"
    else:
        data_type = "string"

    # Show data type
    print("The data type of the input is:", data_type)

    #Expected Output:
    """
    The data type of the input is: integers
    """
# 10. Implicit type conversion
def implicit_explicit_conversion():
    num_int = 10
    num_float = 12.5

    # Add integer and float
    result = num_int + num_float
    print("Result after implicit type conversion:", result)
    print("Data type of result:", type(result))

    # Explicit type conversion
    num_str = "123"
    num_str_to_int = int(num_str)

    print("Result after explicit type conversion:", num_str_to_int)
    print("Data type of result:", type(num_str_to_int))
    #Expected Output:
    """
    Result after implicit type conversion: 22.5
    Data type of result: <class 'float'>
    Result after explicit type conversion: 123
    Data type of result: <class 'int'>
    """
# 11. Script depicting various arithmetic operators
def arithmetic_operators():
    a = 10
    b = 3

    # Addition
    print("Addition:", a + b)

    # Subtraction
    print("Subtraction:", a - b)

    # Multiplication
    print("Multiplication:", a * b)

    # Division
    print("Division:", a / b)

    # Modulus
    print("Modulus:", a % b)

    # Exponentiation
    print("Exponentiation:", a ** b)

    # Floor Division
    print("Floor Division:", a // b)
    #Expected Output:
    """
    Addition: 13
    Subtraction: 7
    Multiplication: 30
    Division: 3.3333333333333335
    Modulus: 1
    Exponentiation: 1000
    Floor Division: 3
    """
# 12. Comparative and Logical Operators in Python 
def comparative_logical_operators():
    a = 5
    b = 10
    c = 5

    # Comparative operators
    print("a == b:", a == b)
    print("a != b:", a != b)
    print("a > c:", a > c)
    print("a < b:", a < b)
    print("a >= c:", a >= c)
    print("a <= b:", a <= b)

    # Logical operators
    print("a == c and b > c:", a == c and b > c)
    print("a == b or b > a:", a == b or b > a)
    print("not a == b:", not a == b)
    #Expected Output:
    """
    a == b: False
    a != b: True
    a > c: False
    a < b: True
    a >= c: True
    a <= b: True
    a == c and b > c: True
    a == b or b > a: True
    not a == b: True
    """
# 13. Assignment operators and Bitwise operators
def assignment_bitwise_operators():
    #Assignment operators
    x = 10
    print(f"Initial x: {x}")

    x += 5
    print(f"After x += 5: {x}")

    x -= 3
    print(f"After x -= 3: {x}")

    x *= 2
    print(f"After x *= 2: {x}")

    x /= 4
    print(f"After x /= 4: {x}")

    #Bitwise operators
    a, b = 60, 13  # 60 = 0011 1100, 13 = 0000 1101

    print(f"a & b: {a & b}")   # AND
    print(f"a | b: {a | b}")   # OR
    print(f"a ^ b: {a ^ b}")   # XOR
    print(f"~a: {~a}")         # NOT
    print(f"a << 2: {a << 2}") # Left shift
    print(f"a >> 2: {a >> 2}") # Right shift

    #Expected Output:
    """
    #Assignment operators
    Initial x: 10
    After x += 5: 15
    After x -= 3: 12
    After x *= 2: 24
    After x /= 4: 6.0

    #Bitwise operators
    a & b: 12
    a | b: 61
    a ^ b: 49
    ~a: -61
    a << 2: 240
    a >> 2: 15
    """

# 14. Membership operators and Identity operators
def membership_identity_operators(): 
    #Membership operators
    fruits = ["apple", "banana", "cherry"]

    print(f"'banana' in fruits: {'banana' in fruits}")
    print(f"'grape' in fruits: {'grape' in fruits}")
    print(f"'pear' not in fruits: {'pear' not in fruits}")

    #Identity operators
    x = [1, 2, 3]
    y = [1, 2, 3]
    z = x

    print(f"x is z: {x is z}")
    print(f"x is y: {x is y}")
    print(f"x is not y: {x is not y}")

    #Expected Output:
    """
    #Membership operators
    'banana' in fruits: True
    'grape' in fruits: False
    'pear' not in fruits: True

    #Identity operators
    x is z: True
    x is y: False
    x is not y: True
    """

if __name__ == "__main__":
    # Your original script execution here
    sum_two_numbers(), 
    calculate_circle_area(), sum_of_digits(), expression_evaluation(),
    type_conversion(), average_marks(), salary_promotion(),
    maximum_of_three(), data_type_identification(), implicit_explicit_conversion(),
    arithmetic_operators(), comparative_logical_operators(),
    assignment_bitwise_operators(), membership_identity_operators()



"""# Script to sum two user-input numbers
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

# Calculate sum
sum = num1 + num2

# Show the sum
print("The sum of {} and {} is {}".format(num1, num2, sum))
"""

"""import math

# Script to compute a circle's area
radius = float(input("Enter the radius of the circle: "))

# Compute area
area = math.pi * (radius ** 2)

# Show the area
print("The area of the circle with radius {} is {:.2f}".format(radius, area))
"""




"""# Script to sum digits of a specified number
number = int(input("Enter a number: "))
sum_of_digits = 0

# Calculate sum of digits
while number > 0:
    digit = number % 10
    sum_of_digits += digit
    number //= 10

# Show the digit sum
print("The sum of digits is:", sum_of_digits)"""


"""# Script to evaluate the expression
result = 2 + 4**2 / 4 - (5 - 3)

# Show the result
print("The result of the expression is:", result)"""


"""

# Script to switch between int and float
int_value = 5
float_value = 7.5

# Convert types
int_to_float = float(int_value)
float_to_int = int(float_value)

# Show conversions
print("Integer to float:", int_to_float)
print("Float to integer:", float_to_int)
"""

"""# Script to compute the average of marks in five subjects
marks = []
for i in range(5):
    mark = float(input(f"Enter mark for subject {i+1}: "))
    marks.append(mark)

average = sum(marks) / len(marks)

# Show the average
print("The average mark is:", average)
"""

"""# Script to compute the new salary post-promotion
initial_salary = 35000
increment = 10 / 100

# Compute new salary
new_salary = initial_salary + (initial_salary * increment)

# Show the new salary
print("The current salary after promotion is:", new_salary)"""


"""# Script to determine the maximum of three numbers
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))
num3 = float(input("Enter third number: "))

# Determine maximum
maximum = max(num1, num2, num3)

# Show the maximum number
print("The maximum of the three numbers is:", maximum)"""

"""# Script to determine the data type of a given input
user_input = input("Enter something: ")

# Identify data type
if user_input.isdigit():
    data_type = "integer"
elif user_input.replace('.', '', 1).isdigit() and user_input.count('.') < 2:
    data_type = "float"
else:
    data_type = "string"

# Show data type
print("The data type of the input is:", data_type)"""

"""# Implicit type conversion
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
print("Data type of result:", type(num_str_to_int))"""


"""# Script depicting various arithmetic operators
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
"""

"""a = 5
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
print("not a == b:", not a == b)"""


# Script to evaluate the expression
result = 2 + 4**2 / 4 - (5 - 3)

# Show the result
print("The result of the expression is:", result)




































































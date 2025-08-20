import unittest
import math
from io import StringIO
import sys
from unittest.mock import patch

# Import functions from the original script
from testable_ideal_completion import (
    sum_two_numbers, calculate_circle_area, expression_evaluation, sum_of_digits,
    type_conversion, average_marks, salary_promotion, implicit_explicit_conversion,
    data_type_identification, assignment_bitwise_operators, assignment_bitwise_operators, 
    membership_identity_operators, maximum_of_three, arithmetic_operators, comparative_logical_operators)


class TestIdealCompletion(unittest.TestCase):
    def capture_output(self, func):
        held_output = StringIO()
        sys.stdout = held_output
        try:
            func()
        finally:
            sys.stdout = sys.__stdout__
        return held_output.getvalue().strip()
    # 1. Script to sum two user-input numbers
    def test_sum_two_numbers(self):
        with patch('builtins.input', side_effect=['5', '3']):
            output = self.capture_output(sum_two_numbers)
        self.assertEqual(output, "The sum of 5.0 and 3.0 is 8.0")
    #2. Area of a Circle
    def test_calculate_circle_area(self):
        with patch('builtins.input', return_value='5'):
            output = self.capture_output(calculate_circle_area)
        self.assertEqual(output, "The area of the circle with radius 5.0 is 78.54")
    # 3. Script to sum digits of a specified number
    def test_sum_of_digits(self):
        with patch('builtins.input', return_value='123'):
            output = self.capture_output(sum_of_digits)
        self.assertEqual(output, "The sum of digits is: 6")
    # 4. Script to evaluate the expression
    def test_expression_evaluation(self):
        output = self.capture_output(expression_evaluation)
        self.assertEqual(output, "The result of the expression is: 4.0")
    # 5. Script to switch between int and float
    def test_type_conversion(self):
        output = self.capture_output(type_conversion)
        self.assertEqual(output, "Integer to float: 5.0\nFloat to integer: 7")
    # 6. Script to compute the average of marks in five subjects
    def test_average_marks(self):
        with patch('builtins.input', side_effect=['85', '90', '75', '80', '95']):
            output = self.capture_output(average_marks)
        self.assertEqual(output, "The average mark is: 85.0")
    # 7. Script to compute the new salary post-promotion
    def test_salary_promotion(self):
        output = self.capture_output(salary_promotion)
        self.assertEqual(output, "The current salary after promotion is: 38500.0")
    # 8. Script to determine the maximum of three numbers
    def test_maximum_of_three(self):
        with patch('builtins.input', side_effect=['10', '20', '15']):
            output = self.capture_output(maximum_of_three)
        self.assertEqual(output, "The maximum of the three numbers is: 20.0")
    # 9. Script to determine the data type of a given input
    def test_data_type_identification(self):
        with patch('builtins.input', return_value='123'):
            output = self.capture_output(data_type_identification)
        self.assertEqual(output, "The data type of the input is: integer")
    # 10. Implicit type conversion
    def test_implicit_explicit_conversion(self):
        output = self.capture_output(implicit_explicit_conversion)
        expected_output = "Result after implicit type conversion: 22.5\n" \
                          "Data type of result: <class 'float'>\n" \
                          "Result after explicit type conversion: 123\n" \
                          "Data type of result: <class 'int'>"
        self.assertEqual(output, expected_output)
    # 11. Script depicting various arithmetic operators
    def test_arithmetic_operators(self):
        output = self.capture_output(arithmetic_operators)
        expected_output = "Addition: 13\n" \
                          "Subtraction: 7\n" \
                          "Multiplication: 30\n" \
                          "Division: 3.3333333333333335\n" \
                          "Modulus: 1\n" \
                          "Exponentiation: 1000\n" \
                          "Floor Division: 3"
        self.assertEqual(output, expected_output)
    # 12. Comparative and Logical Operators in Python 
    def test_comparative_logical_operators(self):
        output = self.capture_output(comparative_logical_operators)
        expected_output = "a == b: False\n" \
                          "a != b: True\n" \
                          "a > c: False\n" \
                          "a < b: True\n" \
                          "a >= c: True\n" \
                          "a <= b: True\n" \
                          "a == c and b > c: True\n" \
                          "a == b or b > a: True\n" \
                          "not a == b: True"
        self.assertEqual(output, expected_output)
    # 13. Assignment operators and Bitwise operators
    def test_assignment_bitwise_operators(self):
        output = self.capture_output(assignment_bitwise_operators)
        expected_output = "Initial x: 10\n" \
                          "After x += 5: 15\n" \
                          "After x -= 3: 12\n" \
                          "After x *= 2: 24\n" \
                          "After x /= 4: 6.0\n" \
                          "a & b: 12\n" \
                          "a | b: 61\n" \
                          "a ^ b: 49\n" \
                          "~a: -61\n" \
                          "a << 2: 240\n" \
                          "a >> 2: 15"
        self.assertEqual(output, expected_output)
    # 14. Membership operators and Identity operators
    def test_membership_identity_operators(self):
        output = self.capture_output(membership_identity_operators)
        expected_output = "'banana' in fruits: True\n" \
                          "'grape' in fruits: False\n" \
                          "'pear' not in fruits: True\n" \
                          "x is z: True\n" \
                          "x is y: False\n" \
                          "x is not y: True"
        self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main(verbosity=2)
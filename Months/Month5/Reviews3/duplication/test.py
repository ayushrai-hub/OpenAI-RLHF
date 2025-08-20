import unittest
from TestableIC import ensure_correct_format, extract_code
import re

# Defining example code_graph for testing
code_graph = '''"import pandas as pd
import plotly.express as px

def create\\_chart(data):
data.rename(columns={'field\\_name:Type': 'Type', 'sample\\_amount:0': 'grand\\_total'}, inplace=True)

plot = px.pie(data, values='grand\\_total', names='Type',
color\\_discrete\\_map=fetch\\_color\\_scheme())
plot.update\\_layout(title='Share of grand\\_total by Type')
plot.update\\_traces(textposition='inside', textinfo='percent+label')
return plot

def fetch\\_color\\_scheme():
return {'Electronics': 'green', 'Home': 'purple'}

plot = create\\_chart(data)"'''

class TestEnsureCorrectFormat(unittest.TestCase):

    def test_format_basic(self):
        # Test formatting of a basic function with a return statement and variable assignment.
        input_code = """def my_function():
data = {'key': 'value'}
return data
returned_data=my_function()"""
        expected_output = """def my_function():
    data = {'key': 'value'}
    return data
returned_data=my_function()"""
        self.assertEqual(ensure_correct_format(input_code), expected_output)

    def test_format_with_multiple_functions(self):
        # Test formatting for code with multiple functions and multiple outer level statements.
        input_code = """import os
def first_function():
return os.getcwd()
def second_function():
return 'Second function'
cwd = first_function()
print('End of code!')"""
        expected_output = """import os
def first_function():
    return os.getcwd()
def second_function():
    return 'Second function'
cwd = first_function()
print('End of code!')"""
        self.assertEqual(ensure_correct_format(input_code), expected_output)
    
    def test_extract_code(self):
        # Test code extraction and backslash removal from a provided code string (code_graph).
        expected_snippet = """import pandas as pd
import plotly.express as px

def create_chart(data):
data.rename(columns={'field_name:Type': 'Type', 'sample_amount:0': 'grand_total'}, inplace=True)

plot = px.pie(data, values='grand_total', names='Type',
color_discrete_map=fetch_color_scheme())
plot.update_layout(title='Share of grand_total by Type')
plot.update_traces(textposition='inside', textinfo='percent+label')
return plot

def fetch_color_scheme():
return {'Electronics': 'green', 'Home': 'purple'}

plot = create_chart(data)"""
        self.assertEqual(extract_code(code_graph), expected_snippet)

    def test_existing_code_graph(self):
        # Test formatting for the extracted and tidied `code_graph` input.
        expected_output = """import pandas as pd
import plotly.express as px

def create_chart(data):
    data.rename(columns={'field_name:Type': 'Type', 'sample_amount:0': 'grand_total'}, inplace=True)

    plot = px.pie(data, values='grand_total', names='Type',
    color_discrete_map=fetch_color_scheme())
    plot.update_layout(title='Share of grand_total by Type')
    plot.update_traces(textposition='inside', textinfo='percent+label')
    return plot

def fetch_color_scheme():
    return {'Electronics': 'green', 'Home': 'purple'}

plot = create_chart(data)"""
        snippet = extract_code(code_graph)
        self.assertEqual(ensure_correct_format(snippet), expected_output)

if __name__ == '__main__':
    unittest.main(verbosity=2)

import unittest
import json
import os
import re
from ideal_completion import store_all_categories


class TestPythonCode(unittest.TestCase):
    def test_total_number_of_lines(self):
        # This test aims to verify by a simple criteria if the solution has chances
        # to be correct: the number of line can be calculated easily if the dictionaries
        # occupe only one line, so if the expected number doesn't match, the solution
        # is automatically incorrect
        category_list = {
            "pizza": [
                {"dish_name": "pizza", "dish_price": "185", "row": 0, "column": 0},
                {"dish_name": "abdc", "dish_price": "xyz", "row": 0, "column": 1},
                {"dish_name": "lmno", "dish_price": "stu", "row": 0, "column": 2},
                {"dish_name": "pqrs", "dish_price": "tuv", "row": 1, "column": 0}
            ],
            "soup": [
                {"dish_name": "Soup", "dish_price": "320", "row": 0, "column": 0},
                {"dish_name": "ijkl", "dish_price": "mnop", "row": 0, "column": 1},
                {"dish_name": "qrst", "dish_price": "uvwx", "row": 0, "column": 2},
                {"dish_name": "yza", "dish_price": "bcd", "row": 1, "column": 0}
            ]
        }
        store_all_categories(category_list)
        with open('category_data.json') as f:
            lines = f.read().split('\n')
        os.remove('category_data.json')
        result = len(lines)
        expected_result = 14
        self.assertEqual(result, expected_result)

    def test_inner_content(self):
        # This test checks if the inner content (i.e. the dictionaries) are indented
        # correctly
        category_list = {
            "pizza": [
                {"dish_name": "pizza", "dish_price": "185", "row": 0, "column": 0},
                {"dish_name": "abdc", "dish_price": "xyz", "row": 0, "column": 1},
                {"dish_name": "lmno", "dish_price": "stu", "row": 0, "column": 2},
                {"dish_name": "pqrs", "dish_price": "tuv", "row": 1, "column": 0}
            ],
            "soup": [
                {"dish_name": "Soup", "dish_price": "320", "row": 0, "column": 0},
                {"dish_name": "ijkl", "dish_price": "mnop", "row": 0, "column": 1},
                {"dish_name": "qrst", "dish_price": "uvwx", "row": 0, "column": 2},
                {"dish_name": "yza", "dish_price": "bcd", "row": 1, "column": 0}
            ]
        }
        store_all_categories(category_list)
        with open('category_data.json') as f:
            text = f.read()
        os.remove('category_data.json')
        results = []
        for category in category_list.values():
            for item in category:
                inner_dict = json.dumps(item).replace(
                    "dish_name", "food_item").replace(
                    "dish_price", "price").replace(
                    "row", "position_row").replace(
                    "column", "position_col")
                results.append(inner_dict in text)
        self.assertTrue(all(results))

    def test_outer_content(self):
        # This test checks if the outer content (i.e. the the rest of the structure,
        # except the dictionaries) are indented correctly
        category_list = {
            "pizza": [
                {"dish_name": "pizza", "dish_price": "185", "row": 0, "column": 0},
                {"dish_name": "abdc", "dish_price": "xyz", "row": 0, "column": 1},
                {"dish_name": "lmno", "dish_price": "stu", "row": 0, "column": 2},
                {"dish_name": "pqrs", "dish_price": "tuv", "row": 1, "column": 0}
            ],
            "soup": [
                {"dish_name": "Soup", "dish_price": "320", "row": 0, "column": 0},
                {"dish_name": "ijkl", "dish_price": "mnop", "row": 0, "column": 1},
                {"dish_name": "qrst", "dish_price": "uvwx", "row": 0, "column": 2},
                {"dish_name": "yza", "dish_price": "bcd", "row": 1, "column": 0}
            ]
        }
        store_all_categories(category_list)
        with open('category_data.json') as f:
            text = f.read()
        os.remove('category_data.json')
        inner_strings = re.findall(r'{(?:\s|.)+?}', text[1:-1])
        for i in inner_strings:
            text = text.replace(i, 'null')
        ref_dict = {}
        for c_name, category in category_list.items():
            ref_dict[c_name] = [None] * len(category)
        ref_text = json.dumps(ref_dict, indent=4)
        self.assertEqual(text, ref_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
import unittest
# Import the function to be tested
from ideal_completion import filter_people_by_age

class TestFilterPeopleByAge(unittest.TestCase):

    def test_filter_people_by_age_above_threshold_success(self):
        # Test with multiple people, all above the age threshold
        # This test ensures that if all people are above the threshold, the function correctly includes them.
        collection = [
            {"name": "Anna", "age": 35},
            {"name": "Bob", "age": 50},
            {"name": "Cathy", "age": 45}
        ]
        self.assertEqual(
            filter_people_by_age(collection, 30),
            [
                {"name": "Anna", "age": 35},
                {"name": "Bob", "age": 50},
                {"name": "Cathy", "age": 45}
            ]
        )

    def test_filter_people_by_age_below_threshold_success(self):
        # Test with multiple people, all below the age threshold
        # This test verifies that if all ages are below the threshold, none of them are included in the result.
        collection = [
            {"name": "Anna", "age": 25},
            {"name": "Bob", "age": 20},
            {"name": "Cathy", "age": 18}
        ]
        self.assertEqual(
            filter_people_by_age(collection, 30),
            []
        )

    def test_filter_people_by_age_mixed_success(self):
        # Test with a mix of people above and below the age threshold
        # This test checks that the function correctly includes only the people with ages greater than the threshold,
        # while excluding those who are equal to or below the threshold.
        collection = [
            {"name": "Anna", "age": 28},
            {"name": "Dave", "age": 32},
            {"name": "Ella", "age": 40}
        ]
        self.assertEqual(
            filter_people_by_age(collection, 30),
            [
                {"name": "Dave", "age": 32},
                {"name": "Ella", "age": 40}
            ]
        )

    def test_filter_people_by_age_no_age_key_success(self):
        # Test with people missing the 'age' key in their dictionary
        # This test is crucial because it ensures that the function can handle cases where some dictionaries do not
        # have an 'age' key without raising errors, and only considers people with a valid 'age' key.
        collection = [
            {"name": "Anna"},
            {"name": "Bob", "age": 35},
            {"name": "Cathy"}
        ]
        self.assertEqual(
            filter_people_by_age(collection, 30),
            [
                {"name": "Bob", "age": 35}
            ]
        )

    def test_filter_people_by_age_edge_cases(self):
        """Test edge cases with various age values."""
        collection = [
            {"name": "A", "age": -1},          # Negative age
            {"name": "B", "age": 0},           # Zero age
            {"name": "C", "age": 30.5},        # Float age
            {"name": "D", "age": 999999},      # Very large age
            {"name": "E", "age": "30"},        # String age
            {"name": "F", "age": True},        # Boolean age
        ]
        result = filter_people_by_age(collection, 30)
        # Should only include valid numeric ages > 30
        self.assertTrue(all(isinstance(person["age"], (int, float)) 
                          and person["age"] > 30 for person in result))
        
    def test_filter_people_by_age_none_values_success(self):
        # Test with people having None values for the 'age' key This test verifies that entries with `None` values
        # for 'age' are excluded, as `None` should not be treated as a valid age.
        collection = [
            {"name": "Anna", "age": 0},
            {"name": "Bob", "age": 35},
            {"name": "Cathy", "age": None}
        ]
        self.assertEqual(
            filter_people_by_age(collection, 30),
            [
                {"name": "Bob", "age": 35}
            ]
        )

    def test_filter_people_by_age_empty_collection_success(self):
        # Test with an empty collection
        # This test ensures that the function correctly handles an empty input collection and returns an empty list.
        # It verifies that the function does not raise any errors or exceptions when given an empty input.
        collection = []
        self.assertEqual(
            filter_people_by_age(collection, 30),
            []
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)


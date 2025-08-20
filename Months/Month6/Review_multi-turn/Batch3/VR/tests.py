import unittest
from ideal_compleiton import VR_Pain_Points
import random

class TestVRPainPoints(unittest.TestCase):

    def test_pain_point_keys(self):
        # Test that all expected pain point categories are present
        expected_keys = [
            "High Initial Investment",
            "Insufficient Content and Cases",
            "Integration Complexity",
            "User Discomfort and Strain",
            "Rapid Technological Changes",
            "Small User Population",
            "Bandwidth and Lag Problems",
            "Privacy and Data Safety Worries",
            "Employee Reluctance to New Tech",
            "Incompatibility with Existing Systems"
        ]
        self.assertCountEqual(list(VR_Pain_Points.keys()), expected_keys)

    def test_sub_keys(self):
        # Test that each pain point has 'Description', 'Why_its_a_pain_point', 'How_to_address'
        for pain_point in VR_Pain_Points.values():
            self.assertIn('Description', pain_point)
            self.assertIn('Why_its_a_pain_point', pain_point)
            self.assertIn('How_to_address', pain_point)

    def test_types(self):
        # Test that 'Description' and 'How_to_address' are strings, 'Why_its_a_pain_point' is a list of strings
        for pain_point in VR_Pain_Points.values():
            self.assertIsInstance(pain_point['Description'], str)
            self.assertIsInstance(pain_point['How_to_address'], str)
            self.assertIsInstance(pain_point['Why_its_a_pain_point'], list)
            for item in pain_point['Why_its_a_pain_point']:
                self.assertIsInstance(item, str)

    def test_random_key_content(self):
        # Randomly verify specific content matches expected values
        tests = [
            {
                "key": "High Initial Investment",
                "field": "Description",
                "expected": "The expense of top-tier VR hardware and the necessary setup can be a significant hurdle, particularly for companies wary of funding new technologies."
            },
            {
                "key": "User Discomfort and Strain",
                "field": "How_to_address",
                "expected": "Highlight VR advancements that reduce discomfort, like enhanced frame rates and ergonomic designs. If possible, provide demos for potential buyers to firsthand experience the improved comfort in the technology."
            },
            {
                "key": "Privacy and Data Safety Worries",
                "field": "Why_its_a_pain_point",
                "expected": [
                    "Complex data safety laws.",
                    "Risk of breaches involving sensitive data.",
                    "Growing user concerns regarding privacy."
                ]
            }
        ]

        for test in tests:
            key = test["key"]
            field = test["field"]
            expected = test["expected"]
            self.assertEqual(VR_Pain_Points[key][field], expected)

if __name__ == "__main__":
    unittest.main(verbosity=2)

import unittest
from TestableIC import sentences

class TestPetSentences(unittest.TestCase):
    
    def test_sentence_count(self):
        """Test to check that the sentence list contains 300 items"""
        self.assertEqual(len(sentences), 300, "The list should contain 300 sentences.")

    def test_sentence_content(self):
        """Test that all sentences are strings"""
        for sentence in sentences:
            self.assertIsInstance(sentence, str, f"Each sentence should be a string, but got {type(sentence)}.")


# Run the tests
if __name__ == "__main__":
    unittest.main(verbosity=2)

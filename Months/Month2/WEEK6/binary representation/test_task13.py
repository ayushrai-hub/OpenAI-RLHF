import unittest
from task13 import generate_sequence
class TestSequenceGeneration(unittest.TestCase):
    def test_generate_sequence(self):
        sequence = generate_sequence(32)
        self.assertEqual(len(sequence), 32)
        self.assertEqual(sequence[0], ('0', 0))
        self.assertEqual(sequence[1], ('1', 1))
        self.assertEqual(sequence[15], ('1', 1))
        self.assertEqual(sequence[31], ('1', 1))

    def test_edge_cases(self):
        self.assertEqual(generate_sequence(0), [])
        self.assertEqual(generate_sequence(1), [('0', 0)])

if __name__ == '__main__':
    unittest.main(verbosity=2)
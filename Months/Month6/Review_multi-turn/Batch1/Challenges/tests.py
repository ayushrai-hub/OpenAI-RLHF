from ideal_completion import cleave
import unittest

class TestScrapyIntegration(unittest.TestCase):
    
    def test1(self):
        # Check user's provided example to match correct expected output
        result = cleave('keyboard', 'mouse', 5)
        self.assertSequenceEqual(result,('keybo','mouseard'))
        
    def test2(self):
        # Check with strings input and zero index
        result = cleave('keyboard', 'mouse', 0)
        # Both sequences are entirely swapped with each other as there are no initial parts.
        self.assertSequenceEqual(result,('mouse','keyboard'))
        
    def test3(self):
        # Check with strings input and beyond range index
        result = cleave('keyboard', 'mouse', 8)
        # returns both sequences in a tuple unchanged as the index falls out of range there are no terminal parts.
        self.assertSequenceEqual(result,('keyboard', 'mouse'))

    def test4(self):
        # Check the user's provided example to match the correct expected output
        result = cleave((5, 6, 7), (8, 9, 10, 11), 1)
        self.assertSequenceEqual(result,((5, 9, 10, 11), (8, 6, 7)))

    def test5(self):
        # Check with tuples input and zero index
        result = cleave((5, 6, 7), (8, 9, 10, 11), 0)
        # Both sequences are entirely swapped with each other as there are no initial parts.
        self.assertSequenceEqual(result,((8, 9, 10, 11), (5, 6, 7)))
        
    def test6(self):
        # Check with tuples input and beyond range index
        result = cleave((5, 6, 7), (8, 9, 10, 11), 5)
        # returns both sequences in a tuple unchanged as the index falls out of range there are no terminal parts.
        self.assertSequenceEqual(result,((5, 6, 7), (8, 9, 10, 11)))
        
                
if __name__ == '__main__':
    unittest.main(verbosity=2)

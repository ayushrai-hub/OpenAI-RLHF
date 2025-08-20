# test.py
import execjs
import unittest
import os

class TestJavaScriptFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load code
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ideal_completion.js')), 'r') as file:
            cls.js_code = file.read()
        cls.ctx = execjs.compile(cls.js_code)
        # Create gachaItems list to use in the tests
        cls.gachaItems = '[{ name: "Common Sword", probability: 0.6, star: 1 },{ name: "Uncommon Shield", probability: 0.25, star: 2 },{ name: "Rare Armor", probability: 0.1, star: 3 },{ name: "Epic Staff", probability: 0.04, star: 4 },{ name: "Legendary Bow", probability: 0.01, star: 4 }]'

    # Test to validade the pityCounter value returned in drawGacha function.
    # This is important to ensure the pityCounter is always calculated correctly and encapsulated properly in the function.
    def test_validate_pityCounter(self):
        # Executing once
        result = self.ctx.eval(f'drawGacha(0, {self.gachaItems})')
        self.assertEqual(result['pityCounter'], 1)
        
        # Executing twice the same value to evaluate if the counter is the same
        result = self.ctx.eval(f'drawGacha(10, {self.gachaItems})')
        self.assertEqual(result['pityCounter'], 11)
        result = self.ctx.eval(f'drawGacha(10, {self.gachaItems})')
        self.assertEqual(result['pityCounter'], 11)

    # Test to ensure pity counter resets after max pity threshold, this is important to ensure the pity counter logic is working to draw 4-star items after 90 attempts and reset the counter properly.
    def test_pity_max_reset(self):
        result = self.ctx.eval(f'drawGacha(89, {self.gachaItems})')
        self.assertEqual(result['pityCounter'], 0)
        self.assertIn(result['SelectedItem'], ["Epic Staff", "Legendary Bow"])  # Item should be 4-star

    # Test to ensure normal increment when pity threshold isn't reached
    # Ensure that a valid item is correctly returned alongside with the counter
    def test_normal_item_draw(self):
        result = self.ctx.eval(f'drawGacha(45, {self.gachaItems})')
        self.assertEqual(result['pityCounter'], 46)  # Pity counter should increment normally
        self.assertIn(result['SelectedItem'], ["Common Sword", "Uncommon Shield", "Rare Armor", "Epic Staff", "Legendary Bow"])  # Valid item check


    # Test to ensure error is thrown when probability is greater than 1
    # This is important to see if the code handles cases where the provided probability in the items can cause error 
    def test_higher_amount_probabilities(self):
        with self.assertRaises(Exception):
            self.ctx.eval('drawGacha(0, [{name: "Common Sword", probability: 1.1, star: 1}])')
    
    # Test to ensure error is thrown when probability is lower than 1
    # This is important to see if the code handles cases where the provided probability in the items can cause error 
    def test_lower_amount_probabilities(self):
        with self.assertRaises(Exception):
            self.ctx.eval('drawGacha(0, [{name: "Common Sword", probability: 0.9, star: 1}])')
            

if __name__ == '__main__':
    unittest.main(verbosity=2)

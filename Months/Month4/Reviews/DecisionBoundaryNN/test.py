import unittest
import torch
from ideal_completion import DecisionBoundaryNN

class TestDecisionBoundary(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.model = DecisionBoundaryNN()
    
    def test_class_0_light(self):
        res = self.model(torch.tensor([1, 6.]))
        res = res.item()  
        self.assertAlmostEqual(res, 0, 1)
        
    def test_class_1_light(self):
        res = self.model(torch.tensor([1, 4.]))  
        res = res.item()
        self.assertAlmostEqual(res, 1, 1)
        
    def test_class_0_heavy(self):
        res = self.model(torch.tensor([1, 6.]))  
        res = res.item()
        self.assertAlmostEqual(res, 0, 4)
        
    def test_class_1_heavy(self):
        res = self.model(torch.tensor([1, 4.]))  
        res = res.item()
        self.assertAlmostEqual(res, 1, 4)
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
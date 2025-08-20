import unittest
from testableIc import select_prime

class TestSelectPrime(unittest.TestCase):
    
    def setUp(self):
        # Common primes list for testing
        self.primes = [2, 3, 5, 7, 11, 13]
    
    def test_normal_case(self):
        # Test with normal domain and seed
        domain = 30
        seed = 10
        result = select_prime(domain, seed, self.primes)
        self.assertEqual(result, (11, 1)) 
    
    def test_edge_case_small_domain(self):
        # Test with small domain
        domain = 5
        seed = 1
        result = select_prime(domain, seed, self.primes)
        self.assertGreater(result[0], 0)  # Should return a valid combination

    def test_seed_reset(self):
        # Test where seed gets reset due to mod operation
        domain = 30
        seed = 100
        result = select_prime(domain, seed, self.primes)
        self.assertLess(result[1], 100)  # Seed should be within valid range after modulo
    
    def test_no_eligible_primes(self):
        # Test when no primes are eligible (domain divisible by all primes)
        domain = 30
        primes = [2, 3, 5]
        result = select_prime(domain, 1, primes)
        self.assertEqual(result, (1, 1))  # Default product with no eligible primes
    
    def test_only_one_prime_eligible(self):
        # Test where only one prime is eligible
        domain = 6
        primes = [2, 3, 5]
        result = select_prime(domain, 0, primes)
        self.assertEqual(result[1], 0)  # Check seed behavior
    
    def test_large_seed(self):
        # Test with a very large seed
        domain = 50
        seed = 1000
        result = select_prime(domain, seed, self.primes)
        self.assertIsInstance(result, tuple)
        self.assertGreater(result[0], 0)  # Should return a valid prime product
    
    def test_same_domain_primes(self):
        # Test with different seeds for the same domain and prime list
        domain = 50
        result1 = select_prime(domain, 0, self.primes)
        result2 = select_prime(domain, 1, self.primes)
        self.assertNotEqual(result1, result2)  # Results should differ for different seeds
    
    def test_empty_primes_list(self):
        # Test with an empty list of primes
        domain = 50
        result = select_prime(domain, 0, [])
        self.assertEqual(result, (1, 0))  # Should return the base product

if __name__ == '__main__':
    unittest.main(verbosity=2)
import unittest
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from try_ideal import simulate_hidden_factors , simulate_stock_prices, ParticleFilter, run_particle_filter,plot_factors
class TestParticleFilterModel(unittest.TestCase):

    # Test to check the functionality of simulate hidden_factors
    #  Its important to make sure that this  function has created the necessary data structure required for later operations.
    def test_simulate_hidden_factors_shape(self):
        num_days, num_factors = 100, 2
        factors = simulate_hidden_factors(num_days, num_factors)
        self.assertEqual(factors.shape, (num_days, num_factors),
                         "Hidden factors matrix shape mismatch.")

#  Test to check the dimensions/shapes of the stock prices data  set
#  Its important to make sure that this  function has created the stock prices dataset and its structure is correct. 
    def test_simulate_stock_prices_shape(self):
        num_days, num_factors, num_stocks = 100, 2, 5
        factors = simulate_hidden_factors(num_days, num_factors)
        stock_prices, _ = simulate_stock_prices(factors, num_stocks)
        self.assertEqual(stock_prices.shape, (num_days, num_stocks),
                         "Stock prices matrix shape mismatch.")

#  Test to check the creation of particle filters
#  Its important to make sure that correct particle filters are created. 
    def test_particle_filter_initialization(self):
        num_particles, num_factors, num_stocks = 500, 2, 3
        pf = ParticleFilter(num_particles, num_factors, num_stocks)
        self.assertEqual(pf.particles.shape, (num_particles, num_factors),
                         "Particles array shape mismatch.")
        self.assertEqual(pf.weights.shape, (num_particles,),
                         "Weights array shape mismatch.")

#  Test to check the particle filter function, which is the main functionality of the code.
#  Its important to make sure that this function can generate estimates over multiple days , and function according to the  time. 
    def test_particle_filter_estimation(self):
        num_days, num_particles, num_factors, num_stocks = 50, 200, 2, 3
        factors = simulate_hidden_factors(num_days, num_factors)
        stock_prices, _ = simulate_stock_prices(factors, num_stocks)
        
        pf = ParticleFilter(num_particles, num_factors, num_stocks)
        estimated_factors = np.zeros((num_days, num_factors))
        
        for t in range(num_days):
            pf.predict()
            pf.update(stock_prices[t])
            pf.resample()
            estimated_factors[t] = pf.estimate()
        
        self.assertEqual(estimated_factors.shape, (num_days, num_factors),
                         "Estimated factors matrix shape mismatch.")

    # Test to check if plot_factors generates a graph or not using memory buffer
    #  Its important because graph generation was one of the major requirement of the user. 
    def test_plot_generation(self):
        num_days = 100
        num_particles = 500
        num_factors = 2
        num_stocks = 1

        factors, estimated_factors = run_particle_filter(num_days, num_particles, num_factors, num_stocks)
        fig, ax = plt.subplots()
        plot_factors(factors, estimated_factors)
        
        img_data = BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        
        self.assertGreater(len(img_data.getvalue()), 0, "No image data was generated.")
        plt.close(fig)

if __name__ == '__main__':
    unittest.main(verbosity=2)


import numpy as np
import matplotlib.pyplot as plt


def simulate_hidden_factors(num_days, num_factors, seed=42):
    np.random.seed(seed)
    factors = np.cumsum(np.random.normal(0, 1, size=(num_days, num_factors)), axis=0)
    return factors


def simulate_stock_prices(factors, num_stocks, noise_std=0.5, seed=42):
    np.random.seed(seed)
    num_days, num_factors = factors.shape
    loadings = np.random.normal(0, 1, size=(num_factors, num_stocks))
    stock_prices = factors @ loadings + np.random.normal(0, noise_std, size=(num_days, num_stocks))
    return stock_prices, loadings


class ParticleFilter:
    def __init__(self, num_particles, num_factors, num_stocks, process_noise_std=0.5, observation_noise_std=0.5, loadings=None):
        self.num_particles = num_particles
        self.num_factors = num_factors
        self.num_stocks = num_stocks
        self.process_noise_std = process_noise_std
        self.observation_noise_std = observation_noise_std
        if loadings is None:
            self.loadings = np.random.normal(0, 1, size=(num_factors, num_stocks))
        else:
            self.loadings = loadings
        self.particles = np.random.normal(0, 1, size=(self.num_particles, self.num_factors))
        self.weights = np.ones(self.num_particles) / self.num_particles

    def initialize(self, initial_mean, initial_std):
        self.particles = np.random.normal(initial_mean, initial_std, size=(self.num_particles, self.num_factors))
        self.weights = np.ones(self.num_particles) / self.num_particles

    def predict(self):
        noise = np.random.normal(0, self.process_noise_std, size=self.particles.shape)
        self.particles += noise

    def update(self, observation):
        if self.loadings is None or self.loadings.shape[0] != self.num_factors or self.loadings.shape[1] != self.num_stocks:
            raise ValueError("Loadings matrix dimensions must match (num_factors, num_stocks).")
        estimated_obs = self.particles @ self.loadings
        likelihoods = np.exp(-0.5 * np.sum(((observation - estimated_obs) / self.observation_noise_std) ** 2, axis=1))
        self.weights *= likelihoods
        self.weights += 1e-300  # Avoid zero weights
        self.weights /= np.sum(self.weights)  # Normalize

    def resample(self):
        indices = np.random.choice(range(self.num_particles), size=self.num_particles, p=self.weights)
        self.particles = self.particles[indices]
        self.weights = np.ones(self.num_particles) / self.num_particles

    def estimate(self):
        return np.average(self.particles, axis=0, weights=self.weights)


def run_particle_filter(num_days, num_particles, num_factors, num_stocks, seed=42):
    np.random.seed(seed)

    factors = simulate_hidden_factors(num_days, num_factors, seed=seed)
    stock_prices, loadings = simulate_stock_prices(factors, num_stocks, seed=seed)

    pf = ParticleFilter(num_particles, num_factors, num_stocks, loadings=loadings)
    pf.initialize(initial_mean=0, initial_std=1)

    estimated_factors = np.zeros((num_days, num_factors))

    for t in range(num_days):
        pf.predict()
        pf.update(stock_prices[t])
        pf.resample()
        estimated_factors[t] = pf.estimate()

    return factors, estimated_factors


def plot_factors(factors, estimated_factors, filename="image.png"):
    num_factors = factors.shape[1]
    plt.figure(figsize=(12, 6))
    for i in range(num_factors):
        plt.plot(factors[:, i], label=f"True Factor {i+1}")
        plt.plot(estimated_factors[:, i], '--', label=f"Estimated Factor {i+1}")
    plt.xlabel("Time")
    plt.ylabel("Factor Value")
    plt.legend()
    plt.title("True vs. Estimated Factors")
    plt.savefig(filename)
    plt.close()

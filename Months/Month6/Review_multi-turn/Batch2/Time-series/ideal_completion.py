import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def logistic_model(t, I0, tau, k, tc, Ib):
    # Logistic function model
    return I0 * np.exp(-t/tau) / (1.0 + np.exp(-k*(t - tc))) + Ib

def estimate_parameters(time, intensity):
    # Initial guesses for parameters
    I0_guess = np.max(intensity)
    tau_guess = 1.0 if np.all(time == time) else 1.0  # fallback
    k_guess = 1.0
    tc_guess = np.median(time)
    Ib_guess = np.min(intensity)
    initial_guess = [I0_guess, tau_guess, k_guess, tc_guess, Ib_guess]
    # Fit the data
    popt, pcov = curve_fit(logistic_model, time, intensity, p0=initial_guess)
    # Calculate intensities using the fitted model
    fitted_intensity = logistic_model(time, *popt)
    # Calculate duration D
    I0_fit, tau_fit, k_fit, tc_fit, Ib_fit = popt
    D = (2.0/k_fit) * np.log(1.0/0.05 - 1.0)
    return popt, fitted_intensity, D

def plot_data(time, intensity, fitted_intensity):
    plt.figure()
    plt.scatter(time, intensity, label='Data')
    plt.plot(time, fitted_intensity, 'r-', label='Fit')
    plt.xlabel('Time')
    plt.ylabel('Intensity')
    plt.legend()
    # Instead of plt.show() use plt.close() for unit tests
    plt.close()

import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, List

def piecewise_linear_3(x, x0, x1, y0, m1, m2, m3):
    return np.piecewise(x, 
                        [x < x0, (x >= x0) & (x < x1), x >= x1], 
                        [lambda x: m1*x + y0 - m1*x0,
                         lambda x: m2*x + y0 + m1*x0 - m2*x0,
                         lambda x: m3*x + y0 + m1*x0 + m2*x1 - m3*x1 - m2*x0])

def piecewise_linear(x, x0, y0, m1, m2):
    return np.piecewise(x,
                        [x < x0, x >= x0],
                        [lambda x: m1*x + y0 - m1*x0,
                         lambda x: m2*x + y0 + m1*x0 - m2*x0])

def piecewise_powerlaw(x, x0, y0, m1, m2):
    return np.piecewise(x,
                        [x < x0, x >= x0],
                        [lambda x: y0 * np.power(np.maximum(x/x0, 1e-10), m1),
                         lambda x: y0 * np.power(np.maximum(x/x0, 1e-10), m2)])

def create_plots(separations_VSF: np.ndarray, VSF: np.ndarray,
                 x0: float, x1: float, y0: float, m1: float, m2: float, m3: float,
                 closest_d1: float, closest_f_d1: float, closest_d2: float, closest_f_d2: float,
                 x0_2: float, y0_2: float, m1_2: float, m2_2: float,
                 closest_d_2lines: float, closest_f_d_2lines: float,
                 x0_p: float, y0_p: float, m1_p: float, m2_p: float,
                 closest_d: float, closest_f_d: float,
                 without: float, within: float) -> Tuple[plt.Figure, List[plt.Axes]]:
    
    fig, axs = plt.subplots(1, 3, figsize=(24, 8), dpi=300)
    fig.subplots_adjust(wspace=0.3)

    d = np.log10(separations_VSF)
    f_d = np.log10(VSF)

    plot_params = [
        ('3 lines free', piecewise_linear_3, [x0, x1, y0, m1, m2, m3], [(closest_d1, closest_f_d1), (closest_d2, closest_f_d2)]),
        ('2 lines constrained', piecewise_linear, [x0_2, y0_2, m1_2, m2_2], [(closest_d_2lines, closest_f_d_2lines)]),
        ('2 lines free', piecewise_powerlaw, [x0_p, y0_p, m1_p, m2_p], [(closest_d, closest_f_d)])
    ]

    for i, (ax, (title, func, params, points)) in enumerate(zip(axs, plot_params)):
        ax.scatter(separations_VSF, VSF, label='VSF2', alpha=0.6, s=30, color='#1f77b4')
        x_fit = np.linspace(min(d), max(d), 500)
        y_fit = func(x_fit, *params)
        ax.loglog(10**x_fit, 10**y_fit, label='Fitted Piecewise Linear', color='#ff7f0e', ls='--', lw=2)
        
        for j, (x, y) in enumerate(points, 1):
            ax.scatter([10**x], [10**y], color='#d62728', s=100, label=f'turning point {j}', zorder=5, edgecolors='black')

        ax.set_xlabel('Separations', fontsize=14)
        if i == 0:
            ax.set_ylabel('VSF', fontsize=14)
        else:
            ax.yaxis.set_visible(False)
        ax.legend(fontsize=12, loc='best')
        ax.set_title(title, fontsize=16, pad=20)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.tick_params(axis='both', which='minor', labelsize=10)
        ax.grid(True, which='both', linestyle='--', alpha=0.5)
        ax.set_facecolor('#f8f8f8')

    fig.suptitle(f'{without} < r < {within}, normal v', fontsize=18, y=1.05)
    plt.tight_layout()
    
    return fig, axs

if __name__ == '__main__':
    # Example usage
    separations_VSF = np.logspace(-2, 2, 100)
    VSF = np.random.rand(100) * 100
    x0, x1 = 0, 1
    y0 = 1
    m1, m2, m3 = 1, 2, 3
    closest_d1, closest_f_d1 = 0.5, 50
    closest_d2, closest_f_d2 = 1.5, 75
    x0_2, y0_2 = 0.5, 2
    m1_2, m2_2 = 2, 3
    closest_d_2lines, closest_f_d_2lines = 0.75, 60
    x0_p, y0_p = 1, 10
    m1_p, m2_p = 0.5, 1.5
    closest_d, closest_f_d = 1.25, 80
    without, within = 0.1, 10

    fig, axs = create_plots(separations_VSF, VSF,
                            x0, x1, y0, m1, m2, m3,
                            closest_d1, closest_f_d1, closest_d2, closest_f_d2,
                            x0_2, y0_2, m1_2, m2_2,
                            closest_d_2lines, closest_f_d_2lines,
                            x0_p, y0_p, m1_p, m2_p,
                            closest_d, closest_f_d,
                            without, within)
    plt.show()
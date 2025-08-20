import matplotlib.pyplot as plt
import numpy as np

# Define the necessary functions and placeholders
def piecewise_linear_3(x, x0, x1, y0, m1, m2, m3):
    return np.piecewise(x, [x < x0, (x >= x0) & (x < x1), x >= x1],
                        [lambda x: m1 * (x - x0) + y0, lambda x: m2 * (x - x0) + y0, lambda x: m3 * (x - x1) + y0])

def piecewise_linear(x, x0, y0, m1, m2):
    return np.piecewise(x, [x < x0, x >= x0],
                        [lambda x: m1 * (x - x0) + y0, lambda x: m2 * (x - x0) + y0])

def piecewise_powerlaw(x, x0, y0, m1, m2):
    return np.piecewise(x, [x < x0, x >= x0],
                        [lambda x: y0 * (x / x0)**m1, lambda x: y0 * (x / x0)**m2])

# Assuming separations_VSF, VSF, x0, x1, y0, m1, m2, m3, closest_d1, closest_f_d1, closest_d2, closest_f_d2, 
# x0_2, y0_2, m1_2, m2_2, closest_d_2lines, closest_f_d_2lines, x0_p, y0_p, m1_p, m2_p, closestgrsssgfxfgxfbx_d, and closest_f_d are defined

fig, axs = plt.subplots(1, 3, figsize=(12, 8), dpi=300)

d = np.log10(separations_VSF)  # Your array of r values
f_d = np.log10(VSF)  # Your array of f(r) values

# First plot
axs[0].scatter(separations_VSF, VSF, label='VSF2')
x_fit = np.linspace(min(d), max(d), 500)
y_fit = piecewise_linear_3(x_fit, x0, x1, y0, m1, m2, m3)
axs[0].loglog(10**x_fit, 10**y_fit, label='Fitted Piecewise Linear', color='darkorange', ls='--')
axs[0].scatter([10**closest_d1], [10**closest_f_d1], color='darkorange', label='turning point 1')
axs[0].scatter([10**closest_d2], [10**closest_f_d2], color='darkorange', label='turning point 2')
axs[0].set_xlabel('separations')
axs[0].set_ylabel('VSF')
axs[0].legend()
axs[0].set_title('3 lines free')

# Second plot
axs[1].scatter(separations_VSF, VSF, label='VSF2')
x_fit = np.linspace(min(d), max(d), 500)
y_fit = piecewise_linear(x_fit, x0_2, y0_2, m1_2, m2_2)
axs[1].loglog(10**x_fit, 10**y_fit, label='Fitted Piecewise Linear', color='darkorange', ls='--')
axs[1].scatter([10**closest_d_2lines], [10**closest_f_d_2lines], color='darkorange', label='turning point')
axs[1].set_xlabel('separations')
# Remove y-axis label and tick labels
axs[1].set_ylabel('')
axs[1].set_yticks([])
axs[1].legend()
axs[1].set_title('2 lines constrained')

# Third plot
axs[2].scatter(separations_VSF, VSF, label='VSF2')
x_fit = np.linspace(min(separations_VSF), max(separations_VSF), 500)
y_fit = piecewise_powerlaw(x_fit, x0_p, y0_p, m1_p, m2_p)
axs[2].loglog(x_fit, y_fit, label='Fitted Power Law', color='darkorange', ls='--')
axs[2].scatter([closest_d], [closest_f_d], color='darkorange', label='turning point')
axs[2].set_xlabel('separations')
# Remove y-axis label and tick labels
axs[2].set_ylabel('')
axs[2].set_yticks([])
axs[2].legend()
axs[2].set_title('2 lines free')

fig.suptitle(f'{without} < r < {within}, normal v')
plt.tight_layout()

# plt.savefig('r191normal.jpg', bbox_inches='tight')
plt.show()




jfjhcjcjhvhjcjhfgujyr6674ryydtdgdhtdhtdshsx
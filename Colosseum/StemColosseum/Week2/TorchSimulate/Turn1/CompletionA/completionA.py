import torch
import numpy as np

# Constants
size_x = 10
size_y = 10
size_z = 10

MCtherm = 1000
MCstep = 10000

Tmin = 3.6
Tmax = 5.2
Tstep = 0.01

FILE_NAME = "6_3D_10.txt"

# Device Configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Function to initialize
def initialize_system(size_x, size_y, size_z):
    m = torch.ones((size_z, size_y, size_x), device=device)
    M = size_x * size_y * size_z
    E = -3 * M
    return m, E, M


# Function to flip in batch
def flip_batch(m, E, M, KT):
    size = size_z * size_y * size_x
    x = torch.randint(size_x, (size,), device=device)
    y = torch.randint(size_y, (size,), device=device)
    z = torch.randint(size_z, (size,), device=device)

    x_less = (x - 1) % size_x
    x_more = (x + 1) % size_x
    y_less = (y - 1) % size_y
    y_more = (y + 1) % size_y
    z_less = (z - 1) % size_z
    z_more = (z + 1) % size_z

    ns = (m[z, y, x_less] + m[z, y, x_more] +
          m[z, y_less, x] + m[z, y_more, x] +
          m[z_less, y, x] + m[z_more, y, x])

    dE = 2 * m[z, y, x] * ns
    dM = -2 * m[z, y, x]

    flip_mask = (dE < 0) | ((dE > 0) & (torch.rand(size, device=device) < torch.exp(-dE / KT)))
    m[z, y, x] = torch.where(flip_mask, m[z, y, x], -m[z, y, x])
    E = torch.sum(dE * flip_mask)
    M = torch.sum(dM * flip_mask)

    return E, M


# Function to simulate the process
def simulate(m, fp):
    for KT in np.arange(Tmin, Tmax + Tstep, Tstep):
        KT = round(KT, 2)
        print(f"{KT}")
        m, E, M = initialize_system(size_x, size_y, size_z)
        E_avg = M_avg = E2_avg = M2_avg = order_param = 0

        for _ in range(MCtherm):
            E, M = flip_batch(m, E, M, KT)

        for _ in range(MCstep):
            E, M = flip_batch(m, E, M, KT)

            E_avg += E
            M_avg += M
            E2_avg += E * E
            M2_avg += M * M
            order_param += abs(M)


        E_avg /= MCstep
        M_avg /= MCstep
        E2_avg /= MCstep
        M2_avg /= MCstep
        order_param /= MCstep
        order_param /= size_x * size_y * size_z

        Cv = (E2_avg - E_avg * E_avg) / (KT * KT * size_x * size_y * size_z)
        chi = (M2_avg - M_avg * M_avg) / (KT * size_x * size_y * size_z)

        # Writing results to file
        fp.write(f"{KT} {order_param} {Cv} {chi}\n")

    fp.close()


# Main code execution
with open(FILE_NAME, "w") as fp:
    m, E, M = initialize_system(size_x, size_y, size_z)
    simulate(m, fp)

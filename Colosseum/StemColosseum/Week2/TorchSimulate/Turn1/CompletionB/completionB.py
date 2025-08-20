import torch
import math
import random
import time

size_x, size_y, size_z = 10, 10, 10
MCtherm, MCstep = 1000, 10000
Tmin, Tmax, Tstep = 3.6, 5.2, 0.01
FILE_NAME = "6_3D_10.txt"

# Function to flip the state of a specific element
def flip(m, x, y, z, E, M, KT):
    x_less = size_x - 1 if x == 0 else x - 1
    x_more = 0 if x == size_x - 1 else x + 1
    y_less = size_y - 1 if y == 0 else y - 1
    y_more = 0 if y == size_y - 1 else y + 1
    z_less = size_z - 1 if z == 0 else z - 1
    z_more = 0 if z == size_z - 1 else z + 1

    ns = m[z, y, x_less] + m[z, y, x_more] + m[z, y_less, x] + m[z, y_more, x] + m[z_less, y, x] + m[z_more, y, x]
    dE = 2 * m[z, y, x] * ns
    dM = -2 * m[z, y, x]

    if dE < 0 or (dE >= 0 and random.random() < math.exp(-dE / KT)):
        m[z, y, x] = -m[z, y, x]
        E[0] += dE
        M[0] += dM

def initialize_system(m, E, M):
    m.fill_(1)
    E[0] = -3 * size_z * size_y * size_x
    M[0] = size_z * size_y * size_x

def simulate(m, fp):
    E, M = torch.tensor([0.0], device='cuda'), torch.tensor([0.0], device='cuda')

    for KT in torch.arange(Tmin, Tmax + Tstep, Tstep):
        print(KT.item())
        initialize_system(m, E, M)

        for _ in range(MCtherm):
            for _ in range(size_z * size_y * size_x):
                x, y, z = random.randint(0, size_x - 1), random.randint(0, size_y - 1), random.randint(0, size_z - 1)
                flip(m, x, y, z, E, M, KT)

        E_avg, M_avg, E2_avg, M2_avg = torch.tensor([0.0]*4, device='cuda')
        for _ in range(MCstep):
            for _ in range(size_z * size_y * size_x):
                x, y, z = random.randint(0, size_x - 1), random.randint(0, size_y - 1), random.randint(0, size_z - 1)
                flip(m, x, y, z, E, M, KT)

            E_avg += E
            M_avg += M
            E2_avg += E * E
            M2_avg += M * M
        
        E_avg /= MCstep
        M_avg /= MCstep
        E2_avg /= MCstep
        M2_avg /= MCstep
        
        order_param = (torch.abs(M_avg) / (size_z * size_y * size_x)).item()
        Cv = ((E2_avg - E_avg * E_avg) / (KT * KT * size_z * size_y * size_x)).item()
        chi = ((M2_avg - M_avg * M_avg) / (KT * size_z * size_y * size_x)).item()

        fp.write(f"{KT.item()} {order_param} {Cv} {chi}\n")


if __name__ == '__main__':
    torch.cuda.manual_seed(time.time())
    m = torch.empty(size_z, size_y, size_x, device='cuda', dtype=torch.int)

    with open(FILE_NAME, "w") as fp:
        simulate(m, fp)

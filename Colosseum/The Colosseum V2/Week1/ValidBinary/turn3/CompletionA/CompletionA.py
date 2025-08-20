def nthBinary(n):
    i = 2
    count = 0
    while True:
        b = bin(i)[2:]
        if b.startswith('1') and '01' not in b and b.endswith('0'):
            count += 1
            if count == n:
                return b
        i += 1

n = 1
for i in range(1, 101):
    bi = nthBinary(i)
    print(f"{n} " + '0' * n + '1', "->", bi)
    n += 1

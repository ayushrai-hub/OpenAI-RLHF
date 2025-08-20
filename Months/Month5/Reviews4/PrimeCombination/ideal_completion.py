# ideal_completion.py
from itertools import chain, combinations
from typing import Sequence, Tuple

NUM_COMBINATIONS = {}

def select_prime(
    domain: int,
    seed: int,
    primes: Sequence[int]
) -> Tuple[int, int]:
    org_seed = seed
    num_comb = None

    # Check if the number of combinations is already cached
    if primes is PRIMES and domain in NUM_COMBINATIONS:
        num_comb = NUM_COMBINATIONS[domain]
        seed %= num_comb

    eligible = (prime for prime in primes if domain % prime != 0)
    seen = set()
    count = 0
    p = 1 

    # Generate combinations lazily and exit early
    for p1, p2, p3 in combinations(chain((1, 1), eligible), 3):
        p = p1 * p2 * p3 % domain
        if p in seen:
            continue
        seen.add(p)
        
        if count == seed:  # Early exit once the correct combination is found
            return p, org_seed // max(count, 1)
        count += 1

    if primes is PRIMES:
        NUM_COMBINATIONS[domain] = count

    return p, org_seed // max(count, 1)

# Example usage
PRIMES = [2, 3, 5, 7, 11, 13]
domain = 30
seed = 10

result = select_prime(domain, seed, PRIMES)
print(result)
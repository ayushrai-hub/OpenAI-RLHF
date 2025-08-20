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
    
    # Generate combinations lazily and exit early
    for p1, p2, p3 in combinations(chain((1, 1), eligible), 3):
        p = p1 * p2 * p3 % domain
        if p in seen:
            continue
        seen.add(p)
        
        if num_comb is not None and count == seed:
            return p, org_seed // num_comb
        count += 1

    if primes is PRIMES:
        NUM_COMBINATIONS[domain] = count

    return p, org_seed // count

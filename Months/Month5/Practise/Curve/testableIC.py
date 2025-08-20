from tinyec.ec import SubGroup, Curve, Point
from os import urandom
import time
from bisect import bisect_left
import random
import hashlib
import base58

# Method to compress the public key
def compress_pub_key(x, y):
    prefix = '02' if y % 2 == 0 else '03'
    return prefix + format(x, '064x')

# Complete operation to convert a public key to a Bitcoin address
def public_key_to_address(pub_key):
    pub_key_bytes = bytes.fromhex(pub_key)
    sha256 = hashlib.sha256(pub_key_bytes).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    # Include network byte (0x00 for mainnet)
    network_byte = b'\x00' + ripemd160
    checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]
    address_bytes = network_byte + checksum
    return base58.b58encode(address_bytes).decode()

# Specify the secp256k1 constants and curve with TinyEC
p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
a = 0
b = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
h = 1  # secp256k1 cofactor is 1

# Build the subgroup first using the generator point G
subgroup = SubGroup(p, (Gx, Gy), N, h)

# Construct the curve object with the linked subgroup
curve = Curve(a, b, subgroup)

# Generator point G is inherently defined within the subgroup
G = curve.g

# Quantum inspired "superposition" guess creation
def quantum_superposition_search(initial_private_key, final_private_key, attempts=100):
    return [random.randint(initial_private_key, final_private_key) for _ in range(attempts)]

# Process a batch of private keys
def process_batch(private_keys, target_pubkey, target_address):
    for private_key in private_keys:
        pub_key_guess = private_key * curve.g
        compressed_guess = compress_pub_key(pub_key_guess.x, pub_key_guess.y)
        if compressed_guess == target_pubkey:
            address = public_key_to_address(compressed_guess)
            if address == target_address:
                return private_key
    return None

# Execute the alien-inspired key search process
def alien_search_for_key(target_pubkey, target_address, max_attempts=1000, batch_size=100, time_limit=300):
    initial_private_key = 1
    final_private_key = N - 1
    key_found = False
    start_time = time.time()

    print("Initiating Alien Algorithm to discover private key...")
    for _ in range(max_attempts):
        if time.time() - start_time > time_limit:
            print("Time limit exceeded. Key not found.")
            return None

        guesses = quantum_superposition_search(initial_private_key, final_private_key, batch_size)
        private_key = process_batch(guesses, target_pubkey, target_address)
        if private_key:
            print("------------ Private Key Discovered! ------------")
            print(f"Private Key: {hex(private_key)}")
            print(f"Matched Address: {target_address}")
            return private_key

        elapsed_time = time.time() - start_time
        print(f"Keys scanned per second: {len(guesses) // elapsed_time:.2f}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

    print("Maximum attempts reached. Key not found.")
    return None

# Main entry point for execution
def main():
    compressed_pub_key = "02e0a8b039282faf6fe0fd769cfbc4b6b4cf8758ba68220eac420e32b91ddfa673"
    ph2k_address = "1NBC8uXJy1GiJ6drkiZa1WuKn51ps7EPTv"
    private_key = alien_search_for_key(compressed_pub_key, ph2k_address, max_attempts=1000, batch_size=100, time_limit=300)
    if private_key:
        print(f"Discovered private key: {hex(private_key)}")
    else:
        print("Private key was not discovered.")

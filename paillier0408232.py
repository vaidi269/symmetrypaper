import random
import math
import sympy

def generate_prime(bits):
    """Generate a random prime number with the specified number of bits."""
    while True:
        p = random.getrandbits(bits)
        if sympy.isprime(p):
            return p

def generate_keypair(bits=1024):
    """Generate a key pair for the Paillier cryptosystem."""
    p = sympy.randprime(2 ** (bits // 2 - 1), 2 ** (bits // 2))
    q = sympy.randprime(2 ** (bits // 2 - 1), 2 ** (bits // 2))
    n = p * q
    g = n + 1
    lambda_n = sympy.lcm(p - 1, q - 1)
    mu = mod_inverse(int(pow(g, int(lambda_n), n ** 2)), n) % n
    public_key = (n, g)
    private_key = (n, g, lambda_n, mu, p, q)  # Include p and q in private key for decryption
    return public_key, private_key, lambda_n



def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def generate_prime1():
    while True:
        prime = random.randint(100, 1000)  # Adjust the range as per your requirement
        if is_prime(prime):
            return prime

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return abs(a * b) // gcd(a, b)



def L(u, n):
    """Carmichael's totient function."""
    return (u - 1) // n

def mod_inverse(a, m):
    """Compute the modular inverse of a mod m."""
    g, x, y = sympy.gcdex(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def encrypt(m, n, g, r):
    return (pow(g, m, n ** 2) * pow(r, n, n ** 2)) % (n ** 2)

def decrypt(ciphertext, private_key):
    n, _, lambda_n, mu, _, _ = private_key
    c = int(ciphertext)
    lambda_n_int = int(lambda_n)

    # Calculate the plaintext using the Paillier decryption formula
    c1 = pow(c, lambda_n, n ** 2)
    m = (L(c1, n) * mu) % n

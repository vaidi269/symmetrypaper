# decrypt_image.py

import cv2
import numpy as np
from paillier0408232 import decrypt, generate_keypair
from paillier0408232 import *

def mod_inverse(a, m):
    """Compute the modular inverse of a mod m."""
    g, x, y = sympy.gcdex(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def find_coprime(n, value, max_attempts=1000):
    """Find a coprime value for 'value' within 'max_attempts'."""
    attempts = 0
    while sympy.gcd(value, n) != 1 and attempts < max_attempts:
        value += 1
        attempts += 1
    return value if attempts < max_attempts else None

def read_image_gray(image_path):
    # Read the image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Convert the image to 8-bit grayscale if it is not already
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)

    return img

def describe_as_color_pixel(ciphertext):
    # Convert the ciphertext to 24-bit color pixel values
    r = ciphertext // (256 ** 2)
    g = (ciphertext % (256 ** 2)) // 256
    b = ciphertext % 256
    return r, g, b

def color_pixel_to_ciphertext(r, g, b):
    # Convert the 24-bit color pixel values back to the ciphertext
    ciphertext = r * (256 ** 2) + g * 256 + b
    return ciphertext

def decrypt_pixel_pair(w_ij, w_ij_plus_1, private_key):
    n, _, _, _, _, _ = private_key
    
    inv_w_ij_plus_1 = find_coprime(n, w_ij_plus_1)
    if inv_w_ij_plus_1 is None:
        raise ValueError("Unable to find a coprime value for w(i, j + 1)")

    # Calculate w(i, j) * w(i, j + 1)^-1 mod n
    w_prod = (w_ij * inv_w_ij_plus_1) % n
    
    
    # Calculate D(w(i, j) * w(i, j + 1)^-1) * 2^-1 mod n
    m_decrypted_ij = (decrypt(w_prod, private_key) * mod_inverse(2, n)) % n

    # Calculate D(w(i, j) * w(i, j + 1)^-1 - n) * 2^-1 mod n if D(w(i, j) * w(i, j + 1)^-1) >= n/2
    if m_decrypted_ij >= n / 2:
        m_decrypted_ij = (decrypt(w_prod - n, private_key) * mod_inverse(2, n)) % n

    # Calculate w(i, j + 1)^-1 mod n
    inv_w_ij = mod_inverse(w_ij, n)

    # Calculate D(w(i, j) * w(i, j + 1)^-1)^-1 * 2^-1 mod n
    m_decrypted_ij_plus_1 = (mod_inverse(decrypt(w_prod, private_key), n) * mod_inverse(2, n)) % n

    # Calculate |D(w(i, j) * w(i, j + 1)^-1)^-1 - n| * 2^-1 mod n if |D(w(i, j) * w(i, j + 1)^-1)^-1| >= n/2
    if m_decrypted_ij_plus_1 >= n / 2:
        m_decrypted_ij_plus_1 = ((n - mod_inverse(decrypt(w_prod, private_key), n)) * mod_inverse(2, n)) % n

    return m_decrypted_ij, m_decrypted_ij_plus_1

def main():
    # Read the watermarked encrypted image and convert it to 8-bit grayscale if needed
    watermarked_encrypted_img = cv2.imread('watermarked_encrypted_image.png')
    height, width, _ = watermarked_encrypted_img.shape

    # Generate the private key for decryption
    public_key, private_key, lambda_n = generate_keypair()

    # Decrypt the neighboring pixel pairs in the watermarked encrypted image
    decrypted_img = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width - 1):
            r1, g1, b1 = watermarked_encrypted_img[y, x]
            r2, g2, b2 = watermarked_encrypted_img[y, x + 1]

            # Convert color pixels back to ciphertext values
            c1 = color_pixel_to_ciphertext(r1, g1, b1)
            c2 = color_pixel_to_ciphertext(r2, g2, b2)

            # Decrypt the ciphertext pixel pairs
            m_decrypted_ij, m_decrypted_ij_plus_1 = decrypt_pixel_pair(c1, c2, private_key)

            # Update the pixel values in the decrypted image
            decrypted_img[y, x] = m_decrypted_ij
            decrypted_img[y, x + 1] = m_decrypted_ij_plus_1

    # Display the decrypted image
    cv2.imshow('Decrypted Image', decrypted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

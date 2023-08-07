import tkinter as tk
from tkinter import filedialog
from paillier0408232 import *
import cv2
import numpy as np
from watermarkemb import embed_watermark
from data_hiding_key import generate_data_hiding_key
import importlib





def read_image_gray(image_path):
    # Read the image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Convert the image to 8-bit grayscale if it is not already
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)

    return img

def encrypt_pixel_pair(m_ij, m_ij_plus_1, n, g):
    # Convert image pixels to integers
    m_ij_int = int(m_ij)
    m_ij_plus_1_int = int(m_ij_plus_1)

    r_i_j = random.randint(1, n)
    r_i_j_plus_1 = random.randint(1, n)

    # Calculate c1 using the equation: c(i, j + 1) = E(m(i, j), r(i, j))·E(m(i, j + 1), r(i, j + 1))
    c1 = encrypt(m_ij_int, n, g, r_i_j) * encrypt(m_ij_plus_1_int, n, g, r_i_j_plus_1) % (n ** 2)

    # Try to calculate c2 using the equation: c(i, j + 1) = inv(c1) = c1^(-1) mod n**2
    try:
        c2 = pow(c1, -1, n ** 2)
    except ValueError:
        # If c1 is not invertible, choose different values for m_ij and m_ij_plus_1
        # You can handle this case based on your specific requirements
        # For simplicity, we will set c2 to be equal to c1
        c2 = c1

    # Reduce the ciphertext values to fit within the range of uint8
    c1 = c1 % 256
    c2 = int(c2) % 256

    return c1, c2


def decrypt_pixel_pair(c1, c2, private_key):
    n, _, lambda_n, _, _, _ = private_key
    m_decrypted_ij = decrypt(c1, private_key)
    m_decrypted_ij_plus_1 = decrypt(c2, private_key)

    # Update the pixel values in the decrypted image
    img[y, x] = m_decrypted_ij
    img[y, x + 1] = m_decrypted_ij_plus_1
    
    

def describe_as_color_pixel(ciphertext):
    # Convert the ciphertext to 24-bit color pixel values
    r = ciphertext // (256 ** 2)
    g = (ciphertext % (256 ** 2)) // 256
    b = ciphertext % 256
    return r, g, b


def detect_watermark(w_ij, w_ij_plus_1):
    # Detect watermark bit b based on whether w(i, j) >= w(i, j + 1)
    if w_ij >= w_ij_plus_1:
        return 1
    else:
        return 0



def main():
    

    p = generate_prime1()
    q = generate_prime1()

    n = p * q
    g = n + 1

    root = tk.Tk()
    root.withdraw()

    # Open a file dialog for image selection
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not file_path:
        print("Image selection canceled.")
        return
    
   

   # Read the image and convert it to 8-bit grayscale if needed
    img = read_image_gray(file_path)
    height, width = img.shape
    
    # Define the number of bits for key generation
    n_length = 1024
    
    
    # Generate the data hiding key
    data_hiding_key = generate_data_hiding_key(height, width)

      # Generate the embedding sequence using the data hiding key
    watermark_sequence = data_hiding_key

   # Encrypt the neighboring pixels and modify the image
    for y in range(height):
        for x in range(width - 1):
            m_ij, m_ij_plus_1 = img[y, x], img[y, x + 1]
            c1, c2 = encrypt_pixel_pair(m_ij, m_ij_plus_1, n, g)

            # Embed watermark in encrypted pixels
            b = watermark_sequence[y, x]  # Get the watermark bit for the current pixel group
            w_ij, w_ij_plus_1 = embed_watermark(c1, c2, b)

            # Update the neighboring pixels in the image with watermarked encrypted values
            img[y, x] = w_ij
            img[y, x + 1] = w_ij_plus_1

    # Describe watermarked ciphertext values as 24-bit color pixels
    watermarked_ciphertext_img = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            r, g, b = describe_as_color_pixel(img[y, x])
            watermarked_ciphertext_img[y, x] = (r, g, b)
            
    cv2.imwrite('watermarked_encrypted_image.png', watermarked_ciphertext_img)

    # Display the watermarked encrypted image
    cv2.imshow('Watermarked Encrypted Image', watermarked_ciphertext_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    # # Detect watermark using the watermark sequence and watermarked encrypted image
    # detected_watermark = np.zeros((height, width), dtype=np.uint8)
    # for y in range(height):
    #     for x in range(width - 1):
    #         w_ij, w_ij_plus_1 = img[y, x], img[y, x + 1]
    #         detected_watermark[y, x] = detect_watermark(w_ij, w_ij_plus_1)

    # # Display the detected watermark sequence
    # print("Detected Watermark Sequence:")
    # print(detected_watermark)
    # public_key, private_key, lambda_n = generate_keypair()
    # m_decrypted_ij = decrypt(c1, private_key)
    # m_decrypted_ij_plus_1 = decrypt(c2, private_key)

    # # Update the pixel values in the decrypted image
    # img[y, x] = m_decrypted_ij
    # img[y, x + 1] = m_decrypted_ij_plus_1

    # # Display the decrypted image
    # cv2.imshow('Decrypted Image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    main()


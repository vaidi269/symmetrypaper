# extract_watermark.py

import cv2
import numpy as np
from watermarkemb import embed_watermark
from data_hiding_key import generate_data_hiding_key

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

def detect_watermark(w_ij, w_ij_plus_1):
    # Detect watermark bit b based on whether w(i, j) >= w(i, j + 1)
    if w_ij >= w_ij_plus_1:
        return 1
    else:
        return 0

def main():
    # Read the watermarked encrypted image and convert it to 8-bit grayscale if needed
    watermarked_encrypted_img = read_image_gray('watermarked_encrypted_image.png')
    height, width = watermarked_encrypted_img.shape

    # Generate the data hiding key
    data_hiding_key = generate_data_hiding_key(height, width)

    # Extract the watermark from the watermarked encrypted image
    detected_watermark = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width - 1):
            w_ij, w_ij_plus_1 = watermarked_encrypted_img[y, x], watermarked_encrypted_img[y, x + 1]
            detected_watermark[y, x] = detect_watermark(w_ij, w_ij_plus_1)

    # Display the detected watermark sequence
    print("Detected Watermark Sequence:")
    print(detected_watermark)

if __name__ == "__main__":
    main()

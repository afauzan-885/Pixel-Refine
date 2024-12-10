import cv2
import numpy as np
from numpy.fft import fft2, ifft2

def FFT_algorithm_name():
    return "FFT (Medium precision)"

def FFT_algorithm_description():
    return (
        "The Fast Fourier Transform (FFT) algorithm uses frequency domain analysis to calculate phase correlation "
        "for image alignment. By analyzing the frequency components of two images, this algorithm determines the "
        "translation required to align them accurately. It is especially useful for detecting shifts or displacements between images.\n\n"
        "Source: \n"
        "This project is taken from: https://github.com/khufkens/align_images/tree/master\n"
        "Author: Khufkens, October 2021"
    )
    
def translation(image_path_1, image_path_2, output_path):
    # Membaca gambar
    im0 = cv2.imread(image_path_1)
    im1 = cv2.imread(image_path_2)

    # Mengonversi gambar menjadi grayscale
    im0_gray = cv2.cvtColor(im0, cv2.COLOR_BGR2GRAY)
    im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)

    # Melakukan FFT pada kedua gambar
    f0 = fft2(im0_gray)
    f1 = fft2(im1_gray)

    # Menghitung korelasi fase
    ir = abs(ifft2((f0 * f1.conjugate()) / (abs(f0) * abs(f1))))
    t0, t1 = np.unravel_index(np.argmax(ir), ir.shape)

    # Menyesuaikan translasi
    if t0 > ir.shape[0] // 2:
        t0 -= ir.shape[0]
    if t1 > ir.shape[1] // 2:
        t1 -= ir.shape[1]

    # Menggeser gambar pertama sesuai dengan pergeseran yang ditemukan
    rows, cols = im0.shape[:2]
    translation_matrix = np.float32([[1, 0, t1], [0, 1, t0]])
    im0_aligned = cv2.warpAffine(im0, translation_matrix, (cols, rows))

    # Menyimpan gambar yang sudah diselaraskan
    cv2.imwrite(output_path, im0_aligned)
    return output_path

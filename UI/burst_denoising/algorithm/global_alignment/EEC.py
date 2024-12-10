import cv2
import numpy as np

def EEC_algorithm_name():
    return "EEC (High precision)"

def EEC_algorithm_description():
    return (
        "The Enhanced Correlation Coefficient (EEC) algorithm is a high-precision method for image alignment. "
        "It calculates transformation matrices using cross-correlation techniques to achieve the best fit between images. "
        "This algorithm is particularly effective for aligning consecutive images with moving objects, making it ideal for tasks such as image stacking.\n\n"
        "Source: \n"
        "This project is taken from: https://github.com/khufkens/align_images/tree/master\n"
        "Author: Khufkens, October 2021"
    )

def eccAlign(image_path_1, image_path_2, output_path, iterations=5000, termination_eps=1e-8):
    # Membaca gambar
    im1 = cv2.imread(image_path_1)
    im2 = cv2.imread(image_path_2)

    # Mengonversi gambar menjadi grayscale
    im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # Mendapatkan ukuran gambar
    sz = im1.shape

    # Menentukan mode gerakan
    warp_mode = cv2.MOTION_EUCLIDEAN

    # Menentukan matriks transformasi
    if warp_mode == cv2.MOTION_HOMOGRAPHY:
        warp_matrix = np.eye(3, 3, dtype=np.float32)
    else:
        warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Menentukan kriteria penghentian
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iterations, termination_eps)

    # Menjalankan algoritma ECC
    (cc, warp_matrix) = cv2.findTransformECC(im1_gray, im2_gray, warp_matrix, warp_mode, criteria)

    # Menyelaraskan gambar
    if warp_mode == cv2.MOTION_HOMOGRAPHY:
        im2_aligned = cv2.warpPerspective(im2, warp_matrix, (sz[1], sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else:
        im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1], sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

    # Menyimpan gambar yang sudah diselaraskan ke output
    cv2.imwrite(output_path, im2_aligned)
    return output_path



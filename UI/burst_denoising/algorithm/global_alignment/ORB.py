import cv2
import numpy as np

def ORB_algorithm_name():
    return "ORB (Low precision)"

def ORB_algorithm_description():
    return (
        "The ORB algorithm is a feature-based alignment method that detects keypoints and computes descriptors "
        "for matching features between two images. By identifying corresponding points, it calculates a transformation "
        "matrix to align the images. This algorithm is efficient and robust, making it suitable for real-time applications.\n\n"
        "Source: \n"
        "This project is taken from: https://github.com/khufkens/align_images/tree/master\n"
        "Author: Khufkens, October 2021"
    )

def featureAlign(image_path_1, image_path_2, output_path, max_features=5000, feature_retention=0.15):
    # Membaca gambar
    im1 = cv2.imread(image_path_1)
    im2 = cv2.imread(image_path_2)

    # Mengonversi gambar menjadi grayscale
    im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # Deteksi fitur ORB
    orb = cv2.ORB_create(max_features)
    keypoints1, descriptors1 = orb.detectAndCompute(im1_gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(im2_gray, None)

    # Mencocokkan fitur
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)

    # Mengurutkan hasil pencocokan berdasarkan skor
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Menyaring hasil pencocokan yang buruk
    num_good_matches = int(len(matches) * feature_retention)
    matches = matches[:num_good_matches]

    # Menarik posisi titik yang cocok
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Mencari homografi
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    # Menyelaraskan gambar dengan menggunakan homografi
    height, width, channels = im2.shape
    im1_reg = cv2.warpPerspective(im1, h, (width, height))

    # Menyimpan gambar yang sudah diselaraskan
    cv2.imwrite(output_path, im1_reg)
    return output_path

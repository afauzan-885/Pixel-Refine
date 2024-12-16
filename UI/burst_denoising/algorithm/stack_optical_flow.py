import cv2
import numpy as np

# Fungsi untuk membaca dan memproses gambar
def read_images(image_paths):
    images = [cv2.imread(img_path) for img_path in image_paths]
    return images

# Fungsi untuk menghitung optical flow
def calculate_optical_flow(base_image, target_image):
    base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
    target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    
    # Menggunakan Farneback Optical Flow
    flow = cv2.calcOpticalFlowFarneback(base_gray, target_gray, None, 
                                        pyr_scale=0.5, levels=3, winsize=15,
                                        iterations=3, poly_n=5, poly_sigma=1.2, flags=0)
    return flow

# Fungsi untuk menerapkan kompensasi gerakan (warp image)
def compensate_motion(base_image, flow):
    h, w = base_image.shape[:2]
    flow_map = np.column_stack(np.meshgrid(np.arange(w), np.arange(h)))
    warped_map = flow_map + flow
    remap_x, remap_y = cv2.split(warped_map.astype(np.float32))
    return cv2.remap(base_image, remap_x, remap_y, interpolation=cv2.INTER_LINEAR)

# Fungsi untuk menumpuk gambar
def stack_images(images, method='average'):
    stack = np.zeros_like(images[0], dtype=np.float32)
    for img in images:
        stack += img.astype(np.float32)
    if method == 'average':
        stack /= len(images)
    return np.clip(stack, 0, 255).astype(np.uint8)

# Path gambar
image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]

# Langkah-langkah proses
images = read_images(image_paths)

# Gunakan gambar pertama sebagai referensi
base_image = images[0]
aligned_images = [base_image]

for i in range(1, len(images)):
    flow = calculate_optical_flow(base_image, images[i])
    aligned_image = compensate_motion(images[i], flow)
    aligned_images.append(aligned_image)

# Tumpuk gambar dengan rata-rata
result = stack_images(aligned_images, method='average')

# Simpan hasil
cv2.imwrite("hdr_result.jpg", result)

# Tampilkan hasil
cv2.imshow("HDR Result", result)
cv2.waitKey(0)
cv2.destroyAllWindows()

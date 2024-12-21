import glob
import os
import cv2
import h5py
import numpy


def save_individual_image(self, image, image_id):
    """
    Save individual aligned image to disk.
    """
    debug_image_path = os.path.join(self.debug_folder, f"aligned_image_{image_id}.png")
    cv2.imwrite(debug_image_path, image)
    print(f"Gambar yang diselaraskan disimpan ke {debug_image_path}.")
    del image


def save_to_hdf5(self, aligned_images):
    """
    Save images in debug folder to HDF5 file.
    """
    print(f"Menyimpan gambar yang diselaraskan ke HDF5: {self.hdf5_path}")
    with h5py.File(self.hdf5_path, "w") as h5f:
        for i, image in enumerate(aligned_images):
            h5f.create_dataset(f"image_{i}", data=image, compression="gzip")
            print(f"Gambar ke-{i} disimpan dalam HDF5.")
    print(f"Semua gambar berhasil disimpan ke HDF5.")


def delete_debug_images(self):
    """
    Delete all images in the debug folder to free up space.
    """
    print("Menghapus gambar di folder debug...")
    for image_file in glob.glob(os.path.join(self.debug_folder, "*.png")):
        os.remove(image_file)
        print(f"Gambar {image_file} dihapus.")
    print("Semua gambar debug berhasil dihapus.")


def split_image(image, rows, cols):
    """
    Membagi gambar menjadi beberapa bagian kecil.
    """
    h, w = image.shape[:2]
    split_images = []
    for i in range(rows):
        for j in range(cols):
            y_start = i * h // rows
            y_end = (i + 1) * h // rows
            x_start = j * w // cols
            x_end = (j + 1) * w // cols
            split_images.append(image[y_start:y_end, x_start:x_end])
    return split_images


def merge_images(parts, rows, cols, image_shape):
    """
    Menggabungkan gambar yang telah diproses menjadi satu gambar utuh.
    """
    h, w = image_shape[:2]  # Ambil hanya dimensi tinggi dan lebar (h, w)
    merged_image = numpy.zeros(
        (h, w, 3), dtype=numpy.uint8
    )  # Pastikan dimensi akhir ada 3 saluran warna
    part_idx = 0
    for i in range(rows):
        for j in range(cols):
            y_start = i * h // rows
            y_end = (i + 1) * h // rows
            x_start = j * w // cols
            x_end = (j + 1) * w // cols
            merged_image[y_start:y_end, x_start:x_end] = parts[part_idx]
            part_idx += 1
    return merged_image

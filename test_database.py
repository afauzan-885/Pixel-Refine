import numpy as np
import h5py
import os

# --- Fungsi Inti yang Ingin Kita Buktikan ---
def save_raw_weight_maps(weight_maps_list, database_path):
    """
    Menyimpan atau menambahkan peta bobot mentah ke database HDF5.
    Setiap peta bobot disimpan sebagai dataset terpisah dengan ID unik.
    """
    if not weight_maps_list:
        print("Tidak ada peta bobot untuk disimpan.")
        return
    
    # Buka file dalam mode 'a' (append), yang akan membuat file jika belum ada.
    with h5py.File(database_path, 'a') as hf:
        # Cari ID terakhir untuk menentukan ID awal yang baru.
        existing_ids = [int(k.split('_')[-1]) for k in hf.keys() if k.startswith('weight_map_')]
        last_id = max(existing_ids) if existing_ids else -1
        
        print(f"\nMenyimpan {len(weight_maps_list)} peta bobot baru...")
        print(f"  ID terakhir di database: {last_id}")

        for i, w_map in enumerate(weight_maps_list):
            new_id = last_id + 1 + i
            dataset_name = f'weight_map_{new_id}'
            hf.create_dataset(dataset_name, data=w_map, compression="gzip")
            print(f"  -> Menyimpan dataset '{dataset_name}' ke dalam file '{os.path.basename(database_path)}'")
            
def inspect_h5_database(database_path):
    """Membaca dan menampilkan isi dari file database HDF5."""
    if not os.path.exists(database_path):
        print(f"Database '{database_path}' tidak ditemukan.")
        return
        
    with h5py.File(database_path, 'r') as hf:
        print("\n--- Inspeksi Isi Database HDF5 ---")
        print(f"File: {os.path.basename(database_path)}")
        
        keys = list(hf.keys())
        if not keys:
            print("  Database kosong.")
            return
            
        print(f"  Total dataset di dalam file: {len(keys)}")
        print("  Daftar dataset (kunci):")
        for key in sorted(keys, key=lambda x: int(x.split('_')[-1])):
            dataset = hf[key]
            print(f"    - Nama: {key}, Bentuk Data: {dataset.shape}, Tipe Data: {dataset.dtype}")
        print("----------------------------------")

# --- Skenario Simulasi ---
if __name__ == "__main__":
    # Tentukan nama file database kita
    DB_FILENAME = "raw_weight_map_database_TEST.h5"

    # Hapus file lama jika ada untuk memulai dari awal
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)
        print(f"File database lama '{DB_FILENAME}' telah dihapus untuk memulai tes.")

    # === SESI KOLEKSI DATA PERTAMA ===
    print("\n>>> Memulai Sesi Koleksi Data #1")
    # Buat beberapa data peta bobot dummy (misal, hasil dari batch pertama)
    batch1_maps = [
        np.random.rand(10, 10) * 1,
        np.random.rand(10, 10) * 2
    ]
    save_raw_weight_maps(batch1_maps, DB_FILENAME)
    inspect_h5_database(DB_FILENAME)

    # === SESI KOLEKSI DATA KEDUA ===
    print("\n>>> Memulai Sesi Koleksi Data #2 (Mode 'Hanya Koleksi')")
    # Buat data peta bobot baru lagi (misal, hasil dari batch kedua)
    batch2_maps = [
        np.random.rand(10, 10) * 3,
        np.random.rand(10, 10) * 4,
        np.random.rand(10, 10) * 5
    ]
    # Panggil fungsi yang sama. Ia akan melanjutkan dari ID terakhir.
    save_raw_weight_maps(batch2_maps, DB_FILENAME)
    inspect_h5_database(DB_FILENAME)

    # Hapus file tes setelah selesai
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)
        print(f"\nTes selesai. File '{DB_FILENAME}' telah dihapus.")
# File: shrink_model.py
# Deskripsi: Skrip untuk memuat model pengetahuan yang besar, mengecilkannya
#            dengan memotong komponen PCA, dan menyimpannya kembali.
# Cara Pakai: Jalankan dari terminal, contoh:
# python shrink_model.py -n 30 
# (Ini akan menggunakan path default dan memotong model menjadi 30 komponen)

import os
import joblib
import numpy as np
import argparse  # Untuk menerima argumen dari baris perintah
from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans

def shrink_existing_model(
    input_model_path: str,
    output_model_path: str,
    new_n_components: int,
    quantize_to_float16: bool = True
):
    """
    Memuat model pengetahuan yang besar, mengecilkannya, dan menyimpannya kembali.

    Args:
        input_model_path (str): Path ke file model besar (.pkl).
        output_model_path (str): Path untuk menyimpan file model yang sudah dikecilkan.
        new_n_components (int): Jumlah komponen PCA teratas yang ingin dipertahankan.
        quantize_to_float16 (bool): Jika True, akan mengurangi presisi ke float16.
    """
    print(f"Membaca model besar dari: {input_model_path}")
    if not os.path.exists(input_model_path):
        print(f"Error: File model input '{input_model_path}' tidak ditemukan.")
        print("Pastikan Anda sudah melatih model setidaknya sekali dengan 'perform_learning=True'.")
        return

    try:
        model_data = joblib.load(input_model_path)
        pca_large = model_data['pca']
        kmeans_large = model_data['kmeans']
    except Exception as e:
        print(f"Error saat memuat model: {e}")
        return

    # --- Validasi Input ---
    original_n_components = pca_large.n_components_
    if new_n_components >= original_n_components:
        print(f"Error: Jumlah komponen baru ({new_n_components}) harus lebih kecil dari jumlah komponen asli ({original_n_components}).")
        return
        
    print(f"Model asli memiliki {original_n_components} komponen PCA.")
    print(f"Target pengecilan: {new_n_components} komponen.")

    # --- Langkah 1: Memotong (Truncate) Model PCA ---
    print("Memotong komponen PCA yang tidak penting...")
    
    pca_small = PCA(n_components=new_n_components)
    
    # Salin atribut-atribut penting yang sudah dipotong
    pca_small.mean_ = pca_large.mean_
    pca_small.components_ = pca_large.components_[:new_n_components, :] # Pemotongan utama
    pca_small.explained_variance_ = pca_large.explained_variance_[:new_n_components]
    pca_small.explained_variance_ratio_ = pca_large.explained_variance_ratio_[:new_n_components]
    pca_small.singular_values_ = pca_large.singular_values_[:new_n_components]
    pca_small.n_features_in_ = pca_large.n_features_in_
    pca_small.n_samples_ = pca_large.n_samples_
    
    # --- Langkah 2: Menyesuaikan K-Means ---
    print("Menyesuaikan pusat cluster K-Means dengan ruang PCA yang baru...")
    
    centers_in_large_space = kmeans_large.cluster_centers_
    centers_in_small_space = centers_in_large_space[:, :new_n_components]

    kmeans_small = MiniBatchKMeans(n_clusters=kmeans_large.n_clusters, n_init=1, random_state=42)
    # Inisialisasi K-Means dengan data dummy, lalu timpa pusat clusternya
    dummy_data = np.zeros((kmeans_large.n_clusters, new_n_components))
    kmeans_small.fit(dummy_data)
    kmeans_small.cluster_centers_ = centers_in_small_space

    # --- Langkah 3: Kuantisasi Tipe Data (Opsional) ---
    if quantize_to_float16:
        print("Mengurangi presisi model ke float16 untuk ukuran file lebih kecil...")
        try:
            pca_small.mean_ = pca_small.mean_.astype(np.float16)
            pca_small.components_ = pca_small.components_.astype(np.float16)
            kmeans_small.cluster_centers_ = kmeans_small.cluster_centers_.astype(np.float16)
        except Exception as e:
            print(f"Gagal melakukan kuantisasi: {e}")

    # --- Langkah 4: Simpan Model yang Sudah Dikecilkan ---
    new_model_data = {
        'pca': pca_small,
        'kmeans': kmeans_small,
        'original_shape': model_data.get('original_shape'),
        'training_resolution': model_data.get('training_resolution') # Pertahankan resolusi training jika ada
    }

    try:
        original_size = os.path.getsize(input_model_path)
        print(f"\nUkuran model asli: {original_size / (1024*1024):.2f} MB")
        
        joblib.dump(new_model_data, output_model_path)
        
        new_size = os.path.getsize(output_model_path)
        print(f"Model baru berhasil disimpan ke: {output_model_path}")
        print(f"Ukuran model baru: {new_size / (1024*1024):.2f} MB")
        print(f"Ukuran berhasil dikurangi sebesar: {(original_size - new_size) / original_size:.2%}")
    except Exception as e:
        print(f"Gagal menyimpan model baru: {e}")


if __name__ == '__main__':
    # --- Membuat Path Absolut Berdasarkan Lokasi Skrip ---
    # Ini menyelesaikan masalah "file tidak ditemukan" dengan memastikan path selalu benar.
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Asumsi struktur: .../ProjectRoot/UI/enhance_stack/algorithm/denoising/
        # Kita naik 4 level untuk mencapai direktori root proyek
        project_root = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
    except NameError:
        # Fallback jika dijalankan di lingkungan interaktif di mana `__file__` tidak ada
        project_root = os.getcwd()

    default_input_path = os.path.join(project_root, "database", "knowledge_model.pkl")
    default_output_path = os.path.join(project_root, "database", "knowledge_model_small.pkl")
    
    # --- Konfigurasi Argumen Baris Perintah ---
    parser = argparse.ArgumentParser(
        description="Mengecilkan ukuran model PCA+K-Means yang sudah ada dengan memotong komponen dan mengurangi presisi.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input", 
        default=default_input_path, 
        help=f"Path ke file model besar yang akan dikecilkan.\nDefault: {default_input_path}"
    )
    parser.add_argument(
        "-o", "--output", 
        default=default_output_path, 
        help=f"Path untuk menyimpan file model baru yang sudah dikecilkan.\nDefault: {default_output_path}"
    )
    parser.add_argument(
        "-n", "--n_components", 
        type=int, 
        required=True, 
        help="Jumlah komponen PCA teratas yang ingin dipertahankan (misal: 30).\nIni adalah parameter wajib."
    )
    parser.add_argument(
        "--no-quantize", 
        action="store_true", 
        help="Gunakan flag ini untuk TIDAK melakukan kuantisasi ke float16."
    )

    args = parser.parse_args()

    # Panggil fungsi utama dengan argumen yang sudah divalidasi
    shrink_existing_model(
        input_model_path=args.input,
        output_model_path=args.output,
        new_n_components=args.n_components,
        quantize_to_float16=not args.no_quantize
    )
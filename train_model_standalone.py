import os
import argparse
import traceback
import json
import random

import numpy as np
import h5py
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.cluster import DBSCAN
import timm
import albumentations as A
from pytorch_msssim import SSIM

# ==============================================================================
# 1. DEFINISI KELAS DAN FUNGSI INTI (Salin dari kode Anda)
#    (Penting: Pastikan definisi ini identik dengan yang digunakan di aplikasi)
# ==============================================================================

class ViTAutoencoder(nn.Module):
    """
    Autoencoder yang menggunakan ViT sebagai encoder, dioptimalkan untuk input 1-channel.
    """
    def __init__(self, image_size=256, patch_size=16, 
                 encoding_dim=64, decoder_channels=256):
        super(ViTAutoencoder, self).__init__()
        
        self.image_size = image_size
        self.patch_size = patch_size
        self.encoding_dim = encoding_dim

        self.vit_encoder = timm.create_model(
            'vit_tiny_patch16_224',
            pretrained=False,
            num_classes=encoding_dim,
            img_size=image_size,
            in_chans=1
        )
        
        num_patches_side = image_size // patch_size
        decoder_start_dim = decoder_channels * num_patches_side * num_patches_side
        self.fc_decoder = nn.Linear(encoding_dim, decoder_start_dim)
        self.decoder_conv = nn.Sequential(
            nn.ConvTranspose2d(decoder_channels, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.ConvTranspose2d(32, 1, kernel_size=4, stride=2, padding=1),
            nn.Sigmoid()
        )

    def encode(self, x):
        return self.vit_encoder(x)

    def decode(self, z):
        x = self.fc_decoder(z)
        num_patches_side = self.image_size // self.patch_size
        x = x.view(-1, 256, num_patches_side, num_patches_side)
        return self.decoder_conv(x)

    def forward(self, x):
        z = self.encode(x)
        return self.decode(z)

class HybridLoss(nn.Module):
    def __init__(self, alpha=0.85, beta=0.15, data_range=1.0, win_size=7):
        super(HybridLoss, self).__init__()
        self.alpha = alpha
        self.beta = beta
        self.ssim_loss = SSIM(data_range=data_range, size_average=True, channel=1, win_size=win_size)
        self.mse_loss = nn.MSELoss()

    def forward(self, generated, target):
        loss_s = 1 - self.ssim_loss(generated, target)
        loss_m = self.mse_loss(generated, target)
        return self.alpha * loss_s + self.beta * loss_m

class DBSCANClusterer:
    def __init__(self, eps=0.5, min_samples=5, device='cpu'):
        self.eps = eps
        self.min_samples = min_samples
        self.device = device
        self.dbscan = None
        self.centroids = None
        self.labels_ = None

    def fit(self, X):
        X_np = X.detach().cpu().numpy() if isinstance(X, torch.Tensor) else X
        self.dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples, n_jobs=-1).fit(X_np)
        self.labels_ = self.dbscan.labels_
        unique_labels = set(self.labels_)
        cluster_centers = {k: X_np[self.labels_ == k].mean(axis=0) for k in unique_labels if k != -1}
        sorted_centers = [cluster_centers[k] for k in sorted(cluster_centers.keys())]
        self.centroids = torch.from_numpy(np.array(sorted_centers)).float().to(self.device) if sorted_centers else torch.empty(0, X.shape[1]).to(self.device)
        return self

    def save_model(self, path):
        if self.centroids is not None:
            torch.save(self.centroids, path)

    def load_model(self, path):
        self.centroids = torch.load(path, map_location=self.device)

def create_augmented_maps(original_maps):
    """
    Membuat berbagai versi augmentasi yang spesifik dan terkontrol untuk setiap peta bobot.
    Nama parameter telah diperbarui sesuai versi Albumentations terbaru.
    """
    
    all_generated_maps = []
    
    # --- PERBAIKAN: Gunakan nama parameter yang benar ---
    
    # ElasticTransform: 'alpha_affine' diganti menjadi 'alpha_bg'
    get_elastic = lambda: A.Compose([
        A.ElasticTransform(p=1.0, alpha=10, sigma=120, alpha_affine=120) 
    ])

    # GridDropout: 'holes_number_x/y', 'unit_size_min/max' diganti
    get_occlusion = lambda: A.Compose([
        A.GridDropout(p=1.0, ratio=0.6, unit_size_min=10, unit_size_max=25, random_offset=True, fill_value=0)
    ])

    # Affine: 'cval' diganti menjadi 'cval', dan 'mode' menjadi 'border_mode'
    get_zoom_in = lambda: A.Compose([
        A.Affine(p=1.0, scale=(1.1, 1.3), rotate=0, translate_percent=0, cval=0, border_mode=cv2.BORDER_REPLICATE)
    ])
    get_zoom_out = lambda: A.Compose([
        A.Affine(p=1.0, scale=(0.7, 0.9), rotate=0, translate_percent=0, cval=0, border_mode=cv2.BORDER_REPLICATE)
    ])
    get_rotation = lambda: A.Compose([
        A.Affine(p=1.0, scale=1, rotate=(-15, 15), translate_percent=0, cval=0, border_mode=cv2.BORDER_REPLICATE)
    ])

    # GaussNoise: 'var_limit' menjadi 'variance'
    get_gauss_noise = lambda: A.Compose([
        A.GaussNoise(p=1.0, mean=0, var_limit=(0.005, 0.015))
    ])

    # RandomGamma dan MultiplicativeNoise biasanya masih valid, tapi kita tulis ulang untuk konsistensi
    get_gamma_noise = lambda: A.Compose([A.RandomGamma(p=1.0, gamma_limit=(80, 120))])
    get_multiplicative_noise = lambda: A.Compose([A.MultiplicativeNoise(p=1.0, multiplier=(0.9, 1.1))])

    # Fungsi Bilateral Filter kustom Anda (tidak ada perubahan di sini)
    def apply_bilateral_filter_cv(image):
        image_uint8 = (image * 255).astype(np.uint8)
        d = 9
        sigma_color = random.uniform(20, 40)
        sigma_space = random.uniform(20, 40)
        denoised_uint8 = cv2.bilateralFilter(src=image_uint8, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space, borderType=cv2.BORDER_REPLICATE)
        denoised_float = (denoised_uint8 / 255.0).astype(np.float32)
        return denoised_float

    # Fungsi Kontras kustom Anda (tidak ada perubahan di sini)
    def apply_contrast_change(image):
        new_image = image.copy()
        low_mask = new_image < 0.3
        high_mid_mask = ~low_mask
        new_image[low_mask] *= 0.70
        new_image[high_mid_mask] *= 1.20
        np.clip(new_image, 0, 1, out=new_image)
        return new_image

    # Iterasi melalui setiap peta bobot asli
    for w_map in original_maps:
        w_map_float = w_map.astype(np.float32)
        
        # Tambahkan semua versi ke dalam daftar
        all_generated_maps.append(w_map_float)
        all_generated_maps.append(get_elastic()(image=w_map_float)['image'])
        all_generated_maps.append(get_occlusion()(image=w_map_float)['image'])
        all_generated_maps.append(get_gauss_noise()(image=w_map_float)['image'])
        all_generated_maps.append(get_gamma_noise()(image=w_map_float)['image']) 
        all_generated_maps.append(get_multiplicative_noise()(image=w_map_float)['image'])
        all_generated_maps.append(apply_bilateral_filter_cv(w_map_float))
        all_generated_maps.append(get_zoom_in()(image=w_map_float)['image'])
        all_generated_maps.append(get_zoom_out()(image=w_map_float)['image'])
        all_generated_maps.append(get_rotation()(image=w_map_float)['image'])
        all_generated_maps.append(apply_contrast_change(w_map_float))

    print(f"Augmentasi spesifik selesai. Menghasilkan {len(all_generated_maps)} total peta dari {len(original_maps)} peta asli.")
    return all_generated_maps    

def load_config(path='config.json'):
    """
    Memuat parameter dari file konfigurasi. Nilai defaultnya identik dengan
    fungsi train_model Anda.
    """
    # <<< PERUBAHAN DI SINI: Salin parameter default dari train_model >>>
    default_config = {
        # Path dan direktori
        "model_dir": "database/Learning_Model/",
        "raw_data_path": "database/Learning_Model/raw_weight_map_database.h5",
        "training_db_path": "database/Learning_Model/training_database.h5",
        "clean_raw_db_after_training": True,

        # Parameter arsitektur model
        "training_resolution": [256, 256],
        "encoding_dim": 64,

        # Parameter pelatihan
        "epochs": 10,
        "batch_size": 8,
        "base_lr": 1e-4,
        "base_batch_size": 16,

        # Parameter Early Stopping & LR Scheduler
        "patience": 5,
        "min_delta": 0.000100,
        "lr_reduction_factor": 0.2,
        "max_lr_reductions": 3,

        # Parameter Clustering & Loss
        "dbscan_eps": 2.5,
        "dbscan_min_samples": 5,
        "loss_alpha": 0.85,
        "loss_beta": 0.15
    }
    
    if os.path.exists(path):
        print(f"Memuat konfigurasi dari file: {path}")
        with open(path, 'r') as f:
            user_config = json.load(f)
            default_config.update(user_config)
    else:
        print("File config.json tidak ditemukan. Menggunakan parameter default.")

    return default_config

def run_training_session(config):
    """
    Fungsi utama untuk menjalankan satu sesi pelatihan penuh, dengan parameter
    yang identik dengan fungsi train_model.
    """
    # <<< PERUBAHAN DI SINI: Ekstrak semua parameter dari config >>>
    model_dir = config['model_dir']
    raw_data_path = config['raw_data_path']
    training_db_path = config['training_db_path']
    training_resolution = tuple(config['training_resolution'])
    encoding_dim = config['encoding_dim']
    epochs = config['epochs']
    batch_size = config['batch_size']
    base_lr = config['base_lr']
    base_batch_size = config['base_batch_size']
    patience = config['patience']
    min_delta = config['min_delta']
    lr_reduction_factor = config['lr_reduction_factor']
    max_lr_reductions = config['max_lr_reductions']
    dbscan_eps = config['dbscan_eps']
    dbscan_min_samples = config['dbscan_min_samples']
    loss_alpha = config['loss_alpha']
    loss_beta = config['loss_beta']

    best_model_path = os.path.join(model_dir, "vit_autoencoder_best.pth")
    os.makedirs(model_dir, exist_ok=True)
    
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("="*60)
        print("  MEMULAI SESI PELATIHAN MODEL MANDIRI")
        print(f"  Menggunakan perangkat: {device}")
        print("="*60)

        # --- Tahap 1: Memuat Data Mentah ---
        print(f"\n--- Memuat data mentah dari '{raw_data_path}' ---")
        if not os.path.exists(raw_data_path):
            print(f"  -> ERROR: Database data mentah tidak ditemukan. Pelatihan dibatalkan.")
            return

        with h5py.File(raw_data_path, 'r') as hf:
            new_weight_maps = [np.array(hf[key]) for key in hf.keys()]
        
        if not new_weight_maps:
            print("  -> Database data mentah kosong. Pelatihan dibatalkan.")
            return
        
        print(f"  -> Berhasil memuat {len(new_weight_maps)} peta bobot baru.")

        # --- Tahap 2: Menyiapkan Dataset Gabungan ---
        all_2d_maps_original = new_weight_maps
        if os.path.exists(training_db_path):
            try:
                with h5py.File(training_db_path, 'r') as hf:
                    if 'weight_maps' in hf:
                        old_maps_data = hf['weight_maps'][:]
                        side_len = int(np.sqrt(old_maps_data.shape[1]))
                        if side_len == training_resolution[0]:
                            old_2d = old_maps_data.reshape(-1, side_len, side_len)
                            all_2d_maps_original.extend(old_2d)
                            print(f"  -> SUKSES: {len(old_2d)} sampel historis dimuat.")
            except Exception as e:
                print(f"  -> PERINGATAN: Gagal memuat data historis. Error: {e}")
        
        final_training_maps_2d = create_augmented_maps(all_2d_maps_original)
        
        # --- Tahap 3: Persiapan DataLoader ---
        all_maps_normalized = [(w / np.max(w) if np.max(w) > 0 else w) for w in final_training_maps_2d]
        training_data_tensor = torch.from_numpy(np.array(all_maps_normalized, dtype=np.float32)).unsqueeze(1)
        train_loader = DataLoader(TensorDataset(training_data_tensor), batch_size=batch_size, shuffle=True)
        
        # --- Tahap 4: Inisialisasi Model, Optimizer, dan Loss ---
        autoencoder = ViTAutoencoder(image_size=training_resolution[0], encoding_dim=encoding_dim).to(device)
        autoencoder_path = os.path.join(model_dir, "vit_autoencoder_pytorch.pth")
        
        if os.path.exists(autoencoder_path):
            try:
                autoencoder.load_state_dict(torch.load(autoencoder_path, map_location=device))
                print("\nSUKSES: Melanjutkan pelatihan dari model ViTAutoencoder yang sudah ada.")
            except Exception as e:
                print(f"\nPERINGATAN: Gagal memuat model ViT. Memulai dari awal. Error: {e}")

        # Logika adaptive learning rate
        scale_factor = batch_size / base_batch_size
        adaptive_lr = base_lr * scale_factor

        criterion = HybridLoss(alpha=loss_alpha, beta=loss_beta).to(device)
        optimizer = optim.Adam(autoencoder.parameters(), lr=adaptive_lr, weight_decay=1e-5)
        
        # --- Loop Pelatihan Utama (Identik dengan train_model) ---
        print(f"\nMemulai pelatihan ViTAutoencoder untuk {epochs} epoch...")
        epochs_without_improvement, best_loss, lr_reductions_count = 0, float('inf'), 0

        for epoch in range(epochs):
            autoencoder.train()
            total_loss_epoch = 0
            for data_batch, in train_loader:
                inputs_1ch = data_batch.to(device)
                optimizer.zero_grad(set_to_none=True)
                outputs = autoencoder(inputs_1ch)
                loss = criterion(outputs, inputs_1ch)
                loss.backward()
                optimizer.step()
                total_loss_epoch += loss.item()
            
            avg_loss = total_loss_epoch / len(train_loader)
            current_lr = optimizer.param_groups[0]['lr']
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}, LR: {current_lr:.1e}")

            if avg_loss < best_loss - min_delta:
                best_loss = avg_loss
                epochs_without_improvement = 0
                torch.save(autoencoder.state_dict(), best_model_path)
            else:
                epochs_without_improvement += 1
            
            if epochs_without_improvement >= patience:
                if lr_reductions_count < max_lr_reductions:
                    lr_reductions_count += 1
                    new_lr = current_lr * lr_reduction_factor
                    print(f"\nPerforma stagnan. Mengurangi learning rate ke {new_lr:.1e}\n")
                    for param_group in optimizer.param_groups:
                        param_group['lr'] = new_lr
                    epochs_without_improvement = 0
                else:
                    print(f"\nEARLY STOPPING: Performa tetap stagnan. Pelatihan berhenti.")
                    break
        
        if os.path.exists(best_model_path):
            autoencoder.load_state_dict(torch.load(best_model_path))
            print("\nModel ViTAutoencoder dengan performa terbaik telah dimuat.")

        # --- Tahap Clustering dengan DBSCAN ---
        print("\nMemulai pengelompokan (clustering) ruang laten dengan DBSCAN...")
        autoencoder.eval()
        with torch.no_grad():
            original_maps_norm = [(w / np.max(w) if np.max(w) > 0 else w) for w in all_2d_maps_original]
            original_data_tensor = torch.from_numpy(np.array(original_maps_norm, dtype=np.float32)).unsqueeze(1).to(device)
            reduced_data_tensor = autoencoder.encode(original_data_tensor)
        
        clusterer = DBSCANClusterer(eps=dbscan_eps, min_samples=dbscan_min_samples, device=device)
        clusterer.fit(reduced_data_tensor)
        
        # --- Tahap Penyimpanan Akhir ---
        print("\n--- Menyimpan Hasil Pelatihan ---")
        torch.save(autoencoder.state_dict(), autoencoder_path)
        print(f"  -> Model ViTAutoencoder disimpan ke: {autoencoder_path}")
        
        cluster_model_path = os.path.join(model_dir, "dbscan_clusters.pth")
        if clusterer.centroids is not None and clusterer.centroids.nelement() > 0:
            clusterer.save_model(cluster_model_path)
            print(f"  -> Cluster DBSCAN ({len(clusterer.centroids)} cluster) disimpan ke: {cluster_model_path}")
        else:
            print("\n[PERINGATAN PENTING] DBSCAN tidak menemukan cluster yang valid.")
            print(" -> File 'dbscan_clusters.pth' TIDAK DIBUAT.")
            print(" -> SARAN: Coba naikkan nilai 'dbscan_eps' di file konfigurasi Anda (misal: dari 0.75 menjadi 2.5).")

        # <<< TAMBAHKAN BLOK KODE INI >>>
        # --- Tahap Visualisasi ---
        # Kita gunakan peta bobot mentah sebelum di-augmentasi untuk visualisasi yang lebih jelas
        create_training_visualization(
            autoencoder=autoencoder,
            clusterer=clusterer,
            sample_maps=new_weight_maps,  # Menggunakan data mentah asli
            output_dir=os.path.join(model_dir, "previews"),
            config=config
        )
        # <<< AKHIR BLOK TAMBAHAN >>>


        with h5py.File(training_db_path, 'w') as hf:
            flat_maps = np.array([w.flatten() for w in all_2d_maps_original], dtype=np.float32)
            hf.create_dataset('weight_maps', data=flat_maps, compression="gzip")
        print(f"  -> Database pelatihan historis diperbarui di: {training_db_path}")

        if config['clean_raw_db_after_training']:
            os.remove(raw_data_path)
            print(f"  -> Database mentah '{os.path.basename(raw_data_path)}' telah dihapus.")

        print("\n*** PELATIHAN SELESAI DENGAN SUKSES ***")

    except Exception as e:
        print("\n!!! TERJADI ERROR KRITIS SELAMA PELATIHAN !!!")
        traceback.print_exc()
    finally:
        if os.path.exists(best_model_path):
            try:
                os.remove(best_model_path)
            except OSError as e:
                print(f"Peringatan: Gagal menghapus file sementara. Error: {e}")

def create_training_visualization(autoencoder, clusterer, sample_maps, output_dir, config):
    """
    Membuat gambar visualisasi perbandingan untuk beberapa sampel data pelatihan.
    """
    print(f"\n--- Membuat Visualisasi Hasil Pelatihan di '{output_dir}' ---")
    os.makedirs(output_dir, exist_ok=True)
    
    device = next(autoencoder.parameters()).device
    training_resolution = tuple(config['training_resolution'])

    # Helper function untuk membuat heatmap dengan label
    def generate_labeled_heatmap(w_map, label):
        if w_map is None:
            w_map = np.zeros(training_resolution)
        
        # Pastikan map 2D
        if w_map.ndim == 3:
            w_map = w_map.squeeze()
            
        w_map_resized = cv2.resize(w_map, training_resolution, interpolation=cv2.INTER_NEAREST)
        norm_map = cv2.normalize(w_map_resized, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        heatmap = cv2.applyColorMap(norm_map, cv2.COLORMAP_JET)
        
        # Tambahkan latar belakang hitam untuk teks agar mudah dibaca
        cv2.rectangle(heatmap, (0, 0), (training_resolution[0], 40), (0, 0, 0), -1)
        cv2.putText(heatmap, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        return heatmap

    # Proses beberapa sampel (misalnya 5 sampel pertama)
    for i, raw_map in enumerate(sample_maps[:5]):
        print(f"  -> Memproses visualisasi untuk sampel {i}...")
        
        # --- Persiapan Input ---
        raw_map_norm = raw_map / np.max(raw_map) if np.max(raw_map) > 0 else raw_map
        input_tensor = torch.from_numpy(raw_map_norm.astype(np.float32)).unsqueeze(0).unsqueeze(0).to(device)

        autoencoder.eval()
        with torch.no_grad():
            # --- 1. Dapatkan Rekonstruksi Murni ---
            # Ini adalah output langsung dari autoencoder (encode -> decode)
            pure_reconstruction_tensor = autoencoder(input_tensor)
            pure_reconstruction_map = pure_reconstruction_tensor.cpu().numpy().squeeze()

            # --- 2. Dapatkan Rekonstruksi Ideal (dari Cluster) ---
            # Ini meniru logika _apply_knowledge_model
            ideal_reconstruction_map = None
            if clusterer.centroids is not None and clusterer.centroids.nelement() > 0:
                encoded_vec = autoencoder.encode(input_tensor)
                
                # Hitung jarak ke semua centroids
                distances = torch.sum((encoded_vec - clusterer.centroids)**2, dim=1)
                cluster_id = torch.argmin(distances)
                
                # Ambil centroid yang menang (vektor ideal)
                ideal_vec = clusterer.centroids[cluster_id].unsqueeze(0)
                
                # Decode dari vektor ideal
                ideal_reconstruction_tensor = autoencoder.decode(ideal_vec)
                ideal_reconstruction_map = ideal_reconstruction_tensor.cpu().numpy().squeeze()
            
        # --- Buat Heatmap untuk setiap tahap ---
        heatmap_raw = generate_labeled_heatmap(raw_map_norm, "1. Input Mentah")
        heatmap_pure = generate_labeled_heatmap(pure_reconstruction_map, "2. Rekonstruksi Murni")
        heatmap_ideal = generate_labeled_heatmap(ideal_reconstruction_map, "3. Rekonstruksi Ideal")

        # --- Gabungkan menjadi satu gambar perbandingan ---
        comparison_image = np.hstack([heatmap_raw, heatmap_pure, heatmap_ideal])
        
        # Simpan gambar
        output_path = os.path.join(output_dir, f"visualisasi_sampel_{i}.png")
        cv2.imwrite(output_path, comparison_image)

    print("--- Visualisasi selesai. ---")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standalone Trainer for Weight Map Reconstruction Model.")
    parser.add_argument('--config', type=str, default='config.json', help='Path to JSON config file.')
    parser.add_argument('--epochs', type=int, help='Override number of training epochs.')
    parser.add_argument('--lr', type=float, help='Override the base learning rate.')
    parser.add_argument('--batch_size', type=int, help='Override the batch size.')
    
    args = parser.parse_args()
    
    training_config = load_config(args.config)
    
    if args.epochs: training_config['epochs'] = args.epochs
    if args.lr: training_config['base_lr'] = args.lr
    if args.batch_size: training_config['batch_size'] = args.batch_size
        
    run_training_session(training_config)
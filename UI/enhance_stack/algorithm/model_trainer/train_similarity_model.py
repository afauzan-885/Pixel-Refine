import random
import timm
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import cv2
import os
import h5py
import albumentations as A
import traceback
from sklearn.cluster import DBSCAN
from pytorch_msssim import SSIM

class ViTAutoencoder(nn.Module):
    """
    Autoencoder yang menggunakan Vision Transformer (ViT) sebagai encoder
    dan decoder berbasis konvolusi terbalik untuk merekonstruksi gambar.
    """
    def __init__(self, image_size=256, patch_size=16, 
                 encoding_dim=64, decoder_channels=256):
        super(ViTAutoencoder, self).__init__()
        
        self.image_size = image_size
        self.patch_size = patch_size
        self.encoding_dim = encoding_dim

        # 1. Encoder: Menggunakan ViT dari pustaka 'timm'
        # Kita menggunakan model 'tiny' agar tidak terlalu berat secara komputasi.
        # `num_classes` kita gunakan sebagai dimensi ruang laten (encoding_dim).
        self.vit_encoder = timm.create_model(
            'vit_tiny_patch16_224',
            pretrained=False,
            num_classes=encoding_dim,
            img_size=image_size 
        )
        
        # 2. Decoder: Mirip dengan CAE sebelumnya, untuk upsampling
        num_patches_side = image_size // patch_size
        decoder_start_dim = decoder_channels * num_patches_side * num_patches_side
        
        self.fc_decoder = nn.Linear(encoding_dim, decoder_start_dim)

        # Lapisan konvolusi terbalik untuk merekonstruksi gambar.
        self.decoder_conv = nn.Sequential(
            # Input: B x 256 x 16 x 16
            nn.ConvTranspose2d(decoder_channels, 128, kernel_size=4, stride=2, padding=1), # -> B x 128 x 32 x 32
            nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),  # -> B x 64 x 64 x 64
            nn.ReLU(True),
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),   # -> B x 32 x 128 x 128
            nn.ReLU(True),
            nn.ConvTranspose2d(32, 1, kernel_size=4, stride=2, padding=1),    # -> B x 1 x 256 x 256
            nn.Sigmoid() # Pastikan output antara 0 dan 1
        )

    def encode(self, x):
        # ViT encoder langsung menghasilkan vektor fitur dengan dimensi `encoding_dim`
        return self.vit_encoder(x)

    def decode(self, z):
        # 1. Proyeksikan vektor laten ke dimensi yang lebih besar
        x = self.fc_decoder(z)
        # 2. Reshape menjadi feature map 2D
        num_patches_side = self.image_size // self.patch_size
        x = x.view(-1, 256, num_patches_side, num_patches_side) # e.g., (B, 256, 16, 16)
        # 3. Rekonstruksi gambar menggunakan konvolusi terbalik
        return self.decoder_conv(x)

    def forward(self, x):
        z = self.encode(x)
        return self.decode(z)
    
class HybridLoss(nn.Module):
    """
    Fungsi loss gabungan yang mengkombinasikan MSE dan SSIM.
    SSIM sangat baik dalam menilai kemiripan struktural gambar.
    """
    def __init__(self, alpha=0.85, beta=0.15, data_range=1.0, win_size=7):
        super(HybridLoss, self).__init__()
        self.alpha = alpha # Bobot untuk SSIM
        self.beta = beta   # Bobot untuk MSE
        self.ssim_loss = SSIM(data_range=data_range, size_average=True, channel=1, win_size=win_size)
        self.mse_loss = nn.MSELoss()

    def forward(self, generated, target):
        # SSIM mengukur kemiripan (nilai tinggi lebih baik),
        # jadi kita hitung (1 - SSIM) untuk menjadikannya loss (nilai rendah lebih baik).
        loss_s = 1 - self.ssim_loss(generated, target)
        
        # MSE mengukur perbedaan kuadrat rata-rata.
        loss_m = self.mse_loss(generated, target)
        
        # Gabungkan keduanya dengan bobot masing-masing
        hybrid_loss = self.alpha * loss_s + self.beta * loss_m
        return hybrid_loss

class DBSCANClusterer:
    """
    Wrapper untuk scikit-learn DBSCAN agar memiliki interface yang mirip
    dengan PyTorchKMeans, termasuk 'centroids' buatan untuk kompatibilitas.
    """
    def __init__(self, eps=0.5, min_samples=5, device='cpu'):
        # eps: Jarak maksimum antara dua sampel untuk dianggap sebagai tetangga.
        #      Ini adalah hyperparameter terpenting di DBSCAN.
        self.eps = eps
        self.min_samples = min_samples
        self.device = device
        self.dbscan = None
        self.centroids = None # Akan kita buat secara manual
        self.labels_ = None

    def fit(self, X):
        """
        Melakukan clustering pada data X.
        X: Tensor PyTorch dengan shape [n_samples, n_features]
        """
        if isinstance(X, torch.Tensor):
            X_np = X.detach().cpu().numpy()
        else:
            X_np = X
            
        # 1. Lakukan clustering dengan DBSCAN
        self.dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples, n_jobs=-1).fit(X_np)
        self.labels_ = self.dbscan.labels_
        
        # 2. Buat 'centroids' buatan dengan menghitung rata-rata setiap cluster
        unique_labels = set(self.labels_)
        cluster_centers = {}
        
        for k in unique_labels:
            if k == -1: # Label -1 adalah untuk noise/outlier, kita abaikan
                continue
            
            class_member_mask = (self.labels_ == k)
            cluster_points = X_np[class_member_mask]
            center = cluster_points.mean(axis=0) # Hitung rata-rata
            cluster_centers[k] = center
            
        # Urutkan centroids berdasarkan labelnya untuk konsistensi
        sorted_centers = [cluster_centers[k] for k in sorted(cluster_centers.keys())]
        
        if sorted_centers:
            self.centroids = torch.from_numpy(np.array(sorted_centers)).float().to(self.device)
        else:
            # Kasus jika tidak ada cluster yang terbentuk
            self.centroids = torch.empty(0, X.shape[1]).to(self.device)

        return self

    def predict(self, X):
        """
        Memprediksi cluster untuk data baru dengan menemukan 'centroid' terdekat.
        DBSCAN secara native tidak punya metode predict.
        """
        if self.centroids is None or self.centroids.nelement() == 0:
             return torch.zeros(X.shape[0], dtype=torch.long) # Jika tidak ada cluster

        if isinstance(X, np.ndarray):
            X = torch.from_numpy(X).float()
        
        X = X.to(self.device)
        distances = torch.cdist(X, self.centroids)
        return torch.argmin(distances, dim=1).cpu()

    def save_model(self, path):
        """Menyimpan centroids buatan ke file."""
        if self.centroids is not None:
            torch.save(self.centroids, path)

    def load_model(self, path):
        """Memuat centroids buatan dari file."""
        self.centroids = torch.load(path, map_location=self.device)
        
def create_augmented_maps(original_maps, num_augmentations_per_map=None): # num_augmentations_per_map tidak lagi digunakan
    """
    Membuat berbagai versi augmentasi yang spesifik dan terkontrol untuk setiap peta bobot.
    
    Untuk setiap peta bobot asli, fungsi ini akan menghasilkan 11 versi:
    ...
    """
    
    all_generated_maps = []
    
    # 1. Definisikan pipeline augmentasi yang spesifik untuk setiap versi
    
    # --- Geometris ---
    get_elastic = lambda: A.Compose([A.ElasticTransform(p=1.0, alpha=10, sigma=120, alpha_affine=120)])
    get_occlusion = lambda: A.Compose([A.GridDropout(p=1.0, holes_number_x=5, holes_number_y=5, unit_size_min=10, unit_size_max=25, fill_value=0)])
    get_zoom_in = lambda: A.Compose([A.ShiftScaleRotate(p=1.0, shift_limit=0, scale_limit=(0.1, 0.3), rotate_limit=0, border_mode=cv2.BORDER_REPLICATE)])
    get_zoom_out = lambda: A.Compose([A.ShiftScaleRotate(p=1.0, shift_limit=0, scale_limit=(-0.3, -0.1), rotate_limit=0, border_mode=cv2.BORDER_REPLICATE)])
    get_rotation = lambda: A.Compose([A.ShiftScaleRotate(p=1.0, shift_limit=0, scale_limit=0, rotate_limit=(-15, 15), border_mode=cv2.BORDER_REPLICATE)])

    # --- Tiga jenis noise (tetap menggunakan Albumentations untuk kemudahan) ---
    get_gauss_noise = lambda: A.Compose([A.GaussNoise(p=1.0, var_limit=(0.005, 0.015))])
    get_gamma_noise = lambda: A.Compose([A.RandomGamma(p=1.0, gamma_limit=(80, 120))])
    get_multiplicative_noise = lambda: A.Compose([A.MultiplicativeNoise(p=1.0, multiplier=(0.9, 1.1))])

    def apply_bilateral_filter_cv(image):
        """
        Menerapkan Bilateral Filter menggunakan OpenCV, meniru parameter Albumentations.
        """
        image_uint8 = (image * 255).astype(np.uint8)
        
        d = 9
        sigma_color = random.uniform(20, 40)
        sigma_space = random.uniform(20, 40)
        
        # Terapkan filter OpenCV
        denoised_uint8 = cv2.bilateralFilter(
            src=image_uint8,
            d=d,
            sigmaColor=sigma_color,
            sigmaSpace=sigma_space,
            borderType=cv2.BORDER_REPLICATE
        )
        
        # Konversi kembali ke tipe data float asli (0-1)
        denoised_float = (denoised_uint8 / 255.0).astype(np.float32)
        
        return denoised_float

    # --- Manipulasi Nilai (tetap sama) ---
    def apply_contrast_change(image):
        new_image = image.copy()
        low_weight_threshold = 0.3
        low_mask = new_image < low_weight_threshold
        high_mid_mask = ~low_mask
        new_image[low_mask] *= 0.70
        new_image[high_mid_mask] *= 1.20
        np.clip(new_image, 0, 1, out=new_image)
        return new_image

    # Iterasi melalui setiap peta bobot asli
    for w_map in original_maps:
        w_map_float = w_map.astype(np.float32)
        
        # --- Tambahkan semua versi ke dalam daftar ---
        
        # 1. Versi Asli
        all_generated_maps.append(w_map_float)
        
        # 2. Renggang
        all_generated_maps.append(get_elastic()(image=w_map_float)['image'])
        
        # 3. Ter-oklusi
        all_generated_maps.append(get_occlusion()(image=w_map_float)['image'])
        
        # 4, 5, 6. Tiga Versi Noise
        all_generated_maps.append(get_gauss_noise()(image=w_map_float)['image'])
        all_generated_maps.append(get_gamma_noise()(image=w_map_float)['image']) 
        all_generated_maps.append(get_multiplicative_noise()(image=w_map_float)['image'])

        # --- PERUBAHAN 2: Panggil fungsi OpenCV kustom kita ---
        all_generated_maps.append(apply_bilateral_filter_cv(w_map_float))

        # 8. Zoom In
        all_generated_maps.append(get_zoom_in()(image=w_map_float)['image'])

        # 9. Zoom Out
        all_generated_maps.append(get_zoom_out()(image=w_map_float)['image'])

        # 10. Rotasi
        all_generated_maps.append(get_rotation()(image=w_map_float)['image'])
        
        # 11. Kontras yang Diubah
        all_generated_maps.append(apply_contrast_change(w_map_float))

    print(f"Augmentasi spesifik selesai. Menghasilkan {len(all_generated_maps)} total peta dari {len(original_maps)} peta asli.")
    return all_generated_maps

def target_distribution(q):
    weight = (q ** 2) / torch.sum(q, 0)
    return (weight.t() / torch.sum(weight, 1)).t()

def train_model(
    new_weight_maps,
    ground_truth_map=None,
    model_dir="database/Learning_Model_ViT/", 
    database_path="database/Learning_Model_ViT/training_database.h5",
    training_resolution=(256, 256),
    encoding_dim=64,
    epochs=50,
    batch_size=8,
    base_lr=1e-4,
    base_batch_size=16, 
    update_callback=None,
    guidance_weight=1.0,
    patience=5,             
    min_delta=0.000100,     
    lr_reduction_factor=0.2,
    max_lr_reductions=3,
    dbscan_eps=0.75,         
    dbscan_min_samples=5,
    loss_alpha=0.85,         
    loss_beta=0.15
):
    # === PERUBAHAN 1: Gunakan Arsitektur ViTAutoencoder ===
    Autoencoder = ViTAutoencoder
    best_model_path = os.path.join(model_dir, "vit_autoencoder_best.pth")
    os.makedirs(model_dir, exist_ok=True)
    
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("="*60)
        print("  MEMULAI SESI PELATIHAN MODEL CANGGIH (ViT + DBSCAN + Hybrid Loss)")
        print(f"  Menggunakan perangkat: {device}")
        print(f"  Parameter DBSCAN: eps={dbscan_eps}, min_samples={dbscan_min_samples}")
        print("="*60)

        # --- Tahap 1 & 2: Persiapan Data dan Augmentasi (Logika tetap sama) ---
        all_2d_maps_original = [cv2.resize(w, training_resolution, interpolation=cv2.INTER_AREA) for w in new_weight_maps]
        
        if os.path.exists(database_path):
            try:
                with h5py.File(database_path, 'r') as hf:
                    if 'weight_maps' in hf:
                        old_flat_maps = hf['weight_maps'][:]
                        side_len = int(np.sqrt(old_flat_maps.shape[1]))
                        if side_len == training_resolution[0]:
                            old_2d = old_flat_maps.reshape(-1, side_len, side_len)
                            all_2d_maps_original.extend(old_2d)
                print(f"Model Trainer: {len(all_2d_maps_original) - len(new_weight_maps)} sampel historis dimuat.")
            except Exception as e:
                print(f"Model Trainer: Gagal memuat basis data lama. Error: {e}")

        if not all_2d_maps_original: 
            print("Tidak ada data untuk dilatih. Proses dihentikan."); return
            
        print(f"Total peta bobot asli sebelum augmentasi: {len(all_2d_maps_original)}")
        final_training_maps_2d = create_augmented_maps(all_2d_maps_original)
        print(f"Ukuran dataset setelah augmentasi: {len(final_training_maps_2d)} sampel.")

        # --- Tahap 3: Persiapan Data Tensor ---
        if len(final_training_maps_2d) < 2: 
            print("Jumlah sampel tidak cukup untuk pelatihan. Proses dihentikan."); return

        all_maps_normalized = [(w / np.max(w) if np.max(w) > 0 else w) for w in final_training_maps_2d]
        training_data_tensor = torch.from_numpy(np.array(all_maps_normalized, dtype=np.float32)).unsqueeze(1)
        
        ground_truth_tensor = None
        if ground_truth_map is not None:
            try:
                ground_truth_resized = cv2.resize(ground_truth_map, training_resolution, interpolation=cv2.INTER_AREA)
                gt_max = np.max(ground_truth_resized)
                ground_truth_norm = ground_truth_resized / gt_max if gt_max > 0 else ground_truth_resized
                ground_truth_tensor = torch.from_numpy(ground_truth_norm.astype(np.float32)).unsqueeze(0).unsqueeze(0).to(device)
                print("  -> Pelatihan akan menggunakan 'Guided Training' dengan peta ground truth.")
            except Exception as e:
                print(f"  -> PERINGATAN: Gagal memproses ground truth: {e}")


        train_loader = DataLoader(TensorDataset(training_data_tensor), batch_size=batch_size, shuffle=True)

        # --- Tahap 4: Inisialisasi Model, Optimizer, dan Loss Baru ---
        autoencoder = Autoencoder(
            image_size=training_resolution[0], 
            encoding_dim=encoding_dim
        ).to(device)
        
        autoencoder_path = os.path.join(model_dir, "vit_autoencoder_pytorch.pth")
        if os.path.exists(autoencoder_path):
            try:
                autoencoder.load_state_dict(torch.load(autoencoder_path, map_location=device, weights_only=True))
                print("SUKSES: Melanjutkan pelatihan dari model ViTAutoencoder yang sudah ada.")
            except Exception as e:
                print(f"PERINGATAN: Gagal memuat model ViT. Memulai dari awal. Error: {e}")

        scale_factor = batch_size / base_batch_size
        adaptive_lr = base_lr * scale_factor
        
        # === PERUBAHAN 2: Gunakan HybridLoss ===
        criterion = HybridLoss(alpha=loss_alpha, beta=loss_beta).to(device)
        optimizer = optim.Adam(autoencoder.parameters(), lr=adaptive_lr, weight_decay=1e-5)
        
        epochs_without_improvement, best_loss, lr_reductions_count = 0, float('inf'), 0

        print(f"\nMemulai pelatihan ViTAutoencoder untuk maksimal {epochs} epoch...")
        for epoch in range(epochs):
            autoencoder.train()
            total_loss_epoch = 0
            for data_batch, in train_loader:
                inputs = data_batch.to(device)
                optimizer.zero_grad(set_to_none=True)
                
                outputs = autoencoder(inputs)
                loss_recon = criterion(outputs, inputs)
                loss = loss_recon
                if ground_truth_tensor is not None:
                    loss_guidance = criterion(outputs, ground_truth_tensor.expand_as(outputs))
                    loss += (guidance_weight * loss_guidance)
                
                loss.backward()
                optimizer.step()
                total_loss_epoch += loss.item()
                
            avg_loss = total_loss_epoch / len(train_loader)
            current_lr = optimizer.param_groups[0]['lr']
            print(f"CAE Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}, LR: {current_lr:.1e}")
            if update_callback: update_callback(int((epoch+1)/epochs * 100), f"Melatih CAE Epoch {epoch+1}")

            if avg_loss < best_loss - min_delta:
                best_loss = avg_loss
                epochs_without_improvement = 0
                torch.save(autoencoder.state_dict(), best_model_path)
            else:
                epochs_without_improvement += 1

            if epochs_without_improvement >= patience:
                if lr_reductions_count < max_lr_reductions:
                    lr_reductions_count += 1
                    print("-" * 25)
                    print(f"PERINGATAN: Performa stagnan. Mencoba penghalusan LR ke-{lr_reductions_count}/{max_lr_reductions}...")
                    
                    new_lr = current_lr * lr_reduction_factor
                    for param_group in optimizer.param_groups:
                        param_group['lr'] = new_lr
                    
                    print(f"Learning rate dikurangi menjadi: {new_lr:.1e}")
                    print("-" * 25)
                    
                    epochs_without_improvement = 0
                else:
                    print(f"\nEARLY STOPPING: Performa tetap stagnan setelah {max_lr_reductions} kali pengurangan LR.")
                    print(f"Pelatihan berhenti di epoch {epoch+1}.")
                    break 
                
        if os.path.exists(best_model_path):
            autoencoder.load_state_dict(torch.load(best_model_path, map_location=device, weights_only=True))
            print("Model ViTAutoencoder dengan performa terbaik telah dimuat.")

        # --- Tahap Clustering dengan DBSCAN ---
        print("\nMemulai pengelompokan (clustering) ruang laten dengan DBSCAN...")
        autoencoder.eval()
        with torch.no_grad():
            original_maps_norm = [(w / np.max(w) if np.max(w) > 0 else w) for w in all_2d_maps_original]
            original_data_tensor = torch.from_numpy(np.array(original_maps_norm, dtype=np.float32)).unsqueeze(1).to(device)
            # Encode dengan input 3 channel
            reduced_data_tensor = autoencoder.encode(original_data_tensor.repeat(1, 3, 1, 1))
        
        # === PERUBAHAN 3: Gunakan DBSCANClusterer ===
        clusterer = DBSCANClusterer(eps=dbscan_eps, min_samples=dbscan_min_samples, device=device)
        clusterer.fit(reduced_data_tensor)
        
        cluster_model_path = os.path.join(model_dir, "dbscan_clusters.pth")
        if clusterer.centroids is not None and clusterer.centroids.nelement() > 0:
            num_clusters = len(clusterer.centroids)
            print(f"Pelatihan DBSCAN Selesai. Ditemukan {num_clusters} cluster (tidak termasuk noise).")
            clusterer.save_model(cluster_model_path)
            print(f"SUKSES! Cluster DBSCAN disimpan ke {cluster_model_path}")
        else:
            print("PERINGATAN: DBSCAN tidak menemukan cluster yang valid. Coba sesuaikan parameter 'eps'.")
           
        # --- Tahap Penyimpanan Akhir ---
        torch.save(autoencoder.state_dict(), autoencoder_path)
        print(f"SUKSES! Model ViTAutoencoder disimpan ke {autoencoder_path}")
            
        with h5py.File(database_path, 'w') as hf:
            original_flat_maps = np.array([w.flatten() for w in all_2d_maps_original], dtype=np.float32)
            hf.create_dataset('weight_maps', data=original_flat_maps, compression="gzip")
        print(f"SUKSES! Database pelatihan diperbarui di {database_path}")

    except Exception as e:
        print("!!! TERJADI ERROR KRITIS DI DALAM train_model !!!")
        traceback.print_exc()
    finally:
        if os.path.exists(best_model_path):
            try:
                os.remove(best_model_path)
                print(f"Pembersihan: File sementara '{os.path.basename(best_model_path)}' telah dihapus.")
            except OSError as e:
                print(f"Peringatan: Gagal menghapus file sementara. Error: {e}")

def create_prototypes_dashboard(prototypes_2d, n_patterns, training_resolution):
    if not prototypes_2d: return np.zeros((training_resolution[1], training_resolution[0]), dtype=np.uint8)
    cols = int(np.ceil(np.sqrt(n_patterns)))
    rows = int(np.ceil(n_patterns / cols))
    dashboard_h, dashboard_w = rows * training_resolution[1], cols * training_resolution[0]
    dashboard = np.zeros((dashboard_h, dashboard_w), dtype=np.uint8)
    for i, proto_img in enumerate(prototypes_2d):
        if i >= rows * cols: break
        row_idx, col_idx = i // cols, i % cols
        y_start, x_start = row_idx * training_resolution[1], col_idx * training_resolution[0]
        vis_img = cv2.normalize(proto_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        dashboard[y_start : y_start+training_resolution[1], x_start : x_start+training_resolution[0]] = vis_img
    return dashboard
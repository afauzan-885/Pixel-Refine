# Belum jadi, baru sekedar kerangka saja

import os
import h5py
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import temporal_consistency_refinement

# --- Konfigurasi Training ---
CONFIG = {
    "database_path": "database/Learning_Model/raw_weight_map_database.h5",
    "backbone_weights": "database/Learning_Model/mobilenet_v2_weights.pth",
    "output_model_path": "database/Learning_Model/mobilenet_refiner.pth",
    "epochs": 50,
    "batch_size": 32,
    "learning_rate": 1e-4,
    "device": "cuda" if torch.cuda.is_available() else "cpu"
}

class PreprocessedWeightMapDataset(Dataset):
    def __init__(self, all_input_tensors, all_target_tensors):
        # Dataset ini sekarang hanya menyimpan tensor yang sudah jadi
        self.all_input_tensors = all_input_tensors
        self.all_target_tensors = all_target_tensors

    def __len__(self):
        return self.all_input_tensors.size(0)

    def __getitem__(self, idx):
        # __getitem__ sekarang menjadi sangat cepat!
        # Hanya mengambil slice dari tensor yang sudah ada di memori.
        return self.all_input_tensors[idx], self.all_target_tensors[idx]

def create_ground_truth(raw_maps):
    """
    Menggunakan logika lama untuk membuat target (ground truth) yang lebih baik
    dari kumpulan peta bobot mentah.
    """
    print("Membuat ground truth dari data mentah...")
    # Tumpuk semua peta menjadi satu array besar (N, H, W)
    weight_stack = np.stack(raw_maps, axis=0)
    
    # Buat peta bobot gabungan (sum)
    weight_map_sum = np.sum(weight_stack, axis=0)
    
    # Gunakan fungsi refinement temporal lama Anda untuk menyempurnakan peta gabungan
    # Fungsi ini akan menyesuaikan nilai-nilai di weight_map_sum berdasarkan stabilitas temporal
    # Ini adalah "cheat" cerdas kita untuk membuat GT
    temporal_consistency_refinement(raw_maps, weight_map_sum)
    
    # Normalisasi peta gabungan yang sudah disempurnakan sebagai target global
    max_val = np.max(weight_map_sum)
    ground_truth_map = weight_map_sum / max_val if max_val > 0 else weight_map_sum
    
    print("Ground truth berhasil dibuat.")
    return ground_truth_map

def load_data(db_path):
    """Memuat semua peta bobot dari file HDF5."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database tidak ditemukan di: {db_path}")
    
    with h5py.File(db_path, 'r') as hf:
        # List comprehension ini sudah benar
        raw_maps = [np.array(hf[key]) for key in hf.keys()]
    
    print(f"Berhasil memuat {len(raw_maps)} peta bobot mentah.")
    
    # --- TAMBAHKAN BARIS INI ---
    return raw_maps
    
class WeightMapRefinementDataset(Dataset):
    def __init__(self, raw_maps, ground_truth_map):
        self.raw_maps = raw_maps
        self.ground_truth_map = ground_truth_map
        # Kita tidak bisa menggunakan frame pertama dan terakhir karena butuh konteks
        self.valid_indices = range(1, len(raw_maps) - 1)

    def __len__(self):
        return len(self.valid_indices)

    def __getitem__(self, idx):
        # Dapatkan indeks sebenarnya dari frame yang akan kita proses
        center_frame_idx = self.valid_indices[idx]
        
        # Ambil 3 frame berurutan: sebelumnya, saat ini, dan berikutnya
        prev_map = self.raw_maps[center_frame_idx - 1]
        current_map = self.raw_maps[center_frame_idx]
        next_map = self.raw_maps[center_frame_idx + 1] # Ini bisa jadi pengganti optical flow
        
        # Ambil bagian dari ground truth yang sesuai dengan frame saat ini
        # Dalam pendekatan sederhana ini, kita bisa gunakan GT global
        # Atau, bisa juga dihitung per-frame, tapi ini lebih mudah
        target_map = self.ground_truth_map 

        # Gabungkan input menjadi 3 channel: (prev, current, next)
        # Ini adalah input "temporal" yang kaya informasi
        # Kita akan "menipu" input channel model sedikit
        input_stack = np.stack([prev_map, current_map, next_map], axis=0) # Shape: (3, H, W)
        
        # Konversi ke tensor
        input_tensor = torch.from_numpy(input_stack).float()
        target_tensor = torch.from_numpy(target_map[np.newaxis, :, :]).float() # Shape: (1, H, W)
        
        return input_tensor, target_tensor
    
def train_model():
    """
    Fungsi utama untuk menjalankan seluruh proses training dengan optimisasi
    Automatic Mixed Precision (AMP) untuk mengurangi penggunaan VRAM.
    """
    # 1. Muat Data (Tidak ada perubahan)
    raw_maps = load_data(CONFIG["database_path"])
    
    # 2. Buat Ground Truth (Tidak ada perubahan)
    stacked_maps = np.stack(raw_maps, axis=0)
    ground_truth_map = np.mean(stacked_maps, axis=0)
    
    # --- Langkah Pra-Pemrosesan (Tidak ada perubahan, ini sudah optimal) ---
    print("Memulai pra-pemrosesan seluruh dataset...")
    num_samples = len(raw_maps) - 2
    h, w = raw_maps[0].shape
    all_inputs = torch.empty((num_samples, 3, h, w), dtype=torch.float32)
    all_targets = torch.empty((num_samples, 1, h, w), dtype=torch.float32)
    target_tensor_template = torch.from_numpy(ground_truth_map[np.newaxis, :, :]).float()
    all_targets.copy_(target_tensor_template.expand_as(all_targets))
    
    for i in tqdm(range(num_samples), desc="Pra-pemrosesan Input"):
        center_idx = i + 1
        prev_map = raw_maps[center_idx - 1]
        current_map = raw_maps[center_idx]
        next_map = raw_maps[center_idx + 1]
        input_stack_np = np.stack([prev_map, current_map, next_map], axis=0)
        all_inputs[i] = torch.from_numpy(input_stack_np)
        
    print("Pra-pemrosesan selesai.")
    
    # 3. Buat Dataset & DataLoader (Tidak ada perubahan)
    dataset = PreprocessedWeightMapDataset(all_inputs, all_targets)
    dataloader = DataLoader(
        dataset, 
        batch_size=CONFIG["batch_size"], 
        shuffle=True, 
        num_workers=2,
        pin_memory=True
    )
    
    model = MobileNetV2_Unet(
        backbone_weights_path=CONFIG["backbone_weights"],
        in_channels=3, 
        out_channels=1
    ).to(CONFIG["device"])
    
    criterion = nn.L1Loss()
    optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG["learning_rate"])

    # --- PERUBAHAN UNTUK AMP (Mulai) ---
    # 1. Inisialisasi GradScaler. Ini membantu mencegah gradien menjadi nol (underflow)
    #    saat menggunakan presisi float16 yang lebih rendah.
    #    Kita hanya membuatnya jika menggunakan CUDA.
    scaler = None
    if CONFIG["device"] == "cuda":
        scaler = torch.cuda.amp.GradScaler()
    # --- PERUBAHAN UNTUK AMP (Selesai) ---
    
    # 5. Loop Training
    print("\n--- Memulai Training ---")
    for epoch in range(CONFIG["epochs"]):
        model.train()
        epoch_loss = 0.0
        
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{CONFIG['epochs']}")
        
        for inputs, targets in progress_bar:
            inputs = inputs.to(CONFIG["device"])
            targets = targets.to(CONFIG["device"])
            
            # Reset gradien optimizer
            optimizer.zero_grad()
            
            # --- PERUBAHAN UNTUK AMP (Mulai) ---
            # 2. Gunakan autocast context manager.
            #    Ini akan secara otomatis menjalankan operasi yang kompatibel (seperti konvolusi)
            #    dalam format float16 untuk menghemat memori dan bandwidth.
            #    `enabled` memastikan ini hanya aktif saat di CUDA.
            with torch.cuda.amp.autocast(enabled=(scaler is not None)):
                outputs = model(inputs)
                loss = criterion(outputs, targets)
            
            # 3. Lakukan scaling pada loss sebelum backward pass.
            #    Kemudian, jalankan langkah optimizer dan perbarui scaler.
            #    Ini adalah pengganti dari loss.backward() dan optimizer.step() standar.
            if scaler:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else: # Fallback untuk CPU (tidak menggunakan AMP)
                loss.backward()
                optimizer.step()
            # --- PERUBAHAN UNTUK AMP (Selesai) ---

            epoch_loss += loss.item()
            progress_bar.set_postfix(loss=loss.item())
            
        avg_epoch_loss = epoch_loss / len(dataloader)
        print(f"Epoch {epoch+1} Selesai. Rata-rata Loss: {avg_epoch_loss:.6f}")

    # 6. Simpan Model yang Sudah Dilatih (Tidak ada perubahan)
    print(f"\nTraining selesai. Menyimpan model ke: {CONFIG['output_model_path']}")
    torch.save(model.state_dict(), CONFIG["output_model_path"])
    print("Model berhasil disimpan.")

if __name__ == "__main__":
    train_model()
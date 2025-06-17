import torch

# Ganti dengan path yang benar jika perlu
ENCODER_PATH = "database/Learning_Model/encoder_pytorch.pth"

print(f"--- Menganalisis isi dari: {ENCODER_PATH} ---")

try:
    # Muat state_dict dari file
    state_dict = torch.load(ENCODER_PATH)

    print("\nKunci (nama lapisan dan parameter) yang ditemukan di dalam file:")
    # Cetak semua kunci yang ada
    for key in state_dict.keys():
        print(key)

    print("\n--- Analisis Arsitektur Berdasarkan Kunci ---")
    if "2.weight" in state_dict:
        print("Model ini KEMUNGKINAN BESAR TIDAK memiliki lapisan Dropout di posisi ke-2.")
        print("Lapisan ke-2 adalah nn.Linear.")
    elif "3.weight" in state_dict:
        print("Model ini KEMUNGKINAN BESAR MEMILIKI lapisan Dropout di posisi ke-2.")
        print("Lapisan ke-3 adalah nn.Linear.")

except FileNotFoundError:
    print(f"ERROR: File tidak ditemukan di '{ENCODER_PATH}'. Pastikan path sudah benar.")
except Exception as e:
    print(f"Terjadi error saat membaca file: {e}")
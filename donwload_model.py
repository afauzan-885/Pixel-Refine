import torch
from torchvision.models import mobilenet_v2
import os

SAVE_DIR = "database/Learning_Model" 
os.makedirs(SAVE_DIR, exist_ok=True)

# Path lengkap untuk file bobot backbone
BACKBONE_SAVE_PATH = os.path.join(SAVE_DIR, "mobilenet_v2_weights.pth")

if not os.path.exists(BACKBONE_SAVE_PATH):
    print("Mendownload bobot pretrained MobileNetV2...")
    # Dapatkan model dengan bobot default
    model = mobilenet_v2(weights='MobileNet_V2_Weights.DEFAULT')
    
    # Simpan hanya state_dict (bobotnya saja)
    torch.save(model.state_dict(), BACKBONE_SAVE_PATH)
    print(f"Bobot MobileNetV2 berhasil disimpan di: {BACKBONE_SAVE_PATH}")
else:
    print(f"Bobot MobileNetV2 sudah ada di: {BACKBONE_SAVE_PATH}")
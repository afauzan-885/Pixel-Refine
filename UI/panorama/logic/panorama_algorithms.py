import time

import cv2
import numpy as np

# --- Bagian Projection & Blending (Contoh) ---
def run_projection(aligned_data, settings, progress_callback):
    print(f"ALGORITHM: Applying {settings.get('projection_type')} projection...")
    time.sleep(0.5)
    progress_callback(1.0, "Projection applied.")
    return "projection_result"

def run_blending(projected_data, settings, progress_callback):
    print(f"ALGORITHM: Applying {settings.get('blending_method')} blending...")
    time.sleep(1.0)
    progress_callback(1.0, "Blending complete.")
    return "final_panorama_image"
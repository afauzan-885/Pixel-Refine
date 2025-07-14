# Di dalam panorama_algorithms.py (setelah fungsi-fungsi di atas)

# Definisikan pemetaan dari nama di dropdown ke fungsi yang sebenarnya
from UI.panorama.logic.panorama_algorithms import run_akaze_alignment, run_blending, run_orb_alignment, run_projection


ALIGNMENT_DISPATCHER = {
    "AKAZE": run_akaze_alignment,
    "ORB": run_orb_alignment,
    # "SIFT": run_sift_alignment, # Tambahkan yang lain di sini
    # "BRISK": run_brisk_alignment,
}

# Fungsi dispatcher utama
def run_panorama_stitching_process(images, settings, progress_callback, target_stage="blending"):
    """
    Satu fungsi untuk menjalankan seluruh alur kerja panorama, bisa berhenti di tahap tertentu.
    """
    if len(images) < 2:
        raise ValueError("Not enough images to create a panorama.")
        
    # --- TAHAP 1: ALIGNMENT ---
    align_choice = settings.get('align_algorithm', 'AKAZE')
    align_function = ALIGNMENT_DISPATCHER.get(align_choice)
    
    if not align_function:
        raise NotImplementedError(f"Alignment algorithm '{align_choice}' is not implemented.")
    
    def align_progress_reporter(p, msg):
        progress_callback(p * 0.4, f"Aligning: {msg}")

    aligned_data = align_function(images, settings, align_progress_reporter)
    
    # Periksa apakah kita harus berhenti setelah alignment
    if target_stage == "alignment":
        return aligned_data 
    
    # --- TAHAP 2: PROJECTION ---
    def projection_progress_reporter(p, msg):
        progress_callback(0.4 + (p * 0.2), f"Projecting: {msg}")
        
    projected_data = run_projection(aligned_data, settings, projection_progress_reporter)

    # Periksa apakah kita harus berhenti setelah projection
    if target_stage == "projection":
        return projected_data
        
    # --- TAHAP 3: BLENDING ---
    def blending_progress_reporter(p, msg):
        progress_callback(0.6 + (p * 0.4), f"Blending: {msg}")
    
    final_image = run_blending(projected_data, settings, blending_progress_reporter)
    
    return final_image
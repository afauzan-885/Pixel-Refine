from UI.panorama.Algorithm.stitching.Standart_Homography import run_standart_homography
from UI.panorama.logic.panorama_algorithms import run_blending, run_orb_alignment, run_projection


ALIGNMENT_DISPATCHER = {
    "Standard_Homography": run_standart_homography,
    "ORB": run_orb_alignment,
    # "SIFT": run_sift_alignment, # Tambahkan yang lain di sini
    # "BRISK": run_brisk_alignment,
}

# Fungsi dispatcher utama
def run_panorama_stitching_process(
    images, 
    settings, 
    progress_callback, 
    target_stage="blending",
    # BARU: Argumen opsional untuk menerima data yang sudah diproses
    cached_alignment_data=None,
    cached_projection_data=None
):
    """
    Satu fungsi untuk menjalankan seluruh alur kerja panorama, 
    bisa memulai dari tahap tengah jika data cache disediakan.
    """
    
    # --- TAHAP 3: BLENDING ---
    # Cek tahap terakhir dulu, jika data proyeksi ada, langsung blending
    if cached_projection_data is not None and target_stage == "blending":
        progress_callback(0.0, "Using cached projection. Starting Blending...")
        def blending_progress_reporter(p, msg):
            progress_callback(p, f"Blending: {msg}") # Progress dari 0 ke 1
        
        final_image = run_blending(cached_projection_data, settings, blending_progress_reporter)
        progress_callback(1.0, "Blending finished.")
        return final_image

    # --- TAHAP 2: PROJECTION ---
    if cached_alignment_data is not None:
        aligned_data = cached_alignment_data
        progress_callback(0.0, "Using cached alignment. Starting Projection...")
    else:
        if len(images) < 2:
            raise ValueError("Not enough images to create a panorama.")
            
        align_choice = settings.get('align_algorithm', 'Standard_Homography')
        align_function = ALIGNMENT_DISPATCHER.get(align_choice)
        
        if not align_function:
            raise NotImplementedError(f"Alignment algorithm '{align_choice}' is not implemented.")
        
        def align_progress_reporter(p, msg):
            # Alokasikan 40% dari total progress bar untuk alignment
            progress_callback(p * 0.4, f"Aligning: {msg}")

        aligned_data = align_function(images, settings, align_progress_reporter)
        
        if target_stage == "alignment":
            progress_callback(1.0, "Alignment finished.")
            return aligned_data
    
    # Sekarang, lanjutkan ke proyeksi
    def projection_progress_reporter(p, msg):
        # Alokasikan 20% berikutnya (dari 40% ke 60%)
        progress_callback(0.4 + (p * 0.2), f"Projecting: {msg}")
        
    projected_data = run_projection(aligned_data, settings, projection_progress_reporter)

    if target_stage == "projection":
        progress_callback(1.0, "Projection finished.")
        return projected_data
        
    # --- Lanjutkan ke TAHAP 3: BLENDING (jika belum dijalankan di atas) ---
    def blending_progress_reporter(p, msg):
        # Alokasikan 40% terakhir (dari 60% ke 100%)
        progress_callback(0.6 + (p * 0.4), f"Blending: {msg}")
    
    final_image = run_blending(projected_data, settings, blending_progress_reporter)
    progress_callback(1.0, "Blending finished.")
    
    return final_image
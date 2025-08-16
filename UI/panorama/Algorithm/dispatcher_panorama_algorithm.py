from UI.panorama.Algorithm.Projection_and_Crop.projection import run_projection_and_crop
from UI.panorama.Algorithm.stitching.Local_Homography import run_local_homography
from UI.panorama.Algorithm.stitching.Standart_Homography import run_standart_homography
from UI.panorama.logic.panorama_algorithms import run_blending


ALIGNMENT_DISPATCHER = {
    "Standard_Homography": run_standart_homography,
    "Local_Homography": run_local_homography, # <<< BARU
}
# Fungsi dispatcher utama
def run_panorama_stitching_process(
    images, 
    settings, 
    progress_callback, 
    target_stage="blending",
    cached_alignment_data=None,
    cached_projection_data=None
):
    """
    Fungsi pabrik utama yang menjalankan seluruh alur kerja panorama.
    """
    try:
        # --- PERSIAPAN AWAL ---
        # Tentukan image_paths di awal agar selalu tersedia.
        if isinstance(images[0], str):
            image_paths = images
        else:
            # Jika input bukan path, kita tidak bisa melanjutkan dengan alur kerja baru.
            # Ini adalah batasan desain yang harus kita terima untuk efisiensi.
            return {"error": "Alur kerja membutuhkan daftar path gambar, bukan gambar yang sudah dimuat."}

        # --- TAHAP 1: RESOLUSI DATA ALIGNMENT ---
        alignment_package = None

        if cached_alignment_data and "homographies" in cached_alignment_data:
            # Jika ada cache (minimal atau penuh), kita akan menggunakannya.
            # Kita akan melengkapinya nanti di tahap proyeksi.
            progress_callback(0.0, "Menggunakan data alignment dari cache...")
            alignment_package = cached_alignment_data
        
        else: # Tidak ada cache yang valid, proses dari awal.
            if len(image_paths) < 2:
                return {"error": "Butuh setidaknya 2 gambar untuk membuat panorama."}
            
            align_choice = settings.get('align_algorithm', 'Standard_Homography')
            align_function = ALIGNMENT_DISPATCHER.get(align_choice)
            
            if not align_function:
                return {"error": f"Algoritma alignment '{align_choice}' tidak terimplementasi."}
            
            def align_progress_reporter(p, msg):
                progress_callback(p * 0.4, msg) # 0% -> 40%

            # Panggil fungsi alignment. images di sini adalah image_paths.
            alignment_package = align_function(image_paths, settings, align_progress_reporter)

        if alignment_package.get("error"):
            return alignment_package

        # --- Titik Keluar 1: Jika targetnya hanya alignment ---
        if target_stage == "alignment":
            progress_callback(1.0, "Tahap Alignment selesai.")
            return alignment_package

        # --- TAHAP 2: PROYEKSI DAN CROPPING ---
        projection_package = None
        
        if target_stage == "blending" and cached_projection_data:
             progress_callback(0.4, "Menggunakan data proyeksi dari cache...")
             projection_package = cached_projection_data
        else:
            # --- BLOK LOGIKA TERPUSAT DAN DIPERBAIKI ---
            
            # Siapkan reporter progres yang sudah di-skalakan
            def projection_progress_reporter(p, msg):
                 # p dari 0-100, diubah ke rentang 0.4 -> 0.95 (55% dari total)
                 progress_callback(0.4 + (p / 100.0 * 0.55), msg)

            # Panggil kontroler proyeksi dengan argumen yang KONSISTEN
            projection_package = run_projection_and_crop(
                alignment_data=alignment_package,
                image_paths=image_paths, # <-- SELALU gunakan image_paths
                settings=settings,
                progress_callback=projection_progress_reporter # <-- SELALU gunakan reporter
            )

        if projection_package.get("error"):
            return projection_package
            
        # --- Titik Keluar 2: Jika targetnya adalah proyeksi ---
        if target_stage == "projection":
            progress_callback(1.0, "Tahap Proyeksi selesai.")
            return projection_package

        # --- TAHAP 3: BLENDING ---
        def blending_progress_reporter(p, msg):
            progress_callback(0.95 + (p * 0.05), msg) # 95% -> 100%
            
        final_image = run_blending(
            projection_package=projection_package,
            settings=settings,
            progress_callback=blending_progress_reporter
        )
        
        progress_callback(1.0, "Panorama selesai dibuat.")
        
        return {"stitched_image": final_image, "error": None}

    except Exception as e:
        import traceback
        error_message = f"Terjadi error fatal di dalam proses stitching: {e}\n{traceback.format_exc()}"
        print(error_message)
        return {"error": error_message}
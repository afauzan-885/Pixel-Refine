from UI.panorama.Algorithm.Projection_and_Crop.projection import run_projection_and_crop
from UI.panorama.Algorithm.stitching.Local_Homography import run_local_homography
from UI.panorama.Algorithm.stitching.Standart_Homography import run_standart_homography
from UI.panorama.logic.panorama_algorithms import run_blending


ALIGNMENT_DISPATCHER = {
    "Standard_Homography": run_standart_homography,
    "Local_Homography": run_local_homography,
}
# Fungsi dispatcher utama
def run_panorama_stitching_process(
    images, 
    settings, 
    progress_callback, 
    target_stage="blending",
    cached_alignment_data=None,
    cached_projection_data=None,
    stop_flag=lambda: False
):
    """
    Fungsi pabrik utama yang menjalankan seluruh alur kerja panorama dengan dukungan stop_flag.
    """
    try:
        # --- PERSIAPAN AWAL ---
        if isinstance(images[0], str):
            image_paths = images
        else:
            return {"error": "Alur kerja membutuhkan daftar path gambar, bukan gambar yang sudah dimuat."}

        # --- TAHAP 1: RESOLUSI DATA ALIGNMENT ---
        if stop_flag():
            return {"error": "Proses dihentikan sebelum alignment."}

        alignment_package = None
        if cached_alignment_data and "homographies" in cached_alignment_data:
            progress_callback(0.0, "Menggunakan data alignment dari cache...")
            alignment_package = cached_alignment_data
        else:
            if len(image_paths) < 2:
                return {"error": "Butuh setidaknya 2 gambar untuk membuat panorama."}
            
            align_choice = settings.get('align_algorithm', 'Standard_Homography')
            align_function = ALIGNMENT_DISPATCHER.get(align_choice)
            if not align_function:
                return {"error": f"Algoritma alignment '{align_choice}' tidak terimplementasi."}
            
            def align_progress_reporter(p, msg):
                if stop_flag():
                    raise RuntimeError("Proses alignment dihentikan oleh stop_flag.")
                progress_callback(p * 0.4, msg)  # 0% -> 40%

            alignment_package = align_function(image_paths, settings, align_progress_reporter)

        if alignment_package.get("error"):
            return alignment_package

        if target_stage == "alignment":
            progress_callback(1.0, "Tahap Alignment selesai.")
            return alignment_package

        # --- TAHAP 2: PROYEKSI DAN CROPPING ---
        if stop_flag():
            return {"error": "Proses dihentikan sebelum proyeksi."}

        projection_package = None
        if target_stage == "blending" and cached_projection_data:
             progress_callback(0.4, "Menggunakan data proyeksi dari cache...")
             projection_package = cached_projection_data
        else:
            def projection_progress_reporter(p, msg):
                 if stop_flag():
                     raise RuntimeError("Proses proyeksi dihentikan oleh stop_flag.")
                 progress_callback(0.4 + (p / 100.0 * 0.55), msg)

            projection_package = run_projection_and_crop(
                alignment_data=alignment_package,
                image_paths=image_paths,
                settings=settings,
                progress_callback=projection_progress_reporter
            )

        if projection_package.get("error"):
            return projection_package
            
        if target_stage == "projection":
            progress_callback(1.0, "Tahap Proyeksi selesai.")
            return projection_package

        # --- TAHAP 3: BLENDING ---
        if stop_flag():
            return {"error": "Proses dihentikan sebelum blending."}

        def blending_progress_reporter(p, msg):
            if stop_flag():
                raise RuntimeError("Proses blending dihentikan oleh stop_flag.")
            progress_callback(0.95 + (p * 0.05), msg)  # 95% -> 100%
            
        final_image = run_blending(
            projection_package=projection_package,
            settings=settings,
            progress_callback=blending_progress_reporter
        )
        
        progress_callback(1.0, "Panorama selesai dibuat.")
        
        return {"stitched_image": final_image, "error": None}

    except Exception as e:
        import traceback
        error_message = f"Terjadi error/fatal di stitching: {e}\n{traceback.format_exc()}"
        print(error_message)
        return {"error": error_message}

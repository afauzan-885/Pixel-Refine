from PySide6.QtCore import QObject, Signal
from UI.panorama.Algorithm.dispatcher_panorama_algorithm import run_panorama_stitching_process

class PanoramaWorker(QObject):
    """
    Worker yang berjalan di thread terpisah untuk menjalankan
    proses stitching panorama tanpa membekukan UI.
    """
    progress_updated = Signal(int, str)
    finished = Signal(str, object)
    error = Signal(str)

    def __init__(self, image_paths, settings, target_stage, 
                 cached_alignment=None, cached_projection=None):
        super().__init__()
        self.image_paths = image_paths
        self.settings = settings
        self.target_stage = target_stage
        self.cached_alignment = cached_alignment
        self.cached_projection = cached_projection
        self.is_running = True

    def run(self):
        try:
            def progress_callback(percentage, message):
                self.progress_updated.emit(int(percentage * 100), message)

            # MODIFIKASI: Teruskan data cache ke fungsi proses
            result = run_panorama_stitching_process(
                images=self.image_paths, 
                settings=self.settings,
                progress_callback=progress_callback,
                target_stage=self.target_stage,
                cached_alignment_data=self.cached_alignment,
                cached_projection_data=self.cached_projection
            )
            
            self.finished.emit(self.target_stage, result)

        except Exception as e:
            # Jika terjadi error, pancarkan sinyal 'error'
            import traceback
            error_message = f"Error in {self.target_stage}: {e}\n{traceback.format_exc()}"
            self.error.emit(error_message)

    def stop(self):
        self.is_running = False
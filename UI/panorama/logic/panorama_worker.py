import traceback
from PySide6.QtCore import QObject, Signal
from UI.panorama.Algorithm.dispatcher_panorama_algorithm import run_panorama_stitching_process

class PanoramaWorker(QObject):
    """
    Worker untuk stitching panorama di thread terpisah.
    Mendukung progress, cancel, dan penggunaan memmap.
    """
    progress_updated = Signal(int, str)  # percentage, message
    finished = Signal(str, object)       # stage, result
    error = Signal(str)                  # error message

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
                # pastikan signal-safe
                self.progress_updated.emit(int(percentage), message)

            # jalankan proses stitching menggunakan pipeline yang sudah dioptimasi
            result = run_panorama_stitching_process(
                images=self.image_paths, 
                settings=self.settings,
                progress_callback=progress_callback,
                target_stage=self.target_stage,
                cached_alignment_data=self.cached_alignment,
                cached_projection_data=self.cached_projection,
                stop_flag=lambda: not self.is_running  # worker tiles bisa cek stop_flag
            )

            if self.is_running:
                self.finished.emit(self.target_stage, result)
            else:
                # worker dihentikan oleh user
                self.finished.emit(self.target_stage, {"stopped": True})

        except Exception as e:
            tb_str = traceback.format_exc()
            self.error.emit(f"Error in {self.target_stage}: {e}\n{tb_str}")

    def stop(self):
        """
        Hentikan proses stitching dengan aman.
        Worker tiles akan berhenti pada tile berikutnya karena stop_flag.
        """
        self.is_running = False
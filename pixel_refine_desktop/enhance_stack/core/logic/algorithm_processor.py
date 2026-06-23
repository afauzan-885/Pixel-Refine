"""
Algorithm Processor Thread
Handles background execution of image processing algorithms with progress tracking.
"""

from PySide6.QtCore import QThread, Signal

# Import algorithm functions
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.Farneback_optical_flow import (
    running_farneback_optical_flow,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.AKAZE import (
    running_akaze,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.ORB import running_orb
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.Light_Glue import (
    running_light_glue,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
    running_median,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    running_similarity,
    running_mf_denoiser,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.WeightedSR import (
    running_weighted_sr,
)



class AlgorithmProcessorThread(QThread):

    """
    Background thread to execute selected algorithms for a batch.

    This thread handles the execution of image processing algorithms
    (alignment, super resolution, denoising) with progress tracking.
    Supports both single process mode and batch processing mode.
    """

    progress_update = Signal(int, str)  # percent, message
    finished_processing = Signal()
    error_occurred = Signal(str)  # error message
    cancel_requested = Signal()  # Signal emitted when cancellation is requested

    def __init__(self, batch_id, settings, parent=None, single_process=True):
        """
        Initialize the algorithm processor thread.

        Args:
            batch_id: ID of the batch to process
            settings: Dict with algorithm selections (alignment, super_resolution, denoising)
            parent: Parent QObject (usually the layout or panel)
            single_process: If True, run in single process mode (default).
                           Set to False for batch processing with batch_id.
        """
        super().__init__(parent)
        self.batch_id = batch_id
        self.settings = settings
        self.parent_panel = parent
        self.single_process = single_process
        self._is_running = True
        self._is_cancelled = False

    def stop(self):
        """Request the thread to stop gracefully."""
        self._is_running = False
        self._is_cancelled = True
        self.cancel_requested.emit()

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        return self._is_cancelled

    def run(self):
        """Execute the selected algorithms."""
        try:
            # Progress callback to emit signal
            def progress_callback(percent, message="", *args, **kwargs):
                if self._is_running:
                    if args:
                        # Forward 3rd argument (like description text) formatted as message||description
                        self.progress_update.emit(percent, f"{message}||{args[0]}")
                    else:
                        self.progress_update.emit(percent, str(message))

            # Define actions mapping
            def get_stop_cb():
                return self._is_cancelled

            actions = {
                "alignment": {
                    "Farneback Optical Flow": lambda: running_farneback_optical_flow(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "AKAZE": lambda: running_akaze(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "ORB": lambda: running_orb(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "Light Glue": lambda: running_light_glue(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "No Alignment": lambda: None,
                    "None": lambda: None,
                },
                "super_resolution": {
                    "WSR": lambda: running_weighted_sr(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "No Super Resolution": lambda: None,
                    "None": lambda: None,
                },


                "denoising": {
                    "Average": lambda: running_mf_denoiser(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                        merging_mode="average",
                        output_suffix="average",
                    ),
                    "Median": lambda: running_median(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "Similarity": lambda: running_similarity(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "No Denoising": lambda: None,
                    "None": lambda: None,
                },
            }

            # Execute selected algorithms
            any_algorithm_executed = False
            for category, selected_algo_name in self.settings.items():
                if not self._is_running:
                    break

                if not selected_algo_name or selected_algo_name in [
                    "None",
                    "No Alignment",
                    "No Super Resolution",
                    "No Denoising",
                ]:
                    continue

                if category in actions and selected_algo_name in actions[category]:
                    print(
                        f"[INFO] Executing '{selected_algo_name}' for batch_id: {self.batch_id}"
                    )
                    try:
                        actions[category][selected_algo_name]()
                        any_algorithm_executed = True
                    except Exception as e:
                        error_msg = f"Failed to execute {selected_algo_name}: {e}"
                        print(f"[ERROR] {error_msg}")
                        self.error_occurred.emit(error_msg)
                else:
                    print(
                        f"[WARN] Algorithm '{selected_algo_name}' for category '{category}' not found in actions."
                    )

            if not any_algorithm_executed:
                print(
                    f"[INFO] No algorithms were executed for batch_id: {self.batch_id}"
                )

        except Exception as e:
            error_msg = f"Critical error in algorithm processing: {e}"
            print(f"[ERROR] {error_msg}")
            self.error_occurred.emit(error_msg)
        finally:
            self.finished_processing.emit()

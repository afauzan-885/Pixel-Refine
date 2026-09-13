"""
Algorithm Processor Thread
Handles background execution of image processing algorithms with progress tracking.
"""

from PySide6.QtCore import QThread, Signal
import config

# Import algorithm functions
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.farneback_flow_cpu import (
    running_farneback_flow,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.AKAZE import (
    running_akaze,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.Light_Glue import (
    running_light_glue,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
    running_median,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    running_similarity as running_mf_similarity,
    running_mf_denoiser,
)

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.FusionNet import (
    running_fusionnet,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
    running_splatting_sr,
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

    def __init__(self, batch_id, settings, parent=None, single_process=None):
        """
        Initialize the algorithm processor thread.

        Args:
            batch_id: ID of the batch to process
            settings: Dict with algorithm selections (alignment, super_resolution, denoising)
            parent: Parent QObject (usually the layout or panel)
            single_process: If True, run in single process mode.
                           If False or if batch_id is given, run in batch processing mode.
        """
        super().__init__(parent)
        self.batch_id = batch_id if (batch_id is not None and batch_id > 0) else 1
        self.settings = settings
        self.parent_panel = parent
        self.single_process = False
        self._is_running = True
        self._is_cancelled = False

    def stop(self):
        """Request the thread to stop gracefully."""
        self._is_running = False
        self._is_cancelled = True
        self.cancel_requested.emit()
        try:
            from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
                BackendWorkerManager,
            )
            BackendWorkerManager.instance().stop_current_task()
        except Exception:
            pass

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        return self._is_cancelled

    def run(self):
        """Execute the selected algorithms via isolated backend worker."""
        import os

        if os.environ.get("PIXEL_REFINE_DISABLE_WORKER") == "1":
            return self._run_in_process()

        try:
            def progress_callback(percent, raw_msg=""):
                if self._is_running:
                    self.progress_update.emit(int(percent), str(raw_msg))

            controller = getattr(self.parent_panel, "controller", None)
            db_path = getattr(controller, "db_path", None)
            if not db_path:
                db_path = os.environ.get("PIXEL_REFINE_SESSION_DB")

            from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
                BackendWorkerManager,
            )

            if self._is_cancelled or not self._is_running:
                print("[AlgorithmProcessorThread] Task was cancelled before worker startup.")
                return

            worker_mgr = BackendWorkerManager.instance()
            if not worker_mgr.ensure_worker_ready():
                self.error_occurred.emit("Backend worker failed to start.")
                return

            if self._is_cancelled or not self._is_running:
                print("[AlgorithmProcessorThread] Task was cancelled while preparing worker.")
                return

            task_payload = {
                "batch_id": self.batch_id,
                "single_process": self.single_process,
                "db_path": db_path,
                "settings": self.settings,
            }

            result = worker_mgr.dispatch_task(
                task_payload,
                progress_cb=progress_callback,
                stop_requested_cb=lambda: self._is_cancelled,
            )

            if not result.get("success", False):
                if result.get("type") == "cancelled" or self._is_cancelled:
                    print(f"[AlgorithmProcessorThread] Task was cancelled by user.")
                else:
                    err = result.get("error", "Unknown error during processing.")
                    print(f"[AlgorithmProcessorThread] Worker error: {err}")
                    self.error_occurred.emit(str(err))

        except Exception as e:
            error_msg = f"Critical error in algorithm processing: {e}"
            print(f"[ERROR] {error_msg}")
            self.error_occurred.emit(error_msg)
        finally:
            self.finished_processing.emit()

    def _run_in_process(self):
        """Fallback in-process algorithm execution."""
        try:
            # Progress callback to emit signal with dual UI & Console messaging:
            def progress_callback(percent, message="", *args, **kwargs):
                if self._is_running:
                    # Support dictionary or kwargs if passed: progress_callback(percent, ui=..., console=...)
                    ui_msg = ""
                    console_msg = ""
                    if isinstance(message, dict):
                        ui_msg = str(message.get("ui", message.get("ui_msg", "")))
                        console_msg = str(message.get("console", message.get("console_msg", "")))
                    elif kwargs:
                        ui_msg = str(kwargs.get("ui", kwargs.get("ui_msg", message)))
                        console_msg = str(kwargs.get("console", kwargs.get("console_msg", message)))
                    elif args:
                        # message=ui_msg, args[0]=console_msg (or vice versa)
                        ui_msg = str(message)
                        console_msg = str(args[0])
                    else:
                        ui_msg = str(message)
                        console_msg = str(message)

                    if console_msg and console_msg != ui_msg:
                        print(f"[Pipeline Progress {int(percent)}%] {console_msg}")

                    # Forward as "ui_msg||console_msg"
                    self.progress_update.emit(int(percent), f"{ui_msg}||{console_msg}")

            # Define actions mapping
            def get_stop_cb():
                return self._is_cancelled

            is_align_checked = self.settings.get(config.KEY_CHECKBOX_ALIGN, True)
            is_sr_checked = self.settings.get(config.KEY_CHECKBOX_SUPER_RES, False)
            is_denoise_checked = self.settings.get(config.KEY_CHECKBOX_DENOISING, False)

            raw_align = self.settings.get(config.KEY_ALIGNMENT) or self.settings.get(
                config.KEY_ALIGNMENT_ALGO, "No Alignment"
            )
            alignment_choice = (
                raw_align
                if (is_align_checked and raw_align not in ("", "None"))
                else "No Alignment"
            )

            raw_sr = self.settings.get(
                config.KEY_SUPER_RESOLUTION
            ) or self.settings.get(
                config.KEY_SUPER_RESOLUTION_ALGO, "No Super Resolution"
            )
            super_resolution_choice = (
                raw_sr
                if (is_sr_checked and raw_sr not in ("", "None"))
                else "No Super Resolution"
            )

            raw_denoise = self.settings.get(config.KEY_DENOISING) or self.settings.get(
                config.KEY_DENOISING_ALGO, "No Denoising"
            )
            denoising_choice = (
                raw_denoise
                if (is_denoise_checked and raw_denoise not in ("", "None"))
                else "No Denoising"
            )

            denoising_active = denoising_choice not in (
                "",
                "None",
                "No Denoising",
            )
            denoising_owns_alignment = denoising_choice in (
                "Average",
                "Similarity",
                "Spatial AI",
                "FusionNet",
            )
            # SplattingSR performs its own internal Block Matching pass to
            # generate sub-pixel flow/confidence maps.  Never run the
            # user-selected alignment stage before it; that would apply an
            # external alignment twice and would also force an HDF5 roundtrip.
            super_resolution_owns_alignment = super_resolution_choice == "splattingSR"
            print(
                f"[AlgorithmProcessorThread] settings={self.settings} "
                f"alignment_choice={alignment_choice} "
                f"super_resolution_choice={super_resolution_choice} "
                f"denoising_choice={denoising_choice}"
            )

            actions = {
                "alignment": {
                    "Farneback": lambda: running_farneback_flow(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "Farneback Optical Flow": lambda: running_farneback_flow(
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
                    "OFB": lambda: running_mf_denoiser(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                        alignment_backend="OFB",
                        merging_mode="none",
                    ),
                    "Light Glue": lambda: running_light_glue(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "Lucas Kanade": lambda: running_mf_denoiser(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                        alignment_backend="Lucas Kanade",
                        merging_mode="none",
                    ),
                    "Block Matching GPU": lambda: running_mf_denoiser(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                        alignment_backend="Block Matching GPU",
                        merging_mode="none",
                    ),
                    "RAFT": lambda: running_mf_denoiser(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                        alignment_backend="RAFT",
                        merging_mode="none",
                    ),
                    "No Alignment": lambda: None,
                    "None": lambda: None,
                },
                "super_resolution": {
                    "splattingSR": lambda: running_splatting_sr(
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
                        alignment_backend=alignment_choice,
                    ),
                    "Median": lambda: running_median(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                    ),
                    "Similarity": lambda: running_mf_similarity(
                        self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                        alignment_backend=alignment_choice,
                    ),
                    "Spatial AI": lambda: running_fusionnet(
                        parent=self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                        alignment_backend=alignment_choice,
                    ),
                    "FusionNet": lambda: running_fusionnet(
                        parent=self.parent_panel,
                        single_process=self.single_process,
                        batch_id=self.batch_id,
                        progress_callback=progress_callback,
                        stop_callback=get_stop_cb,
                        alignment_backend=alignment_choice,
                    ),
                    "No Denoising": lambda: None,
                    "None": lambda: None,
                },
            }

            any_algorithm_executed = False

            def execute(category, selected_algo_name):
                nonlocal any_algorithm_executed
                if not self._is_running:
                    return
                if not selected_algo_name or selected_algo_name in [
                    "None",
                    "No Alignment",
                    "No Super Resolution",
                    "No Denoising",
                ]:
                    return
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

            if denoising_owns_alignment or super_resolution_owns_alignment:
                if alignment_choice not in ("", "None", "No Alignment"):
                    print(
                        f"[AlgorithmProcessorThread] Alignment '{alignment_choice}' "
                        "is owned by the selected internal pipeline; external "
                        "alignment is bypassed."
                    )
                if denoising_owns_alignment:
                    execute("denoising", denoising_choice)
                execute("super_resolution", super_resolution_choice)
            else:
                execute("alignment", alignment_choice)
                execute("denoising", denoising_choice)
                execute("super_resolution", super_resolution_choice)

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

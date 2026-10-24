"""
Algorithm Processor Thread
Handles background execution of image processing algorithms with progress tracking.
"""

from PySide6.QtCore import QThread, Signal
import config
from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import get_spec, normalize_name, plan_stages, run_algorithm

# Import algorithm functions
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.farneback_flow import (
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
    running_mf_denoiser,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.HDR import (
    SPDEMRAlgorithm,
    WeightedHDRAlgorithm,
    running_hdr_fusion,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
    running_splatting_sr,
)


_SUPPORTED_BACKENDS = ("cuda", "vulkan", "cpu")


def _is_backend_compatibility_error(result):
    """Retry only errors that point to an unavailable or failed backend graph."""
    details = " ".join(
        str(result.get(key, "")) for key in ("error", "traceback", "message")
    ).casefold()
    graph_markers = (".tcm", "tcm", "graph", "compute_graph", "aot")
    graph_failures = (
        "unavailable", "not found", "name not found", "compile",
        "compilation", "c-api error", "launch failed",
    )
    device_markers = ("backend", "cuda", "vulkan", "opengl", "device")
    device_failures = (
        "failed to initialize", "could not initialize", "initialization failed",
        "device lost", "device unavailable", "no cuda-capable device",
    )
    return (
        any(marker in details for marker in graph_markers)
        and any(marker in details for marker in graph_failures)
    ) or (
        any(marker in details for marker in device_markers)
        and any(marker in details for marker in device_failures)
    )


def _fallback_backend_configs(worker_mgr):
    """Build remaining backend candidates from the selected device's saved chain."""
    active = worker_mgr.get_current_backend_config()
    try:
        from pixel_refine_desktop.ui.views.settings.General.general_store import (
            get_general_store,
        )

        store = get_general_store()
    except Exception:
        store = None

    chain = active.get("device_fallback_chain")
    if not chain and store is not None:
        chain = store.get("device_fallback_chain", [])
    current_backend = str(active.get("arch", "cpu")).strip().lower()
    if not chain or current_backend not in {
        str(item).strip().lower() for item in chain
    }:
        if current_backend == "cuda":
            chain = ["cuda", "vulkan", "cpu"]
        elif current_backend == "vulkan":
            chain = ["vulkan", "cpu"]
        else:
            chain = [current_backend]
    chain = [str(item).strip().lower() for item in (chain or [])]
    # OpenGL is excluded from the recovery chain: its native graph dispatch
    # crashes the worker (0xC0000005) on validated NVIDIA desktop drivers, so
    # a stored chain containing it must never be retried here.
    chain = [item for item in chain if item in _SUPPORTED_BACKENDS]

    try:
        start_index = chain.index(current_backend) + 1
    except ValueError:
        return []

    def stored_id(config_key, store_key, fallback):
        value = active.get(config_key)
        if value is None and store is not None:
            value = store.get(store_key)
        try:
            if value is None or int(value) < 0:
                return fallback
        except (TypeError, ValueError):
            return fallback
        return int(value)

    cuda_id = stored_id("cuda_device_id", "device_cuda_id", 0)
    vulkan_id = stored_id("vulkan_device_id", "device_vulkan_id", 0)
    base_text = active.get("selected_backend_text") or active.get(
        "backend_text", "GPU"
    )
    candidates = []
    for backend in chain[start_index:]:
        device_id = {
            "cuda": cuda_id,
            "vulkan": vulkan_id,
            "cpu": 0,
        }[backend]
        candidate = dict(active)
        candidate.update(
            arch=backend,
            device_id=device_id,
            backend_text=f"{base_text} — {backend.upper()} auto fallback",
            auto_fallback=True,
            device_fallback_chain=chain,
            cuda_device_id=cuda_id,
            vulkan_device_id=vulkan_id,
            selected_backend_text=base_text,
            runtime_fallback=True,
        )
        candidates.append(candidate)
    return candidates


def dispatch_worker_task(worker_mgr, task_payload, progress_callback, stop_requested):
    """Run a task with the shared backend recovery policy outside the UI thread."""
    result = worker_mgr.dispatch_task(
        task_payload,
        progress_cb=progress_callback,
        stop_requested_cb=stop_requested,
    )

    attempted_backends = []
    while (
        not result.get("success", False)
        and result.get("type") != "cancelled"
        and not stop_requested()
        and _is_backend_compatibility_error(result)
    ):
        active_config = worker_mgr.get_current_backend_config()
        try:
            from pixel_refine_desktop.ui.views.settings.General.general_store import (
                get_general_store,
            )

            auto_fallback = bool(
                get_general_store().get(
                    "auto_fallback", active_config.get("auto_fallback", True)
                )
            )
        except Exception:
            auto_fallback = bool(active_config.get("auto_fallback", True))
        if not auto_fallback:
            break

        candidates = _fallback_backend_configs(worker_mgr)
        if not candidates:
            break

        initial_error = result.get("error", "Unknown backend error.")
        recovered = False
        for candidate in candidates:
            if stop_requested():
                break
            backend = candidate["arch"]
            attempted_backends.append(backend.upper())
            progress_callback(
                0,
                f"Backend tidak kompatibel; mencoba {backend.upper()} otomatis...",
            )
            print(
                f"[AlgorithmProcessorThread] Backend error on "
                f"{active_config.get('arch', 'unknown')}; trying {backend}.",
                flush=True,
            )
            if not worker_mgr.switch_backend(candidate, force_restart=True):
                print(
                    f"[AlgorithmProcessorThread] Could not start {backend} fallback worker.",
                    flush=True,
                )
                continue

            if stop_requested():
                break
            result = worker_mgr.dispatch_task(
                task_payload,
                progress_cb=progress_callback,
                stop_requested_cb=stop_requested,
            )
            if result.get("success", False):
                progress_callback(
                    0, f"Melanjutkan pemrosesan dengan {backend.upper()}..."
                )
                recovered = True
                break
            if result.get("type") == "cancelled" or stop_requested():
                break
            if not _is_backend_compatibility_error(result):
                recovered = True
                break
            active_config = worker_mgr.get_current_backend_config()

        if recovered or result.get("type") == "cancelled" or stop_requested():
            break

        if attempted_backends:
            tried = " → ".join(attempted_backends)
            last_error = result.get("error", initial_error)
            result = dict(result)
            result["error"] = (
                f"Auto Fallback sudah mencoba {tried}, tetapi pemrosesan "
                f"belum berhasil. Error terakhir: {last_error}"
            )
        break
    return result


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

            from pixel_refine_desktop.app_core import perf_probe

            # The first start of a session waits for the worker's cold boot
            # (engine init + algorithm pre-imports).  Say so in the UI instead of
            # leaving the progress bar frozen at 0%, which reads as a hang.
            self.progress_update.emit(0, "Menyiapkan mesin proses...")

            # Measures the respawn cost when the idle policy has put the worker
            # to sleep between batches; this is the batch-start latency.
            # ensure_worker_ready() waits for the ready handshake, not merely a
            # live process, within START_READY_TIMEOUT_S.
            _ready_mark = perf_probe.perf_mark(
                "worker_ready", batch_id=self.batch_id
            )
            _ready = worker_mgr.ensure_worker_ready()
            _ready_mark.end(ready=_ready)
            if not _ready:
                self.error_occurred.emit(
                    "Mesin proses belum siap (worker masih memuat). "
                    "Tunggu sebentar lalu jalankan lagi."
                )
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

            _task_mark = perf_probe.perf_mark("dispatch_task", batch_id=self.batch_id)
            stop_requested = lambda: self._is_cancelled or not self._is_running
            result = dispatch_worker_task(
                worker_mgr, task_payload, progress_callback, stop_requested
            )

            _task_mark.end(success=bool(result.get("success", False)))

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
            import os

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
            is_hdr_checked = self.settings.get(config.KEY_CHECKBOX_HDR, False)

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
            raw_hdr = self.settings.get(config.KEY_HDR) or self.settings.get(
                config.KEY_HDR_ALGO, "No HDR"
            )
            hdr_choice = (
                raw_hdr
                if (is_hdr_checked and raw_hdr not in ("", "None"))
                else "No HDR"
            )

            alignment_choice = normalize_name("alignment", alignment_choice)
            super_resolution_choice = normalize_name("super_resolution", super_resolution_choice)
            denoising_choice = normalize_name("denoising", denoising_choice)
            hdr_choice = normalize_name("hdr", hdr_choice)

            db_path = getattr(
                getattr(self.parent_panel, "controller", None), "db_path", None
            ) or os.environ.get("PIXEL_REFINE_SESSION_DB")
            print(
                f"[AlgorithmProcessorThread] settings={self.settings} "
                f"alignment_choice={alignment_choice} "
                f"super_resolution_choice={super_resolution_choice} "
                f"denoising_choice={denoising_choice} hdr_choice={hdr_choice}"
            )

            any_algorithm_executed = False

            def execute(category, selected_algo_name):
                nonlocal any_algorithm_executed
                if not self._is_running:
                    return
                try:
                    spec = get_spec(category, selected_algo_name)
                    if spec.disabled:
                        return
                    print(
                        f"[INFO] Executing '{spec.name}' for batch_id: {self.batch_id}"
                    )
                    kwargs = {
                        "single_process": self.single_process,
                        "batch_id": self.batch_id,
                        "progress_callback": progress_callback,
                        "stop_callback": get_stop_cb,
                    }
                    if category == "hdr":
                        kwargs["db_path"] = db_path
                    if category == "denoising" and spec.owns_alignment:
                        kwargs["alignment_backend"] = alignment_choice
                    # Retain imported entrypoints for existing callers/test injection.
                    entrypoint = globals().get(spec.entrypoint.rsplit(":", 1)[-1])
                    run_algorithm(
                        category, spec.key, self.parent_panel,
                        executor=entrypoint, **kwargs,
                    )
                    any_algorithm_executed = True
                except Exception as exc:
                    error_msg = f"Failed to execute {selected_algo_name}: {exc}"
                    print(f"[ERROR] {error_msg}")
                    self.error_occurred.emit(error_msg)

            stages = plan_stages({
                "alignment": alignment_choice,
                "denoising": denoising_choice,
                "super_resolution": super_resolution_choice,
                "hdr": hdr_choice,
            })
            for spec in stages:
                execute(spec.category, spec.name)

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

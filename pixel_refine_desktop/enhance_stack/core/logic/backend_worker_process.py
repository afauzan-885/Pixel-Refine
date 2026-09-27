"""
Isolated Backend Worker Process
===============================
Runs as an independent OS subprocess hosting the Taichi Vision and ONNX compute runtime.
Zero VRAM/RAM residue on exit; allows real-time hardware backend switching without
restarting the main application.

Communication protocol:
- Reads JSON commands line-by-line from stdin.
- Writes JSON events line-by-line to stdout (unbuffered).
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True, write_through=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True, write_through=True)
    except Exception:
        pass

# Guarantee workspace root is in sys.path regardless of how the subprocess is invoked
workspace_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import json
import threading
import queue
import traceback

# Preload numpy before anything imports taichi_vision.
#
# ``taichi_vision.taichi_aot`` runs ``engine.py`` through a file-location loader
# during its own package init, and ``engine.py`` imports numpy.  When numpy's
# native extension was first loaded inside that nested import context, the
# Windows loader deadlocked: the spawned worker never printed anything, never
# sent its ready handshake, and the application looked hung ("worker did not
# send ready in time").  Loading numpy here first keeps that DLL load in a clean
# loader state; the later import inside the package init becomes a sys.modules
# hit.  Verified by stack dump: before this, the worker was stuck in
# ``create_module`` for a numpy extension; after it, the worker reaches ready and
# idles in its command queue.
try:
    import numpy as _numpy_preload  # noqa: F401
except Exception:
    pass


def send_ipc(msg: dict):
    """Write newline-delimited JSON message to stdout and flush."""
    try:
        sys.stdout.write(json.dumps(msg) + "\n")
        sys.stdout.flush()
    except Exception:
        pass


class WorkerRunner:
    def __init__(self):
        self.cmd_queue = queue.Queue()
        self.current_stop_event = threading.Event()
        self.is_running = True
        self.current_task_id = None

    def start_stdin_reader(self):
        """Read lines from stdin asynchronously to remain responsive to stop commands."""
        def reader():
            while self.is_running:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        # EOF received (parent closed pipe)
                        self.cmd_queue.put({"cmd": "shutdown"})
                        break
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    cmd = data.get("cmd")
                    if cmd == "stop":
                        # Immediate stop trigger
                        self.current_stop_event.set()
                    self.cmd_queue.put(data)
                except Exception as exc:
                    send_ipc({"type": "log", "level": "warning", "message": f"Stdin read error: {exc}"})
                    break

        t = threading.Thread(target=reader, daemon=True, name="WorkerStdinReader")
        t.start()

    def run_loop(self):
        """Main event loop processing tasks from the command queue."""
        arch = os.environ.get("AOT_ARCH", "unknown")
        device = os.environ.get("AOT_DEVICE", "0")
        vendor = os.environ.get("TARGET_VENDOR", "")

        # Pre-initialize Taichi Vision engine in worker background so backend DLLs load immediately
        try:
            import taichi_vision.taichi_aot as ta_aot
            ta_aot.get_engine()
        except Exception as e:
            send_ipc({"type": "log", "level": "warning", "message": f"Taichi AOT engine pre-init: {e}"})

        # Pre-import and initialize algorithms during startup
        try:
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
                running_mf_denoiser,
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
                running_median,
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
                running_splatting_sr,
            )
            import config
            self._algorithms_ready = True
        except Exception as e:
            send_ipc({"type": "log", "level": "error", "message": f"Pre-import error: {e}"})
            self._algorithms_ready = False

        # Announce readiness after engine and algorithm modules are loaded
        send_ipc({
            "type": "ready",
            "pid": os.getpid(),
            "arch": arch,
            "device": device,
            "vendor": vendor,
        })



        while self.is_running:
            try:
                msg = self.cmd_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            cmd = msg.get("cmd")
            if cmd == "shutdown":
                self.is_running = False
                break
            elif cmd == "ping":
                send_ipc({
                    "type": "pong",
                    "status": "busy" if self.current_task_id else "idle",
                    "pid": os.getpid(),
                    "arch": os.environ.get("AOT_ARCH", "unknown"),
                    "device": os.environ.get("AOT_DEVICE", "0"),
                })
            elif cmd == "execute":
                self.execute_task(msg)

    def execute_task(self, msg: dict):
        task_id = msg.get("task_id", "default")
        self.current_task_id = task_id

        # If stop was already signaled (e.g. user clicked cancel during worker warmup or task queueing)
        if self.current_stop_event.is_set():
            send_ipc({
                "type": "cancelled",
                "task_id": task_id,
                "message": "Task cancelled before execution.",
            })
            self.current_stop_event.clear()
            self.current_task_id = None
            return

        self.current_stop_event.clear()

        batch_id = msg.get("batch_id")
        if batch_id is None or batch_id == 0:
            batch_id = 1
        single_process = False
        db_path = msg.get("db_path")
        settings = msg.get("settings", {})

        if db_path:
            os.environ["PIXEL_REFINE_SESSION_DB"] = db_path

        def progress_callback(percent, message="", *args, **kwargs):
            if self.current_stop_event.is_set():
                return
            ui_msg = ""
            console_msg = ""
            if isinstance(message, dict):
                ui_msg = str(message.get("ui", message.get("ui_msg", "")))
                console_msg = str(message.get("console", message.get("console_msg", "")))
            elif kwargs:
                ui_msg = str(kwargs.get("ui", kwargs.get("ui_msg", message)))
                console_msg = str(kwargs.get("console", kwargs.get("console_msg", message)))
            elif args:
                ui_msg = str(message)
                console_msg = str(args[0])
            else:
                ui_msg = str(message)
                console_msg = str(message)

            send_ipc({
                "type": "progress",
                "task_id": task_id,
                "percent": int(percent),
                "ui_msg": ui_msg,
                "console_msg": console_msg,
                "raw_msg": f"{ui_msg}||{console_msg}",
            })

        def stop_callback():
            return self.current_stop_event.is_set()

        try:
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
                running_mf_denoiser,
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.HDR import (
                SPDEMRAlgorithm,
                WeightedHDRAlgorithm,
                running_hdr_fusion,
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
                running_median,
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
                running_splatting_sr,
            )
            import config

            is_align_checked = settings.get(config.KEY_CHECKBOX_ALIGN, True)
            is_sr_checked = settings.get(config.KEY_CHECKBOX_SUPER_RES, False)
            is_denoise_checked = settings.get(config.KEY_CHECKBOX_DENOISING, False)
            is_hdr_checked = settings.get(config.KEY_CHECKBOX_HDR, False)

            raw_align = settings.get(config.KEY_ALIGNMENT) or settings.get(
                config.KEY_ALIGNMENT_ALGO, "No Alignment"
            )
            alignment_choice = (
                raw_align
                if (is_align_checked and raw_align not in ("", "None"))
                else "No Alignment"
            )

            raw_sr = settings.get(config.KEY_SUPER_RESOLUTION) or settings.get(
                config.KEY_SUPER_RESOLUTION_ALGO, "No Super Resolution"
            )
            super_resolution_choice = (
                raw_sr
                if (is_sr_checked and raw_sr not in ("", "None"))
                else "No Super Resolution"
            )

            raw_denoise = settings.get(config.KEY_DENOISING) or settings.get(
                config.KEY_DENOISING_ALGO, "No Denoising"
            )
            denoising_choice = (
                raw_denoise
                if (is_denoise_checked and raw_denoise not in ("", "None"))
                else "No Denoising"
            )
            raw_hdr = settings.get(config.KEY_HDR) or settings.get(
                config.KEY_HDR_ALGO, "No HDR"
            )
            hdr_choice = (
                raw_hdr
                if (is_hdr_checked and raw_hdr not in ("", "None"))
                else "No HDR"
            )

            denoising_owns_alignment = denoising_choice in (
                "Average",
                "Similarity",
                "Spatial AI",
                "FusionNet",
            )
            super_resolution_owns_alignment = super_resolution_choice == "splattingSR"
            hdr_owns_alignment = hdr_choice in (
                WeightedHDRAlgorithm.NAME,
                WeightedHDRAlgorithm.LEGACY_NAME,
                SPDEMRAlgorithm.NAME,
            )

            actions = {
                "alignment": {
                    "Lucas Kanade": lambda: running_mf_denoiser(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        alignment_backend="Lucas Kanade",
                        merging_mode="none",
                        db_path=db_path,
                    ),
                    "Block Matching GPU": lambda: running_mf_denoiser(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        alignment_backend="Block Matching GPU",
                        merging_mode="none",
                        db_path=db_path,
                    ),
                    "RAFT": lambda: running_mf_denoiser(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        alignment_backend="RAFT",
                        merging_mode="none",
                        db_path=db_path,
                    ),
                    "No Alignment": lambda: None,
                    "None": lambda: None,
                },
                "super_resolution": {
                    "splattingSR": lambda: running_splatting_sr(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        db_path=db_path,
                    ),
                    "No Super Resolution": lambda: None,
                    "None": lambda: None,
                },
                "hdr": {
                    WeightedHDRAlgorithm.NAME: lambda: running_hdr_fusion(
                        single_process=single_process,
                        batch_id=batch_id,
                        algorithm_name=WeightedHDRAlgorithm.NAME,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        db_path=db_path,
                    ),
                    WeightedHDRAlgorithm.LEGACY_NAME: lambda: running_hdr_fusion(
                        single_process=single_process,
                        batch_id=batch_id,
                        algorithm_name=WeightedHDRAlgorithm.NAME,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        db_path=db_path,
                    ),
                    SPDEMRAlgorithm.NAME: lambda: running_hdr_fusion(
                        single_process=single_process,
                        batch_id=batch_id,
                        algorithm_name=SPDEMRAlgorithm.NAME,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        db_path=db_path,
                    ),
                    "No HDR": lambda: None,
                    "None": lambda: None,
                },
                "denoising": {
                    "Average": lambda: running_mf_denoiser(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        merging_mode="average",
                        output_suffix="average",
                        alignment_backend=alignment_choice,
                        db_path=db_path,
                    ),
                    "Median": lambda: running_median(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                    ),
                    "Similarity": lambda: running_mf_denoiser(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        merging_mode="Similarity",
                        output_suffix="similarity",
                        alignment_backend=alignment_choice,
                        db_path=db_path,
                    ),
                    "Spatial AI": lambda: running_mf_denoiser(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        merging_mode="FusionNet",
                        output_suffix="fusionet",
                        alignment_backend=alignment_choice,
                        db_path=db_path,
                    ),
                    "FusionNet": lambda: running_mf_denoiser(
                        single_process=single_process,
                        batch_id=batch_id,
                        progress_callback=progress_callback,
                        stop_callback=stop_callback,
                        merging_mode="FusionNet",
                        output_suffix="fusionet",
                        alignment_backend=alignment_choice,
                        db_path=db_path,
                    ),
                    "No Denoising": lambda: None,
                    "None": lambda: None,
                },
            }

            any_executed = False

            def execute(category, selected_algo_name):
                nonlocal any_executed
                if stop_callback():
                    return
                if not selected_algo_name or selected_algo_name in [
                    "None",
                    "No Alignment",
                    "No Super Resolution",
                    "No Denoising",
                    "No HDR",
                ]:
                    return
                if category in actions and selected_algo_name in actions[category]:
                    send_ipc({
                        "type": "log",
                        "level": "info",
                        "message": f"Worker executing '{selected_algo_name}' for batch_id: {batch_id}",
                    })
                    actions[category][selected_algo_name]()
                    any_executed = True
                else:
                    send_ipc({
                        "type": "log",
                        "level": "warning",
                        "message": f"Algorithm '{selected_algo_name}' in category '{category}' not recognized.",
                    })

            if (
                denoising_owns_alignment
                or super_resolution_owns_alignment
                or hdr_owns_alignment
            ):
                if denoising_owns_alignment:
                    execute("denoising", denoising_choice)
                execute("super_resolution", super_resolution_choice)
                execute("hdr", hdr_choice)
            else:
                execute("alignment", alignment_choice)
                execute("super_resolution", super_resolution_choice)
                execute("hdr", hdr_choice)
                execute("denoising", denoising_choice)

            if stop_callback():
                send_ipc({
                    "type": "cancelled",
                    "task_id": task_id,
                    "message": "Task cancelled by user (partial result preserved).",
                    "success": True,
                    "any_executed": any_executed,
                    "recovered": True,
                })
            else:
                send_ipc({
                    "type": "finished",
                    "task_id": task_id,
                    "success": True,
                    "any_executed": any_executed,
                })

        except Exception as exc:
            tb = traceback.format_exc()
            send_ipc({
                "type": "error",
                "task_id": task_id,
                "error": str(exc),
                "traceback": tb,
            })
        finally:
            self.current_task_id = None
            # --- Universal Post-Task Memory Cleanup ---
            try:
                import taichi_vision.taichi_aot as ta_aot
                engine = ta_aot.get_engine()
                if hasattr(engine, "buffer_pool") and hasattr(engine.buffer_pool, "clear"):
                    engine.buffer_pool.clear()
                if hasattr(engine, "_drain_retired"):
                    engine._drain_retired(wait=True)
                if hasattr(engine, "sync"):
                    engine.sync()
            except Exception:
                pass

            try:
                from taichi_vision.taichi_algorithm.aot_api import clear_farneback_cache
                clear_farneback_cache()
            except Exception:
                pass

            try:
                from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_pipeline import (
                    clear_spatial_cache,
                )
                clear_spatial_cache()
            except Exception:
                pass

            try:
                actions = None
                settings = None
                msg = None
            except Exception:
                pass

            import gc
            gc.collect()

            if sys.platform == "win32":
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetProcessWorkingSetSize(
                        ctypes.windll.kernel32.GetCurrentProcess(), -1, -1
                    )
                except Exception:
                    pass


def main():
    runner = WorkerRunner()
    runner.start_stdin_reader()
    runner.run_loop()
    sys.exit(0)


if __name__ == "__main__":
    main()

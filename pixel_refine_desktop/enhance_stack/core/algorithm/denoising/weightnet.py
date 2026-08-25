"""
WeightNet / FusionNet Desktop Orchestrator.
Delegates image list to weightnet_engine/weightnet_inference.py, receives uncompressed float32 array,
and saves the final result.
"""

import os
import threading
import traceback
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox, QProgressBar, QVBoxLayout

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    extract_all_metadata,
    get_all_image_paths_for_single_process,
    get_all_image_paths_for_batch_process,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.weightnet_engine.weightnet_inference import (
    run_weightnet_inference,
)
from resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


class FusionNetDenoisingAlgorithm:
    """WeightNet ONNX-based deep multi-frame fusion denoising adapter."""

    NAME = "FusionNet"
    KIND = "denoising"
    DESCRIPTION = "Deep learning multi-frame burst fusion using WeightNet ONNX."

    def run(self, ctx, frames, batch_plan=None):
        raise RuntimeError("FusionNet must be launched through running_weightnet.")


def save_rgb_result(image_fp32: np.ndarray, output_path: str | Path) -> None:
    """Save uncompressed float32 RGB array [H, W, 3] to 16-bit TIFF or PNG/JPEG."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = np.ascontiguousarray(np.clip(image_fp32, 0.0, 1.0), dtype=np.float32)

    ext = output_path.suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        Image.fromarray((image * 255.0 + 0.5).astype(np.uint8), mode="RGB").save(
            output_path, quality=95
        )
    elif ext == ".png":
        image_u8 = np.clip(image * 255.0 + 0.5, 0, 255).astype(np.uint8)
        image_bgr = cv2.cvtColor(image_u8, cv2.COLOR_RGB2BGR)
        if not cv2.imwrite(str(output_path), image_bgr):
            raise RuntimeError(f"Failed to save PNG result: {output_path}")
    else:
        # Default: 16-bit TIFF
        image_u16 = np.clip(image * 65535.0 + 0.5, 0, 65535).astype(np.uint16)
        image_bgr = cv2.cvtColor(image_u16, cv2.COLOR_RGB2BGR)
        if not cv2.imwrite(str(output_path), image_bgr):
            raise RuntimeError(f"Failed to save 16-bit RGB result: {output_path}")


def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    progress_bar=None,
    work_scale: float = 0.50,
    tile_size: int = 256,
    overlap: float = 0.30,
):
    """
    Orchestrator: resolves image paths -> passes to weightnet_inference ->
    receives float32 -> saves result to database/stack.
    """
    try:
        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)

        # 1. Mengambil list data gambar dari database
        if single_process:
            image_paths = get_all_image_paths_for_single_process(db_path)
            ref_name = (
                os.path.splitext(os.path.basename(image_paths[0]))[0]
                if image_paths
                else "single_process"
            )
        else:
            if batch_id is None:
                raise ValueError(
                    language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS
                )
            image_paths = get_all_image_paths_for_batch_process(db_path, batch_id)
            ref_name = (
                os.path.splitext(os.path.basename(image_paths[0]))[0]
                if image_paths
                else f"batch_{batch_id}"
            )

        if not image_paths:
            if update_progress:
                update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return

        metadata_output_path = os.path.join("database", "align", "metadata.json")
        try:
            extract_all_metadata(image_paths, metadata_file=metadata_output_path)
        except Exception:
            pass

        output_name_safe = (
            "".join(c for c in ref_name if c.isalnum() or c in ("_", "-")).rstrip()
            or "stack_result"
        )
        output_path = os.path.join(
            output_folder_stack, f"{output_name_safe}_weightnet.tif"
        )
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))

        # 2. Mengumpankan list gambar ke dalam weightnet_inference.py
        stop_event = threading.Event()

        def progress_bridge(val, msg):
            if stop_requested and stop_requested():
                stop_event.set()
            if update_progress:
                update_progress(val, msg)

        result_float32, alpha = run_weightnet_inference(
            image_paths=image_paths,
            work_scale=work_scale,
            tile_size=tile_size,
            overlap=overlap,
            stop_event=stop_event,
            progress_callback=progress_bridge,
        )

        if stop_requested and stop_requested():
            if update_progress:
                update_progress(100, "Proses dibatalkan.")
            return

        # 3. Menerima float32 tak terkompresi & Simpan hasil
        if update_progress:
            update_progress(96, "Menyimpan hasil fusi...")

        save_rgb_result(result_float32, output_path)

        final_message = (
            f"{language_config.IMAGE_PROCESS_FINISHED}: "
            f"{os.path.basename(output_path)} (alpha={alpha:.4f})"
        )
        if update_progress:
            update_progress(100, final_message)

    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)


def running_weightnet(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
    db_path=None,
):
    if not db_path:
        controller = getattr(parent, "controller", None)
        db_path = getattr(controller, "db_path", None)
    db_path = (
        db_path
        or os.environ.get("PIXEL_REFINE_SESSION_DB")
        or "pixel_refine_database.db"
    )

    # MODE BATCH (TANPA GUI)
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path=db_path,
                update_progress=progress_callback,
                stop_requested=stop_callback,
                single_process=False,
                batch_id=batch_id,
            )
        except Exception as e:
            raise e
        return

    # MODE SINGLE (DENGAN GUI DIALOG)
    process_finished = False
    dialog = QDialog(parent)
    dialog.setWindowTitle(
        getattr(language_config, "WINDOW_TITLE_WEIGHTNET", "FusionNet Stacking")
    )
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
    )

    layout = QVBoxLayout(dialog)
    label = QLabel(language_config.WINDOW_START_PROCESSING)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(progress_bar)

    worker = BaseAlgorithmWorker(
        main,
        db_path,
        single_process=single_process,
        batch_id=batch_id,
    )
    worker.progress_updated.connect(
        lambda progress, message: (
            progress_bar.setValue(progress),
            label.setText(message),
        )
    )

    def finish_handler():
        nonlocal process_finished
        process_finished = True
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(
            dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error)
        )
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(
                dialog,
                "Cancel Process",
                language_config.CANCEL_PROCESSING,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                worker.stop()
                worker.quit()
                worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    dialog.closeEvent = on_dialog_close
    worker.start()
    dialog.exec()


if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    main(db_path)

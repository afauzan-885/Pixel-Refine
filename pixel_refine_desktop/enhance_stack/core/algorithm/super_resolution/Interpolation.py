import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PySide6.QtCore import QThread, Signal, Qt

from resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


class ThreadWorker(QThread):
    progress_updated = Signal(int, str)  # Sinyal untuk memperbarui progress
    finished = Signal()  # Sinyal untuk menandakan selesai
    error_occurred = Signal(str)  # Sinyal untuk menandakan error

    def __init__(self, db_path, single_process=True, batch_id=None):
        super().__init__()
        self.db_path = db_path
        self.single_process = (
            single_process  # Menentukan apakah proses single atau batch
        )
        self.batch_id = batch_id  # ID batch jika batch processing
        self.stop_requested = False  # Flag untuk menghentikan thread

    def run(self):
        try:

            def update_progress(progress, message):
                self.progress_updated.emit(progress, message)

            # Fungsi callback untuk mengecek status stop
            def is_stop_requested():
                return self.stop_requested

            # Panggil main dengan parameter yang sesuai
            main(
                self.db_path,
                update_progress=update_progress,
                stop_requested=is_stop_requested,
                single_process=self.single_process,
                batch_id=self.batch_id,
            )

            self.finished.emit()
        except Exception as e:
            print(f"Error terjadi: {str(e)}")  # Menampilkan pesan error di konsol
            self.error_occurred.emit(str(e))  # Mengirim pesan error melalui sinyal

    def stop(self):
        self.stop_requested = True

        pass


def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
):
    """Thread-safe entry point used by ``ThreadWorker.run``.

    The legacy UI dialog is hosted via :func:`running_interpolation`,
    which is driven by ``BaseAlgorithmWorker``. Headless callers can use
    this entry point to perform interpolation without spawning a UI
    dialog.
    """
    # No-op wrapper kept for backward compatibility. The MFDenoiser
    # orchestrator handles actual interpolation; this function exists
    # so that ``ThreadWorker.run`` can still invoke it when the legacy
    # single-process super-resolution pipeline is requested.
    return None


def running_interpolation(parent=None, single_process=None, batch_id=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    controller = getattr(parent, "controller", None)
    db_path = getattr(controller, "db_path", None)
    db_path = db_path or os.environ.get("PIXEL_REFINE_SESSION_DB")
    if not db_path:
        raise RuntimeError(
            "A session database is required for interpolation. "
            "Set PIXEL_REFINE_SESSION_DB or pass db_path explicitly."
        )

    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_INTERPOLATION)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
    )

    # Layout untuk progress bar dan label
    layout = QVBoxLayout(dialog)
    label = QLabel(language_config.WINDOW_START_PROCESSING)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(progress_bar)

    # Inisialisasi thread worker
    worker = ThreadWorker(db_path, single_process=single_process, batch_id=batch_id)

    # Menghubungkan signal worker ke fungsi pembaruan UI
    worker.progress_updated.connect(
        lambda progress, message: (
            progress_bar.setValue(progress),
            label.setText(message),
        )
    )

    def finish_handler():
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)

    def error_handler(error):

        # messages: An error occurred
        QMessageBox.critical(
            dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error)
        )
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    # Mulai worker
    worker.start()

    # Pastikan worker dihentikan jika dialog ditutup
    def on_dialog_close(event):
        if worker.isRunning():
            # Menampilkan konfirmasi sebelum menutup dialog
            reply = QMessageBox.question(
                dialog,
                "Cancel Process",
                # message: Are you sure you want to cancel the process?
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

    dialog.closeEvent = on_dialog_close

    dialog.exec()

# batch_process_dialog.py

import os
import time
from PySide6.QtCore import Signal, QObject, QThread, QRectF
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QWidget
)
from PySide6.QtGui import QColor, QPixmap, QColor, QBrush

from UI.panorama.Algorithm.dispatcher_panorama_algorithm import run_panorama_stitching_process
from UI.resources.animation.loading.modern_progress_bar import ModernProgressBar

def stitch_panorama_placeholder(images, settings, progress_callback):
    """Fungsi placeholder untuk mensimulasikan proses stitching."""
    print(f"  -> Stitching {len(images)} images with settings: {settings}")
    if len(images) < 2:
        raise ValueError("Not enough images to create a panorama.")
    
    # Definisikan bobot untuk setiap tahap
    PROCESS_WEIGHTS = {"align": 0.4, "project": 0.2, "blend": 0.3, "save": 0.1}
    cumulative_progress = 0.0

    # Tahap 1: Alignment
    time.sleep(1.0)
    cumulative_progress += PROCESS_WEIGHTS["align"]
    progress_callback(cumulative_progress, "Aligning (100%)")

    # Tahap 2: Projection
    time.sleep(0.5)
    cumulative_progress += PROCESS_WEIGHTS["project"]
    progress_callback(cumulative_progress, "Projection (100%)")

    # Tahap 3: Blending
    time.sleep(1.0)
    cumulative_progress += PROCESS_WEIGHTS["blend"]
    progress_callback(cumulative_progress, "Blending (100%)")

    # Tahap 4: Saving
    time.sleep(0.2)
    cumulative_progress += PROCESS_WEIGHTS["save"]
    progress_callback(cumulative_progress, "Saving (100%)")

    return True

class ProgressSegmentWidget(QWidget):
    """
    Blok bangunan yang HANYA berisi ModernProgressBar.
    Label status telah dihapus.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout sekarang hanya berisi progress bar
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Tidak perlu margin
        
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setFixedHeight(15) # Sedikit lebih tinggi agar lebih jelas
        
        layout.addWidget(self.progress_bar)

    def setProgress(self, value: int):
        self.progress_bar.setValue(value)

    def setColor(self, color: QColor):
        self.progress_bar.setBarColor(color)        

class SegmentedProgressBar(QWidget):
    """
    Widget kontainer yang mengatur beberapa ProgressSegmentWidget
    dan mengisi celah di antara mereka.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20) # Kurangi tinggi karena tidak ada label

        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(5)

        self._segments = []
        
        # --- PERBAIKAN UNTUK MENGHILANGKAN GAP ---
        # Atur warna background widget ini agar sama dengan background progress bar anak.
        # Spasi di layout sekarang akan terlihat seperti konektor solid.
        # Ambil warna BG dari instance sementara ModernProgressBar.
        temp_bar = ModernProgressBar()
        bg_color_hex = temp_bar.BG_COLOR.name()
        self.setStyleSheet(f"background-color: {bg_color_hex}; border-radius: 7px;")

    def set_segment_count(self, count):
        for widget in self._segments:
            self._main_layout.removeWidget(widget)
            widget.deleteLater()
        self._segments.clear()

        if count <= 0: count = 1

        for _ in range(count):
            segment_widget = ProgressSegmentWidget()
            self._main_layout.addWidget(segment_widget)
            self._segments.append(segment_widget)

    def update_progress(self, index, progress_float, color=None):
        """
        Versi yang disederhanakan: hanya menerima progress dan warna.
        """
        if 0 <= index < len(self._segments):
            segment_widget = self._segments[index]
            progress_int = int(progress_float * 100)
            
            segment_widget.setProgress(progress_int)
            if color:
                segment_widget.setColor(color)
                
class SingleProjectWorker(QObject):
    """Worker yang memproses satu proyek panorama di thread terpisah."""
    # Sinyal untuk progress bar di DisplayPanel: (title, value)
    progress_updated = Signal(str, int)
    
    # Sinyal saat selesai: (hasil_gambar, stage_selesai)
    finished = Signal(QPixmap, str) 
    
    # Sinyal jika ada error: (pesan_error)
    error = Signal(str)

    def __init__(self, project_id, target_stage, database_manager):
        super().__init__()
        self.db_manager = database_manager
        self.project_id = project_id
        self.target_stage = target_stage # "alignment", "projection", dll.

    def run(self):
        try:
            # 1. Ambil data dari DB
            images = self.db_manager.get_images_for_project(self.project_id)
            settings = self.db_manager.get_project_workflow_settings(self.project_id)

            # 2. Definisikan callback untuk menerima progress
            def progress_update_handler(progress_float, status_text):
                progress_int = int(progress_float * 100)
                self.progress_updated.emit(status_text, progress_int)

            # 3. Panggil dispatcher utama dengan target stage
            result_data = run_panorama_stitching_process(
                images,
                settings,
                progress_update_handler,
                target_stage=self.target_stage
            )

            # <<< PERUBAHAN UTAMA DI SINI >>>
            # Buat QPixmap placeholder dengan warna berbeda untuk setiap tahap
            pixmap = QPixmap(600, 450) # Ukuran yang layak untuk preview
            
            if self.target_stage == "alignment":
                # Biru muda untuk alignment
                pixmap.fill(QColor("#A8D8EA")) 
                print(f"DEBUG: Created BLUE pixmap for '{self.target_stage}'")
            elif self.target_stage == "projection":
                # Merah muda untuk projection
                pixmap.fill(QColor("#F4B6C2"))
                print(f"DEBUG: Created PINK pixmap for '{self.target_stage}'")
            elif self.target_stage == "blending":
                # Hijau muda untuk blending
                pixmap.fill(QColor("#A8E6CF"))
                print(f"DEBUG: Created GREEN pixmap for '{self.target_stage}'")
            else:
                # Warna default jika ada kesalahan
                pixmap.fill(QColor("lightgray"))

            # Dalam implementasi nyata, Anda akan mengubah 'result_data' menjadi QPixmap di sini.
            # Untuk sekarang, kita gunakan placeholder berwarna.
            
            self.finished.emit(pixmap, self.target_stage)

        except Exception as e:
            self.error.emit(str(e))

class PanoramaProcessorWorker(QObject):
    table_status_updated = Signal(int, str, str)
    project_progress_updated = Signal(int, float, QColor)
    overall_status_updated = Signal(str)
    
    finished = Signal()

    def __init__(self, projects, output_folder, database_manager):
        super().__init__()
        # ... (properti lain tetap sama) ...
        self.projects = projects
        self.output_folder = output_folder
        self.database_manager = database_manager
        self.is_running = True

    def run(self):
        for i, (project_id, project_name) in enumerate(self.projects):
            if not self.is_running:
                self.overall_status_updated.emit("Cancelled")
                break
            
            self.table_status_updated.emit(i, "Processing...", "")
            self.project_progress_updated.emit(i, 0.0, QColor("orange"))
            self.overall_status_updated.emit(f"Starting: {project_name}")

            try:
                images = self.database_manager.get_images_for_project(project_id)
                settings = self.database_manager.get_project_workflow_settings(project_id)

                # Definisikan callback untuk menerima progress dari dispatcher
                def progress_update_handler(progress_value, status_text):
                    # Teruskan progress ke UI
                    self.project_progress_updated.emit(i, progress_value, QColor("orange"))
                    self.overall_status_updated.emit(status_text)
                
                # <<< PERUBAHAN UTAMA: Panggil dispatcher yang sebenarnya >>>
                result_image = run_panorama_stitching_process(
                    images, 
                    settings, 
                    progress_update_handler
                )

                if result_image:
                    output_path = os.path.join(self.output_folder, f"{project_name.replace(' ', '_')}.jpg")
                    # Di dunia nyata, Anda akan menyimpan result_image ke output_path
                    # result_image.save(output_path)
                    
                    self.table_status_updated.emit(i, "Completed", output_path)
                    self.project_progress_updated.emit(i, 1.0, QColor("lightgreen"))
                else:
                    raise RuntimeError("Stitching process returned no result.")

            except Exception as e:
                error_msg = str(e)
                self.table_status_updated.emit(i, "Failed", error_msg)
                self.project_progress_updated.emit(i, 1.0, QColor("salmon")) # Tunjukkan gagal dengan bar penuh
                self.overall_status_updated.emit(f"Failed: {project_name}")
        
        if self.is_running:
            self.overall_status_updated.emit("All tasks completed.")
        self.finished.emit()

    def stop(self):
        self.is_running = False

    def get_last_progress_for_project(self, index):
        # Ini fungsi helper sederhana. Dalam aplikasi nyata, Anda mungkin
        # ingin cara yang lebih canggih untuk melacak progress terakhir.
        # Untuk sekarang, kita asumsikan gagal di tengah.
        return 0.5


class BatchProcessDialog(QDialog):
    def __init__(self, projects, database_manager, parent=None):
        super().__init__(parent)
        self.projects_to_process = projects
        self.database_manager = database_manager
        self.worker_thread = None
        self.worker = None

        self.setWindowTitle("Batch Panorama Processing")
        self.setMinimumSize(600, 400)
        self.setModal(True)

        self._setup_ui()
        self._populate_table()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # 1. Output Folder Selection
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Output Folder:"))
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        folder_layout.addWidget(self.output_folder_edit)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._select_output_folder)
        folder_layout.addWidget(self.browse_button)
        main_layout.addLayout(folder_layout)

        # 2. Tabel Progress
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(3)
        self.progress_table.setHorizontalHeaderLabels(["Project Name", "Status", "Details"])
        self.progress_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.progress_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.progress_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.progress_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.progress_table)

        # 3. Progress Bar Utama dengan Label Status Global
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Overall Progress:"))
        
        # Label baru untuk menampilkan status (misal: "Aligning...")
        self.current_step_label = QLabel("Idle")
        self.current_step_label.setStyleSheet("color: #888;") # Warna abu-abu agar tidak terlalu menonjol
        progress_layout.addWidget(self.current_step_label)
        progress_layout.addStretch()
        
        main_layout.addLayout(progress_layout) # Tambahkan layout horizontal ini
        
        self.progress_bar = SegmentedProgressBar()
        main_layout.addWidget(self.progress_bar)

        # 4. Tombol Kontrol
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.start_button = QPushButton("Start Processing")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self._start_processing)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)

    def _populate_table(self):
        self.progress_table.setRowCount(len(self.projects_to_process))
        for row, (proj_id, proj_name) in enumerate(self.projects_to_process):
            self.progress_table.setItem(row, 0, QTableWidgetItem(proj_name))
            self.progress_table.setItem(row, 1, QTableWidgetItem("Pending"))
            self.progress_table.setItem(row, 2, QTableWidgetItem(""))
            self.progress_bar.set_segment_count(len(self.projects_to_process))

    def _select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_edit.setText(folder)
            self.start_button.setEnabled(True)

    def _start_processing(self):
        output_folder = self.output_folder_edit.text()
        if not output_folder:
            QMessageBox.warning(self, "Warning", "Please select an output folder first.")
            return

        self.start_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.close_button.setText("Cancel")
        self.close_button.clicked.disconnect()
        self.close_button.clicked.connect(self._stop_processing)

        self.worker_thread = QThread()
        self.worker = PanoramaProcessorWorker(self.projects_to_process, self.output_folder_edit.text(), self.database_manager)
        self.worker.moveToThread(self.worker_thread)

        # --- PERUBAHAN KONEKSI SINYAL ---
        self.worker.table_status_updated.connect(self._update_table_status)
        
        # Hubungkan sinyal yang sudah diubah ke slot yang benar
        self.worker.project_progress_updated.connect(self.progress_bar.update_progress)
        self.worker.overall_status_updated.connect(self.current_step_label.setText)
        
        self.worker.finished.connect(self._on_processing_finished)

        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def _update_table_status(self, row, status, detail):
        self.progress_table.item(row, 1).setText(status)
        self.progress_table.item(row, 2).setText(detail)
        
        color = QColor("orange") # Processing
        if status == "Completed":
            color = QColor("lightgreen")
        elif status == "Failed":
            color = QColor("salmon")
        
        for col in range(self.progress_table.columnCount()):
            self.progress_table.item(row, col).setBackground(color)

        self.progress_table.item(row, 2).setText(detail)

    def _on_processing_finished(self):
        QMessageBox.information(self, "Finished", "Batch processing has completed.")
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.worker_thread.deleteLater()
        self.worker.deleteLater()
        self.worker_thread = None
        self.worker = None

        self.close_button.setText("Close")
        self.close_button.clicked.disconnect()
        self.close_button.clicked.connect(self.accept)

    def _stop_processing(self):
        if self.worker:
            self.worker.stop()
        self._on_processing_finished()
        self.accept()

    def closeEvent(self, event):
        """Pastikan thread berhenti saat dialog ditutup."""
        if self.worker_thread and self.worker_thread.isRunning():
            self._stop_processing()
        event.accept()
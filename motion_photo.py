import sys
import os
import shutil
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QListWidget, QComboBox, QPushButton, QProgressBar, 
                             QAbstractItemView, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal

# ==========================================
# WIDGET KUSTOM UNTUK DRAG AND DROP
# ==========================================
class DropListWidget(QListWidget):
    def __init__(self, title, file_extensions):
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_extensions = file_extensions
        self.setToolTip(f"Drag & Drop file {', '.join(self.file_extensions)} ke sini")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            # Cek apakah file memiliki ekstensi yang diizinkan
            if any(file_path.lower().endswith(ext) for ext in self.file_extensions):
                # Hindari duplikasi di list
                items = [self.item(x).text() for x in range(self.count())]
                if file_path not in items:
                    self.addItem(file_path)

# ==========================================
# WORKER THREAD UNTUK PROSES BACKGROUND
# ==========================================
class MotionWorker(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal()

    def __init__(self, images, videos, compression_level):
        super().__init__()
        self.images = [Path(img) for img in images]
        self.videos = {Path(vid).stem: Path(vid) for vid in videos} # Dictionary untuk pencocokan nama
        self.compression_level = compression_level

    def run(self):
        if not self.images or not self.videos:
            self.status.emit("Error: Harap masukkan foto dan video.")
            self.finished.emit()
            return

        # Buat folder output di direktori foto pertama
        output_dir = self.images[0].parent / "Motion_Output"
        output_dir.mkdir(exist_ok=True)

        total_files = len(self.images)
        processed = 0

        for img_path in self.images:
            img_stem = img_path.stem
            
            # Cari video yang namanya cocok dengan foto
            if img_stem in self.videos:
                vid_path = self.videos[img_stem]
                output_file = output_dir / f"{img_stem}_motion.jpg"
                temp_vid_path = output_dir / f"temp_{img_stem}.mp4"

                try:
                    self.status.emit(f"Memproses: {img_stem}...")
                    
                    # 1. Kompresi Video (Jika dipilih)
                    current_vid_to_embed = vid_path
                    if self.compression_level != "Original":
                        self.status.emit(f"Mengompresi video {img_stem}...")
                        self.compress_video(vid_path, temp_vid_path, self.compression_level)
                        current_vid_to_embed = temp_vid_path

                    # 2. Copy JPG Asli (Tanpa re-compress)
                    self.status.emit(f"Menggabungkan biner {img_stem}...")
                    shutil.copy2(img_path, output_file)

                    # 3. Append Video secara Biner
                    with open(output_file, 'ab') as out_f, open(current_vid_to_embed, 'rb') as in_f:
                        out_f.write(in_f.read())

                    # 4. Inject Metadata via ExifTool
                    self.status.emit(f"Menyuntikkan Metadata ke {img_stem}...")
                    video_size = os.path.getsize(current_vid_to_embed)
                    self.inject_metadata(output_file, video_size)

                    # 5. Cleanup temp video
                    if temp_vid_path.exists():
                        os.remove(temp_vid_path)

                except Exception as e:
                    self.status.emit(f"Error pada {img_stem}: {str(e)}")
            else:
                self.status.emit(f"Video untuk {img_stem} tidak ditemukan. Dilewati.")

            processed += 1
            self.progress.emit(int((processed / total_files) * 100))

        self.status.emit("Proses Selesai! Cek folder Motion_Output.")
        self.finished.emit()

    def compress_video(self, input_path, output_path, level):
        # Command dasar FFmpeg
        cmd = ["ffmpeg", "-y", "-i", str(input_path)]
        
        if level == "Medium (720p, 15fps)":
            cmd.extend(["-vf", "scale=-2:720", "-r", "15", "-c:v", "libx264", "-crf", "28", "-preset", "veryfast", "-an"])
        elif level == "High (1080p, 24fps)":
            cmd.extend(["-vf", "scale=-2:1080", "-r", "24", "-c:v", "libx264", "-crf", "24", "-preset", "fast", "-an"])
            
        cmd.append(str(output_path))
        
        # Eksekusi FFmpeg tanpa memunculkan window CMD
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

    def inject_metadata(self, file_path, video_size):
        cmd = [
            "exiftool",
            "-overwrite_original",
            "-XMP-GCamera:MotionPhoto=1",
            "-XMP-GCamera:MotionPhotoVersion=1",
            "-XMP-GCamera:MotionPhotoPresentationTimestampUs=0",
            f"-Container:DirectoryItemLength={video_size}",
            str(file_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)


# ==========================================
# MAIN GUI WINDOW
# ==========================================
class MotionEmbedderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pixel Refine - Motion Photo Embedder")
        self.resize(600, 700)
        
        layout = QVBoxLayout()

        # 1. Drop Zone Foto
        layout.addWidget(QLabel("<b>1. Drop Foto Editan (.jpg, .jpeg)</b><br><i>Pastikan nama file cocok dengan video, misal: edit_01.jpg</i>"))
        self.list_images = DropListWidget("Images", [".jpg", ".jpeg"])
        layout.addWidget(self.list_images)

        # 2. Drop Zone Video
        layout.addWidget(QLabel("<b>2. Drop Video Burst (.mp4)</b><br><i>Misal: edit_01.mp4</i>"))
        self.list_videos = DropListWidget("Videos", [".mp4"])
        layout.addWidget(self.list_videos)

        # 3. Opsi Kompresi
        layout.addWidget(QLabel("<b>3. Kualitas Embed Video</b>"))
        self.combo_compression = QComboBox()
        self.combo_compression.addItems([
            "Medium (720p, 15fps) - Direkomendasikan",
            "High (1080p, 24fps)",
            "Original (No Compression - Ukuran File Besar)"
        ])
        layout.addWidget(self.combo_compression)

        # 4. Progress & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("Status: Menunggu file...")
        layout.addWidget(self.lbl_status)

        # 5. Tombol Eksekusi
        self.btn_process = QPushButton("Embed Motion!")
        self.btn_process.setMinimumHeight(40)
        self.btn_process.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.btn_process.clicked.connect(self.start_processing)
        layout.addWidget(self.btn_process)

        # Tombol Clear (Opsional)
        self.btn_clear = QPushButton("Clear Lists")
        self.btn_clear.clicked.connect(self.clear_lists)
        layout.addWidget(self.btn_clear)

        self.setLayout(layout)

    def clear_lists(self):
        self.list_images.clear()
        self.list_videos.clear()
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Status: Menunggu file...")

    def start_processing(self):
        images = [self.list_images.item(i).text() for i in range(self.list_images.count())]
        videos = [self.list_videos.item(i).text() for i in range(self.list_videos.count())]

        if not images or not videos:
            QMessageBox.warning(self, "Peringatan", "Harap masukkan setidaknya satu foto dan satu video yang cocok.")
            return

        # Disable UI saat proses berjalan
        self.btn_process.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.combo_compression.setEnabled(False)

        comp_level = self.combo_compression.currentText().split(" - ")[0]

        # Mulai Worker Thread
        self.worker = MotionWorker(images, videos, comp_level)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.process_finished)
        self.worker.start()

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def update_status(self, msg):
        self.lbl_status.setText(f"Status: {msg}")

    def process_finished(self):
        self.btn_process.setEnabled(True)
        self.btn_clear.setEnabled(True)
        self.combo_compression.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set style yang lebih modern (native Windows look)
    app.setStyle("Fusion") 
    
    window = MotionEmbedderApp()
    window.show()
    sys.exit(app.exec())
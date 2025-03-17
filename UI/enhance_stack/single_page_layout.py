from PyQt6.QtWidgets import (
    QHBoxLayout, QMessageBox, QGraphicsView,
    QGraphicsScene, QVBoxLayout, QWidget, 
    QProgressBar, QPushButton, QFileDialog,
    QGraphicsPixmapItem, QLabel
)
import cv2
import os

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from UI.enhance_stack.components.single_page_layout import setup_main_layout, setup_preview_panel, setup_progress_section, setup_signals
from UI.enhance_stack.logic.multi_threading import RawImageProcessingThread
from UI.resources.stylesheet import stylesheet

from UI.enhance_stack.logic.database_manager import DatabaseManager
from .components.left_panel import LeftPanel
from .components.right_panel import RightPanel
from UI.settings.General.Language import language_config

class SinglePageLayout(QWidget):
    process_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()
        self.original_pixmap = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)

# ==================== LAYOUT APP ==================== 
        setup_main_layout(self)
        setup_progress_section(self)
        setup_preview_panel(self)
        setup_signals(self)


    def handle_image_ready(self, pixmap):
        """Tangani hasil gambar yang diproses."""
        self.original_pixmap = pixmap
        self.fit_image_to_panel()


    def handle_image_error(self, error_message):
        """Tangani error selama pemrosesan."""
        self.preview_scene.clear()
        label = QLabel(error_message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_scene.addWidget(label)


    def update_preview_panel(self, selected_paths):
        
        self.preview_scene.clear()  # Hapus semua elemen dari scene sebelumnya

        if hasattr(self, "raw_thread") and self.raw_thread.isRunning():
            # Hentikan thread jika masih berjalan
            self.raw_thread.stop()
            self.raw_thread.quit
            return

        if selected_paths:
            # Tampilkan pesan loading sementara gambar diproses
            label = QLabel(language_config.UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Tambahkan label ke scene dengan QGraphicsProxyWidget
            proxy = self.preview_scene.addWidget(label)
            self.image_status_info(proxy)

            # Tambahkan jeda waktu 2 detik sebelum memulai proses gambar
            self.preview_timer = QTimer()
            self.preview_timer.setSingleShot(True)  # Timer berjalan sekali
            self.preview_timer.timeout.connect(
                lambda: self.start_image_processing(selected_paths)
            )
            self.preview_timer.start(1000)
        else:
            self.original_pixmap = None

            # Tampilkan pesan bahwa tidak ada gambar yang dipilih
            label = QLabel(language_config.UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Tambahkan label ke scene dengan QGraphicsProxyWidget
            proxy = self.preview_scene.addWidget(label)
            self.image_status_info(proxy)  # Pusatkan widget di scene


    def start_image_processing(self, selected_paths):
        """Mulai proses pemrosesan gambar RAW setelah jeda."""
        # Mulai thread pemrosesan gambar RAW
        self.raw_thread = RawImageProcessingThread(selected_paths, batch_size=1, delay_ms=0)
        self.raw_thread.result_signal.connect(self.handle_image_ready)
        self.raw_thread.error_signal.connect(self.handle_image_error)
        self.raw_thread.start()


    def image_status_info(self, proxy):
        """
        Center the widget (QGraphicsProxyWidget) in the center of the scene.
        """
        scene_width = self.preview_scene.sceneRect().width()
        scene_height = self.preview_scene.sceneRect().height()

        widget_width = proxy.size().width()
        widget_height = proxy.size().height()

        # Hitung posisi tengah
        center_x = (scene_width - widget_width) / 2
        center_y = (scene_height - widget_height) / 2

        # Set posisi widget
        proxy.setPos(center_x, center_y)


    def fit_image_to_panel(self):
        """Scales the image to fit the preview panel."""
        if self.original_pixmap:
            view_size = self.preview_view.size()
            max_width = view_size.width()
            max_height = view_size.height()

            # Scale image to fit the view size
            scaled_pixmap = self.original_pixmap.scaled(
                max_width,
                max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.display_image(scaled_pixmap)

    def display_image(self, pixmap):
        """Displays the given pixmap in the graphics view."""
        self.preview_scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.preview_scene.addItem(self.pixmap_item)
        self.preview_scene.setSceneRect(self.pixmap_item.boundingRect())

    def pause_preview_update(self):
        """Temporarily disable preview panel updates."""
        self.update_preview_enabled = False

    def resume_preview_update(self):
        """Re-enable preview panel updates."""
        self.update_preview_enabled = True

    def resizeEvent(self, event):
        """Handles window resizing by adjusting the image size to fit the preview panel."""
        super().resizeEvent(event)
        self.fit_image_to_panel()
            
    def fit_image_to_panel(self):
        """Scales the image to fit the preview panel."""
        if self.original_pixmap:
            view_size = self.preview_view.size()
            max_width = view_size.width()
            max_height = view_size.height()

            # Scale image to fit the view size
            scaled_pixmap = self.original_pixmap.scaled(
                max_width,
                max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.display_image(scaled_pixmap)


    def handle_import_button(self):
        """Function to manage images import"""
        # Open file dialog and get image paths with filter
        file_dialog_filter = language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
        image_paths, _ = QFileDialog.getOpenFileNames(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, "", file_dialog_filter)
        
        if not image_paths:
            return

        # Extract file extensions from the filter string
        filter_extensions = [ext.strip().lower() for ext in file_dialog_filter.split("*") if ext.strip().startswith(".")]

        # Step 1: Validate duplicate files
        existing_paths = self.database_manager.get_all_image_paths()
        duplicates = [path for path in image_paths if path in existing_paths]
        unique_files = [path for path in image_paths if path not in duplicates]

        if duplicates:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
            QMessageBox.warning(self,
                                language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE,
                                message)

        # Step 2: Group files by format based on selected file extensions
        format_groups = {ext: [] for ext in filter_extensions}

        for path in unique_files:
            for ext in filter_extensions:
                if path.lower().endswith(ext):
                    format_groups[ext].append(path)
                    break

        # Step 3: Determine dominant format
        dominant_format = max(format_groups, key=lambda ext: len(format_groups[ext]))

        # Step 4: Select files based on priority or dominant format
        selected_files = []
        if len(format_groups[dominant_format]) > len(unique_files) / 2:
            # If dominant format is more than half, prioritize it
            selected_files = format_groups[dominant_format]
        else:
            # Otherwise, follow the original priority order based on filter
            for ext in filter_extensions:
                if format_groups[ext]:
                    selected_files = format_groups[ext]
                    break

        # Step 5: Proceed with selected files
        if selected_files:
            # Inform user about the selected format and number of files to import
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT.format(
            
            count=len(selected_files),
            format=dominant_format)
            
            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_SELECTED, message)
            
            # Proceed with importing the selected files
            self.multi_thread_import_images = ImageImportThreading(
                self.database_manager,
                selected_files,
                batch_size=15,
                delay_ms=25
            )

            # Connect signals to update progress and completion
            self.multi_thread_import_images.progress_signal.connect(self.update_progress_bar)
            self.multi_thread_import_images.completion_signal.connect(self.on_import_complete)

            # Start the thread
            self.multi_thread_import_images.start()
        else:
            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED)

    def handle_delete_button(self):
        """Function to delete images"""
        selected_paths = self.right_panel.get_select_image_list()
        if not selected_paths:
            title, message = language_config.HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED
            QMessageBox.information(self, title, message)
            return

        reply = QMessageBox.question(
            self,
            "Delete Images",
            language_config.HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE.format(count=len(selected_paths)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.database_manager.delete_images(selected_paths)
            self.right_panel.remove_selected_images()


    def process_algorithm(self):
        """
        Fungsi untuk memproses algoritma berdasarkan pilihan dropdown.
        """
        try:
            alignment_choice = self.left_panel.alignment_dropdown.currentText()
            denoising_choice = self.left_panel.denoising_dropdown.currentText()  # Ambil pilihan denoising
            super_resolution_choice = self.left_panel.super_resolution_dropdown.currentText()  # Ambil pilihan super resolution

            # Jika tidak ada algoritma yang dipilih
            if alignment_choice == "None" and denoising_choice == "None" and super_resolution_choice == "None":
                QMessageBox.warning(self, "Caution", language_config.PROCESS_ALGORITHM_PROCESS_SKIPPED)
                return

            # Proses untuk Alignment
            if alignment_choice == "ORB":
                running_orb(self)
            elif alignment_choice == "Farneback Optical Flow":
                running_farneback_optical_flow(self)
            elif alignment_choice == "AKAZE":
                running_akaze(self)

            elif alignment_choice == "None":
                if denoising_choice != "None":  # Jika hanya denoising yang dipilih
                    reply = QMessageBox.question(self, "Confirm", 
                                                language_config.NO_ALIGNMENT_PROCESS,
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                                QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return  # Jika pengguna memilih 'No', berhenti proses
            else:
                QMessageBox.warning(self, "Warning", "Pilihan algoritma alignment tidak dikenali.")
                
            super_resolution_executed = False
            # Proses untuk Super Resolution
            if super_resolution_choice == "Interpolation":
               running_interpolation(self) 
            #    super_resolution_executed = True
            elif super_resolution_choice == "none":
                return 
            # else:
            #     QMessageBox.information(self, "Info", language_config.MODULE_NOT_IMPLEMENT)
        
            
            if super_resolution_executed:
                latest_image_path = get_last_image("database/stack")
                if latest_image_path:
                    dialog = ImageViewer(latest_image_path, self)  # Menampilkan gambar di ImageViewer
                    dialog.exec()  # Menampilkan dialog secara modal
                else:
                    QMessageBox.warning(self, "Caution", language_config.NOT_IMAGE_PREVIEW)


            # Proses untuk Denoising
            denoising_executed = False  # Flag untuk melacak apakah denoising dilakukan
            if denoising_choice == "Average":
                running_average(self)
                denoising_executed = True
            elif denoising_choice == "Median":
                running_median(self)
                denoising_executed = True
            elif denoising_choice == "Weighted Average":
                running_weighted_average(self)
                denoising_executed = True
            elif denoising_choice == "Similarity":
               running_similarity(self)
               denoising_executed = True
            elif denoising_choice == "none":
                return 
           
            # Tampilkan hasil hanya jika denoising berhasil dijalankan
            if denoising_executed:
                latest_image_path = get_last_image("database/stack")
                if latest_image_path:
                    dialog = ImageViewer(latest_image_path, self)  # Menampilkan gambar di ImageViewer
                    dialog.exec()  # Menampilkan dialog secara modal
                else:
                    QMessageBox.warning(self, "Warning", language_config.NOT_IMAGE_PREVIEW)
        except Exception as e:
                    # QMessageBox.critical(self, "Error", f"Terjadi kesalahan: {e}")
                    QMessageBox.critical(self, "Error", language_config.RUN_ERROR_STATUS.format(error = e))


    def save_image(self):
            """Menyimpan gambar hasil proses ke lokasi yang dipilih oleh pengguna."""
            folder_path = "database/stack"
            if not os.path.exists(folder_path):
                QMessageBox.warning(self, "Error", "The folder 'database/stack' does not exist.")
                return

            # Mendapatkan file gambar terbaru di dalam folder
            image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if not image_files:
                QMessageBox.warning(self, "No Images", "There are no processed images to save.")
                return

            image_files.sort(key=os.path.getmtime, reverse=True)
            latest_image_path = image_files[0]

            # Dialog penyimpanan file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image As",
                os.path.basename(latest_image_path),
                "JPEG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;PNG (*.png)"
            )

            if not file_path:
                return  # User membatalkan penyimpanan

            file_extension = os.path.splitext(file_path)[-1].lower()
            if file_extension not in [".jpg", ".jpeg", ".tif", ".tiff", ".png"]:
                QMessageBox.warning(self, "Invalid Format", "Unsupported file format.")
                return

            try:
                # Load gambar dengan OpenCV
                image = cv2.imread(latest_image_path, cv2.IMREAD_UNCHANGED)
                if image is None:
                    QMessageBox.critical(self, "Error", "Failed to load the image.")
                    return

                # Simpan gambar berdasarkan format file
                if file_extension in [".jpg", ".jpeg"]:
                    cv2.imwrite(file_path, image, [cv2.IMWRITE_JPEG_QUALITY, 100])
                elif file_extension in [".tif", ".tiff"]:
                    cv2.imwrite(file_path, image)
                elif file_extension == ".png":
                    cv2.imwrite(file_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 5])

                QMessageBox.information(self, "Success", f"Image saved successfully as {file_path}.")
                os.remove(latest_image_path)  # Hapus gambar asli setelah disimpan
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {e}")

    def update_progress_bar(self, value, images_left):
        """Memperbarui progress bar dan menampilkan jumlah gambar yang tersisa."""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(
            language_config.UPDATE_PROGRESS_BAR_STATUS.format(value=value, images_left=images_left)
        )

    def on_import_complete(self, successful_images):
        """Called when the import process is complete."""
        self.right_panel.load_image_paths()
        QMessageBox.information(
            self,
            language_config.ON_IMPORT_COMPLETE_STATUS,
            language_config.ON_IMPORT_COMPLETE_MESSAGES.format(successful_images=successful_images)
        )
        self.progress_section.progress_bar.setValue(0)
        self.progress_section.progress_bar.setFormat("0%")

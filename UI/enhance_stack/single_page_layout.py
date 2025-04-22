import subprocess
from PyQt6.QtWidgets import (
    QMessageBox, QVBoxLayout, QWidget,
    QFileDialog,
)
import cv2
import os
from PIL import Image
from PyQt6.QtCore import pyqtSignal
from UI.enhance_stack.algorithm.alignment.AKAZE import running_akaze
from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import running_farneback_optical_flow
from UI.enhance_stack.algorithm.alignment.ORB import running_orb
from UI.enhance_stack.algorithm.denoising.Average import running_average
from UI.enhance_stack.algorithm.denoising.Median import running_median
from UI.enhance_stack.algorithm.denoising.Motion_Flow import running_motion_flow
from UI.enhance_stack.algorithm.denoising.Similarity import running_similarity
from UI.enhance_stack.algorithm.denoising.Weighted_average import running_weighted_average
from UI.enhance_stack.algorithm.super_resolution.Interpolation import running_interpolation
from UI.enhance_stack.components.single_page_layout.image_preview_handler import fit_image_to_panel
from UI.enhance_stack.components.single_page_layout.page_layout import (setup_main_layout, 
                                                                        setup_preview_panel, 
                                                                        setup_progress_section, 
                                                                        setup_signals)

from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.enhance_stack.logic.multi_threading import ImageImportThreading
from UI.enhance_stack.logic.workflow_process import ImageViewer, get_last_image
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

# ==================== LAYOUT APP ==================== #
        setup_main_layout(self)
        setup_progress_section(self)
        setup_preview_panel(self)
        setup_signals(self)
# ==================== LAYOUT APP ==================== #
        
    def pause_preview_update(self):
        """Temporarily disable preview panel updates."""
        self.update_preview_enabled = False

    def resume_preview_update(self):
        """Re-enable preview panel updates."""
        self.update_preview_enabled = True

    def resizeEvent(self, event):
        """Handles window resizing by adjusting the image size to fit the preview panel."""
        super().resizeEvent(event)
        fit_image_to_panel(self)
        
    def convert_tiff_to_uncompressed(self, input_path, output_folder):
        """Konversi TIFF terkompresi ke TIFF tanpa kompresi"""
        try:
            with Image.open(input_path) as img:
                output_path = os.path.join(output_folder, os.path.basename(input_path))
                img.save(output_path, format="TIFF", compression="none")  # Simpan tanpa kompresi
                return output_path
        except Exception as e:
            print(f"Error converting TIFF: {e}")
            return None

    def handle_import_button(self):
        """Function to manage images import, including TIFF decompression"""
        # Open file dialog and get image paths with filter
        file_dialog_filter = language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
        image_paths, _ = QFileDialog.getOpenFileNames(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, "", file_dialog_filter)

        if not image_paths:
            return

        # Mapping ekstensi alternatif ke dalam tiga kategori utama
        SUPPORTED_FORMATS = {
            "jpg": [".jpg", ".jpeg", ".jiff", ".jli"],
            "tiff": [".tif", ".tiff"],
            "png": [".png"],
        }

        # Step 1: Validate duplicate files
        existing_paths = self.database_manager.get_all_image_paths()
        duplicates = [path for path in image_paths if path in existing_paths]
        unique_files = [path for path in image_paths if path not in duplicates]

        if duplicates:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
            QMessageBox.warning(self,
                                language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE,
                                message)

        # Step 2: Group files berdasarkan format utama yang didukung
        format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}

        for path in unique_files:
            lower_path = path.lower()
            for format_key, extensions in SUPPORTED_FORMATS.items():
                if any(lower_path.endswith(ext) for ext in extensions):
                    format_groups[format_key].append(path)
                    break

        # Jika tidak ada file valid sesuai ketiga kategori, tampilkan pesan garis besar
        if not any(format_groups.values()):
            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED)
            return

        # Step 3: Konversi TIFF dengan kompresi ke uncompressed
        output_folder = "database/align/uncompressed_tiff"  # Folder penyimpanan hasil konversi
        os.makedirs(output_folder, exist_ok=True)

        uncompressed_tiff_files = []
        if "tiff" in format_groups:
            for tiff_path in format_groups["tiff"]:
                try:
                    with Image.open(tiff_path) as img:
                        compression = img.info.get("compression", "None")  # Cek tipe kompresi
                        if compression.lower() in ["tiff_lzw", "tiff_zip", "packbits"]:  # Jika dikompresi
                            new_tiff_path = self.convert_tiff_to_uncompressed(tiff_path, output_folder)
                            if new_tiff_path:
                                uncompressed_tiff_files.append(new_tiff_path)
                        else:
                            uncompressed_tiff_files.append(tiff_path)  # Jika sudah uncompressed, langsung gunakan
                except Exception as e:
                    print(f"Skipping invalid TIFF: {tiff_path}, Error: {e}")

            # Update daftar TIFF dengan versi uncompressed
            format_groups["tiff"] = uncompressed_tiff_files

        # Step 4: Tentukan format dominan (format dengan jumlah file terbanyak)
        dominant_format = max(format_groups, key=lambda key: len(format_groups[key]))

        # Step 5: Seleksi file berdasarkan prioritas atau dominan format
        selected_files = []
        total_unique = sum(len(v) for v in format_groups.values())
        if len(format_groups[dominant_format]) > total_unique / 2:
            selected_files = format_groups[dominant_format]
        else:
            for key in SUPPORTED_FORMATS.keys():
                if format_groups[key]:
                    selected_files = format_groups[key]
                    break

        # Step 6: Proses file terpilih
        if selected_files:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT.format(
                count=len(selected_files),
                format=dominant_format)
            
            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_SELECTED, message)
            
            # Proses import file
            self.multi_thread_import_images = ImageImportThreading(
                self.database_manager,
                selected_files,
                batch_size=15,
                delay_ms=25
            )

            # Connect signals untuk progress dan completion
            self.multi_thread_import_images.progress_signal.connect(self.update_progress_bar)
            self.multi_thread_import_images.completion_signal.connect(self.on_import_complete)

            # Mulai thread import
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
            self.database_manager.single_process_delete_path_images(selected_paths)
            self.right_panel.remove_selected_images()

    def single_process_algorithm(self):
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
                running_orb(self, single_process=True)
            elif alignment_choice == "Farneback Optical Flow":
                running_farneback_optical_flow(self, single_process=True)
            elif alignment_choice == "AKAZE":
                running_akaze(self, single_process=True)

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
               running_interpolation(self, single_process=True) 
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
                running_average(self, single_process=True)
                denoising_executed = True
            elif denoising_choice == "Median":
                running_median(self, single_process=True)
                denoising_executed = True
            elif denoising_choice == "Weighted Average":
                running_weighted_average(self, single_process=True)
                denoising_executed = True
            elif denoising_choice == "Similarity":
                running_similarity(self, single_process=True)
                denoising_executed = True
            elif denoising_choice == "Motion Flow":
               running_motion_flow(self, single_process=True)
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
        """Menyimpan gambar hasil proses ke lokasi yang dipilih oleh pengguna dengan metadata asli."""
        folder_path = "database/stack"

        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "Error", language_config.UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH)
            return

        # Dapatkan daftar gambar yang tersedia di folder
        image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not image_files:
            QMessageBox.warning(self, "No Images", "There are no processed images to save.")
            return

        # Ambil gambar terbaru berdasarkan waktu modifikasi
        image_files.sort(key=os.path.getmtime, reverse=True)
        latest_image_path = image_files[0]

        # Dialog untuk menyimpan file
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
            if file_extension in [".tif", ".tiff"]:
                image = cv2.imread(latest_image_path, cv2.IMREAD_UNCHANGED)  # TIFF disimpan tanpa perubahan
            else:
                image = cv2.imread(latest_image_path)

            if image is None:
                QMessageBox.critical(self, "Error", language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
                return

            # Simpan gambar berdasarkan format file
            if file_extension in [".jpg", ".jpeg"]:
                cv2.imwrite(file_path, image, [cv2.IMWRITE_JPEG_QUALITY, 100])
            elif file_extension == ".png":
                cv2.imwrite(file_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 5])
            elif file_extension in [".tif", ".tiff"]:
                cv2.imwrite(file_path, image)  # TIFF disimpan langsung tanpa kompresi

            # Gunakan ExifTool untuk menyalin metadata dari gambar asli ke gambar yang baru disimpan
            if os.path.exists(latest_image_path):
                try:
                    subprocess.run(
                        ["exiftool", "-overwrite_original", "-TagsFromFile", latest_image_path, file_path],
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Error restoring metadata to {file_path}: {e}")

            # Hapus gambar asli setelah disimpan
            os.remove(latest_image_path)

            # Beri notifikasi sukses
            QMessageBox.information(self, "Success", language_config.UI_SUCCES_TO_SAVE_IMAGE_BATCH.format(file_path))

        except Exception as e:
            QMessageBox.critical(self, "Error", language_config.UI_FAILED_TO_SAVE_IMAGE_BATCH.format(e))

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
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0%")

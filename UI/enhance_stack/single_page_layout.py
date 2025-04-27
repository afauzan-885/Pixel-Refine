import subprocess
from PyQt6.QtWidgets import (
    QMessageBox, QVBoxLayout, QWidget,
    QFileDialog,
)
import cv2
import os
from PIL import Image, UnidentifiedImageError
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from UI.enhance_stack.algorithm.alignment.AKAZE import running_akaze
from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import running_farneback_optical_flow
from UI.enhance_stack.algorithm.alignment.ORB import running_orb
from UI.enhance_stack.algorithm.denoising.Average import running_average
from UI.enhance_stack.algorithm.denoising.Median import running_median
from UI.enhance_stack.algorithm.denoising.Similarity import running_similarity
from UI.enhance_stack.algorithm.denoising.Similarity_V2 import running_similarity_v2
from UI.enhance_stack.algorithm.super_resolution.Interpolation import running_interpolation
from UI.enhance_stack.components.single_page_layout.page_layout import (setup_main_layout, 
                                                                        setup_preview_panel, 
                                                                        setup_progress_section, 
                                                                        setup_signals)

from UI.enhance_stack.logic.ImagePreviewHandler import ImagePreviewHandler
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.enhance_stack.logic.multi_threading import ImageImportThreading
from UI.enhance_stack.logic.workflow_process import ImageViewer, get_last_image
from UI.settings.General.Language import language_config
from config import SUPPORTED_FORMATS

class SinglePageLayout(QWidget):
    process_clicked = pyqtSignal()

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        self.preview_handler: ImagePreviewHandler | None = None # Tambahkan atribut untuk handler
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)

# ==================== LAYOUT APP ==================== #
        # Penting: Urutan setup mungkin berpengaruh pada ketersediaan objek
        setup_main_layout(self, self.database_manager) # Membuat left/right panel
        setup_progress_section(self)                   # Membuat progress bar/tombol
        setup_preview_panel(self)                      # Membuat scene/view di left_panel

        # --- Inisialisasi Handler SETELAH scene/view dibuat oleh setup_preview_panel ---
        if hasattr(self, 'preview_scene') and hasattr(self, 'preview_view'):
            # Pastikan preview_view adalah tipe Zoomable jika diperlukan
            if isinstance(getattr(self, 'preview_view', None), QWidget):
                 self.preview_handler = ImagePreviewHandler(self.preview_scene, self.preview_view, self)
            else:
                 print("Error: preview_view is not a valid QWidget for ImagePreviewHandler.")
                 # Atau tampilkan QMessageBox kritis
        else:
            print("Error: preview_scene or preview_view not found for ImagePreviewHandler.")
            QMessageBox.critical(self, "Layout Error", "Preview panel components could not be initialized.")
        # ---------------------------------------------------------------------------

        setup_signals(self) # Menghubungkan sinyal tombol proses/simpan

        # --- Hubungkan Sinyal Preview di SINI ---
        if self.preview_handler and hasattr(self, 'right_panel'):
            try:
                # Hubungkan sinyal dari right_panel ke slot handler
                self.right_panel.previewImageRequested.connect(self.preview_handler.update_preview)
                if hasattr(self.right_panel, 'imagesDropped'):
                     self.right_panel.imagesDropped.connect(self.handle_dropped_images)
                     
            except AttributeError as e:
                 print(f"Error connecting signals: {e}")
                 QMessageBox.warning(self, "Signal Error", f"Could not connect preview signals: {e}")
            except TypeError as e:
                 print(f"Error connecting signals (TypeError): {e}") # Misal jika slot tidak benar
                 QMessageBox.warning(self, "Signal Error", f"Could not connect preview signals due to type mismatch: {e}")
        elif not self.preview_handler:
            print("Warning: preview_handler not initialized, cannot connect preview signals.")
        else: # preview_handler ada, tapi right_panel tidak
            print("Warning: right_panel not found, cannot connect preview signals.")
        # ==================== LAYOUT APP ==================== #

        # self.update_preview_enabled = True # Defaultnya aktif
        
    def resizeEvent(self, event):
        """Handles window resizing by calling the handler's resize method."""
        super().resizeEvent(event)
        if self.preview_handler:
            self.preview_handler.handle_resize()
        
    def convert_tiff_to_uncompressed(self, input_path, output_folder):
        try:
            with Image.open(input_path) as img:
                output_path = os.path.join(output_folder, os.path.basename(input_path))
                img.save(output_path, format="TIFF", compression="none")  # Simpan tanpa kompresi
                return output_path
        except Exception as e:
            print(f"Error converting TIFF: {e}")
            return None

    def handle_import_button(self):
        """Membuka dialog file dan memulai proses impor."""
        file_dialog_filter = language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
        image_paths, _ = QFileDialog.getOpenFileNames(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, "", file_dialog_filter)

        if image_paths:
            self._process_and_start_import(image_paths)

    @pyqtSlot(list)
    def handle_dropped_images(self, image_paths: list):
        """Menangani file gambar yang di-drop dan memulai proses impor."""
        if image_paths:
            self._process_and_start_import(image_paths)

    def _process_and_start_import(self, image_paths: list):
        """
        Memvalidasi, memproses (konversi TIFF), menyeleksi, dan
        memulai impor background untuk daftar path gambar yang diberikan.
        """
        if not image_paths: return

        # 1. Validasi Duplikat di DB
        try:
            existing_single_paths = self.database_manager.get_single_process_image_paths()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", "Could not retrieve existing image paths.")
            return

        duplicates = [path for path in image_paths if path in existing_single_paths]
        unique_files = [path for path in image_paths if path not in duplicates]

        if duplicates:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
            QMessageBox.warning(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE, message)

        if not unique_files:
             return

        # 2. Buat Group Berdasarkan Format
        format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}
        valid_files_grouped = False
        for path in unique_files:
            lower_path = path.lower()
            for format_key, extensions in SUPPORTED_FORMATS.items():
                if any(lower_path.endswith(ext) for ext in extensions):
                    format_groups[format_key].append(path)
                    valid_files_grouped = True
                    break 
                
        if not valid_files_grouped:
            # Jika tidak ada file dengan format yang didukung sama sekali
            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED)
            return

        # 3. Konversi TIFF (jika ada)
        output_folder = "database/align/uncompressed_tiff" # Pertimbangkan jadikan konstanta
        try:
            os.makedirs(output_folder, exist_ok=True)
        except OSError as e:
            print(f"Error creating TIFF output folder: {e}")
            QMessageBox.critical(self, "Folder Error", f"Could not create folder for TIFF conversion:\n{e}")
            return

        # Kumpulkan semua path yang siap diimpor
        files_ready_for_import = []
        for fmt_key in SUPPORTED_FORMATS:
            if fmt_key != "tiff":
                 files_ready_for_import.extend(format_groups.get(fmt_key, []))

        # Proses TIFF
        tiff_files = format_groups.get("tiff", [])
        if tiff_files:
             print(f"Processing {len(tiff_files)} TIFF files...")
             tiff_errors = []
             for tiff_path in tiff_files:
                  processed_tiff_path = tiff_path # Default pakai asli
                  needs_conversion = False
                  try:
                      with Image.open(tiff_path) as img:
                           compression = img.info.get("compression", "none").lower()
                           # Cek kompresi yang perlu dikonversi
                           if compression in ["tiff_lzw", "tiff_zip", "packbits", "jpeg"]:
                                needs_conversion = True
                  except (FileNotFoundError, UnidentifiedImageError, Exception) as e:
                       print(f"  TIFF Error reading info/opening: {os.path.basename(tiff_path)}, Error: {e}")
                       tiff_errors.append(f"{os.path.basename(tiff_path)} (Read Error)")
                       continue 
                   
                  if needs_conversion:
                       print(f"  Converting compressed TIFF: {os.path.basename(tiff_path)}")
                       converted = self.convert_tiff_to_uncompressed(tiff_path, output_folder)
                       if converted:
                            processed_tiff_path = converted
                       else:
                            print(f"  Skipping TIFF due to conversion error: {os.path.basename(tiff_path)}")
                            tiff_errors.append(f"{os.path.basename(tiff_path)} (Conversion Failed)")
                            continue # Skip jika konversi gagal

                  files_ready_for_import.append(processed_tiff_path) # Tambahkan path TIFF (asli atau konversi)

             if tiff_errors:
                  QMessageBox.warning(self, "TIFF Processing Issues", f"Could not process some TIFF files:\n{', '.join(tiff_errors)}")


        # 4. & 5. Seleksi File Akhir (Sekarang berisi semua file valid)
        selected_files = files_ready_for_import
        if not selected_files:
             QMessageBox.information(self, "Import Failed", "No valid files could be prepared for import after processing.")
             return

        # 6. Proses Impor di Thread
        # Pesan 'dominant format' mungkin tidak relevan lagi, gunakan pesan generik
        # message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_SELECTED.format(count=len(selected_files)) # Gunakan string generik
        # QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_SELECTED, message)
        try:
             self.multi_thread_import_images = ImageImportThreading(
                 database_manager=self.database_manager,
                 image_paths=selected_files,
                 batch_size=15, 
                 delay_ms=25    
             )

             # --- Koneksi Sinyal Thread ---
             # Hubungkan ke slot yang sudah ada di kelas ini
             if hasattr(self, 'update_progress_bar') and callable(self.update_progress_bar):
                  self.multi_thread_import_images.progress_signal.connect(self.update_progress_bar)
             else: print("Warning: Slot 'update_progress_bar' not found.")

             if hasattr(self, 'on_import_complete') and callable(self.on_import_complete):
                  self.multi_thread_import_images.completion_signal.connect(self.on_import_complete)
             else: print("Warning: Slot 'on_import_complete' not found.")

             # Tambahkan koneksi untuk error jika ada
             if hasattr(self.multi_thread_import_images, 'error_signal') and hasattr(self, 'on_import_error'):
                  self.multi_thread_import_images.error_signal.connect(self.on_import_error)

             # Mulai thread
             self.multi_thread_import_images.start()
        except Exception as e:
            QMessageBox.critical(self, "Threading Error", f"Could not start the import process:\n{e}")
            

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
            language_config.HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE.format(len(selected_paths)),
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
            elif denoising_choice == "Similarity":
                running_similarity(self, single_process=True)
                denoising_executed = True
            elif denoising_choice == "Similarity V2":
               running_similarity_v2(self, single_process=True)
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
            language_config.UPDATE_PROGRESS_BAR_STATUS.format(value,images_left)
        )

    def on_import_complete(self, successful_images):
        """Called when the import process is complete."""
        self.right_panel.load_image_paths()
        QMessageBox.information(
            self,
            language_config.ON_IMPORT_COMPLETE_STATUS,
            language_config.ON_IMPORT_COMPLETE_MESSAGES.format(successful_images)
        )
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0%")

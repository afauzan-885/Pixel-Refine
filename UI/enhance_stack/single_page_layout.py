import shutil
import subprocess
import traceback
from PySide6.QtWidgets import (
    QMessageBox, QVBoxLayout, QWidget,
    QFileDialog,
)
import cv2
import os
from PIL import Image, UnidentifiedImageError
from PySide6.QtCore import Signal, Slot
import tifffile
from UI.enhance_stack.algorithm.alignment.AKAZE import running_akaze
from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import running_farneback_optical_flow
from UI.enhance_stack.algorithm.alignment.Light_Glue import running_light_glue
from UI.enhance_stack.algorithm.alignment.ORB import running_orb
from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import save_special_jpg_and_png
from UI.enhance_stack.algorithm.denoising.Average import running_average
from UI.enhance_stack.algorithm.denoising.Median import running_median
from UI.enhance_stack.algorithm.denoising.Similarity import running_similarity
from UI.enhance_stack.algorithm.super_resolution.Interpolation import running_interpolation
from UI.enhance_stack.components.batch_page_layout.image_batch_management import convert_tiff_to_uncompressed
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
    process_clicked = Signal()

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        self.preview_handler: ImagePreviewHandler | None = None # Tambahkan atribut untuk handler
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)

# ==================== LAYOUT APP ==================== #
        setup_main_layout(self, self.database_manager) 
        setup_progress_section(self)                   
        setup_preview_panel(self)                      
        if hasattr(self, 'preview_scene') and hasattr(self, 'preview_view'):
            if isinstance(getattr(self, 'preview_view', None), QWidget):
                 self.preview_handler = ImagePreviewHandler(self.preview_scene, self.preview_view, self)
            else:
                 print("Error: preview_view is not a valid QWidget for ImagePreviewHandler.")
        else:
            print("Error: preview_scene or preview_view not found for ImagePreviewHandler.")
            QMessageBox.critical(self, "Layout Error", "Preview panel components could not be initialized.")
        # ---------------------------------------------------------------------------

        setup_signals(self) # Menghubungkan sinyal tombol proses/simpan

        if self.preview_handler and hasattr(self, 'right_panel'):
            try:
                self.right_panel.previewImageRequested.connect(self.preview_handler.update_preview)
                self.right_panel.preloadRequested.connect(self.preview_handler.preload_low_res_images)
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

    def handle_import_button(self):
        """Membuka dialog file dan memulai proses impor."""
        filter_parts = []

        all_supported_extensions = []
        for ext_list in SUPPORTED_FORMATS.values():
            all_supported_extensions.extend([f"*{ext}" for ext in ext_list])
        all_filter_str = f"All Supported Images ({' '.join(sorted(list(set(all_supported_extensions))))})"
        filter_parts.append(all_filter_str)

        # 3. Tambahkan filter untuk setiap tipe format secara spesifik
        for format_key, extensions in SUPPORTED_FORMATS.items():
            formatted_extensions = ' '.join([f"*{ext}" for ext in extensions])
            description = f"{format_key.upper()} Files"
            filter_parts.append(f"{description} ({formatted_extensions})")

        # 4. Tambahkan filter "Semua File" sebagai opsi terakhir
        filter_parts.append("All Files (*)")

        # 5. Gabungkan semua bagian filter dengan ';;'
        file_dialog_filter = ';;'.join(filter_parts)
    
        # Gunakan filter string yang sudah dibuat
        image_paths, _ = QFileDialog.getOpenFileNames(
            self,
            language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH,
            "",
            file_dialog_filter 
        )

        if image_paths:
            self._process_and_start_import(image_paths)

    @Slot(list)
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
                       converted = convert_tiff_to_uncompressed(tiff_path, output_folder)
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
             else: 
                #  print("Warning: Slot 'update_progress_bar' not found.")
                pass

             if hasattr(self, 'on_import_complete') and callable(self.on_import_complete):
                  self.multi_thread_import_images.completion_signal.connect(self.on_import_complete)
             else: 
                #  print("Warning: Slot 'on_import_complete' not found.")
                pass

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
            if  alignment_choice == "No Alignment" and \
                denoising_choice == "No Denoising" and \
                super_resolution_choice == "No Super Resolution":
                QMessageBox.warning(self, "Caution", language_config.PROCESS_ALGORITHM_PROCESS_SKIPPED)
                return

            # Proses untuk Alignment
            alignment_valid = True
            if alignment_choice == "ORB":
                running_orb(self, single_process=True)
            elif alignment_choice == "Farneback Optical Flow":
                running_farneback_optical_flow(self, single_process=True)
            elif alignment_choice == "AKAZE":
                running_akaze(self, single_process=True)
            elif alignment_choice == "Light Glue":
                running_light_glue(self, single_process=True)
            elif alignment_choice == "No Alignment":
                if denoising_choice != "No Denoising" or super_resolution_choice != "No Super Resolution":
                    reply = QMessageBox.question(self, "Confirm",
                                            language_config.NO_ALIGNMENT_PROCESS,
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return
                else:
                    alignment_valid = False
                    QMessageBox.warning(self, "Warning", f"The alignment algorithm option '{alignment_choice}' is not recognized.")
                    return 
                
            super_resolution_executed = False
            if super_resolution_choice == "Interpolation":
               running_interpolation(self, single_process=True) 
            elif super_resolution_choice == "No Super Resolution":
                pass 
           
            
            if super_resolution_executed:
                latest_image_path = get_last_image("database/stack")
                if latest_image_path:
                    dialog = ImageViewer(latest_image_path, self) 
                    dialog.exec() 
                else:
                    QMessageBox.warning(self, "Caution", language_config.NOT_IMAGE_PREVIEW)


            # Proses untuk Denoising
            denoising_executed = False
            if denoising_choice == "Average":
                running_average(self, single_process=True)
                denoising_executed = True
            elif denoising_choice == "Median":
                running_median(self, single_process=True)
                denoising_executed = True
            elif denoising_choice == "Similarity":
                running_similarity(self, single_process=True)
                denoising_executed = True
            elif denoising_choice == "No Denoising":
                pass 
           
            if denoising_executed:
                latest_image_path = get_last_image("database/stack")
                if latest_image_path:
                    dialog = ImageViewer(latest_image_path, self)
                    dialog.exec()  
                else:
                    QMessageBox.warning(self, "Warning", language_config.NOT_IMAGE_PREVIEW)
        except Exception as e:
                    QMessageBox.critical(self, "Error", language_config.RUN_ERROR_STATUS.format(error = e))

    def save_image(self):
        """Menyimpan gambar hasil proses ke lokasi yang dipilih pengguna.
        Untuk TIFF, file akan disalin/dipindahkan. Untuk format lain, akan dikonversi.
        Metadata asli dari gambar sumber akan coba diterapkan."""
        folder_path = "database/stack"

        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "Error", language_config.UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH)
            return

        image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not image_files:
            QMessageBox.warning(self, "No Images", "There are no processed images to save.")
            return

        image_files.sort(key=os.path.getmtime, reverse=True)
        latest_image_path = image_files[0] # Ini adalah path sumber

        default_save_filename = os.path.basename(latest_image_path)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image As",
            default_save_filename, # Gunakan nama file asli sebagai default
            "TIFF (*.tif *.tiff);;JPEG (*.jpg *.jpeg);;PNG (*.png)"
        )

        if not file_path:
            return  # Pengguna membatalkan dialog

        # Tentukan ekstensi file tujuan berdasarkan pilihan pengguna
        chosen_file_extension = os.path.splitext(file_path)[-1].lower()
        
        # Validasi format tujuan
        supported_save_formats = [".tif", ".tiff", ".jpg", ".jpeg", ".png"]
        if chosen_file_extension not in supported_save_formats:
            if not chosen_file_extension and "TIFF (*.tif *.tiff)" in file_path: # Heuristik sederhana
                 file_path += ".tif"
                 chosen_file_extension = ".tif"
            elif not chosen_file_extension and "JPEG (*.jpg *.jpeg)" in file_path:
                 file_path += ".jpg"
                 chosen_file_extension = ".jpg"
            elif not chosen_file_extension and "PNG (*.png)" in file_path:
                 file_path += ".png"
                 chosen_file_extension = ".png"
            else:
                QMessageBox.warning(self, "Invalid Format", "Unsupported file format or no valid extension provided.")
                return

        try:
            if chosen_file_extension in [".tif", ".tiff"]:
                # Jika tujuannya TIFF, cukup salin filenya
                if os.path.abspath(latest_image_path) != os.path.abspath(file_path):
                    shutil.copy2(latest_image_path, file_path)
            else: 
                # 1. Baca data gambar HANYA SEKALI menggunakan metode yang paling andal.
                source_image_data = None
                try:
                    source_image_data = tifffile.imread(latest_image_path)
                except Exception as tif_read_error:
                        QMessageBox.critical(self, "Error", f"{language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED}\nCould not read source: {tif_read_error}")
                        return

                # 2. Periksa apakah pembacaan berhasil
                if source_image_data is None:
                    # Jika kedua metode gagal, tampilkan pesan error dan berhenti
                    QMessageBox.critical(self, "Error", language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
                    return
                
                # 3. Panggil fungsi konversi dengan DATA GAMBAR, bukan path
                save_special_jpg_and_png(
                    img_np=source_image_data,           # <--- Kirim array NumPy
                    dst_path=file_path,
                    reference_image_path=latest_image_path, # <--- Tetap kirim path referensi untuk metadata
                    quality=98,
                    optimize=True
                )
                
            # [PERBAIKAN] Logika pembersihan file sementara di luar blok konversi
            if os.path.exists(latest_image_path):
                try:
                    os.remove(latest_image_path)
                except OSError as e:
                    QMessageBox.warning(self, "Cleanup Error", f"Could not remove the temporary processed file:\n{latest_image_path}\n\nError: {e}")

            QMessageBox.information(self, "Success", language_config.UI_SUCCES_TO_SAVE_IMAGE_BATCH.format(file_path))

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Exiftool not found. Please ensure it is installed and in your system's PATH.")
        except Exception as e:
            error_message = str(e)
            if isinstance(e, subprocess.CalledProcessError):
                error_message = f"Exiftool error: {e.stderr}"
            
            QMessageBox.critical(self, "Error", language_config.UI_FAILED_TO_SAVE_IMAGE_BATCH.format(error_message))
            
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

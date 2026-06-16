from __future__ import annotations
import shutil
import subprocess
import os
from PIL import Image, UnidentifiedImageError
import tifffile

from PySide6.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QTimer,
    QEvent,
    QCoreApplication,
    QSize,
)

# Generic UI Library
from resources.GenericUILibrary.store import (
    get_store,
    DataStore,
)


from pixel_refine_desktop.enhance_stack.core.logic.ImagePreviewHandler import (
    ImagePreviewHandler,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.AKAZE import (
    running_akaze,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.Farneback_optical_flow import (
    running_farneback_optical_flow,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.Light_Glue import (
    running_light_glue,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.ORB import running_orb
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    save_special_jpg_and_png,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Average import (
    running_average,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
    running_median,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    running_mf_denoiser as running_similarity,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.Interpolation import (
    running_interpolation,
)

from pixel_refine_desktop.enhance_stack.components.batch_page_v2.page_layout import (
    setup_main_layout,
    setup_signals,
)

from pixel_refine_desktop.enhance_stack.core.logic.database_manager import (
    DatabaseManager,
)
from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
    ImageImportThreading,
)
from pixel_refine_desktop.enhance_stack.core.logic.workflow_process import (
    ImageViewer,
    get_last_image,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_import_service import (
    convert_tiff_to_uncompressed,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from config import SUPPORTED_FORMATS
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.left_panel import (
        LeftPanel,
    )
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.right_panel import (
        RightPanel,
    )
    from pixel_refine_desktop.enhance_stack.controllers.batch_page_controller import (
        BatchPageController,
    )


class BatchPageV2Layout(QWidget):
    """Batch page layout v2 - Enhanced version with modular components."""

    process_clicked = Signal()
    page_changed = Signal(int)  # For global navigation forwarding

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        self.preview_handler: ImagePreviewHandler | None = None
        self.workspace_panel: LeftPanel | None = None
        self.batch_panel: RightPanel | None = None
        self.controller: BatchPageController | None = None
        self.single_page_layout: QHBoxLayout | None = None

        # Initialize Centralized Data Store
        self.store = get_store()  # Use global store or new instance
        # If we want a dedicated one for this page:
        # self.store = DataStore()

        # Bind to settings file
        json_path = os.path.join("database", "align", "batch_parameter.json")
        self.store.bind_to_file(json_path)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 5, 0, 0)

        setup_main_layout(self, self.database_manager)
        setup_signals(self)  # Menghubungkan sinyal tombol proses/simpan

        # Connect workspace signals (optional, non-critical)
        self._connect_workspace_signals()

    def _connect_workspace_signals(self):
        """
        Gracefully attempt to connect preview signals if components are available.
        This method fails silently if components are not initialized.
        """
        try:
            # Try to find workspace_panel from parent layout
            workspace_panel: Optional["LeftPanel"] = None
            layout = self.layout()
            if layout is not None:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item is not None:
                        widget = item.widget()
                        if widget and hasattr(widget, "display_panel"):
                            workspace_panel = widget  # type: ignore
                            self.workspace_panel = workspace_panel
                            break

            if workspace_panel and self.preview_handler:
                # image_updated signal is no longer present in LeftPanel
                pass
        except Exception as e:
            # Catch all exceptions to prevent initialization failure
            # This is non-critical functionality
            pass

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
            formatted_extensions = " ".join([f"*{ext}" for ext in extensions])
            description = f"{format_key.upper()} Files"
            filter_parts.append(f"{description} ({formatted_extensions})")

        # 4. Tambahkan filter "Semua File" sebagai opsi terakhir
        filter_parts.append("All Files (*)")

        # 5. Gabungkan semua bagian filter dengan ';;'
        file_dialog_filter = ";;".join(filter_parts)

        # Gunakan filter string yang sudah dibuat
        image_paths, _ = QFileDialog.getOpenFileNames(
            self,
            language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH,
            "",
            file_dialog_filter,
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
        if not image_paths:
            return

        # 1. Validasi Duplikat di DB
        try:
            existing_single_paths = (
                self.database_manager.get_single_process_image_paths()
            )
        except Exception as e:
            QMessageBox.critical(
                self, language_config.MSG_DATABASE_ERROR, language_config.MSG_DB_RETRIEVE_FAILED
            )
            return

        duplicates = [path for path in image_paths if path in existing_single_paths]
        unique_files = [path for path in image_paths if path not in duplicates]

        if duplicates:
            message = (
                language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(
                    count=len(duplicates)
                )
            )
            QMessageBox.warning(
                self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE, message
            )

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
            QMessageBox.information(
                self, *language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
            )
            return

        # 3. Konversi TIFF (jika ada)
        output_folder = "database/align/uncompressed_tiff"
        try:
            os.makedirs(output_folder, exist_ok=True)
        except OSError as e:
            print(f"Error creating TIFF output folder: {e}")
            QMessageBox.critical(
                self,
                language_config.MSG_FOLDER_ERROR,
                f"{language_config.MSG_CREATE_FOLDER_TIFF_FAILED}\n{e}",
            )
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
                processed_tiff_path = tiff_path  # Default pakai asli
                needs_conversion = False
                compression = "unknown"

                try:
                    # Gunakan Pillow untuk membaca informasi
                    with Image.open(tiff_path) as img:
                        compression = img.info.get("compression", "none").lower()

                        print(
                            f"  TIFF File: {os.path.basename(tiff_path)} -> Detected Compression: {compression}"
                        )

                        # Cek kompresi yang perlu dikonversi
                        if compression in ["tiff_lzw", "tiff_zip", "packbits", "jpeg"]:
                            needs_conversion = True

                except (FileNotFoundError, UnidentifiedImageError, Exception) as e:
                    print(
                        f"  TIFF Error reading info/opening: {os.path.basename(tiff_path)}, Error: {e}"
                    )
                    tiff_errors.append(f"{os.path.basename(tiff_path)} (Read Error)")
                    continue

                if needs_conversion:
                    print(f"  Conversion triggered: {compression} needs decompressing.")

                    # Logic yang sudah diubah (menggunakan next() untuk generator)
                    conversion_generator = convert_tiff_to_uncompressed(
                        [tiff_path], output_folder
                    )
                    conversion_successful = False
                    try:
                        success, result_path_or_error = next(conversion_generator)

                        if success:
                            converted = result_path_or_error
                            conversion_successful = True
                        else:
                            converted = None
                            tiff_errors.append(result_path_or_error)

                    except StopIteration:
                        print(
                            f"  Conversion generator failed to produce output for: {os.path.basename(tiff_path)}"
                        )
                        tiff_errors.append(
                            f"{os.path.basename(tiff_path)} (No result generated)"
                        )
                        converted = None

                    if conversion_successful and converted:
                        processed_tiff_path = converted
                    else:
                        print(
                            f"  Skipping TIFF due to conversion error: {os.path.basename(tiff_path)}"
                        )
                        continue  # Skip jika konversi gagal

                files_ready_for_import.append(
                    processed_tiff_path
                )  # Tambahkan path TIFF (asli atau konversi)

            if tiff_errors:
                QMessageBox.warning(
                    self,
                    language_config.MSG_TIFF_PROCESSING_ISSUES,
                    f"{language_config.MSG_TIFF_PROCESS_FAILED_SOME}\n{', '.join(tiff_errors)}",
                )

        # 4. & 5. Seleksi File Akhir (Sekarang berisi semua file valid)
        selected_files = files_ready_for_import
        if not selected_files:
            QMessageBox.information(
                self,
                language_config.MSG_IMPORT_FAILED,
                language_config.MSG_NO_VALID_FILES_IMPORT,
            )
            return

        # 6. Proses Impor di Thread
        try:
            self.multi_thread_import_images = ImageImportThreading(
                database_manager=self.database_manager,
                image_paths=selected_files,
                batch_size=15,
                delay_ms=25,
            )

            # KONEKSI REAL-TIME:
            # Setiap 1 gambar selesai di-import thread, langsung muncul di DisplayPanel
            if self.workspace_panel and hasattr(self.workspace_panel, "display_panel"):
                self.multi_thread_import_images.image_added_signal.connect(
                    self.workspace_panel.display_panel.add_single_image_to_grid
                )

            # ... (koneksi sinyal progress lainnya) ...
            self.multi_thread_import_images.start()

        except Exception as e:
            QMessageBox.critical(self, language_config.MSG_ERROR_TITLE, f"{language_config.MSG_IMPORT_ERROR_OCCURRED}\n{e}")

    def on_import_complete(self, successful_images):
        """Dijalankan saat semua proses impor selesai."""
        # HILANGKAN Dialog Konfirmasi (QMessageBox) agar UI tidak terjeda.
        
        # Pastikan progress bar disembunyikan
        if self.workspace_panel and hasattr(self.workspace_panel, "algorithm_panel"):
            algo_panel = self.workspace_panel.algorithm_panel
            if hasattr(algo_panel, "progress_bar"):
                algo_panel.progress_bar.setValue(0)
                algo_panel.progress_bar.setVisible(True)
        
        print(f"Impor selesai: {successful_images} gambar berhasil dimasukkan.")

    def handle_delete_button(self):
        """Function to delete images"""
        if not self.workspace_panel:
            return

        selected_paths = self.workspace_panel.get_select_image_list()
        if not selected_paths:
            title, message = (
                language_config.HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED
            )
            QMessageBox.information(self, title, message)
            return

        from resources.GenericUILibrary import modal_confirm
        confirmed = modal_confirm.question(
            self,
            language_config.HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE.format(
                len(selected_paths)
            )
        )
        
        if confirmed:
            self.database_manager.single_process_delete_path_images(selected_paths)
            self.workspace_panel.remove_selected_images()

    def single_process_algorithm(self, batch_mode=False):
        """
        Fungsi untuk memproses algoritma berdasarkan pilihan dropdown.

        Args:
            batch_mode: If True, skip UI dialogs and previews (for background processing)
        """
        try:
            # Ambil parameter dari Right Panel (Generic UI) via AlgorithmPanel
            if not self.workspace_panel or not hasattr(
                self.workspace_panel, "algorithm_panel"
            ):
                return

            algo_panel = self.workspace_panel.algorithm_panel
            settings = algo_panel.logic.get_settings()
            alignment_choice = settings.get("alignment", "No Alignment")
            denoising_choice = settings.get("denoising", "No Denoising")
            super_resolution_choice = settings.get(
                "super_resolution", "No Super Resolution"
            )

            # Jika tidak ada algoritma yang dipilih
            if (
                alignment_choice == "No Alignment"
                and denoising_choice == "No Denoising"
                and super_resolution_choice == "No Super Resolution"
            ):
                if not batch_mode:
                    QMessageBox.warning(
                        self,
                        language_config.MSG_CAUTION_TITLE,
                        language_config.PROCESS_ALGORITHM_PROCESS_SKIPPED,
                    )
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
                if (
                    denoising_choice != "No Denoising"
                    or super_resolution_choice != "No Super Resolution"
                ):
                    # In batch mode, skip confirmation dialog
                    if not batch_mode:
                        reply = QMessageBox.question(
                            self,
                            language_config.MSG_CONFIRM_TITLE,
                            language_config.NO_ALIGNMENT_PROCESS,
                            QMessageBox.StandardButton.Yes
                            | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No,
                        )
                        if reply == QMessageBox.StandardButton.No:
                            return
                else:
                    alignment_valid = False
                    if not batch_mode:
                        QMessageBox.warning(
                            self,
                            language_config.MSG_WARNING_TITLE,
                            language_config.MSG_ALIGN_ALGO_NOT_RECOGNIZED.format(alignment_choice),
                        )
                    return

            super_resolution_executed = False
            if super_resolution_choice == "Interpolation":
                running_interpolation(self, single_process=True)
            elif super_resolution_choice == "No Super Resolution":
                pass

            if super_resolution_executed and not batch_mode:
                latest_image_path = get_last_image("database/stack")
                if latest_image_path:
                    dialog = ImageViewer(latest_image_path, self)
                    dialog.exec()
                else:
                    QMessageBox.warning(
                        self, "Caution", language_config.NOT_IMAGE_PREVIEW
                    )

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

            if denoising_executed and not batch_mode:
                latest_image_path = get_last_image("database/stack")
                if latest_image_path:
                    dialog = ImageViewer(latest_image_path, self)
                    dialog.exec()
                else:
                    QMessageBox.warning(
                        self, "Warning", language_config.NOT_IMAGE_PREVIEW
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", language_config.RUN_ERROR_STATUS.format(error=e)
            )

    def run_batch_for_id(self, batch_id):
        """
        Execute processing pipeline for a specific batch ID programmatically.
        Used by BatchProcessingThread.

        IMPORTANT: This method is called from a background thread, so it must NOT
        perform any UI operations directly. All UI updates should be done via signals.

        This version uses AlgorithmProcessorThread for proper threading control.
        """
        from PySide6.QtCore import QEventLoop
        from pixel_refine_desktop.enhance_stack.core.logic.algorithm_processor import (
            AlgorithmProcessorThread,
        )

        # Get current algorithm settings from the workspace panel
        if not self.workspace_panel or not hasattr(
            self.workspace_panel, "algorithm_panel"
        ):
            return

        algo_panel = self.workspace_panel.algorithm_panel
        settings = algo_panel.logic.get_settings()

        # Create event loop to wait for thread completion
        loop = QEventLoop()

        # Create and configure the algorithm processor thread
        processor = AlgorithmProcessorThread(
            batch_id=batch_id,
            settings=settings,
            parent=self,
            single_process=True,  # Run in single process mode for batch
        )

        # Connect finished signal to quit the event loop
        processor.finished_processing.connect(loop.quit)
        processor.error_occurred.connect(loop.quit)

        # Start the thread and wait for completion
        processor.start()
        loop.exec()  # Block until thread finishes

        # Clean up
        processor.wait()

    def get_files_in_stack_folder(self):
        """Get list of files in the stack folder."""
        folder_path = "database/stack"
        if not os.path.exists(folder_path):
            return []

        # Return set of full paths efficiently
        return [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

    def _move_single_batch_result(self, source_file, target_folder):
        """Move a processed file to target folder, handling naming."""
        if not os.path.exists(target_folder):
            try:
                os.makedirs(target_folder)
            except OSError:
                return False

        filename = os.path.basename(source_file)
        target_path = os.path.join(target_folder, filename)

        # Basic collision handling (append suffix)
        if os.path.exists(target_path):
            name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(target_path):
                target_path = os.path.join(target_folder, f"{name}_{counter}{ext}")
                counter += 1

        try:
            shutil.move(source_file, target_path)
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False

    def save_image(self):
        """
        Menyimpan gambar hasil proses ke lokasi yang dipilih pengguna.
        Untuk TIFF, file akan disalin/dipindahkan. Untuk format lain, akan dikonversi.
        Metadata asli dari gambar sumber akan coba diterapkan.
        """
        folder_path = "database/stack"

        if not os.path.exists(folder_path):
            QMessageBox.warning(
                self,
                language_config.MSG_ERROR_TITLE,
                language_config.UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH,
            )
            return

        image_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        if not image_files:
            QMessageBox.warning(
                self, language_config.MSG_WARNING_TITLE, language_config.MSG_NO_PROCESSED_IMAGES_SAVE
            )
            return

        image_files.sort(key=os.path.getmtime, reverse=True)
        latest_image_path = image_files[0]  # Ini adalah path sumber

        default_save_filename = os.path.basename(latest_image_path)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image As",
            default_save_filename,  # Gunakan nama file asli sebagai default
            "TIFF (*.tif *.tiff);;JPEG (*.jpg *.jpeg);;PNG (*.png)",
        )

        if not file_path:
            return  # Pengguna membatalkan dialog

        # Tentukan ekstensi file tujuan berdasarkan pilihan pengguna
        chosen_file_extension = os.path.splitext(file_path)[-1].lower()

        # Validasi format tujuan
        supported_save_formats = [".tif", ".tiff", ".jpg", ".jpeg", ".png"]
        if chosen_file_extension not in supported_save_formats:
            if not chosen_file_extension and "TIFF (*.tif *.tiff)" in file_path:
                file_path += ".tif"
                chosen_file_extension = ".tif"
            elif not chosen_file_extension and "JPEG (*.jpg *.jpeg)" in file_path:
                file_path += ".jpg"
                chosen_file_extension = ".jpg"
            elif not chosen_file_extension and "PNG (*.png)" in file_path:
                file_path += ".png"
                chosen_file_extension = ".png"
            else:
                QMessageBox.warning(
                    self,
                    language_config.MSG_INVALID_FORMAT,
                    language_config.MSG_UNSUPPORTED_FORMAT_EXTENSION,
                )
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
                    QMessageBox.critical(
                        self,
                        language_config.MSG_ERROR_TITLE,
                        f"{language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED}\n{language_config.MSG_COULD_NOT_READ_SOURCE} {tif_read_error}",
                    )
                    return

                # 2. Periksa apakah pembacaan berhasil
                if source_image_data is None:
                    # Jika kedua metode gagal, tampilkan pesan error dan berhenti
                    QMessageBox.critical(
                        self,
                        language_config.MSG_ERROR_TITLE,
                        language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED,
                    )
                    return

                # 3. Panggil fungsi konversi dengan DATA GAMBAR, bukan path
                save_special_jpg_and_png(
                    img_np=source_image_data,  # <--- Kirim array NumPy
                    dst_path=file_path,
                    reference_image_path=latest_image_path,  # <--- Tetap kirim path referensi untuk metadata
                    quality=98,
                    optimize=True,
                )

            # [PERBAIKAN] Logika pembersihan file sementara di luar blok konversi
            if os.path.exists(latest_image_path):
                try:
                    os.remove(latest_image_path)
                except OSError as e:
                    QMessageBox.warning(
                        self,
                        language_config.MSG_CLEANUP_ERROR,
                        f"{language_config.MSG_REMOVE_TEMP_FAILED}\n{latest_image_path}\n\nError: {e}",
                    )

            QMessageBox.information(
                self,
                language_config.MSG_SUCCESS_TITLE,
                language_config.UI_SUCCES_TO_SAVE_IMAGE_BATCH.format(file_path),
            )

        except FileNotFoundError:
            QMessageBox.critical(
                self,
                language_config.MSG_ERROR_TITLE,
                language_config.MSG_EXIFTOOL_NOT_FOUND,
            )
        except Exception as e:
            error_message = str(e)
            if isinstance(e, subprocess.CalledProcessError):
                error_message = f"Exiftool error: {e.stderr}"

            QMessageBox.critical(
                self,
                language_config.MSG_ERROR_TITLE,
                language_config.UI_FAILED_TO_SAVE_IMAGE_BATCH.format(error_message),
            )

    def update_progress_bar(self, value, images_left):
        """Memperbarui progress bar dan menampilkan jumlah gambar yang tersisa."""
        if self.workspace_panel and hasattr(self.workspace_panel, "algorithm_panel"):
            algo_panel = self.workspace_panel.algorithm_panel
            if hasattr(algo_panel, "progress_bar"):
                algo_panel.progress_bar.setVisible(True)
                algo_panel.progress_bar.setValue(value)
                # text is not supported by minimalist ModernProgressBar
                pass
            
    def on_import_error(self, error_message):
        """Handle errors during image import."""
        QMessageBox.critical(
            self, language_config.MSG_IMPORT_ERROR, f"{language_config.MSG_IMPORT_ERROR_OCCURRED}\n{error_message}"
        )
        if self.workspace_panel and hasattr(self.workspace_panel, "algorithm_panel"):
            algo_panel = self.workspace_panel.algorithm_panel
            if hasattr(algo_panel, "progress_bar"):
                algo_panel.progress_bar.setVisible(False)

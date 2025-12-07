import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from config import SUPPORTED_FORMATS

from .multi_threading import ImageImportThreading
    
def handle_import_button(self):
        """Function to manage images import using SUPPORTED_FORMATS."""

        # --- Buat filter dialog dari SUPPORTED_FORMATS ---
        filter_parts = []
        all_supported_extensions_list = []
        for ext_list in SUPPORTED_FORMATS.values():
            all_supported_extensions_list.extend([f"*{ext}" for ext in ext_list])
        # Gunakan set untuk unik dan urutkan
        all_filter_str = f"All Supported Images ({' '.join(sorted(list(set(all_supported_extensions_list))))})"
        filter_parts.append(all_filter_str)

        for format_key, extensions in SUPPORTED_FORMATS.items():
            formatted_extensions = ' '.join([f"*{ext}" for ext in extensions])
            description = f"{format_key.upper()} Files"
            filter_parts.append(f"{description} ({formatted_extensions})")
        filter_parts.append("All Files (*)")
        file_dialog_filter = ';;'.join(filter_parts)
        # --- Selesai membuat filter ---

        # Buka dialog file
        image_paths, _ = QFileDialog.getOpenFileNames(
            self,
            language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, # Judul dialog
            "", # Direktori awal
            file_dialog_filter # Gunakan filter yang dibuat
        )

        if not image_paths:
            return

        # Buat set dari semua ekstensi yang didukung untuk pengecekan efisien
        supported_extensions_set = {
            ext.lower() for fmt_list in SUPPORTED_FORMATS.values() for ext in fmt_list
        }

        # Pra-filter: Hanya proses file yang memiliki ekstensi didukung
        valid_format_paths = [
            path for path in image_paths
            if os.path.splitext(path)[1].lower() in supported_extensions_set
        ]

        # Beri tahu jika ada file tidak valid yang dipilih & dibuang
        num_invalid = len(image_paths) - len(valid_format_paths)
        if num_invalid > 0:
             QMessageBox.information(self, "Format Tidak Didukung",
                                    f"{num_invalid} file yang dipilih memiliki format tidak didukung dan diabaikan.")

        if not valid_format_paths:
            # Gunakan pesan dari language_config jika ada, atau fallback
            msg_title = getattr(language_config, 'HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TITLE', "Tidak Ada File Valid")
            msg_text = getattr(language_config, 'HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TEXT', "Tidak ada file dengan format yang didukung yang dipilih.")
            QMessageBox.information(self, msg_title, msg_text)
            return

        # Step 1: Validasi duplikat (cek terhadap file dengan format valid saja)
        try:
            existing_paths = self.database_manager.get_all_image_paths() # Asumsi ini ada
            existing_paths_set = set(existing_paths)
        except Exception as e:
            print(f"Error getting existing paths: {e}")
            QMessageBox.critical(self, "Database Error", "Could not retrieve existing image paths from database.")
            return

        duplicates = [path for path in valid_format_paths if path in existing_paths_set]
        unique_files = [path for path in valid_format_paths if path not in existing_paths_set]

        if duplicates:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
            QMessageBox.warning(self,
                                language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE, # Judul duplikat
                                message)

        if not unique_files:
            print("Tidak ada file unik baru yang valid untuk diimpor.")
            return # Tidak ada yang perlu diimpor

        # Step 2: Group files by format key from SUPPORTED_FORMATS
        format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}
        files_found_count = 0
        for path in unique_files:
            file_ext_lower = os.path.splitext(path)[1].lower()
            found_group = False
            for format_key, extensions in SUPPORTED_FORMATS.items():
                if file_ext_lower in extensions:
                    format_groups[format_key].append(path)
                    files_found_count += 1
                    found_group = True
                    break
            # if not found_group: # Seharusnya tidak terjadi karena sudah difilter di awal
            #    print(f"Peringatan: File '{os.path.basename(path)}' melewati filter awal tapi tidak cocok grup?")

        # Periksa lagi jika setelah grouping tidak ada file (seharusnya tidak terjadi)
        if files_found_count == 0:
             QMessageBox.information(self, "Error", "Tidak ada file yang bisa dikelompokkan berdasarkan format yang didukung.")
             return

        # Step 3: Determine dominant format key
        # Filter dulu grup yang tidak kosong untuk menghindari error jika ada format tanpa file
        non_empty_groups = {k: v for k, v in format_groups.items() if v}
        if not non_empty_groups:
             QMessageBox.information(self, "Error", "Tidak ada grup format yang berisi file setelah pengelompokan.")
             return
        dominant_format_key = max(non_empty_groups, key=lambda k: len(non_empty_groups[k]))

        # Step 4: Select files based on priority or dominant format
        selected_files = []
        # Gunakan files_found_count sebagai total file valid yang berhasil dikelompokkan
        if len(format_groups[dominant_format_key]) > files_found_count / 2:
            # Jika format dominan lebih dari setengah, prioritaskan
            selected_files = format_groups[dominant_format_key]
            print(f"Memilih format dominan '{dominant_format_key}' dengan {len(selected_files)} file.")
        else:
            # Jika tidak, ambil format pertama yang tersedia berdasarkan urutan di SUPPORTED_FORMATS
            selected = False
            for key in SUPPORTED_FORMATS.keys(): # Iterasi sesuai urutan dictionary (Python 3.7+)
                if format_groups[key]: # Ambil grup pertama yang tidak kosong
                    selected_files = format_groups[key]
                    dominant_format_key = key # Update dominant_format_key untuk pesan
                    print(f"Memilih format pertama tersedia '{dominant_format_key}' dengan {len(selected_files)} file.")
                    selected = True
                    break
            if not selected:
                 # Fallback jika terjadi error logika (seharusnya tidak mungkin jika non_empty_groups dicek)
                 print("Error: Tidak bisa memilih file, tidak ada grup yang valid?")
                 return


        # Step 5: Proceed with selected files
        if selected_files:
            # Inform user about the selected format and number of files to import
            # Gunakan dominant_format_key yang sudah benar (entah dari max atau dari iterasi fallback)
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT.format(
                count=len(selected_files),
                format=dominant_format_key.upper() # Tampilkan format key (misal "JPG", "DNG")
            )

            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_SELECTED, message) # Judul info

            # Proceed with importing the selected files
            try:
                self.multi_thread_import_images = ImageImportThreading(
                    database_manager=self.database_manager, # Berikan instance db_manager
                    image_paths=selected_files,
                    batch_size=15, # Atau ambil dari setting
                    delay_ms=25    # Atau ambil dari setting
                )

                # Connect signals to update progress and completion
                # Gunakan getattr untuk keamanan jika slot tidak ada
                progress_slot = getattr(self, 'update_progress_bar', None)
                if callable(progress_slot):
                    self.multi_thread_import_images.progress_signal.connect(progress_slot)

                completion_slot = getattr(self, 'on_import_complete', None)
                if callable(completion_slot):
                    self.multi_thread_import_images.completion_signal.connect(completion_slot)

                # Tambahkan error signal jika ada
                error_slot = getattr(self, 'on_import_error', None) # Asumsi nama slot error
                if hasattr(self.multi_thread_import_images, 'error_signal') and callable(error_slot):
                     self.multi_thread_import_images.error_signal.connect(error_slot)


                # Start the thread
                self.multi_thread_import_images.start()
            except Exception as e:
                 print(f"Error creating/starting import thread: {e}")
                 QMessageBox.critical(self, "Threading Error", f"Could not start the import process:\n{e}")

        else:
             # Pesan jika tidak ada file terpilih setelah logika dominan/prioritas
             msg_title = getattr(language_config, 'HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TITLE', "Tidak Ada File Valid")
             msg_text = getattr(language_config, 'HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TEXT', "Tidak ada file yang valid untuk diimpor setelah seleksi format.")
             QMessageBox.information(self, msg_title, msg_text)

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

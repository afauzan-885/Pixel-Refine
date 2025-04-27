import os
import shutil
import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QMessageBox, QFileDialog,
                              QApplication, QGraphicsOpacityEffect)
from PyQt6.QtCore import (pyqtSignal, QPropertyAnimation, QEasingCurve, QEvent,
                          QTimer,pyqtSlot, QThread)
import weakref
from PIL import Image, UnidentifiedImageError
from UI.enhance_stack.components.batch_page_layout.batch_layout import refresh_ui, setup_main_panel
from UI.enhance_stack.components.batch_page_layout.combined_panel import CombinedPanel
from UI.enhance_stack.components.batch_page_layout.image_batch_management import BatchDeleteProcess
from UI.enhance_stack.components.batch_page_layout.thumbnail import stop_all_thumbnails
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.enhance_stack.logic.multi_threading import BatchImageImportThreading
from UI.resources.animation.animation_manager import StackedWidgetAnimator
from UI.resources.animation.fade import fade_out
from UI.resources.stylesheet.stylesheet import SCROLL_AREA
from UI.settings.General.Language import language_config
from config import  CACHE_DIR, SUPPORTED_FORMATS

os.makedirs(CACHE_DIR, exist_ok=True)

class BatchPageLayout(QWidget):
    data_changed = pyqtSignal()
    show_toast_requested = pyqtSignal(str, object, bool)

    def __init__(self):
        super().__init__()
        self.thumbnail_threads = []
        self.thumbnail_placeholders = weakref.WeakValueDictionary()
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()
        self.animator = StackedWidgetAnimator(self)
        self._active_fade_in_animations = {}
        self._running_delete_threads = []
        self._bulk_delete_animation_counter = 0 # Tetap diperlukan di sini untuk 
        self.active_batch_panels = weakref.WeakValueDictionary()
        self.batch_states = {}
        # --- State Pelacakan Progres Agregat ---
        self._total_pending_imports = 0
        self._total_processed_imports = 0
        self._active_import_threads = [] # Simpan instance thread di sini
        # --------------------------------------
        
        self.combined_panel = CombinedPanel(self.database_manager)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)

        # Gunakan instance layout yang akan diisi oleh setup_main_panel
        self.main_panel_container = QVBoxLayout()
        self.main_scroll_area = setup_main_panel(self.main_panel_container, SCROLL_AREA)
        self.main_scroll_area.setObjectName("MainBatchScrollArea")
        
        # --- Aktifkan Drop & Filter untuk Scroll Area ---
        self.main_scroll_area.setAcceptDrops(True)
        self.main_scroll_area.installEventFilter(self)
        self._original_scroll_stylesheet = self.main_scroll_area.styleSheet()
        # ---------------------------------------------

        self.data_changed.connect(self.refresh_ui)
        
        self.refresh_ui()
        self.layout.addWidget(self.main_scroll_area)
        

    def stop_thumbnail(self):
        """Menghentikan semua thread thumbnail yang sedang berjalan."""
        stop_all_thumbnails(self.thumbnail_threads)

    def refresh_ui(self):
        ids_before_refresh = set(self.active_batch_panels.keys())
        current_batch_ids_in_ui = list(self.active_batch_panels.keys())
        for batch_id in current_batch_ids_in_ui:
            panel = self.active_batch_panels.get(batch_id)
            if panel:
                try:
                    # Cek jika panel sedang fade out (dikelola animator, tapi kita cek referensinya saja)
                    # Mungkin lebih aman tidak menyimpan state jika akan dihapus
                    # Perlu cara mengetahui apakah panel dijadwalkan untuk fade out
                    # Untuk sekarang, kita biarkan saja, mungkin tidak masalah besar
                    self.batch_states[batch_id] = panel.get_current_state()
                except Exception as e:
                    print(f"Error getting state from panel for batch {batch_id}: {e}")

        refresh_ui(
            self.database_manager,
            self.main_panel_container,
            self.setup_combined_panel
        )

        ids_after_refresh = set(self.active_batch_panels.keys())
        newly_added_ids = ids_after_refresh - ids_before_refresh

        for new_id in newly_added_ids:
            panel_to_animate = self.active_batch_panels.get(new_id)
            if panel_to_animate:
                 if panel_to_animate in self._active_fade_in_animations and \
                    self._active_fade_in_animations[panel_to_animate].state() == QPropertyAnimation.State.Running:
                     self._active_fade_in_animations[panel_to_animate].stop()
                     if panel_to_animate.graphicsEffect():
                          panel_to_animate.setGraphicsEffect(None)

                 opacity_effect = QGraphicsOpacityEffect(panel_to_animate)
                 panel_to_animate.setGraphicsEffect(opacity_effect)
                 opacity_effect.setOpacity(0.0)

                 duration = 350
                 curve = QEasingCurve.Type.InOutQuad

                 anim = QPropertyAnimation(opacity_effect, b"opacity", self)
                 anim.setDuration(duration)
                 anim.setStartValue(0.0)
                 anim.setEndValue(1.0)
                 anim.setEasingCurve(curve)

                 anim.finished.connect(lambda effect=opacity_effect, widget=panel_to_animate:
                                        self._on_fade_in_finished(effect, widget))

                 self._active_fade_in_animations[panel_to_animate] = anim
                 anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                
    def _on_fade_in_finished(self, effect: QGraphicsOpacityEffect, widget: QWidget):
         if widget:
              if widget.graphicsEffect() == effect:
                  widget.setGraphicsEffect(None)
         if widget in self._active_fade_in_animations:
              del self._active_fade_in_animations[widget]
    
    def setup_combined_panel(self, batch_id=None):
        initial_state = self.batch_states.get(batch_id, {})
        combined_panel = CombinedPanel(
            self.database_manager, batch_id, self, self.thumbnail_threads,
            self.thumbnail_placeholders, initial_state=initial_state
        )
        combined_panel.setVisible(True) # Pastikan terlihat
        self.active_batch_panels[batch_id] = combined_panel
        return combined_panel
    
    def eventFilter(self, source, event: QEvent):
        # ... (Logika eventFilter Drag/Drop tidak berubah) ...
        if source == self.main_scroll_area:
            if event.type() == QEvent.Type.DragEnter:
                should_accept = False
                if event.mimeData().hasUrls():
                    supported_extensions = {ext for fmts in SUPPORTED_FORMATS.values() for ext in fmts}
                    has_image = any( url.isLocalFile() and os.path.splitext(url.toLocalFile())[1].lower() in supported_extensions for url in event.mimeData().urls())
                    if has_image: should_accept = True

                if should_accept: event.acceptProposedAction(); self.main_scroll_area.setProperty("acceptingDrop", True); self.main_scroll_area.setStyleSheet(self._original_scroll_stylesheet + " QScrollArea#MainBatchScrollArea { border: 2px dashed #4CAF50; }")
                else: event.ignore()
                return True

            elif event.type() == QEvent.Type.DragLeave:
                if self.main_scroll_area.property("acceptingDrop"): self.main_scroll_area.setProperty("acceptingDrop", False); self.main_scroll_area.setStyleSheet(self._original_scroll_stylesheet)
                event.accept(); return True

            elif event.type() == QEvent.Type.DragMove:
                if event.mimeData().hasUrls(): event.acceptProposedAction()
                else: event.ignore()
                return True

            elif event.type() == QEvent.Type.Drop:
                if self.main_scroll_area.property("acceptingDrop"): self.main_scroll_area.setProperty("acceptingDrop", False); self.main_scroll_area.setStyleSheet(self._original_scroll_stylesheet)
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                    supported_extensions = {ext for fmts in SUPPORTED_FORMATS.values() for ext in fmts}
                    valid_image_paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile() and os.path.isfile(url.toLocalFile()) and os.path.splitext(url.toLocalFile())[1].lower() in supported_extensions]
                    if valid_image_paths: self._process_and_start_batch_import(valid_image_paths)
                    return True
                event.ignore(); return True
        return super().eventFilter(source, event)

    def process_all_batches(self):
        active_panels_list = list(self.active_batch_panels.values()) # Dapatkan daftar panel
        active_panels = [
            panel for panel in active_panels_list
            if panel and (panel not in self.animator._active_fade_outs) # Cek ke animator
        ]

        if not active_panels:
            self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_NO_PROCESS, 3000, False)
            return

        target_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not target_folder: return

        total_batches = len(active_panels)
        if total_batches == 0: self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_NO_PROCESS, 3000, False); return

        self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_PROCESS.format(total_batches), None, False); QApplication.processEvents()
        print(f"Starting processing for {total_batches} batches...")
        for i, batch_panel in enumerate(active_panels, start=1):
            if batch_panel: # Seharusnya selalu True karena sudah difilter
                 print(f"Processing batch {batch_panel.batch_id} ({i}/{total_batches})...")
                 try:
                    batch_panel.process_all_batch()
                    self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_PROGRESS.format(i, total_batches), None, True); QApplication.processEvents()
                 except Exception as e:
                    print(f"Error processing batch {batch_panel.batch_id}: {e}")
                    QMessageBox.warning(self, "Processing Error", f"An error occurred while processing batch {batch_panel.batch_id}:\n{e}")

        print("All batch processing finished. Saving images..."); self.save_image(target_folder)
        self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_SUCCES, 5000, False)

    def save_image(self, target_folder):
        """Memindahkan gambar dan MEMINTA toast ditampilkan."""
        folder_path = "database/stack"

        if not os.path.exists(folder_path):
            self.show_toast_requested.emit(language_config.UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH, 4000, False)
            return

        try:
            image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        except Exception as e:
             self.show_toast_requested.emit(f"Error accessing stack folder: {e}", 4000, False)
             return

        if not image_files:
            self.show_toast_requested.emit(language_config.UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH, 4000, False)
            return

        # Tampilkan toast sebelum memindahkan
        self.show_toast_requested.emit(language_config.UI_LABEL_MOVING_FILES.format(len(image_files), target_folder), None, True) # Progress
        QApplication.processEvents()

        move_errors = []
        for image_file_name in image_files:
             source_path = os.path.join(folder_path, image_file_name)
             destination_path = os.path.join(target_folder, image_file_name)
             try:
                 shutil.move(source_path, destination_path)
             except Exception as e:
                 error_msg = f"Failed to move '{image_file_name}': {e}"
                 print(error_msg)
                 move_errors.append(error_msg)

        # Tampilkan hasil akhir (toast success sudah ditampilkan oleh process_all_batches)
        if move_errors:
             error_details = "\n".join(move_errors)
             QMessageBox.critical(self, "Move Error", f"Some files could not be moved:\n{error_details}")


    # Contoh penggunaan di handle_delete_individual_batch
    def handle_delete_individual_batch(self, batch_id):
        panel_to_delete = self.active_batch_panels.get(batch_id)
        panel_ref = weakref.ref(panel_to_delete) if panel_to_delete else None

        if not panel_to_delete:
            print(f"Warning: Panel for batch {batch_id} not found for deletion animation.")
            return

        title, message = language_config.BATCH_DELETE_LABEL; message = message.format(batch_id)
        reply = QMessageBox.question(self, title, message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if batch_id in self.batch_states: del self.batch_states[batch_id]

            fade_out(
                animator=self.animator,
                widget=panel_to_delete,
                duration=300,
                on_finished_callback=lambda bid=batch_id, pref=panel_ref: self._individual_delete_post_animation(bid, pref)
            )
            

    def _individual_delete_post_animation(self, batch_id, panel_ref):
        """Callback setelah animasi fade-out individual selesai."""
        panel = panel_ref() if panel_ref else None
        if panel:
             panel.hide() 
        self._start_background_delete_process(batch_id)
            
    def _start_background_delete_process(self, batch_id):
        """Memulai proses penghapusan di background thread."""
        deleter_thread = BatchDeleteProcess(self.database_manager, batch_id, CACHE_DIR, self.thumbnail_threads)
        self._running_delete_threads.append(deleter_thread)
        
        # Hubungkan sinyal SEBELUM memulai thread
        deleter_thread.batch_deleted.connect(self.data_changed.emit)

        # --- HUBUNGKAN FINISHED UNTUK CLEANUP ---
        deleter_thread.finished.connect(lambda thread=deleter_thread: self._on_delete_thread_finished(thread))
        deleter_thread.start()
    
    def _on_delete_thread_finished(self, thread_instance):
        """Dipanggil saat thread delete selesai untuk menghapusnya dari list."""
        try:
            self._running_delete_threads.remove(thread_instance)
        except ValueError:
            pass  # Thread mungkin sudah dihapus karena suatu alasan, atau tidak pernah ditambahkan

    def handle_delete_all_batches(self):
        title = language_config.TITLE_BATCH_ALL_DELETE_BUTTON; conn = None; batch_defined_count = 0
        try:
            db_path = self.database_manager.db_path; conn = sqlite3.connect(db_path); cursor = conn.cursor(); cursor.execute("PRAGMA foreign_keys = ON;"); cursor.execute("SELECT COUNT(*) FROM batch_process"); batch_defined_count = cursor.fetchone()[0]
        except Exception as e: QMessageBox.critical(self, "Database Error", f"Failed to check batch status: {e}"); return
        finally:
            if conn: conn.close()
        if batch_defined_count == 0: QMessageBox.information(self, title, language_config.NO_DATA_BATCH_ALL_DELETE_BUTTON, QMessageBox.StandardButton.Ok); return
        message = language_config.CONFIRM_BATCH_ALL_DELETE_BUTTON.format(batch_defined_count)
        reply = QMessageBox.question(self, title, message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)


        if reply == QMessageBox.StandardButton.Yes:
            self.batch_states.clear()
            panels_to_animate = list(self.active_batch_panels.values())
            panel_refs = [weakref.ref(p) for p in panels_to_animate]

            if not panels_to_animate:
                self._start_bulk_background_delete_process(); return

            self._bulk_delete_animation_counter = len(panels_to_animate)
            delay_ms = 300

            for index, panel_ref in enumerate(panel_refs):
                 QTimer.singleShot(index * delay_ms,
                                   lambda pref=panel_ref: self._trigger_single_bulk_fade_out(pref))
    
    def _trigger_single_bulk_fade_out(self, panel_ref):
        """Memulai fade out untuk satu panel dalam proses bulk delete."""
        panel = panel_ref() if panel_ref else None
        if panel:
            fade_out(
                animator=self.animator, 
                widget=panel,
                duration=300,
                on_finished_callback=lambda pref=panel_ref: self._bulk_delete_post_single_animation(pref)
            )
        else:
            self._check_bulk_delete_animations_finished()
            
    def _bulk_delete_post_single_animation(self, panel_ref):
        panel = panel_ref() if panel_ref else None
        if panel: panel.hide()
        self._check_bulk_delete_animations_finished()
                 
    def _check_bulk_delete_animations_finished(self):
        """Dipanggil setiap kali satu animasi fade-out selesai saat delete all."""
        self._bulk_delete_animation_counter -= 1
        if self._bulk_delete_animation_counter <= 0:
            self._start_bulk_background_delete_process()

    def _start_bulk_background_delete_process(self):
        """Memulai proses penghapusan semua batch di background."""
        deleter = BatchDeleteProcess(self.database_manager, None, CACHE_DIR, self.thumbnail_threads)
        deleter.batch_deleted.connect(self.data_changed.emit)
        deleter.delete_all_batch()

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

    # --- Metode Pemanggil Utama ---
    def handle_batch_import_button(self):
        """Membuka dialog file dan memulai proses impor batch."""
        file_dialog_filter = language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
        image_paths, _ = QFileDialog.getOpenFileNames(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, "", file_dialog_filter)

        if image_paths:
            self._process_and_start_batch_import(image_paths)

    # --- Metode Helper Inti ---
    def _process_and_start_batch_import(self, image_paths: list):
        """
        Memproses daftar path gambar untuk impor batch: membuat batch baru,
        validasi, konversi, seleksi, dan memulai impor background.
        """
        if not image_paths: return

        try:
             existing_batch_names = self.database_manager.get_all_batch_names()
             next_batch_num = 1
             prefix = "batch"
             max_num_found = 0
             for name in existing_batch_names:
                 if name.startswith(prefix):
                     try:
                         num_part = name[len(prefix):]
                         if num_part.isdigit(): num = int(num_part)
                         if num > max_num_found: max_num_found = num
                     except ValueError: continue
             next_batch_num = max_num_found + 1
             target_batch_name = f"{prefix}{next_batch_num}"
             target_batch_id = self.database_manager.create_new_batch(target_batch_name)
             if target_batch_id is None:
                 raise Exception(f"Could not create or find batch '{target_batch_name}'.") # Jadi exception
        except Exception as e:
            QMessageBox.critical(self, "Batch Error", f"Failed to prepare batch:\n{e}")
            return
        # ------------------------------------

        # --- Step 1: Validasi Duplikat (dalam batch BARU ini) ---
        unique_files = list(image_paths)
        
        # --- Step 2: Group File berdasarkan Format ---
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
            title, message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
            QMessageBox.information(self, title, message)
            return
        # -------------------------------------------

        # --- Step 3: Konversi TIFF ---
        output_folder = "database/align/uncompressed_tiff"
        try:
            os.makedirs(output_folder, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, "Folder Error", f"Could not create folder for TIFF conversion:\n{e}")
            return

        files_to_import = []
        files_to_import.extend(format_groups.get("jpg", []))
        files_to_import.extend(format_groups.get("png", []))

        tiff_files = format_groups.get("tiff", [])
        if tiff_files:
             print(f"Processing {len(tiff_files)} TIFF files for batch {target_batch_id}...")
             converted_or_original_tiffs = []
             tiff_errors = []
             for tiff_path in tiff_files:
                  processed_tiff_path = tiff_path
                  needs_conversion = False
                  try:
                      with Image.open(tiff_path) as img:
                           compression = img.info.get("compression", "none").lower()
                           if compression in ["tiff_lzw", "tiff_zip", "packbits", "jpeg"]: needs_conversion = True
                  except (FileNotFoundError, UnidentifiedImageError, Exception) as e:
                       print(f"  TIFF Error reading info/opening: {os.path.basename(tiff_path)}, Error: {e}"); tiff_errors.append(f"{os.path.basename(tiff_path)} (Read Error)"); continue

                  if needs_conversion:
                       print(f"  Converting compressed TIFF: {os.path.basename(tiff_path)}")
                       converted = self.convert_tiff_to_uncompressed(tiff_path, output_folder)
                       if converted: processed_tiff_path = converted
                       else: print(f"  Skipping TIFF due to conversion error: {os.path.basename(tiff_path)}"); tiff_errors.append(f"{os.path.basename(tiff_path)} (Conversion Failed)"); continue
                  converted_or_original_tiffs.append(processed_tiff_path)

             files_to_import.extend(converted_or_original_tiffs)
             if tiff_errors: QMessageBox.warning(self, "TIFF Processing Issues", f"Could not process some TIFF files:\n{', '.join(tiff_errors)}")
        # ---------------------------

        # --- Step 4 & 5: Seleksi File (Logika Dominan/Prioritas) ---
        selected_files = []
        if files_to_import: # Hanya proses jika ada file setelah filter/konversi
            temp_format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}
            for path in files_to_import: # Kelompokkan ulang path yang SIAP impor
                 lower_path = path.lower()
                 for format_key, extensions in SUPPORTED_FORMATS.items():
                     if any(lower_path.endswith(ext) for ext in extensions):
                          temp_format_groups[format_key].append(path)
                          break

            if any(temp_format_groups.values()): # Pastikan ada grup yang valid
                dominant_format = max(temp_format_groups, key=lambda key: len(temp_format_groups[key]))
                total_to_import = len(files_to_import)
                # Terapkan logika dominan
                if len(temp_format_groups[dominant_format]) > total_to_import / 2:
                     selected_files = temp_format_groups[dominant_format]
                     print(f"Selected dominant format '{dominant_format}' with {len(selected_files)} files.")
                else:
                     for key in SUPPORTED_FORMATS.keys():
                          if temp_format_groups[key]:
                              selected_files = temp_format_groups[key]
                              print(f"Selected first available format '{key}' with {len(selected_files)} files.")
                              dominant_format = key # Update dominant format untuk pesan
                              break
            else: # Seharusnya tidak terjadi, tapi jaga-jaga
                 print("Warning: No valid format groups found after TIFF conversion.")
                 selected_files = [] # Pastikan kosong
                 dominant_format = "N/A" # Default jika tidak ada yg terpilih
        else:
             dominant_format = "N/A" # Default jika tidak ada file awal
        # ---------------------------------------------------------

        # --- Step 6: Proses Impor File Terpilih ---
        if selected_files:
            num_files_this_batch = len(selected_files)
            
            # --- Update State Agregat ---
            self._total_pending_imports += num_files_this_batch
            # --------------------------

            # Tampilkan Toast Awal/Update
            self._update_aggregated_progress_toast() # Panggil update toast

            # Mulai impor di background thread
            try:
                import_thread = BatchImageImportThreading( # Buat instance thread baru
                    database_manager=self.database_manager, image_paths=selected_files,
                    batch_id=target_batch_id, batch_size=15, delay_ms=25
                )

                # --- Simpan Thread Aktif ---
                self._active_import_threads.append(import_thread)
                # -------------------------

                # --- Hubungkan Sinyal Thread ke Slot Agregasi ---
                import_thread.item_processed.connect(self._handle_item_imported) # Sinyal baru
                import_thread.finished.connect(lambda t=import_thread: self._handle_thread_finished(t)) # Sinyal bawaan QThread
                # Hubungkan error jika perlu
                if hasattr(import_thread, 'error_signal'):
                     import_thread.error_signal.connect(self.on_batch_import_error)
                # ---------------------------------------------

                import_thread.start() # Mulai thread

            except Exception as e:
                print(f"Error creating/starting batch import thread: {e}")
                QMessageBox.critical(self, "Threading Error", f"Could not start import process:\n{e}")
                self._total_pending_imports -= num_files_this_batch
                if self._total_pending_imports < 0: self._total_pending_imports = 0
                self._update_aggregated_progress_toast() # Update toast lagi


        else: # Jika tidak ada file terpilih
            title, message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
            QMessageBox.information(self, title, message)
            self.database_manager.batch_process_delete_batch(target_batch_id) # Hapus 
        # -----------------------------------

    @pyqtSlot()
    def _handle_item_imported(self):
        """Dipanggil setiap kali satu item berhasil diimpor oleh thread manapun."""
        self._total_processed_imports += 1
        self._update_aggregated_progress_toast() # Update tampilan progres

    @pyqtSlot(QThread) # Terima instance thread yang selesai
    def _handle_thread_finished(self, thread_instance):
        """Dipanggil saat thread impor selesai."""
        if thread_instance in self._active_import_threads:
            self._active_import_threads.remove(thread_instance)
        else:
            print("Warning: Finished thread not found in active list.")

        # Cek apakah SEMUA thread sudah selesai
        if not self._active_import_threads:
            #  final_processed = self._total_processed_imports
             final_total = self._total_pending_imports

             # Tampilkan pesan selesai terakhir
             completion_msg = language_config.ON_IMPORT_COMPLETE_MESSAGES.format(final_total)
             self.show_toast_requested.emit(completion_msg, 3000, False)

             # Reset state agregat
             self._total_pending_imports = 0
             self._total_processed_imports = 0

             # Emit sinyal data changed untuk refresh UI
             self.data_changed.emit()
        else:
             self._update_aggregated_progress_toast()


    def _update_aggregated_progress_toast(self):
        """Menghitung dan menampilkan progres impor agregat via toast."""
        if self._total_pending_imports > 0:
            progress = int((self._total_processed_imports / self._total_pending_imports) * 100)
            remaining = self._total_pending_imports - self._total_processed_imports
            progress_msg = language_config.UPDATE_PROGRESS_BAR_STATUS.format(progress, remaining)
            self.show_toast_requested.emit(progress_msg, None, True)
        elif not self._active_import_threads: 
             pass 
         
    @pyqtSlot(int, int)
    def _update_import_progress_toast(self, progress_percent, items_left):
        """Update teks toast dengan informasi progres impor."""
        progress_msg = language_config.UPDATE_PROGRESS_BAR_STATUS.format(progress_percent, items_left)
        
        self.show_toast_requested.emit(progress_msg, None, True) 
        
    @pyqtSlot(str, str)
    def on_batch_import_error(self, item_path, error_message):
        self._total_pending_imports -= 1
        if self._total_pending_imports < 0 : self._total_pending_imports = 0
        self._update_aggregated_progress_toast()
        QMessageBox.warning(self, "Batch Import Error", f"Failed import '{os.path.basename(item_path)}':\n{error_message}")

    @pyqtSlot(int) 
    def _on_batch_import_complete(self, total_items_processed):
        """Dipanggil saat thread impor batch selesai."""
        completion_msg = language_config.ON_IMPORT_COMPLETE_STATUS
        self.show_toast_requested.emit(completion_msg, 3000, False) 

        self.data_changed.emit()

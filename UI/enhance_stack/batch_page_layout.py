import os
import shutil
import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QMessageBox, QFileDialog,
                              QApplication, QGraphicsOpacityEffect)
from PyQt6.QtCore import (pyqtSignal, QPropertyAnimation, QEasingCurve, QEvent,
                          QTimer, pyqtSlot, QThread)
import weakref
from UI.enhance_stack.components.batch_page_layout.batch_layout import refresh_ui, setup_main_panel
from UI.enhance_stack.components.batch_page_layout.combined_panel import CombinedPanel
from UI.enhance_stack.components.batch_page_layout.image_batch_management import BatchDeleteProcess, process_and_start_batch_import
from UI.enhance_stack.components.batch_page_layout.thumbnail import stop_process_thumbnails
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.resources.animation.animation_manager import StackedWidgetAnimator
from UI.resources.animation.fade import fade_out
from UI.resources.stylesheet.stylesheet import SCROLL_AREA
from UI.settings.General.Language import language_config
from config import CACHE_DIR, SUPPORTED_FORMATS

def is_widget_valid(widget):
    """Cek apakah widget masih valid (belum dihapus)."""
    if widget is None:
        return False
    try:
        _ = widget.isVisible()  # akses properti sederhana
        return True
    except RuntimeError:
        return False
    except Exception:
        return False

def safe_hide_widget(widget):
    """Sembunyikan widget jika masih valid, tangani error jika sudah dihapus."""
    if not is_widget_valid(widget):
        return
    try:
        widget.hide()
    except Exception:
        pass

class BatchPageLayout(QWidget):
    data_changed = pyqtSignal()
    show_toast_requested = pyqtSignal(str, object, bool)

    def __init__(self):
        super().__init__()
        # --- Initialization ---
        self.thumbnail_threads = []
        self.thumbnail_placeholders = weakref.WeakValueDictionary()
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()
        self.animator = StackedWidgetAnimator(self)
        self._active_fade_in_animations = {}
        self._running_delete_threads = []
        self._bulk_delete_animation_counter = 0
        self.active_batch_panels = weakref.WeakValueDictionary()
        self.batch_states = {}
        self._total_pending_imports = 0
        self._total_processed_imports = 0
        self._active_import_threads = []
        
        self.batch_order_viewer = 0 
        
        # --- UI Setup ---
        self.combined_panel = CombinedPanel(self.database_manager)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)
        self.main_panel_container = QVBoxLayout()
        self.main_scroll_area = setup_main_panel(self.main_panel_container, SCROLL_AREA)
        self.main_scroll_area.setObjectName("MainBatchScrollArea")
        self.main_scroll_area.setAcceptDrops(True)
        self.main_scroll_area.installEventFilter(self)
        self._original_scroll_stylesheet = self.main_scroll_area.styleSheet()
        self.data_changed.connect(self.refresh_ui)
        self.refresh_ui()
        self.layout.addWidget(self.main_scroll_area)

    # --- UI Refresh and Animation ---
    def refresh_ui(self):
        # 1. Kumpulkan batch_id yang sebaiknya dihapus dari active_batch_panels
        to_remove = []
        for batch_id, panel in list(self.active_batch_panels.items()):
            try:
                # Jika panel None atau sudah tidak valid (isWidgetType -> False), tandai untuk di‐remove
                if panel is None or not panel.isWidgetType():
                    to_remove.append(batch_id)
            except RuntimeError:
                # Kalau memanggil isWidgetType() langsung me‐lempar RuntimeError,
                # berarti objek C++ sudah di‐destroy. Maka kita juga hapus entry ini.
                to_remove.append(batch_id)

        # 2. Hapus semua panel yang sudah mati dari kamus
        for bid in to_remove:
            self.active_batch_panels.pop(bid, None)

        # 3. Sekarang ambil state hanya dari panel yang masih hidup
        ids_before_refresh = set(self.active_batch_panels.keys())
        for batch_id, panel in list(self.active_batch_panels.items()):
            try:
                # Metode get_current_state() sebaiknya juga sudah dibuat aman, 
                # meng‐handle widget yang mungkin telah dihapus
                self.batch_states[batch_id] = panel.get_current_state()
            except Exception as e:
                print(f"Error getting state from panel for batch {batch_id}: {e}")

        # 4. Reset urutan tampilan UI
        self.batch_order_viewer = 0

        # 5. Panggil fungsi global refresh_ui yang (kemungkinan) mem‐recreate UI
        refresh_ui(
            self.database_manager,
            self.main_panel_container,
            self.setup_combined_panel
        )

        # 6. Animasi untuk panel yang baru masuk
        ids_after_refresh = set(self.active_batch_panels.keys())
        newly_added_ids = ids_after_refresh - ids_before_refresh
        for new_id in newly_added_ids:
            panel_to_animate = self.active_batch_panels.get(new_id)
            if panel_to_animate:
                self._start_fade_in_animation(panel_to_animate)

    def _start_fade_in_animation(self, panel_to_animate):
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

    # --- Combined Panel Setup ---
    def setup_combined_panel(self, batch_id=None):
        self.batch_order_viewer += 1 
        current_ui_order_for_this_panel = self.batch_order_viewer

        initial_state = self.batch_states.get(batch_id, {})
        combined_panel = CombinedPanel(
            database_manager=self.database_manager,
            batch_id=batch_id,
            parent=self,
            thumbnail_threads=self.thumbnail_threads,
            thumbnail_placeholders=self.thumbnail_placeholders,
            initial_state=initial_state,
            sequential_batch_number=current_ui_order_for_this_panel 
        )
        self.active_batch_panels[batch_id] = combined_panel
        return combined_panel

    # --- Event Handling ---
    def eventFilter(self, source, event: QEvent):
        if source == self.main_scroll_area:
            return self._handle_scroll_area_events(event)
        return super().eventFilter(source, event)

    def _handle_scroll_area_events(self, event: QEvent):
        if event.type() == QEvent.Type.DragEnter:
            return self._handle_drag_enter(event)
        elif event.type() == QEvent.Type.DragLeave:
            return self._handle_drag_leave(event)
        elif event.type() == QEvent.Type.DragMove:
            return self._handle_drag_move(event)
        elif event.type() == QEvent.Type.Drop:
            return self._handle_drop(event)
        return False

    def _handle_drag_enter(self, event):
        should_accept = False
        if event.mimeData().hasUrls():
            supported_extensions = {ext for fmts in SUPPORTED_FORMATS.values() for ext in fmts}
            has_image = any(url.isLocalFile() and os.path.splitext(url.toLocalFile())[1].lower() in supported_extensions for url in event.mimeData().urls())
            if has_image:
                should_accept = True

        if should_accept:
            event.acceptProposedAction()
            self.main_scroll_area.setProperty("acceptingDrop", True)
            self.main_scroll_area.setStyleSheet(self._original_scroll_stylesheet + " QScrollArea#MainBatchScrollArea { border: 2px dashed #4CAF50; }")
        else:
            event.ignore()
        return True

    def _handle_drag_leave(self, event):
        if self.main_scroll_area.property("acceptingDrop"):
            self.main_scroll_area.setProperty("acceptingDrop", False)
            self.main_scroll_area.setStyleSheet(self._original_scroll_stylesheet)
        event.accept()
        return True

    def _handle_drag_move(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
        return True

    def _handle_drop(self, event):
        if self.main_scroll_area.property("acceptingDrop"):
            self.main_scroll_area.setProperty("acceptingDrop", False)
            self.main_scroll_area.setStyleSheet(self._original_scroll_stylesheet)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            supported_extensions = {ext for fmts in SUPPORTED_FORMATS.values() for ext in fmts}
            valid_image_paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile() and os.path.isfile(url.toLocalFile()) and os.path.splitext(url.toLocalFile())[1].lower() in supported_extensions]
            if valid_image_paths:
                process_and_start_batch_import(self, valid_image_paths)
            return True
        event.ignore()
        return True

    # --- Batch Processing ---
    def get_files_in_stack_folder(self):
        """Mengembalikan daftar path lengkap file di folder 'database/stack'."""
        folder_path = "database/stack"
        if not os.path.isdir(folder_path):
            return []
        try:
            return [os.path.join(folder_path, f)
                    for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f))]
        except Exception as e:
            return []

    def process_all_batches(self):
        active_panels_list = list(self.active_batch_panels.values())
        active_panels = [
            panel for panel in active_panels_list
            if panel and hasattr(panel, 'isWidgetType') and panel.isWidgetType() and \
               (not hasattr(self, 'animator') or not hasattr(self.animator, '_active_fade_outs') or \
                panel not in self.animator._active_fade_outs)
        ]

        candidate_panels = []
        for panel in active_panels:
            if hasattr(panel, 'batch_id') and panel.batch_id is not None and \
               hasattr(panel, 'sequential_batch_number'):
                candidate_panels.append(panel)
            else:
                pass


        if not candidate_panels:
            self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_NO_PROCESS, 4000, False)
            return

        target_folder = QFileDialog.getExistingDirectory(self, language_config.SELECT_OUTPUT_FOLDER_TITLE)
        if not target_folder:
            self.show_toast_requested.emit(language_config.OUTPUT_FOLDER_SELECTION_CANCELLED, 3000, False)
            return

        panels_to_actually_process = []
        for panel_candidate in candidate_panels:
            try:
                batch_id_to_check = str(panel_candidate.batch_id)
                images_in_db_for_panel = self.database_manager.get_images_by_batch(batch_id_to_check)
                
                if not images_in_db_for_panel: 
                   pass
                else:
                    panels_to_actually_process.append(panel_candidate)

            except Exception as db_val_e:
                pass
        
        if not panels_to_actually_process:
            self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_NO_PROCESS + " (after DB validation).", 4000, False)
            print(language_config.LOG_ALL_BATCH_ATTEMPTS_FINISHED + " (No valid batches found after DB check)")
            return

        total_batches_to_process = len(panels_to_actually_process)
       

        self.show_toast_requested.emit(
            language_config.UI_LABEL_BATCH_PROCESS_START.format(total_batches_to_process), None, False # Durasi None untuk toast default
        )
        QApplication.processEvents()
        print(language_config.LOG_BATCH_PROCESSING_START.format(total_batches_to_process))

        processed_and_saved_count = 0
        for i, batch_panel in enumerate(panels_to_actually_process, start=1):
            try:
                seq_num_for_msg = batch_panel.sequential_batch_number
                batch_id_for_msg = str(batch_panel.batch_id)

                print(language_config.LOG_PROCESSING_BATCH_DETAIL.format(
                    seq_num_for_msg, batch_id_for_msg,
                    i, total_batches_to_process
                ))

                files_before_processing = set(self.get_files_in_stack_folder())

                batch_panel.process_all_batch() 

                files_after_processing = set(self.get_files_in_stack_folder())
                newly_created_files = list(files_after_processing - files_before_processing)

                if newly_created_files:
                    output_file_to_move = newly_created_files[0]
                    if len(newly_created_files) > 1:
                        print(language_config.LOG_WARN_MULTIPLE_NEW_FILES.format(
                            batch_id_for_msg,
                            output_file_to_move
                        ))

                    print(language_config.LOG_BATCH_PROCESSED_NEW_OUTPUT.format(
                        batch_id_for_msg,
                        output_file_to_move
                    ))
                    move_success = self._move_single_batch_result(output_file_to_move, target_folder, seq_num_for_msg)
                    if move_success:
                        processed_and_saved_count += 1
                        toast_msg = language_config.UI_LABEL_BATCH_PROGRESS_DONE_SAVED.format(
                            seq_num_for_msg, i, total_batches_to_process
                        )
                    else:
                        toast_msg = language_config.UI_LABEL_BATCH_PROGRESS_SAVE_FAILED.format(
                            seq_num_for_msg, i, total_batches_to_process
                        )
                    self.show_toast_requested.emit(toast_msg, 3000, True) # Durasi 3s, closable
                else:
                    stack_folder_path = "database/stack"
                    print(language_config.LOG_BATCH_PROCESSED_NO_OUTPUT.format(
                        batch_id=batch_id_for_msg,
                        stack_folder=stack_folder_path
                    ))
                    toast_msg = language_config.UI_LABEL_BATCH_PROGRESS_NO_OUTPUT.format(
                        seq_num_for_msg, i, total_batches_to_process
                    )
                    self.show_toast_requested.emit(toast_msg, 3000, True)
                QApplication.processEvents()

            except Exception as e:
                error_detail_msg = str(e)
                print(language_config.LOG_ERROR_PROCESSING_BATCH.format(
                    getattr(batch_panel, 'batch_id', 'UNKNOWN'),
                    error_detail_msg
                ))
                QMessageBox.warning(self, language_config.BATCH_PROCESSING_ERROR_TITLE,
                                    language_config.BATCH_PROCESSING_ERROR_MESSAGE.format(
                                        getattr(batch_panel, 'sequential_batch_number', '?'),
                                        getattr(batch_panel, 'batch_id', 'UNKNOWN'),
                                        error_detail_msg
                                    ))
                toast_msg = language_config.UI_LABEL_BATCH_PROGRESS_ERROR.format(
                    getattr(batch_panel, 'sequential_batch_number', '?'), i, total_batches_to_process
                )
                self.show_toast_requested.emit(toast_msg, 5000, True) # Durasi 5s, closable
                QApplication.processEvents()

        folder_name_for_msg = os.path.basename(target_folder) if target_folder else "selected folder"
        if processed_and_saved_count == total_batches_to_process and total_batches_to_process > 0:
            final_message = language_config.UI_LABEL_BATCH_ALL_SUCCESS_SPECIFIC.format(
                total_batches_to_process, folder_name_for_msg
            )
        elif processed_and_saved_count > 0:
            final_message = language_config.UI_LABEL_BATCH_PARTIAL_SUCCESS_SPECIFIC.format(
                processed_and_saved_count, total_batches_to_process, folder_name_for_msg
            )
        elif total_batches_to_process > 0: 
            final_message = language_config.UI_LABEL_BATCH_NO_SUCCESS_SPECIFIC.format(
                folder_name_for_msg
            )
        else: 
             final_message = language_config.UI_LABEL_BATCH_NONE_PROCESSED


        self.show_toast_requested.emit(final_message, 7000, False)
        print(language_config.LOG_ALL_BATCH_ATTEMPTS_FINISHED)


    def _move_single_batch_result(self, source_file_path, target_folder, sequential_batch_num_for_naming=None):
        original_file_name_for_msg = os.path.basename(source_file_path) if source_file_path else "unknown_file"

        if not source_file_path or not os.path.exists(source_file_path):
            print(language_config.SOURCE_FILE_DOES_NOT_EXIST.format(source_file_path))
            return False

        if not target_folder or not os.path.isdir(target_folder):
            print(language_config.TARGET_FOLDER_INVALID.format(target_folder))
            QMessageBox.critical(self, language_config.BATCH_SAVE_ERROR_TITLE,
                                 language_config.TARGET_FOLDER_NOT_ACCESSIBLE.format(target_folder))
            return False

        original_file_name = os.path.basename(source_file_path)

        if sequential_batch_num_for_naming is not None:
            # base, ext = os.path.splitext(original_file_name) # Tidak perlu jika format baru sudah mencakup nama asli
            new_file_name = f"Batch_{sequential_batch_num_for_naming}_{original_file_name}"
        else:
            new_file_name = original_file_name

        destination_path = os.path.join(target_folder, new_file_name)

        try:
            counter = 1
            base_dest, ext_dest = os.path.splitext(new_file_name)
            # Perbaiki logika penanganan nama file duplikat agar base_dest tidak kehilangan bagian nomor batch awal
            temp_destination_path = destination_path
            while os.path.exists(temp_destination_path):
                temp_destination_path = os.path.join(target_folder, f"{base_dest}_{counter}{ext_dest}")
                counter += 1
            destination_path = temp_destination_path 

            shutil.move(source_file_path, destination_path)
            print(language_config.LOG_MOVE_SUCCESS.format(
                original_file_name_for_msg,
                destination_path
            ))
            return True
        except Exception as e:
            error_detail_msg = str(e)
            print(language_config.LOG_MOVE_FAILED.format(
                original_file_name_for_msg,
                target_folder,
                error_detail_msg
            ))
            QMessageBox.warning(self, language_config.MOVE_FILE_ERROR_TITLE,
                                language_config.COULD_NOT_SAVE_FILE_FOR_BATCH.format(
                                    original_file_name_for_msg, error=error_detail_msg
                                ))
            return False
    
    def handle_delete_individual_batch(self, batch_id):
        panel_to_delete = self.active_batch_panels.get(batch_id)
        panel_ref = weakref.ref(panel_to_delete) if panel_to_delete else None

        if not panel_to_delete:
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

    def handle_delete_all_batches(self):
        title = language_config.TITLE_BATCH_ALL_DELETE_BUTTON
        conn = None
        batch_defined_count = 0
        try:
            db_path = self.database_manager.db_path
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("SELECT COUNT(*) FROM batch_process")
            batch_defined_count = cursor.fetchone()[0]
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to check batch status: {e}")
            return
        finally:
            if conn:
                conn.close()

        if batch_defined_count == 0:
            QMessageBox.information(self, title, language_config.NO_DATA_BATCH_ALL_DELETE_BUTTON, QMessageBox.StandardButton.Ok)
            return

        message = language_config.CONFIRM_BATCH_ALL_DELETE_BUTTON.format(batch_defined_count)
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.batch_states.clear()
            panels_to_animate = list(self.active_batch_panels.values())
            panel_refs = [weakref.ref(p) for p in panels_to_animate]

            if not panels_to_animate:
                self._start_bulk_background_delete_process()
                return

            self._bulk_delete_animation_counter = len(panels_to_animate)
            delay_ms = 300

            for index, panel_ref in enumerate(panel_refs):
                QTimer.singleShot(index * delay_ms,
                                  lambda pref=panel_ref: self._trigger_single_bulk_fade_out(pref))

    def _start_bulk_background_delete_process(self):
        """Memulai proses penghapusan semua batch di background."""
        deleter = BatchDeleteProcess(self.database_manager, None, CACHE_DIR, self.thumbnail_threads)
        deleter.batch_deleted.connect(self.data_changed.emit)
        deleter.delete_all_batch()

    def _trigger_single_bulk_fade_out(self, panel_ref):
        """Memulai fade out untuk satu panel dalam proses bulk delete."""
        panel = panel_ref() if panel_ref else None
        if is_widget_valid(panel):
            fade_out(
                animator=self.animator,
                widget=panel,
                duration=300,
                on_finished_callback=lambda pref=panel_ref: self._bulk_delete_post_single_animation(pref)
            )
        else:
            # Widget sudah tidak valid, langsung cek animasi selesai
            self._check_bulk_delete_animations_finished()

    def _check_bulk_delete_animations_finished(self):
        """Dipanggil setiap kali satu animasi fade-out selesai saat delete all."""
        self._bulk_delete_animation_counter -= 1
        if self._bulk_delete_animation_counter <= 0:
            self._start_bulk_background_delete_process()

    def _bulk_delete_post_single_animation(self, panel_ref):
        panel = panel_ref() if panel_ref else None
        safe_hide_widget(panel)
        self._check_bulk_delete_animations_finished()

    def _individual_delete_post_animation(self, batch_id, panel_ref):
        """Callback setelah animasi fade-out individual selesai."""
        panel = panel_ref() if panel_ref else None
        safe_hide_widget(panel)
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
            pass
        
    # --- Batch Import ---
    def handle_batch_import_button(self):
        """Membuka dialog file dan memulai proses impor batch."""

        filter_parts = []
        all_supported_extensions = []
        
        for ext_list in SUPPORTED_FORMATS.values():
            all_supported_extensions.extend([f"*{ext}" for ext in ext_list])
        all_filter_str = f"All Supported Images ({' '.join(sorted(list(set(all_supported_extensions))))})"
        filter_parts.append(all_filter_str)
        
        for format_key, extensions in SUPPORTED_FORMATS.items():
            formatted_extensions = ' '.join([f"*{ext}" for ext in extensions])
            description = f"{format_key.upper()} Files"
            filter_parts.append(f"{description} ({formatted_extensions})")
        
        filter_parts.append("All Files (*)")
        
        file_dialog_filter = ';;'.join(filter_parts)
        
        image_paths, _ = QFileDialog.getOpenFileNames(
            self,
            language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, # Judul dialog
            "", 
            file_dialog_filter 
        )

        if image_paths:
            process_and_start_batch_import(self, image_paths)

    # --- Helper Methods ---
    def stop_thumbnail(self):
        """Menghentikan semua thread thumbnail yang sedang berjalan."""
        stop_process_thumbnails(self.thumbnail_threads)

    # --- Aggregated Progress ---
    @pyqtSlot()
    def _handle_item_imported(self):
        """Dipanggil setiap kali satu item berhasil diimpor oleh thread manapun."""
        self._total_processed_imports += 1
        self._update_aggregated_progress_toast() # Update tampilan progres

    @pyqtSlot(QThread)
    def _handle_thread_finished(self, thread_instance):
        """Dipanggil saat thread impor selesai."""
        if thread_instance in self._active_import_threads:
            self._active_import_threads.remove(thread_instance)
        else:
            print("Warning: Finished thread not found in active list.")

        if not self._active_import_threads:
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

    @pyqtSlot(str)
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

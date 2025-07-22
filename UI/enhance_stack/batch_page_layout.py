import os
import shutil
import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSpacerItem, QSizePolicy, QLabel
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QMessageBox, QFileDialog,
                              QApplication, QGraphicsOpacityEffect)
from PySide6.QtCore import (Signal, QPropertyAnimation, QEasingCurve, QEvent,
                          QTimer, Slot, QThread, Qt)
import weakref
from UI.enhance_stack.components.batch_page_layout.batch_layout import setup_main_panel
from UI.enhance_stack.components.batch_page_layout.combined_panel import CombinedPanel
from UI.enhance_stack.components.batch_page_layout.image_batch_management import BatchDeleteProcess, process_and_start_batch_import
from UI.enhance_stack.components.batch_page_layout.scrollable_error_dialog import ScrollableErrorDialog
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
    data_changed = Signal()
    show_toast_requested = Signal(str, object, bool)

    def __init__(self):
        super().__init__()
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
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)
        self.main_panel_container = QVBoxLayout()
        self._spacer_item = None
        self._placeholder_widget = None
        
        self.main_scroll_area = setup_main_panel(self.main_panel_container, SCROLL_AREA)
        self.main_scroll_area.setObjectName("MainBatchScrollArea")
        self.main_scroll_area.setAcceptDrops(True)
        self.main_scroll_area.installEventFilter(self)
        self._original_scroll_stylesheet = self.main_scroll_area.styleSheet()
        
        self.data_changed.connect(self.update_batch_view)
        
        self.update_batch_view()
        
        self.layout.addWidget(self.main_scroll_area)

    def update_batch_view(self):
        """
        Memperbarui tampilan daftar batch secara cerdas.
        Hanya menambah, menghapus, atau mempertahankan widget yang ada
        tanpa membangun ulang seluruh UI.
        """
        # 1. Dapatkan state dari database dan UI
        # Gunakan list untuk menjaga urutan dari database
        db_ids = self.database_manager.get_all_batch_ids()
        ui_ids = set(self.active_batch_panels.keys())
        
        # 2. Identifikasi batch yang perlu dihapus dari UI
        ids_to_remove = ui_ids - set(db_ids)
        for batch_id in ids_to_remove:
            panel_to_remove = self.active_batch_panels.pop(batch_id, None)
            if panel_to_remove:
                self.batch_states.pop(batch_id, None)
                
                # Hapus widget dari layout SECARA LANGSUNG
                self.main_panel_container.removeWidget(panel_to_remove)
                # Sembunyikan widget agar tidak terlihat sesaat sebelum benar-benar dihapus
                panel_to_remove.hide()
                # Jadwalkan penghapusan memori widget
                panel_to_remove.deleteLater()
                
        # 3. Identifikasi batch yang perlu ditambahkan ke UI
        # Pertahankan urutan dari database saat menambahkan
        ids_to_add = [bid for bid in db_ids if bid not in ui_ids]
        for batch_id in ids_to_add:
            # Simpan state saat ini dari panel lain sebelum membuat yang baru
            for bid, panel in self.active_batch_panels.items():
                try:
                    self.batch_states[bid] = panel.get_current_state()
                except Exception:
                    pass

            # Buat dan tambahkan panel baru
            new_panel = self.setup_combined_panel(batch_id)
            
            # Tambahkan widget baru ke layout. Jika ada spacer, tambahkan sebelum spacer.
            if self._spacer_item:
                # Sisipkan sebelum item terakhir (yaitu spacer)
                self.main_panel_container.insertWidget(self.main_panel_container.count() - 1, new_panel)
            else:
                self.main_panel_container.addWidget(new_panel)

            self._start_fade_in_animation(new_panel) # Beri animasi untuk panel baru

        # 4. Atur ulang nomor urut visual untuk semua panel yang ada
        self._reorder_visual_batch_numbers()

        # 5. Kelola tampilan placeholder atau spacer
        self._manage_placeholder_and_spacer()

    def _reorder_visual_batch_numbers(self):
        """Mengatur ulang label nomor urut (Batch #1, Batch #2, dst.) pada semua panel."""
        # Ambil semua widget CombinedPanel yang ada di layout
        panels_in_layout = []
        for i in range(self.main_panel_container.count()):
            widget = self.main_panel_container.itemAt(i).widget()
            # Pastikan itu adalah instance dari CombinedPanel
            if widget and isinstance(widget, CombinedPanel):
                panels_in_layout.append(widget)

        # Update nomor urut berdasarkan posisi mereka di layout
        for index, panel in enumerate(panels_in_layout):
            panel.update_sequential_number(index + 1)

    def _manage_placeholder_and_spacer(self):
        """Menampilkan placeholder jika tidak ada batch, atau spacer jika ada batch."""
        has_batches = len(self.active_batch_panels) > 0

        # Jika ada batch
        if has_batches:
            # Sembunyikan placeholder jika ada
            if self._placeholder_widget:
                self._placeholder_widget.hide()
                self._placeholder_widget.deleteLater()
                self._placeholder_widget = None

            # Pastikan spacer ada di bagian bawah
            if not self._spacer_item:
                self._spacer_item = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                self.main_panel_container.addSpacerItem(self._spacer_item)
        
        else:
            # Hapus spacer jika ada
            if self._spacer_item:
                self.main_panel_container.removeItem(self._spacer_item)
                self._spacer_item = None
            
            # Tampilkan placeholder jika belum ada
            if not self._placeholder_widget:
                self._placeholder_widget = self._create_placeholder_widget()
                self.main_panel_container.addWidget(self._placeholder_widget, 0, Qt.AlignmentFlag.AlignCenter)

    def _create_placeholder_widget(self):
        """Membuat widget placeholder untuk ditampilkan saat tidak ada batch."""
        try:
            format_keys = SUPPORTED_FORMATS.keys()
            supported_formats_text = ", ".join(sorted(list(format_keys)))
        except NameError:
            supported_formats_text = "jpg, png, tiff" 
        except Exception as e:
            supported_formats_text = "(Gagal memuat format)"

        html_text = f"""
        <p align="center">
            {language_config.PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES}<br><br>
            <span style="color:#666;">{language_config.SUPPORTED_IMAGE_EXTENSION}:</span><br>
            {supported_formats_text}
        </p>
        """
        placeholder_label = QLabel()
        placeholder_label.setTextFormat(Qt.TextFormat.RichText)
        placeholder_label.setText(html_text)
        placeholder_label.setWordWrap(True)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #777777; font-size: 21px; border: none;
                background-color: transparent; padding: 20px;
            }
        """)
        placeholder_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        
        # [BARU] Buat layout vertikal untuk memusatkan placeholder
        container_widget = QWidget()
        v_layout = QVBoxLayout(container_widget)
        v_layout.addStretch(1)
        v_layout.addWidget(placeholder_label)
        v_layout.addStretch(1)
        
        return container_widget

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

    def setup_combined_panel(self, batch_id=None):
        initial_state = self.batch_states.get(batch_id, {})
        combined_panel = CombinedPanel(
            database_manager=self.database_manager,
            batch_id=batch_id,
            parent=self,
            thumbnail_threads=self.thumbnail_threads,
            thumbnail_placeholders=self.thumbnail_placeholders,
            initial_state=initial_state,
            # sequential_batch_number akan diatur nanti
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
        """
        Memproses semua batch panel yang aktif, menangani error secara non-blocking,
        dan menampilkan ringkasan error di akhir.
        """
        # Bagian 1: Mengumpulkan dan memvalidasi panel yang akan diproses
        active_panels_list = list(self.active_batch_panels.values())
        active_panels = []
        for panel in active_panels_list:
            try:
                if panel and hasattr(panel, 'isWidgetType') and panel.isWidgetType() and \
                    (not hasattr(self, 'animator') or not hasattr(self.animator, '_active_fade_outs') or \
                        panel not in self.animator._active_fade_outs):
                    active_panels.append(panel)
            except RuntimeError:
                # Widget mungkin sudah dihapus, ini aman untuk diabaikan
                print(f"RuntimeError: Panel {panel} has been deleted.")
            except Exception as e:
                print(f"Unexpected error while filtering panel {panel}: {e}")

        candidate_panels = []
        for panel in active_panels:
            if hasattr(panel, 'batch_id') and panel.batch_id is not None and \
                hasattr(panel, 'sequential_batch_number'):
                candidate_panels.append(panel)

        if not candidate_panels:
            self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_NO_PROCESS, 4000, False)
            return

        # Bagian 2: Mendapatkan folder tujuan dari pengguna
        target_folder = QFileDialog.getExistingDirectory(self, language_config.SELECT_OUTPUT_FOLDER_TITLE)
        if not target_folder:
            self.show_toast_requested.emit(language_config.OUTPUT_FOLDER_SELECTION_CANCELLED, 3000, False)
            return

        # Bagian 3: Validasi akhir terhadap database
        panels_to_actually_process = []
        for panel_candidate in candidate_panels:
            try:
                batch_id_to_check = str(panel_candidate.batch_id)
                images_in_db_for_panel = self.database_manager.get_images_by_batch(batch_id_to_check)
                if images_in_db_for_panel:
                    panels_to_actually_process.append(panel_candidate)
            except Exception as db_val_e:
                print(f"Error validating batch {panel_candidate.batch_id} against DB: {db_val_e}")
                pass # Lanjutkan meskipun ada error validasi DB
        
        if not panels_to_actually_process:
            self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_NO_PROCESS + " (after DB validation).", 4000, False)
            print(language_config.LOG_ALL_BATCH_ATTEMPTS_FINISHED + " (No valid batches found after DB check)")
            return

        # Bagian 4: Inisialisasi proses utama
        total_batches_to_process = len(panels_to_actually_process)
        self.show_toast_requested.emit(
            language_config.UI_LABEL_BATCH_PROCESS_START.format(total_batches_to_process), None, False
        )
        QApplication.processEvents()
        print(language_config.LOG_BATCH_PROCESSING_START.format(total_batches_to_process))

        processed_and_saved_count = 0
        failed_batches_summary = []
        
        # Bagian 5: Loop pemrosesan utama per batch
        for i, batch_panel in enumerate(panels_to_actually_process, start=1):
            try:
                seq_num_for_msg = batch_panel.sequential_batch_number
                batch_id_for_msg = str(batch_panel.batch_id)

                print(language_config.LOG_PROCESSING_BATCH_DETAIL.format(
                    seq_num_for_msg, batch_id_for_msg, i, total_batches_to_process
                ))

                files_before_processing = set(self.get_files_in_stack_folder())
                batch_panel.process_all_batch() # Panggilan inti untuk memproses
                files_after_processing = set(self.get_files_in_stack_folder())
                newly_created_files = list(files_after_processing - files_before_processing)

                if newly_created_files:
                    output_file_to_move = newly_created_files[0]
                    if len(newly_created_files) > 1:
                        print(language_config.LOG_WARN_MULTIPLE_NEW_FILES.format(
                            batch_id_for_msg, output_file_to_move
                        ))
                    
                    move_success = self._move_single_batch_result(output_file_to_move, target_folder)
                    if move_success:
                        processed_and_saved_count += 1
                        toast_msg = language_config.UI_LABEL_BATCH_PROGRESS_DONE_SAVED.format(
                            seq_num_for_msg, i, total_batches_to_process
                        )
                    else:
                        toast_msg = language_config.UI_LABEL_BATCH_PROGRESS_SAVE_FAILED.format(
                            seq_num_for_msg, i, total_batches_to_process
                        )
                    self.show_toast_requested.emit(toast_msg, 3000, True)
                else:
                    stack_folder_path = "database/stack"
                    print(language_config.LOG_BATCH_PROCESSED_NO_OUTPUT.format(
                        batch_id=batch_id_for_msg, stack_folder=stack_folder_path
                    ))
                    toast_msg = language_config.UI_LABEL_BATCH_PROGRESS_NO_OUTPUT.format(
                        seq_num_for_msg, i, total_batches_to_process
                    )
                    self.show_toast_requested.emit(toast_msg, 3000, True)
                
                QApplication.processEvents()

            except Exception as e:
                error_detail_msg = str(e)
                seq_num = getattr(batch_panel, 'sequential_batch_number', '?')
                batch_id = getattr(batch_panel, 'batch_id', 'UNKNOWN')

                print(language_config.LOG_ERROR_PROCESSING_BATCH.format(batch_id, error_detail_msg))
                
                # 3. Tambahkan detail error ke dalam list untuk laporan akhir.
                failed_batches_summary.append({
                    "seq": seq_num,
                    "id": batch_id,
                    "error": error_detail_msg
                })

                # Tetap tampilkan notifikasi toast non-blocking untuk feedback instan.
                toast_msg = language_config.UI_LABEL_BATCH_PROGRESS_ERROR.format(
                    seq_num, i, total_batches_to_process
                )
                self.show_toast_requested.emit(toast_msg, 5000, True)
                QApplication.processEvents() # Pastikan toast ditampilkan
                # Loop akan otomatis berlanjut ke iterasi berikutnya (batch selanjutnya)
                # ========================================================================

        # Bagian 6: Memberikan pesan ringkasan akhir melalui toast
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

        # 4. Tampilkan ringkasan semua error jika ada, SETELAH SEMUA PROSES SELESAI
        if failed_batches_summary:
            error_report_title = language_config.BATCH_PROCESSING_ERROR_REPORT_TITLE
            
            num_failed = len(failed_batches_summary)
            # Teks pengantar yang tidak di-scroll
            intro_message = language_config.BATCH_PROCESSING_ERROR_REPORT_INTRO.format(
                num_failed=num_failed,
                num_total=total_batches_to_process
            )
            
            # Teks detail yang akan masuk ke area scroll
            error_details = "\n\n".join([
                language_config.BATCH_PROCESSING_ERROR_REPORT_ITEM.format(
                    seq=err['seq'], 
                    id=err['id'], 
                    error=err['error']
                )
                for err in failed_batches_summary
            ])

            # Pastikan kelas ScrollableErrorDialog sudah diimpor atau ada di file yang sama
            error_dialog = ScrollableErrorDialog(
                title=error_report_title,
                intro_text=intro_message,
                detailed_text=error_details,
                parent=self
            )
            error_dialog.exec_() # Tampilkan dialog secara modal
            
    def _move_single_batch_result(self, source_file_path, target_folder):
        """
        Memindahkan file hasil ke folder target, hanya menggunakan nama file asli.
        Jika file dengan nama yang sama sudah ada, tambahkan akhiran "_1", "_2", dst.
        """
        if not source_file_path or not os.path.exists(source_file_path):
            print(language_config.SOURCE_FILE_DOES_NOT_EXIST.format(source_file_path))
            return False

        if not target_folder or not os.path.isdir(target_folder):
            print(language_config.TARGET_FOLDER_INVALID.format(target_folder))
            QMessageBox.critical(self, language_config.BATCH_SAVE_ERROR_TITLE,
                                 language_config.TARGET_FOLDER_NOT_ACCESSIBLE.format(target_folder))
            return False

        original_file_name = os.path.basename(source_file_path)
        destination_path = os.path.join(target_folder, original_file_name)

        try:
            # Jika file tujuan sudah ada, cari nama baru yang tersedia.
            if os.path.exists(destination_path):
                base, ext = os.path.splitext(original_file_name)
                counter = 1
                while os.path.exists(destination_path):
                    new_file_name = f"{base}_{counter}{ext}"
                    destination_path = os.path.join(target_folder, new_file_name)
                    counter += 1
            
            # Pindahkan file setelah nama tujuan yang valid ditemukan
            shutil.move(source_file_path, destination_path)
            
            print(language_config.LOG_MOVE_SUCCESS.format(original_file_name, destination_path))
            return True

        except Exception as e:
            error_detail_msg = str(e)
            print(language_config.LOG_MOVE_FAILED.format(original_file_name, target_folder, error_detail_msg))
            QMessageBox.warning(self, language_config.MOVE_FILE_ERROR_TITLE,
                                language_config.COULD_NOT_SAVE_FILE_FOR_BATCH.format(original_file_name, error=error_detail_msg))
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
    @Slot()
    def _handle_item_imported(self):
        """Dipanggil setiap kali satu item berhasil diimpor oleh thread manapun."""
        self._total_processed_imports += 1
        self._update_aggregated_progress_toast() # Update tampilan progres

    @Slot(QThread)
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

    @Slot(int, int)
    def _update_import_progress_toast(self, progress_percent, items_left):
        """Update teks toast dengan informasi progres impor."""
        progress_msg = language_config.UPDATE_PROGRESS_BAR_STATUS.format(progress_percent, items_left)
        
        self.show_toast_requested.emit(progress_msg, None, True) 

    @Slot(str)
    def on_batch_import_error(self, item_path, error_message):
        self._total_pending_imports -= 1
        if self._total_pending_imports < 0 : self._total_pending_imports = 0
        self._update_aggregated_progress_toast()
        QMessageBox.warning(self, "Batch Import Error", f"Failed import '{os.path.basename(item_path)}':\n{error_message}")

    @Slot(int)
    def _on_batch_import_complete(self, total_items_processed):
        """Dipanggil saat thread impor batch selesai."""
        completion_msg = language_config.ON_IMPORT_COMPLETE_STATUS
        self.show_toast_requested.emit(completion_msg, 3000, False) 

        self.data_changed.emit()

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QStackedWidget
from PySide6.QtCore import Slot, Signal, QThread

from UI.panorama.display_area.display_panel import DisplayPanel
from UI.panorama.logic.panorama_worker import PanoramaWorker
from UI.panorama.workflow_area.workflow_panel import WorkflowPanel
from UI.resources.animation.animation_manager import HeightAnimator, SlideDirection, StackedWidgetAnimator
from UI.resources.animation.slide import slide


class WorkingLeftPanel(QWidget):
    rename_project_requested = Signal(int, str)

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.cached_alignment_result = None
        self.cached_projection_result = None

        self.current_project_id = None
        self.projects_exist = False
        self.latest_successful_stage = "grid"
        self.last_preview_info = None 
        self.slide_animator = StackedWidgetAnimator()
        self.height_animator = HeightAnimator(self)

        # --- Setup UI ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        self.display_panel = DisplayPanel()
        self.workflow_stack = QStackedWidget()
        self.workflow_panel = WorkflowPanel()
        self.workflow_placeholder = QWidget()
        self.workflow_stack.addWidget(self.workflow_panel)
        self.workflow_stack.addWidget(self.workflow_placeholder)
        main_layout.addWidget(self.display_panel, 1)
        main_layout.addWidget(self.workflow_stack, 0)
        self.workflow_stack.setCurrentWidget(self.workflow_placeholder)
        self.workflow_stack.setFixedHeight(0)
        self.thread = None
        self.worker = None
        self._connect_signals()

    def _connect_signals(self):
        """Menghubungkan sinyal dari anak ke kontroler ini."""
        # Dari DisplayPanel
        self.display_panel.rename_project_requested.connect(self._on_rename_request)
        self.display_panel.images_to_import_selected.connect(self._on_images_imported)
        self.display_panel.images_to_delete_selected.connect(self._on_images_deleted)
        self.display_panel.back_to_grid_requested.connect(self._on_back_to_grid_request)
        self.display_panel.back_to_preview_requested.connect(self._on_back_to_preview_request)

        # Dari WorkflowPanel
        self.workflow_panel.setting_changed.connect(self._on_workflow_setting_changed)
        self.workflow_panel.preview_requested.connect(self._on_preview_requested)

    @Slot(int, str)
    def update_display_for_project(self, project_id, project_name):
        self.current_project_id = project_id
        self.latest_successful_stage = "grid"
        self.last_preview_info = None # <<< MODIFIKASI: Reset memori saat ganti proyek
        self.cached_alignment_result = None
        self.cached_projection_result = None

        image_paths = self.database_manager.get_images_for_project(project_id)
        settings = self.database_manager.get_project_workflow_settings(project_id)
        
        self.display_panel.show_grid_view() 
        self.display_panel.load_project(project_id, project_name, image_paths)

        if image_paths:
            self.workflow_panel.load_settings(settings)
            self.workflow_panel.update_workflow_stage("grid", has_images=True)
            self.workflow_panel.tab_widget.setCurrentIndex(0)
            
            if self.workflow_stack.height() == 0:
                target_height = self.workflow_panel.sizeHint().height()
                if target_height <= 0: target_height = 200 # Fallback

                self.height_animator.animate_height(
                    target_widget=self.workflow_stack,
                    end_height=target_height,
                    duration=350
                )
                slide(
                    animator=self.slide_animator,
                    stack_widget=self.workflow_stack,
                    target=self.workflow_panel,
                    direction=SlideDirection.UP,
                    duration=350
                )
        else:
            if self.workflow_stack.height() > 0:
                self.height_animator.animate_height(
                    target_widget=self.workflow_stack,
                    end_height=0,
                    duration=300
                )
                slide(
                    animator=self.slide_animator,
                    stack_widget=self.workflow_stack,
                    target=self.workflow_placeholder,
                    direction=SlideDirection.DOWN,
                    duration=300
                )

    @Slot()
    def clear_display(self):
        self.current_project_id = None
        self.last_preview_info = None 
        self.cached_alignment_result = None
        self.cached_projection_result = None
        self.display_panel.clear_display(no_projects_exist=(not self.projects_exist))
        
        if self.workflow_stack.height() > 0:
            self.height_animator.animate_height(
                target_widget=self.workflow_stack,
                end_height=0,
                duration=300
            )
            slide(
                animator=self.slide_animator,
                stack_widget=self.workflow_stack,
                target=self.workflow_placeholder,
                direction=SlideDirection.DOWN,
                duration=300
            )

    @Slot(bool)
    def on_project_existence_changed(self, exists):
        self.projects_exist = exists
        if not self.current_project_id:
            self.clear_display()

    @Slot(int, str)
    def _on_rename_request(self, current_name):
        self.rename_project_requested.emit(self.current_project_id, current_name)

    @Slot(list)
    def _on_images_imported(self, file_paths):
        success = self.database_manager.add_images_to_project(
            self.current_project_id, file_paths
        )
        if success:
            # Muat ulang data untuk proyek saat ini
            project_name = self.display_panel.project_name
            self.update_display_for_project(self.current_project_id, project_name)
        else:
            QMessageBox.critical(self, "Database Error", "Failed to save images.")

    @Slot(list)
    def _on_images_deleted(self, paths_to_delete):
        success = self.database_manager.delete_images_from_project(
            self.current_project_id, paths_to_delete
        )
        if success:
            project_name = self.display_panel.project_name
            self.update_display_for_project(self.current_project_id, project_name)
        else:
            QMessageBox.critical(self, "Database Error", "Failed to delete images.")

    @Slot(str, str)
    def _on_workflow_setting_changed(self, setting_key, value): 
        """Menyimpan perubahan dan MENG-INVALIDASI CACHE yang relevan."""
        # Daftar pengaturan untuk setiap tahap
        alignment_settings = ['align_algorithm', 'akaze_threshold', 'orb_nfeatures'] # Tambahkan setting alignment lain
        projection_settings = ['projection_type', 'projection_scale'] # Tambahkan setting proyeksi lain

        # Logika invalidasi
        if setting_key in alignment_settings:
            print("INFO: Pengaturan alignment berubah. Membersihkan cache alignment dan projection.")
            self.cached_alignment_result = None
            self.cached_projection_result = None
        elif setting_key in projection_settings:
            print("INFO: Pengaturan proyeksi berubah. Membersihkan cache projection.")
            self.cached_projection_result = None
            
        # Simpan perubahan ke DB seperti biasa
        if self.current_project_id:
            self.database_manager.save_project_workflow_setting(
                self.current_project_id, setting_key, value
            )

    @Slot()
    def _on_back_to_grid_request(self):
        self.display_panel.show_grid_view()
        
        if self.last_preview_info:
            self.display_panel.set_restore_button_visibility(True)

        image_paths = self.database_manager.get_images_for_project(
            self.current_project_id
        )
        self.workflow_panel.update_workflow_stage(
            self.latest_successful_stage, has_images=bool(image_paths)
        )
        
    @Slot()
    def _on_back_to_preview_request(self):
        if not self.last_preview_info:
            return

        stage, message, tab_index = self.last_preview_info

        if stage == "aligned":
            self.display_panel.show_preview_result(message)
        else: 
            self.display_panel.show_preview_message(message)

        image_paths = self.database_manager.get_images_for_project(self.current_project_id)
        self.workflow_panel.update_workflow_stage(stage, has_images=bool(image_paths))
        self.workflow_panel.tab_widget.setCurrentIndex(tab_index)

    @Slot(str)
    def _on_preview_requested(self, stage_name):
        """Menangani permintaan preview dengan progress bar modern."""
        self.progress_timer.stop()
        
        simulations = {
            "alignment": {"title": "Aligning Images", "delay": 2500, "callback": self._on_alignment_finished},
            "projection": {"title": "Applying Projection", "delay": 1500, "callback": self._on_projection_finished},
            "blending": {"title": "Blending Panorama", "delay": 2000, "callback": self._on_blending_finished},
        }
        
        sim = simulations.get(stage_name)
        if not sim: return

        print(f"SIMULASI: Memulai {sim['title']}...")
        
        self._current_process_callback = sim["callback"]
        self._current_process_title = sim["title"]
        self.progress_value = 0
        
        self.display_panel.show_processing_view(self._current_process_title)
        
        interval = sim["delay"] / 100.0
        self.progress_timer.start(int(interval))

    @Slot(int, str)
    def _on_real_progress_update(self, percentage, message):
        """Menerima sinyal dari worker dan mengupdate progress bar."""
        self.display_panel.update_processing_progress(message, percentage)


    @Slot(str, object)
    def _on_stitching_finished(self, stage_name, result):
        """Menangani hasil dan MENYIMPANNYA KE CACHE."""
        print(f"PROSES NYATA: {stage_name} selesai. Menyimpan hasil ke cache.")

        # BARU: Simpan hasil ke variabel cache yang sesuai
        if stage_name == "alignment":
            self.cached_alignment_result = result
            # Penting: Jika alignment dijalankan ulang, cache proyeksi jadi tidak valid
            self.cached_projection_result = None 
            self._on_alignment_finished(result)
        elif stage_name == "projection":
            self.cached_projection_result = result
            self._on_projection_finished(result)
        elif stage_name == "blending":
            # Hasil blending adalah final, tidak perlu di-cache untuk tahap selanjutnya
            self._on_blending_finished(result)
            
        self.cleanup_thread()
    
    @Slot(str)
    def _on_stitching_error(self, error_message):
        print(f"ERROR: {error_message}")
        QMessageBox.critical(self, "Processing Error", error_message)
        self._on_back_to_grid_request() 
        self.cleanup_thread()

    def cleanup_thread(self):
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait()
        self.thread = None
        self.worker = None

    
    @Slot(str)
    def _on_preview_requested(self, stage_name):
        """
        MODIFIKASI: Menangani permintaan preview dengan menjalankan worker di thread baru.
        """
        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "Process Running", "Another process is already running. Please wait.")
            return

        # 1. Kumpulkan data yang dibutuhkan
        image_paths = self.database_manager.get_images_for_project(self.current_project_id)
        if not image_paths or len(image_paths) < 2:
            QMessageBox.information(self, "Not Enough Images", "You need at least two images to create a panorama.")
            return
            
        settings = self.database_manager.get_project_workflow_settings(self.current_project_id)
        
        # MODIFIKASI UTAMA: Tentukan data cache mana yang akan digunakan
        align_cache = None
        proj_cache = None

        if stage_name == "projection":
            if self.cached_alignment_result is None:
                QMessageBox.information(self, "Langkah Dibutuhkan", 
                                        "Silakan jalankan tahap 'Alignment' terlebih dahulu sebelum melihat pratinjau proyeksi.")
                return
            align_cache = self.cached_alignment_result
            
        elif stage_name == "blending":
            if self.cached_projection_result is not None:
                proj_cache = self.cached_projection_result
            elif self.cached_alignment_result is not None:
                align_cache = self.cached_alignment_result
            else:
                QMessageBox.information(self, "Langkah Dibutuhkan", 
                                        "Silakan jalankan tahap 'Alignment' dan 'Projection' terlebih dahulu.")
                return
        
        titles = {
            "alignment": "Aligning Images",
            "projection": "Applying Projection",
            "blending": "Blending Panorama",
        }
        
        # 2. Siapkan UI untuk processing
        self.display_panel.show_processing_view(titles.get(stage_name, "Processing..."))
        
        # Buat thread dan worker dengan data cache yang relevan
        self.thread = QThread()
        self.worker = PanoramaWorker(
            image_paths=image_paths,
            settings=settings,
            target_stage=stage_name,
            # Teruskan cache ke worker
            cached_alignment=align_cache,
            cached_projection=proj_cache
        )
        self.worker.moveToThread(self.thread)

        # 4. Hubungkan sinyal dari worker ke slot di kelas ini
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_stitching_finished)
        self.worker.error.connect(self._on_stitching_error)
        self.worker.progress_updated.connect(self._on_real_progress_update)
        
        # 5. Mulai thread
        self.thread.start()

    def _on_alignment_finished(self, aligned_data): # MODIFIKASI: Terima 'aligned_data'
        # 'aligned_data' sekarang adalah hasil nyata dari run_akaze_alignment, dll.
        # Untuk tujuan tampilan, kita mungkin masih butuh representasi visual.
        # Mari asumsikan untuk saat ini kita hanya menampilkan pesan sukses.
        # Di dunia nyata, `aligned_data` mungkin berisi gambar debug atau informasi homografi.
        message = "Alignment process completed successfully."
        self.last_preview_info = ("aligned", message, 0) # 'message' bisa diganti dengan 'aligned_data' jika bisa ditampilkan

        self.display_panel.show_preview_result(message) # Mungkin perlu fungsi baru seperti show_preview_image(image)
        self.latest_successful_stage = "aligned"
        
        image_paths = self.database_manager.get_images_for_project(self.current_project_id)
        self.workflow_panel.update_workflow_stage("aligned", has_images=bool(image_paths))
        self.workflow_panel.tab_widget.setCurrentIndex(1)

    def _on_projection_finished(self, projected_data): # MODIFIKASI: Terima 'projected_data'
        # 'projected_data' adalah hasil dari run_projection
        message = "Projection process completed successfully."
        self.last_preview_info = ("projected", message, 1)

        self.display_panel.show_preview_message(message)
        self.latest_successful_stage = "projected"

        image_paths = self.database_manager.get_images_for_project(self.current_project_id)
        self.workflow_panel.update_workflow_stage("projected", has_images=bool(image_paths))
        self.workflow_panel.tab_widget.setCurrentIndex(2)

    def _on_blending_finished(self, final_image): # MODIFIKASI: Terima 'final_image'
        # 'final_image' adalah gambar panorama (objek NumPy array dari OpenCV)
        message = "Panorama created successfully!"
        self.last_preview_info = ("blended", final_image, 2) # Simpan gambar asli di memori

        # Idealnya, DisplayPanel punya metode untuk menampilkan gambar NumPy secara langsung
        # self.display_panel.show_final_panorama(final_image) 
        # Untuk saat ini, kita tetap tampilkan pesan
        self.display_panel.show_preview_message(message)
        self.latest_successful_stage = "blended"
        
        image_paths = self.database_manager.get_images_for_project(self.current_project_id)
        self.workflow_panel.update_workflow_stage("blended", has_images=bool(image_paths))
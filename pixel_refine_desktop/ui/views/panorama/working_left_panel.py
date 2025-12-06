from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QStackedWidget
from PySide6.QtCore import Slot, Signal, QThread
import cv2
import numpy as np
import os
import pickle  # Untuk menyimpan objek Python (termasuk NumPy array) ke disk
import hashlib # Untuk membuat nama file yang unik

from pixel_refine_desktop.ui.views.panorama.display_area.display_panel import DisplayPanel
from pixel_refine_desktop.ui.views.panorama.logic.panorama_worker import PanoramaWorker
from pixel_refine_desktop.ui.views.panorama.workflow_area.workflow_panel import WorkflowPanel
from pixel_refine_desktop.ui.resources.animations.animation_manager import HeightAnimator, SlideDirection, StackedWidgetAnimator
from pixel_refine_desktop.ui.resources.animations.slide import slide

class WorkingLeftPanel(QWidget):
    """
    Panel kiri yang mengelola tampilan gambar proyek, alur kerja (workflow),
    dan memulai proses stitching panorama.
    """
    rename_project_requested = Signal(int, str)

    # =========================================================================
    # === 1. Inisialisasi dan Pengaturan UI ===
    # =========================================================================

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager

        # --- State Internal dan Cache ---
        self.current_project_id = None
        self.projects_exist = False
        self.latest_successful_stage = "grid"
        self.last_preview_info = None
        self.cached_alignment_result = None
        self.cached_alignment_data = None      # <-- menjadi ini, untuk menyimpan seluruh paket
        self.cached_projection_result = None
        
        # --- Worker Thread ---
        self.thread = None
        self.worker = None

        # --- Animator ---
        self.slide_animator = StackedWidgetAnimator()
        self.height_animator = HeightAnimator(self)

        # --- Setup UI ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        self.display_panel = DisplayPanel()
        self.workflow_stack = QStackedWidget()
        self.workflow_panel = WorkflowPanel()
        self.workflow_placeholder = QWidget() # Placeholder untuk saat panel disembunyikan
        
        self.workflow_stack.addWidget(self.workflow_panel)
        self.workflow_stack.addWidget(self.workflow_placeholder)
        
        main_layout.addWidget(self.display_panel, 1)
        main_layout.addWidget(self.workflow_stack, 0)
        
        self.workflow_stack.setCurrentWidget(self.workflow_placeholder)
        self.workflow_stack.setFixedHeight(0)
        
        self._connect_signals()

    def _connect_signals(self):
        """Menghubungkan sinyal dari widget anak ke slot di kelas ini."""
        # Dari DisplayPanel
        self.display_panel.rename_project_requested.connect(self._on_rename_request)
        self.display_panel.images_to_import_selected.connect(self._on_images_imported)
        self.display_panel.images_to_delete_selected.connect(self._on_images_deleted)
        self.display_panel.back_to_grid_requested.connect(self._on_back_to_grid_request)
        self.display_panel.back_to_preview_requested.connect(self._on_back_to_preview_request)

        # Dari WorkflowPanel
        self.workflow_panel.setting_changed.connect(self._on_workflow_setting_changed)
        self.workflow_panel.preview_requested.connect(self._on_preview_requested)

    # =========================================================================
    # === 2. Slot Publik dan Manajemen State Utama ===
    # =========================================================================

    @Slot(int, str)
    def update_display_for_project(self, project_id, project_name):
        """Memuat dan menampilkan data untuk proyek yang dipilih."""
        self.current_project_id = project_id
        self.latest_successful_stage = "grid"
        # Reset cache dan state saat berpindah proyek
        self.last_preview_info = None
        self.cached_alignment_result = None
        self.cached_projection_result = None

        image_paths = self.database_manager.get_images_for_project(project_id)
        settings = self.database_manager.get_project_workflow_settings(project_id)
        
        self.display_panel.show_grid_view() 
        self.display_panel.load_project(project_id, project_name, image_paths)

        if image_paths:
            # Tampilkan panel workflow jika ada gambar
            self.workflow_panel.load_settings(settings)
            self.workflow_panel.update_workflow_stage("grid", has_images=True)
            self.workflow_panel.tab_widget.setCurrentIndex(0)
            
            if self.workflow_stack.height() == 0:
                target_height = self.workflow_panel.sizeHint().height() or 200
                self.height_animator.animate_height(self.workflow_stack, target_height, 350)
                slide(self.slide_animator, self.workflow_stack, self.workflow_panel, SlideDirection.UP, 350)
        else:
            # Sembunyikan panel workflow jika tidak ada gambar
            if self.workflow_stack.height() > 0:
                self.height_animator.animate_height(self.workflow_stack, 0, 300)
                slide(self.slide_animator, self.workflow_stack, self.workflow_placeholder, SlideDirection.DOWN, 300)

    @Slot()
    def clear_display(self):
        """Membersihkan tampilan saat tidak ada proyek yang dipilih."""
        self.current_project_id = None
        self.last_preview_info = None 
        self.cached_alignment_result = None
        self.cached_projection_result = None
        
        self.display_panel.clear_display(no_projects_exist=(not self.projects_exist))
        
        if self.workflow_stack.height() > 0:
            self.height_animator.animate_height(self.workflow_stack, 0, 300)
            slide(self.slide_animator, self.workflow_stack, self.workflow_placeholder, SlideDirection.DOWN, 300)

    @Slot(bool)
    def on_project_existence_changed(self, exists):
        """Dipanggil saat ada/tidaknya proyek berubah (misal: proyek terakhir dihapus)."""
        self.projects_exist = exists
        if not self.current_project_id:
            self.clear_display()

    # =========================================================================
    # === 3. Penanganan Aksi dari Child Widget (Slots) ===
    # =========================================================================

    # --- 3a. Manajemen Proyek & Gambar ---
    
    @Slot(int, str)
    def _on_rename_request(self, current_name):
        """Meneruskan permintaan penggantian nama proyek ke parent widget."""
        self.rename_project_requested.emit(self.current_project_id, current_name)

    @Slot(list)
    def _on_images_imported(self, file_paths):
        """Menangani penambahan gambar baru ke proyek."""
        self._invalidate_alignment_cache() # Hapus cache sebelum operasi DB
        success = self.database_manager.add_images_to_project(self.current_project_id, file_paths)
        if success:
            project_name = self.display_panel.project_name
            self.update_display_for_project(self.current_project_id, project_name)
        else:
            QMessageBox.critical(self, "Database Error", "Failed to save images.")

    @Slot(list)
    def _on_images_deleted(self, paths_to_delete):
        """Menangani penghapusan gambar dari proyek."""
        self._invalidate_alignment_cache() # Hapus cache sebelum operasi DB
        success = self.database_manager.delete_images_from_project(self.current_project_id, paths_to_delete)
        if success:
            project_name = self.display_panel.project_name
            self.update_display_for_project(self.current_project_id, project_name)
        else:
            QMessageBox.critical(self, "Database Error", "Failed to delete images.")

    # --- 3b. Navigasi UI ---

    @Slot()
    def _on_back_to_grid_request(self):
        """Kembali ke tampilan grid gambar."""
        self.display_panel.show_grid_view()
        if self.last_preview_info:
            self.display_panel.set_restore_button_visibility(True)
        
        has_images = bool(self.database_manager.get_images_for_project(self.current_project_id))
        self.workflow_panel.update_workflow_stage(self.latest_successful_stage, has_images)
        
    @Slot()
    def _on_back_to_preview_request(self):
        """Mengembalikan tampilan ke hasil pratinjau terakhir."""
        if not self.last_preview_info:
            return

        stage, data, tab_index = self.last_preview_info

        if isinstance(data, np.ndarray):
            self.display_panel.display_zoomable_image(data)
        elif isinstance(data, str):
            self.display_panel.show_preview_message(data)

        has_images = bool(self.database_manager.get_images_for_project(self.current_project_id))
        self.workflow_panel.update_workflow_stage(stage, has_images)
        self.workflow_panel.tab_widget.setCurrentIndex(tab_index)

    # --- 3c. Pengaturan Workflow ---
    
    @Slot(str, str)
    def _on_workflow_setting_changed(self, setting_key, value): 
        """Menyimpan perubahan pengaturan dan membatalkan validasi cache yang relevan."""
        # Definisikan kedua daftar pengaturan di sini
        alignment_settings = ['align_algorithm', 'akaze_threshold', 'orb_nfeatures']
        projection_settings = ['projection_type', 'projection_scale'] # <-- TAMBAHKAN BARIS INI

        if setting_key in alignment_settings:
            print("INFO: Pengaturan alignment berubah. Membersihkan cache alignment.")
            # --- BAGIAN BARU: HAPUS CACHE DARI DISK ---
            cache_path, _ = self._get_alignment_cache_path()
            if cache_path and os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    print(f"INFO: File cache alignment '{cache_path}' telah dihapus.")
                except OSError as e:
                    print(f"ERROR: Gagal menghapus file cache: {e}")
            # --- AKHIR BAGIAN BARU ---
            
            self.cached_alignment_result = None
            self.cached_projection_result = None
        
        elif setting_key in projection_settings:
            print("INFO: Pengaturan proyeksi berubah. Membersihkan cache projection.")
            # (Di sini Anda juga bisa menambahkan logika untuk menghapus cache disk untuk proyeksi jika sudah diimplementasikan)
            self.cached_projection_result = None
            
        if self.current_project_id:
            self.database_manager.save_project_workflow_setting(self.current_project_id, setting_key, value)
            
    def _invalidate_alignment_cache(self):
        """Fungsi bantuan untuk menghapus cache alignment."""
        cache_path, _ = self._get_alignment_cache_path()
        if cache_path and os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                print(f"INFO: File cache alignment '{cache_path}' telah dihapus karena perubahan gambar.")
            except OSError as e:
                print(f"ERROR: Gagal menghapus file cache: {e}")
        self.cached_alignment_result = None
        self.cached_projection_result = None

    # =========================================================================
    # === 4. Logika Pemrosesan Asinkron (Panorama Stitching) ===
    # =========================================================================

    # --- 4a. Inisiasi Proses ---
    @Slot(str)
    def _on_preview_requested(self, stage_name):
        """
        Memulai proses stitching. Untuk alignment, periksa cache disk dan verifikasi
        pengaturan yang digunakan sebelumnya.
        """
        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "Process Running", "Another process is already running. Please wait.")
            return

        # --- BAGIAN PEMERIKSAAN CACHE YANG DIPERBARUI ---
        if stage_name == "alignment":
            cache_path, _ = self._get_alignment_cache_path()
            if cache_path and os.path.exists(cache_path):
                print(f"INFO: File cache alignment ditemukan. Memverifikasi pengaturan...")
                try:
                    # 1. Muat seluruh data dari cache (pengaturan + hasil)
                    with open(cache_path, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    saved_settings = cached_data.get("settings")
                    result_data = cached_data.get("result_data")
                    
                    # 2. Ambil pengaturan terbaru dari database untuk perbandingan
                    current_settings = self.database_manager.get_project_workflow_settings(self.current_project_id)

                    if not saved_settings or not result_data or not current_settings:
                        raise ValueError("Format cache tidak valid atau pengaturan tidak ditemukan.")

                    # 3. Bandingkan pengaturan yang relevan untuk alignment
                    keys_to_check = ['align_algorithm', 'feature_detector']
                    settings_match = True
                    for key in keys_to_check:
                        if saved_settings.get(key) != current_settings.get(key):
                            print(f"INFO: Pengaturan '{key}' telah berubah. (Cache: '{saved_settings.get(key)}', Saat ini: '{current_settings.get(key)}')")
                            settings_match = False
                            break 
                        
                    # 4. Jika pengaturan cocok, gunakan cache. Jika tidak, lanjutkan ke pemrosesan ulang.
                    if settings_match:
                        print("INFO: Pengaturan cocok. Memuat hasil dari cache.")
                        self._on_alignment_finished(result_data) 
                        return

                    else:
                        print("INFO: Pengaturan tidak cocok. Cache tidak valid, akan diproses ulang.")

                except Exception as e:
                    print(f"ERROR: Gagal memuat atau memverifikasi file cache: {e}. Melanjutkan dengan pemrosesan ulang.")
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
        
        image_paths = self.database_manager.get_images_for_project(self.current_project_id)
        if not image_paths or len(image_paths) < 2:
            QMessageBox.information(self, "Not Enough Images", "You need at least two images for alignment.")
            return
            
        settings = self.database_manager.get_project_workflow_settings(self.current_project_id)
        
        # Tentukan data cache yang akan digunakan berdasarkan tahap yang diminta
        align_cache = None
        proj_cache = None 

        if stage_name == "projection":
            if not self.cached_alignment_data:
                QMessageBox.information(self, "Langkah Dibutuhkan", "Silakan jalankan tahap 'Alignment' terlebih dahulu.")
                return
            # Siapkan data alignment untuk diteruskan ke worker
            print("INFO: Menggunakan data alignment dari memori untuk tahap Proyeksi.")
            align_cache = self.cached_alignment_data
        elif stage_name == "blending":
            pass

        titles = {"alignment": "Aligning Images...", "projection": "Applying Projection...", "blending": "Blending Panorama..."}
        self.display_panel.show_processing_view(titles.get(stage_name, "Processing..."))
        
        # Setup dan jalankan worker thread
        self.thread = QThread()
        self.worker = PanoramaWorker(
            image_paths=image_paths, 
            settings=settings,
            target_stage=stage_name,
            cached_alignment=align_cache,
            cached_projection=proj_cache  # Sekarang variabel ini sudah didefinisikan
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_stitching_finished)
        self.worker.error.connect(self._on_stitching_error)
        self.worker.progress_updated.connect(self._on_real_progress_update)
        
        self.thread.start()

    # --- 4b. Slot untuk Sinyal dari Worker Thread ---

    @Slot(int, str)
    def _on_real_progress_update(self, percentage, message):
        """Memperbarui progress bar di UI."""
        self.display_panel.update_processing_progress(message, percentage)

    @Slot(str, object)
    def _on_stitching_finished(self, stage_name, result):
        """
        Menangani hasil sukses dari worker. Menyimpan hasil alignment DAN pengaturannya 
        ke cache disk.
        """
        self.cleanup_thread()

        if result.get("error"):
            QMessageBox.critical(self, "Processing Error", result["error"])
            self._on_back_to_grid_request()
            return

        if stage_name == "alignment":
            cache_path, _ = self._get_alignment_cache_path()
            if cache_path:
                try:
                    # 1. Ambil pengaturan saat ini yang digunakan untuk proses ini
                    current_settings = self.database_manager.get_project_workflow_settings(self.current_project_id)
                    
                    # 2. Buat dictionary untuk disimpan, berisi pengaturan dan hasil
                    data_to_cache = {
                        "settings": current_settings,
                        "result_data": result 
                    }
                    
                    with open(cache_path, 'wb') as f:
                        # Simpan seluruh dictionary ke file cache
                        pickle.dump(data_to_cache, f)

                except Exception as e:
                    print(f"ERROR: Gagal menyimpan file cache: {e}")
            
            self.cached_projection_result = None
            # Panggil handler selanjutnya dengan hasil pemrosesan ('result')
            self._on_alignment_finished(result) 
        
        elif stage_name == "projection":
            # Simpan hasil proyeksi ke cache memori untuk tahap blending
            self.cached_projection_data = result
            self._on_projection_finished(result) # Panggil handler UI yang baru
        
        elif stage_name == "blending":
            pass
    
    @Slot(str)
    def _on_stitching_error(self, error_message):
        """Menangani sinyal error dari worker."""
        print(f"ERROR DARI WORKER: {error_message}")
        self.cleanup_thread()
        QMessageBox.critical(self, "Processing Error", error_message)
        self._on_back_to_grid_request() 

    # --- 4c. Penanganan Hasil Spesifik per Tahap ---

    def _on_alignment_finished(self, alignment_result_data, target_display_size=None, 
                           viewport_offset=(0, 0), zoom_level=0.1):
        """
        Menampilkan hasil alignment menggunakan memmap panorama besar.

        - target_display_size: (width, height) viewport di UI
        - viewport_offset: (x, y) posisi tengah viewport dalam koordinat full panorama
        - zoom_level: >1 = zoom in, <1 = zoom out
        """
        memmap_path = alignment_result_data.get("memmap_path")
        full_shape = alignment_result_data.get("shape")  # (h, w, c)

        # fallback jika memmap tidak ada
        if memmap_path is None or full_shape is None or not os.path.exists(memmap_path):
            stitched_panorama = alignment_result_data.get("stitched_image")
            if stitched_panorama is None:
                error_msg = alignment_result_data.get("error", "No preview available.")
                self.display_panel.show_preview_message(error_msg)
                return
        else:
            h_full, w_full, c_full = full_shape
            fp = np.memmap(memmap_path, dtype=alignment_result_data.get("dtype", np.float32),
                        mode="r", shape=full_shape)

            if target_display_size is None:
                # baca full panorama dari memmap → hati-hati RAM
                stitched_panorama = np.array(fp)
            else:
                target_w, target_h = target_display_size
                crop_w = int(target_w / zoom_level)
                crop_h = int(target_h / zoom_level)

                offset_x, offset_y = viewport_offset
                x1 = max(0, min(offset_x, w_full - crop_w))
                y1 = max(0, min(offset_y, h_full - crop_h))
                x2 = x1 + crop_w
                y2 = y1 + crop_h

                # baca crop langsung dari memmap → RAM tetap kecil
                stitched_panorama = np.array(fp[y1:y2, x1:x2])

                # resize crop agar sesuai viewport
                stitched_panorama = cv2.resize(
                    stitched_panorama, (target_w, target_h), interpolation=cv2.INTER_LINEAR
                )

            del fp  # flush memmap

        # simpan data alignment lengkap
        self.cached_alignment_data = alignment_result_data
        self.cached_projection_result = None

        # tampilkan di UI (display_zoomable_image sudah resize aman)
        self.last_preview_info = ("aligned", stitched_panorama, zoom_level)
        self.display_panel.display_zoomable_image(stitched_panorama)

        self.latest_successful_stage = "aligned"
        has_images = bool(self.database_manager.get_images_for_project(self.current_project_id))
        self.workflow_panel.update_workflow_stage("aligned", has_images=has_images)
        self.workflow_panel.tab_widget.setCurrentIndex(1)



    def _on_projection_finished(self, projected_data): 
        """
        Menampilkan hasil proyeksi dan memperbarui state UI.
        """
        stitched_panorama = projected_data.get("stitched_image")
        if stitched_panorama is None:
            error_msg = projected_data.get("error", "Projection failed.")
            self.display_panel.show_preview_message(error_msg)
            return

        self.last_preview_info = ("projected", stitched_panorama, 1) # stage, data, tab_index
        self.display_panel.display_zoomable_image(stitched_panorama)
        
        self.latest_successful_stage = "projected"
        has_images = bool(self.database_manager.get_images_for_project(self.current_project_id))
        self.workflow_panel.update_workflow_stage("projected", has_images=has_images)
        self.workflow_panel.tab_widget.setCurrentIndex(2) # Pindah ke tab Blending

    def _on_blending_finished(self, final_image):
        """Menampilkan hasil blending akhir dan memperbarui state UI."""
        message = "Panorama created successfully!"
        self.last_preview_info = ("blended", final_image, 2)
        self.display_panel.show_preview_message(message)

        self.latest_successful_stage = "blended"
        has_images = bool(self.database_manager.get_images_for_project(self.current_project_id))
        self.workflow_panel.update_workflow_stage("blended", has_images=has_images)

    # =========================================================================
    # === 5. Metode Utilitas dan Bantuan ===
    # =========================================================================
    
    def _get_alignment_cache_path(self):
        """
        Membuat path file cache yang unik untuk hasil alignment.
        Nama file didasarkan pada hash dari ID proyek dan daftar path gambar.
        """
        if not self.current_project_id:
            return None, None

        # 1. Tentukan direktori cache
        cache_dir = os.path.join("database", "cache", "align_stitch")
        os.makedirs(cache_dir, exist_ok=True) # Buat folder jika belum ada

        # 2. Kumpulkan input yang relevan untuk hash
        image_paths = sorted(self.database_manager.get_images_for_project(self.current_project_id))
        
        # Jika tidak ada gambar, tidak ada cache
        if not image_paths:
            return None, None
            
        input_string = f"project:{self.current_project_id}-images:{','.join(image_paths)}"
        
        # 3. Buat hash yang unik
        # Menggunakan MD5 untuk kecepatan, SHA256 lebih aman tetapi tidak diperlukan di sini
        filename = hashlib.md5(input_string.encode('utf-8')).hexdigest() + ".pkl"
        
        # 4. Kembalikan path lengkap
        full_path = os.path.join(cache_dir, filename)
        
        return full_path, cache_dir
    
    def cleanup_thread(self):
        """Membersihkan thread dan worker setelah selesai atau terjadi error."""
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        self.thread = None
        self.worker = None
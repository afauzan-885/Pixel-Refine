from collections import OrderedDict
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsTextItem
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QObject, QRectF, QBuffer, QByteArray, QIODevice, QPointF
from PyQt6.QtGui import QPixmap, QImage
try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    print("Warning: psutil library not found. RAM-based cache limits disabled.")
    print("Please install it: pip install psutil")
    psutil = None
    _PSUTIL_AVAILABLE = False
from UI.settings.General.Language import language_config
from UI.enhance_stack.logic.multi_threading import RawImageProcessingThread
from UI.enhance_stack.logic.Zoomable_Handler import Zoomable
# -------------------------------------------

class ImagePreviewHandler(QObject):
    """
    Mengelola logika tampilan pratinjau gambar dengan cache LRU adaptif
    berbasis RAM/item count, dengan opsi penyimpanan cache sebagai JPEG bytes atau QImage.
    """
    
    def __init__(self, preview_scene: QGraphicsScene, preview_view: Zoomable, parent=None):
        super().__init__(parent)
        if not isinstance(preview_view, Zoomable):
             print("Warning: ImagePreviewHandler expected a Zoomable view.")

        self.preview_scene = preview_scene
        self.preview_view = preview_view
        self._original_pixmap: QPixmap | None = None
        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._raw_thread: RawImageProcessingThread | None = None

        # --- Timer Utama (untuk delay awal cache miss) ---
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._initiate_processing)
        self._current_paths_to_process: list = [] 
        
        self._full_res_load_timer = QTimer(self)
        self._full_res_load_timer.setSingleShot(True)
        self._full_res_load_timer.timeout.connect(self._initiate_pending_full_res_load)
        self._pending_full_res_path: str | None = None 
        
        self.MAX_CACHE_ITEMS = 3                # Batas cache utama (full-res / JPEG)
        self.MAX_LOW_RES_ITEMS = 40             # Batas cache sekunder (low-res QImage)
        self.LOW_RES_TARGET_SIZE = 512          # Ukuran target (sisi terpanjang) untuk low-res
        self.RAM_LIMIT_PERCENT = 8.0            # Batas RAM untuk cache utama
        self.use_jpeg_cache = False             # Opsi format cache utama
        self.jpeg_quality = 95                  # Cache Utama: Menyimpan QImage atau bytes (JPEG)
        self._preview_cache = OrderedDict()     
        self._low_res_cache = OrderedDict()     
        self._current_processing_path: str | None = None
        self._persistent_zoom_level = 0

        self._process: "psutil".Process | None = None
        self._total_system_ram: int = 0
        self.psutil_monitoring_active = False
        
        self._persistent_zoom_level = 0
        self._persistent_relative_center: tuple[float, float] | None = None # Simpan posisi relatif
       
        if _PSUTIL_AVAILABLE:
            try:
                self._process = psutil.Process()
                self._total_system_ram = psutil.virtual_memory().total
                self.psutil_monitoring_active = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                self._process = None
                self._total_system_ram = 0
                self.psutil_monitoring_active = False
        
        if hasattr(self.preview_view, 'view_state_changed'):
            self.preview_view.view_state_changed.connect(self._store_view_state)
        else:
            print("Warning: Zoomable view does not have 'view_state_changed' signal.")

        
    # --- Metode Publik ---
    @pyqtSlot(int, object)
    def _store_view_state(self, level: int, relative_center: tuple[float, float] | None):
        """Menyimpan level zoom dan posisi tengah relatif terakhir."""
        self._persistent_zoom_level = level
        if isinstance(relative_center, tuple) and len(relative_center) == 2:
            self._persistent_relative_center = relative_center

    @pyqtSlot(list)
    def update_preview(self, selected_paths: list):
        """
        Memulai proses pembaruan panel pratinjau. Mengecek cache QImage terlebih dahulu.
        """
        self._stop_current_processing()

        if selected_paths:
            image_path = selected_paths[0]
            self._currently_displayed_path = image_path
            
            # 1. Cek Cache Utama
            if image_path in self._preview_cache:
                cached_value = self._preview_cache[image_path]
                self._preview_cache.move_to_end(image_path)
                pixmap_to_display = self._load_pixmap_from_cache_value(image_path, cached_value)
                if pixmap_to_display:
                    self._display_image(pixmap_to_display)
                else: 
                    del self._preview_cache[image_path]
                    self._trigger_full_processing(image_path)
                return

            # 2. Cek Cache Sekunder (Low-Res)
            elif image_path in self._low_res_cache:
                low_res_qimage = self._low_res_cache[image_path]
                self._low_res_cache.move_to_end(image_path)
                pixmap_low_res = QPixmap.fromImage(low_res_qimage)
                if not pixmap_low_res.isNull():
                    self._display_image(pixmap_low_res) # Tampilkan low-res segera
                    # --- Mulai Timer Penundaan untuk Full-Res ---
                    self._pending_full_res_path = image_path
                    self._full_res_load_timer.start(500) # 500 ms delay
                    
                else: # Cache low-res rusak
                    del self._low_res_cache[image_path]
                    self._trigger_full_processing(image_path) # Proses ulang
                return

            self._trigger_full_processing(image_path) # Mulai proses full-res (dengan delay timer utama)

        else:
            self.preview_scene.clear()
            self._pixmap_item = None
            self._original_pixmap = None
            self._show_status_message(language_config.UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED)
            self._fit_image_to_panel()
            
    def _load_pixmap_from_cache_value(self, image_path: str, cached_value: QImage | bytes) -> QPixmap | None:
        """Helper untuk memuat QPixmap dari nilai cache (QImage atau bytes)."""
        pixmap = QPixmap()
        success = False
        if isinstance(cached_value, bytes): # JPEG Bytes
            byte_array = QByteArray(cached_value); buffer = QBuffer(byte_array)
            if buffer.open(QIODevice.OpenModeFlag.ReadOnly):
                success = pixmap.loadFromData(buffer.buffer(), "JPG")
                buffer.close()
        elif isinstance(cached_value, QImage): # QImage
             pixmap = QPixmap.fromImage(cached_value)
             success = not pixmap.isNull()

        if success:
            return pixmap
        else:
            print(f"Error loading QPixmap from cached data for {image_path} (Type: {type(cached_value).__name__})")
            return None
            
    def _trigger_full_processing(self, image_path: str):
        """Menampilkan status loading & memulai timer utama."""
        self._show_status_message(language_config.UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE)
        self._current_paths_to_process = [image_path]
        self._preview_timer.start(500) # Delay awal

    def handle_resize(self):
        """Menyesuaikan tampilan gambar saat ukuran view berubah."""
        self._fit_image_to_panel()

    def get_original_pixmap(self) -> QPixmap | None:
         """Mengembalikan QPixmap asli yang sedang ditampilkan."""
         return self._original_pixmap

    def clear_cache(self):
        """Menghapus semua item dari cache preview."""
        self._preview_cache.clear()
        
    def set_cache_mode(self, use_jpeg: bool, quality: int = 95):
        """Mengatur mode cache dan membersihkan cache lama."""
        new_mode = 'JPEG' if use_jpeg else 'QImage'
        old_mode = 'JPEG' if self.use_jpeg_cache else 'QImage'
        if new_mode != old_mode:
            self.clear_cache()
            self.use_jpeg_cache = use_jpeg
            if use_jpeg:
                self.jpeg_quality = max(0, min(100, quality)) 
        else:
             if use_jpeg and self.jpeg_quality != quality:
                  self.jpeg_quality = max(0, min(100, quality))
                  
    def _stop_current_processing(self):
        """Menghentikan SEMUA timer dan thread pemrosesan."""
        if self._preview_timer.isActive(): self._preview_timer.stop()
        if self._full_res_load_timer.isActive(): self._full_res_load_timer.stop() # <<<--- Hentikan timer kedua juga
        self._pending_full_res_path = None # <<<--- Reset path yang ditunda

        if self._raw_thread and self._raw_thread.isRunning():
            cancelling_path = self._current_processing_path or "Unknown"
            self._raw_thread.stop(); self._raw_thread.quit(); self._raw_thread.wait(500)
            self._raw_thread = None
        self._current_processing_path = None
        
    def _initiate_processing(self):
        """Memulai pemrosesan dari timer UTAMA."""
        if self._current_paths_to_process:
            path_to_process = self._current_paths_to_process[0]
            if path_to_process == self._currently_displayed_path:
                self._start_raw_processing(path_to_process)
            else:
                print(f"Skipping processing for {path_to_process}, user now wants {self._currently_displayed_path}")
        self._current_paths_to_process = [] 
        
    def _initiate_pending_full_res_load(self):
        """Memulai pemrosesan full-res JIKA path masih relevan."""
        if self._pending_full_res_path:
            path_to_load = self._pending_full_res_path
            self._pending_full_res_path = None # Reset flag penundaan

            if path_to_load == self._currently_displayed_path:
                # Cek juga apakah sudah ada di cache utama (mungkin dimuat oleh proses lain?)
                if path_to_load not in self._preview_cache:
                    self._start_raw_processing(path_to_load)
        else:
             print("Warning: _initiate_pending_full_res_load called without a pending path.")
    # -----------------------------------
        
    def _start_raw_processing(self, path_to_process: str):
        """Memulai thread untuk memproses satu gambar full-res."""
        # Hentikan proses LAMA jika ada (misal proses full-res lain yg belum selesai)
        if self._raw_thread and self._raw_thread.isRunning():
            # Jangan hentikan jika path-nya sama (sudah dicek di timer)
            if self._current_processing_path != path_to_process:
                 self._raw_thread.stop(); self._raw_thread.quit(); self._raw_thread.wait(500)
                 self._raw_thread = None
            else:
                 return 
        
        try:
             self._current_processing_path = path_to_process
             self._raw_thread = RawImageProcessingThread([path_to_process], batch_size=1, delay_ms=0)
             self._raw_thread.result_signal.connect(self._handle_image_ready)
             self._raw_thread.error_signal.connect(self._handle_image_error)
             self._raw_thread.start()
        except Exception as e:
             self._handle_image_error(f"Failed to start processing thread: {e}")
             self._current_processing_path = None

    def _handle_image_ready(self, image_result: object):
        """Menangani hasil full-res, update cache, pindahkan ke low-res jika perlu."""
        processing_path = self._current_processing_path
        self._current_processing_path = None

        if not processing_path: self._raw_thread = None; return

        # --- Validasi -> qimage_full ---
        qimage_full: QImage | None = None
        # ... (validasi sama) ...
        if isinstance(image_result, QImage) and not image_result.isNull(): qimage_full = image_result
        elif isinstance(image_result, QPixmap) and not image_result.isNull(): qimage_full = image_result.toImage()
        if qimage_full is None or qimage_full.isNull():
             self._handle_image_error(f"Invalid result/conversion for {processing_path}")
             return
        # -----------------------------

        # --- Siapkan value_to_cache & pixmap_for_display ---
        value_to_cache: QImage | bytes | None = None
        pixmap_for_display: QPixmap | None = None
        # ... (logika JPEG/QImage cache sama) ...
        if self.use_jpeg_cache:
             byte_array=QByteArray(); buffer=QBuffer(byte_array); pixmap_for_display=QPixmap.fromImage(qimage_full)
             if pixmap_for_display.isNull(): self._handle_image_error(f"QImage->QPixmap failed for JPEG ({processing_path})"); return
             if buffer.open(QIODevice.OpenModeFlag.WriteOnly) and pixmap_for_display.save(buffer, "JPG", self.jpeg_quality):
                  buffer.close(); value_to_cache = byte_array.data()
             else: buffer.close(); value_to_cache = qimage_full # Fallback
        else: # QImage Mode
             value_to_cache = qimage_full
             pixmap_for_display = QPixmap.fromImage(qimage_full)
             if pixmap_for_display.isNull(): self._handle_image_error(f"QImage->QPixmap failed for display ({processing_path})"); return
        # --------------------------------------------------

        if value_to_cache is not None:
            ram_ok = True; item_count_ok = True
            if self.psutil_monitoring_active and self._process:
                 try:
                      if self._process.memory_percent() > self.RAM_LIMIT_PERCENT: ram_ok = False
                 except Exception: pass
            item_count_ok = len(self._preview_cache) < self.MAX_CACHE_ITEMS

            while not (ram_ok and item_count_ok) and len(self._preview_cache) > 0:
                try:
                    oldest_path, evicted_item = self._preview_cache.popitem(last=False)
                    evicted_qimage: QImage | None = None
                    if isinstance(evicted_item, QImage): evicted_qimage = evicted_item
                    elif isinstance(evicted_item, bytes):
                         temp_pixmap = QPixmap(); temp_byte_array = QByteArray(evicted_item); temp_buffer = QBuffer(temp_byte_array)
                         if temp_buffer.open(QIODevice.OpenModeFlag.ReadOnly) and temp_pixmap.loadFromData(temp_buffer.buffer(), "JPG"):
                              evicted_qimage = temp_pixmap.toImage()
                         temp_buffer.close()

                    if evicted_qimage and not evicted_qimage.isNull():
                         target_size = self.LOW_RES_TARGET_SIZE; current_size = evicted_qimage.size()
                         new_size = current_size.scaled(target_size, target_size, Qt.AspectRatioMode.KeepAspectRatio)
                         if new_size.isValid():
                              qimage_low = evicted_qimage.scaled(new_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                              if not qimage_low.isNull():
                                   if len(self._low_res_cache) >= self.MAX_LOW_RES_ITEMS:
                                        lru_low_path, _ = self._low_res_cache.popitem(last=False)
                                   self._low_res_cache[oldest_path] = qimage_low
                                   
                    del evicted_item 
                    
                    item_count_ok = len(self._preview_cache) < self.MAX_CACHE_ITEMS
                    if self.psutil_monitoring_active and self._process:
                         try: ram_ok = self._process.memory_percent() <= self.RAM_LIMIT_PERCENT
                         except Exception: ram_ok = True
                    else: ram_ok = True
                except KeyError: break
        
            if processing_path:
                 self._preview_cache[processing_path] = value_to_cache
                 self._preview_cache.move_to_end(processing_path)
                 if processing_path in self._low_res_cache: # Hapus dari low-res
                     del self._low_res_cache[processing_path]
                 
        if pixmap_for_display is not None and self._currently_displayed_path == processing_path:
             self._display_image(pixmap_for_display)
        elif self._currently_displayed_path != processing_path:
             pass
        # -----------------------------------------------------

        self._raw_thread = None
        

    @pyqtSlot(str)
    def _handle_image_error(self, error_message: str):
        """Menangani pesan error dari thread pemrosesan."""
        processing_path = self._current_processing_path or "Unknown Path" # Gunakan path jika ada
        self._current_processing_path = None

        self.preview_scene.clear()
        self._pixmap_item = None
        self._original_pixmap = None
        status_msg = f"{language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED} ({processing_path})\nError: {error_message}"
        self._show_status_message(status_msg)
        self._fit_image_to_panel()
        self._raw_thread = None

    def _display_image(self, pixmap: QPixmap):
        """Menampilkan QPixmap yang diberikan dan memanggil _fit_image_to_panel."""
        if not self.preview_scene: return

        self.preview_scene.clear()
        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self.preview_scene.addItem(self._pixmap_item)
        self._original_pixmap = pixmap
        scene_rect = self._pixmap_item.boundingRect()
        self.preview_scene.setSceneRect(scene_rect)

        self._fit_image_to_panel()

    def _fit_image_to_panel(self):
        """
        Reset view, fit item, dan terapkan state zoom/posisi persisten.
        """
        if not self.preview_view or not self.preview_scene: return

        try:
            if hasattr(self.preview_view, 'reset_zoom') and callable(self.preview_view.reset_zoom):
                self.preview_view.reset_zoom()
            else:
                self.preview_view.resetTransform()
               
            scene_rect = self.preview_scene.sceneRect()
            items_rect = self.preview_scene.itemsBoundingRect() # Gunakan ini untuk perhitungan relatif
            if self._pixmap_item and not scene_rect.isEmpty():
                self.preview_view.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
            else:
                items_rect = QRectF() # Pastikan rect kosong jika tidak ada item

            if hasattr(self.preview_view, 'apply_state') and callable(self.preview_view.apply_state):
                 self.preview_view.apply_state(self._persistent_zoom_level, self._persistent_relative_center)
            else:
                 if hasattr(self.preview_view, 'apply_zoom_level'):
                      self.preview_view.apply_zoom_level(self._persistent_zoom_level)
                 if self._persistent_relative_center is not None and not items_rect.isEmpty() and items_rect.width() > 0 and items_rect.height() > 0 :
                      rel_x, rel_y = self._persistent_relative_center
                      target_x = items_rect.left() + rel_x * items_rect.width()
                      target_y = items_rect.top() + rel_y * items_rect.height()
                      self.preview_view.centerOn(QPointF(target_x, target_y))

        except Exception as e:
             print(f"Error during _fit_image_to_panel: {e}")


    def _show_status_message(self, message: str):
        """Menampilkan pesan status menggunakan QGraphicsTextItem."""
        if not self.preview_scene or not self.preview_view: return
        self.preview_scene.clear()
        self._pixmap_item = None
        self._original_pixmap = None
        
        text_item = QGraphicsTextItem()
        text_item.setHtml(f'<div style="color: transparent; text-align: center; font-size: 18px;">{message}</div>')
        text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.preview_scene.addItem(text_item)
        viewport_rect = self.preview_view.viewport().rect()
        self.preview_scene.setSceneRect(QRectF(viewport_rect))
        scene_center = self.preview_scene.sceneRect().center()
        item_rect = text_item.boundingRect()
        text_item.setPos(scene_center.x() - item_rect.width() / 2,
                         scene_center.y() - item_rect.height() / 2)
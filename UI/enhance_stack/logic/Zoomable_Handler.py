from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QWheelEvent, QPainter, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QPointF

class Zoomable(QGraphicsView):
    """
    QGraphicsView dengan kemampuan zoom in/out berbasis kursor mouse.
    """
    view_state_changed = pyqtSignal(int, object)
    user_zoom_level_changed = pyqtSignal(int)
    def __init__(self, scene: QGraphicsScene = None, parent=None):
        if scene is None:
            scene = QGraphicsScene(parent) 
        super().__init__(scene, parent)

        # Pengaturan awal view
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setInteractive(True) 

        # Faktor zoom
        self._zoom_factor_base = 1.3 # Seberapa cepat zoom per scroll
        self._zoom_level = 0      # Menyimpan level zoom saat ini
        self._max_zoom_level = 20 # Batas zoom in
        self._min_zoom_level = -1 # Batas zoom out
        self._is_panning = False
        
    def _get_relative_center(self) -> tuple[float, float] | None:
        """ Menghitung posisi relatif pusat viewport terhadap item utama di scene. """
        items_rect = self.scene().itemsBoundingRect()
        if items_rect.isEmpty() or items_rect.width() == 0 or items_rect.height() == 0:
            return None 
        viewport_center = self.viewport().rect().center()
        scene_center = self.mapToScene(viewport_center)

        relative_x = (scene_center.x() - items_rect.left()) / items_rect.width()
        relative_y = (scene_center.y() - items_rect.top()) / items_rect.height()

        relative_x = max(0.0, min(1.0, relative_x))
        relative_y = max(0.0, min(1.0, relative_y))

        return (relative_x, relative_y)
    
    def _emit_view_state(self):
        """ Mengambil state saat ini dan memancarkan sinyal. """
        relative_center = self._get_relative_center()
        self.view_state_changed.emit(self._zoom_level, relative_center)

    def wheelEvent(self, event: QWheelEvent):
        """ Tangani zoom dan emit state baru. """
        angle = event.angleDelta().y()
        zoom_direction = 1 if angle > 0 else -1 if angle < 0 else 0

        if zoom_direction != 0:
            previous_level = self._zoom_level
            new_level = previous_level + zoom_direction

            if not (self._min_zoom_level <= new_level <= self._max_zoom_level):
                event.accept()
                return

            zoom_factor = self._zoom_factor_base ** zoom_direction
            self.scale(zoom_factor, zoom_factor)
            self._zoom_level = new_level
            self._emit_view_state()
            
            event.accept()
        else:
            super().wheelEvent(event)
            
    def mousePressEvent(self, event: QMouseEvent):
        """ Catat jika pan dimulai. """
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag and event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """ Jika pan selesai, emit state baru. """
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag and event.button() == Qt.MouseButton.LeftButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self._emit_view_state()
            
        else:
             if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
                  self.setCursor(Qt.CursorShape.OpenHandCursor) 
             self._is_panning = False 
        super().mouseReleaseEvent(event)
            
    def apply_zoom_level(self, target_level: int):
        """ Terapkan level zoom absolut. """
        if target_level != 0:
            if not (self._min_zoom_level <= target_level <= self._max_zoom_level):
                target_level = max(self._min_zoom_level, min(target_level, self._max_zoom_level))
                if target_level == 0: return

            scale_factor = self._zoom_factor_base ** target_level
            self.scale(scale_factor, scale_factor)
            self._zoom_level = target_level
            
    def apply_state(self, target_level: int, relative_center: tuple[float, float] | None):
        """ Menerapkan level zoom dan posisi tengah relatif. """
        self.reset_zoom()
        self.apply_zoom_level(target_level) 
        
        if relative_center is not None:
            items_rect = self.scene().itemsBoundingRect()
            if not items_rect.isEmpty() and items_rect.width() > 0 and items_rect.height() > 0:
                rel_x, rel_y = relative_center
                target_scene_x = items_rect.left() + rel_x * items_rect.width()
                target_scene_y = items_rect.top() + rel_y * items_rect.height()
                target_point = QPointF(target_scene_x, target_scene_y)
                self.centerOn(target_point)
        else:
             pass

    def reset_zoom(self):
        """Mengembalikan zoom ke level default (100%)."""
        if self._zoom_level != 0:
            # Reset transformasi matrix ke identitas
            self.resetTransform()
            self._zoom_level = 0
            
    # Override showEvent untuk reset zoom saat pertama kali ditampilkan (opsional)
    # def showEvent(self, event):
    #     super().showEvent(event)
    #     self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio) # Fit awal
    #     self.reset_zoom()

    # Override resizeEvent untuk fit-in view saat ukuran berubah (opsional)
    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     if self.scene() and not self.scene().itemsBoundingRect().isEmpty():
    #          self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
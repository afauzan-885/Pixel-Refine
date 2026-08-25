"""
Grid Manager - Handles all grid-related operations for DisplayPanel.
Manages grid population, incremental loading, and viewport detection.

Windowed Lazy Loading:
- Hanya WINDOW_SIZE (50) card terdekat dari viewport yang memuat gambar di RAM.
- Card di luar window otomatis di-unload (card.unload_image()) untuk hemat RAM.
- Saat scroll, window dihitung ulang → card baru dimuat dari disk cache (JPG), lama di-unload.
- Sort berdasarkan jarak dari tengah viewport (bukan FIFO).
- Recovery watchdog setiap 15 detik untuk retry card yang tertinggal.
"""

import os

from PySide6.QtCore import QTimer, QPoint, QRect
from PySide6.QtWidgets import QWidget
from typing import Optional, Callable, List, Dict, Any
from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
    ProcessManager,
    is_widget_alive,
)
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_policy import (
    thumbnail_creation_enabled,
)

# Jumlah card maksimal yang memiliki gambar di RAM sekaligus
WINDOW_SIZE = 50


class GridManager:
    """Manages grid operations including population and viewport detection."""

    def __init__(self, parent_panel):
        """
        Initialize GridManager.

        Args:
            parent_panel: Reference to DisplayPanel for accessing UI components
        """
        self.panel = parent_panel
        self._populate_queue = []
        self._populate_timer = None
        self._real_paths_for_sync = []

        # Set card_id yang saat ini memiliki gambar di RAM (windowed tracking)
        self._loaded_card_ids: set = set()

        # Staged load timer (Breathing room sebelum background sync)
        self.staged_load_timer = QTimer(self.panel)
        self.staged_load_timer.setSingleShot(True)
        self.staged_load_timer.setInterval(500)  # 500ms breathing room
        self.staged_load_timer.timeout.connect(self._start_background_sync)

        # Scroll debounce timer — update window setelah scroll berhenti 120ms
        self.scroll_debounce_timer = QTimer(self.panel)
        self.scroll_debounce_timer.setSingleShot(True)
        self.scroll_debounce_timer.setInterval(120)
        self.scroll_debounce_timer.timeout.connect(self._update_window)

        # Recovery/Watchdog timer — retry thumbnail yang tertinggal setiap 15 detik
        # Berhenti otomatis ketika semua card dalam window sudah termuat
        self.recovery_timer = QTimer(self.panel)
        self.recovery_timer.setInterval(15000)  # 15 detik
        self.recovery_timer.timeout.connect(self._recovery_check)

    # =========================================================================
    # === GRID POPULATION ===
    # =========================================================================

    def clear_grid(self):
        """Remove all widgets from grid container."""
        self._loaded_card_ids.clear()
        self.panel.grid_animator.stop_all()
        self.panel.grid_container.set_batch_update(False)
        self.panel.grid_container.clear_items()

    def populate_grid_incremental(self, visual_images: List[Any]):
        """
        Start incremental population of grid with images.

        Args:
            visual_images: List of image objects to populate
        """
        self._populate_queue = list(visual_images)

        if self._populate_timer and self._populate_timer.isActive():
            self._populate_timer.stop()

        self._populate_timer = QTimer(self.panel)
        self._populate_timer.timeout.connect(self._process_incremental_population)

        ProcessManager.instance().register_timer(
            "display_populate", self._populate_timer
        )

        # 15 gambar per 30ms (Smooth & Fast)
        self._populate_timer.start(30)

    def _process_incremental_population(self):
        """Tambah gambar ke grid dalam chunk untuk menghindari UI freeze."""
        if not self._populate_queue:
            self._populate_timer.stop()
            self.panel.grid_container.set_batch_update(False)

            # Trigger window update pertama setelah semua card ada di grid
            self._update_window()

            # Breathing room sebelum background sync untuk card di luar viewport
            if self._real_paths_for_sync:
                self.staged_load_timer.start()
            return

        CHUNK_SIZE = 15
        for _ in range(CHUNK_SIZE):
            if not self._populate_queue:
                break

            img = self._populate_queue.pop(0)

            is_zombie = (
                hasattr(img, "__class__") and img.__class__.__name__ == "ZombieImg"
            )

            from resources.GenericUILibrary import ImageCard

            card = ImageCard(card_id=str(img.id), size=110)
            card._image_path = img.path
            if not thumbnail_creation_enabled(self.panel.logic.thumbnail_policy):
                card.set_placeholder_text(
                    os.path.basename(img.path).replace("_", "\n")
                )

            if not is_zombie:
                card.double_clicked.connect(self.panel._on_card_double_clicked)
                card.clicked.connect(
                    lambda cid, event, c=card: self.panel._on_card_clicked(
                        cid, event, c
                    )
                )

                self.panel.all_cards[str(img.id)] = card
                self.panel.grid_container.add_item(card)
                self.panel.logic.register_grid_item(str(img.id), {"path": img.path})
            else:
                self.panel.all_cards[str(img.id)] = card
                self.panel.grid_container.add_item(card)
                self.panel.deletion_manager.queue_zombie_card(str(img.id), card)

        self.panel._update_header_title()

        # Update window setiap 3 ticks selama populasi agar viewport terisi cepat
        if len(self._populate_queue) % 3 == 0:
            self._update_window()

    # =========================================================================
    # === WINDOWED LAZY LOADING ===
    # =========================================================================

    def on_scroll(self):
        """Dipanggil saat scrollbar bergerak. Debounce 120ms sebelum update window."""
        if not self.scroll_debounce_timer.isActive():
            self.scroll_debounce_timer.start()

    def _get_viewport_center_y(self) -> int:
        """Dapatkan posisi Y tengah viewport dalam koordinat content widget."""
        try:
            viewport = self.panel.grid_container.viewport()
            scrollbar = self.panel.grid_container.verticalScrollBar()
            scroll_offset = scrollbar.value() if scrollbar else 0
            viewport_half = viewport.height() // 2 if viewport else 0
            return scroll_offset + viewport_half
        except Exception:
            return 0

    def _compute_card_distance(self, card: QWidget, center_y: int) -> float:
        """
        Hitung jarak absolut card dari pusat viewport.
        Digunakan untuk sort prioritas loading (terdekat = prioritas tertinggi).
        """
        try:
            # pos().y() adalah posisi card dalam content widget (parent)
            card_y = card.pos().y() + card.height() // 2
            return abs(card_y - center_y)
        except Exception:
            return float("inf")

    def _update_window(self):
        """
        Inti dari Windowed Lazy Loading.
        1. Hitung jarak semua card dari pusat viewport.
        2. Card dalam WINDOW_SIZE terdekat → load jika belum termuat.
        3. Card di luar window → unload untuk bebaskan RAM.
        """
        if not thumbnail_creation_enabled(self.panel.logic.thumbnail_policy):
            return

        all_cards = self.panel.all_cards
        if not all_cards:
            return

        center_y = self._get_viewport_center_y()

        # Kumpulkan semua card yang valid beserta jaraknya
        card_distances = []
        for card_id, card in list(all_cards.items()):
            try:
                if not is_widget_alive(card):
                    continue
                dist = self._compute_card_distance(card, center_y)
                card_distances.append((dist, card_id, card))
            except Exception:
                continue

        if not card_distances:
            return

        # Sort berdasarkan jarak (terdekat ke viewport = index kecil = prioritas tinggi)
        card_distances.sort(key=lambda x: x[0])

        in_window = card_distances[:WINDOW_SIZE]    # 50 terdekat → harus termuat
        out_window = card_distances[WINDOW_SIZE:]   # Sisanya → unload

        # --- UNLOAD: Card di luar window ---
        for _dist, card_id, card in out_window:
            if card.has_image():
                card.unload_image()
                self._loaded_card_ids.discard(card_id)

        # --- LOAD: Card di dalam window yang belum termuat ---
        to_fetch = []
        for _dist, card_id, card in in_window:
            if not card.has_image() and not card._is_fetching:
                img_path = getattr(card, "_image_path", None)
                if img_path:
                    card._is_fetching = True
                    to_fetch.append((img_path, card, card_id))

        if not to_fetch:
            return

        # Bangun pairs (path, callback) — JPG sudah di disk, ini akan cepat
        pairs = []
        for path, card, card_id in to_fetch:
            def make_cb(c, cid):
                def cb(q_img, p):
                    self._on_card_loaded(q_img, p, c, cid)
                return cb
            pairs.append((path, make_cb(card, card_id)))

        self.panel.logic.load_thumbnails_bulk_async(pairs)

    def _on_card_loaded(self, q_image, path, card, card_id):
        """Callback setelah thumbnail selesai dimuat dari disk/decode."""
        self.panel._on_thumbnail_ready(q_image, path, card)
        if card.has_image():
            self._loaded_card_ids.add(card_id)

    # =========================================================================
    # === BACKGROUND SYNC (Card di luar viewport saat batch pertama dimuat) ===
    # =========================================================================

    def _start_background_sync(self):
        """Trigger background sync setelah breathing room selesai."""
        if not thumbnail_creation_enabled(self.panel.logic.thumbnail_policy):
            self._real_paths_for_sync = []
            return

        if not self._real_paths_for_sync:
            return

        # Bangun path→card lookup
        path_to_card = {}
        path_to_id = {}
        for card_id, card in self.panel.all_cards.items():
            img_path = getattr(card, "_image_path", None)
            if img_path:
                path_to_card[img_path] = card
                path_to_id[img_path] = card_id

        pairs = []
        for path in self._real_paths_for_sync:
            card = path_to_card.get(path)
            card_id = path_to_id.get(path)
            if card is not None:
                def make_cb(c, cid):
                    def cb(q_img, p):
                        self._on_card_loaded(q_img, p, c, cid)
                    return cb
                pairs.append((path, make_cb(card, card_id)))
            else:
                pairs.append((path, None))

        self.panel.logic.load_thumbnails_bulk_async(pairs)
        self._real_paths_for_sync = []

        # Trigger window update setelah sync selesai di-schedule
        # agar eviction langsung terjadi jika hasil melebihi WINDOW_SIZE
        self.scroll_debounce_timer.start()

    def set_sync_paths(self, paths: List[str]):
        """Set paths untuk background sync."""
        self._real_paths_for_sync = paths

    # =========================================================================
    # === RECOVERY WATCHDOG ===
    # =========================================================================

    def start_recovery_timer(self):
        """Mulai watchdog timer untuk retry thumbnail yang tertinggal."""
        if not self.recovery_timer.isActive():
            self.recovery_timer.start()

    def stop_recovery_timer(self):
        """Stop watchdog timer."""
        self.recovery_timer.stop()

    def _recovery_check(self):
        """
        Watchdog: Dipanggil setiap 15 detik.
        Cek apakah card di dalam window saat ini ada yang masih belum termuat.
        - Jika semua dalam window sudah termuat → stop timer.
        - Jika ada yang tertinggal → reset _is_fetching (lepas stuck state), retry.
        """
        if not thumbnail_creation_enabled(self.panel.logic.thumbnail_policy):
            self.stop_recovery_timer()
            return

        all_cards = self.panel.all_cards
        if not all_cards:
            self.stop_recovery_timer()
            return

        center_y = self._get_viewport_center_y()
        card_distances = []
        for card_id, card in list(all_cards.items()):
            try:
                if not is_widget_alive(card):
                    continue
                dist = self._compute_card_distance(card, center_y)
                card_distances.append((dist, card_id, card))
            except Exception:
                continue

        card_distances.sort(key=lambda x: x[0])
        in_window = card_distances[:WINDOW_SIZE]

        missing = []
        for _dist, card_id, card in in_window:
            if not card.has_image():
                card._is_fetching = False  # Reset stuck flag
                img_path = getattr(card, "_image_path", None)
                if img_path:
                    missing.append((img_path, card, card_id))

        if not missing:
            self.stop_recovery_timer()
            return

        print(
            f"[GridManager] Recovery: {len(missing)} thumbnail dalam window belum termuat, retry..."
        )

        pairs = []
        for path, card, card_id in missing:
            def make_cb(c, cid):
                def cb(q_img, p):
                    self._on_card_loaded(q_img, p, c, cid)
                return cb
            card._is_fetching = True
            pairs.append((path, make_cb(card, card_id)))

        self.panel.logic.load_thumbnails_bulk_async(pairs)

    # =========================================================================
    # === TIMER MANAGEMENT ===
    # =========================================================================

    def stop_staged_timer(self):
        """Stop semua timer (staged, scroll debounce, dan recovery)."""
        self.staged_load_timer.stop()
        self.scroll_debounce_timer.stop()
        self.recovery_timer.stop()
        self._loaded_card_ids.clear()

    # =========================================================================
    # === VIEWPORT UTILITIES ===
    # =========================================================================

    def is_widget_in_viewport(self, widget: QWidget) -> bool:
        """
        Check if widget is visible in GridContainer viewport.
        Used for viewport-aware animation optimization.
        """
        if not is_widget_alive(widget) or not widget.isVisible():
            return False

        try:
            viewport = self.panel.grid_container.viewport()
            if not viewport:
                return False

            visible_rect = viewport.rect()
            widget_pos = widget.mapTo(viewport, QPoint(0, 0))
            widget_rect = QRect(widget_pos, widget.size())

            return visible_rect.intersects(widget_rect)
        except Exception:
            return False

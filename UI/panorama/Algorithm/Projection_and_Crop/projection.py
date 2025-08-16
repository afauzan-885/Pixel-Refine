# File: UI/panorama/logic/projection.py

from typing import Any, Callable, Dict, List, Optional
import cv2
import numpy as np

from UI.panorama.Algorithm import panorama_utils

class Projector:
    """
    Kelas yang menangani seluruh proses rendering untuk proyeksi Planar.
    Menggunakan pendekatan two-pass untuk me-render kanvas yang ketat.
    (Versi ini tidak melakukan auto-cropping pasca-render).
    """

    def __init__(
        self,
        alignment_data: Dict[str, Any],
        image_paths: List[str],
        settings: Dict[str, Any],
        progress_callback: Optional[Callable],
    ):
        self.minimal_data = alignment_data
        self.image_paths = image_paths
        self.settings = settings
        self.progress_callback = progress_callback
        self.full_data: Dict[str, Any] = {}

    def _progress(self, p: float, msg: str):
        if self.progress_callback:
            self.progress_callback(p, msg)

    def _calculate_tight_bounds(
        self,
        homographies_for_max_canvas: List[np.ndarray],
        image_shapes: List[tuple],
        max_canvas_size: tuple,
    ) -> tuple:
        self._progress(5, "Menganalisis batas konten...")
        preview_scale = min(0.1, 1024 / max(max_canvas_size))
        max_h, max_w = max_canvas_size[1], max_canvas_size[0]
        preview_h, preview_w = int(max_h * preview_scale), int(max_w * preview_scale)
        S = np.array(
            [[preview_scale, 0, 0], [0, preview_scale, 0], [0, 0, 1]], dtype=np.float64
        )
        combined_mask = np.zeros((preview_h, preview_w), dtype=np.uint8)
        for i in range(len(self.image_paths)):
            h, w = image_shapes[i][:2]
            original_mask = np.full((h, w), 255, dtype=np.uint8)
            preview_homography = S @ homographies_for_max_canvas[i]
            warped_mask = cv2.warpPerspective(
                original_mask, preview_homography, (preview_w, preview_h)
            )
            cv2.bitwise_or(combined_mask, warped_mask, combined_mask)
        contours, _ = cv2.findContours(
            combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return (0, 0, max_canvas_size[0], max_canvas_size[1])
        all_points = np.concatenate(contours, axis=0)
        x, y, w, h = cv2.boundingRect(all_points)
        return (
            int(x / preview_scale),
            int(y / preview_scale),
            int(w / preview_scale),
            int(h / preview_scale),
        )

    def _prepare_data(self) -> bool:
        self._progress(0, "Memvalidasi dan menyiapkan data alignment...")
        initial_homographies = self.minimal_data.get("homographies")
        if not initial_homographies:
            self.full_data["error"] = "Data alignment tidak berisi 'homographies'."
            return False
        try:
            shapes = [
                cv2.imread(p, cv2.IMREAD_UNCHANGED).shape for p in self.image_paths
            ]
            self.full_data["image_shapes"] = shapes
        except Exception as e:
            self.full_data["error"] = f"Gagal membaca bentuk gambar: {e}"
            return False
        centered_homographies = panorama_utils.center_FOV(initial_homographies)
        all_corners = []
        for i, H in enumerate(centered_homographies):
            h, w = self.full_data["image_shapes"][i][:2]
            corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            warped = cv2.perspectiveTransform(corners, H)
            all_corners.append(warped)
        all_corners = np.concatenate(all_corners, axis=0)
        x_min, y_min = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        x_max, y_max = np.int32(all_corners.max(axis=0).ravel() + 0.5)
        T_translate_max = np.array(
            [[1, 0, -x_min], [0, 1, -y_min], [0, 0, 1]], dtype=np.float64
        )
        homographies_for_max_canvas = [
            T_translate_max @ H for H in centered_homographies
        ]
        max_canvas_size = (x_max - x_min, y_max - y_min)
        tight_rect = self._calculate_tight_bounds(
            homographies_for_max_canvas, self.full_data["image_shapes"], max_canvas_size
        )
        tx, ty, tw, th = tight_rect
        final_offset_x, final_offset_y = -(x_min + tx), -(y_min + ty)
        T_translate_final = np.array(
            [[1, 0, final_offset_x], [0, 1, final_offset_y], [0, 0, 1]],
            dtype=np.float64,
        )
        homographies_for_render = [T_translate_final @ H for H in centered_homographies]
        self.full_data["tight_output_shape"] = (th, tw, 3)
        self.full_data["homographies_for_render"] = homographies_for_render
        self.full_data["error"] = None
        return True

    def _render_panorama(self) -> Optional[np.ndarray]:
        def render_progress_reporter(p, msg):
            self._progress(15 + (p / 100.0 * 85), msg)  # Progres dari 15% -> 100%

        return panorama_utils.planar_warp_tile(
            image_paths=self.image_paths,
            image_shapes=self.full_data["image_shapes"],
            homographies=self.full_data["homographies_for_render"],
            output_shape=self.full_data["tight_output_shape"],
            progress_callback=render_progress_reporter,
        )

    # <<< METODE _autocrop DIHAPUS SEPENUHNYA >>>

    def process(self) -> Dict[str, Any]:
        """
        Metode utama yang menjalankan seluruh alur kerja.
        (Versi ini tidak melakukan cropping pasca-render).
        """
        if not self._prepare_data():
            return self.full_data

        final_panorama = self._render_panorama()
        if final_panorama is None:
            return {"stitched_image": None, "error": "Rendering panorama gagal."}

        # <<< TIDAK ADA LAGI LOGIKA CROPPING DI SINI >>>
        final_result = final_panorama

        self._progress(100, "Selesai.")
        return {"stitched_image": final_result, "error": None}

# =========================================================================
# === Fungsi Kontroler Sederhana (Panel Kontrol) ===
# =========================================================================


def run_projection_and_crop(
    alignment_data: Dict[str, Any],
    image_paths: List[str],
    settings: Dict[str, Any],
    progress_callback: Callable,
) -> Dict[str, Any]:
    """
    Fungsi utama untuk menjalankan proyeksi.
    (Nama fungsi dipertahankan, tapi sekarang tidak melakukan crop).
    """
    projection_type = settings.get("projection_type", "Planar")

    try:
        if projection_type == "Planar":
            projector = Projector(
                alignment_data=alignment_data,
                image_paths=image_paths,
                settings=settings,
                progress_callback=progress_callback,
            )
            # Panggilan sekarang sederhana, tanpa argumen 'use_crop'
            result = projector.process()

        else:
            result = {
                "stitched_image": None,
                "error": f"Proyeksi '{projection_type}' tidak dikenal atau belum diimplementasikan.",
            }

        return result

    except Exception as e:
        import traceback

        error_msg = f"Error fatal selama proses proyeksi: {e}\n{traceback.format_exc()}"
        print(error_msg)
        return {"stitched_image": None, "error": error_msg}

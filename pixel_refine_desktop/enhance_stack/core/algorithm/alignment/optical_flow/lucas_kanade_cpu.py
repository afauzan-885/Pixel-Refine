import json
import os
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import (
    align_with_tiled_flow,
)


DEFAULT_LUCAS_KANADE_CONFIG = {
    "grid_step": 16,
    "border_margin": 8,
    "point_workers": 2,
    "win_size": 17,
    "max_level": 2,
    "iterations": 18,
    "epsilon": 0.015,
    "use_multi_core": True,
    "tile_cols": 2,
    "tile_rows": 2,
    "tile_overlap": 0.20,
}


class LucasKanadeCPU:
    NAME = "Lucas Kanade Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "Tile-based CPU Lucas-Kanade optical flow alignment."

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        config = DEFAULT_LUCAS_KANADE_CONFIG.copy()
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                config.update(params.get("LucasKanade", {}))
                config.update(params.get("LucasKanade_BATCH", {}))
        except Exception as exc:
            print(f"[LucasKanadeCPU] Failed to load config: {exc}")
        return config

    @staticmethod
    def load_lucas_kanade_config(config_filename=None):
        return LucasKanadeCPU.load_config(config_filename=config_filename)

    @staticmethod
    def load_lucas_kanade_config_for_batch(config_filename=None):
        return LucasKanadeCPU.load_config(config_filename=config_filename)

    def calculate_flow(self, reference_gray, target_gray, config, point_executor=None):
        height, width = reference_gray.shape[:2]
        points = self._make_grid_points(width, height, config)
        if points is None or len(points) < 4:
            return np.zeros((height, width, 2), dtype=np.float32)

        win_size = max(5, int(config.get("win_size", 17)))
        if win_size % 2 == 0:
            win_size += 1

        next_points, status = self._track_grid_points(
            reference_gray,
            target_gray,
            points,
            config,
            win_size,
            point_executor=point_executor,
        )
        if next_points is None or status is None:
            return np.zeros((height, width, 2), dtype=np.float32)

        valid = status.reshape(-1).astype(bool)
        source = points.reshape(-1, 2)[valid]
        target = next_points.reshape(-1, 2)[valid]
        if len(source) < 4:
            return np.zeros((height, width, 2), dtype=np.float32)

        sparse_flow = np.zeros((height, width, 2), dtype=np.float32)
        weight = np.zeros((height, width), dtype=np.float32)
        displacement = target - source
        coords = np.rint(source).astype(np.int32)
        coords[:, 0] = np.clip(coords[:, 0], 0, width - 1)
        coords[:, 1] = np.clip(coords[:, 1], 0, height - 1)

        for (x, y), (dx, dy) in zip(coords, displacement):
            sparse_flow[y, x, 0] += dx
            sparse_flow[y, x, 1] += dy
            weight[y, x] += 1.0

        known = weight > 0
        sparse_flow[known, 0] /= weight[known]
        sparse_flow[known, 1] /= weight[known]
        return self._densify_sparse_flow(sparse_flow, known)

    def _make_grid_points(self, width, height, config):
        step = max(4, int(config.get("grid_step", 16)))
        margin = max(0, int(config.get("border_margin", 8)))
        x_start = min(margin, max(0, width - 1))
        y_start = min(margin, max(0, height - 1))
        x_stop = max(x_start + 1, width - margin)
        y_stop = max(y_start + 1, height - margin)

        xs = np.arange(x_start, x_stop, step, dtype=np.float32)
        ys = np.arange(y_start, y_stop, step, dtype=np.float32)
        if xs.size == 0 or ys.size == 0:
            return None
        grid_x, grid_y = np.meshgrid(xs, ys)
        return np.column_stack((grid_x.ravel(), grid_y.ravel())).reshape(-1, 1, 2)

    def _track_grid_points(
        self,
        reference_gray,
        target_gray,
        points,
        config,
        win_size,
        point_executor=None,
    ):
        criteria = (
            cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
            max(1, int(config.get("iterations", 18))),
            float(config.get("epsilon", 0.015)),
        )
        max_level = max(0, int(config.get("max_level", 2)))

        def track_chunk(chunk):
            next_chunk, status_chunk, _ = cv2.calcOpticalFlowPyrLK(
                reference_gray,
                target_gray,
                chunk,
                None,
                winSize=(win_size, win_size),
                maxLevel=max_level,
                criteria=criteria,
            )
            return next_chunk, status_chunk

        point_workers = max(1, int(config.get("point_workers", 2)))
        if point_executor is None or point_workers <= 1 or len(points) < 256:
            return track_chunk(points)

        chunks = [
            chunk
            for chunk in np.array_split(points, min(point_workers, len(points)))
            if len(chunk) > 0
        ]
        results = list(point_executor.map(track_chunk, chunks))
        next_chunks = []
        status_chunks = []
        for next_chunk, status_chunk in results:
            if next_chunk is None or status_chunk is None:
                continue
            next_chunks.append(next_chunk)
            status_chunks.append(status_chunk)
        if not next_chunks:
            return None, None
        return np.vstack(next_chunks), np.vstack(status_chunks)

    def _densify_sparse_flow(self, sparse_flow, known):
        if not np.any(known):
            return sparse_flow

        dense = sparse_flow.astype(np.float32, copy=True)
        valid = known.astype(np.float32)
        for _ in range(64):
            missing = valid <= 0
            if not np.any(missing):
                break
            weighted = dense * valid[..., None]
            blur_flow = cv2.blur(weighted, (5, 5))
            blur_weight = cv2.blur(valid, (5, 5))
            can_fill = missing & (blur_weight > 1e-6)
            dense[can_fill] = blur_flow[can_fill] / blur_weight[can_fill, None]
            valid[can_fill] = 1.0
        return cv2.GaussianBlur(dense, (5, 5), 0)

    def align_frame(
        self,
        reference,
        target,
        config=None,
        stop_requested=None,
        tile_executor=None,
        point_executor=None,
    ):
        config = config or self.load_config()

        def flow_func(reference_gray, target_gray):
            return self.calculate_flow(
                reference_gray,
                target_gray,
                config,
                point_executor=point_executor,
            )

        return align_with_tiled_flow(
            reference,
            target,
            flow_func,
            cols=int(config.get("tile_cols", 3)),
            rows=int(config.get("tile_rows", 2)),
            overlap=float(config.get("tile_overlap", 0.20)),
            use_multi_core=bool(config.get("use_multi_core", True)),
            stop_requested=stop_requested,
            executor=tile_executor,
        )

    def build_flow_alignment(self, ctx, reference, target_dims, orchestrator, config):
        os.makedirs(os.path.dirname(ctx.hdf5_path), exist_ok=True)
        if os.path.exists(ctx.hdf5_path):
            os.remove(ctx.hdf5_path)

        import gc
        import h5py
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            extract_exif,
            save_to_hdf5,
        )

        tile_workers = max(
            1,
            min(
                int(config.get("tile_cols", 3)) * int(config.get("tile_rows", 2)),
                os.cpu_count() or 4,
            ),
        )
        point_workers = max(1, min(int(config.get("point_workers", 2)), os.cpu_count() or 4))

        def compute_aligned(index, path, tile_executor, point_executor):
            if ctx.stop_requested and ctx.stop_requested():
                return index, path, None
            if index == 0:
                return index, path, np.array(reference, copy=True)

            frame = orchestrator._load_single_frame(
                ctx, path, target_dims=target_dims
            )
            if frame is None:
                return index, path, None
            try:
                aligned = self.align_frame(
                    reference,
                    frame,
                    config=config,
                    stop_requested=ctx.stop_requested,
                    tile_executor=tile_executor,
                    point_executor=point_executor,
                )
            finally:
                del frame
            return index, path, aligned

        saved_count = 0
        with h5py.File(ctx.hdf5_path, "w") as h5f:
            h5f.attrs["ref_image_path"] = ctx.image_paths[0]
            h5f.attrs["alignment_algorithm"] = self.NAME
            h5f.attrs["alignment_process"] = "tile_optical_flow"

            paths = list(ctx.image_paths)
            with ThreadPoolExecutor(max_workers=1) as frame_executor:
                with ThreadPoolExecutor(max_workers=tile_workers) as tile_executor:
                    with ThreadPoolExecutor(max_workers=point_workers) as point_executor:
                        future = None
                        for index, path in enumerate(paths):
                            if future is None:
                                future = frame_executor.submit(
                                    compute_aligned,
                                    index,
                                    path,
                                    tile_executor,
                                    point_executor,
                                )

                            result_index, result_path, aligned = future.result()
                            next_index = index + 1
                            if next_index < len(paths) and not (
                                ctx.stop_requested and ctx.stop_requested()
                            ):
                                future = frame_executor.submit(
                                    compute_aligned,
                                    next_index,
                                    paths[next_index],
                                    tile_executor,
                                    point_executor,
                                )
                            else:
                                future = None

                            if ctx.stop_requested and ctx.stop_requested():
                                break
                            if aligned is None:
                                continue

                            save_to_hdf5(
                                h5f,
                                f"image_{result_index}",
                                aligned,
                                extract_exif(result_path),
                            )
                            h5f.flush()
                            saved_count += 1
                            print(
                                f"[LucasKanadeCPU] saved image_{result_index} shape={aligned.shape} dtype={aligned.dtype}"
                            )
                            del aligned

                            if saved_count % 4 == 0:
                                gc.collect()

                            if ctx.update_progress:
                                progress = 25 + int(
                                    ((result_index + 1) / max(1, ctx.total_images))
                                    * 65
                                )
                                ctx.update_progress(
                                    progress,
                                    f"Lucas-Kanade flow {result_index + 1}/{ctx.total_images}",
                                )

        ctx.aligned_frames = []
        ctx.frames = []
        ctx.data_source = ctx.hdf5_path
        ctx.needs_alignment = False
        print(
            f"[LucasKanadeCPU] finished saved={saved_count} hdf5_path={ctx.hdf5_path}"
        )
        return ctx

    def run(self, ctx, frames, batch_plan=None):
        return list(frames)

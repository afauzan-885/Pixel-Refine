import json
import os
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import (
    align_with_block_flow,
)


DEFAULT_LUCAS_KANADE_CONFIG = {
    "backend": "cpu",
    "mode": "fast",
}

LUCAS_KANADE_CPU_PRESETS = {
    "fast": {
        "grid_step": 24,
        "border_margin": 8,
        "point_workers": 2,
        "win_size": 15,
        "max_level": 2,
        "iterations": 12,
        "epsilon": 0.02,
        "use_multi_core": True,
        "tile_overlap": 0.20,
    },
    "medium": {
        "grid_step": 16,
        "border_margin": 8,
        "point_workers": 2,
        "win_size": 17,
        "max_level": 2,
        "iterations": 18,
        "epsilon": 0.015,
        "use_multi_core": True,
        "tile_overlap": 0.20,
    },
    "high": {
        "grid_step": 12,
        "border_margin": 8,
        "point_workers": 3,
        "win_size": 21,
        "max_level": 3,
        "iterations": 24,
        "epsilon": 0.01,
        "use_multi_core": True,
        "tile_overlap": 0.25,
    },
}


class LucasKanadeCPU:
    NAME = "Lucas Kanade Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "Tile-based CPU Lucas-Kanade optical flow alignment."

    @staticmethod
    def _normalize_mode(mode):
        value = str(mode or "fast").strip().lower()
        if value in ("balanced", "balance", "normal"):
            return "medium"
        if value not in LUCAS_KANADE_CPU_PRESETS:
            return "fast"
        return value

    @staticmethod
    def _resolve_mode_config(config):
        mode = LucasKanadeCPU._normalize_mode(config.get("mode", "fast"))
        resolved = LUCAS_KANADE_CPU_PRESETS[mode].copy()
        resolved["mode"] = mode
        resolved["backend"] = str(config.get("backend", "cpu") or "cpu")
        return resolved

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
        if batch_id is not None:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic import (
                    batch_parameter_manager,
                )

                batch_params = batch_parameter_manager.load_json_state().get(
                    str(batch_id), {}
                )
                section = batch_params.get("lucas_kanade_params", {})
                if isinstance(section, dict):
                    config.update(section)
            except Exception as exc:
                print(f"[LucasKanadeCPU] Failed to load batch config: {exc}")
        return LucasKanadeCPU._resolve_mode_config(config)

    @staticmethod
    def load_lucas_kanade_config(config_filename=None):
        return LucasKanadeCPU.load_config(config_filename=config_filename)

    @staticmethod
    def load_lucas_kanade_config_for_batch(config_filename=None):
        return LucasKanadeCPU.load_config(config_filename=config_filename)

    def calculate_flow(self, reference_gray, target_gray, config, point_executor=None):
        """Run the full-frame Taichi AOT Lucas-Kanade implementation."""
        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK
        win_size = max(5, int(config.get("win_size", 17)))
        if win_size % 2 == 0:
            win_size += 1
        flow = calcOpticalFlowPyrLK(
            np.ascontiguousarray(reference_gray),
            np.ascontiguousarray(target_gray),
            winSize=(win_size, win_size),
            maxLevel=max(0, int(config.get("max_level", 2))),
            grid_step=max(4, int(config.get("grid_step", 16))),
            border_margin=max(0, int(config.get("border_margin", 8))),
            motion_mode=str(config.get("motion_mode", "fast")),
            max_flow_px=float(config.get("max_flow_px", 0.0)),
        )
        if isinstance(flow, tuple):
            flow = flow[0]
        flow = np.asarray(flow, dtype=np.float32)
        expected = (*reference_gray.shape[:2], 2)
        if flow.shape != expected or not np.isfinite(flow).all():
            raise RuntimeError(f"Taichi Lucas-Kanade returned invalid flow: {flow.shape}, expected {expected}")
        return np.ascontiguousarray(flow)

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
        target_for_warping=None,
    ):
        config = config or self.load_config()

        def flow_func(reference_gray, target_gray):
            return self.calculate_flow(
                reference_gray,
                target_gray,
                config,
                point_executor=point_executor,
            )

        halo = int(config.get("win_size", 15)) * (
            2 ** max(0, int(config.get("max_level", 2)) - 1)
        )
        return align_with_block_flow(
            reference,
            target,
            flow_func,
            halo=halo,
            use_multi_core=bool(config.get("use_multi_core", True)),
            stop_requested=stop_requested,
            executor=tile_executor,
            target_for_warping=target_for_warping,
        )

    def build_flow_alignment(self, ctx, reference, target_dims, orchestrator, config):
        os.makedirs(os.path.dirname(ctx.hdf5_path), exist_ok=True)
        if os.path.exists(ctx.hdf5_path):
            os.remove(ctx.hdf5_path)

        import gc
        # (h5py removed)
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            extract_exif,
            save_to_hdf5,
            write_alignment_cache_attrs,
        )

        tile_workers = 1
        if bool(config.get("use_multi_core", True)):
            tile_workers = max(1, min(4, os.cpu_count() or 4))
        point_workers = max(
            1, min(int(config.get("point_workers", 2)), os.cpu_count() or 4)
        )

        def compute_aligned(index, path, frame, tile_executor, point_executor):
            if ctx.stop_requested and ctx.stop_requested():
                return index, path, None
            if frame is None:
                return index, path, None
            aligned = self.align_frame(
                reference,
                frame,
                config=config,
                stop_requested=ctx.stop_requested,
                tile_executor=tile_executor,
                point_executor=point_executor,
            )
            return index, path, aligned

        saved_count = 0
        with h5py.File(ctx.hdf5_path, "w") as h5f:
            write_alignment_cache_attrs(
                h5f,
                ref_image_path=ctx.image_paths[0],
                alignment_selection=getattr(ctx, "alignment_selection_name", self.NAME),
                alignment_algorithm=getattr(ctx, "alignment_effective_name", self.NAME),
                alignment_process="tile_optical_flow",
                cache_key=getattr(ctx, "alignment_cache_key", ""),
                cache_payload=getattr(ctx, "alignment_cache_payload", ""),
            )

            paths = list(ctx.image_paths)
            from pixel_refine_desktop.ui.views.settings.General.Language import (
                language_config,
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
                setup_balanced_batching,
            )
            compute_batch_size = max(
                1, int(getattr(ctx, "params", {}).get("batch_size", 8))
            )
            write_batch_size = max(
                1, int(getattr(ctx, "params", {}).get("h5_write_batch_size", 4))
            )
            # Index 0 is an immutable reference and is persisted once.  Every
            # compute batch contains only target frames, so batch_size=8 means
            # eight comparison images are held ready for the GPU pipeline.
            compute_plan = list(getattr(ctx, "batch_plan", []) or [])
            if not compute_plan:
                comparison_plan = setup_balanced_batching(
                    paths[1:],
                    language_config,
                    max_batch_size=compute_batch_size,
                )
                compute_plan = [
                    (start + 1, end + 1) for start, end in comparison_plan
                ]

            save_to_hdf5(
                h5f,
                "image_0",
                np.array(reference, copy=True),
                extract_exif(paths[0]),
            )
            h5f.flush()
            saved_count = 1
            print(
                "[LucasKanadeCPU] saved persistent reference image_0 "
                f"shape={reference.shape} dtype={reference.dtype}"
            )

            def acquire_compute_batch(compute_start, compute_end):
                """Reuse MFDenoiser's resident RAM batch when it is available."""
                active_start = getattr(ctx, "alignment_prefetch_start", -1)
                active_end = getattr(ctx, "alignment_prefetch_end", -1)
                batch_paths = paths[compute_start:compute_end]
                if (
                    active_start == compute_start
                    and active_end == compute_end
                    and getattr(ctx, "alignment_prefetch_frames", None)
                ):
                    batch_frames = [
                        ctx.alignment_prefetch_frames.get(path)
                        for path in batch_paths
                    ]
                    ctx.alignment_prefetch_frames.clear()
                    ctx.alignment_prefetch_start = -1
                    ctx.alignment_prefetch_end = -1
                    print(
                        f"[LucasKanadeCPU][Batch] reused prefetched resident batch "
                        f"indices={compute_start}:{compute_end} "
                        f"frames={len(batch_frames)}"
                    )
                    return batch_paths, batch_frames

                job = orchestrator._load_alignment_batch(
                    ctx, (compute_start, compute_end)
                )
                return list(job.paths), list(job.frames)

            with ThreadPoolExecutor(max_workers=1) as writer_executor:
                with ThreadPoolExecutor(max_workers=tile_workers) as tile_executor:
                    with ThreadPoolExecutor(
                        max_workers=point_workers
                    ) as point_executor:

                        def write_job(records):
                            for idx, r_path, img in records:
                                save_to_hdf5(
                                    h5f,
                                    f"image_{idx}",
                                    img,
                                    extract_exif(r_path),
                                )
                                print(
                                    f"[LucasKanadeCPU] saved image_{idx} "
                                    f"shape={img.shape} dtype={img.dtype}"
                                )
                            h5f.flush()

                        pending_writes = []
                        for compute_start, compute_end in compute_plan:
                            if ctx.stop_requested and ctx.stop_requested():
                                break

                            batch_paths, batch_frames = acquire_compute_batch(
                                compute_start, compute_end
                            )
                            print(
                                f"[LucasKanadeCPU][Batch] compute job "
                                f"indices={compute_start}:{compute_end} "
                                f"resident_frames={len(batch_frames)} "
                                f"write_batch_size={write_batch_size}"
                            )
                            write_buffer = []
                            for offset, (path, frame) in enumerate(
                                zip(batch_paths, batch_frames)
                            ):
                                if ctx.stop_requested and ctx.stop_requested():
                                    break
                                index = compute_start + offset
                                result_index, result_path, aligned = compute_aligned(
                                    index,
                                    path,
                                    frame,
                                    tile_executor,
                                    point_executor,
                                )
                                # The source is no longer needed once remap has
                                # completed; retain only the aligned result until
                                # the next HDF5 write batch is dispatched.
                                batch_frames[offset] = None
                                del frame
                                if aligned is None:
                                    continue

                                write_buffer.append(
                                    (result_index, result_path, aligned)
                                )
                                saved_count += 1
                                if len(write_buffer) >= write_batch_size:
                                    pending_writes.append(
                                        writer_executor.submit(
                                            write_job, write_buffer
                                        )
                                    )
                                    write_buffer = []
                                    # One active write plus one queued batch is
                                    # enough to overlap disk I/O with GPU work
                                    # without retaining unbounded full-res data.
                                    if len(pending_writes) >= 2:
                                        pending_writes.pop(0).result()

                                if ctx.update_progress:
                                    progress = 25 + int(
                                        ((result_index + 1) / max(1, ctx.total_images))
                                        * 65
                                    )
                                    msg = getattr(
                                        language_config,
                                        "PROGRESS_ALIGN",
                                        "Align: {}/{}",
                                    ).format(
                                        result_index + 1, ctx.total_images
                                    )
                                    ctx.update_progress(progress, msg)

                            if write_buffer:
                                pending_writes.append(
                                    writer_executor.submit(write_job, write_buffer)
                                )
                            batch_frames.clear()
                            batch_paths.clear()
                            gc.collect()

                            if len(pending_writes) >= 2:
                                pending_writes.pop(0).result()

                        for write_future in pending_writes:
                            write_future.result()
                        print(
                            f"[LucasKanadeCPU] compute_batch_size={compute_batch_size} "
                            f"h5_write_batch_size={write_batch_size} "
                            f"compute_batches={len(compute_plan)}"
                        )

        ctx.aligned_frames = []
        ctx.frames = []
        ctx.data_source = ctx.hdf5_path
        ctx.needs_alignment = False

        # Clear Vulkan buffer pool at the end of the batch process
        try:
            from taichi_vision import taichi_aot
            if hasattr(taichi_aot, "engine") and hasattr(taichi_aot.engine, "buffer_pool") and taichi_aot.engine.buffer_pool:
                taichi_aot.engine.buffer_pool.clear()
        except Exception:
            pass

        print(
            f"[LucasKanadeCPU] finished saved={saved_count} hdf5_path={ctx.hdf5_path}"
        )
        return ctx

    def run(self, ctx, frames, batch_plan=None):
        return list(frames)

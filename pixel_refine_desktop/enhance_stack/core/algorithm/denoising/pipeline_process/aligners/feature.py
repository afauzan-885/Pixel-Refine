"""Taichi Vision OFB/AKAZE feature aligner with native descriptors."""

from __future__ import annotations

import os
from typing import Optional, Tuple

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine

from ..contracts import scale_homography
from ..facade import api as _facade

__all__ = ["FeatureMatchingGPUAligner"]


class FeatureMatchingGPUAligner:
    """Taichi Vision OFB/AKAZE feature aligner with native descriptors."""

    @staticmethod
    def _validate_homography(
        homography,
        src_points,
        dst_points,
        inlier_mask,
        *,
        width: int,
        height: int,
        reproj_threshold: float = 5.0,
    ):
        """Return a safe support->reference transform or a robust translation.

        Feature matching can occasionally produce a numerically valid but
        geometrically nonsensical projective matrix (especially on repeated
        texture/blurred burst frames).  Applying such a matrix is worse than
        skipping alignment: it creates the long streaks/ghosting visible in
        Average output.  Keep this check on the small host-side point arrays;
        image buffers remain resident on the active backend.
        """

        try:
            src = np.asarray(src_points, dtype=np.float64)
            dst = np.asarray(dst_points, dtype=np.float64)
            if src.ndim != 2 or dst.ndim != 2 or src.shape[1] != 2 or dst.shape[1] != 2:
                return None
            n = min(len(src), len(dst))
            if n < 4:
                return None
            src = src[:n]
            dst = dst[:n]
            if inlier_mask is None:
                inliers = np.ones(n, dtype=bool)
            else:
                inliers = np.asarray(inlier_mask).reshape(-1)[:n].astype(bool, copy=False)
            inlier_count = int(inliers.sum())
            min_inliers = max(8, min(32, int(np.ceil(0.08 * n))))

            def _translation_fallback():
                if inlier_count < max(6, min(24, int(np.ceil(0.06 * n)))):
                    return None
                delta = dst[inliers] - src[inliers]
                if delta.size == 0 or not np.isfinite(delta).all():
                    return None
                median = np.median(delta, axis=0)
                mad = np.median(np.abs(delta - median), axis=0)
                spread = float(np.max(mad))
                max_shift = 0.5 * max(float(width), float(height))
                if (
                    not np.isfinite(median).all()
                    or spread > max(3.0, 1.5 * float(reproj_threshold))
                    or float(np.max(np.abs(median))) > max_shift
                ):
                    return None
                return np.asarray(
                    [[1.0, 0.0, median[0]], [0.0, 1.0, median[1]], [0.0, 0.0, 1.0]],
                    dtype=np.float32,
                )

            if inlier_count < min_inliers:
                return _translation_fallback()

            H = np.asarray(homography, dtype=np.float64)
            if H.shape != (3, 3) or not np.isfinite(H).all():
                return _translation_fallback()
            if abs(float(H[2, 2])) < 1e-10:
                return _translation_fallback()
            H = H / H[2, 2]

            src_h = np.concatenate(
                (src[inliers], np.ones((inlier_count, 1), dtype=src.dtype)), axis=1
            )
            projected_h = src_h @ H.T
            denom = projected_h[:, 2]
            if not np.isfinite(projected_h).all() or np.any(np.abs(denom) < 1e-8):
                return _translation_fallback()
            projected = projected_h[:, :2] / denom[:, None]
            errors = np.linalg.norm(projected - dst[inliers], axis=1)
            p90 = float(np.percentile(errors, 90)) if errors.size else float("inf")
            if not np.isfinite(errors).all() or p90 > max(10.0, 2.5 * float(reproj_threshold)):
                return _translation_fallback()

            affine = H[:2, :2]
            det = float(np.linalg.det(affine))
            if not np.isfinite(det) or det <= 0.0:
                return _translation_fallback()
            singular = np.linalg.svd(affine, compute_uv=False)
            if (
                not np.isfinite(singular).all()
                or float(singular.min()) < 0.10
                or float(singular.max()) > 10.0
            ):
                return _translation_fallback()

            corners = np.asarray(
                [[0.0, 0.0], [float(width), 0.0], [0.0, float(height)], [float(width), float(height)]],
                dtype=np.float64,
            )
            corners_h = (
                np.concatenate((corners, np.ones((4, 1), dtype=corners.dtype)), axis=1)
                @ H.T
            )
            cden = corners_h[:, 2]
            if not np.isfinite(corners_h).all() or np.any(np.abs(cden) < 1e-8):
                return _translation_fallback()
            corners_xy = corners_h[:, :2] / cden[:, None]
            margin_x = 0.75 * float(width)
            margin_y = 0.75 * float(height)
            if (
                float(corners_xy[:, 0].min()) < -margin_x
                or float(corners_xy[:, 0].max()) > float(width) + margin_x
                or float(corners_xy[:, 1].min()) < -margin_y
                or float(corners_xy[:, 1].max()) > float(height) + margin_y
            ):
                return _translation_fallback()
            return np.asarray(H, dtype=np.float32)
        except Exception:
            return None

    def __init__(
        self,
        ref_analysis_gpu: TaichiGPUBuffer,
        *,
        feature_type: str = "orb",
        work_scale: float = 0.50,
        full_shape: Optional[Tuple[int, int]] = None,
        feature_config: Optional[dict] = None,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _facade()._managed_api(taichi_aot)

        self.feature_type = str(feature_type).lower().strip()
        self.work_scale = work_scale
        self.config = feature_config or {}
        self.apap_fit_grid_size = _facade()._resolve_apap_fit_grid_size(self.config)
        requested_warp_method = str(
            self.config.get("warp_method", "homography")
        ).strip().lower()
        self.warp_method = "homography"
        if requested_warp_method != "homography":
            print(
                f"[GPU Pipeline][Align] {self.feature_type.upper()} requested "
                f"warp={requested_warp_method.upper()} is disabled; using HOMOGRAPHY"
            )
        print(
            f"[GPU Pipeline][Align] feature={self.feature_type.upper()} "
            f"warp={self.warp_method.upper()}"
        )

        ref_gray_gpu = taichi_aot.cvtColor(ref_analysis_gpu, taichi_aot.COLOR_RGB2GRAY)
        h, w = ref_gray_gpu.shape[:2]
        if full_shape is not None:
            self.target_h, self.target_w = int(full_shape[0]), int(full_shape[1])
        else:
            self.target_h, self.target_w = h, w

        if ref_analysis_gpu.shape[:2] != (self.target_h, self.target_w):
            self.work_h, self.work_w = ref_analysis_gpu.shape[:2]
        else:
            self.work_h = max(32, int(self.target_h * work_scale))
            self.work_w = max(32, int(self.target_w * work_scale))

        if (self.work_h, self.work_w) != (h, w):
            ref_gray_work = taichi_aot.resize(
                ref_gray_gpu,
                (self.work_w, self.work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
            _facade()._destroy_work_item(ref_gray_gpu)
            ref_gray_gpu = ref_gray_work

        self.ref_gray_gpu = ref_gray_gpu
        self.feature_type = "akaze" if "akaze" in self.feature_type else "ofb"
        self._feature_reference_cache = None
        self._feature_resident_matches = False
        # Reuse the reference on all resident graphics backends.  CUDA,
        # Vulkan, and OpenGL have target-qualified feature graphs; CPU keeps
        # the established stateless path as a compatibility fallback.
        try:
            feature_arch = str(getattr(taichi_aot.engine, "arch", "")).lower()
            if (
                feature_arch in {"cuda", "vulkan", "opengl"}
                and os.environ.get("TAICHI_CUDA_FEATURE_CACHE", "1") != "0"
            ):
                self._feature_reference_cache = taichi_aot.create_feature_reference_cache(
                    self.feature_type,
                    self.ref_gray_gpu,
                    ratio_threshold=float(self.config.get("ratio", 0.75)),
                    grid_size=max(8, int(self.config.get("grid_size", 32))),
                    threshold=float(
                        self.config.get(
                            "threshold", 0.001 if self.feature_type == "akaze" else 0.015
                        )
                    ),
                    margin=max(4, int(self.config.get("margin", 15))),
                    max_keypoints=int(self.config.get("max_keypoints", 1200)),
                    k_contrast=float(self.config.get("k_contrast", 0.02)),
                    num_fed_steps=max(1, int(self.config.get("num_fed_steps", 8))),
                )
                resident_algorithm_allowed = (
                    self.warp_method == "homography"
                    and (
                        self.feature_type == "ofb"
                        or (
                            self.feature_type == "akaze"
                            and os.environ.get("TAICHI_FEATURE_RESIDENT_AKAZE", "0")
                            == "1"
                        )
                    )
                )
                # CUDA's resident correspondence pack path can corrupt the
                # native heap after matching completes. Keep CUDA on the
                # cache-backed compatibility readback path until that graph
                # is validated there; feature extraction and RANSAC still run
                # on the selected backend / host respectively.
                resident_match_backend_allowed = feature_arch != "cuda"
                self._feature_resident_matches = (
                    resident_algorithm_allowed
                    and resident_match_backend_allowed
                    and os.environ.get("TAICHI_FEATURE_RESIDENT_MATCHES", "1") != "0"
                    and taichi_aot.aot_graph_available(
                        self.feature_type, "compact_matches_to_points"
                    )
                    and taichi_aot.aot_graph_available(
                        self.feature_type, "pack_compacted_points"
                    )
                )
                # The cache owns only derived keypoints/descriptors.  The
                # grayscale reference itself is no longer needed per frame.
                _facade()._destroy_work_item(self.ref_gray_gpu)
                self.ref_gray_gpu = None
                print(
                    f"[GPU Pipeline] {feature_arch.upper()} {self.feature_type.upper()} "
                    f"reference cache ready "
                    f"(levels={self._feature_reference_cache.num_levels}, "
                    f"resident_matches={self._feature_resident_matches})"
                )
        except Exception as exc:
            self._feature_reference_cache = None
            self._feature_resident_matches = False
            print(
                f"[GPU Pipeline] {feature_arch.upper()} reference cache unavailable; "
                f"using legacy path: {exc}"
            )

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        return_transform: bool = False,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _facade()._managed_api(taichi_aot)

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Alignment cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("Alignment cancelled.")

        src_for_analysis = (
            analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        )
        supp_gray_gpu = taichi_aot.cvtColor(src_for_analysis, taichi_aot.COLOR_RGB2GRAY)
        if tuple(int(v) for v in supp_gray_gpu.shape[:2]) != (self.work_h, self.work_w):
            supp_gray_work = taichi_aot.resize(
                supp_gray_gpu,
                (self.work_w, self.work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
            _facade()._destroy_work_item(supp_gray_gpu)
            supp_gray_gpu = supp_gray_work

        resident_matches = None
        try:
            if self._feature_reference_cache is not None:
                if self._feature_resident_matches:
                    resident_matches = taichi_aot.match_feature_reference_resident(
                        self._feature_reference_cache, supp_gray_gpu
                    )
                    matched = None
                else:
                    matched = taichi_aot.match_feature_reference(
                        self._feature_reference_cache, supp_gray_gpu
                    )
            elif self.feature_type == "akaze":
                matched = taichi_aot.akaze(
                    self.ref_gray_gpu,
                    supp_gray_gpu,
                    ratio_threshold=float(self.config.get("ratio", 0.75)),
                    grid_size=max(8, int(self.config.get("grid_size", 32))),
                    threshold=float(self.config.get("threshold", 0.001)),
                    margin=max(4, int(self.config.get("margin", 15))),
                    max_keypoints=int(self.config.get("max_keypoints", 1200)),
                    k_contrast=float(self.config.get("k_contrast", 0.02)),
                    num_fed_steps=max(1, int(self.config.get("num_fed_steps", 8))),
                )
            else:
                matched = taichi_aot.ofb(
                    self.ref_gray_gpu,
                    supp_gray_gpu,
                    ratio_threshold=float(self.config.get("ratio", 0.75)),
                    grid_size=max(8, int(self.config.get("grid_size", 24))),
                    threshold=float(self.config.get("threshold", 0.03)),
                    margin=max(4, int(self.config.get("margin", 15))),
                    max_keypoints=int(self.config.get("max_keypoints", 1200)),
                )
        finally:
            _facade()._destroy_work_item(supp_gray_gpu)

        H_matrix = None
        apap_ref_points = None
        apap_support_points = None
        matched_pair_count = 0
        if resident_matches is not None:
            matched_pair_count = int(resident_matches.count)
        elif matched is not None and len(matched) >= 2:
            matched_pair_count = min(len(matched[0]), len(matched[1]))
        scale_x = self.target_w / float(self.work_w)
        scale_y = self.target_h / float(self.work_h)
        if resident_matches is not None:
            try:
                if resident_matches.count >= 4:
                    pts_ref_gpu, pts_supp_gpu = resident_matches.point_views()
                    reproj_threshold = max(
                        0.5, float(self.config.get("ransac_threshold", 5.0))
                    )
                    ransac_hypotheses = max(
                        64, int(self.config.get("ransac_hypotheses", 256))
                    )
                    ransac_iters = max(1, int(self.config.get("ransac_iters", 2)))
                    if self.feature_type == "ofb":
                        from ....alignment.feature_matching.OFB import OFBAlgorithm

                        H_candidate, inlier_mask = OFBAlgorithm._find_homography(
                            pts_supp_gpu.to_numpy(),
                            pts_ref_gpu.to_numpy(),
                            threshold=reproj_threshold,
                            hypotheses=ransac_hypotheses,
                            refinements=ransac_iters,
                        )
                    else:
                        H_candidate, inlier_mask = taichi_aot.find_homography(
                            pts_supp_gpu,
                            pts_ref_gpu,
                            method="RANSAC",
                            ransacReprojThreshold=reproj_threshold,
                            n_hypotheses=ransac_hypotheses,
                            max_iters=ransac_iters,
                            return_gpu=True,
                        )
                    if H_candidate is not None:
                        if self.feature_type == "ofb":
                            H_matrix = scale_homography(
                                np.asarray(H_candidate, dtype=np.float32),
                                source_shape=(self.work_h, self.work_w),
                                destination_shape=(self.target_h, self.target_w),
                            )
                        else:
                            H_matrix = scale_homography(
                                H_candidate,
                                source_shape=(self.work_h, self.work_w),
                                destination_shape=(self.target_h, self.target_w),
                            )
                    if self.warp_method == "apap":
                        if H_matrix is not None:
                            pts_ref = np.ascontiguousarray(
                                pts_ref_gpu.to_numpy(), dtype=np.float32
                            )
                            pts_supp = np.ascontiguousarray(
                                pts_supp_gpu.to_numpy(), dtype=np.float32
                            )
                            apap_ref_points, apap_support_points = (
                                _facade()._select_ransac_inlier_correspondences(
                                    pts_ref, pts_supp, inlier_mask
                                )
                            )
                            scale = np.array([scale_x, scale_y], dtype=np.float32)
                            apap_ref_points *= scale
                            apap_support_points *= scale
                    if isinstance(inlier_mask, TaichiGPUBuffer):
                        get_engine().sync()
                        _facade()._destroy_work_item(inlier_mask)
            finally:
                resident_matches.close()
        elif matched is not None and len(matched) >= 2:
            pts_ref = np.ascontiguousarray(matched[0], dtype=np.float32)
            pts_supp = np.ascontiguousarray(matched[1], dtype=np.float32)
            if len(pts_ref) >= 4 and len(pts_supp) >= 4:
                pts_ref *= np.array([scale_x, scale_y], dtype=np.float32)
                pts_supp *= np.array([scale_x, scale_y], dtype=np.float32)
                # Spend extra RANSAC work only when there are enough
                # correspondences for it to improve model selection.  Sparse
                # AKAZE matches already fail closed via the geometry gate.
                akaze_ransac_quality = len(pts_ref) >= 64
                ransac_hypotheses = max(
                    64,
                    int(
                        self.config.get(
                            "ransac_hypotheses",
                            1024
                            if self.feature_type == "akaze" and akaze_ransac_quality
                            else 256,
                        )
                    ),
                )
                ransac_iters = max(
                    1,
                    int(
                        self.config.get(
                            "ransac_iters",
                            3
                            if self.feature_type == "akaze" and akaze_ransac_quality
                            else 2,
                        )
                    ),
                )
                reproj_threshold = max(
                    0.5, float(self.config.get("ransac_threshold", 5.0))
                )
                if self.feature_type == "ofb":
                    from ....alignment.feature_matching.OFB import OFBAlgorithm

                    H_candidate, inlier_mask = OFBAlgorithm._find_homography(
                        pts_supp,
                        pts_ref,
                        threshold=reproj_threshold,
                        hypotheses=ransac_hypotheses,
                        refinements=ransac_iters,
                    )
                    H_matrix = (
                        None
                        if H_candidate is None
                        else np.asarray(H_candidate, dtype=np.float32)
                    )
                else:
                    H_candidate, inlier_mask = taichi_aot.find_homography(
                        pts_supp,
                        pts_ref,
                        method="RANSAC",
                        ransacReprojThreshold=reproj_threshold,
                        n_hypotheses=ransac_hypotheses,
                        max_iters=ransac_iters,
                        return_gpu=False,
                    )
                    # AKAZE's binary matches are more vulnerable to repeated
                    # texture producing a plausible-looking but wrong H.
                    H_matrix = self._validate_homography(
                        H_candidate,
                        pts_supp,
                        pts_ref,
                        inlier_mask,
                        width=self.target_w,
                        height=self.target_h,
                        reproj_threshold=reproj_threshold,
                    )
                if self.warp_method == "apap" and H_matrix is not None:
                    apap_ref_points, apap_support_points = (
                        _facade()._select_ransac_inlier_correspondences(
                            pts_ref, pts_supp, inlier_mask
                        )
                    )

        if H_matrix is not None:
            if self.warp_method == "apap":
                if apap_ref_points is None or apap_support_points is None:
                    raise RuntimeError(
                        f"{self.feature_type.upper()} APAP warp needs at least four matched point pairs"
                    )
                from taichi_vision.taichi_algorithm.alignment.apap import fit_apap

                print(
                    "[GPU Pipeline][Align] APAP RANSAC inliers="
                    f"{len(apap_ref_points)} (no second correspondence filter)"
                )
                # RANSAC's H maps support -> reference. APAP's inverse map
                # consumes reference coordinates and returns support
                # coordinates, so reuse the validated transform in reverse
                # instead of estimating the same global control a second time.
                apap_global_h = np.linalg.inv(
                    np.asarray(H_matrix, dtype=np.float64)
                )
                if return_transform:
                    # RAW merges the CFA carrier, not this RGB proxy. Return
                    # the local inverse field instead of losing APAP here by
                    # returning only its global RANSAC homography.
                    apap_warp = fit_apap(
                        apap_ref_points,
                        apap_support_points,
                        global_homography=apap_global_h,
                        grid_shape=(self.apap_fit_grid_size,) * 2,
                    )
                    flow = apap_warp.to_flow(
                        (33, 33), full_shape=(self.target_h, self.target_w)
                    )
                    flow_gpu = taichi_aot.upload(flow, is_vector=False)
                    warped_primary = None
                    warped_secondary = None
                    try:
                        if supp_linear_gpu is not None:
                            warped_primary = taichi_aot.remap_with_flow(
                                supp_linear_gpu, flow_gpu,
                                int(supp_linear_gpu.shape[0]), int(supp_linear_gpu.shape[1]),
                                return_gpu=True,
                            )
                        if secondary_frame_to_warp is not None:
                            warped_secondary = taichi_aot.remap_with_flow(
                                secondary_frame_to_warp, flow_gpu,
                                int(secondary_frame_to_warp.shape[0]),
                                int(secondary_frame_to_warp.shape[1]),
                                return_gpu=True,
                            )
                    except BaseException:
                        for buffer in (warped_primary, warped_secondary, flow_gpu):
                            if buffer is not None:
                                _facade()._destroy_work_item(buffer)
                        raise
                    print(
                        "[GPU Pipeline][Align] APAP carrier transform=local_flow "
                        f"grid={flow.shape[:2]} model_grid="
                        f"{self.apap_fit_grid_size}x{self.apap_fit_grid_size} "
                        "warp=AOT-flow units=flow_pixels"
                    )
                    return warped_primary, warped_secondary, flow_gpu

                from taichi_vision.taichi_algorithm.alignment.mesh_warp import (
                    warp_apap,
                )

                warped_primary = None
                if supp_linear_gpu is not None:
                    warped_primary = _facade()._track_gpu_result(
                        warp_apap(
                            supp_linear_gpu,
                            apap_ref_points,
                            apap_support_points,
                            dsize=(self.target_w, self.target_h),
                            global_homography=apap_global_h,
                            fit_grid_shape=(self.apap_fit_grid_size,) * 2,
                            return_gpu=True,
                        )
                    )
            elif supp_linear_gpu is None:
                warped_primary = None
            elif self.feature_type == "ofb":
                from ....alignment.feature_matching.OFB import OFBAlgorithm

                prim_h, prim_w = (int(v) for v in supp_linear_gpu.shape[:2])
                H_prim = (
                    scale_homography(
                        H_matrix,
                        source_shape=(self.target_h, self.target_w),
                        destination_shape=(prim_h, prim_w),
                    )
                    if (prim_h, prim_w) != (self.target_h, self.target_w)
                    else H_matrix
                )
                primary_np = np.ascontiguousarray(supp_linear_gpu.to_numpy())
                warped_primary_np = OFBAlgorithm._warp_perspective(
                    primary_np, H_prim, (prim_w, prim_h)
                )
                warped_primary = taichi_aot.upload(
                    np.ascontiguousarray(warped_primary_np), is_vector=False
                )
            else:
                prim_h, prim_w = (int(v) for v in supp_linear_gpu.shape[:2])
                H_prim = (
                    scale_homography(
                        H_matrix,
                        source_shape=(self.target_h, self.target_w),
                        destination_shape=(prim_h, prim_w),
                    )
                    if (prim_h, prim_w) != (self.target_h, self.target_w)
                    else H_matrix
                )
                warped_primary = taichi_aot.warp_perspective(
                    supp_linear_gpu,
                    H_prim,
                    (prim_w, prim_h),
                    return_gpu=True,
                )
            warped_secondary = None
            if secondary_frame_to_warp is not None:
                scale_mat = np.array(
                    [[1.0 / scale_x, 0, 0], [0, 1.0 / scale_y, 0], [0, 0, 1.0]],
                    dtype=np.float32,
                )
                scale_mat_inv = np.array(
                    [[scale_x, 0, 0], [0, scale_y, 0], [0, 0, 1.0]],
                    dtype=np.float32,
                )
                H_work = scale_mat @ H_matrix @ scale_mat_inv
                if self.warp_method == "apap":
                    scale = np.array([scale_x, scale_y], dtype=np.float32)
                    work_ref_points = apap_ref_points / scale
                    work_support_points = apap_support_points / scale
                    warped_secondary = _facade()._track_gpu_result(
                        warp_apap(
                            secondary_frame_to_warp,
                            work_ref_points,
                            work_support_points,
                            dsize=(self.work_w, self.work_h),
                            global_homography=np.linalg.inv(
                                np.asarray(H_work, dtype=np.float64)
                            ),
                            return_gpu=True,
                        )
                    )
                elif self.feature_type == "ofb":
                    secondary_np = np.ascontiguousarray(
                        secondary_frame_to_warp.to_numpy()
                    )
                    warped_secondary_np = OFBAlgorithm._warp_perspective(
                        secondary_np, H_work, (self.work_w, self.work_h)
                    )
                    warped_secondary = taichi_aot.upload(
                        np.ascontiguousarray(warped_secondary_np), is_vector=False
                    )
                else:
                    warped_secondary = taichi_aot.warp_perspective(
                        secondary_frame_to_warp,
                        H_work,
                        (self.work_w, self.work_h),
                        return_gpu=True,
                    )
            if return_transform:
                return warped_primary, warped_secondary, np.ascontiguousarray(
                    H_matrix, dtype=np.float32
                )
            return warped_primary, warped_secondary
        else:
            print(
                f"[GPU Pipeline][Align] feature={self.feature_type.upper()} "
                f"warp={self.warp_method.upper()} not_applied=no_trusted_transform "
                f"matched_pairs={matched_pair_count}; support remains unaligned"
            )
            if return_transform:
                return supp_linear_gpu, secondary_frame_to_warp, None
            return supp_linear_gpu, secondary_frame_to_warp

    def close(self):
        cache = getattr(self, "_feature_reference_cache", None)
        if cache is not None:
            try:
                cache.close()
            except Exception:
                pass
        self._feature_reference_cache = None
        self._feature_resident_matches = False
        ref_gray_gpu = getattr(self, "ref_gray_gpu", None)
        if ref_gray_gpu is not None and hasattr(ref_gray_gpu, "destroy"):
            _facade()._destroy_work_item(ref_gray_gpu)
        self.ref_gray_gpu = None

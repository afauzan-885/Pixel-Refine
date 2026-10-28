"""Hybrid homography: AOT hypothesis search and explicit float64 host refinement."""
from __future__ import annotations

import os
import time

import numpy as np

from .quality import _consensus_errors, _normalize_points, _refine_consensus


def find_homography_hybrid(pts1, pts2, threshold, n_hypotheses, max_iters, return_gpu, seed):
    from .. import aot_api as api

    if pts1 is None or pts2 is None:
        return None, None
    is_source_gpu = isinstance(pts1, api.TaichiGPUBuffer)
    is_target_gpu = isinstance(pts2, api.TaichiGPUBuffer)
    # This host phase is unconditional, not a fallback on GPU failure. Device
    # input incurs a point readback; caller-owned device buffers stay alive.
    source = np.asarray(pts1.to_numpy() if is_source_gpu else pts1, dtype=np.float64)
    target = np.asarray(pts2.to_numpy() if is_target_gpu else pts2, dtype=np.float64)
    if source.ndim == 3 and source.shape[1:] == (1, 2):
        source = source[:, 0]
    if target.ndim == 3 and target.shape[1:] == (1, 2):
        target = target[:, 0]
    if source.ndim != 2 or source.shape[1:] != (2,) or target.shape != source.shape:
        raise ValueError("homography expects matching Nx2 or Nx1x2 point arrays")
    n_pts = len(source)
    if n_pts < 4 or not np.isfinite(source).all() or not np.isfinite(target).all():
        return None, None
    threshold = float(threshold)
    if not np.isfinite(threshold) or threshold <= 0:
        raise ValueError("ransacReprojThreshold must be finite and positive")
    n_hypotheses, max_iters = int(n_hypotheses), int(max_iters)
    if n_hypotheses < 1 or max_iters < 1:
        raise ValueError("n_hypotheses and max_iters must be positive")
    for points in (source, target):
        normalized, _ = _normalize_points(points)
        if np.linalg.matrix_rank(np.column_stack((normalized, np.ones(n_pts)))) < 3:
            return None, None

    if seed is None:
        try:
            seed = int(os.environ.get("PIXEL_REFINE_RANSAC_SEED", ""))
        except ValueError:
            pass
    seed_base = (int(seed) if seed is not None else int(time.time() * 1000)) & 0x7FFFFFFF
    owned = []
    try:
        source_gpu = pts1 if is_source_gpu else api.upload(np.ascontiguousarray(source, dtype=np.float32))
        if not is_source_gpu:
            owned.append(source_gpu)
        target_gpu = pts2 if is_target_gpu else api.upload(np.ascontiguousarray(target, dtype=np.float32))
        if not is_target_gpu:
            owned.append(target_gpu)
        candidates_gpu = api.engine.allocate((n_hypotheses, 9), dtype=np.float32)
        owned.append(candidates_gpu)
        scores_gpu = api.engine.allocate((n_hypotheses,), dtype=np.int32)
        owned.append(scores_gpu)
        best, best_cost = None, float("inf")
        for iteration in range(max_iters):
            api._mod("ransac").run(
                "ransac_homography", pts1=source_gpu, pts2=target_gpu, n_pts=n_pts,
                n_hypotheses=n_hypotheses, reproj_threshold=threshold,
                H_candidates=candidates_gpu, inlier_counts=scores_gpu,
                seed_offset=(seed_base + iteration * 31337) & 0x7FFFFFFF,
            )
            scores = scores_gpu.to_numpy()
            candidates = candidates_gpu.to_numpy().reshape(-1, 3, 3).astype(np.float64)
            # Bounded local optimization of GPU candidates only. No host RANSAC
            # or OpenCV estimation is used, including on device exceptions.
            shortlist = np.argsort(-scores, kind="stable")[:min(8, n_hypotheses)]
            for index in shortlist:
                candidate = candidates[index]
                if scores[index] <= 0 or not np.isfinite(candidate).all():
                    continue
                candidate, mask, cost = _refine_consensus(
                    source, target, candidate, model="homography", threshold=threshold,
                )
                if mask.sum() >= 4 and cost < best_cost:
                    best, best_cost = candidate, cost
        if best is None:
            return None, None
        # Classify with the returned float64 matrix, not a rounded f32 copy.
        mask = _consensus_errors(source, target, best) <= threshold * threshold
        if return_gpu:
            return best, api.upload(mask.astype(np.int32))
        return best, mask.astype(np.uint8).reshape(-1, 1)
    finally:
        for buffer in reversed(owned):
            buffer.release()

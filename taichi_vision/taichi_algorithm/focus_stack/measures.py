"""Focus-quality maps using existing AOT gradient primitives where possible."""

from __future__ import annotations

import numpy as np

from ..pipeline_common import as_gray_float32


MAX_POLICY_PIXELS = 55_000_000
MAX_SMOOTH_RADIUS = 8


def _box_mean(image: np.ndarray, radius: int) -> np.ndarray:
    radius = int(radius)
    if radius > MAX_SMOOTH_RADIUS:
        raise ValueError(f"radius is limited to {MAX_SMOOTH_RADIUS} for bounded host policy work")
    data = np.asarray(image, dtype=np.float32)
    if radius <= 0:
        return data.copy()
    padded = np.pad(data, radius, mode="edge")
    result = np.zeros_like(data, dtype=np.float32)
    width = 2 * radius + 1
    for dy in range(width):
        for dx in range(width):
            result += padded[dy : dy + data.shape[0], dx : dx + data.shape[1]]
    result /= float(width * width)
    return result


def _local_variance(image: np.ndarray, radius: int) -> np.ndarray:
    mean = _box_mean(image, radius)
    mean_sq = _box_mean(np.square(image, dtype=np.float32), radius)
    return np.maximum(mean_sq - np.square(mean, dtype=np.float32), 0.0).astype(np.float32)


def _numpy_laplacian(image: np.ndarray) -> np.ndarray:
    padded = np.pad(image, 1, mode="edge")
    return (
        padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        + padded[1:-1, :-2]
        + padded[1:-1, 2:]
        - 4.0 * padded[1:-1, 1:-1]
    ).astype(np.float32)


def _numpy_sobel(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    padded = np.pad(image, 1, mode="edge")
    dx = (
        padded[:-2, 2:]
        + 2.0 * padded[1:-1, 2:]
        + padded[2:, 2:]
        - padded[:-2, :-2]
        - 2.0 * padded[1:-1, :-2]
        - padded[2:, :-2]
    )
    dy = (
        padded[2:, :-2]
        + 2.0 * padded[2:, 1:-1]
        + padded[2:, 2:]
        - padded[:-2, :-2]
        - 2.0 * padded[:-2, 1:-1]
        - padded[:-2, 2:]
    )
    return dx.astype(np.float32), dy.astype(np.float32)


def _derivatives(image: np.ndarray, backend: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    backend = str(backend).lower()
    if backend == "numpy":
        lap = _numpy_laplacian(image)
        dx, dy = _numpy_sobel(image)
        return lap, dx, dy
    if backend == "taichi":
        from .native import gradients_taichi

        return gradients_taichi(image)
    if backend != "aot":
        raise ValueError("backend must be 'aot', 'taichi', or the explicit host backend 'numpy'")
    # These wrappers dispatch the already compiled gradients graphs.  Import
    # lazily so a host-only test does not initialise the AOT runtime.
    from ..aot_api import laplacian, sobel

    lap = np.ascontiguousarray(laplacian(image), dtype=np.float32)
    dx, dy = sobel(image)
    return lap, np.ascontiguousarray(dx, dtype=np.float32), np.ascontiguousarray(dy, dtype=np.float32)


def focus_measure(image, *, method: str = "tenengrad", radius: int = 2, backend: str = "aot") -> np.ndarray:
    """Compute a per-pixel focus-quality map.

    Methods are ``variance_laplacian``, ``modified_laplacian``, ``tenengrad``,
    ``brenner``, and ``local_variance``.  Derivative-based methods use the
    existing AOT Sobel/Laplacian graphs when ``backend="aot"``.  The
    ``backend="numpy"`` route is explicit and serves as a deterministic oracle;
    ``backend="taichi"`` provides the two-pixel Brenner JIT leaf.  No failure
    in an AOT or JIT route is converted into another backend implicitly.
    """

    gray = as_gray_float32(image, name="image")
    if int(gray.size) > MAX_POLICY_PIXELS:
        raise ValueError(
            f"focus policy input has {int(gray.size):,} pixels; maximum is {MAX_POLICY_PIXELS:,}"
        )
    if not np.isfinite(gray).all():
        raise ValueError("image must contain only finite values")
    radius = int(radius)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    name = str(method).lower().replace("-", "_").replace(" ", "_")

    if name == "local_variance":
        if str(backend).lower() == "aot":
            raise NotImplementedError(
                "local_variance has no qualified AOT reduction graph; "
                "use backend='numpy' or backend='taichi' explicitly"
            )
        return _local_variance(gray, radius)

    if name in {"variance_laplacian", "laplacian_variance", "modified_laplacian", "tenengrad", "sobel"}:
        lap, dx, dy = _derivatives(gray, backend)
        if name in {"variance_laplacian", "laplacian_variance"}:
            return _local_variance(lap, radius)
        if name == "modified_laplacian":
            # The existing Laplacian graph is the shared second-derivative
            # primitive.  Its local energy is the stable scalar proxy for the
            # modified-Laplacian measure and avoids another kernel family.
            return _box_mean(np.abs(lap), radius)
        return _box_mean(np.square(dx, dtype=np.float32) + np.square(dy, dtype=np.float32), radius)

    if name == "brenner":
        backend_name = str(backend).lower()
        if backend_name == "taichi":
            from .native import brenner_taichi

            result = brenner_taichi(gray)
        elif backend_name == "numpy":
            result = np.zeros_like(gray, dtype=np.float32)
            if gray.shape[1] > 2:
                result[:, :-2] = np.square(gray[:, 2:] - gray[:, :-2], dtype=np.float32)
        else:
            raise NotImplementedError("brenner has no qualified AOT leaf; use backend='numpy' or backend='taichi'")
        return _box_mean(result, radius)

    raise ValueError(
        "unknown focus method; expected variance_laplacian, modified_laplacian, "
        "tenengrad, brenner, or local_variance"
    )


__all__ = ["focus_measure"]

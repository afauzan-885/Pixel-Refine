"""Public AOT wrappers for the remaining image-processing families.

The wrappers keep host-side validation and small policy steps explicit while
dispatching the pixel loops through target-qualified TCM modules.
"""

from __future__ import annotations

import numpy as np

from taichi_vision.taichi_algorithm.aot_api.research import _as_f32, _dispatch


def _structure(kernel, ksize):
    if kernel is None:
        size = int(ksize)
        if size <= 0 or size > 21:
            raise ValueError("ksize must be in [1, 21]")
        data = np.ones((size, size), dtype=np.int32)
    else:
        data = np.asarray(kernel, dtype=np.int32)
        if data.ndim == 1:
            side = int(np.sqrt(data.size))
            if side * side != data.size:
                raise ValueError("flat morphology kernel must be square")
            data = data.reshape(side, side)
        if data.ndim != 2 or any(value <= 0 or value > 21 for value in data.shape):
            raise ValueError("morphology kernel must be a 2D array no larger than 21x21")
    padded = np.zeros((21, 21), dtype=np.int32)
    padded[: data.shape[0], : data.shape[1]] = data
    return padded, int(data.shape[0]), int(data.shape[1])


def _morphology_dispatch(data, structure, kh, kw, operation):
    """Dispatch one morphology pass without invoking the block planner."""
    graph = f"morphology_{operation}_{'3d' if data.ndim == 3 else '2d'}"
    h, w = data.shape[:2]
    scalars = {"kh": int(kh), "kw": int(kw), "h": h, "w": w}
    if data.ndim == 3:
        scalars["channels"] = data.shape[2]
    return _dispatch(
        "morphology",
        graph,
        inputs={"src": data, "structure": structure},
        outputs={"dst": (data.shape, np.float32)},
        scalars=scalars,
    )


def _morphology(src, kernel, ksize, iterations, operation):
    data = _as_f32(src)
    structure, kh, kw = _structure(kernel, ksize)
    if iterations < 1:
        raise ValueError("iterations must be positive")
    if data.ndim not in (2, 3):
        raise ValueError("morphology input must be 2D or 3D")

    # A morphology pass is a bounded stencil.  The block helper receives a
    # halo large enough for the selected structuring element and writes only
    # the core, so an internal tile edge never becomes an artificial border.
    # Import lazily to avoid the extended -> package -> extended import cycle.
    try:
        # ``extended_aot`` lives under ``image_processing`` while the shared
        # executor is owned by ``aot_api``.  A relative import here resolves
        # to the empty image_processing package and silently disables block
        # execution for every extended operation.
        from taichi_vision.taichi_algorithm.aot_api import _run_blockwise
    except ImportError:  # pragma: no cover - only possible during import
        _run_blockwise = None

    result = data
    halo = max(int(kh) // 2, int(kw) // 2)
    for iteration in range(int(iterations)):
        block_result = None
        if _run_blockwise is not None and isinstance(result, np.ndarray):
            block_result = _run_blockwise(
                "morphology",
                (result,),
                result.shape,
                np.float32,
                lambda tile: _morphology_dispatch(
                    tile, structure, kh, kw, operation
                ),
                halo=halo,
                params={
                    "operation": str(operation),
                    "kh": int(kh),
                    "kw": int(kw),
                    "structure": structure.tobytes().hex(),
                    "iteration": int(iteration),
                },
            )
        result = (
            block_result
            if block_result is not None
            else _morphology_dispatch(result, structure, kh, kw, operation)
        )
    return result


def dilate_aot(src, kernel=None, ksize=3, iterations=1):
    return _morphology(src, kernel, ksize, iterations, "dilate")


def erode_aot(src, kernel=None, ksize=3, iterations=1):
    return _morphology(src, kernel, ksize, iterations, "erode")


def histogram_aot(src, bins=256, range=(0, 256)):
    data = _as_f32(src)
    bins = int(bins)
    if bins <= 0:
        raise ValueError("bins must be positive")
    range_min, range_max = float(range[0]), float(range[1])
    if data.ndim == 1:
        data = np.ascontiguousarray(data.reshape(1, -1))
    if data.ndim == 2:
        graph = "histogram_2d"
        scalars = {"h": data.shape[0], "w": data.shape[1]}
    elif data.ndim == 3:
        graph = "histogram_3d"
        scalars = {"h": data.shape[0], "w": data.shape[1], "channels": data.shape[2]}
    else:
        raise ValueError("histogram input must be 1D, 2D, or 3D")
    counts = _dispatch(
        "histogram",
        graph,
        inputs={"src": data},
        outputs={"hist": np.zeros(bins, dtype=np.int32)},
        scalars={**scalars, "bins": bins, "range_min": range_min, "range_max": range_max},
    )
    return counts, np.linspace(range_min, range_max, bins + 1, dtype=np.float32)


def ssim_aot(img1, img2, window_size=11, data_range=None, k1=0.01, k2=0.03):
    raw_first = img1.to_numpy() if hasattr(img1, "to_numpy") else np.asarray(img1)
    first = _as_f32(img1)
    second = _as_f32(img2)
    if first.shape != second.shape:
        raise ValueError("SSIM inputs must have identical shapes")
    window_size = int(window_size)
    if window_size < 1 or window_size > 21 or window_size % 2 == 0:
        raise ValueError("window_size must be odd and no larger than 21")
    if data_range is None:
        if np.issubdtype(raw_first.dtype, np.integer):
            data_range = float(np.iinfo(raw_first.dtype).max)
        else:
            data_range = float(np.max(first) - np.min(first)) or 1.0
    c1 = float(k1 * data_range) ** 2
    c2 = float(k2 * data_range) ** 2
    channels = first.shape[2] if first.ndim == 3 else 1
    score = 0.0
    for channel in range(channels):
        a = first if first.ndim == 2 else np.ascontiguousarray(first[..., channel])
        b = second if second.ndim == 2 else np.ascontiguousarray(second[..., channel])
        result = _dispatch(
            "ssim",
            "ssim_2d",
            inputs={"img1": a, "img2": b},
            outputs={"result": np.zeros(2, dtype=np.float32)},
            scalars={"h": a.shape[0], "w": a.shape[1], "radius": window_size // 2, "c1": c1, "c2": c2},
        )
        score += float(result[0] / max(result[1], 1.0))
    return score / channels


def warp_affine_aot(src, matrix, dsize):
    data = _as_f32(src)
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.shape != (2, 3):
        raise ValueError("matrix must have shape (2, 3)")
    width, height = (int(dsize[0]), int(dsize[1]))
    if width <= 0 or height <= 0:
        raise ValueError("dsize must be positive")
    homogeneous = np.eye(3, dtype=np.float32)
    homogeneous[:2] = matrix
    inverse = np.linalg.inv(homogeneous)[:2].astype(np.float32)
    graph = "warp_affine_3d" if data.ndim == 3 else "warp_affine_2d"
    scalars = {"h_src": data.shape[0], "w_src": data.shape[1], "h_dst": height, "w_dst": width}
    if data.ndim == 3:
        scalars["channels"] = data.shape[2]
        shape = (height, width, data.shape[2])
    elif data.ndim == 2:
        shape = (height, width)
    else:
        raise ValueError("warp_affine input must be 2D or 3D")
    return _dispatch("warp_affine", graph, inputs={"src": data, "matrix": inverse}, outputs={"dst": (shape, np.float32)}, scalars=scalars)


def _filter2d_dispatch(data, padded, kh, kw):
    graph = "filter2d_3d" if data.ndim == 3 else "filter2d_2d"
    scalars = {
        "kh": int(kh),
        "kw": int(kw),
        "h": data.shape[0],
        "w": data.shape[1],
    }
    if data.ndim == 3:
        scalars["channels"] = data.shape[2]
    return _dispatch(
        "filter2d",
        graph,
        inputs={"src": data, "kernel": padded},
        outputs={"dst": (data.shape, np.float32)},
        scalars=scalars,
    )


def filter2d_aot(src, kernel, border_mode="REFLECT_101"):
    if str(border_mode).upper() not in {"REFLECT_101", "BORDER_REFLECT_101", "DEFAULT"}:
        raise ValueError("the portable filter2d graph currently supports REFLECT_101")
    data = _as_f32(src)
    filt = np.asarray(kernel, dtype=np.float32)
    if filt.ndim != 2 or any(value <= 0 or value > 31 for value in filt.shape):
        raise ValueError("kernel must be a 2D array no larger than 31x31")
    padded = np.zeros((31, 31), dtype=np.float32)
    padded[: filt.shape[0], : filt.shape[1]] = filt
    if data.ndim not in (2, 3):
        raise ValueError("filter2d input must be 2D or 3D")

    try:
        from taichi_vision.taichi_algorithm.aot_api import _run_blockwise
    except ImportError:  # pragma: no cover - only possible during import
        _run_blockwise = None
    halo = max(int(filt.shape[0]) // 2, int(filt.shape[1]) // 2)
    if _run_blockwise is not None:
        result = _run_blockwise(
            "filter2d",
            (data,),
            data.shape,
            np.float32,
            lambda tile: _filter2d_dispatch(
                tile, padded, filt.shape[0], filt.shape[1]
            ),
            halo=halo,
            params={
                "kh": int(filt.shape[0]),
                "kw": int(filt.shape[1]),
                "border_mode": str(border_mode).upper(),
                "kernel": filt.tobytes().hex(),
            },
        )
        if result is not None:
            return result
    return _filter2d_dispatch(data, padded, filt.shape[0], filt.shape[1])


_BORDER_MODES = {"CONSTANT": 0, "REPLICATE": 1, "REFLECT": 2, "WRAP": 3, "REFLECT_101": 4, "REFLECT101": 4, "DEFAULT": 4}


def copy_make_border_aot(src, top, bottom, left, right, border_type="REFLECT_101", value=0.0):
    data = _as_f32(src)
    mode = _BORDER_MODES.get(str(border_type).upper(), border_type if isinstance(border_type, int) else None)
    if mode not in range(5):
        raise ValueError("unsupported border_type")
    if min(int(top), int(bottom), int(left), int(right)) < 0:
        raise ValueError("border sizes must be non-negative")
    constant_values = np.asarray(value, dtype=np.float32).reshape(-1)
    if constant_values.size == 0:
        raise ValueError("border value must contain at least one scalar")
    shape = (data.shape[0] + int(top) + int(bottom), data.shape[1] + int(left) + int(right), *data.shape[2:])
    graph = "copy_make_border_3d" if data.ndim == 3 else "copy_make_border_2d"
    scalars = {"top": int(top), "left": int(left), "mode": int(mode)}
    if data.ndim == 3:
        scalars["channels"] = data.shape[2]
        if constant_values.size not in (1, data.shape[2]):
            raise ValueError("3D border value must be scalar or contain one value per channel")
        if constant_values.size == data.shape[2]:
            return _dispatch("copy_make_border", "copy_make_border_3d_values", inputs={"src": data, "constants": np.ascontiguousarray(constant_values)}, outputs={"dst": (shape, np.float32)}, scalars=scalars)
        scalars["constant"] = float(constant_values[0])
    else:
        scalars["constant"] = float(constant_values[0])
    return _dispatch("copy_make_border", graph, inputs={"src": data}, outputs={"dst": (shape, np.float32)}, scalars=scalars)


def _normalize_dispatch(data, alpha, beta, mode, *, src_min=None, src_max=None, norm_value=None):
    if mode == "MINMAX":
        graph = "normalize_minmax_2d"
        scalars = {
            "h": data.shape[0],
            "w": data.shape[1],
            "alpha": float(alpha),
            "beta": float(beta),
            "src_min": float(src_min),
            "src_max": float(src_max),
        }
    else:
        graph = "normalize_norm_2d"
        scalars = {
            "h": data.shape[0],
            "w": data.shape[1],
            "alpha": float(alpha),
            "norm_value": float(norm_value),
        }
    return _dispatch(
        "normalize",
        graph,
        inputs={"src": data},
        outputs={"dst": (data.shape, np.float32)},
        scalars=scalars,
    )


def normalize_aot(src, alpha=0.0, beta=255.0, norm_type="MINMAX"):
    data = _as_f32(src)
    if data.ndim == 3:
        return np.stack([normalize_aot(data[..., c], alpha, beta, norm_type) for c in range(data.shape[2])], axis=2)
    if data.ndim != 2:
        raise ValueError("normalize input must be 2D or 3D")
    name = str(norm_type).upper() if isinstance(norm_type, str) else int(norm_type)
    if name == "MINMAX" or name == 32:
        # A single-kernel min/max reduction is serial on CPU but can be
        # scheduled as competing workgroups on graphics backends.  Resolve
        # the two scalar statistics host-side and keep the pixel transform
        # native/AOT so results are deterministic on every target.
        src_min = float(np.min(data))
        src_max = float(np.max(data))
        mode_params = {"mode": "MINMAX", "src_min": src_min, "src_max": src_max}
        dispatch = lambda tile: _normalize_dispatch(
            tile,
            alpha,
            beta,
            "MINMAX",
            src_min=src_min,
            src_max=src_max,
        )
    else:
        mode = {"INF": 0, "L1": 1, "L2": 2}.get(name, name)
        if mode not in (0, 1, 2):
            raise ValueError("norm_type must be MINMAX, INF, L1, or L2")
        absolute = np.abs(data)
        norm_value = float(np.max(absolute) if mode == 0 else np.sum(absolute) if mode == 1 else np.sqrt(np.sum(absolute * absolute)))
        mode_params = {"mode": int(mode), "norm_value": norm_value}
        dispatch = lambda tile: _normalize_dispatch(
            tile, alpha, beta, "NORM", norm_value=norm_value
        )

    try:
        from taichi_vision.taichi_algorithm.aot_api import _run_blockwise
    except ImportError:  # pragma: no cover - only possible during import
        _run_blockwise = None
    if _run_blockwise is not None:
        result = _run_blockwise(
            "normalize",
            (data,),
            data.shape,
            np.float32,
            dispatch,
            params=mode_params,
        )
        if result is not None:
            return result
    return _normalize_dispatch(
        data,
        alpha,
        beta,
        "MINMAX" if mode_params["mode"] == "MINMAX" else "NORM",
        src_min=mode_params.get("src_min"),
        src_max=mode_params.get("src_max"),
        norm_value=mode_params.get("norm_value"),
    )


_THRESHOLD_MODES = {"BINARY": 0, "BINARY_INV": 1, "TRUNC": 2, "TOZERO": 3, "TOZERO_INV": 4}


def _otsu_threshold(data):
    values = np.asarray(data, dtype=np.float32)
    low, high = float(values.min()), float(values.max())
    if high <= low:
        return low
    hist, _ = np.histogram(values.ravel(), bins=256, range=(low, high))
    total = int(hist.sum())
    positions = np.arange(256, dtype=np.float64)
    total_sum = float((positions * hist).sum())
    weight, running, best, best_var = 0, 0.0, 0, -1.0
    for index, count in enumerate(hist):
        weight += int(count)
        if weight == 0 or weight == total:
            continue
        running += index * int(count)
        between = weight * (total - weight) * ((running / weight) - ((total_sum - running) / (total - weight))) ** 2
        if between > best_var:
            best_var, best = between, index
    return low + (high - low) * best / 255.0


def _threshold_dispatch(data, threshold, maxval, mode):
    graph = "threshold_3d" if data.ndim == 3 else "threshold_2d"
    scalars = {
        "h": data.shape[0],
        "w": data.shape[1],
        "threshold": float(threshold),
        "max_value": float(maxval),
        "mode": int(mode),
    }
    if data.ndim == 3:
        scalars["channels"] = data.shape[2]
    return _dispatch(
        "threshold",
        graph,
        inputs={"src": data},
        outputs={"dst": (data.shape, np.float32)},
        scalars=scalars,
    )


def threshold_aot(src, thresh=127.0, maxval=255.0, thresh_type="BINARY"):
    data = _as_f32(src)
    raw = str(thresh_type).upper() if isinstance(thresh_type, str) else int(thresh_type)
    otsu = isinstance(raw, str) and raw == "OTSU"
    if isinstance(raw, int):
        otsu = bool(raw & 8)
        raw &= 7
    if otsu:
        thresh = _otsu_threshold(data)
        raw = 0 if isinstance(raw, str) else raw
    mode = _THRESHOLD_MODES.get(raw, raw if isinstance(raw, int) else None)
    if mode not in range(5):
        raise ValueError("unsupported threshold type")
    if data.ndim not in (2, 3):
        raise ValueError("threshold input must be 2D or 3D")
    try:
        from taichi_vision.taichi_algorithm.aot_api import _run_blockwise
    except ImportError:  # pragma: no cover - only possible during import
        _run_blockwise = None
    result = None
    if _run_blockwise is not None:
        result = _run_blockwise(
            "threshold",
            (data,),
            data.shape,
            np.float32,
            lambda tile: _threshold_dispatch(tile, thresh, maxval, mode),
            params={
                "threshold": float(thresh),
                "max_value": float(maxval),
                "mode": int(mode),
                "otsu": bool(otsu),
            },
        )
    if result is None:
        result = _threshold_dispatch(data, thresh, maxval, mode)
    return float(thresh), result


def gaussian_window_aot(height, width, sigma=None):
    height, width = int(height), int(width)
    sigma = float(sigma if sigma is not None else max(height, width) / 6.0)
    if height <= 0 or width <= 0 or sigma <= 0:
        raise ValueError("window dimensions and sigma must be positive")
    return _dispatch("gaussian_window", "gaussian_window_2d", inputs={}, outputs={"window": ((height, width), np.float32)}, scalars={"h": height, "w": width, "sigma": sigma})


def joint_bilateral_guidance_aot(src, guide, preset="medium", radius=2):
    data = _as_f32(src)
    guide_data = _as_f32(guide)
    if guide_data.ndim != 2 or data.shape[:2] != guide_data.shape:
        raise ValueError("guide must be a grayscale image matching src height/width")
    if int(radius) not in (1, 2, 3):
        raise ValueError("radius must be 1, 2, or 3")
    presets = {"high": (0.8, 0.05), "medium": (1.5, 0.10), "low": (2.5, 0.20)}
    sigma_space, sigma_range = presets.get(str(preset).lower(), presets["medium"])
    inv_space = 1.0 / (2.0 * sigma_space * sigma_space)
    inv_range = 1.0 / (2.0 * sigma_range * sigma_range)

    def dispatch(src_tile, guide_tile):
        graph = "joint_bilateral_3d" if src_tile.ndim == 3 else "joint_bilateral_2d"
        scalars = {
            "h": src_tile.shape[0],
            "w": src_tile.shape[1],
            "radius": int(radius),
            "inv_space": inv_space,
            "inv_range": inv_range,
        }
        if src_tile.ndim == 3:
            scalars["channels"] = src_tile.shape[2]
        return _dispatch(
            "joint_bilateral_guidance",
            graph,
            inputs={"src": src_tile, "guide": guide_tile},
            outputs={"dst": (src_tile.shape, np.float32)},
            scalars=scalars,
        )

    try:
        from taichi_vision.taichi_algorithm.aot_api import _run_blockwise
    except ImportError:  # pragma: no cover - only possible during import
        _run_blockwise = None
    if _run_blockwise is not None:
        result = _run_blockwise(
            "joint_bilateral_guidance",
            (data, guide_data),
            data.shape,
            np.float32,
            dispatch,
            halo=int(radius),
            params={
                "preset": str(preset).lower(),
                "radius": int(radius),
                "inv_space": float(inv_space),
                "inv_range": float(inv_range),
            },
        )
        if result is not None:
            return result
    return dispatch(data, guide_data)


def enhance_image_aot(src, blur, lut, micro_contrast=2.93, clarity=0.0, noise_coring=0.0):
    data = _as_f32(src)
    blur_data = _as_f32(blur)
    lut_data = _as_f32(lut).reshape(-1)
    if data.ndim != 2 or blur_data.shape != data.shape or lut_data.size < 256:
        raise ValueError("enhance_image_aot expects 2D src/blur and a 256-entry LUT")
    def dispatch(src_tile, blur_tile):
        return _dispatch(
            "enhance_image",
            "enhance_grayscale_2d",
            inputs={"src": src_tile, "blur": blur_tile, "lut": lut_data[:256]},
            outputs={"dst": (src_tile.shape, np.float32)},
            scalars={
                "h": src_tile.shape[0],
                "w": src_tile.shape[1],
                "micro_contrast": float(micro_contrast),
                "clarity": float(clarity),
                "noise_coring": float(noise_coring),
            },
        )

    try:
        # ``extended_aot`` lives under ``image_processing`` while the shared
        # executor is owned by ``aot_api``.  Keep this lazy to avoid the
        # extended -> package -> extended import cycle.
        from taichi_vision.taichi_algorithm.aot_api import _run_blockwise
    except ImportError:  # pragma: no cover - only possible during import
        _run_blockwise = None
    if _run_blockwise is not None:
        result = _run_blockwise(
            "enhance_image",
            (data, blur_data),
            data.shape,
            np.float32,
            dispatch,
            params={
                "micro_contrast": float(micro_contrast),
                "clarity": float(clarity),
                "noise_coring": float(noise_coring),
                "lut": lut_data[:256].tobytes().hex(),
            },
        )
        if result is not None:
            return result
    return dispatch(data, blur_data)


__all__ = [
    "dilate_aot", "erode_aot", "histogram_aot", "ssim_aot", "warp_affine_aot", "filter2d_aot",
    "copy_make_border_aot", "normalize_aot", "threshold_aot", "gaussian_window_aot",
    "joint_bilateral_guidance_aot", "enhance_image_aot",
]

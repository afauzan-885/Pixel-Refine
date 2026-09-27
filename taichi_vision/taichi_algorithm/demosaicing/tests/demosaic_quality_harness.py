"""Shared quality harness for the Bayer demosaic families.

This module is deliberately free of Taichi, rawpy, *and* OpenCV: it owns scene
generation, sensor simulation, and the metric definitions so that a CLI runner,
a unit test, and a parameter search can all measure the *same* thing.  Every
metric declares whether lower or higher is better in ``METRIC_DIRECTIONS``,
because a search that optimises the wrong direction silently produces a
regression (``psnr_db`` in particular improves when it increases).

OpenCV was removed on purpose.  The installed OpenCV build intermittently aborts
with ``0x8007000e`` (out of memory) inside ``Sobel``/``GaussianBlur``, and
because those calls sat inside ``_edge_mask`` a flaky abort could fail a metric
assertion rather than reporting an honest number.  Everything below now uses
NumPy and ``scipy.ndimage``, which are stable here.

Two metric classes are provided:

Ground-truth metrics compare a reconstruction against the optical RGB image that
was mosaiced.  They require a synthetic scene.

Ground-truth-free metrics work on real sensor data.  ``sample_site_fidelity``
uses the fact that the measured CFA samples are exact truth,
``cfa_halo_overshoot`` derives a local same-colour range from those samples, and
``chroma_highpass_energy`` / ``cfa_checkerboard_chroma`` are *comparative*
artifact proxies.  These are the only metrics that can be applied to a real DNG.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
from scipy import ndimage


# 0 = R, 1 = G1, 2 = B, 3 = G2.  The two green codes are distinct because a
# sensor may carry different gains for the two green sites.
CFA_PATTERNS: Mapping[str, tuple[int, int, int, int]] = {
    "RGGB": (0, 1, 3, 2),
    "GRBG": (1, 0, 2, 3),
    "GBRG": (3, 2, 0, 1),
    "BGGR": (2, 3, 1, 0),
}

# Channel index in an RGB image for each CFA colour code.
_COLOUR_TO_CHANNEL = {0: 0, 1: 1, 2: 2, 3: 1}

# Metrics where a larger value is a better result.  Everything else is
# lower-is-better, which is the natural direction for an error measure.
METRIC_DIRECTIONS: Mapping[str, str] = {
    "psnr_db": "higher",
}

DEFAULT_BORDER = 8

# Gradient magnitude above which a pixel counts as an edge.  ``np.gradient``
# reports the true central-difference derivative, so a step of amplitude A shows
# roughly A/2 at the edge; 0.06 therefore selects contrasts above about 0.12.
_EDGE_THRESHOLD = 0.06


def direction_of(metric: str) -> str:
    """Return ``"higher"`` or ``"lower"`` for a metric name."""

    return METRIC_DIRECTIONS.get(metric, "lower")


def smoothstep(value):
    return value * value * (3.0 - 2.0 * value)


def _luma(rgb: np.ndarray) -> np.ndarray:
    return (
        rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    ).astype(np.float32)


def _gradients(field: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(gx, gy)`` central-difference derivatives of a 2-D field."""

    gy, gx = np.gradient(field.astype(np.float32))
    return gx, gy


def _shift(field: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """Shift a 2-D field by whole pixels.

    ``np.roll`` is used because every metric is evaluated on a border-cropped
    window, so wrap-around cannot reach the scored region.
    """

    return np.roll(np.roll(field, dy, axis=0), dx, axis=1)


def _edge_mask(reference: np.ndarray, threshold: float = _EDGE_THRESHOLD) -> np.ndarray:
    gx, gy = _gradients(_luma(reference))
    strong = np.hypot(gx, gy) > threshold
    return ndimage.binary_dilation(strong, structure=np.ones((3, 3), dtype=bool))


# ---------------------------------------------------------------------------
# Drawing primitives (NumPy only)
# ---------------------------------------------------------------------------
def _window(image: np.ndarray, x0, y0, x1, y1):
    """Clamped integer window plus local index grids for a bounded shape.

    Drawing through a local window matters: the foliage scene paints thousands
    of small shapes, and a full-canvas operation per shape makes generation
    quadratic in image size.
    """

    height, width = image.shape[:2]
    left = max(0, int(np.floor(x0)))
    top = max(0, int(np.floor(y0)))
    right = min(width, int(np.ceil(x1)) + 1)
    bottom = min(height, int(np.ceil(y1)) + 1)
    if right <= left or bottom <= top:
        return None
    ys, xs = np.mgrid[top:bottom, left:right]
    return (slice(top, bottom), slice(left, right)), ys.astype(np.float32), xs.astype(np.float32)


def _coverage(distance: np.ndarray, half_width: float) -> np.ndarray:
    """Anti-aliased coverage for a shape edge at ``distance`` from centre."""

    return np.clip(half_width + 0.5 - distance, 0.0, 1.0)


def _blend(image: np.ndarray, target, alpha: np.ndarray, colour) -> None:
    paint = np.asarray(colour, dtype=np.float32)
    image[target] = image[target] * (1.0 - alpha[..., None]) + paint * alpha[..., None]


def _paint_rect(image, x0, y0, x1, y1, colour) -> None:
    image[int(y0) : int(y1), int(x0) : int(x1)] = np.asarray(colour, dtype=np.float32)


def _paint_line(image, x0, y0, x1, y1, colour, thickness: float) -> None:
    pad = thickness * 0.5 + 1.0
    window = _window(
        image,
        min(x0, x1) - pad,
        min(y0, y1) - pad,
        max(x0, x1) + pad,
        max(y0, y1) + pad,
    )
    if window is None:
        return
    target, ys, xs = window
    dx, dy = float(x1 - x0), float(y1 - y0)
    length2 = dx * dx + dy * dy
    if length2 <= 0.0:
        t = np.zeros_like(xs)
    else:
        t = np.clip(((xs - x0) * dx + (ys - y0) * dy) / length2, 0.0, 1.0)
    distance = np.hypot(xs - (x0 + t * dx), ys - (y0 + t * dy))
    _blend(image, target, _coverage(distance, thickness * 0.5), colour)


def _paint_convex_polygon(image, points, colour) -> None:
    xs_points = [point[0] for point in points]
    ys_points = [point[1] for point in points]
    window = _window(
        image,
        min(xs_points) - 1,
        min(ys_points) - 1,
        max(xs_points) + 1,
        max(ys_points) + 1,
    )
    if window is None:
        return
    target, ys, xs = window
    count = len(points)
    # Orientation from the signed area keeps the inside test valid for either
    # winding order, which cv2.fillConvexPoly accepted and this must match.
    signed_area = 0.0
    for index in range(count):
        x0, y0 = points[index]
        x1, y1 = points[(index + 1) % count]
        signed_area += x0 * y1 - x1 * y0
    orientation = 1.0 if signed_area >= 0.0 else -1.0
    inside = np.ones(xs.shape, dtype=bool)
    for index in range(count):
        x0, y0 = points[index]
        x1, y1 = points[(index + 1) % count]
        cross = (x1 - x0) * (ys - y0) - (y1 - y0) * (xs - x0)
        inside &= orientation * cross >= -1e-6
    region = image[target]
    region[inside] = np.asarray(colour, dtype=np.float32)
    image[target] = region


def _paint_disk(image, cx, cy, radius, colour, anti_alias: bool = True) -> None:
    window = _window(image, cx - radius - 1, cy - radius - 1, cx + radius + 1, cy + radius + 1)
    if window is None:
        return
    target, ys, xs = window
    distance = np.hypot(xs - cx, ys - cy)
    if anti_alias:
        _blend(image, target, _coverage(distance, radius), colour)
    else:
        region = image[target]
        region[distance <= radius] = np.asarray(colour, dtype=np.float32)
        image[target] = region


def _paint_ellipse(image, cx, cy, semi_x, semi_y, angle_deg, colour) -> None:
    theta = np.deg2rad(angle_deg)
    cos_t, sin_t = float(np.cos(theta)), float(np.sin(theta))
    # Axis-aligned extent of a rotated ellipse.
    extent_x = np.hypot(semi_x * cos_t, semi_y * sin_t)
    extent_y = np.hypot(semi_x * sin_t, semi_y * cos_t)
    window = _window(
        image, cx - extent_x - 1, cy - extent_y - 1, cx + extent_x + 1, cy + extent_y + 1
    )
    if window is None:
        return
    target, ys, xs = window
    dx, dy = xs - cx, ys - cy
    u = dx * cos_t + dy * sin_t
    v = -dx * sin_t + dy * cos_t
    norm = np.sqrt((u / max(semi_x, 1e-3)) ** 2 + (v / max(semi_y, 1e-3)) ** 2)
    # Convert the normalised radius error into an approximate pixel distance so
    # the edge is anti-aliased at a consistent width.
    edge = np.abs(norm - 1.0) * min(semi_x, semi_y)
    alpha = np.where(norm <= 1.0, 1.0, np.clip(1.0 - edge, 0.0, 1.0))
    _blend(image, target, alpha, colour)


def _downsample(canvas: np.ndarray, size: int) -> np.ndarray:
    """Exact area average of an integer block factor (cv2 INTER_AREA equivalent)."""

    factor = canvas.shape[0] // size
    if factor <= 1:
        return canvas.astype(np.float32)
    trimmed = canvas[: size * factor, : size * factor]
    blocks = trimmed.reshape(size, factor, size, factor, canvas.shape[2])
    return blocks.mean(axis=(1, 3)).astype(np.float32)


# ---------------------------------------------------------------------------
# Scene generation
# ---------------------------------------------------------------------------
def make_contrast_edges(size: int = 256) -> np.ndarray:
    """High-contrast achromatic edges: the classic halo/zipper scene."""

    scale = 4
    n = size * scale
    image = np.full((n, n, 3), 0.025, dtype=np.float32)
    _paint_rect(image, n // 11, n // 10, n * 5 // 11, n * 9 // 10, (0.92, 0.92, 0.92))
    _paint_convex_polygon(
        image,
        [(n * 5 // 10, n // 12), (n * 19 // 20, n * 4 // 10), (n * 6 // 10, n * 19 // 20)],
        (0.04, 0.04, 0.04),
    )
    _paint_line(image, n // 20, n * 17 // 20, n * 19 // 20, n // 5, (0.98,) * 3, 3 * scale)
    _paint_line(image, n // 15, n // 3, n * 14 // 15, n // 3 + 9 * scale, (0.01,) * 3, scale)
    return np.clip(_downsample(image, size), 0.0, 1.0)


def make_color_edges(size: int = 256) -> np.ndarray:
    """Saturated coloured edges: the classic colour-fringing scene."""

    scale = 4
    n = size * scale
    image = np.full((n, n, 3), (0.015, 0.02, 0.025), dtype=np.float32)
    _paint_rect(image, n // 14, n // 12, n * 7 // 15, n * 11 // 13, (0.92, 0.025, 0.02))
    _paint_disk(image, n * 7 // 10, n * 3 // 10, n // 5, (0.025, 0.88, 0.035))
    _paint_convex_polygon(
        image,
        [(n * 11 // 20, n * 19 // 20), (n * 19 // 20, n * 9 // 20), (n * 19 // 20, n * 19 // 20)],
        (0.02, 0.035, 0.94),
    )
    _paint_line(image, n // 20, n * 18 // 20, n * 19 // 20, n // 15, (0.96, 0.96, 0.05), 2 * scale)
    return np.clip(_downsample(image, size), 0.0, 1.0)


def make_repeating_detail(size: int = 256) -> np.ndarray:
    """Near-Nyquist repetition: the classic zipper/moire scene."""

    y, x = np.indices((size, size), dtype=np.float32)
    sweep = 0.5 + 0.46 * np.sin(2.0 * np.pi * (0.035 * x + 0.00072 * x * x))
    diagonal = 0.5 + 0.46 * np.sign(np.sin(2.0 * np.pi * (x + 1.71 * y) / 5.5))
    checker = (((x.astype(np.int32) // 2) + (y.astype(np.int32) // 2)) & 1).astype(np.float32)
    mono = np.where(y < size / 3, sweep, np.where(y < 2 * size / 3, diagonal, 0.04 + 0.92 * checker))
    return np.repeat(mono[:, :, None], 3, axis=2).astype(np.float32)


def make_micro_foliage(size: int = 256, seed: int = 885) -> np.ndarray:
    """Dense random microstructure: worst-case tail error for a demosaic."""

    scale = 4
    n = size * scale
    rng = np.random.default_rng(seed)
    image = np.empty((n, n, 3), dtype=np.float32)
    image[:] = (0.32, 0.48, 0.68)
    for _ in range(135):
        x0 = int(rng.integers(0, n))
        y0 = int(rng.integers(n // 7, n))
        length = int(rng.integers(20, 150))
        angle = float(rng.uniform(-1.45, 1.45))
        x1 = int(x0 + np.cos(angle) * length)
        y1 = int(y0 - abs(np.sin(angle)) * length)
        shade = float(rng.uniform(0.015, 0.12))
        _paint_line(
            image,
            x0,
            y0,
            x1,
            y1,
            (shade * 0.8, shade * 0.65, shade * 0.35),
            float(rng.integers(1, 4)),
        )
    for _ in range(1850):
        centre = (int(rng.integers(0, n)), int(rng.integers(n // 9, n)))
        semi_x = int(rng.integers(2, 11))
        semi_y = int(rng.integers(1, 6))
        angle = float(rng.uniform(0.0, 180.0))
        level = float(rng.uniform(0.08, 0.62))
        colour = (level * rng.uniform(0.18, 0.48), level, level * rng.uniform(0.12, 0.36))
        _paint_ellipse(image, centre[0], centre[1], semi_x, semi_y, angle, colour)
    return np.clip(_downsample(image, size), 0.0, 1.0)


def make_neutral_chart(size: int = 256) -> np.ndarray:
    """Achromatic step chart with slanted edges.

    Every region is neutral, so any chroma in the reconstruction is false
    colour.  This is the scene that isolates colour fringing from genuine
    scene colour.
    """

    scale = 4
    n = size * scale
    steps = 8
    image = np.zeros((n, n, 3), dtype=np.float32)
    band = n // steps
    for index in range(steps):
        level = 0.04 + 0.92 * index / (steps - 1)
        _paint_rect(image, 0, index * band, n, (index + 1) * band, (level,) * 3)
    _paint_convex_polygon(
        image,
        [(n * 3 // 10, 0), (n * 4 // 10, n), (n * 5 // 10, n), (n * 4 // 10, 0)],
        (0.5, 0.5, 0.5),
    )
    return np.clip(_downsample(image, size), 0.0, 1.0)


def make_star_chart(size: int = 256, spokes: int = 48) -> np.ndarray:
    """Achromatic Siemens star; ``spokes`` is a held-out variation knob."""

    y, x = np.ogrid[:size, :size]
    centre = size / 2.0
    angle = np.arctan2(y - centre, x - centre)
    radius = np.hypot(y - centre, x - centre)
    pattern = 0.5 + 0.47 * np.cos(spokes * angle)
    pattern = np.where(radius < 4.0, 0.5, pattern)
    return np.repeat(pattern.astype(np.float32)[:, :, None], 3, axis=2)


SCENE_LIBRARY: Mapping[str, object] = {
    "contrast_edges": make_contrast_edges,
    "color_edges": make_color_edges,
    "repeating_detail": make_repeating_detail,
    "micro_foliage": make_micro_foliage,
    "neutral_chart": make_neutral_chart,
}

# Scenes whose reference is achromatic, so false-chroma metrics are meaningful.
ACHROMATIC_SCENES = frozenset(
    {"contrast_edges", "repeating_detail", "neutral_chart", "star_chart"}
)

# Held-out variations for the parameter search.  These are deliberately not
# part of the default tuning set so a tuned constant must generalise.
HELD_OUT_SCENES: Mapping[str, object] = {
    "star_chart": make_star_chart,
    "micro_foliage_alt": lambda size=256: make_micro_foliage(size, seed=4242),
}


# ---------------------------------------------------------------------------
# Sensor simulation
# ---------------------------------------------------------------------------
def apply_lens_psf(rgb: np.ndarray, sigma: float) -> np.ndarray:
    """Blur with the lens point-spread function before sampling."""

    rgb = rgb.astype(np.float32)
    if sigma <= 0.0:
        return rgb
    return np.dstack(
        [ndimage.gaussian_filter(rgb[..., index], sigma=sigma, mode="nearest") for index in range(3)]
    ).astype(np.float32)


def apply_lateral_ca(rgb: np.ndarray, strength: float) -> np.ndarray:
    """Simulate lateral chromatic aberration.

    Real fringing is produced by the lens, not by the demosaic, so the harness
    must inject it before mosaicing.  Red and blue are scaled radially by
    opposite amounts around the image centre, exactly as ``cv2.remap`` did.
    """

    rgb = rgb.astype(np.float32)
    if strength <= 0.0:
        return rgb
    height, width = rgb.shape[:2]
    cy, cx = height / 2.0, width / 2.0
    y, x = np.indices((height, width), dtype=np.float32)
    output = np.empty_like(rgb)
    for channel, direction in enumerate((1.0 + strength, 0.0, 1.0 - strength)):
        if direction == 0.0:
            output[..., channel] = rgb[..., channel]
            continue
        map_y = cy + (y - cy) / direction
        map_x = cx + (x - cx) / direction
        output[..., channel] = ndimage.map_coordinates(
            rgb[..., channel], [map_y, map_x], order=1, mode="mirror"
        )
    return output


def rgb_to_cfa(rgb: np.ndarray, cfa: Sequence[int]) -> np.ndarray:
    """Mosaic an RGB image with an arbitrary 2x2 CFA layout."""

    c00, c01, c10, c11 = (int(value) for value in cfa)
    bayer = np.empty(rgb.shape[:2], dtype=np.float32)
    block = ((c00, c01), (c10, c11))
    for row in range(2):
        for col in range(2):
            code = block[row][col]
            bayer[row::2, col::2] = rgb[row::2, col::2, _COLOUR_TO_CHANNEL[code]]
    return bayer


def add_sensor_noise(
    bayer: np.ndarray,
    *,
    full_well: float = 12000.0,
    read_noise_e: float = 2.4,
    seed: int = 7,
) -> np.ndarray:
    """Apply photon shot noise and read noise in the sensor's own domain."""

    rng = np.random.default_rng(seed)
    electrons = np.clip(bayer, 0.0, 1.0).astype(np.float64) * full_well
    shot = rng.poisson(electrons).astype(np.float64)
    read = rng.normal(0.0, read_noise_e, size=electrons.shape)
    return np.clip((shot + read) / full_well, 0.0, 1.0).astype(np.float32)


@dataclass(frozen=True)
class SensorModel:
    """Optical and electronic parameters used to render a synthetic frame."""

    psf_sigma: float = 0.6
    ca_strength: float = 0.0015
    full_well: float = 12000.0
    read_noise_e: float = 2.4
    noise_seed: int = 7
    cfa: str = "RGGB"


@dataclass(frozen=True)
class RenderedFrame:
    """A simulated capture and the image an ideal demosaic should reproduce."""

    bayer: np.ndarray
    optical: np.ndarray


def render_frame(scene: np.ndarray, model: SensorModel) -> RenderedFrame:
    """Simulate a capture and return both the mosaic and the scoring reference.

    The reference for any quality metric is the **optical** image, after the
    lens point-spread function and chromatic aberration but before mosaicing --
    not the sharp scene.  Scoring against the sharp scene would penalise every
    algorithm for the lens blur and, worse, would reward ringing and unsharp
    masking during a parameter search, which is exactly the artifact this
    harness exists to suppress.
    """

    optical = apply_lens_psf(scene, model.psf_sigma)
    optical = apply_lateral_ca(optical, model.ca_strength)
    bayer = rgb_to_cfa(optical, CFA_PATTERNS[model.cfa])
    if model.full_well > 0.0 and model.read_noise_e >= 0.0:
        bayer = add_sensor_noise(
            bayer,
            full_well=model.full_well,
            read_noise_e=model.read_noise_e,
            seed=model.noise_seed,
        )
    return RenderedFrame(bayer=bayer, optical=optical.astype(np.float32))


def simulate_sensor(scene: np.ndarray, model: SensorModel) -> np.ndarray:
    """Render a scene through lens, chromatic aberration, and sensor noise.

    Only the Bayer frame is returned.  Prefer :func:`render_frame` when the
    result will be scored, because that also returns the optical image that the
    metrics must actually compare against.
    """

    return render_frame(scene, model).bayer


def gain_vector(cfa: Sequence[int], gains: Sequence[float]) -> np.ndarray:
    """Return the per-colour-code gain table indexed by CFA colour code."""

    table = np.ones(4, dtype=np.float32)
    for index in range(4):
        table[index] = gains[index]
    return table


# ---------------------------------------------------------------------------
# Transfer domain
# ---------------------------------------------------------------------------
def output_transfer(rgb: np.ndarray, method: str = "hamilton") -> np.ndarray:
    """Mirror the public graph's highlight recovery and dynamic range compression."""

    rgb = np.asarray(rgb, dtype=np.float32)
    maximum = np.max(rgb, axis=2)
    minimum = np.min(rgb, axis=2)
    if method == "arm":
        factor = np.clip((maximum - 0.45) / 0.35, 0.0, 1.0)
        ratio = minimum / np.maximum(maximum, 1e-5)
        neutrality = np.clip((0.82 - ratio) / 0.52, 0.0, 1.0)
    else:
        factor = np.clip((maximum - 0.55) / 0.43, 0.0, 1.0)
        ratio = minimum / np.maximum(maximum, 1e-5)
        neutrality = np.clip((ratio - 0.40) / 0.45, 0.0, 1.0)
    blend = (smoothstep(factor) * smoothstep(neutrality))[:, :, None]
    peak = maximum[:, :, None]
    recovered = rgb * (1.0 - blend) + peak * blend
    return (recovered / np.sqrt(1.0 + recovered * recovered)).astype(np.float32)


def invert_output_transfer(value: np.ndarray) -> np.ndarray:
    """Invert ``x / sqrt(1 + x*x)``.

    Highlight recovery also desaturates near-clipping pixels, which this inverse
    cannot undo, so fidelity metrics must exclude sites close to clipping.
    """

    value = np.clip(np.asarray(value, dtype=np.float32), 0.0, 0.999999)
    return (value / np.sqrt(1.0 - value * value)).astype(np.float32)


# ---------------------------------------------------------------------------
# Ground-truth metrics
# ---------------------------------------------------------------------------
def halo_overshoot(
    reference: np.ndarray, candidate: np.ndarray, *, radius: int = 1, margin: float = 0.01
) -> dict:
    """Measure overshoot/undershoot beyond the local reference range.

    A ring-inducing demosaic pushes reconstructed values past the range that the
    reference itself occupies in a small neighbourhood.  This detector is blind
    to blur (which stays inside the range) and blind to bias (which the local
    range follows), so it isolates ringing.
    """

    size = 2 * radius + 1
    local_min = ndimage.minimum_filter(reference, size=(size, size, 1), mode="nearest")
    local_max = ndimage.maximum_filter(reference, size=(size, size, 1), mode="nearest")
    over = np.maximum(candidate - local_max - margin, 0.0)
    under = np.maximum(local_min - candidate - margin, 0.0)
    excess = over + under
    return {
        "halo_energy": float(np.mean(excess)),
        "halo_p99": float(np.quantile(excess, 0.99)),
        "halo_rate": float(np.mean(np.max(excess, axis=2) > 0.0)),
    }


def zipper_score(
    reference: np.ndarray, candidate: np.ndarray, *, edge_threshold: float = _EDGE_THRESHOLD
) -> dict:
    """Measure the alternating residual that defines a zipper artifact.

    Zipper appears as a residual that flips sign every other pixel along an
    edge.  The second difference of the residual along the dominant edge axis is
    therefore large exactly where the artifact is, and small for a smooth but
    biased reconstruction.
    """

    mask = _edge_mask(reference, edge_threshold)
    if not np.any(mask):
        return {"zipper_score": 0.0, "zipper_p99": 0.0}

    residual = _luma(candidate) - _luma(reference)
    gx, gy = _gradients(_luma(reference))

    second_x = np.abs(2.0 * residual - _shift(residual, 0, 1) - _shift(residual, 0, -1))
    second_y = np.abs(2.0 * residual - _shift(residual, 1, 0) - _shift(residual, -1, 0))
    second = np.where(np.abs(gx) >= np.abs(gy), second_x, second_y)

    values = second[mask]
    return {
        "zipper_score": float(np.mean(values)),
        "zipper_p99": float(np.quantile(values, 0.99)),
    }


def fringing_score(
    reference: np.ndarray, candidate: np.ndarray, *, edge_threshold: float = _EDGE_THRESHOLD
) -> dict:
    """Measure chroma that varies across an edge faster than luminance does.

    Colour fringing is chroma change along the edge direction and across it at a
    scale the scene does not contain; measuring the chroma step between opposite
    neighbours (a high-pass along the dominant axis) isolates it from legitimate
    scene colour.
    """

    mask = _edge_mask(reference, edge_threshold)
    if not np.any(mask):
        return {"fringing_score": 0.0, "fringing_p99": 0.0}

    chroma = np.max(candidate, axis=2) - np.min(candidate, axis=2)
    gx, gy = _gradients(_luma(reference))

    high_x = np.abs(_shift(chroma, 0, 1) - _shift(chroma, 0, -1)) * 0.5
    high_y = np.abs(_shift(chroma, 1, 0) - _shift(chroma, -1, 0)) * 0.5
    response = np.where(np.abs(gx) >= np.abs(gy), high_x, high_y)

    values = response[mask]
    return {
        "fringing_score": float(np.mean(values)),
        "fringing_p99": float(np.quantile(values, 0.99)),
    }


def metric_bundle(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    achromatic: bool,
    border: int = DEFAULT_BORDER,
) -> dict:
    """Compute every ground-truth metric on a border-cropped window."""

    reference = np.asarray(reference, dtype=np.float32)
    candidate = np.asarray(candidate, dtype=np.float32)
    if candidate.shape != reference.shape:
        raise ValueError(
            f"shape mismatch: candidate={candidate.shape} reference={reference.shape}"
        )
    if border:
        reference = reference[border:-border, border:-border]
        candidate = candidate[border:-border, border:-border]

    error = np.abs(candidate - reference)
    mse = float(np.mean((candidate - reference) ** 2))
    mask = _edge_mask(reference)

    result = {
        "mae": float(np.mean(error)),
        "psnr_db": float(10.0 * np.log10(1.0 / max(mse, 1e-12))),
        "p99_abs": float(np.quantile(error, 0.99)),
        "false_pixel_rate": float(np.mean(np.max(error, axis=2) > 0.08)),
        "edge_mae": float(np.mean(error[mask])) if np.any(mask) else 0.0,
    }
    result.update(halo_overshoot(reference, candidate))
    result.update(zipper_score(reference, candidate))
    result.update(fringing_score(reference, candidate))

    # Chroma *error* is valid on every scene: it compares the candidate's chroma
    # with the reference's chroma.  The "false chroma" family is only meaningful
    # where the reference has no chroma at all, so it is reported for achromatic
    # scenes only -- reporting it elsewhere would measure the scene's own colour.
    chroma_candidate = np.max(candidate, axis=2) - np.min(candidate, axis=2)
    chroma_reference = np.max(reference, axis=2) - np.min(reference, axis=2)
    chroma_error = np.abs(chroma_candidate - chroma_reference)
    result["chroma_error_mean"] = float(np.mean(chroma_error))
    result["chroma_error_p99"] = float(np.quantile(chroma_error, 0.99))
    result["edge_chroma_error"] = (
        float(np.mean(chroma_error[mask])) if np.any(mask) else 0.0
    )

    if achromatic:
        result["false_chroma_mean"] = float(np.mean(chroma_candidate))
        result["false_chroma_p99"] = float(np.quantile(chroma_candidate, 0.99))
        result["edge_false_chroma"] = (
            float(np.mean(chroma_candidate[mask])) if np.any(mask) else 0.0
        )
        result["reference_chroma_mean"] = float(np.mean(chroma_reference))
    return result


# ---------------------------------------------------------------------------
# Ground-truth-free metrics (valid on real sensor data)
# ---------------------------------------------------------------------------
def _cfa_lattice_maps(
    bayer: np.ndarray,
    cfa: Sequence[int],
    *,
    black_level: float = 0.0,
    white_level: float = 1.0,
) -> list[tuple[int, int, int, np.ndarray]]:
    """Split a Bayer frame into its four same-colour lattices.

    Returns ``(row_offset, col_offset, colour, measured)`` entries where
    ``measured`` is the black-subtracted, range-normalised sample **before**
    white balance.  Callers multiply by the gain themselves because the
    highlight-recovery knee is defined in this pre-gain domain, so the
    usability gate and the value comparison live in different domains.
    """

    inv_range = 1.0 / max(1e-6, float(white_level) - float(black_level))
    block = ((int(cfa[0]), int(cfa[1])), (int(cfa[2]), int(cfa[3])))
    lattices = []
    for row in range(2):
        for col in range(2):
            colour = block[row][col]
            measured = np.clip(
                (bayer[row::2, col::2] - black_level) * inv_range, 0.0, 1.0
            ).astype(np.float32)
            lattices.append((row, col, colour, measured))
    return lattices


def sample_site_fidelity(
    bayer: np.ndarray,
    candidate: np.ndarray,
    cfa: Sequence[int],
    gains: Sequence[float],
    *,
    black_level: float = 0.0,
    white_level: float = 1.0,
    soft_ceiling: float = 0.5,
) -> dict:
    """Compare the reconstruction against the exact measured samples.

    The measured CFA sample is ground truth that needs no synthetic scene: the
    demosaic is free to interpolate between samples, but at a measured site the
    corresponding channel must reproduce what the sensor saw.

    ``soft_ceiling`` is applied to the **pre-gain** sample, which is the domain
    where the graph's highlight recovery acts.  Gating on the post-gain value
    would mis-classify highlights whenever the white-balance gains exceed one,
    and would then report a large phantom fidelity error on real captures.
    """

    linear = invert_output_transfer(candidate)
    table = gain_vector(cfa, gains)
    deviations = []
    per_colour: dict[int, list[float]] = {}

    for row, col, colour, measured in _cfa_lattice_maps(
        bayer, cfa, black_level=black_level, white_level=white_level
    ):
        expected = (measured * table[colour]).astype(np.float32)
        channel = _COLOUR_TO_CHANNEL[colour]
        actual = linear[row::2, col::2, channel]
        usable = measured < soft_ceiling
        if not np.any(usable):
            continue
        deviation = np.abs(actual[usable] - expected[usable])
        deviations.append(deviation)
        per_colour.setdefault(colour, []).append(float(np.mean(deviation)))

    if not deviations:
        return {
            "sample_site_fidelity_mean": float("nan"),
            "sample_site_fidelity_max": float("nan"),
        }

    stacked = np.concatenate(deviations)
    result = {
        "sample_site_fidelity_mean": float(np.mean(stacked)),
        "sample_site_fidelity_max": float(np.max(stacked)),
        "sample_site_fidelity_p99": float(np.quantile(stacked, 0.99)),
    }
    for colour, means in per_colour.items():
        result[f"sample_site_fidelity_colour{colour}"] = float(np.mean(means))
    return result


def cfa_halo_overshoot(
    bayer: np.ndarray,
    candidate: np.ndarray,
    cfa: Sequence[int],
    gains: Sequence[float],
    *,
    black_level: float = 0.0,
    white_level: float = 1.0,
    radius: int = 2,
    margin: float = 0.01,
    soft_ceiling: float = 0.5,
) -> dict:
    """Detect ringing using the measured samples as a local reference.

    Overshoot is measured against the range of *same-colour* measured samples in
    a neighbourhood, which is available on real data.  Blur alone cannot trip
    this detector because blur does not leave the sampled range.

    The value range is compared in the post-gain domain, matching the graph
    output, while the usability gate uses the pre-gain sample because that is
    where highlight recovery acts.
    """

    size = 2 * radius + 1
    linear = invert_output_transfer(candidate)
    table = gain_vector(cfa, gains)
    energies = []
    positives = 0
    total = 0

    for row, col, colour, measured in _cfa_lattice_maps(
        bayer, cfa, black_level=black_level, white_level=white_level
    ):
        values = (measured * table[colour]).astype(np.float32)
        local_min = ndimage.minimum_filter(values, size=size, mode="nearest")
        local_max = ndimage.maximum_filter(values, size=size, mode="nearest")
        pre_max = ndimage.maximum_filter(measured, size=size, mode="nearest")
        channel = _COLOUR_TO_CHANNEL[colour]
        actual = linear[row::2, col::2, channel]

        over = np.maximum(actual - local_max - margin, 0.0)
        under = np.maximum(local_min - actual - margin, 0.0)
        excess = over + under
        usable = pre_max < soft_ceiling
        if not np.any(usable):
            continue
        energies.append(excess[usable])
        positives += int(np.count_nonzero(excess[usable]))
        total += int(np.count_nonzero(usable))

    if not energies:
        return {"cfa_halo_energy": float("nan"), "cfa_halo_rate": float("nan")}

    stacked = np.concatenate(energies)
    return {
        "cfa_halo_energy": float(np.mean(stacked)),
        "cfa_halo_p99": float(np.quantile(stacked, 0.99)),
        "cfa_halo_rate": float(positives / max(1, total)),
    }


def chroma_highpass_energy(
    candidate: np.ndarray, *, border: int = DEFAULT_BORDER
) -> dict:
    """High-frequency chroma energy, a comparative false-colour proxy.

    Real photographs have legitimate chroma detail, so this cannot be scored
    against an absolute threshold.  Comparing two reconstructions of the *same*
    frame is meaningful: demosaic artifacts add chroma energy at frequencies the
    scene does not contain, so a lower value is a cleaner reconstruction.
    """

    chroma = (np.max(candidate, axis=2) - np.min(candidate, axis=2)).astype(np.float32)
    highpass = chroma - ndimage.uniform_filter(chroma, size=3, mode="nearest")
    if border:
        highpass = highpass[border:-border, border:-border]
    return {
        "chroma_hp_energy": float(np.mean(highpass * highpass)),
        "chroma_hp_p99": float(np.quantile(np.abs(highpass), 0.99)),
    }


def cfa_checkerboard_chroma(
    candidate: np.ndarray, *, border: int = DEFAULT_BORDER
) -> dict:
    """Chroma energy locked to the 2x2 CFA checkerboard frequency.

    False colour and zipper artifacts alternate with the CFA phase, so
    correlating chroma with the checkerboard kernel isolates them from scene
    colour.  Like :func:`chroma_highpass_energy` this is a comparative metric.
    """

    chroma = (np.max(candidate, axis=2) - np.min(candidate, axis=2)).astype(np.float32)
    board = (
        chroma[0::2, 0::2] - chroma[0::2, 1::2] - chroma[1::2, 0::2] + chroma[1::2, 1::2]
    ) * 0.25
    if border:
        cut = border // 2
        if cut:
            board = board[cut:-cut, cut:-cut]
    return {
        "cfa_checkerboard_chroma": float(np.mean(np.abs(board))),
        "cfa_checkerboard_chroma_p99": float(np.quantile(np.abs(board), 0.99)),
    }


def ground_truth_free_bundle(
    bayer: np.ndarray,
    candidate: np.ndarray,
    cfa: Sequence[int],
    gains: Sequence[float],
    *,
    black_level: float = 0.0,
    white_level: float = 1.0,
) -> dict:
    """Every metric that can be evaluated on a real capture."""

    report = {}
    report.update(
        sample_site_fidelity(
            bayer,
            candidate,
            cfa,
            gains,
            black_level=black_level,
            white_level=white_level,
        )
    )
    report.update(
        cfa_halo_overshoot(
            bayer,
            candidate,
            cfa,
            gains,
            black_level=black_level,
            white_level=white_level,
        )
    )
    report.update(chroma_highpass_energy(candidate))
    report.update(cfa_checkerboard_chroma(candidate))
    return report


# ---------------------------------------------------------------------------
# Execution and timing
# ---------------------------------------------------------------------------
def run_full_frame(
    api,
    method: str,
    bayer: np.ndarray,
    scalars: Sequence[float],
    *,
    runs: int = 3,
    resident: bool = True,
) -> tuple[np.ndarray, dict]:
    """Invoke a demosaic graph full-frame and report dispatch/end-to-end timings.

    ``api`` is the ``taichi_aot`` facade, injected rather than imported so this
    module stays backend free (and therefore testable without a device).
    Full-frame is used deliberately: it is the correctness oracle, while the
    block path is covered by its own parity probe.
    """

    function = getattr(api, method)
    input_bayer = api.upload(bayer) if resident else bayer
    dispatch_ms: list[float] = []
    end_to_end_ms: list[float] = []
    output = None
    try:
        warm = function(input_bayer, *scalars, return_gpu=True)
        if hasattr(warm, "release"):
            warm.release()
        for _ in range(max(1, runs)):
            started = time.perf_counter()
            candidate = function(input_bayer, *scalars, return_gpu=True)
            dispatched = time.perf_counter()
            output = (
                candidate.to_numpy()
                if hasattr(candidate, "to_numpy")
                else np.asarray(candidate)
            )
            finished = time.perf_counter()
            dispatch_ms.append((dispatched - started) * 1000.0)
            end_to_end_ms.append((finished - started) * 1000.0)
            if hasattr(candidate, "release"):
                candidate.release()
    finally:
        if resident and hasattr(input_bayer, "release"):
            input_bayer.release()
    return np.asarray(output, dtype=np.float32), {
        "dispatch_median_ms": float(np.median(dispatch_ms)),
        "end_to_end_median_ms": float(np.median(end_to_end_ms)),
        "dispatch_runs_ms": dispatch_ms,
        "end_to_end_runs_ms": end_to_end_ms,
        "runs": max(1, runs),
        "input_mode": "resident" if resident else "host",
    }


# ---------------------------------------------------------------------------
# Gate comparison
# ---------------------------------------------------------------------------
REGRESSION_TOLERANCE = 1e-6


def compare_scene_metrics(
    baseline: Mapping[str, float],
    candidate: Mapping[str, float],
    *,
    tolerance: float = REGRESSION_TOLERANCE,
) -> list[dict]:
    """Return every metric that regressed between two measurements."""

    regressions = []
    for metric, base_value in baseline.items():
        if metric not in candidate:
            continue
        if not np.isfinite(base_value) or not np.isfinite(candidate[metric]):
            continue
        direction = direction_of(metric)
        delta = candidate[metric] - base_value
        worse = delta > tolerance if direction == "lower" else delta < -tolerance
        if worse:
            regressions.append(
                {
                    "metric": metric,
                    "baseline": float(base_value),
                    "candidate": float(candidate[metric]),
                    "direction": direction,
                }
            )
    return regressions

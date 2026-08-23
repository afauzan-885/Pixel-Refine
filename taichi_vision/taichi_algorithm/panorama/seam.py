"""Deterministic panorama seam primitives.

``dynamic_programming_seam`` computes a minimum-cost monotone seam through an
overlap.  ``graph_cut_surrogate`` remains a bounded local-label refinement for
backward compatibility.  ``graph_cut_maxflow`` is the exact binary s/t
min-cut solver for the documented finite grid energy; its residual push-relabel
solver is deliberately kept on the host because a dynamic graph cannot be
represented by the currently qualified AOT graphs.  ``backend="taichi"``
accelerates the unary-map construction on a CPU JIT kernel and then invokes the
same deterministic host solver.  ``backend="aot"`` uses a target-qualified
static unary-map leaf followed by that same host solver; it fails closed when
the target artifact is unavailable.
"""

from collections import deque
import importlib
from typing import Any

import numpy as np

from ..pipeline_common import as_float32_image


MAX_SEAM_PIXELS = 55_000_000
DEFAULT_MAX_WORKING_BYTES = 1_500_000_000
# A residual graph has substantially higher fan-out and storage than the
# pixelwise seam-energy path.  The byte budget below remains the authoritative
# guard; this cap prevents accidental construction of an enormous Python graph
# when a caller leaves the generic seam limit unchanged.
MAX_GRAPH_CUT_PIXELS = 4_000_000
_GRAPH_EPS = 1.0e-12

try:
    _ti = importlib.import_module("taichi")
except ImportError:  # pragma: no cover - minimal installations
    _ti = None


def _ensure_taichi_cpu() -> Any:
    if _ti is None:
        raise ImportError("backend='taichi' requires the taichi package")
    from taichi.lang import impl

    runtime = impl.get_runtime()
    if getattr(runtime, "prog", None) is None:
        _ti.init(arch=_ti.cpu, offline_cache=False)
    else:
        current_arch = getattr(getattr(_ti, "cfg", None), "arch", None)
        if current_arch != _ti.cpu:
            raise RuntimeError(
                f"backend='taichi' requires a CPU JIT runtime; current arch is {current_arch}"
            )
    return _ti


if _ti is not None:

    @_ti.kernel
    def _seam_energy_gray_kernel(
        left: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        right: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        overlap: _ti.types.ndarray(dtype=_ti.i32, ndim=2),
        energy: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        color_weight: _ti.f32,
        gradient_weight: _ti.f32,
    ):
        for y, x in _ti.ndrange(left.shape[0], left.shape[1]):
            gx_left = 0.0 if x == 0 else left[y, x] - left[y, x - 1]
            gx_right = 0.0 if x == 0 else right[y, x] - right[y, x - 1]
            gy_left = 0.0 if y == 0 else left[y, x] - left[y - 1, x]
            gy_right = 0.0 if y == 0 else right[y, x] - right[y - 1, x]
            value = color_weight * _ti.abs(left[y, x] - right[y, x])
            value += gradient_weight * (_ti.abs(gx_left - gx_right) + _ti.abs(gy_left - gy_right))
            energy[y, x] = value if overlap[y, x] != 0 else 1.0e6

    @_ti.kernel
    def _seam_energy_color_kernel(
        left: _ti.types.ndarray(dtype=_ti.f32, ndim=3),
        right: _ti.types.ndarray(dtype=_ti.f32, ndim=3),
        overlap: _ti.types.ndarray(dtype=_ti.i32, ndim=2),
        energy: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        color_weight: _ti.f32,
        gradient_weight: _ti.f32,
    ):
        for y, x in _ti.ndrange(left.shape[0], left.shape[1]):
            color = 0.0
            for channel in range(left.shape[2]):
                color += _ti.abs(left[y, x, channel] - right[y, x, channel])
            color /= float(left.shape[2])
            left_luma = 0.299 * left[y, x, 0] + 0.587 * left[y, x, 1] + 0.114 * left[y, x, 2]
            right_luma = 0.299 * right[y, x, 0] + 0.587 * right[y, x, 1] + 0.114 * right[y, x, 2]
            gx_left = 0.0
            gx_right = 0.0
            gy_left = 0.0
            gy_right = 0.0
            if x == 0:
                gx_left = 0.0
                gx_right = 0.0
            else:
                gx_left = left_luma - (0.299 * left[y, x - 1, 0] + 0.587 * left[y, x - 1, 1] + 0.114 * left[y, x - 1, 2])
                gx_right = right_luma - (0.299 * right[y, x - 1, 0] + 0.587 * right[y, x - 1, 1] + 0.114 * right[y, x - 1, 2])
            if y == 0:
                gy_left = 0.0
                gy_right = 0.0
            else:
                gy_left = left_luma - (0.299 * left[y - 1, x, 0] + 0.587 * left[y - 1, x, 1] + 0.114 * left[y - 1, x, 2])
                gy_right = right_luma - (0.299 * right[y - 1, x, 0] + 0.587 * right[y - 1, x, 1] + 0.114 * right[y - 1, x, 2])
            value = color_weight * color + gradient_weight * (_ti.abs(gx_left - gx_right) + _ti.abs(gy_left - gy_right))
            energy[y, x] = value if overlap[y, x] != 0 else 1.0e6

    @_ti.kernel
    def _graph_cut_unary_kernel(
        left_gray: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        right_gray: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        unary_left: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        unary_right: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        color_difference: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        gradient_weight: _ti.f32,
        color_weight: _ti.f32,
    ):
        """Build the finite unary/cross-image maps used by max-flow.

        The graph solver itself is intentionally host-side.  Keeping this
        map construction in a separate kernel makes ``backend="taichi"`` an
        honest CPU-JIT path without pretending that a dynamic residual graph
        is an AOT image kernel.
        """
        for y, x in _ti.ndrange(left_gray.shape[0], left_gray.shape[1]):
            gx_l = 0.0 if x == 0 else left_gray[y, x] - left_gray[y, x - 1]
            gx_r = 0.0 if x == 0 else right_gray[y, x] - right_gray[y, x - 1]
            gy_l = 0.0 if y == 0 else left_gray[y, x] - left_gray[y - 1, x]
            gy_r = 0.0 if y == 0 else right_gray[y, x] - right_gray[y - 1, x]
            unary_left[y, x] = gradient_weight * (_ti.abs(gx_l) + _ti.abs(gy_l))
            unary_right[y, x] = gradient_weight * (_ti.abs(gx_r) + _ti.abs(gy_r))
            color_difference[y, x] = color_weight * _ti.abs(left_gray[y, x] - right_gray[y, x])


def _backend_name(backend: str, *, allow_aot: bool = False) -> str:
    value = str(backend).lower()
    if value == "aot" and not allow_aot:
        raise NotImplementedError(
            "panorama seams have no qualified AOT graph; use backend='numpy' or 'taichi' explicitly"
        )
    allowed = {"numpy", "taichi"}
    if allow_aot:
        allowed.add("aot")
    if value not in allowed:
        suffix = ", or 'aot'" if allow_aot else ""
        raise ValueError(f"backend must be 'numpy', 'taichi'{suffix}")
    return value


def _seam_energy_taichi(
    lhs: np.ndarray,
    rhs: np.ndarray,
    overlap: np.ndarray,
    color_weight: float,
    gradient_weight: float,
) -> np.ndarray:
    taichi = _ensure_taichi_cpu()
    overlap_i32 = np.ascontiguousarray(overlap, dtype=np.int32)
    energy = np.empty(lhs.shape[:2], dtype=np.float32)
    if lhs.ndim == 2:
        _seam_energy_gray_kernel(lhs, rhs, overlap_i32, energy, color_weight, gradient_weight)
    else:
        _seam_energy_color_kernel(lhs, rhs, overlap_i32, energy, color_weight, gradient_weight)
    taichi.sync()
    return np.ascontiguousarray(energy, dtype=np.float32)


def _validate_budget(shape: tuple[int, ...], max_pixels: int, max_working_bytes: int) -> None:
    pixels = int(shape[0]) * int(shape[1])
    if pixels < 1 or pixels > int(max_pixels):
        raise ValueError(f"seam input has {pixels:,} pixels; maximum is {int(max_pixels):,}")
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    channels = 1 if len(shape) == 2 else int(shape[2])
    estimate = pixels * (4 * channels * 2 + 4 + 1)
    if estimate > int(max_working_bytes):
        raise MemoryError(f"seam requires about {estimate} bytes, limit is {int(max_working_bytes)}")


def _validate_graph_budget(
    shape: tuple[int, ...],
    overlap: np.ndarray,
    max_pixels: int,
    max_working_bytes: int,
) -> None:
    """Guard the much larger residual graph before allocating it.

    The estimate intentionally errs high.  Besides the source images, a
    compact residual graph stores ``head/current`` arrays, float64 residual
    capacities, integer endpoints/links, labels, and the push-relabel queue.
    ``backend="taichi"`` may additionally hold CPU-JIT map temporaries.  A
    caller may lower ``max_working_bytes`` for an application-specific budget;
    no graph allocation occurs before this check passes.
    """

    pixels = int(shape[0]) * int(shape[1])
    if pixels < 1 or pixels > int(max_pixels):
        raise ValueError(f"graph-cut input has {pixels:,} pixels; maximum is {int(max_pixels):,}")
    if pixels > int(MAX_GRAPH_CUT_PIXELS):
        raise ValueError(
            f"graph-cut input has {pixels:,} pixels; exact bounded solver maximum is "
            f"{int(MAX_GRAPH_CUT_PIXELS):,}"
        )
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    active = int(np.count_nonzero(overlap))
    # At most two internal undirected edges per pixel plus one boundary edge;
    # every directed residual edge stores three arrays (float64 + 2x int32).
    # The remaining 64 bytes/pixel cover maps, graph heads, queue, and labels.
    worst_directed_edges = 12 * active + 2
    channels = 1 if len(shape) == 2 else int(shape[2])
    estimate = int(worst_directed_edges) * 16 + pixels * (64 + channels * 8)
    if estimate > int(max_working_bytes):
        raise MemoryError(
            f"graph-cut requires about {estimate} bytes, limit is {int(max_working_bytes)}"
        )


def _graph_cut_maps_numpy(
    lhs: np.ndarray,
    rhs: np.ndarray,
    *,
    color_weight: float,
    gradient_weight: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(D_left, D_right, cross_image_difference)`` in float64.

    The finite binary energy solved by :func:`graph_cut_maxflow` is:

    ``D_left(i) [x_i=0] + D_right(i) [x_i=1]``
    ``+ V_ij [x_i != x_j]``.

    Unary costs prefer the locally smoother source.  The pairwise edge cost is
    formed from ``cross_image_difference`` and therefore discourages a cut
    through a strong image disagreement.  Keeping this construction explicit
    makes the max-flow result independently auditable against brute-force
    small-grid oracles.
    """

    left_gray = np.asarray(_gray(lhs), dtype=np.float32)
    right_gray = np.asarray(_gray(rhs), dtype=np.float32)
    gx_l = np.diff(left_gray, axis=1, prepend=left_gray[:, :1])
    gy_l = np.diff(left_gray, axis=0, prepend=left_gray[:1, :])
    gx_r = np.diff(right_gray, axis=1, prepend=right_gray[:, :1])
    gy_r = np.diff(right_gray, axis=0, prepend=right_gray[:1, :])
    unary_left = float(gradient_weight) * (np.abs(gx_l) + np.abs(gy_l))
    unary_right = float(gradient_weight) * (np.abs(gx_r) + np.abs(gy_r))
    cross_difference = float(color_weight) * np.abs(left_gray - right_gray)
    return (
        np.ascontiguousarray(unary_left, dtype=np.float64),
        np.ascontiguousarray(unary_right, dtype=np.float64),
        np.ascontiguousarray(cross_difference, dtype=np.float64),
    )


def _graph_cut_maps_taichi(
    lhs: np.ndarray,
    rhs: np.ndarray,
    *,
    color_weight: float,
    gradient_weight: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build graph maps with the explicit CPU-JIT Taichi leaf."""

    taichi = _ensure_taichi_cpu()
    left_gray = np.ascontiguousarray(_gray(lhs), dtype=np.float32)
    right_gray = np.ascontiguousarray(_gray(rhs), dtype=np.float32)
    unary_left = np.empty(left_gray.shape, dtype=np.float32)
    unary_right = np.empty(left_gray.shape, dtype=np.float32)
    cross_difference = np.empty(left_gray.shape, dtype=np.float32)
    _graph_cut_unary_kernel(
        left_gray,
        right_gray,
        unary_left,
        unary_right,
        cross_difference,
        float(gradient_weight),
        float(color_weight),
    )
    taichi.sync()
    return (
        np.ascontiguousarray(unary_left, dtype=np.float64),
        np.ascontiguousarray(unary_right, dtype=np.float64),
        np.ascontiguousarray(cross_difference, dtype=np.float64),
    )


def _graph_cut_maps_aot(
    lhs: np.ndarray,
    rhs: np.ndarray,
    *,
    color_weight: float,
    gradient_weight: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build static maps through the target-qualified panorama AOT leaf.

    The dynamic residual graph remains the same host implementation used by
    the NumPy and Taichi paths.  Importing lazily keeps the panorama module
    usable in installations that do not ship the AOT runtime or artifact.
    Missing/stale target artifacts propagate as the explicit AOT error from
    the research wrapper; no CPU/JIT fallback is attempted here.
    """

    from ..aot_api.research import graph_cut_unary_aot

    left_gray = np.ascontiguousarray(_gray(lhs), dtype=np.float32)
    right_gray = np.ascontiguousarray(_gray(rhs), dtype=np.float32)
    maps = graph_cut_unary_aot(
        left_gray,
        right_gray,
        color_weight=float(color_weight),
        gradient_weight=float(gradient_weight),
    )
    return (
        np.ascontiguousarray(maps["unary_left"], dtype=np.float64),
        np.ascontiguousarray(maps["unary_right"], dtype=np.float64),
        np.ascontiguousarray(maps["color_difference"], dtype=np.float64),
    )


class _ResidualGraph:
    """Compact float-capacity residual graph for deterministic max-flow.

    Arrays are preallocated once from the image's active-neighbour count.  A
    push-relabel implementation avoids Python object-per-edge overhead and is
    suitable for the bounded reference path.  Capacities remain float64 so the
    solver does not quantise image energies into an arbitrary integer scale.
    """

    def __init__(self, node_count: int, directed_edge_capacity: int) -> None:
        self.node_count = int(node_count)
        edge_capacity = max(2, int(directed_edge_capacity))
        self.head = np.full(self.node_count, -1, dtype=np.int32)
        self.to = np.empty(edge_capacity, dtype=np.int32)
        self.next = np.empty(edge_capacity, dtype=np.int32)
        self.capacity = np.zeros(edge_capacity, dtype=np.float64)
        self.edge_count = 0

    def add_edge(self, source: int, target: int, capacity: float) -> None:
        value = float(capacity)
        if not np.isfinite(value) or value < 0.0:
            raise ValueError("graph capacities must be finite and non-negative")
        if self.edge_count + 2 > self.to.size:
            raise MemoryError("graph residual edge capacity estimate was insufficient")
        edge = int(self.edge_count)
        reverse = edge + 1
        self.to[edge] = int(target)
        self.capacity[edge] = value
        self.next[edge] = self.head[int(source)]
        self.head[int(source)] = edge
        self.to[reverse] = int(source)
        self.capacity[reverse] = 0.0
        self.next[reverse] = self.head[int(target)]
        self.head[int(target)] = reverse
        self.edge_count += 2

    def _push(self, edge: int, amount: float, excess: np.ndarray) -> None:
        value = min(float(amount), float(self.capacity[int(edge)]))
        if value <= _GRAPH_EPS:
            return
        edge_index = int(edge)
        reverse_index = edge_index ^ 1
        source = int(self.to[reverse_index])
        target = int(self.to[edge_index])
        remainder = float(self.capacity[edge_index]) - value
        self.capacity[edge_index] = 0.0 if remainder <= _GRAPH_EPS else remainder
        self.capacity[reverse_index] += value
        excess[source] -= value
        excess[target] += value

    def max_flow(self, source: int, sink: int) -> float:
        """Run FIFO push-relabel and return the finite max-flow value."""

        source = int(source)
        sink = int(sink)
        if source == sink:
            raise ValueError("source and sink must be different")
        node_count = self.node_count
        height = np.zeros(node_count, dtype=np.int32)
        excess = np.zeros(node_count, dtype=np.float64)
        current = self.head.copy()
        in_queue = np.zeros(node_count, dtype=np.bool_)
        queue: deque[int] = deque()
        height[source] = node_count

        # Saturate the source arcs to create the initial preflow.
        edge = int(self.head[source])
        while edge != -1:
            if float(self.capacity[edge]) > _GRAPH_EPS:
                self._push(edge, float(self.capacity[edge]), excess)
                target = int(self.to[edge])
                if target != sink and target != source and excess[target] > _GRAPH_EPS and not in_queue[target]:
                    queue.append(target)
                    in_queue[target] = True
            edge = int(self.next[edge])

        while queue:
            node = int(queue.popleft())
            in_queue[node] = False
            if node == source or node == sink or excess[node] <= _GRAPH_EPS:
                continue
            while excess[node] > _GRAPH_EPS:
                edge = int(current[node])
                while edge != -1:
                    target = int(self.to[edge])
                    if float(self.capacity[edge]) > _GRAPH_EPS and int(height[node]) == int(height[target]) + 1:
                        break
                    edge = int(self.next[edge])
                current[node] = edge
                if edge == -1:
                    minimum = node_count + 1
                    probe = int(self.head[node])
                    while probe != -1:
                        if float(self.capacity[probe]) > _GRAPH_EPS:
                            minimum = min(minimum, int(height[int(self.to[probe])]))
                        probe = int(self.next[probe])
                    if minimum > node_count:
                        # No residual path remains.  This only occurs for an
                        # isolated zero-capacity component; discard numerical
                        # dust and keep the deterministic source-side label.
                        excess[node] = 0.0
                        break
                    height[node] = np.int32(minimum + 1)
                    current[node] = self.head[node]
                    continue
                target = int(self.to[edge])
                before = float(excess[target])
                amount = min(float(excess[node]), float(self.capacity[edge]))
                self._push(edge, amount, excess)
                current[node] = edge if float(self.capacity[edge]) > _GRAPH_EPS else self.next[edge]
                if (
                    target != source
                    and target != sink
                    and before <= _GRAPH_EPS
                    and excess[target] > _GRAPH_EPS
                    and not in_queue[target]
                ):
                    queue.append(target)
                    in_queue[target] = True
            if excess[node] > _GRAPH_EPS and not in_queue[node]:
                queue.append(node)
                in_queue[node] = True

        flow = 0.0
        edge = int(self.head[source])
        while edge != -1:
            # The reverse residual capacity on a source arc is the realised
            # flow.  Include both source->node and source->sink if present.
            flow += float(self.capacity[edge ^ 1])
            edge = int(self.next[edge])
        return float(flow)

    def source_reachable(self, source: int) -> np.ndarray:
        """Return residual nodes reachable from source after max-flow."""

        reachable = np.zeros(self.node_count, dtype=np.bool_)
        source = int(source)
        reachable[source] = True
        stack = [source]
        while stack:
            node = int(stack.pop())
            edge = int(self.head[node])
            while edge != -1:
                target = int(self.to[edge])
                if float(self.capacity[edge]) > _GRAPH_EPS and not reachable[target]:
                    reachable[target] = True
                    stack.append(target)
                edge = int(self.next[edge])
        return reachable


def _gray(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    if image.shape[2] == 1:
        return image[..., 0]
    return (0.299 * image[..., 0] + 0.587 * image[..., 1] + 0.114 * image[..., 2]).astype(np.float32)


def seam_energy(
    left: Any,
    right: Any,
    *,
    overlap_mask: Any | None = None,
    color_weight: float = 1.0,
    gradient_weight: float = 0.5,
    backend: str = "numpy",
) -> tuple[np.ndarray, np.ndarray]:
    """Return per-pixel energy and a validated overlap mask.

    ``backend="taichi"`` computes the pixelwise unary/pairwise energy on a
    CPU-JIT kernel.  Dynamic-programming backtracking remains deterministic
    host control flow; this split is explicit and does not silently substitute
    a different backend.
    """

    backend_name = _backend_name(backend)
    lhs = as_float32_image(left, name="left")
    rhs = as_float32_image(right, name="right")
    if lhs.shape != rhs.shape:
        raise ValueError(f"left and right must have the same shape, got {lhs.shape} vs {rhs.shape}")
    if not np.isfinite(lhs).all() or not np.isfinite(rhs).all():
        raise ValueError("left and right must contain only finite values")
    if not np.isfinite(float(color_weight)) or float(color_weight) < 0.0:
        raise ValueError("color_weight must be finite and non-negative")
    if not np.isfinite(float(gradient_weight)) or float(gradient_weight) < 0.0:
        raise ValueError("gradient_weight must be finite and non-negative")
    if overlap_mask is None:
        overlap = np.ones(lhs.shape[:2], dtype=bool)
    else:
        overlap = np.asarray(overlap_mask, dtype=bool)
        if overlap.shape != lhs.shape[:2]:
            raise ValueError(f"overlap_mask must have shape {lhs.shape[:2]}, got {overlap.shape}")
    if backend_name == "taichi":
        if lhs.ndim == 3 and lhs.shape[2] == 1:
            lhs = np.ascontiguousarray(lhs[..., 0], dtype=np.float32)
            rhs = np.ascontiguousarray(rhs[..., 0], dtype=np.float32)
        return _seam_energy_taichi(lhs, rhs, overlap, float(color_weight), float(gradient_weight)), overlap
    if lhs.ndim == 2:
        color = np.abs(lhs - rhs)
    else:
        color = np.mean(np.abs(lhs - rhs), axis=2)
    lhs_gray, rhs_gray = _gray(lhs), _gray(rhs)
    gx_l = np.diff(lhs_gray, axis=1, prepend=lhs_gray[:, :1])
    gy_l = np.diff(lhs_gray, axis=0, prepend=lhs_gray[:1, :])
    gx_r = np.diff(rhs_gray, axis=1, prepend=rhs_gray[:, :1])
    gy_r = np.diff(rhs_gray, axis=0, prepend=rhs_gray[:1, :])
    gradient = np.abs(gx_l - gx_r) + np.abs(gy_l - gy_r)
    energy = (float(color_weight) * color + float(gradient_weight) * gradient).astype(np.float32)
    # Invalid pixels are not candidates for a seam.  A finite sentinel keeps
    # the DP recurrence branch-free while labels are fixed afterwards.
    energy = np.where(overlap, energy, np.float32(1.0e6)).astype(np.float32)
    return energy, overlap


def _dp_vertical(energy: np.ndarray, overlap: np.ndarray) -> np.ndarray:
    h, w = energy.shape
    if not np.any(overlap):
        return np.zeros((h, w), dtype=bool)
    # Quantise the local cost before the sequential recurrence so the CPU-JIT
    # and NumPy paths share deterministic tie decisions despite f32 reduction
    # order differences below 1e-7.
    energy = np.round(np.asarray(energy, dtype=np.float64), decimals=6)
    cost = np.full((h, w), np.float64(1.0e30), dtype=np.float64)
    predecessor = np.zeros((h, w), dtype=np.int8)
    first = overlap[0]
    cost[0, first] = energy[0, first]
    for row in range(1, h):
        for col in range(w):
            if not overlap[row, col]:
                continue
            candidates = [col]
            if col > 0:
                candidates.append(col - 1)
            if col + 1 < w:
                candidates.append(col + 1)
            # ``min`` preserves insertion order on ties: straight, left,
            # right.  This makes the seam bit-for-bit deterministic.
            previous = min(candidates, key=lambda idx: (cost[row - 1, idx], idx != col, idx))
            cost[row, col] = float(energy[row, col]) + cost[row - 1, previous]
            predecessor[row, col] = np.int8(previous - col)
    last_candidates = np.flatnonzero(np.isfinite(cost[-1]) & (cost[-1] < 1.0e30))
    if len(last_candidates) == 0:
        return np.zeros((h, w), dtype=bool)
    col = int(min(last_candidates, key=lambda idx: (cost[-1, idx], idx)))
    seam = np.zeros((h, w), dtype=bool)
    for row in range(h - 1, -1, -1):
        seam[row, : col + 1] = True
        previous_col = col + int(predecessor[row, col]) if row > 0 else col
        col = max(0, min(w - 1, previous_col))
    return seam


def _dp_horizontal(energy: np.ndarray, overlap: np.ndarray) -> np.ndarray:
    # Transposition lets the vertical implementation define all tie-breaking
    # rules in one place.
    transposed = _dp_vertical(energy.T, overlap.T)
    return transposed.T


def dynamic_programming_seam(
    left: Any,
    right: Any,
    *,
    overlap_mask: Any | None = None,
    direction: str = "vertical",
    color_weight: float = 1.0,
    gradient_weight: float = 0.5,
    backend: str = "numpy",
    max_pixels: int = MAX_SEAM_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
) -> np.ndarray:
    """Return a boolean label map where ``True`` selects ``right``.

    A monotone seam is found only inside the overlap.  Outside the overlap the
    valid source is selected directly (right where only right is valid, left
    where only left is valid).  ``backend="taichi"`` computes the energy with
    the CPU-JIT kernel and keeps the sequential recurrence/backtrack explicit.
    """

    _backend_name(backend)
    lhs = as_float32_image(left, name="left")
    rhs = as_float32_image(right, name="right")
    _validate_budget(lhs.shape, int(max_pixels), int(max_working_bytes))
    if lhs.shape != rhs.shape:
        raise ValueError("left and right must have the same shape")
    direction_name = str(direction).lower()
    if direction_name not in {"vertical", "horizontal"}:
        raise ValueError("direction must be 'vertical' or 'horizontal'")
    energy, overlap = seam_energy(
        lhs,
        rhs,
        overlap_mask=overlap_mask,
        color_weight=color_weight,
        gradient_weight=gradient_weight,
        backend=backend,
    )
    labels = _dp_vertical(energy, overlap) if direction_name == "vertical" else _dp_horizontal(energy, overlap)
    if overlap_mask is not None:
        supplied = np.asarray(overlap_mask, dtype=bool)
        labels = np.where(supplied, labels, False)
    return np.ascontiguousarray(labels, dtype=bool)


def graph_cut_surrogate(
    left: Any,
    right: Any,
    *,
    overlap_mask: Any | None = None,
    smoothness: float = 0.25,
    iterations: int = 4,
    color_weight: float = 1.0,
    gradient_weight: float = 0.5,
    backend: str = "numpy",
    max_pixels: int = MAX_SEAM_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
) -> np.ndarray:
    """Deterministic local binary-label seam surrogate.

    The update minimises unary local-gradient cost plus a four-neighbour Potts
    smoothness term in row-major order.  It is intentionally named
    *surrogate*: it has no max-flow/min-cut guarantee, but is bounded and
    reproducible when a full graph-cut dependency is unavailable.  With
    ``backend="taichi"`` only the unary energy generation is JIT-native; the
    row-major label updates remain explicit host control flow.
    """

    _backend_name(backend)
    lhs = as_float32_image(left, name="left")
    rhs = as_float32_image(right, name="right")
    _validate_budget(lhs.shape, int(max_pixels), int(max_working_bytes))
    if lhs.shape != rhs.shape:
        raise ValueError("left and right must have the same shape")
    if not np.isfinite(float(smoothness)) or float(smoothness) < 0.0:
        raise ValueError("smoothness must be finite and non-negative")
    if int(iterations) < 1 or int(iterations) > 32:
        raise ValueError("iterations must be between 1 and 32")
    energy, overlap = seam_energy(
        lhs,
        rhs,
        overlap_mask=overlap_mask,
        color_weight=color_weight,
        gradient_weight=gradient_weight,
        backend=backend,
    )
    # Unary costs favour a locally smooth source (cutting through a strong
    # edge is undesirable).  The pairwise disagreement already lives in the
    # DP initialisation; keeping a per-source gradient term here gives the
    # surrogate a meaningful label preference without claiming a full graph
    # cut solution.
    gray_left = _gray(lhs)
    gray_right = _gray(rhs)
    gx_left = np.diff(gray_left, axis=1, prepend=gray_left[:, :1])
    gy_left = np.diff(gray_left, axis=0, prepend=gray_left[:1, :])
    gx_right = np.diff(gray_right, axis=1, prepend=gray_right[:, :1])
    gy_right = np.diff(gray_right, axis=0, prepend=gray_right[:1, :])
    unary_left = np.abs(gx_left) + np.abs(gy_left)
    unary_right = np.abs(gx_right) + np.abs(gy_right)
    labels = np.asarray(dynamic_programming_seam(
        lhs,
        rhs,
        overlap_mask=overlap_mask,
        backend=backend,
        max_pixels=max_pixels,
        max_working_bytes=max_working_bytes,
        color_weight=color_weight,
        gradient_weight=gradient_weight,
    ), dtype=bool)
    for _ in range(int(iterations)):
        changed = False
        for row in range(lhs.shape[0]):
            for col in range(lhs.shape[1]):
                if not overlap[row, col]:
                    continue
                neighbours = []
                if row > 0:
                    neighbours.append(labels[row - 1, col])
                if row + 1 < lhs.shape[0]:
                    neighbours.append(labels[row + 1, col])
                if col > 0:
                    neighbours.append(labels[row, col - 1])
                if col + 1 < lhs.shape[1]:
                    neighbours.append(labels[row, col + 1])
                right_neighbours = sum(bool(value) for value in neighbours)
                left_cost = float(unary_left[row, col]) + float(smoothness) * right_neighbours
                right_cost = float(unary_right[row, col]) + float(smoothness) * (len(neighbours) - right_neighbours)
                candidate = bool(right_cost < left_cost)  # deterministic left tie
                if candidate != bool(labels[row, col]):
                    labels[row, col] = candidate
                    changed = True
        if not changed:
            break
    return np.ascontiguousarray(np.where(overlap, labels, False), dtype=bool)


def graph_cut_maxflow(
    left: Any,
    right: Any,
    *,
    overlap_mask: Any | None = None,
    smoothness: float = 0.25,
    color_weight: float = 1.0,
    gradient_weight: float = 0.5,
    backend: str = "numpy",
    max_pixels: int = MAX_GRAPH_CUT_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
) -> np.ndarray:
    """Return an exact binary s/t min-cut seam label map.

    ``False`` selects ``left`` and ``True`` selects ``right``.  For active
    overlap pixels, the solved energy is

    ``D_left(i) + D_right(i) + V_ij``

    where ``D_left/D_right`` are the local grayscale gradient magnitudes (each
    scaled by ``gradient_weight``), and every four-neighbour disagreement has
    ``V_ij = smoothness * (1 + mean(cross_image_difference))``.  A neighbour
    outside the supplied overlap is a fixed left label and contributes the
    corresponding boundary penalty when the active node chooses right.

    The residual push-relabel solver is a deterministic float64 reference
    implementation.  Equal/zero-capacity cuts receive a tiny deterministic
    source-side (left) tie-break.  ``backend="taichi"`` only moves the map
    construction to an explicit CPU-JIT kernel; the dynamic graph and min-cut
    remain on the host.  ``backend="aot"`` uses the target-qualified static
    unary-map leaf and the same bounded host residual solver.  Missing or
    stale target artifacts are surfaced explicitly; no CPU/JIT fallback is
    attempted.  The conservative graph budget is checked before
    residual-array allocation.
    """

    backend_name = _backend_name(backend, allow_aot=True)
    lhs = as_float32_image(left, name="left")
    rhs = as_float32_image(right, name="right")
    if lhs.shape != rhs.shape:
        raise ValueError(f"left and right must have the same shape, got {lhs.shape} vs {rhs.shape}")
    if lhs.ndim not in {2, 3}:
        raise ValueError("left and right must be 2-D grayscale or 3-D color images")
    if not np.isfinite(lhs).all() or not np.isfinite(rhs).all():
        raise ValueError("left and right must contain only finite values")
    if not np.isfinite(float(smoothness)) or float(smoothness) < 0.0:
        raise ValueError("smoothness must be finite and non-negative")
    if not np.isfinite(float(color_weight)) or float(color_weight) < 0.0:
        raise ValueError("color_weight must be finite and non-negative")
    if not np.isfinite(float(gradient_weight)) or float(gradient_weight) < 0.0:
        raise ValueError("gradient_weight must be finite and non-negative")
    if overlap_mask is None:
        overlap = np.ones(lhs.shape[:2], dtype=bool)
    else:
        overlap = np.asarray(overlap_mask, dtype=bool)
        if overlap.shape != lhs.shape[:2]:
            raise ValueError(f"overlap_mask must have shape {lhs.shape[:2]}, got {overlap.shape}")
        overlap = np.ascontiguousarray(overlap, dtype=bool)
    _validate_graph_budget(lhs.shape, overlap, int(max_pixels), int(max_working_bytes))
    if not np.any(overlap):
        return np.zeros(lhs.shape[:2], dtype=bool)

    if backend_name == "taichi":
        unary_left, unary_right, cross_difference = _graph_cut_maps_taichi(
            lhs,
            rhs,
            color_weight=float(color_weight),
            gradient_weight=float(gradient_weight),
        )
    elif backend_name == "aot":
        unary_left, unary_right, cross_difference = _graph_cut_maps_aot(
            lhs,
            rhs,
            color_weight=float(color_weight),
            gradient_weight=float(gradient_weight),
        )
    else:
        unary_left, unary_right, cross_difference = _graph_cut_maps_numpy(
            lhs,
            rhs,
            color_weight=float(color_weight),
            gradient_weight=float(gradient_weight),
        )
    if not (
        np.isfinite(unary_left).all()
        and np.isfinite(unary_right).all()
        and np.isfinite(cross_difference).all()
    ):
        raise ValueError("graph-cut energy maps overflowed; reduce image/weight magnitude")

    height, width = lhs.shape[:2]
    flat_overlap = overlap.reshape(-1)
    active_flat = np.flatnonzero(flat_overlap).astype(np.int32, copy=False)
    active_count = int(active_flat.size)
    node_index = np.full(height * width, -1, dtype=np.int32)
    node_index[active_flat] = np.arange(active_count, dtype=np.int32)
    internal_horizontal = overlap[:, :-1] & overlap[:, 1:] if width > 1 else np.zeros((height, 0), dtype=bool)
    internal_vertical = overlap[:-1, :] & overlap[1:, :] if height > 1 else np.zeros((0, width), dtype=bool)
    pair_count = int(np.count_nonzero(internal_horizontal) + np.count_nonzero(internal_vertical))
    boundary_count = 0
    boundary_count += int(np.count_nonzero(overlap[:, 0])) if width else 0
    boundary_count += int(np.count_nonzero(overlap[:, -1])) if width else 0
    boundary_count += int(np.count_nonzero(overlap[0, :])) if height else 0
    boundary_count += int(np.count_nonzero(overlap[-1, :])) if height else 0
    if width > 1:
        boundary_count += int(np.count_nonzero(overlap[:, :-1] & ~overlap[:, 1:]))
        boundary_count += int(np.count_nonzero(~overlap[:, :-1] & overlap[:, 1:]))
    if height > 1:
        boundary_count += int(np.count_nonzero(overlap[:-1, :] & ~overlap[1:, :]))
        boundary_count += int(np.count_nonzero(~overlap[:-1, :] & overlap[1:, :]))
    # Two source/sink arcs per active node, two directed arcs per internal
    # undirected pair, and one source boundary arc per active/outside edge;
    # each call stores a forward and reverse residual edge.
    directed_calls = 2 * active_count + 2 * pair_count + boundary_count
    residual_capacity = 2 * directed_calls + 4
    source = active_count
    sink = active_count + 1
    graph = _ResidualGraph(active_count + 2, residual_capacity)

    for flat_index in active_flat:
        flat = int(flat_index)
        row, col = divmod(flat, width)
        node = int(node_index[flat])
        # A vanishing-capacity tie is resolved toward the source/left label.
        # It is far below ordinary image energies but prevents an all-zero
        # graph from returning an arbitrary sink-side component.
        graph.add_edge(source, node, float(unary_right[row, col]) + 8.0 * _GRAPH_EPS)
        graph.add_edge(node, sink, float(unary_left[row, col]))

        # Only right/down pairs are inserted; each is represented as two
        # directed capacities so a cut crossing either orientation pays once.
        if col + 1 < width:
            neighbour_flat = flat + 1
            if bool(overlap[row, col + 1]):
                neighbour = int(node_index[neighbour_flat])
                pair = float(smoothness) * (
                    1.0 + 0.5 * (float(cross_difference[row, col]) + float(cross_difference[row, col + 1]))
                )
                graph.add_edge(node, neighbour, pair)
                graph.add_edge(neighbour, node, pair)
            else:
                boundary = float(smoothness) * (1.0 + float(cross_difference[row, col]))
                graph.add_edge(source, node, boundary)
        elif width:
            boundary = float(smoothness) * (1.0 + float(cross_difference[row, col]))
            graph.add_edge(source, node, boundary)
        if row + 1 < height:
            neighbour_flat = flat + width
            if bool(overlap[row + 1, col]):
                neighbour = int(node_index[neighbour_flat])
                pair = float(smoothness) * (
                    1.0 + 0.5 * (float(cross_difference[row, col]) + float(cross_difference[row + 1, col]))
                )
                graph.add_edge(node, neighbour, pair)
                graph.add_edge(neighbour, node, pair)
            else:
                boundary = float(smoothness) * (1.0 + float(cross_difference[row, col]))
                graph.add_edge(source, node, boundary)
        elif height:
            boundary = float(smoothness) * (1.0 + float(cross_difference[row, col]))
            graph.add_edge(source, node, boundary)
        if col == 0 and width:
            graph.add_edge(source, node, float(smoothness) * (1.0 + float(cross_difference[row, col])))
        elif col > 0 and not bool(overlap[row, col - 1]):
            graph.add_edge(source, node, float(smoothness) * (1.0 + float(cross_difference[row, col])))
        if row == 0 and height:
            graph.add_edge(source, node, float(smoothness) * (1.0 + float(cross_difference[row, col])))
        elif row > 0 and not bool(overlap[row - 1, col]):
            graph.add_edge(source, node, float(smoothness) * (1.0 + float(cross_difference[row, col])))

    graph.max_flow(source, sink)
    reachable = graph.source_reachable(source)
    labels = np.zeros(height * width, dtype=bool)
    labels[active_flat] = ~reachable[:active_count][node_index[active_flat]]
    return np.ascontiguousarray(labels.reshape(height, width), dtype=bool)


def blend_with_seam(left: Any, right: Any, labels: Any, *, overlap_mask: Any | None = None) -> np.ndarray:
    """Composite two same-shaped images using a boolean right-label map."""

    lhs = as_float32_image(left, name="left")
    rhs = as_float32_image(right, name="right")
    if lhs.shape != rhs.shape:
        raise ValueError("left and right must have the same shape")
    labels_array = np.asarray(labels, dtype=bool)
    if labels_array.shape != lhs.shape[:2]:
        raise ValueError("labels must match image height and width")
    if overlap_mask is None:
        overlap = np.ones(labels_array.shape, dtype=bool)
    else:
        overlap = np.asarray(overlap_mask, dtype=bool)
        if overlap.shape != labels_array.shape:
            raise ValueError("overlap_mask must match labels")
    output = np.where(labels_array[..., None] if lhs.ndim == 3 else labels_array, rhs, lhs).astype(np.float32)
    only_right = overlap & labels_array
    if lhs.ndim == 2:
        output[only_right] = rhs[only_right]
    else:
        output[only_right, :] = rhs[only_right, :]
    return np.ascontiguousarray(output)


__all__ = [
    "seam_energy",
    "dynamic_programming_seam",
    "graph_cut_surrogate",
    "graph_cut_maxflow",
    "blend_with_seam",
]

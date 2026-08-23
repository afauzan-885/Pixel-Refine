import concurrent.futures
from functools import lru_cache
import os

import cv2
import numpy as np


# Creating a thread pool is not free, and cv2's remap/flow kernels already
# release the GIL.  Below this pixel count the scheduling cost is usually
# larger than the useful parallel work (especially for thumbnail-sized
# previews).  The value is deliberately an implementation detail so the
# existing public alignment API remains unchanged.  It can be tuned for a
# particular CPU without changing call sites.
_DEFAULT_PARALLEL_PIXELS = 600_000
_DEFAULT_MAX_FLOW_WORKERS = 4
_GRID_CACHE_MAX_PIXELS = 1_048_576


def _parallel_pixel_threshold():
    try:
        value = int(os.environ.get("PIXEL_REFINE_FLOW_PARALLEL_MIN_PIXELS", ""))
    except (TypeError, ValueError):
        value = _DEFAULT_PARALLEL_PIXELS
    return max(0, value or _DEFAULT_PARALLEL_PIXELS)


def _flow_worker_limit(item_count):
    """Return a bounded worker count for a local, short-lived executor."""
    try:
        configured = int(os.environ.get("PIXEL_REFINE_FLOW_MAX_WORKERS", ""))
    except (TypeError, ValueError):
        configured = 0
    configured = configured or _DEFAULT_MAX_FLOW_WORKERS
    configured = max(1, configured)
    return max(1, min(int(item_count), configured, os.cpu_count() or 4))


def _should_parallelize(height, width, item_count, use_multi_core, executor):
    """Choose parallel flow dispatch without changing numerical ordering.

    A caller-supplied executor is assumed to be shared by the surrounding
    pipeline, so its creation cost has already been paid and the threshold is
    bypassed.  For a local executor, avoid spawning threads for small frames.
    """
    if not use_multi_core or item_count <= 1:
        return False
    if executor is not None:
        return True
    return int(height) * int(width) >= _parallel_pixel_threshold()


def _bounded_map(executor, function, items, max_in_flight):
    """Yield completed work while keeping only a small number of blocks live."""
    iterator = iter(items)
    pending = set()
    for _ in range(max(1, int(max_in_flight))):
        try:
            pending.add(executor.submit(function, next(iterator)))
        except StopIteration:
            break
    while pending:
        done, pending = concurrent.futures.wait(
            pending, return_when=concurrent.futures.FIRST_COMPLETED
        )
        for future in done:
            yield future.result()
            try:
                pending.add(executor.submit(function, next(iterator)))
            except StopIteration:
                pass


def _bounded_ordered_map(executor, function, items, max_in_flight):
    """Yield bounded parallel results in submission order.

    Optical-flow accumulation uses floating-point addition.  Keeping the
    original tile order avoids introducing a numerical change merely because
    a worker completed earlier, while the bounded queue prevents completed
    warped tiles from accumulating in memory.
    """
    from collections import deque

    iterator = iter(items)
    pending = deque()
    for _ in range(max(1, int(max_in_flight))):
        try:
            pending.append(executor.submit(function, next(iterator)))
        except StopIteration:
            break
    while pending:
        future = pending.popleft()
        yield future.result()
        try:
            pending.append(executor.submit(function, next(iterator)))
        except StopIteration:
            pass


def to_flow_gray_u8(image):
    if image is None:
        return None
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if image.dtype == np.uint8:
        return image
    if image.dtype == np.uint16:
        return (image >> 8).astype(np.uint8, copy=False)
    return np.clip(image, 0, 255).astype(np.uint8, copy=False)


def iter_flow_tiles(width, height, cols=4, rows=3, overlap=0.20):
    tile_w = max(1, width // cols)
    tile_h = max(1, height // rows)
    overlap_w = int(tile_w * overlap)
    overlap_h = int(tile_h * overlap)
    for row in range(rows):
        for col in range(cols):
            x0 = col * tile_w
            y0 = row * tile_h
            x1 = width if col == cols - 1 else min(width, x0 + tile_w)
            y1 = height if row == rows - 1 else min(height, y0 + tile_h)
            rx0 = max(0, x0 - overlap_w)
            ry0 = max(0, y0 - overlap_h)
            rx1 = min(width, x1 + overlap_w)
            ry1 = min(height, y1 + overlap_h)
            yield {
                "valid": (x0, y0, x1, y1),
                "roi": (rx0, ry0, rx1, ry1),
            }


def iter_runtime_flow_blocks(width, height, halo=0):
    """Yield flow regions from the shared compute-block runtime."""
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_aot.block import BlockGrid

    runtime_config = taichi_aot.get_block_config()
    if not runtime_config.enabled:
        yield {"valid": (0, 0, width, height), "roi": (0, 0, width, height)}
        return
    size = runtime_config.normalized_size()
    for block in BlockGrid((height, width), size=size, halo=max(0, int(halo))):
        yield {
            "valid": (block.x0, block.y0, block.x1, block.y1),
            "roi": (block.read_x0, block.read_y0, block.read_x1, block.read_y1),
        }


def _to_float32_tile(tile):
    return tile.astype(np.float32, copy=False)


def _restore_dtype(image, dtype):
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
        np.clip(image, info.min, info.max, out=image)
    return image.astype(dtype, copy=False)


def _accumulate_weighted_tile(accumulator, warped, weight, x, y):
    """Accumulate one warped tile without a second weighted temporary.

    ``warped`` is freshly allocated by ``cv2.remap`` and is no longer used
    after this call.  Converting it in place (when possible) and multiplying
    in place avoids the short-lived ``weighted * weight`` array that used to
    double the peak allocation for every tile.  The numerical operation and
    accumulation order are unchanged.
    """
    weighted = _to_float32_tile(warped)
    h_tile, w_tile = weighted.shape[:2]
    target = accumulator[y : y + h_tile, x : x + w_tile]
    if weighted.ndim == 3:
        np.multiply(weighted, weight[..., None], out=weighted)
    else:
        np.multiply(weighted, weight, out=weighted)
    np.add(target, weighted, out=target)
    return h_tile, w_tile


def warp_tile_with_flow(target_tile, flow):
    height, width = flow.shape[:2]
    grid = _cached_coordinate_grid(height, width)
    if grid is None:
        grid_x, grid_y = np.meshgrid(
            np.arange(width, dtype=np.float32),
            np.arange(height, dtype=np.float32),
        )
    else:
        grid_x, grid_y = grid

    # Reuse the coordinate-grid storage and only allocate the two maps that
    # cv2.remap requires.  The old expression form created temporary arrays
    # for both additions on every tile.
    flow_x = flow[..., 0].astype(np.float32, copy=False)
    flow_y = flow[..., 1].astype(np.float32, copy=False)
    map_x = np.empty_like(grid_x)
    map_y = np.empty_like(grid_y)
    np.add(grid_x, flow_x, out=map_x)
    np.add(grid_y, flow_y, out=map_y)
    return cv2.remap(
        target_tile,
        map_x,
        map_y,
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT,
    )


@lru_cache(maxsize=2)
def _cached_coordinate_grid(height, width):
    """Cache small tile coordinate grids; avoid retaining full-frame grids."""
    height = int(height)
    width = int(width)
    if height <= 0 or width <= 0 or height * width > _GRID_CACHE_MAX_PIXELS:
        return None
    grid_x, grid_y = np.meshgrid(
        np.arange(width, dtype=np.float32),
        np.arange(height, dtype=np.float32),
    )
    grid_x.setflags(write=False)
    grid_y.setflags(write=False)
    return grid_x, grid_y


@lru_cache(maxsize=4)
def _cached_weight_mask(height, width):
    height = int(height)
    width = int(width)
    y = np.hanning(height) if height > 1 else np.ones(1, dtype=np.float32)
    x = np.hanning(width) if width > 1 else np.ones(1, dtype=np.float32)
    mask = np.outer(y, x).astype(np.float32)
    mask_scale = float(mask.max())
    if mask_scale <= 0:
        mask.fill(1.0)
    else:
        # Normalize and clamp in-place; this cache is shared read-only after
        # construction, so retaining intermediate division/max arrays only
        # increases peak allocation during the first tile of a new shape.
        mask /= mask_scale
        np.maximum(mask, np.float32(1e-3), out=mask)
    mask.setflags(write=False)
    return mask


def make_weight_mask(height, width):
    # Masks are read-only in the compositor, so sharing same-shaped masks
    # across tiles removes repeated hanning/outer allocations.
    return _cached_weight_mask(int(height), int(width))


def _compute_and_warp_tile(reference_gray, target_gray, target_original, tile, flow_func):
    vx0, vy0, vx1, vy1 = tile["valid"]
    rx0, ry0, rx1, ry1 = tile["roi"]
    ref_roi = reference_gray[ry0:ry1, rx0:rx1]
    target_roi_gray = target_gray[ry0:ry1, rx0:rx1]
    target_roi_original = target_original[ry0:ry1, rx0:rx1]
    flow_roi = flow_func(ref_roi, target_roi_gray)
    if flow_roi is None:
        return None

    ox0 = vx0 - rx0
    oy0 = vy0 - ry0
    ox1 = ox0 + (vx1 - vx0)
    oy1 = oy0 + (vy1 - vy0)
    flow_valid = flow_roi[oy0:oy1, ox0:ox1]
    target_valid = target_roi_original[oy0:oy1, ox0:ox1]
    warped = warp_tile_with_flow(target_valid, flow_valid)
    return vx0, vy0, warped, make_weight_mask(warped.shape[0], warped.shape[1])


def align_with_tiled_flow(
    reference,
    target,
    flow_func,
    cols=4,
    rows=3,
    overlap=0.20,
    use_multi_core=True,
    stop_requested=None,
    executor=None,
    target_for_warping=None,
):
    reference_gray = to_flow_gray_u8(reference)
    target_gray = to_flow_gray_u8(target)
    if reference_gray is None or target_gray is None:
        return None

    height, width = reference_gray.shape[:2]
    # Keep the tile iterator lazy.  The normal tiled-flow path has only a few
    # regions, but callers can request a dense grid and should not pay for a
    # list of dictionaries before the first worker starts.
    tiles = iter_flow_tiles(width, height, cols=cols, rows=rows, overlap=overlap)
    tile_count = max(1, int(cols)) * max(1, int(rows))
    output_shape = target.shape
    accumulator = np.zeros(output_shape, dtype=np.float32)
    weights = np.zeros((height, width), dtype=np.float32)

    def run_tile(tile):
        if stop_requested and stop_requested():
            return None
        tgt_warp = target_for_warping if target_for_warping is not None else target
        return _compute_and_warp_tile(reference_gray, target_gray, tgt_warp, tile, flow_func)

    pool = None
    parallel_tiles = _should_parallelize(
        height, width, tile_count, use_multi_core, executor
    )
    if parallel_tiles:
        if executor is not None:
            # Stream completed tiles instead of materializing every warped
            # tile at once.  This keeps the public ordering/accumulation
            # semantics unchanged while bounding peak host memory.
            max_workers = max(
                1, int(getattr(executor, "_max_workers", tile_count))
            )
            results = _bounded_ordered_map(executor, run_tile, tiles, max_workers)
        else:
            max_workers = _flow_worker_limit(tile_count)
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            results = _bounded_ordered_map(pool, run_tile, tiles, max_workers)
    else:
        results = map(run_tile, tiles)

    try:
        for result in results:
            if result is None:
                continue
            x, y, warped, weight = result
            h_tile, w_tile = _accumulate_weighted_tile(
                accumulator, warped, weight, x, y
            )
            weights[y : y + h_tile, x : x + w_tile] += weight
    finally:
        if pool is not None:
            pool.shutdown(wait=True)

    valid = weights > 0
    if not np.any(valid):
        return None
    if target.ndim == 3:
        # ``accumulator[valid] / weights[valid, None]`` creates two large
        # advanced-indexing temporaries.  A masked ufunc keeps the full-frame
        # result resident in-place and only retains the existing validity mask.
        np.divide(
            accumulator,
            weights[..., None],
            out=accumulator,
            where=valid[..., None],
        )
    else:
        np.divide(accumulator, weights, out=accumulator, where=valid)
    if not np.all(valid):
        # NumPy casts directly into the float32 accumulator.  Avoid creating
        # a full-resolution float32 copy of the target just for uncovered
        # pixels (which are uncommon but costly on large frames).
        accumulator[~valid] = target[~valid]
    return _restore_dtype(accumulator, target.dtype)


def align_with_block_flow(
    reference,
    target,
    flow_func,
    *,
    halo=0,
    use_multi_core=True,
    stop_requested=None,
    executor=None,
    target_for_warping=None,
):
    """Run the legacy CPU flow compositor on runtime-owned BlockGrid regions."""
    reference_gray = to_flow_gray_u8(reference)
    target_gray = to_flow_gray_u8(target)
    if reference_gray is None or target_gray is None:
        return None

    height, width = reference_gray.shape[:2]
    # Block grids can contain thousands of regions for large images.  Keep
    # only the bounded futures/results live instead of materialising every
    # block descriptor up front.
    from taichi_vision import taichi_aot
    runtime_config = taichi_aot.get_block_config()
    if runtime_config.enabled:
        # ``BlockConfig.normalized_size()`` is a ``(height, width)`` pair.
        # The old scalar assumption only surfaced when the runtime block mode
        # was actually enabled, so full-frame tests never exercised it.  Keep
        # rectangular block support and compute the count per axis instead of
        # coercing the pair (which would break custom block dimensions).
        normalized = runtime_config.normalized_size()
        # Keep compatibility with older lightweight runtime stubs that
        # returned a scalar while the production ``BlockConfig`` returns a
        # pair.  Rectangular production grids retain their independent axes.
        if isinstance(normalized, (tuple, list)):
            block_h, block_w = normalized[0], normalized[1]
        else:
            block_h = block_w = normalized
        block_count = (
            (int(height) + int(block_h) - 1) // int(block_h)
        ) * ((int(width) + int(block_w) - 1) // int(block_w))
    else:
        block_count = 1
    blocks = iter_runtime_flow_blocks(width, height, halo=halo)
    output_shape = target.shape
    accumulator = np.zeros(output_shape, dtype=np.float32)
    weights = np.zeros((height, width), dtype=np.float32)

    def run_block(block):
        if stop_requested and stop_requested():
            return None
        source = target_for_warping if target_for_warping is not None else target
        return _compute_and_warp_tile(
            reference_gray, target_gray, source, block, flow_func
        )

    max_workers = _flow_worker_limit(block_count)
    pool = None
    parallel_blocks = _should_parallelize(
        height, width, block_count, use_multi_core, executor
    )
    if parallel_blocks:
        if executor is not None:
            results = _bounded_ordered_map(
                executor,
                run_block,
                blocks,
                max(1, int(getattr(executor, "_max_workers", max_workers))),
            )
        else:
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            results = _bounded_ordered_map(pool, run_block, blocks, max_workers)
    else:
        results = map(run_block, blocks)

    try:
        for item in results:
            if item is None:
                continue
            x, y, warped, weight = item
            h_block, w_block = _accumulate_weighted_tile(
                accumulator, warped, weight, x, y
            )
            weights[y:y + h_block, x:x + w_block] += weight
    finally:
        if pool is not None:
            pool.shutdown(wait=True)

    valid = weights > 0
    if not np.any(valid):
        return None
    if target.ndim == 3:
        np.divide(
            accumulator,
            weights[..., None],
            out=accumulator,
            where=valid[..., None],
        )
    else:
        np.divide(accumulator, weights, out=accumulator, where=valid)
    if not np.all(valid):
        accumulator[~valid] = target[~valid]
    return _restore_dtype(accumulator, target.dtype)

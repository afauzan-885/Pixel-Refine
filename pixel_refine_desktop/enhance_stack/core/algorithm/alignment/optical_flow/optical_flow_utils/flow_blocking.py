import concurrent.futures
import os

import cv2
import numpy as np


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
    from taichi_library import taichi_aot
    from taichi_library.taichi_aot.block import BlockGrid

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


def warp_tile_with_flow(target_tile, flow):
    height, width = flow.shape[:2]
    grid_x, grid_y = np.meshgrid(
        np.arange(width, dtype=np.float32),
        np.arange(height, dtype=np.float32),
    )
    map_x = grid_x + flow[..., 0].astype(np.float32, copy=False)
    map_y = grid_y + flow[..., 1].astype(np.float32, copy=False)
    return cv2.remap(
        target_tile,
        map_x,
        map_y,
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT,
    )


def make_weight_mask(height, width):
    y = np.hanning(height) if height > 1 else np.ones(1, dtype=np.float32)
    x = np.hanning(width) if width > 1 else np.ones(1, dtype=np.float32)
    mask = np.outer(y, x).astype(np.float32)
    if float(mask.max()) <= 0:
        return np.ones((height, width), dtype=np.float32)
    return np.maximum(mask / float(mask.max()), 1e-3).astype(np.float32)


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
    tiles = list(iter_flow_tiles(width, height, cols=cols, rows=rows, overlap=overlap))
    output_shape = target.shape
    accumulator = np.zeros(output_shape, dtype=np.float32)
    weights = np.zeros((height, width), dtype=np.float32)

    def run_tile(tile):
        if stop_requested and stop_requested():
            return None
        tgt_warp = target_for_warping if target_for_warping is not None else target
        return _compute_and_warp_tile(reference_gray, target_gray, tgt_warp, tile, flow_func)

    if use_multi_core and len(tiles) > 1:
        if executor is not None:
            results = list(executor.map(run_tile, tiles))
        else:
            max_workers = max(1, min(len(tiles), os.cpu_count() or 4))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(run_tile, tiles))
    else:
        results = [run_tile(tile) for tile in tiles]

    for result in results:
        if result is None:
            continue
        x, y, warped, weight = result
        h_tile, w_tile = warped.shape[:2]
        if target.ndim == 3:
            accumulator[y : y + h_tile, x : x + w_tile] += _to_float32_tile(warped) * weight[..., None]
        else:
            accumulator[y : y + h_tile, x : x + w_tile] += _to_float32_tile(warped) * weight
        weights[y : y + h_tile, x : x + w_tile] += weight

    valid = weights > 0
    if not np.any(valid):
        return None
    if target.ndim == 3:
        accumulator[valid] = accumulator[valid] / weights[valid, None]
    else:
        accumulator[valid] = accumulator[valid] / weights[valid]
    if not np.all(valid):
        accumulator[~valid] = target.astype(np.float32, copy=False)[~valid]
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
    blocks = list(iter_runtime_flow_blocks(width, height, halo=halo))
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

    max_workers = max(1, min(len(blocks), os.cpu_count() or 4))
    pool = None
    if use_multi_core and len(blocks) > 1:
        if executor is not None:
            results = _bounded_map(
                executor,
                run_block,
                blocks,
                max(1, int(getattr(executor, "_max_workers", max_workers))),
            )
        else:
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            results = _bounded_map(pool, run_block, blocks, max_workers)
    else:
        results = map(run_block, blocks)

    try:
        for item in results:
            if item is None:
                continue
            x, y, warped, weight = item
            h_block, w_block = warped.shape[:2]
            weighted = _to_float32_tile(warped)
            if target.ndim == 3:
                accumulator[y:y + h_block, x:x + w_block] += weighted * weight[..., None]
            else:
                accumulator[y:y + h_block, x:x + w_block] += weighted * weight
            weights[y:y + h_block, x:x + w_block] += weight
    finally:
        if pool is not None:
            pool.shutdown(wait=True)

    valid = weights > 0
    if not np.any(valid):
        return None
    if target.ndim == 3:
        accumulator[valid] /= weights[valid, None]
    else:
        accumulator[valid] /= weights[valid]
    if not np.all(valid):
        accumulator[~valid] = target.astype(np.float32, copy=False)[~valid]
    return _restore_dtype(accumulator, target.dtype)

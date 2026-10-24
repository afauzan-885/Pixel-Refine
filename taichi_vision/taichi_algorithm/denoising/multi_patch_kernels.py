"""Taichi AOT kernels for FusionNet's per-location multi-patch search."""

import taichi as ti


MAX_NEIGHBORS = 16
PATCH_RADIUS = 2
PATCH_AREA = (PATCH_RADIUS * 2 + 1) ** 2
_F32_MAX = 3.402823466e38


@ti.kernel
def multi_patch_topk_kernel(
    reference: ti.types.ndarray(ti.f32, 3),
    candidate: ti.types.ndarray(ti.f32, 3),
    offsets: ti.types.ndarray(ti.i32, 2),
    indices: ti.types.ndarray(ti.i32, 3),
    height: ti.i32,
    width: ti.i32,
    channels: ti.i32,
    candidate_count: ti.i32,
    neighbor_count: ti.i32,
    cell_size: ti.i32,
):
    """Rank aligned integer offsets by local 5x5 mean squared difference.

    One Taichi program owns each search cell. The bounded insertion keeps only
    requested best offsets, avoiding a candidate_count x H x W distance tensor.
    ``cell_size=1`` preserves pixelwise selection; larger values score only each
    cell center and return a coarse map for a later device expansion.
    """
    cells_y = (height + cell_size - 1) // cell_size
    cells_x = (width + cell_size - 1) // cell_size
    for cell_y, cell_x in ti.ndrange(cells_y, cells_x):
        y = ti.min(height - 1, cell_y * cell_size + cell_size // 2)
        x = ti.min(width - 1, cell_x * cell_size + cell_size // 2)
        best_distances = ti.Vector.zero(ti.f32, MAX_NEIGHBORS)
        best_indices = ti.Vector.zero(ti.i32, MAX_NEIGHBORS)
        for rank in ti.static(range(MAX_NEIGHBORS)):
            best_distances[rank] = _F32_MAX
            best_indices[rank] = -1

        if cell_size <= 1:
            target_valid = (
                y >= PATCH_RADIUS
                and y + PATCH_RADIUS < height
                and x >= PATCH_RADIUS
                and x + PATCH_RADIUS < width
            )
            if target_valid:
                for candidate_index in range(candidate_count):
                    dx = offsets[candidate_index, 0]
                    dy = offsets[candidate_index, 1]
                    source_valid = (
                        y + dy >= PATCH_RADIUS
                        and y + dy + PATCH_RADIUS < height
                        and x + dx >= PATCH_RADIUS
                        and x + dx + PATCH_RADIUS < width
                    )
                    if source_valid:
                        distance = 0.0
                        for py in ti.static(range(-PATCH_RADIUS, PATCH_RADIUS + 1)):
                            for px in ti.static(range(-PATCH_RADIUS, PATCH_RADIUS + 1)):
                                difference = 0.0
                                if channels == 1:
                                    difference = (
                                        reference[0, y + py, x + px]
                                        - candidate[0, y + dy + py, x + dx + px]
                                    )
                                else:
                                    reference_luma = (
                                        reference[0, y + py, x + px] * 0.299
                                        + reference[1, y + py, x + px] * 0.587
                                        + reference[2, y + py, x + px] * 0.114
                                    )
                                    candidate_luma = (
                                        candidate[0, y + dy + py, x + dx + px] * 0.299
                                        + candidate[1, y + dy + py, x + dx + px] * 0.587
                                        + candidate[2, y + dy + py, x + dx + px] * 0.114
                                    )
                                    difference = reference_luma - candidate_luma
                                distance += difference * difference
                        distance /= ti.cast(PATCH_AREA, ti.f32)

                        carry_distance = distance
                        carry_index = candidate_index
                        for rank in ti.static(range(MAX_NEIGHBORS)):
                            if rank < neighbor_count and carry_distance < best_distances[rank]:
                                displaced_distance = best_distances[rank]
                                displaced_index = best_indices[rank]
                                best_distances[rank] = carry_distance
                                best_indices[rank] = carry_index
                                carry_distance = displaced_distance
                                carry_index = displaced_index
        else:
            # Spatial cell aggregation (5-point cross subsample within the cell)
            # with center-pixel edge-preserving boost (weight 2.0 at center, 1.0
            # at the 4 quadrant anchors). Suppresses flat-field noise while
            # keeping sharp object boundaries coherent.
            step_y = ti.max(1, cell_size // 4)
            step_x = ti.max(1, cell_size // 4)
            for candidate_index in range(candidate_count):
                dx = offsets[candidate_index, 0]
                dy = offsets[candidate_index, 1]
                agg_distance = 0.0
                weight_sum = 0.0
                for sy, sx, w_sample in ti.static(
                    (
                        (0, 0, 2.0),
                        (-1, -1, 1.0),
                        (-1, 1, 1.0),
                        (1, -1, 1.0),
                        (1, 1, 1.0),
                    )
                ):
                    py_c = ti.min(
                        height - 1,
                        ti.max(0, y + sy * step_y),
                    )
                    px_c = ti.min(
                        width - 1,
                        ti.max(0, x + sx * step_x),
                    )
                    sample_valid = (
                        py_c >= PATCH_RADIUS
                        and py_c + PATCH_RADIUS < height
                        and px_c >= PATCH_RADIUS
                        and px_c + PATCH_RADIUS < width
                        and py_c + dy >= PATCH_RADIUS
                        and py_c + dy + PATCH_RADIUS < height
                        and px_c + dx >= PATCH_RADIUS
                        and px_c + dx + PATCH_RADIUS < width
                    )
                    if sample_valid:
                        patch_dist = 0.0
                        for py in ti.static(range(-PATCH_RADIUS, PATCH_RADIUS + 1)):
                            for px in ti.static(range(-PATCH_RADIUS, PATCH_RADIUS + 1)):
                                difference = 0.0
                                if channels == 1:
                                    difference = (
                                        reference[0, py_c + py, px_c + px]
                                        - candidate[0, py_c + dy + py, px_c + dx + px]
                                    )
                                else:
                                    reference_luma = (
                                        reference[0, py_c + py, px_c + px] * 0.299
                                        + reference[1, py_c + py, px_c + px] * 0.587
                                        + reference[2, py_c + py, px_c + px] * 0.114
                                    )
                                    candidate_luma = (
                                        candidate[0, py_c + dy + py, px_c + dx + px] * 0.299
                                        + candidate[1, py_c + dy + py, px_c + dx + px] * 0.587
                                        + candidate[2, py_c + dy + py, px_c + dx + px] * 0.114
                                    )
                                    difference = reference_luma - candidate_luma
                                patch_dist += difference * difference
                        patch_dist /= ti.cast(PATCH_AREA, ti.f32)
                        agg_distance += patch_dist * w_sample
                        weight_sum += w_sample

                if weight_sum > 0.0:
                    distance = agg_distance / weight_sum
                    carry_distance = distance
                    carry_index = candidate_index
                    for rank in ti.static(range(MAX_NEIGHBORS)):
                        if rank < neighbor_count and carry_distance < best_distances[rank]:
                            displaced_distance = best_distances[rank]
                            displaced_index = best_indices[rank]
                            best_distances[rank] = carry_distance
                            best_indices[rank] = carry_index
                            carry_distance = displaced_distance
                            carry_index = displaced_index

        for rank in ti.static(range(MAX_NEIGHBORS)):
            if rank < neighbor_count:
                indices[rank, cell_y, cell_x] = best_indices[rank]


@ti.func
def _sample_dense_flow(
    flow: ti.template(),
    x: ti.f32,
    y: ti.f32,
    flow_width: ti.i32,
    flow_height: ti.i32,
    channel: ti.i32,
):
    """Bilinear sample with zero-valued out-of-bounds taps (OpenCV remap contract)."""
    x0 = ti.cast(ti.floor(x), ti.i32)
    y0 = ti.cast(ti.floor(y), ti.i32)
    x1 = x0 + 1
    y1 = y0 + 1
    wx = x - ti.cast(x0, ti.f32)
    wy = y - ti.cast(y0, ti.f32)
    value = 0.0
    if 0 <= x0 and x0 < flow_width and 0 <= y0 and y0 < flow_height:
        value += flow[y0, x0, channel] * (1.0 - wx) * (1.0 - wy)
    if 0 <= x1 and x1 < flow_width and 0 <= y0 and y0 < flow_height:
        value += flow[y0, x1, channel] * wx * (1.0 - wy)
    if 0 <= x0 and x0 < flow_width and 0 <= y1 and y1 < flow_height:
        value += flow[y1, x0, channel] * (1.0 - wx) * wy
    if 0 <= x1 and x1 < flow_width and 0 <= y1 and y1 < flow_height:
        value += flow[y1, x1, channel] * wx * wy
    return value


@ti.kernel
def multi_patch_compose_dense_flow_kernel(
    rank_indices: ti.types.ndarray(),
    offsets: ti.types.ndarray(),
    base_flow: ti.types.ndarray(),
    output_flow: ti.types.ndarray(),
    index_height: ti.i32,
    index_width: ti.i32,
    flow_height: ti.i32,
    flow_width: ti.i32,
    full_height: ti.i32,
    full_width: ti.i32,
    candidate_count: ti.i32,
):
    """Compose a selected local offset with a resident dense alignment flow."""
    scale_x = ti.cast(flow_width, ti.f32) / ti.cast(full_width, ti.f32)
    scale_y = ti.cast(flow_height, ti.f32) / ti.cast(full_height, ti.f32)
    index_scale_x = ti.cast(index_width, ti.f32) / ti.cast(flow_width, ti.f32)
    index_scale_y = ti.cast(index_height, ti.f32) / ti.cast(flow_height, ti.f32)
    for y, x in ti.ndrange(flow_height, flow_width):
        index_y = ti.min(index_height - 1, ti.cast(ti.floor(y * index_scale_y), ti.i32))
        index_x = ti.min(index_width - 1, ti.cast(ti.floor(x * index_scale_x), ti.i32))
        selected = rank_indices[index_y, index_x]
        dx_flow = 0.0
        dy_flow = 0.0
        flow_x = 0.0
        flow_y = 0.0
        if 0 <= selected and selected < candidate_count:
            dx_flow = ti.cast(offsets[selected, 0], ti.f32) * scale_x
            dy_flow = ti.cast(offsets[selected, 1], ti.f32) * scale_y
        flow_x = _sample_dense_flow(
            base_flow, ti.cast(x, ti.f32) + dx_flow,
            ti.cast(y, ti.f32) + dy_flow, flow_width, flow_height, 0,
        ) + dx_flow
        flow_y = _sample_dense_flow(
            base_flow, ti.cast(x, ti.f32) + dx_flow,
            ti.cast(y, ti.f32) + dy_flow, flow_width, flow_height, 1,
        ) + dy_flow
        output_flow[y, x, 0] = flow_x
        output_flow[y, x, 1] = flow_y


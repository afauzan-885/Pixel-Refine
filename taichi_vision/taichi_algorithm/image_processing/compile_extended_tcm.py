"""Compile the remaining portable image-processing AOT graphs.

The original modules in ``image_processing`` and ``smoothing`` expose JIT
kernels with loose ndarray ABIs.  This compiler provides explicit f32/i32
contracts for the operations that still need a target-qualified native
artifact.  Host code remains responsible for small policy decisions such as
kernel preparation, channel iteration, and JPEG entropy/container assembly.
"""

import os
from pathlib import Path
from typing import Callable

os.environ.setdefault("AOT_MODE", "0")

import taichi as ti


def _nd(name: str, dtype, ndim: int):
    return ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, dtype, ndim=ndim)


def _scalar(name: str, dtype):
    return ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, dtype)


def _add_graph(module, name: str, kernel, *args) -> None:
    builder = ti.graph.GraphBuilder()
    builder.dispatch(kernel, *args)
    module.add_graph(name, builder.compile())


def _compile_one(arch, save_path: str, register: Callable) -> str:
    output = Path(save_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    ti.init(arch=arch, offline_cache=False)
    try:
        module = ti.aot.Module(arch)
        register(module)
        module.archive(str(output))
    finally:
        ti.reset()
    print(f"[OK] Archived {output}")
    return str(output)


@ti.func
def _reflect101(idx, size):
    value = ti.abs(idx)
    diff = value - (size - 1)
    value = value - 2 * ti.max(0, diff)
    return ti.max(0, ti.min(size - 1, value))


@ti.func
def _border_index(idx, size, mode):
    # mode: 1=replicate, 2=reflect, 3=wrap, 4=reflect101
    result = idx
    if mode == 1:
        result = ti.max(0, ti.min(size - 1, idx))
    elif mode == 2:
        period = ti.max(1, 2 * size)
        value = idx % period
        result = ti.select(value < size, value, period - 1 - value)
    elif mode == 3:
        result = idx % size
    else:
        period = ti.max(1, 2 * (size - 1))
        value = idx % period
        result = ti.select(value < size, value, period - value)
    return ti.max(0, ti.min(size - 1, result))


@ti.kernel
def _morph_dilate_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), structure: ti.types.ndarray(dtype=ti.i32, ndim=2), kh: ti.i32, kw: ti.i32, h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h, w):
        best = -1e30
        for ky in range(kh):
            if ky < kh:
                for kx in range(kw):
                    if kx < kw and structure[ky, kx] != 0:
                        sy = _reflect101(y + ky - kh // 2, h)
                        sx = _reflect101(x + kx - kw // 2, w)
                        best = ti.max(best, src[sy, sx])
        dst[y, x] = best


@ti.kernel
def _morph_erode_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), structure: ti.types.ndarray(dtype=ti.i32, ndim=2), kh: ti.i32, kw: ti.i32, h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h, w):
        best = 1e30
        for ky in range(kh):
            if ky < kh:
                for kx in range(kw):
                    if kx < kw and structure[ky, kx] != 0:
                        sy = _reflect101(y + ky - kh // 2, h)
                        sx = _reflect101(x + kx - kw // 2, w)
                        best = ti.min(best, src[sy, sx])
        dst[y, x] = best


@ti.kernel
def _morph_dilate_3d(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), structure: ti.types.ndarray(dtype=ti.i32, ndim=2), kh: ti.i32, kw: ti.i32, h: ti.i32, w: ti.i32, channels: ti.i32):
    for y, x, c in ti.ndrange(h, w, channels):
        best = -1e30
        for ky in range(kh):
            if ky < kh:
                for kx in range(kw):
                    if kx < kw and structure[ky, kx] != 0:
                        sy = _reflect101(y + ky - kh // 2, h)
                        sx = _reflect101(x + kx - kw // 2, w)
                        best = ti.max(best, src[sy, sx, c])
        dst[y, x, c] = best


@ti.kernel
def _morph_erode_3d(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), structure: ti.types.ndarray(dtype=ti.i32, ndim=2), kh: ti.i32, kw: ti.i32, h: ti.i32, w: ti.i32, channels: ti.i32):
    for y, x, c in ti.ndrange(h, w, channels):
        best = 1e30
        for ky in range(kh):
            if ky < kh:
                for kx in range(kw):
                    if kx < kw and structure[ky, kx] != 0:
                        sy = _reflect101(y + ky - kh // 2, h)
                        sx = _reflect101(x + kx - kw // 2, w)
                        best = ti.min(best, src[sy, sx, c])
        dst[y, x, c] = best


@ti.kernel
def _histogram_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), hist: ti.types.ndarray(dtype=ti.i32, ndim=1), h: ti.i32, w: ti.i32, bins: ti.i32, range_min: ti.f32, range_max: ti.f32):
    scale = ti.select(range_max > range_min, ti.cast(bins, ti.f32) / (range_max - range_min), 1.0)
    for y, x in ti.ndrange(h, w):
        index = ti.cast((src[y, x] - range_min) * scale, ti.i32)
        index = ti.max(0, ti.min(bins - 1, index))
        ti.atomic_add(hist[index], 1)


@ti.kernel
def _histogram_3d(src: ti.types.ndarray(dtype=ti.f32, ndim=3), hist: ti.types.ndarray(dtype=ti.i32, ndim=1), h: ti.i32, w: ti.i32, channels: ti.i32, bins: ti.i32, range_min: ti.f32, range_max: ti.f32):
    scale = ti.select(range_max > range_min, ti.cast(bins, ti.f32) / (range_max - range_min), 1.0)
    for y, x, c in ti.ndrange(h, w, channels):
        index = ti.cast((src[y, x, c] - range_min) * scale, ti.i32)
        index = ti.max(0, ti.min(bins - 1, index))
        ti.atomic_add(hist[index], 1)


@ti.kernel
def _ssim_2d(img1: ti.types.ndarray(dtype=ti.f32, ndim=2), img2: ti.types.ndarray(dtype=ti.f32, ndim=2), result: ti.types.ndarray(dtype=ti.f32, ndim=1), h: ti.i32, w: ti.i32, radius: ti.i32, c1: ti.f32, c2: ti.f32):
    total = 0.0
    count_total = 0
    for y, x in ti.ndrange(h, w):
        sum1 = 0.0
        sum2 = 0.0
        sum11 = 0.0
        sum22 = 0.0
        sum12 = 0.0
        count = 0
        for dy in range(21):
            if dy <= 2 * radius:
                for dx in range(21):
                    if dx <= 2 * radius:
                        sy = y + dy - radius
                        sx = x + dx - radius
                        if 0 <= sy < h and 0 <= sx < w:
                            a = img1[sy, sx]
                            b = img2[sy, sx]
                            sum1 += a
                            sum2 += b
                            sum11 += a * a
                            sum22 += b * b
                            sum12 += a * b
                            count += 1
        if count > 0:
            inv = 1.0 / ti.cast(count, ti.f32)
            mean1 = sum1 * inv
            mean2 = sum2 * inv
            var1 = ti.max(0.0, sum11 * inv - mean1 * mean1)
            var2 = ti.max(0.0, sum22 * inv - mean2 * mean2)
            cov = sum12 * inv - mean1 * mean2
            numerator = (2.0 * mean1 * mean2 + c1) * (2.0 * cov + c2)
            denominator = (mean1 * mean1 + mean2 * mean2 + c1) * (var1 + var2 + c2)
            total += numerator / ti.max(denominator, 1e-30)
            count_total += 1
    result[0] = total
    result[1] = ti.cast(count_total, ti.f32)


@ti.func
def _bilinear(src: ti.types.ndarray(dtype=ti.f32, ndim=2), x, y, h, w):
    ix = ti.cast(ti.floor(x), ti.i32)
    iy = ti.cast(ti.floor(y), ti.i32)
    fx = x - ti.cast(ix, ti.f32)
    fy = y - ti.cast(iy, ti.f32)
    x0 = _reflect101(ix, w)
    x1 = _reflect101(ix + 1, w)
    y0 = _reflect101(iy, h)
    y1 = _reflect101(iy + 1, h)
    top = src[y0, x0] * (1.0 - fx) + src[y0, x1] * fx
    bottom = src[y1, x0] * (1.0 - fx) + src[y1, x1] * fx
    return top * (1.0 - fy) + bottom * fy


@ti.func
def _bilinear3(src: ti.types.ndarray(dtype=ti.f32, ndim=3), x, y, h, w, c):
    ix = ti.cast(ti.floor(x), ti.i32)
    iy = ti.cast(ti.floor(y), ti.i32)
    fx = x - ti.cast(ix, ti.f32)
    fy = y - ti.cast(iy, ti.f32)
    x0 = _reflect101(ix, w)
    x1 = _reflect101(ix + 1, w)
    y0 = _reflect101(iy, h)
    y1 = _reflect101(iy + 1, h)
    top = src[y0, x0, c] * (1.0 - fx) + src[y0, x1, c] * fx
    bottom = src[y1, x0, c] * (1.0 - fx) + src[y1, x1, c] * fx
    return top * (1.0 - fy) + bottom * fy


@ti.kernel
def _warp_affine_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), matrix: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), h_src: ti.i32, w_src: ti.i32, h_dst: ti.i32, w_dst: ti.i32):
    for y, x in ti.ndrange(h_dst, w_dst):
        sx = matrix[0, 0] * ti.cast(x, ti.f32) + matrix[0, 1] * ti.cast(y, ti.f32) + matrix[0, 2]
        sy = matrix[1, 0] * ti.cast(x, ti.f32) + matrix[1, 1] * ti.cast(y, ti.f32) + matrix[1, 2]
        dst[y, x] = _bilinear(src, sx, sy, h_src, w_src)


@ti.kernel
def _warp_affine_3d(src: ti.types.ndarray(dtype=ti.f32, ndim=3), matrix: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h_src: ti.i32, w_src: ti.i32, h_dst: ti.i32, w_dst: ti.i32, channels: ti.i32):
    for y, x, c in ti.ndrange(h_dst, w_dst, channels):
        sx = matrix[0, 0] * ti.cast(x, ti.f32) + matrix[0, 1] * ti.cast(y, ti.f32) + matrix[0, 2]
        sy = matrix[1, 0] * ti.cast(x, ti.f32) + matrix[1, 1] * ti.cast(y, ti.f32) + matrix[1, 2]
        dst[y, x, c] = _bilinear3(src, sx, sy, h_src, w_src, c)


@ti.kernel
def _filter2d_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), kernel: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), kh: ti.i32, kw: ti.i32, h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h, w):
        value = 0.0
        for ky in range(kh):
            if ky < kh:
                for kx in range(kw):
                    if kx < kw:
                        sy = _reflect101(y + ky - kh // 2, h)
                        sx = _reflect101(x + kx - kw // 2, w)
                        value += src[sy, sx] * kernel[ky, kx]
        dst[y, x] = value


@ti.kernel
def _filter2d_3d(src: ti.types.ndarray(dtype=ti.f32, ndim=3), kernel: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), kh: ti.i32, kw: ti.i32, h: ti.i32, w: ti.i32, channels: ti.i32):
    for y, x, c in ti.ndrange(h, w, channels):
        value = 0.0
        for ky in range(kh):
            if ky < kh:
                for kx in range(kw):
                    if kx < kw:
                        sy = _reflect101(y + ky - kh // 2, h)
                        sx = _reflect101(x + kx - kw // 2, w)
                        value += src[sy, sx, c] * kernel[ky, kx]
        dst[y, x, c] = value


@ti.kernel
def _border_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), top: ti.i32, left: ti.i32, mode: ti.i32, constant: ti.f32):
    for y, x in ti.ndrange(dst.shape[0], dst.shape[1]):
        sy = y - top
        sx = x - left
        if mode == 0 and (sy < 0 or sy >= src.shape[0] or sx < 0 or sx >= src.shape[1]):
            dst[y, x] = constant
        else:
            dst[y, x] = src[_border_index(sy, src.shape[0], mode), _border_index(sx, src.shape[1], mode)]


@ti.kernel
def _border_3d(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), top: ti.i32, left: ti.i32, mode: ti.i32, constant: ti.f32, channels: ti.i32):
    for y, x, c in ti.ndrange(dst.shape[0], dst.shape[1], channels):
        sy = y - top
        sx = x - left
        if mode == 0 and (sy < 0 or sy >= src.shape[0] or sx < 0 or sx >= src.shape[1]):
            dst[y, x, c] = constant
        else:
            dst[y, x, c] = src[_border_index(sy, src.shape[0], mode), _border_index(sx, src.shape[1], mode), c]


@ti.kernel
def _border_3d_values(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), top: ti.i32, left: ti.i32, mode: ti.i32, constants: ti.types.ndarray(dtype=ti.f32, ndim=1), channels: ti.i32):
    for y, x, c in ti.ndrange(dst.shape[0], dst.shape[1], channels):
        sy = y - top
        sx = x - left
        if mode == 0 and (sy < 0 or sy >= src.shape[0] or sx < 0 or sx >= src.shape[1]):
            dst[y, x, c] = constants[c]
        else:
            dst[y, x, c] = src[_border_index(sy, src.shape[0], mode), _border_index(sx, src.shape[1], mode), c]


@ti.kernel
def _reduce_minmax(src: ti.types.ndarray(dtype=ti.f32, ndim=2), result: ti.types.ndarray(dtype=ti.f32, ndim=1), h: ti.i32, w: ti.i32):
    min_value = 1e30
    max_value = -1e30
    for y, x in ti.ndrange(h, w):
        value = src[y, x]
        min_value = ti.min(min_value, value)
        max_value = ti.max(max_value, value)
    result[0] = min_value
    result[1] = max_value


@ti.kernel
def _normalize_minmax(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), h: ti.i32, w: ti.i32, alpha: ti.f32, beta: ti.f32, src_min: ti.f32, src_max: ti.f32):
    denominator = ti.select(ti.abs(src_max - src_min) > 1e-10, src_max - src_min, 1.0)
    for y, x in ti.ndrange(h, w):
        dst[y, x] = (src[y, x] - src_min) / denominator * (beta - alpha) + alpha


@ti.kernel
def _reduce_norm(src: ti.types.ndarray(dtype=ti.f32, ndim=2), result: ti.types.ndarray(dtype=ti.f32, ndim=1), h: ti.i32, w: ti.i32, norm_type: ti.i32):
    accumulator = 0.0
    maximum = 0.0
    for y, x in ti.ndrange(h, w):
        value = ti.abs(src[y, x])
        if norm_type == 0:
            maximum = ti.max(maximum, value)
        elif norm_type == 1:
            accumulator += value
        else:
            accumulator += value * value
    result[0] = ti.select(norm_type == 0, maximum, ti.select(norm_type == 1, accumulator, ti.sqrt(accumulator)))


@ti.kernel
def _normalize_norm(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), h: ti.i32, w: ti.i32, alpha: ti.f32, norm_value: ti.f32):
    scale = ti.select(ti.abs(norm_value) > 1e-10, alpha / norm_value, 1.0)
    for y, x in ti.ndrange(h, w):
        dst[y, x] = src[y, x] * scale


@ti.kernel
def _threshold_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), h: ti.i32, w: ti.i32, threshold: ti.f32, max_value: ti.f32, mode: ti.i32):
    for y, x in ti.ndrange(h, w):
        value = src[y, x]
        if mode == 0:
            dst[y, x] = ti.select(value > threshold, max_value, 0.0)
        elif mode == 1:
            dst[y, x] = ti.select(value > threshold, 0.0, max_value)
        elif mode == 2:
            dst[y, x] = ti.min(value, threshold)
        elif mode == 3:
            dst[y, x] = ti.select(value > threshold, value, 0.0)
        else:
            dst[y, x] = ti.select(value > threshold, 0.0, value)


@ti.kernel
def _threshold_3d(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h: ti.i32, w: ti.i32, channels: ti.i32, threshold: ti.f32, max_value: ti.f32, mode: ti.i32):
    for y, x, c in ti.ndrange(h, w, channels):
        value = src[y, x, c]
        if mode == 0:
            dst[y, x, c] = ti.select(value > threshold, max_value, 0.0)
        elif mode == 1:
            dst[y, x, c] = ti.select(value > threshold, 0.0, max_value)
        elif mode == 2:
            dst[y, x, c] = ti.min(value, threshold)
        elif mode == 3:
            dst[y, x, c] = ti.select(value > threshold, value, 0.0)
        else:
            dst[y, x, c] = ti.select(value > threshold, 0.0, value)


@ti.kernel
def _gaussian_window(window: ti.types.ndarray(dtype=ti.f32, ndim=2), h: ti.i32, w: ti.i32, sigma: ti.f32):
    center_y = ti.cast(h, ti.f32) / 2.0
    center_x = ti.cast(w, ti.f32) / 2.0
    for y, x in ti.ndrange(h, w):
        dy = ti.cast(y, ti.f32) - center_y
        dx = ti.cast(x, ti.f32) - center_x
        window[y, x] = ti.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))


@ti.kernel
def _joint_bilateral_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), guide: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), h: ti.i32, w: ti.i32, radius: ti.i32, inv_space: ti.f32, inv_range: ti.f32):
    for y, x in ti.ndrange(h, w):
        total = 1e-12
        value = 0.0
        center = guide[y, x]
        for dy in ti.static(range(-3, 4)):
            if ti.abs(dy) <= radius:
                for dx in ti.static(range(-3, 4)):
                    if ti.abs(dx) <= radius:
                        sy = ti.max(0, ti.min(h - 1, y + dy))
                        sx = ti.max(0, ti.min(w - 1, x + dx))
                        delta = guide[sy, sx] - center
                        weight = ti.exp(-ti.cast(dx * dx + dy * dy, ti.f32) * inv_space - delta * delta * inv_range)
                        value += src[sy, sx] * weight
                        total += weight
        dst[y, x] = value / total


@ti.kernel
def _joint_bilateral_3d(src: ti.types.ndarray(dtype=ti.f32, ndim=3), guide: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h: ti.i32, w: ti.i32, channels: ti.i32, radius: ti.i32, inv_space: ti.f32, inv_range: ti.f32):
    for y, x, c in ti.ndrange(h, w, channels):
        total = 1e-12
        value = 0.0
        center = guide[y, x]
        for dy in ti.static(range(-3, 4)):
            if ti.abs(dy) <= radius:
                for dx in ti.static(range(-3, 4)):
                    if ti.abs(dx) <= radius:
                        sy = ti.max(0, ti.min(h - 1, y + dy))
                        sx = ti.max(0, ti.min(w - 1, x + dx))
                        delta = guide[sy, sx] - center
                        weight = ti.exp(-ti.cast(dx * dx + dy * dy, ti.f32) * inv_space - delta * delta * inv_range)
                        value += src[sy, sx, c] * weight
                        total += weight
        dst[y, x, c] = value / total


@ti.kernel
def _enhance_grayscale(src: ti.types.ndarray(dtype=ti.f32, ndim=2), blur: ti.types.ndarray(dtype=ti.f32, ndim=2), lut: ti.types.ndarray(dtype=ti.f32, ndim=1), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), h: ti.i32, w: ti.i32, micro_contrast: ti.f32, clarity: ti.f32, noise_coring: ti.f32):
    for y, x in ti.ndrange(h, w):
        value = src[y, x]
        difference = value - blur[y, x]
        magnitude = ti.abs(difference)
        attenuation = ti.select(magnitude < noise_coring, magnitude / ti.max(noise_coring, 1e-10), 1.0)
        shaped = difference * attenuation / (1.0 + magnitude * 5.0)
        midtone = 16.0 * value * value * (1.0 - value) * (1.0 - value)
        enhanced = value + shaped * micro_contrast + shaped * clarity * midtone
        index = ti.cast(ti.min(255.0, ti.max(0.0, enhanced * 255.0)), ti.i32)
        dst[y, x] = lut[index]


def _register_extended(module) -> None:
    f32, i32 = ti.f32, ti.i32
    structure = _nd("structure", i32, 2)
    for name, kernel in (("ext_morph_dilate_2d", _morph_dilate_2d), ("ext_morph_erode_2d", _morph_erode_2d)):
        _add_graph(module, name, kernel, _nd("src", f32, 2), _nd("dst", f32, 2), structure, _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32))
    for name, kernel in (("ext_morph_dilate_3d", _morph_dilate_3d), ("ext_morph_erode_3d", _morph_erode_3d)):
        _add_graph(module, name, kernel, _nd("src", f32, 3), _nd("dst", f32, 3), structure, _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32))

    _add_graph(module, "ext_histogram_2d", _histogram_2d, _nd("src", f32, 2), _nd("hist", i32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("bins", i32), _scalar("range_min", f32), _scalar("range_max", f32))
    _add_graph(module, "ext_histogram_3d", _histogram_3d, _nd("src", f32, 3), _nd("hist", i32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("bins", i32), _scalar("range_min", f32), _scalar("range_max", f32))
    _add_graph(module, "ext_ssim_2d", _ssim_2d, _nd("img1", f32, 2), _nd("img2", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("radius", i32), _scalar("c1", f32), _scalar("c2", f32))

    _add_graph(module, "ext_warp_affine_2d", _warp_affine_2d, _nd("src", f32, 2), _nd("matrix", f32, 2), _nd("dst", f32, 2), _scalar("h_src", i32), _scalar("w_src", i32), _scalar("h_dst", i32), _scalar("w_dst", i32))
    _add_graph(module, "ext_warp_affine_3d", _warp_affine_3d, _nd("src", f32, 3), _nd("matrix", f32, 2), _nd("dst", f32, 3), _scalar("h_src", i32), _scalar("w_src", i32), _scalar("h_dst", i32), _scalar("w_dst", i32), _scalar("channels", i32))
    _add_graph(module, "ext_filter2d_2d", _filter2d_2d, _nd("src", f32, 2), _nd("kernel", f32, 2), _nd("dst", f32, 2), _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32))
    _add_graph(module, "ext_filter2d_3d", _filter2d_3d, _nd("src", f32, 3), _nd("kernel", f32, 2), _nd("dst", f32, 3), _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32))
    _add_graph(module, "ext_border_2d", _border_2d, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("top", i32), _scalar("left", i32), _scalar("mode", i32), _scalar("constant", f32))
    _add_graph(module, "ext_border_3d", _border_3d, _nd("src", f32, 3), _nd("dst", f32, 3), _scalar("top", i32), _scalar("left", i32), _scalar("mode", i32), _scalar("constant", f32), _scalar("channels", i32))

    _add_graph(module, "ext_reduce_minmax_2d", _reduce_minmax, _nd("src", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32))
    _add_graph(module, "ext_normalize_minmax_2d", _normalize_minmax, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("alpha", f32), _scalar("beta", f32), _scalar("src_min", f32), _scalar("src_max", f32))
    _add_graph(module, "ext_reduce_norm_2d", _reduce_norm, _nd("src", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("norm_type", i32))
    _add_graph(module, "ext_normalize_norm_2d", _normalize_norm, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("alpha", f32), _scalar("norm_value", f32))
    _add_graph(module, "ext_threshold_2d", _threshold_2d, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("threshold", f32), _scalar("max_value", f32), _scalar("mode", i32))
    _add_graph(module, "ext_threshold_3d", _threshold_3d, _nd("src", f32, 3), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("threshold", f32), _scalar("max_value", f32), _scalar("mode", i32))
    _add_graph(module, "ext_gaussian_window_2d", _gaussian_window, _nd("window", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("sigma", f32))
    _add_graph(module, "ext_joint_bilateral_2d", _joint_bilateral_2d, _nd("src", f32, 2), _nd("guide", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("radius", i32), _scalar("inv_space", f32), _scalar("inv_range", f32))
    _add_graph(module, "ext_joint_bilateral_3d", _joint_bilateral_3d, _nd("src", f32, 3), _nd("guide", f32, 2), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("radius", i32), _scalar("inv_space", f32), _scalar("inv_range", f32))
    _add_graph(module, "ext_enhance_grayscale_2d", _enhance_grayscale, _nd("src", f32, 2), _nd("blur", f32, 2), _nd("lut", f32, 1), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("micro_contrast", f32), _scalar("clarity", f32), _scalar("noise_coring", f32))


def _register_extended_core(module) -> None:
    """Register reductions, transforms, borders, and scalar image ops."""

    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "ext_histogram_2d", _histogram_2d, _nd("src", f32, 2), _nd("hist", i32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("bins", i32), _scalar("range_min", f32), _scalar("range_max", f32))
    _add_graph(module, "ext_histogram_3d", _histogram_3d, _nd("src", f32, 3), _nd("hist", i32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("bins", i32), _scalar("range_min", f32), _scalar("range_max", f32))
    _add_graph(module, "ext_ssim_2d", _ssim_2d, _nd("img1", f32, 2), _nd("img2", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("radius", i32), _scalar("c1", f32), _scalar("c2", f32))
    _add_graph(module, "ext_warp_affine_2d", _warp_affine_2d, _nd("src", f32, 2), _nd("matrix", f32, 2), _nd("dst", f32, 2), _scalar("h_src", i32), _scalar("w_src", i32), _scalar("h_dst", i32), _scalar("w_dst", i32))
    _add_graph(module, "ext_warp_affine_3d", _warp_affine_3d, _nd("src", f32, 3), _nd("matrix", f32, 2), _nd("dst", f32, 3), _scalar("h_src", i32), _scalar("w_src", i32), _scalar("h_dst", i32), _scalar("w_dst", i32), _scalar("channels", i32))
    _add_graph(module, "ext_border_2d", _border_2d, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("top", i32), _scalar("left", i32), _scalar("mode", i32), _scalar("constant", f32))
    _add_graph(module, "ext_border_3d", _border_3d, _nd("src", f32, 3), _nd("dst", f32, 3), _scalar("top", i32), _scalar("left", i32), _scalar("mode", i32), _scalar("constant", f32), _scalar("channels", i32))
    _add_graph(module, "ext_reduce_minmax_2d", _reduce_minmax, _nd("src", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32))
    _add_graph(module, "ext_normalize_minmax_2d", _normalize_minmax, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("alpha", f32), _scalar("beta", f32), _scalar("src_min", f32), _scalar("src_max", f32))
    _add_graph(module, "ext_reduce_norm_2d", _reduce_norm, _nd("src", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("norm_type", i32))
    _add_graph(module, "ext_normalize_norm_2d", _normalize_norm, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("alpha", f32), _scalar("norm_value", f32))
    _add_graph(module, "ext_threshold_2d", _threshold_2d, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("threshold", f32), _scalar("max_value", f32), _scalar("mode", i32))
    _add_graph(module, "ext_threshold_3d", _threshold_3d, _nd("src", f32, 3), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("threshold", f32), _scalar("max_value", f32), _scalar("mode", i32))
    _add_graph(module, "ext_gaussian_window_2d", _gaussian_window, _nd("window", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("sigma", f32))


def _register_extended_heavy(module) -> None:
    """Register large static-window morphology and convolution graphs."""

    f32, i32 = ti.f32, ti.i32
    structure = _nd("structure", i32, 2)
    for name, kernel in (("ext_morph_dilate_2d", _morph_dilate_2d), ("ext_morph_erode_2d", _morph_erode_2d)):
        _add_graph(module, name, kernel, _nd("src", f32, 2), _nd("dst", f32, 2), structure, _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32))
    for name, kernel in (("ext_morph_dilate_3d", _morph_dilate_3d), ("ext_morph_erode_3d", _morph_erode_3d)):
        _add_graph(module, name, kernel, _nd("src", f32, 3), _nd("dst", f32, 3), structure, _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32))
    _add_graph(module, "ext_filter2d_2d", _filter2d_2d, _nd("src", f32, 2), _nd("kernel", f32, 2), _nd("dst", f32, 2), _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32))
    _add_graph(module, "ext_filter2d_3d", _filter2d_3d, _nd("src", f32, 3), _nd("kernel", f32, 2), _nd("dst", f32, 3), _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32))


def _register_extended_guidance(module) -> None:
    """Register edge-aware guidance and grayscale enhancement graphs."""

    f32, i32 = ti.f32, ti.i32
    _add_graph(module, "ext_joint_bilateral_2d", _joint_bilateral_2d, _nd("src", f32, 2), _nd("guide", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("radius", i32), _scalar("inv_space", f32), _scalar("inv_range", f32))
    _add_graph(module, "ext_joint_bilateral_3d", _joint_bilateral_3d, _nd("src", f32, 3), _nd("guide", f32, 2), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("radius", i32), _scalar("inv_space", f32), _scalar("inv_range", f32))
    _add_graph(module, "ext_enhance_grayscale_2d", _enhance_grayscale, _nd("src", f32, 2), _nd("blur", f32, 2), _nd("lut", f32, 1), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("micro_contrast", f32), _scalar("clarity", f32), _scalar("noise_coring", f32))


def _register_named(module, group: str) -> None:
    """Register one family so expensive static kernels compile independently."""

    f32, i32 = ti.f32, ti.i32
    if group == "morphology":
        structure = _nd("structure", i32, 2)
        for name, kernel in (("morphology_dilate_2d", _morph_dilate_2d), ("morphology_erode_2d", _morph_erode_2d)):
            _add_graph(module, name, kernel, _nd("src", f32, 2), _nd("dst", f32, 2), structure, _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32))
        for name, kernel in (("morphology_dilate_3d", _morph_dilate_3d), ("morphology_erode_3d", _morph_erode_3d)):
            _add_graph(module, name, kernel, _nd("src", f32, 3), _nd("dst", f32, 3), structure, _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32))
    elif group == "histogram":
        _add_graph(module, "histogram_2d", _histogram_2d, _nd("src", f32, 2), _nd("hist", i32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("bins", i32), _scalar("range_min", f32), _scalar("range_max", f32))
        _add_graph(module, "histogram_3d", _histogram_3d, _nd("src", f32, 3), _nd("hist", i32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("bins", i32), _scalar("range_min", f32), _scalar("range_max", f32))
    elif group == "ssim":
        _add_graph(module, "ssim_2d", _ssim_2d, _nd("img1", f32, 2), _nd("img2", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("radius", i32), _scalar("c1", f32), _scalar("c2", f32))
    elif group == "warp_affine":
        _add_graph(module, "warp_affine_2d", _warp_affine_2d, _nd("src", f32, 2), _nd("matrix", f32, 2), _nd("dst", f32, 2), _scalar("h_src", i32), _scalar("w_src", i32), _scalar("h_dst", i32), _scalar("w_dst", i32))
        _add_graph(module, "warp_affine_3d", _warp_affine_3d, _nd("src", f32, 3), _nd("matrix", f32, 2), _nd("dst", f32, 3), _scalar("h_src", i32), _scalar("w_src", i32), _scalar("h_dst", i32), _scalar("w_dst", i32), _scalar("channels", i32))
    elif group == "filter2d":
        _add_graph(module, "filter2d_2d", _filter2d_2d, _nd("src", f32, 2), _nd("kernel", f32, 2), _nd("dst", f32, 2), _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32))
        _add_graph(module, "filter2d_3d", _filter2d_3d, _nd("src", f32, 3), _nd("kernel", f32, 2), _nd("dst", f32, 3), _scalar("kh", i32), _scalar("kw", i32), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32))
    elif group == "border":
        _add_graph(module, "copy_make_border_2d", _border_2d, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("top", i32), _scalar("left", i32), _scalar("mode", i32), _scalar("constant", f32))
        _add_graph(module, "copy_make_border_3d", _border_3d, _nd("src", f32, 3), _nd("dst", f32, 3), _scalar("top", i32), _scalar("left", i32), _scalar("mode", i32), _scalar("constant", f32), _scalar("channels", i32))
        _add_graph(module, "copy_make_border_3d_values", _border_3d_values, _nd("src", f32, 3), _nd("dst", f32, 3), _scalar("top", i32), _scalar("left", i32), _scalar("mode", i32), _nd("constants", f32, 1), _scalar("channels", i32))
    elif group == "normalize":
        _add_graph(module, "normalize_reduce_minmax_2d", _reduce_minmax, _nd("src", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32))
        _add_graph(module, "normalize_minmax_2d", _normalize_minmax, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("alpha", f32), _scalar("beta", f32), _scalar("src_min", f32), _scalar("src_max", f32))
        _add_graph(module, "normalize_reduce_norm_2d", _reduce_norm, _nd("src", f32, 2), _nd("result", f32, 1), _scalar("h", i32), _scalar("w", i32), _scalar("norm_type", i32))
        _add_graph(module, "normalize_norm_2d", _normalize_norm, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("alpha", f32), _scalar("norm_value", f32))
    elif group == "threshold":
        _add_graph(module, "threshold_2d", _threshold_2d, _nd("src", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("threshold", f32), _scalar("max_value", f32), _scalar("mode", i32))
        _add_graph(module, "threshold_3d", _threshold_3d, _nd("src", f32, 3), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("threshold", f32), _scalar("max_value", f32), _scalar("mode", i32))
    elif group == "gaussian_window":
        _add_graph(module, "gaussian_window_2d", _gaussian_window, _nd("window", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("sigma", f32))
    elif group == "guidance":
        _add_graph(module, "joint_bilateral_2d", _joint_bilateral_2d, _nd("src", f32, 2), _nd("guide", f32, 2), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("radius", i32), _scalar("inv_space", f32), _scalar("inv_range", f32))
        _add_graph(module, "joint_bilateral_3d", _joint_bilateral_3d, _nd("src", f32, 3), _nd("guide", f32, 2), _nd("dst", f32, 3), _scalar("h", i32), _scalar("w", i32), _scalar("channels", i32), _scalar("radius", i32), _scalar("inv_space", f32), _scalar("inv_range", f32))
    elif group == "enhance":
        _add_graph(module, "enhance_grayscale_2d", _enhance_grayscale, _nd("src", f32, 2), _nd("blur", f32, 2), _nd("lut", f32, 1), _nd("dst", f32, 2), _scalar("h", i32), _scalar("w", i32), _scalar("micro_contrast", f32), _scalar("clarity", f32), _scalar("noise_coring", f32))
    else:
        raise ValueError(f"unknown extended image group: {group}")


def _compile_named(arch, save_path: str, group: str) -> str:
    return _compile_one(arch, save_path, lambda module: _register_named(module, group))


def compile_morphology_aot(arch=ti.cpu, save_path="morphology.tcm") -> str:
    return _compile_named(arch, save_path, "morphology")


def compile_histogram_aot(arch=ti.cpu, save_path="histogram.tcm") -> str:
    return _compile_named(arch, save_path, "histogram")


def compile_ssim_aot(arch=ti.cpu, save_path="ssim.tcm") -> str:
    return _compile_named(arch, save_path, "ssim")


def compile_warp_affine_aot(arch=ti.cpu, save_path="warp_affine.tcm") -> str:
    return _compile_named(arch, save_path, "warp_affine")


def compile_filter2d_aot(arch=ti.cpu, save_path="filter2d.tcm") -> str:
    return _compile_named(arch, save_path, "filter2d")


def compile_border_aot(arch=ti.cpu, save_path="border.tcm") -> str:
    return _compile_named(arch, save_path, "border")


def compile_normalize_aot(arch=ti.cpu, save_path="normalize.tcm") -> str:
    return _compile_named(arch, save_path, "normalize")


def compile_threshold_aot(arch=ti.cpu, save_path="threshold.tcm") -> str:
    return _compile_named(arch, save_path, "threshold")


def compile_gaussian_window_aot(arch=ti.cpu, save_path="gaussian_window.tcm") -> str:
    return _compile_named(arch, save_path, "gaussian_window")


def compile_guidance_aot(arch=ti.cpu, save_path="guidance.tcm") -> str:
    return _compile_named(arch, save_path, "guidance")


def compile_enhance_aot(arch=ti.cpu, save_path="enhance.tcm") -> str:
    return _compile_named(arch, save_path, "enhance")


def compile_extended_aot(arch=ti.cpu, save_path="extended_image.tcm") -> str:
    return _compile_one(arch, save_path, _register_extended)


def compile_image_core_aot(arch=ti.cpu, save_path="image_core.tcm") -> str:
    return _compile_one(arch, save_path, _register_extended_core)


def compile_image_heavy_aot(arch=ti.cpu, save_path="image_heavy.tcm") -> str:
    return _compile_one(arch, save_path, _register_extended_heavy)


def compile_image_guidance_aot(arch=ti.cpu, save_path="image_guidance.tcm") -> str:
    return _compile_one(arch, save_path, _register_extended_guidance)


__all__ = [
    "compile_extended_aot", "compile_image_core_aot", "compile_image_heavy_aot", "compile_image_guidance_aot",
    "compile_morphology_aot", "compile_histogram_aot", "compile_ssim_aot", "compile_warp_affine_aot",
    "compile_filter2d_aot", "compile_border_aot", "compile_normalize_aot", "compile_threshold_aot",
    "compile_gaussian_window_aot", "compile_guidance_aot", "compile_enhance_aot",
]


if __name__ == "__main__":
    compile_extended_aot()

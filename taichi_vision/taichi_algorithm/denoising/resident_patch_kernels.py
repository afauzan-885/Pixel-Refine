"""Device-only patch preparation, confidence stitching and candidate geometry."""
import taichi as ti
from .multi_patch_kernels import _sample_dense_flow
from .multi_patch_kernels import multi_patch_topk_kernel


@ti.kernel
def proxy(gray: ti.types.ndarray(ti.f32, 2), output: ti.types.ndarray(ti.f32, 1), width: ti.i32):
    for y, x in gray:
        output[y * width + x] = gray[y, x]


@ti.kernel
def extract(reference: ti.types.ndarray(ti.f32, 1), support: ti.types.ndarray(ti.f32, 1),
            ref_tile: ti.types.ndarray(ti.f32, 1), support_tile: ti.types.ndarray(ti.f32, 1),
            height: ti.i32, width: ti.i32, size: ti.i32, y0: ti.i32, x0: ti.i32):
    for i in ref_tile:
        y, x = i // size + y0, i % size + x0
        r, s = 0.0, 0.0
        if y < height and x < width:
            r, s = reference[y * width + x], support[y * width + x]
        ref_tile[i], support_tile[i] = r, s


@ti.kernel
def clear(numerator: ti.types.ndarray(ti.f32, 2), denominator: ti.types.ndarray(ti.f32, 2),
          alpha: ti.types.ndarray(ti.f32, 1)):
    for y, x in numerator:
        numerator[y, x], denominator[y, x] = 0.0, 0.0
    alpha[0] = 0.0


@ti.kernel
def stitch(weight: ti.types.ndarray(ti.f32, 1), window: ti.types.ndarray(ti.f32, 1),
           numerator: ti.types.ndarray(ti.f32, 2), denominator: ti.types.ndarray(ti.f32, 2),
           alpha: ti.types.ndarray(ti.f32, 1), alpha_sum: ti.types.ndarray(ti.f32, 1),
           size: ti.i32, cur_h: ti.i32, cur_w: ti.i32, y0: ti.i32, x0: ti.i32):
    for y, x in ti.ndrange(cur_h, cur_w):
        value = window[y * size + x]
        numerator[y0 + y, x0 + x] += weight[y * size + x] * value
        denominator[y0 + y, x0 + x] += value
    alpha_sum[0] += alpha[0]


@ti.kernel
def confidence(numerator: ti.types.ndarray(ti.f32, 2), denominator: ti.types.ndarray(ti.f32, 2),
               output: ti.types.ndarray(ti.f32, 2), indices: ti.types.ndarray(ti.i32, 3),
               rank: ti.i32, penalty: ti.f32, cutoff: ti.f32):
    for y, x in output:
        value = ti.min(1.0, ti.max(0.0, numerator[y, x] / (denominator[y, x] + 1e-8)))
        if penalty != 1.0:
            value = ti.pow(value, penalty)
        if cutoff > 0.0:
            value = ti.min(1.0, ti.max(0.0, (value - cutoff) / (1.0 - cutoff)))
        if rank >= 0:
            if indices[rank, y, x] < 0:
                value = 0.0
        output[y, x] = value


@ti.kernel
def scalar(a: ti.types.ndarray(ti.f32, 1), b: ti.types.ndarray(ti.f32, 1),
           output: ti.types.ndarray(ti.f32, 1), ca: ti.f32, cb: ti.f32, bias: ti.f32):
    output[0] = a[0] * ca + b[0] * cb + bias


@ti.kernel
def scale(image: ti.types.ndarray(ti.f32, 2), output: ti.types.ndarray(ti.f32, 2), factor: ti.f32):
    for y, x in image:
        output[y, x] = image[y, x] * factor


@ti.kernel
def coherent(indices: ti.types.ndarray(ti.i32, 3), output: ti.types.ndarray(ti.i32, 3),
             height: ti.i32, width: ti.i32, border_y: ti.i32, border_x: ti.i32):
    for rank, y, x in output:
        cy, cx = ti.min(height - 1, y // 10 * 10 + 5), ti.min(width - 1, x // 10 * 10 + 5)
        selected = indices[rank, cy, cx]
        if y < border_y or y >= height - border_y or x < border_x or x >= width - border_x:
            selected = -1
        output[rank, y, x] = selected


@ti.kernel
def coherent_cells(indices: ti.types.ndarray(ti.i32, 3), output: ti.types.ndarray(ti.i32, 3),
                   height: ti.i32, width: ti.i32, cell_size: ti.i32,
                   border_y: ti.i32, border_x: ti.i32):
    for rank, y, x in output:
        cy, cx = ti.min(indices.shape[1] - 1, y // cell_size), ti.min(indices.shape[2] - 1, x // cell_size)
        selected = indices[rank, cy, cx]
        if y < border_y or y >= height - border_y or x < border_x or x >= width - border_x:
            selected = -1
        output[rank, y, x] = selected


@ti.kernel
def gather(source: ti.types.ndarray(ti.f32, 1), indices: ti.types.ndarray(ti.i32, 3),
           offsets: ti.types.ndarray(ti.i32, 2), output: ti.types.ndarray(ti.f32, 1),
           height: ti.i32, width: ti.i32, rank: ti.i32):
    for i in output:
        y, x = i // width, i % width
        selected = indices[rank, y, x]
        value = 0.0
        if selected >= 0:
            sy, sx = y + offsets[selected, 1], x + offsets[selected, 0]
            if 0 <= sy < height and 0 <= sx < width:
                value = source[sy * width + sx]
        output[i] = value


@ti.kernel
def flow(indices: ti.types.ndarray(ti.i32, 3), offsets: ti.types.ndarray(ti.i32, 2),
         base: ti.types.ndarray(ti.f32, 3), inverse: ti.types.ndarray(ti.f32, 1),
         output: ti.types.ndarray(ti.f32, 3), rank: ti.i32, mode: ti.i32,
         height: ti.i32, width: ti.i32, full_h: ti.i32, full_w: ti.i32):
    fh, fw = output.shape[0], output.shape[1]
    for y, x in ti.ndrange(fh, fw):
        iy, ix = ti.min(height - 1, y * height // fh), ti.min(width - 1, x * width // fw)
        selected = indices[rank, iy, ix]
        dx, dy = 0.0, 0.0
        if selected >= 0:
            dx, dy = ti.cast(offsets[selected, 0], ti.f32), ti.cast(offsets[selected, 1], ti.f32)
        fx, fy = dx * fw / full_w, dy * fh / full_h
        if mode == 1:
            fx += _sample_dense_flow(base, x + fx, y + fy, fw, fh, 0)
            fy += _sample_dense_flow(base, x + dx * fw / full_w, y + dy * fh / full_h, fw, fh, 1)
        elif mode == 2:
            tx, ty = x * ti.cast(full_w, ti.f32) / fw + dx, y * ti.cast(full_h, ti.f32) / fh + dy
            den = inverse[6] * tx + inverse[7] * ty + inverse[8]
            if ti.abs(den) < 1e-8:
                fx, fy = 1e20, 1e20
            else:
                fx = ((inverse[0] * tx + inverse[1] * ty + inverse[2]) / den) * fw / full_w - x
                fy = ((inverse[3] * tx + inverse[4] * ty + inverse[5]) / den) * fh / full_h - y
        output[y, x, 0], output[y, x, 1] = fx, fy


def register_graphs(module):
    from taichi.types.ndarray_type import NdarrayType
    for kernel in (proxy, extract, clear, stitch, confidence, scalar, scale,
                   coherent, coherent_cells, gather, flow, multi_patch_topk_kernel):
        args = []
        for arg in kernel._primal.arguments:
            annotation = arg.annotation
            args.append(
                ti.graph.Arg(ti.graph.ArgKind.NDARRAY, arg.name, annotation.dtype, ndim=annotation.ndim)
                if isinstance(annotation, NdarrayType)
                else ti.graph.Arg(ti.graph.ArgKind.SCALAR, arg.name, annotation)
            )
        graph = ti.graph.GraphBuilder()
        graph.dispatch(kernel, *args)
        module.add_graph(f"deno_resident_{kernel.__name__}_v1", graph.compile())

import numpy as np
import pyopencl as cl



ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

# Build program dan ambil kernel sekali saja
kernel_code = """
#pragma OPENCL EXTENSION cl_khr_fp64 : enable

int reflect(int x, int size) {
    while (x < 0 || x >= size) {
        if (x < 0) x = -x - 1;
        else x = 2 * size - x - 1;
    }
    return x;
}

__kernel void remap_bilinear(
    __global const float *src,
    __global const float *map_x,
    __global const float *map_y,
    __global float *dst,
    int width, int height, int src_stride, int dst_stride
) {
    int x = get_global_id(0);
    int y = get_global_id(1);

    if (x >= width || y >= height) return;

    int idx_out = y * dst_stride + x;
    float sx = map_x[y * width + x];
    float sy = map_y[y * width + x];

    int x0 = (int)floor(sx);
    int y0 = (int)floor(sy);
    int x1 = x0 + 1;
    int y1 = y0 + 1;

    float dx = sx - (float)x0;
    float dy = sy - (float)y0;

    int xr0 = reflect(x0, width);
    int yr0 = reflect(y0, height);
    int xr1 = reflect(x1, width);
    int yr1 = reflect(y1, height);

    float p00 = src[yr0 * src_stride + xr0];
    float p10 = src[yr0 * src_stride + xr1];
    float p01 = src[yr1 * src_stride + xr0];
    float p11 = src[yr1 * src_stride + xr1];

    float p0 = p00 * (1.0f - dx) + p10 * dx;
    float p1 = p01 * (1.0f - dx) + p11 * dx;
    float interpolated = p0 * (1.0f - dy) + p1 * dy;

    dst[idx_out] = interpolated;
}
"""

# Build program sekali
prg = cl.Program(ctx, kernel_code).build()
remap_kernel = cl.Kernel(prg, "remap_bilinear")  # <-- Ambil kernel sekali

def remap_gpu(base_image, map_x, map_y):
    """
    Melakukan operasi remap menggunakan OpenCL dengan kernel yang direuse.
    
    Args:
        base_image (np.ndarray): Citra input (H x W) atau (H x W x 3)
        map_x (np.ndarray): Peta koordinat X (float32)
        map_y (np.ndarray): Peta koordinat Y (float32)
        
    Returns:
        np.ndarray: Citra hasil remap
    """
    if base_image.ndim not in [2, 3]:
        raise ValueError("base_image harus berupa citra grayscale (2D) atau RGB/BGR (3D).")

    is_color = base_image.ndim == 3 and base_image.shape[2] in [3, 4]
    h, w = base_image.shape[:2]

    assert map_x.shape == (h, w), "Dimensi map_x tidak cocok"
    assert map_y.shape == (h, w), "Dimensi map_y tidak cocok"

    base = base_image.astype(np.float32)
    map_x = map_x.astype(np.float32)
    map_y = map_y.astype(np.float32)

    if is_color:
        c = base.shape[2]
        base_planar = np.stack([base[:, :, i] for i in range(c)], axis=0)
    else:
        base_planar = base[np.newaxis, ...]
        c = 1

    result_planar = np.empty_like(base_planar)

    mf = cl.mem_flags

    for ch in range(c):
        src_data = base_planar[ch]
        dest_data = result_planar[ch]

        src_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=src_data)
        map_x_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=map_x)
        map_y_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=map_y)
        dst_buf = cl.Buffer(ctx, mf.WRITE_ONLY, dest_data.nbytes)

        # Gunakan kernel yang sudah dibuat sebelumnya
        remap_kernel.set_arg(0, src_buf)
        remap_kernel.set_arg(1, map_x_buf)
        remap_kernel.set_arg(2, map_y_buf)
        remap_kernel.set_arg(3, dst_buf)
        remap_kernel.set_arg(4, np.int32(w))
        remap_kernel.set_arg(5, np.int32(h))
        remap_kernel.set_arg(6, np.int32(w))
        remap_kernel.set_arg(7, np.int32(w))

        # Jalankan kernel
        cl.enqueue_nd_range_kernel(queue, remap_kernel, (w, h), None)
        cl.enqueue_copy(queue, dest_data, dst_buf)

    if is_color:
        result = np.stack(result_planar, axis=2)
    else:
        result = result_planar[0]

    if base_image.dtype == np.uint8:
        result = np.clip(result, 0, 255).astype(np.uint8)
    else:
        result = result.astype(base_image.dtype)

    return result
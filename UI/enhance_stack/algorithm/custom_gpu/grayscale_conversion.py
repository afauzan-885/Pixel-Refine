import numpy as np
import pyopencl as cl

def bgr_to_gray_gpu(bgr_np):
    if bgr_np.ndim != 3 or bgr_np.shape[2] != 3:
        raise ValueError("Input harus berupa array BGR dengan 3 channel")

    h, w = bgr_np.shape[:2]

    # Setup OpenCL
    platform = cl.get_platforms()[0]
    device = platform.get_devices()[0]
    context = cl.Context([device])
    queue = cl.CommandQueue(context)

    mf = cl.mem_flags
    bgr_buf = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=bgr_np.astype(np.uint8))
    gray_np = np.empty((h, w), dtype=np.uint8)
    gray_buf = cl.Buffer(context, mf.WRITE_ONLY, gray_np.nbytes)

    kernel_code = """
    #define GID0 get_global_id(0)
    #define GID1 get_global_id(1)

    typedef uchar4 pixel;

    __kernel void bgr_to_gray(__global uchar *input,
                              __global uchar *output,
                              int width, int height) {
        int idx = GID1 * width + GID0;
        pixel p = ((const __global pixel *)input)[idx];

        float gray = 0.114f * p.z + 0.587f * p.y + 0.2989f * p.x;
        output[idx] = (uchar)(gray);
    }
    """

    program = cl.Program(context, kernel_code).build(options=["-cl-mad-enable", "-cl-fast-relaxed-math"])
    kernel = program.bgr_to_gray
    kernel.set_args(bgr_buf, gray_buf, np.int32(w), np.int32(h))

    # Gunakan ukuran workgroup yang valid
    local_size = (16, 16)  # Ukuran workgroup yang umum dan aman
    global_size = (
        ((w + local_size[0] - 1) // local_size[0]) * local_size[0],
        ((h + local_size[1] - 1) // local_size[1]) * local_size[1]
    )

    # Jalankan kernel dengan workgroup size valid
    cl.enqueue_nd_range_kernel(queue, kernel, global_size, local_size)
    cl.enqueue_copy(queue, gray_np, gray_buf)
    queue.finish()

    return gray_np
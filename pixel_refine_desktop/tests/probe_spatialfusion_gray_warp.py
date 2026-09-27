"""Numerical parity probe for SpatialFusion's grayscale-before-warp path.

Set PIXEL_REFINE_AOT_ARCH, then run as a module from the repository root.
"""

import numpy as np

from taichi_vision import taichi_aot as aot


def main():
    height, width = 64, 96
    rng = np.random.default_rng(7)
    source = aot.upload(rng.random((height, width, 3), dtype=np.float32))
    source_gray = aot.cvtColor(source, aot.COLOR_RGB2GRAY)
    flow_array = np.zeros((height, width, 2), dtype=np.float32)
    flow_array[:, :, 0] = 1.25
    flow_array[:, :, 1] = -0.75
    flow = aot.upload(flow_array, is_vector=False)
    homography = np.array(
        [[1.0, 0.0, 1.5], [0.0, 1.0, -0.75], [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )

    transforms = {
        "flow": lambda image: aot.remap_with_flow(
            image, flow, height, width, return_gpu=True
        ),
        "homography": lambda image: aot.warp_perspective(
            image, homography, (width, height), return_gpu=True
        ),
    }
    for name, warp in transforms.items():
        old_warp = warp(source)
        old_gray = aot.cvtColor(old_warp, aot.COLOR_RGB2GRAY)
        new_gray = warp(source_gray)
        difference = np.abs(old_gray.to_numpy() - new_gray.to_numpy())
        maximum = float(difference.max())
        print(
            f"backend={aot.get_engine().arch} operation={name} "
            f"shape=({height},{width},3) dtype=float32 max_abs={maximum:.9g}"
        )
        assert maximum < 1.0e-5
        aot.get_engine().sync()
        for buffer in (old_warp, old_gray, new_gray):
            buffer.destroy()

    aot.get_engine().sync()
    for buffer in (source, source_gray, flow):
        buffer.destroy()


if __name__ == "__main__":
    main()

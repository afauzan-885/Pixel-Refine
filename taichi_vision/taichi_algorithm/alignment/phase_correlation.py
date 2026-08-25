"""
Global Motion Estimation (Phase Correlation) - Taichi GPU Implementation
========================================================================
Provides an extremely fast global shift estimator using frequency-domain
Phase Correlation. Acts as a high-performance replacement for
OpenCV's CPU phaseCorrelate.
"""

import numpy as np

import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from ..taichi_worker import ti_thread
    from .. import common
    from ..pyramid import fft
except ImportError:
    pass


if TAICHI_AVAILABLE:

    @ti.kernel
    def _phase_normalize_kernel(R: ti.types.ndarray(), mag: ti.types.ndarray()):
        for I in ti.grouped(R):
            m = mag[I]
            if m > 1e-12:
                R[I] /= m

    @ti_thread
    def phase_correlate_fft(ref, comp):
        """
        Frequency-domain Phase Correlation for sub-pixel shift estimation.
        formula: Cross-power spectrum R = (F * G*) / |F * G*|
        shift = argmax(IFFT(R))
        """
        # 1. FFT (using core FFT functions)
        F = fft.fft2(ref)
        G = fft.fft2(comp)

        h, w = F.shape
        R = common.get_temp_buffer((h, w), ti.types.vector(2, ti.f32))

        # 2. Cross-power spectrum: G * F* (gives shift ref -> comp)
        # Using kernels from fft module
        fft._complex_mul_kernel(G, F, R, conj_b=1)

        # 3. Normalize magnitude to 1.0 (Phase Correlation)
        mag = common.get_temp_buffer((h, w), ti.f32)
        fft._complex_to_mag_kernel(R, mag)

        _phase_normalize_kernel(R, mag)
        common.release_temp_buffer(mag)

        # 4. Inverse FFT
        corr_gpu = fft.ifft2(R)
        corr_np = corr_gpu.to_numpy()

        # Find peak
        idx = np.unravel_index(np.argmax(corr_np), corr_np.shape)
        dy, dx = idx[0], idx[1]
        peak_val = corr_np[idx]

        # Cleanup
        common.release_temp_buffer(F)
        common.release_temp_buffer(G)
        common.release_temp_buffer(R)
        common.release_temp_buffer(corr_gpu)

        # Shift wrapping (standard FFT behavior)
        if dy > h // 2:
            dy -= h
        if dx > w // 2:
            dx -= w

        return float(dx), float(dy), float(peak_val)


def phase_correlation(
    ref_layer: np.ndarray, comp_layer: np.ndarray, max_shift: int = 16
):
    """
    Estimates the dominant global translation (dx, dy) between two 2D images
    using frequency-domain Phase Correlation.

    Returns:
        (dx, dy, response)
        where response is the correlation peak value [0.0, 1.0].
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.phase_correlation(ref_layer, comp_layer)

    if not TAICHI_AVAILABLE:
        raise RuntimeError("Taichi is not available")

    # Call GPU implementation
    return phase_correlate_fft(ref_layer, comp_layer)

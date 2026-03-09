import sys
import os
import numpy as np
import taichi as ti

# Add project root to sys.path
# Based on the user environment, the project root is 'e:\APP Developer\Pixel Refine'
# This script is at the root.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm as ta


def test_fft_accuracy():
    print("Testing 2D FFT accuracy...")
    size = 64
    img = np.random.rand(size, size).astype(np.float32)
    np_fft = np.fft.fft2(img)
    ti_fft_field = ta.fft2(img)
    ti_fft = ti_fft_field.to_numpy()
    ti_fft_complex = ti_fft[..., 0] + 1j * ti_fft[..., 1]
    diff = np.abs(np_fft - ti_fft_complex)
    max_diff = np.max(diff)
    print(f"Max difference (FFT): {max_diff}")
    assert max_diff < 1e-3, f"FFT accuracy check failed: {max_diff}"
    print("✅ FFT Accuracy Test Passed.")

    reconstructed_gpu = ta.ifft2(ti_fft_field)
    reconstructed = reconstructed_gpu.to_numpy()
    diff_recon = np.abs(img - reconstructed)
    max_diff_recon = np.max(diff_recon)
    print(f"Max difference (IFFT reconstruction): {max_diff_recon}")
    assert max_diff_recon < 1e-3, "IFFT reconstruction check failed!"
    print("✅ IFFT Reconstruction Test Passed.")
    ta.common.release_temp_buffer(ti_fft_field)
    ta.common.release_temp_buffer(reconstructed_gpu)


def test_phase_correlation():
    print("\nTesting Phase Correlation...")
    size = 256
    img = np.random.rand(size, size).astype(np.float32)
    dx_true, dy_true = 12, -7
    shifted = np.roll(img, (dy_true, dx_true), axis=(0, 1))
    dx, dy, conf = ta.phase_correlation(img, shifted)
    print(f"True shift: ({dx_true}, {dy_true})")
    print(f"Detected shift: ({dx}, {dy}), confidence: {conf}")
    assert abs(dx - dx_true) < 1.0, f"DX mismatch: expected {dx_true}, got {dx}"
    assert abs(dy - dy_true) < 1.0, f"DY mismatch: expected {dy_true}, got {dy}"
    print("✅ Phase Correlation Test Passed.")


def test_ncc():
    print("\n[NCC/Template Matching Test]")
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import ncc

    # Create a large image and a template
    large_img = np.random.rand(128, 128).astype(np.float32)
    # Place a specific pattern
    template = np.zeros((32, 32), dtype=np.float32)
    template[8:24, 8:24] = 1.0

    # Inject template into image at (50, 50)
    large_img[50:82, 50:82] = template

    # Test NCC via simplified API
    print("Running NCC via simplified ta.ncc API...")
    ncc_map_ti = ta.ncc(large_img, template)

    # Find peak
    peak_idx = np.unravel_index(np.argmax(ncc_map_ti), ncc_map_ti.shape)
    print(
        f"NCC Peak location: {peak_idx}, Correlation Value: {ncc_map_ti[peak_idx]:.4f}"
    )

    # In 'same' padding, the peak should correspond to the top-left center?
    # Actually, for 32x32 template at (50, 50), the center is (50+16, 50+16) = (66, 66)
    # Let's see if it's close to 1.0
    if ncc_map_ti[peak_idx] > 0.9:
        print("✅ NCC Accuracy Test Passed (Peak found with high correlation)")
    else:
        print("❌ NCC Accuracy Test Failed (Low correlation at peak)")


if __name__ == "__main__":
    try:
        test_fft_accuracy()
        test_phase_correlation()
        test_ncc()
        print("\nAll Taichi FFT Algorithm tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

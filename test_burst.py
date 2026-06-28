"""
test_burst.py - Burst Capture & Exposure Bracketing Test
========================================================
Test burst capture dan exposure bracketing.

Usage:
    python test_burst.py
"""

import sys
import os
import time
import numpy as np

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from taichi_library.taichi_algorithm.camera_api2.burst_capture import BurstCapture, quick_burst
from taichi_library.taichi_algorithm.camera_api2.exposure_bracket import ExposureBracket, create_bracket_sequence
from taichi_library.taichi_algorithm.camera_api2.post_capture_processor import PostCaptureProcessor, post_process_burst
from taichi_library.taichi_algorithm.camera_api2.frame_source import SyntheticSource, OpenCVSource


def test_burst_capture():
    """Test burst capture performance."""
    print("=" * 60)
    print("Test 1: Burst Capture")
    print("=" * 60)

    # Create source
    source = SyntheticSource(width=640, height=480, pattern="gradient")

    # Create capturer
    capturer = BurstCapture(source)

    # Capture 8 frames
    print("\nCapturing 8 frames...")
    start = time.perf_counter()
    frames = capturer.capture_burst(n_frames=8)
    elapsed = time.perf_counter() - start

    # Get stats
    stats = capturer.get_latency_stats()

    print(f"Frames captured: {stats['total_frames']}")
    print(f"Total time: {stats['total_ms']:.2f}ms")
    print(f"Avg per frame: {stats['avg_ms']:.2f}ms")
    print(f"Min per frame: {stats['min_ms']:.2f}ms")
    print(f"Max per frame: {stats['max_ms']:.2f}ms")
    print(f"Estimated FPS: {stats['estimated_fps']:.1f}")

    return frames


def test_exposure_bracket():
    """Test exposure bracketing."""
    print("\n" + "=" * 60)
    print("Test 2: Exposure Bracketing")
    print("=" * 60)

    # Create bracket controller
    bracket = ExposureBracket(
        iso_range=(100, 3200),
        exposure_range_ns=(100_000, 200_000_000),
    )

    # Generate bracket sequence
    print("\nGenerating bracket sequence (5 frames)...")
    sequence = bracket.generate_bracket(
        base_iso=200,
        base_exposure_ns=16_670_000,  # 1/60s
        ev_offsets=[-2.0, -1.0, 0.0, 1.0, 2.0],
    )

    print(f"\n{'EV':>6} | {'ISO':>6} | {'Exposure':>10} | {'Scale':>6} | {'Base':>4}")
    print("-" * 50)
    for setting in sequence:
        print(f"{setting.ev_offset:+6.1f} | {setting.iso:>6} | {setting.exposure_ms:>8.2f}ms | {setting.scale:>6.2f} | {'Yes' if setting.is_base else 'No':>4}")

    # Calculate EV spread
    ev_spread = bracket.calculate_ev_spread(base_iso=200, base_exposure_ns=16_670_000)
    print(f"\nDevice EV spread: {ev_spread:.1f} stops")

    # Get recommended bracket
    recommended = bracket.get_recommended_bracket()
    print(f"Recommended EV offsets: {recommended}")

    return sequence


def test_post_processing():
    """Test post-capture processing."""
    print("\n" + "=" * 60)
    print("Test 3: Post-Capture Processing")
    print("=" * 60)

    # Create source and capture frames
    source = SyntheticSource(width=640, height=480, pattern="gradient")
    capturer = BurstCapture(source)
    frames = capturer.capture_burst(n_frames=8)

    print(f"\nCaptured {len(frames)} frames")

    # Test 1: Simple average
    print("\n--- Simple Average ---")
    processor = PostCaptureProcessor(align=False, denoise=False)
    result = processor.process(frames)
    if result is not None:
        print(f"Result shape: {result.shape}")
        print(f"Result range: [{result.min():.3f}, {result.max():.3f}]")

    # Test 2: With denoising
    print("\n--- With Temporal Denoising ---")
    processor_denoise = PostCaptureProcessor(align=False, denoise=True)
    result_denoise = processor_denoise.process(frames)
    if result_denoise is not None:
        print(f"Result shape: {result_denoise.shape}")

    # Test 3: With alignment
    print("\n--- With MTB Alignment ---")
    processor_align = PostCaptureProcessor(align=True, denoise=True)
    result_align = processor_align.process(frames)
    if result_align is not None:
        print(f"Result shape: {result_align.shape}")

    return result


def test_quick_burst():
    """Test quick burst wrapper."""
    print("\n" + "=" * 60)
    print("Test 4: Quick Burst Wrapper")
    print("=" * 60)

    source = SyntheticSource(width=640, height=480, pattern="bars")

    print("\nQuick burst 5 frames...")
    frames, stats = quick_burst(source, n_frames=5)

    print(f"Frames: {stats['total_frames']}")
    print(f"Total time: {stats['total_ms']:.2f}ms")
    print(f"Estimated FPS: {stats['estimated_fps']:.1f}")


def main():
    """Main test function."""
    print("=" * 60)
    print("Burst Capture & Exposure Bracketing Test")
    print("=" * 60)

    # Run tests
    test_burst_capture()
    test_exposure_bracket()
    test_post_processing()
    test_quick_burst()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

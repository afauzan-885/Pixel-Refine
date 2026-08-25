from __future__ import annotations

import pytest

from taichi_vision.taichi_algorithm.aot_py.arm64_simulator import (
    simulate_arm64_block_plan,
)


def test_arm64_simulator_has_exact_coverage_and_never_native():
    report = simulate_arm64_block_plan(
        "cpu_arm64_linux", (513, 769, 3), dtype="f16", channels=3,
        total_bytes=8 * 1024**3, available_bytes=4 * 1024**3,
    )
    assert report.qualification == "simulated"
    assert report.native_runtime is False
    assert report.coverage_complete is True
    assert report.covered_pixels == 513 * 769
    assert report.block_count == report.block_rows * report.block_cols
    assert report.within_budget is True


def test_arm64_simulator_uses_shape_aware_dtype_memory_estimate():
    low = simulate_arm64_block_plan(
        "cpu_arm64_android", (4096, 4096), dtype="u8", channels=1,
        total_bytes=4 * 1024**3, available_bytes=2 * 1024**3,
    )
    high = simulate_arm64_block_plan(
        "cpu_arm64_android", (4096, 4096), dtype="f32", channels=4,
        total_bytes=4 * 1024**3, available_bytes=2 * 1024**3,
    )
    assert high.estimated_peak_bytes > low.estimated_peak_bytes


def test_arm64_simulator_rejects_non_arm_and_invalid_dtype():
    with pytest.raises(ValueError, match="ARM64"):
        simulate_arm64_block_plan("cpu_x86_64_linux", (256, 256))
    with pytest.raises(ValueError, match="unsupported simulation dtype"):
        simulate_arm64_block_plan("cpu_arm64_linux", (256, 256), dtype="bf16")


@pytest.mark.parametrize("dtype", ["u1", "uint8", "f2", "float16", "f4", "float32"])
def test_arm64_simulator_normalizes_numpy_style_dtype_aliases(dtype):
    report = simulate_arm64_block_plan(
        "cpu_arm64_linux", (257, 259), dtype=dtype, channels=1
    )
    assert report.dtype in {"u8", "f16", "f32"}
    assert report.coverage_complete is True


def test_arm64_simulator_validates_shape_channels_and_clamps_explicit_tile():
    with pytest.raises(ValueError, match="channel count"):
        simulate_arm64_block_plan("cpu_arm64_linux", (256, 256, 4), channels=3)
    with pytest.raises(ValueError, match="2 or 3 dimensions"):
        simulate_arm64_block_plan("cpu_arm64_linux", (256,))

    # 512 MiB available is emergency pressure; an explicit 2048 request must
    # not bypass the governor's 256 tile cap.
    report = simulate_arm64_block_plan(
        "cpu_arm64_linux", (1024, 1024, 1), dtype="u8", channels=1,
        total_bytes=8 * 1024**3, available_bytes=256 * 1024**2,
        block_size=2048,
    )
    assert report.pressure == "emergency"
    assert report.recommended_block_size == 256
    assert report.block_size == 256

"""Native RAW demosaic path: no rawpy container, path and bytes agree."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from taichi_vision import algorithm as taichi_aot
from taichi_vision.taichi_algorithm.compression import save_dng_aot


def test_native_demosaic_accepts_path_and_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIXEL_REFINE_BACKEND", "cpu")
    monkeypatch.setenv("PIXEL_REFINE_AOT_MODE", "1")
    rng = np.random.default_rng(42)
    mosaic = rng.integers(0, 1024, size=(32, 32), dtype=np.uint16)
    path = tmp_path / "native_demosaic.dng"
    save_dng_aot(
        mosaic,
        path,
        metadata={
            "cfa_pattern": (0, 1, 1, 2),
            "black_level": 0,
            "white_level": 1023,
            "orientation": 1,
        },
        compression="none",
        bits_per_sample=16,
    )

    from_path = np.asarray(taichi_aot.demosaic(path, method="bilinear"))
    from_bytes = np.asarray(taichi_aot.demosaic(path.read_bytes(), method="bilinear"))

    assert from_path.shape == (32, 32, 3)
    assert from_path.dtype == np.float32
    assert np.isfinite(from_path).all()
    np.testing.assert_allclose(from_path, from_bytes, rtol=1e-6, atol=1e-6)


def test_demosaic_rejects_rawpy_objects() -> None:
    class RawLike:
        raw_image = np.zeros((4, 4), dtype=np.uint16)

    with pytest.raises(TypeError, match="rawpy objects"):
        taichi_aot.demosaic(RawLike())

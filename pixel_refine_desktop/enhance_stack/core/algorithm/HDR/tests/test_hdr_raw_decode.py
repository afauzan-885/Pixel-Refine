"""HDR RAW decoding follows the GPU-resident MF-Denoising demosaic route."""

import numpy as np


def test_raw_decode_requests_resident_hamilton_and_releases_buffer(
    tmp_path, monkeypatch
):
    from taichi_vision import taichi_aot
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR.streaming_pipeline import (
        _load_rgb,
    )

    source = tmp_path / "capture.dng"
    source.write_bytes(b"fixture")
    expected = np.full((12, 16, 3), 0.42, dtype=np.float32)
    calls = {}

    class ResultBuffer:
        def to_numpy(self):
            return expected

        def destroy(self):
            calls["released"] = True

    def fake_demosaic(path, *, method, return_gpu):
        calls.update(path=path, method=method, return_gpu=return_gpu)
        return ResultBuffer()

    monkeypatch.setattr(taichi_aot, "demosaic", fake_demosaic)

    actual = _load_rgb(source)

    assert calls["method"] == "hamilton"
    assert calls["return_gpu"] is True
    assert calls["released"] is True
    np.testing.assert_array_equal(actual, expected)

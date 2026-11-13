"""HDR RAW decoding follows the GPU-resident MF-Denoising demosaic route."""

import numpy as np

def _resolve_output(source, dst=None):
    """True when the result should stay resident (device-owned)."""
    from taichi.aot_engine import is_resident

    if dst is not None and is_resident(dst):
        return True
    if isinstance(source, dict):
        return any(is_resident(value) for value in source.values())
    if isinstance(source, (list, tuple)):
        return any(is_resident(value) for value in source)
    return is_resident(source)




def test_raw_decode_requests_resident_hamilton_and_releases_buffer(
    tmp_path, monkeypatch
):
    from taichi_vision import algorithm as taichi_aot
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

    def fake_demosaic(path, *, method):
        _resident_output = _resolve_output(path)
        calls.update(path=path, method=method, _resident_output=_resident_output)
        return ResultBuffer()

    monkeypatch.setattr(taichi_aot, "demosaic", fake_demosaic)

    actual = _load_rgb(source)

    assert calls["method"] == "hamilton"
    assert calls["_resident_output"] is False
    assert calls["released"] is True
    np.testing.assert_array_equal(actual, expected)

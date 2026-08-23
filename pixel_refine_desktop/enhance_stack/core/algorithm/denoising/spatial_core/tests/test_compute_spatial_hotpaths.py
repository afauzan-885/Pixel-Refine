"""Regression tests for low-overhead spatial AOT dispatch helpers."""

import numpy as np
import zipfile

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
    SpatialScratchCache,
    _tcm_graph_available,
)


def test_optional_clear_graph_is_metadata_gated(tmp_path):
    old_artifact = tmp_path / "spatial_old.tcm"
    with zipfile.ZipFile(old_artifact, "w") as archive:
        archive.writestr("graphs.tcb", b"phase1_coarse_analysis")

    new_artifact = tmp_path / "spatial_new.tcm"
    with zipfile.ZipFile(new_artifact, "w") as archive:
        archive.writestr("graphs.tcb", b"phase1_coarse_analysis\0clear_f32_2d")

    assert _tcm_graph_available(old_artifact, "clear_f32_2d") is False
    assert _tcm_graph_available(new_artifact, "clear_f32_2d") is True


def test_invalid_spatial_artifact_fails_closed(tmp_path):
    artifact = tmp_path / "not_a_tcm.tcm"
    artifact.write_bytes(b"not a zip")

    assert _tcm_graph_available(artifact, "clear_f32_2d") is False


def test_same_path_tcm_replacement_invalidates_metadata_cache(tmp_path):
    """Replacing an artifact in place must re-read its graph index."""

    artifact = tmp_path / "spatial_replaced.tcm"
    with zipfile.ZipFile(artifact, "w") as archive:
        archive.writestr("graphs.tcb", b"phase1_coarse_analysis")
    assert _tcm_graph_available(artifact, "clear_f32_2d") is False

    with zipfile.ZipFile(artifact, "w") as archive:
        archive.writestr("graphs.tcb", b"phase1_coarse_analysis\0clear_f32_2d")
    assert _tcm_graph_available(artifact, "clear_f32_2d") is True


def test_spatial_scratch_cache_replaces_dtype_mismatch():
    class Buffer:
        def __init__(self, shape, dtype):
            self.shape = tuple(shape)
            self.dtype = dtype
            self.destroyed = False

        def destroy(self):
            self.destroyed = True

    class Engine:
        def __init__(self):
            self.created = []

        def allocate(self, shape, dtype, **_kwargs):
            buf = Buffer(shape, dtype)
            self.created.append(buf)
            return buf

    engine = Engine()
    cache = SpatialScratchCache()
    first = cache.acquire(engine, "gradient", (4, 4), dtype="float32")
    assert cache.acquire(engine, "gradient", (4, 4), dtype="float32") is first

    second = cache.acquire(engine, "gradient", (4, 4), dtype="float16")
    assert second is not first
    assert first.destroyed is True


def test_gaussian_blur_owned_float_conversion_releases_source_once(monkeypatch):
    """An implicit f32 conversion must not double-destroy its temporary source."""

    import taichi_vision.taichi_algorithm.aot_api as aot_api

    class Buffer:
        def __init__(self, value, *, dtype=None):
            array = np.asarray(value)
            self.shape = tuple(array.shape)
            self.dtype = np.dtype(dtype or array.dtype)
            self.is_vector = False
            self.vector_dim = 3
            self._array = np.asarray(array, dtype=self.dtype)
            self.destroy_count = 0
            self.release_count = 0

        def to_numpy(self):
            return np.array(self._array, copy=True)

        def destroy(self):
            self.destroy_count += 1

        def release(self):
            self.release_count += 1

    class Engine:
        arch = "cpu"

        def __init__(self):
            self.uploads = []

        def plan_blocks(self, *_args, **_kwargs):
            return None

        def upload(self, value, **_kwargs):
            buffer = Buffer(value)
            self.uploads.append(buffer)
            return buffer

        def allocate(self, shape, dtype=np.float32, **_kwargs):
            return Buffer(np.zeros(shape, dtype=dtype))

        def sync(self):
            return None

    class Module:
        def run(self, _graph, *, src, dst, **_kwargs):
            dst._array[...] = src._array

    engine = Engine()
    source = Buffer(np.ones((4, 4), dtype=np.float16))

    monkeypatch.setattr(aot_api, "engine", engine)
    monkeypatch.setattr(aot_api, "TaichiGPUBuffer", Buffer)
    monkeypatch.setattr(aot_api, "InputArray", lambda value, **_kwargs: Buffer(value))
    monkeypatch.setattr(
        aot_api,
        "OutputArray",
        lambda shape, dtype=np.float32, **_kwargs: Buffer(
            np.zeros(shape, dtype=dtype)
        ),
    )
    monkeypatch.setattr(aot_api, "_mod", lambda _name: Module())

    result = aot_api.gaussian_blur(source, sigma=1.0, kernel_size=3)

    assert result.shape == source.shape
    # The recursive f16 -> f32 conversion creates one owned temporary source.
    # It must be released exactly once after the synchronized graph completes.
    # The original caller-owned f16 source is never destroyed by the wrapper.
    assert source.destroy_count == 0
    assert len(engine.uploads) == 1
    assert engine.uploads[0].dtype == np.dtype(np.float32)
    assert engine.uploads[0].destroy_count == 1

"""Engine facade contract: the bridge-backed engine serving the algorithm layer.

The facade wraps the proven dispatch path (bit-exact vs legacy) and adds the
block-aware state surface the algorithm layer reads. Everything that binds the
native runtime runs in a subprocess, following the isolation rule the bridge
tests established.
"""

import os
import subprocess
import sys
import textwrap

import numpy as np
import pytest

import taichi as ti

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VERDICT_SCRIPT = textwrap.dedent(
    """
    import os
    os.environ["PIXEL_REFINE_AOT_DISABLE_CACHE"] = "1"
    import numpy as np
    import taichi.aot_engine as ae
    import taichi_vision.taichi_algorithm.aot_api as legacy

    engine = ae.get_engine(arch="vulkan")
    rng = np.random.default_rng(9)

    # Dispatch parity through the facade helpers.
    gray = rng.random((64, 96), dtype=np.float32)
    src = ae.InputArray(gray)
    dst = ae.OutputArray(gray.shape, gray.dtype)
    engine.load("box_filter").run(
        "box_filter_fused_3x3_1ch_f32",
        src=src, dst=dst, h=gray.shape[0], w=gray.shape[1],
    )
    engine.sync()
    print("BOX_EXACT", np.array_equal(dst.to_numpy(), legacy.box_filter(gray, kernel_size=3)))
    src.destroy(); dst.destroy()

    rgb = rng.random((48, 72, 3), dtype=np.float32)
    src = ae.InputArray(rgb).view_as_vector(True, vector_dim=3)
    dst = ae.OutputArray(rgb.shape[:2], rgb.dtype)
    engine.load("common").run("rgb2gray_f32", src=src, dst=dst)
    engine.sync()
    print("GRAY_EXACT", np.array_equal(dst.to_numpy(), legacy.rgb2gray(rgb)))
    src.destroy(); dst.destroy()

    # Buffer compatibility surface.
    buffer = ae.upload(np.arange(16, dtype=np.float32).reshape(4, 4))
    print("NDIM", buffer.ndim == 2)
    print("SIZE_BYTES", buffer.size_bytes == 64)
    clone = buffer.copy()
    print("COPY_EXACT", np.array_equal(clone.to_numpy(), buffer.to_numpy()))
    clone.destroy()
    staging = engine.acquire_staging_buffer((4, 4), np.float32)
    engine.release_staging_buffer(staging)
    print("STAGING_REUSE", engine.acquire_staging_buffer((4, 4), np.float32) is staging)
    engine.acquire_staging_buffer((4, 4), np.float32).destroy()
    print("GPU_NAME", engine.gpu_name)
    print("MEMORY_STATUS_KEYS", sorted(engine.get_memory_status().keys()))
    buffer.destroy()

    # Block-aware state surface.
    config = engine.get_block_config()
    print("BLOCK_ENABLED_FALSE", config.enabled is False)
    print("BLOCK_SIZE_512", config.size == 512)
    cache = engine.get_block_cache()
    record = ae.BlockRecord(
        block_id="probe", data=np.zeros(8, np.float32),
        checksum=ae.checksum(np.zeros(8, np.float32)), owner="op",
    )
    engine.put_block_record(record)
    print("PUT_PEEK", cache.peek("probe") is record)
    print("STATS_ENTRIES", engine.get_block_cache_stats()["entries"] == 1)
    print("QUARANTINE_OP", engine.quarantine_block_operation("op", "test") is not None)
    print("QUARANTINE_CLEAR", engine.clear_block_quarantine() is None)
    print("LAST_EXEC_EMPTY", engine.get_last_block_execution() == {})
    print("BATCH_SIZE", engine.recommend_block_batch_size((512, 512)) >= 1)
    # Disabled mode (default) plans no blocks, matching the legacy engine.
    print("PLAN_BLOCKS_DISABLED_NONE", engine.plan_blocks("demo", (1000, 2000), 0) is None)
    engine.configure_blocks(enabled=True, threshold_bytes=1)
    planned = engine.plan_blocks("demo", (1000, 2000), 80000)
    print("PLAN_BLOCKS_ENABLED_GRID", planned is not None and len(planned) > 0)
    print("CLEAR_PIPELINES", engine.clear_pipelines() == 0)
    print("RESERVATION", engine.configure_block_reservation("demo", soft_bytes=2048) is None)
    print("DONE")
    """
)


@pytest.fixture(scope="module")
def verdicts():
    env = dict(os.environ)
    env["PYTHONPATH"] = REPO_ROOT
    completed = subprocess.run(
        [sys.executable, "-c", VERDICT_SCRIPT],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=420,
    )
    assert completed.returncode == 0, completed.stderr[-2000:]
    values = {}
    for line in completed.stdout.splitlines():
        parts = line.split(" ", 1)
        if parts[0].isupper() and (len(parts) == 1 or len(parts) == 2):
            values[parts[0]] = parts[1] if len(parts) == 2 else ""
    assert "DONE" in values
    return values


def test_box_filter_dispatch_is_bit_exact(verdicts):
    assert verdicts["BOX_EXACT"] == "True"


def test_rgb2gray_dispatch_is_bit_exact(verdicts):
    assert verdicts["GRAY_EXACT"] == "True"


def test_buffer_compat_surface(verdicts):
    assert verdicts["NDIM"] == "True"
    assert verdicts["SIZE_BYTES"] == "True"
    assert verdicts["COPY_EXACT"] == "True"
    assert verdicts["STAGING_REUSE"] == "True"
    assert verdicts["GPU_NAME"] == "Intel(R) UHD Graphics 620"


def test_memory_status_reports_all_fields(verdicts):
    fields = verdicts["MEMORY_STATUS_KEYS"]
    for key in ("pressure", "resident_bytes", "live_bytes", "pooled_bytes", "staging_bytes"):
        assert key in fields, key


def test_block_state_surface(verdicts):
    assert verdicts["BLOCK_ENABLED_FALSE"] == "True"
    assert verdicts["BLOCK_SIZE_512"] == "True"
    assert verdicts["PUT_PEEK"] == "True"
    assert verdicts["STATS_ENTRIES"] == "True"
    assert verdicts["QUARANTINE_OP"] == "True"
    assert verdicts["QUARANTINE_CLEAR"] == "True"
    assert verdicts["LAST_EXEC_EMPTY"] == "True"
    assert verdicts["BATCH_SIZE"] == "True"
    assert verdicts["PLAN_BLOCKS_DISABLED_NONE"] == "True"
    assert verdicts["PLAN_BLOCKS_ENABLED_GRID"] == "True"
    assert verdicts["CLEAR_PIPELINES"] == "True"
    assert verdicts["RESERVATION"] == "True"


def test_facade_module_surface():
    from taichi import aot_engine

    for name in (
        "AOTEngine", "TaichiGPUBuffer", "InputArray", "OutputArray",
        "select_backend", "resolve_backend_config", "get_backend_config",
        "get_backend_name", "backend_info", "engine", "get_engine",
        "enable_experiment_mode", "is_experiment_mode", "upload", "copy_field",
        "unload_all_modules",
    ):
        assert hasattr(aot_engine, name), name
    for name in ("INTER_NEAREST", "INTER_LINEAR", "INTER_CUBIC", "INTER_AREA"):
        assert getattr(aot_engine, name) in (0, 1, 2, 3), name
    for name in ("COLOR_BGR2GRAY", "COLOR_RGB2GRAY", "COLOR_GRAY2BGR"):
        assert getattr(aot_engine, name) in (6, 7, 8), name
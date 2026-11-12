"""AOT graph dispatch parity: migrated bridge client vs the legacy runtime.

Each side runs in its own interpreter because both bind a process-global
native runtime. The migrated side goes through taichi.aot_dispatch (bridge
buffers, DynamicArg marshalling, run_graph); the legacy side goes through the
high-level aot_api. Outputs are compared bit-exactly.
"""

import os
import subprocess
import sys
import textwrap

import numpy as np
import pytest

import taichi as ti

pytestmark = pytest.mark.skipif(
    not ti._TESTS_HAVE_VULKAN, reason="no Vulkan device on this host"
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LEGACY_SCRIPT = textwrap.dedent(
    """
    import os
    os.environ["PIXEL_REFINE_AOT_DISABLE_CACHE"] = "1"
    import numpy as np
    import taichi_vision.taichi_algorithm.aot_api as legacy

    rng = np.random.default_rng(7)
    gray = rng.random((64, 96), dtype=np.float32)
    rgb = rng.random((48, 72, 3), dtype=np.float32)
    gray5 = rng.random((40, 60), dtype=np.float32)
    np.save(os.environ["OUT_GRAY3"], legacy.box_filter(gray, kernel_size=3))
    np.save(os.environ["OUT_RGB3"], legacy.box_filter(rgb, kernel_size=3))
    np.save(os.environ["OUT_GRAY5"], legacy.box_filter(gray5, kernel_size=5))
    np.save(os.environ["OUT_RGB2GRAY"], legacy.rgb2gray(rgb))
    np.save(os.environ["OUT_BGR2GRAY"], legacy.bgr2gray(rgb))
    print("LEGACY_DONE")
    """
)

MIGRATED_SCRIPT = textwrap.dedent(
    """
    import os
    os.environ["PIXEL_REFINE_AOT_DISABLE_CACHE"] = "1"
    import numpy as np
    import taichi as ti

    rng = np.random.default_rng(7)
    gray = rng.random((64, 96), dtype=np.float32)
    rgb = rng.random((48, 72, 3), dtype=np.float32)
    gray5 = rng.random((40, 60), dtype=np.float32)

    engine = ti.get_graph_engine(arch="vulkan")
    module = engine.load("box_filter")

    src = engine.upload(gray)
    dst = engine.allocate(gray.shape, gray.dtype)
    module.run(
        "box_filter_fused_3x3_1ch_f32",
        src=src, dst=dst, h=gray.shape[0], w=gray.shape[1],
    )
    engine.sync()
    np.save(os.environ["OUT_GRAY3"], dst.to_numpy())
    src.release(); dst.release()

    src = engine.upload(rgb).view_as_vector(True, vector_dim=3)
    dst = engine.allocate(rgb.shape, rgb.dtype).view_as_vector(True, vector_dim=3)
    module.run(
        "box_filter_fused_3x3_vec3_f32",
        src=src, dst=dst, h=rgb.shape[0], w=rgb.shape[1],
    )
    engine.sync()
    np.save(os.environ["OUT_RGB3"], dst.to_numpy())
    src.release(); dst.release()

    # The separable graph also exercises the scalar float argument path.
    src = engine.upload(gray5)
    tmp = engine.allocate(gray5.shape, gray5.dtype)
    dst = engine.allocate(gray5.shape, gray5.dtype)
    module.run(
        "box_filter_separable_generic_1ch_f32",
        src=src, tmp=tmp, dst=dst,
        h=gray5.shape[0], w=gray5.shape[1], radius=2.0,
    )
    engine.sync()
    np.save(os.environ["OUT_GRAY5"], dst.to_numpy())
    src.release(); tmp.release(); dst.release()

    # A second module proves dispatch parity is not box_filter specific.
    common = engine.load("common")
    src = engine.upload(rgb).view_as_vector(True, vector_dim=3)
    dst = engine.allocate(rgb.shape[:2], rgb.dtype)
    common.run("rgb2gray_f32", src=src, dst=dst)
    engine.sync()
    np.save(os.environ["OUT_RGB2GRAY"], dst.to_numpy())
    src.destroy(); dst.destroy()

    src = engine.upload(rgb).view_as_vector(True, vector_dim=3)
    dst = engine.allocate(rgb.shape[:2], rgb.dtype)
    common.run("bgr2gray_f32", src=src, dst=dst)
    engine.sync()
    np.save(os.environ["OUT_BGR2GRAY"], dst.to_numpy())
    src.destroy(); dst.destroy()
    print("MIGRATED_DONE")
    """
)


def _run(script, tmp_path, prefix):
    env = dict(os.environ)
    env["PYTHONPATH"] = REPO_ROOT
    outputs = {}
    for name in ("gray3", "rgb3", "gray5", "rgb2gray", "bgr2gray"):
        path = str(tmp_path / f"{prefix}_{name}.npy")
        outputs[name] = path
        env[f"OUT_{name.upper()}"] = path
    completed = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=420,
    )
    assert completed.returncode == 0, completed.stderr[-2000:]
    return outputs


@pytest.fixture(scope="module")
def parity(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("dispatch_parity")
    legacy_out = _run(LEGACY_SCRIPT, tmp_path, "legacy")
    migrated_out = _run(MIGRATED_SCRIPT, tmp_path, "migrated")
    return {
        name: (np.load(legacy_out[name]), np.load(migrated_out[name]))
        for name in ("gray3", "rgb3", "gray5", "rgb2gray", "bgr2gray")
    }


@pytest.mark.parametrize("case", ["gray3", "rgb3", "gray5", "rgb2gray", "bgr2gray"])
def test_graph_dispatch_is_bit_exact(parity, case):
    legacy_result, migrated_result = parity[case]
    assert migrated_result.shape == legacy_result.shape
    np.testing.assert_array_equal(migrated_result, legacy_result)
    assert float(np.max(np.abs(migrated_result - legacy_result))) == 0.0


def test_scalar_and_buffer_args_are_both_marshalled(parity):
    """The separable graph takes buffers plus a float radius argument."""
    legacy_result, migrated_result = parity["gray5"]
    assert migrated_result.shape == legacy_result.shape
    np.testing.assert_array_equal(migrated_result, legacy_result)
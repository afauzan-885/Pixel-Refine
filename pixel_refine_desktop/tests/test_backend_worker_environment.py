"""Worker retries must override canonical backend/device settings from the UI."""

import pytest

from taichi.backend_config import requested_backend
from pixel_refine_desktop.enhance_stack.core.logic import backend_worker_manager


@pytest.mark.parametrize(
    ("arch", "device_id"),
    [("cuda", 1), ("vulkan", 2), ("opengl", 0), ("cpu", 0)],
)
def test_worker_spawn_overrides_inherited_backend_and_device(monkeypatch, arch, device_id):
    for key, value in {
        "PIXEL_REFINE_AOT_ARCH": "cuda",
        "PIXEL_REFINE_AOT_DEVICE": "0",
        "PIXEL_REFINE_CUDA_DEVICE": "0",
        "AOT_ARCH": "cuda",
        "AOT_DEVICE": "0",
        "CUDA_DEVICE": "0",
        "CUDA_EXPECTED_NAME": "NVIDIA GeForce MX150",
    }.items():
        monkeypatch.setenv(key, value)

    captured = {}

    def capture_spawn(*args, **kwargs):
        captured.update(kwargs["env"])
        # Inspect the real launch boundary without creating threads or a GPU
        # process. The manager handles this as a failed process launch.
        raise OSError("test: process launch intentionally intercepted")

    monkeypatch.setattr(backend_worker_manager.subprocess, "Popen", capture_spawn)
    manager = backend_worker_manager.BackendWorkerManager()
    manager._active_backend_config = {
        "arch": arch,
        "device_id": device_id,
        "vendor": "cpu" if arch == "cpu" else "nvidia",
        "auto_fallback": True,
    }
    try:
        assert manager._spawn_worker_locked() is False
        assert requested_backend(environ=captured)[0] == arch
        assert captured["PIXEL_REFINE_AOT_ARCH"] == captured["AOT_ARCH"] == arch
        assert captured["PIXEL_REFINE_AOT_DEVICE"] == captured["AOT_DEVICE"] == str(device_id)
        if arch == "cuda":
            assert captured["PIXEL_REFINE_CUDA_DEVICE"] == captured["CUDA_DEVICE"] == str(device_id)
        else:
            assert not {"PIXEL_REFINE_CUDA_DEVICE", "CUDA_DEVICE", "CUDA_EXPECTED_NAME"} & captured.keys()
        assert captured["PIXEL_REFINE_AOT_ALLOW_CPU_FALLBACK"] == "0"
    finally:
        manager.shutdown()


def test_worker_engine_binding_uses_selected_backend_and_device(monkeypatch):
    monkeypatch.setenv("AOT_ARCH", "vulkan")
    monkeypatch.setenv("AOT_DEVICE", "1")
    monkeypatch.setenv("TARGET_VENDOR", "nvidia")

    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_process import (
        WorkerRunner,
    )
    import taichi.aot_engine as ta_aot
    from taichi_vision.taichi_algorithm import aot_api

    engine = WorkerRunner._initialize_engine()

    assert engine.arch == "vulkan"
    assert engine.device_id == 1
    assert ta_aot.engine._target is engine
    assert aot_api._module_loader.engine is engine

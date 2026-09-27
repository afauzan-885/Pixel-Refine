from types import SimpleNamespace
from unittest.mock import Mock


def test_batch_warmup_resolves_target_once_and_reuses_cache(tmp_path, monkeypatch):
    """Warm-up metadata is resolved once while the module cache stays reusable."""
    import taichi_vision.taichi_aot.aot_module_loader as module_loader

    module_cache = {}
    fake_engine = SimpleNamespace(
        arch="vulkan",
        gpu_name="test-device",
        _generation=7,
    )

    def load(path):
        module = SimpleNamespace(module_ptr=object(), engine_generation=7)
        fake_engine.loaded_paths.append(path)
        return module

    fake_engine.loaded_paths = []
    fake_engine.load = load
    target = SimpleNamespace(
        target_id="vulkan_x86_64_windows",
        is_arm=False,
        is_mobile=False,
    )
    detect_target = Mock(return_value=target)
    resolve_artifact = Mock()

    for name in ("bilinear_demosaice", "hamilton", "common"):
        (tmp_path / name).mkdir()

    monkeypatch.setattr(module_loader, "detect_target", detect_target)
    monkeypatch.setattr(module_loader, "resolve_artifact", resolve_artifact)
    monkeypatch.setenv("PIXEL_REFINE_AOT_TCM_ROOT", str(tmp_path))

    loader = module_loader.AOTModuleLoader(
        fake_engine,
        tcm_dir=str(tmp_path),
        cache=module_cache,
    )
    first = loader.warmup(("bilinear_demosaice", "hamilton", "common"))
    second = loader.warmup(("bilinear_demosaice", "hamilton", "common"))

    assert first["loaded_modules"] == 3
    assert first["deferred_modules"] == []
    assert second["loaded_modules"] == 3
    assert second["deferred_modules"] == []
    assert detect_target.call_count == 1
    assert resolve_artifact.call_count == 0
    assert len(fake_engine.loaded_paths) == 3


def test_batch_warmup_continues_after_one_module_failure(tmp_path, monkeypatch):
    """An optional artifact failure must not abort the remaining Pack 1 loads."""
    import taichi_vision.taichi_aot.aot_module_loader as module_loader

    fake_engine = SimpleNamespace(
        arch="vulkan",
        gpu_name="test-device",
        _generation=3,
        loaded_paths=[],
    )
    calls = {"count": 0}

    def load(path):
        calls["count"] += 1
        if calls["count"] == 2:
            raise RuntimeError("test artifact load failure")
        fake_engine.loaded_paths.append(path)
        return SimpleNamespace(module_ptr=object(), engine_generation=3)

    fake_engine.load = load
    target = SimpleNamespace(
        target_id="vulkan_x86_64_windows",
        is_arm=False,
        is_mobile=False,
    )

    for name in ("first", "broken", "last"):
        (tmp_path / name).mkdir()

    monkeypatch.setattr(module_loader, "detect_target", Mock(return_value=target))
    monkeypatch.setenv("PIXEL_REFINE_AOT_TCM_ROOT", str(tmp_path))

    result = module_loader.AOTModuleLoader(
        fake_engine,
        tcm_dir=str(tmp_path),
    ).warmup(("first", "broken", "last"))

    assert result["loaded_modules"] == 2
    assert [name for name, _ in result["deferred_modules"]] == ["broken"]
    assert len(fake_engine.loaded_paths) == 2


def test_local_generic_graphics_root_skips_slow_staging_probe(tmp_path, monkeypatch):
    """A local generic Vulkan target must not touch an optional staging disk."""
    import taichi_vision.taichi_aot.aot_module_loader as module_loader

    target_dir = tmp_path / "vulkan_x86_64_windows"
    target_dir.mkdir()
    (target_dir / "common_vulkan_x86_64_windows.tcm").write_bytes(b"tcm")
    fake_engine = SimpleNamespace(
        arch="vulkan",
        gpu_name="Intel(R) UHD Graphics 620",
        _generation=1,
    )
    target = SimpleNamespace(
        target_id="vulkan_x86_64_windows_intel",
        backend="vulkan",
        is_arm=False,
        is_mobile=False,
    )

    monkeypatch.delenv("PIXEL_REFINE_AOT_TCM_ROOT", raising=False)
    monkeypatch.setattr(module_loader, "detect_target", Mock(return_value=target))

    import taichi_vision.llvm20_runtime_paths as runtime_paths

    monkeypatch.setattr(
        runtime_paths,
        "tcm_root",
        Mock(side_effect=AssertionError("staging probe must be skipped")),
    )

    loader = module_loader.AOTModuleLoader(fake_engine, tcm_dir=str(tmp_path))
    resolved_target, active_root = loader.resolve_target()

    assert resolved_target is target
    assert active_root == str(tmp_path.resolve())

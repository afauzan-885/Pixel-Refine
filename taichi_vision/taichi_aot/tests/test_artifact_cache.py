import json
import os

from taichi_vision.taichi_aot import artifact_cache


def test_tcm_content_change_invalidates_quarantine_even_when_stat_is_unchanged(
    tmp_path, monkeypatch
):
    cache_dir = tmp_path / "status"
    artifact_path = tmp_path / "common_cuda.tcm"
    monkeypatch.setenv("PIXEL_REFINE_AOT_CACHE", str(cache_dir))
    monkeypatch.delenv("PIXEL_REFINE_AOT_DISABLE_CACHE", raising=False)
    artifact_path.write_bytes(b"old tcm")
    original_stat = artifact_path.stat()

    old_key = artifact_cache.artifact_key(artifact_path, "cuda", 0, "test-device")
    artifact_cache.set_status(old_key, "quarantined", error="stale load failure")

    artifact_path.write_bytes(b"new tcm")
    os.utime(
        artifact_path,
        ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns),
    )
    new_key = artifact_cache.artifact_key(artifact_path, "cuda", 0, "test-device")

    assert old_key != new_key
    assert artifact_cache.get_status(new_key) is None
    cache = json.loads((cache_dir / "artifact_status.json").read_text(encoding="utf-8"))
    assert old_key not in cache["_entries"]

    artifact_cache.set_status(new_key, "valid", artifact="common_cuda.tcm")
    assert artifact_cache.get_status(new_key)["status"] == "valid"


def test_materialized_cpu_tcm_content_change_prunes_previous_status(tmp_path, monkeypatch):
    cache_dir = tmp_path / "status"
    extraction_root = tmp_path / ".cpu_aot_cache"
    first = extraction_root / ("a" * 64)
    second = extraction_root / ("b" * 64)
    first.mkdir(parents=True)
    second.mkdir()
    (first / "__content__").write_text("cgraph:common", encoding="utf-8")
    (second / "__content__").write_text("cgraph:common", encoding="utf-8")
    (first / "kernel.ll").write_text("old kernel", encoding="utf-8")
    (second / "kernel.ll").write_text("new kernel", encoding="utf-8")
    monkeypatch.setenv("PIXEL_REFINE_AOT_CACHE", str(cache_dir))
    monkeypatch.delenv("PIXEL_REFINE_AOT_DISABLE_CACHE", raising=False)

    old_key = artifact_cache.artifact_key(first, "cpu", 0, "logical-device")
    artifact_cache.set_status(old_key, "quarantined", error="old payload")
    new_key = artifact_cache.artifact_key(second, "cpu", 0, "logical-device")

    assert old_key != new_key
    assert artifact_cache.get_status(new_key) is None
    cache = json.loads((cache_dir / "artifact_status.json").read_text(encoding="utf-8"))
    assert old_key not in cache["_entries"]


def test_legacy_status_cache_is_recreated_without_unfingerprinted_entries(
    tmp_path, monkeypatch
):
    cache_dir = tmp_path / "status"
    cache_dir.mkdir()
    cache_path = cache_dir / "artifact_status.json"
    cache_path.write_text(
        json.dumps({"legacy-status-key": {"status": "quarantined"}}),
        encoding="utf-8",
    )
    artifact_path = tmp_path / "bilinear_cuda.tcm"
    artifact_path.write_bytes(b"fresh tcm")
    monkeypatch.setenv("PIXEL_REFINE_AOT_CACHE", str(cache_dir))
    monkeypatch.delenv("PIXEL_REFINE_AOT_DISABLE_CACHE", raising=False)

    key = artifact_cache.artifact_key(artifact_path, "cuda", 0, "test-device")

    assert artifact_cache.get_status(key) is None
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache == {"_schema": 4, "_entries": {}}

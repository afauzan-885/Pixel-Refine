"""TCM format boundary: what the Rust runtime can and cannot read today.

Two artifacts share the .tcm extension:

* the Rust reader format parsed by taichi-aot (magic checked by read_module),
* the legacy bridge format, which is a zip archive produced by the C++ AOT
  pipeline and is what the desktop tree ships.

The inspection helper reports which one it found instead of failing with a
magic-byte error, so the remaining work is visible rather than surprising.
"""

import os

import pytest

from taichi import taichi_python as tp

TCM_ROOT = os.path.join(
    "taichi_vision", "taichi_algorithm", "aot_tcm"
)


def _first_tcm():
    if not os.path.isdir(TCM_ROOT):
        pytest.skip("no compiled TCM tree on this host")
    for root, _dirs, names in os.walk(TCM_ROOT):
        for name in names:
            if name.endswith(".tcm"):
                return os.path.join(root, name)
    pytest.skip("no .tcm artifact on this host")


def test_legacy_artifact_is_reported_as_zip_archive():
    path = _first_tcm()
    info = tp.inspect_tcm(path)
    assert info["format"] == "zip-archive"
    assert info["rust_readable"] is False
    assert info["size_bytes"] == os.path.getsize(path)
    # No kernel data may be invented for a format the reader cannot parse.
    assert info["kernel_count"] == 0
    assert info["field_count"] == 0


def test_inspection_reports_size_for_every_artifact():
    path = _first_tcm()
    info = tp.inspect_tcm(path)
    assert info["size_bytes"] > 0
    assert info["path"].endswith(".tcm")


def test_missing_artifact_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        tp.inspect_tcm(os.path.join(TCM_ROOT, "definitely-missing.tcm"))

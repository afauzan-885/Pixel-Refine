from pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller import (
    _parse_bulk_progress,
)
from pixel_refine_desktop.enhance_stack.components.bulk_page.bulk_page_layout import (
    _move_file_with_verified_copy_fallback,
)


def test_bulk_progress_parser_accepts_resident_ui_console_keywords():
    assert _parse_bulk_progress(
        42, ui="Aligning support frame", console="support=2/5"
    ) == (42, "Aligning support frame")


def test_bulk_progress_parser_keeps_legacy_callback_signatures():
    assert _parse_bulk_progress(25, "Loading") == (25, "Loading")
    assert _parse_bulk_progress(2, 4, "Merging") == (50, "Merging")


def test_bulk_file_move_reports_saved_copy_if_locked_original_cannot_be_deleted(
    tmp_path, monkeypatch
):
    import os
    from pixel_refine_desktop.enhance_stack.components.bulk_page import bulk_page_layout

    source = tmp_path / "result.dng"
    destination = tmp_path / "output" / "result.dng"
    destination.parent.mkdir()
    source.write_bytes(b"known image payload")

    def reject_move(*_args, **_kwargs):
        raise PermissionError("simulated open-file lock")

    original_remove = os.remove
    monkeypatch.setattr(bulk_page_layout.time, "sleep", lambda _delay: None)

    def keep_locked_source(path, *args, **kwargs):
        if os.fspath(path) == os.fspath(source):
            raise PermissionError("simulated source lock")
        return original_remove(path, *args, **kwargs)

    monkeypatch.setattr(bulk_page_layout.shutil, "move", reject_move)
    monkeypatch.setattr(bulk_page_layout.os, "remove", keep_locked_source)

    success, detail = _move_file_with_verified_copy_fallback(str(source), str(destination))

    assert success
    assert "original could not be deleted" in detail
    assert "original retained" in detail
    assert destination.read_bytes() == b"known image payload"
    assert source.exists()


def test_bulk_file_move_deletes_original_after_transient_lock(
    tmp_path, monkeypatch
):
    import os

    from pixel_refine_desktop.enhance_stack.components.bulk_page import bulk_page_layout

    source = tmp_path / "result.dng"
    destination = tmp_path / "output" / "result.dng"
    destination.parent.mkdir()
    source.write_bytes(b"known image payload")

    def reject_move(*_args, **_kwargs):
        raise PermissionError("simulated open-file lock")

    original_remove = os.remove
    delete_attempts = 0

    def transiently_locked_source(path, *args, **kwargs):
        nonlocal delete_attempts
        if os.fspath(path) == os.fspath(source):
            delete_attempts += 1
            if delete_attempts < 3:
                raise PermissionError("simulated transient source lock")
        return original_remove(path, *args, **kwargs)

    monkeypatch.setattr(bulk_page_layout.shutil, "move", reject_move)
    monkeypatch.setattr(bulk_page_layout.os, "remove", transiently_locked_source)
    monkeypatch.setattr(bulk_page_layout.time, "sleep", lambda _delay: None)

    success, detail = _move_file_with_verified_copy_fallback(str(source), str(destination))

    assert success
    assert "copied after move failed" in detail
    assert destination.read_bytes() == b"known image payload"
    assert not source.exists()

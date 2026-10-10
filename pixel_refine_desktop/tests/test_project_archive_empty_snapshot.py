"""Regression tests for empty and malformed project SQLite snapshots."""

from __future__ import annotations

import json
import sqlite3
import zipfile

import pytest

from pixel_refine_desktop.enhance_stack.core.logic.database_manager import (
    DatabaseManager,
)
from pixel_refine_desktop.enhance_stack.core.logic import project_archive


def _write_project_archive(path, snapshot_path):
    manifest = {
        "magic": project_archive.PROJECT_MAGIC,
        "format_version": project_archive.PROJECT_FORMAT_VERSION,
        "database_snapshot": "session.sqlite",
        "batch_parameters": "batch_parameters.json",
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.write(snapshot_path, "session.sqlite")
        archive.writestr("batch_parameters.json", "{}")


def test_open_empty_project_archive_clears_session_without_missing_table_error(
    tmp_path, monkeypatch
):
    database_path = tmp_path / "session.sqlite"
    db = DatabaseManager(str(database_path))
    batch_id = db.create_new_batch("Existing batch")
    db.batch_process_save_image_path(batch_id, [str(tmp_path / "existing.jpg")])

    empty_snapshot = tmp_path / "empty.sqlite"
    sqlite3.connect(empty_snapshot).close()
    project_path = tmp_path / "empty_project.prf"
    _write_project_archive(project_path, empty_snapshot)
    monkeypatch.setattr(project_archive, "_json_path", lambda: tmp_path / "params.json")

    result = project_archive.load_project(
        str(project_path), str(database_path), replace=True
    )

    assert result["batch_id_map"] == {}
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM batch_process").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM images").fetchone()[0] == 0


def test_open_partially_initialized_project_reports_schema_error_transactionally(
    tmp_path, monkeypatch
):
    database_path = tmp_path / "session.sqlite"
    db = DatabaseManager(str(database_path))
    batch_id = db.create_new_batch("Existing batch")

    partial_snapshot = tmp_path / "partial.sqlite"
    with sqlite3.connect(partial_snapshot) as connection:
        connection.execute(
            "CREATE TABLE batch_process (id INTEGER PRIMARY KEY, batch_name TEXT)"
        )
    project_path = tmp_path / "partial_project.prf"
    _write_project_archive(project_path, partial_snapshot)
    monkeypatch.setattr(project_archive, "_json_path", lambda: tmp_path / "params.json")

    with pytest.raises(ValueError, match="missing required table"):
        project_archive.load_project(
            str(project_path), str(database_path), replace=True
        )

    with sqlite3.connect(database_path) as connection:
        names = connection.execute(
            "SELECT batch_name FROM batch_process WHERE id = ?", (batch_id,)
        ).fetchone()
    assert names == ("Existing batch",)

"""Portable Pixel Refine project archive (.prf) support.

The archive is a ZIP container.  The embedded SQLite file is a snapshot, not
the application's live database.  Loading merges batches and images into the
active database and remaps IDs safely.
"""

from __future__ import annotations

import json
import hashlib
import os
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import config


PROJECT_EXTENSION = ".prf"
PROJECT_MAGIC = "PIXELREFINE_PROJECT"
PROJECT_FORMAT_VERSION = 1
RECENT_PROJECTS_PATH = Path("database/setting/recent_projects.json")


def _json_path() -> Path:
    from pixel_refine_desktop.enhance_stack.core.logic.batch_parameter_manager import (
        get_json_path,
    )

    return Path(get_json_path())


def _read_json(path: Path, default: Any) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return default


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)


def session_state_token(database_path: str) -> str:
    """Return a content token for the live session database and parameters.

    The token is intentionally independent of the project archive itself.  It
    lets the UI detect changes made after the last Save Project operation,
    including changes to batch parameters.
    """
    digest = hashlib.sha256()
    # Hash logical rows rather than SQLite file bytes.  WAL checkpoints,
    # auto-increment metadata, and journal headers must not look like edits.
    try:
        with sqlite3.connect(database_path) as connection:
            for table in ("images", "single_process_image", "batch_process", "batch_process_image"):
                try:
                    columns = [row[1] for row in connection.execute(f"PRAGMA table_info({table})")]
                    rows = connection.execute(f"SELECT * FROM {table}").fetchall()
                except sqlite3.Error:
                    columns, rows = [], []
                digest.update(table.encode("utf-8"))
                digest.update(json.dumps(columns, ensure_ascii=False).encode("utf-8"))
                digest.update(json.dumps(rows, ensure_ascii=False, default=str).encode("utf-8"))
    except sqlite3.Error:
        digest.update(b"<database-unavailable>")
    parameters = _read_json(_json_path(), {})
    digest.update(json.dumps(parameters, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8"))
    return digest.hexdigest()


def session_has_data(database_path: str) -> bool:
    """Return whether the live session contains anything worth saving."""
    if not os.path.isfile(database_path):
        return False
    try:
        with sqlite3.connect(database_path) as connection:
            for table in ("batch_process", "images", "single_process_image"):
                try:
                    row = connection.execute(
                        f"SELECT 1 FROM {table} LIMIT 1"
                    ).fetchone()
                except sqlite3.Error:
                    row = None
                if row is not None:
                    return True
    except sqlite3.Error:
        return False
    parameters = _read_json(_json_path(), {})
    return bool(parameters) if isinstance(parameters, dict) else False


def recent_projects(limit: int = 10) -> list[str]:
    values = _read_json(RECENT_PROJECTS_PATH, [])
    if not isinstance(values, list):
        return []
    result = []
    for value in values:
        path = os.path.abspath(str(value))
        if os.path.isfile(path) and path.lower().endswith(PROJECT_EXTENSION):
            result.append(path)
        if len(result) >= limit:
            break
    return result


def remember_project(path: str, limit: int = 10) -> None:
    normalized = os.path.abspath(path)
    values = [normalized] + [item for item in recent_projects(limit * 2) if item != normalized]
    _write_json(RECENT_PROJECTS_PATH, values[:limit])


def save_project(
    destination: str,
    database_path: str,
    *,
    active_batch_id: Optional[int] = None,
    page: str = "enhance_stack",
) -> Dict[str, Any]:
    """Write a self-contained project snapshot to ``destination``."""
    destination_path = Path(destination).with_suffix(PROJECT_EXTENSION)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    database_path = os.path.abspath(database_path)
    if not os.path.isfile(database_path):
        raise FileNotFoundError(database_path)

    parameters_path = _json_path()
    manifest = {
        "magic": PROJECT_MAGIC,
        "format_version": PROJECT_FORMAT_VERSION,
        "application_version": getattr(config, "APP_VERSION", "unknown"),
        "page": page,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active_batch_id": active_batch_id,
        "database_snapshot": "session.sqlite",
        "batch_parameters": "batch_parameters.json",
    }

    with tempfile.TemporaryDirectory(prefix="pixelrefine_prf_") as temp_dir:
        snapshot = Path(temp_dir) / "session.sqlite"
        source = sqlite3.connect(database_path)
        target = sqlite3.connect(str(snapshot))
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()

        with zipfile.ZipFile(
            destination_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
        ) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
            archive.write(snapshot, "session.sqlite")
            if parameters_path.is_file():
                archive.write(parameters_path, "batch_parameters.json")
            else:
                archive.writestr("batch_parameters.json", "{}\n")

    remember_project(str(destination_path))
    return manifest | {"path": str(destination_path)}


def restore_project_session(project_path: str, database_path: str) -> Dict[str, Any]:
    """Restore a project snapshot into a fresh runtime session database.

    This is used before the UI is created (for Explorer/double-click launch),
    so the application never needs the historical public database filename.
    """
    source_path = Path(project_path)
    target_path = Path(database_path)
    with zipfile.ZipFile(source_path, "r") as archive:
        try:
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            if manifest.get("magic") != PROJECT_MAGIC:
                raise ValueError("Not a Pixel Refine project archive")
            if int(manifest.get("format_version", 0)) > PROJECT_FORMAT_VERSION:
                raise ValueError("Project format is newer than this application")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="pixelrefine_prf_restore_") as temp_dir:
                temp_path = Path(temp_dir)
                archive.extract("session.sqlite", temp_path)
                if target_path.exists():
                    target_path.unlink()
                shutil.copy2(temp_path / "session.sqlite", target_path)
                parameters = archive.read("batch_parameters.json")
            parameter_path = _json_path()
            parameter_path.parent.mkdir(parents=True, exist_ok=True)
            parameter_path.write_bytes(parameters)
        except KeyError as exc:
            raise ValueError(f"Invalid project archive: missing {exc}") from exc
    remember_project(str(source_path))
    return {
        "manifest": manifest,
        "path": str(source_path.resolve()),
        "active_batch_id": manifest.get("active_batch_id"),
    }


def _table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}


def load_project(
    destination: str, database_path: str, *, replace: bool = False
) -> Dict[str, Any]:
    """Merge a `.prf` snapshot into the active database transactionally."""
    project_path = Path(destination)
    with zipfile.ZipFile(project_path, "r") as archive:
        try:
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            if manifest.get("magic") != PROJECT_MAGIC:
                raise ValueError("Not a Pixel Refine project archive")
            if int(manifest.get("format_version", 0)) > PROJECT_FORMAT_VERSION:
                raise ValueError("Project format is newer than this application")
            with tempfile.TemporaryDirectory(prefix="pixelrefine_prf_load_") as temp_dir:
                temp_path = Path(temp_dir)
                archive.extract("session.sqlite", temp_path)
                parameters = json.loads(
                    archive.read("batch_parameters.json").decode("utf-8")
                )
                result = _merge_snapshot(
                    str(temp_path / "session.sqlite"),
                    database_path,
                    parameters,
                    manifest.get("active_batch_id"),
                    replace=replace,
                )
        except KeyError as exc:
            raise ValueError(f"Invalid project archive: missing {exc}") from exc

    remember_project(str(project_path))
    result["manifest"] = manifest
    result["path"] = str(project_path.resolve())
    return result


def _merge_snapshot(
    snapshot_path: str,
    database_path: str,
    parameters: Any,
    active_source_batch_id: Any = None,
    *,
    replace: bool = False,
) -> Dict[str, Any]:
    source = sqlite3.connect(snapshot_path)
    target = sqlite3.connect(database_path)
    target.execute("PRAGMA foreign_keys = ON")
    remap: dict[int, int] = {}
    try:
        target.execute("BEGIN")
        if replace:
            # The project file is the source of truth for an explicit Open
            # operation; remove the previous runtime session first.
            target.execute("DELETE FROM batch_process_image")
            target.execute("DELETE FROM single_process_image")
            target.execute("DELETE FROM batch_process")
            target.execute("DELETE FROM images")
        source_columns = _table_columns(source, "batch_process")
        order_expr = "order_index" if "order_index" in source_columns else "0"
        batches = source.execute(
            f"SELECT id, batch_name, {order_expr} FROM batch_process ORDER BY id"
        ).fetchall()
        target_batch_columns = _table_columns(target, "batch_process")
        for source_id, name, order_index in batches:
            row = target.execute(
                "SELECT id FROM batch_process WHERE batch_name = ?", (name,)
            ).fetchone()
            if row:
                target_id = int(row[0])
            else:
                if "order_index" in target_batch_columns:
                    target.execute(
                        "INSERT INTO batch_process(batch_name, order_index) VALUES (?, ?)",
                        (name, order_index or 0),
                    )
                else:
                    target.execute("INSERT INTO batch_process(batch_name) VALUES (?)", (name,))
                target_id = int(target.execute("SELECT last_insert_rowid()").fetchone()[0])
            remap[int(source_id)] = target_id

        source_image_paths = dict(source.execute("SELECT id, path FROM images").fetchall())
        for path in source_image_paths.values():
            target.execute("INSERT OR IGNORE INTO images(path) VALUES (?)", (path,))

        for batch_id, image_id, is_reference in source.execute(
            "SELECT batch_id, image_id_batch, is_reference_batch FROM batch_process_image"
        ).fetchall():
            target_batch = remap.get(int(batch_id))
            source_path = source_image_paths.get(int(image_id))
            image_row = (
                target.execute("SELECT id FROM images WHERE path = ?", (source_path,)).fetchone()
                if source_path
                else None
            )
            if target_batch is None or image_row is None:
                continue
            target.execute(
                "INSERT OR IGNORE INTO batch_process_image(batch_id, image_id_batch, is_reference_batch) VALUES (?, ?, ?)",
                (target_batch, int(image_row[0]), int(bool(is_reference))),
            )

        target.commit()
    except Exception:
        target.rollback()
        raise
    finally:
        source.close()
        target.close()

    if isinstance(parameters, dict):
        current = _read_json(_json_path(), {})
        if not isinstance(current, dict):
            current = {}
        if replace:
            current = {}
        for source_id, entry in parameters.items():
            target_id = remap.get(int(source_id)) if str(source_id).isdigit() else None
            if target_id is not None:
                current[str(target_id)] = entry
        _write_json(_json_path(), current)

    try:
        active_source = int(active_source_batch_id)
    except (TypeError, ValueError):
        active_source = None
    return {"batch_id_map": remap, "active_batch_id": remap.get(active_source)}

"""Exact bulk-output identity and filesystem-only export (no image decoding)."""

import hashlib
import os
import shutil
import tempfile
import time

import config
from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import normalize_name


def batch_selections(state, selected=None):
    """Use the same saved switches/aliases for cache lookup and execution."""
    selected = selected or {}
    selections = {}
    for category, stored_key, enabled_key, default_enabled in (
        ("alignment", config.KEY_ALIGNMENT_ALGO, config.KEY_CHECKBOX_ALIGN, True),
        ("denoising", config.KEY_DENOISING_ALGO, config.KEY_CHECKBOX_DENOISING, False),
        ("super_resolution", config.KEY_SUPER_RESOLUTION_ALGO, config.KEY_CHECKBOX_SUPER_RES, False),
        ("hdr", config.KEY_HDR_ALGO, config.KEY_CHECKBOX_HDR, False),
    ):
        value = state.get(category) or state.get(stored_key) or selected.get(category)
        selections[category] = normalize_name(category, value) if (
            state.get(enabled_key, default_enabled) and value not in (None, "", "None")
        ) else "none"
    return selections


def expected_output_names(stages, image_paths, settings):
    """Return exact names, or None when an algorithm's reference is dynamic.

    HDR can select a different reference during its preflight, so its returned
    paths, rather than a guessed prefix, are authoritative after processing.
    """
    if not image_paths or not stages:
        return None
    stem = os.path.splitext(os.path.basename(image_paths[0]))[0]
    safe_name = "".join(c for c in stem if c.isalnum() or c in ("_", "-")).rstrip()
    native = str(settings.get("processing_format", "RGB Linear")).strip().lower() == "raw native"
    extensions = [os.path.splitext(path)[1].lower() for path in image_paths]
    linear = settings.get("enable_linear_mode", False) or native
    extension = ".dng" if linear and extensions[0] in (
        ".dng", ".cr2", ".cr3", ".nef", ".arw"
    ) else ".tif"
    # Do not hide an invalid RAW Native input behind a cache hit.
    if native and any(ext != ".dng" for ext in extensions):
        return None
    names = []
    for spec in stages:
        kwargs = dict(spec.entrypoint_kwargs)
        if spec.category == "denoising" and "output_suffix" in kwargs:
            names.append(f"{safe_name or 'stack'}_{kwargs['output_suffix']}{extension}")
        elif spec.category == "super_resolution" and spec.key == "splatting_sr":
            # SplatSR's RGB writer follows enable_linear_mode, not RAW Native.
            sr_extension = ".dng" if settings.get("enable_linear_mode", False) and extensions[0] in (
                ".dng", ".cr2", ".cr3", ".nef", ".arw"
            ) else ".tif"
            names.append(f"{safe_name or 'sr_result'}_splattingSR{sr_extension}")
        else:
            return None
    return names


def usable_output(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def find_existing_outputs(names, directories):
    """Require every exact output; never match a prefix, numbered copy or preview."""
    if not names:
        return []
    paths = []
    for name in names:
        match = next((os.path.join(folder, name) for folder in directories
                      if folder and usable_output(os.path.join(folder, name))), None)
        if match is None:
            return []
        paths.append(match)
    return paths


def returned_output_paths(result):
    """Extract only declared result paths, not input/reference paths from reports."""
    if isinstance(result, (str, os.PathLike)):
        return [os.fspath(result)]
    if isinstance(result, (list, tuple)):
        return [path for item in result for path in returned_output_paths(item)]
    if isinstance(result, dict):
        return [os.fspath(result[key]) for key in ("ldr_path", "radiance_path", "output_path")
                if result.get(key)]
    return []


def _digest(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").digest()


def copy_result(source, destination):
    """Publish a byte-verified copy atomically, leaving the source untouched."""
    if not usable_output(source):
        return False, f"Source output is missing or empty: {source}"
    if os.path.normcase(os.path.abspath(source)) == os.path.normcase(os.path.abspath(destination)):
        return True, "already in target folder"
    if os.path.exists(destination):
        if usable_output(destination) and _digest(source) == _digest(destination):
            return True, "identical destination already exists"
        return False, f"Destination already exists with different content: {destination}"
    fd, temporary = tempfile.mkstemp(
        prefix=f".{os.path.basename(destination)}.", suffix=".partial",
        dir=os.path.dirname(destination) or ".",
    )
    os.close(fd)
    try:
        shutil.copy2(source, temporary)
        if os.path.getsize(source) != os.path.getsize(temporary) or _digest(source) != _digest(temporary):
            raise OSError("Copied file does not match the source bytes")
        # Unlike replace(), link() cannot overwrite an existing destination.
        # The temporary lives on the target volume; rename is also safe on Windows.
        if os.name == "nt":
            os.rename(temporary, destination)
        else:
            os.link(temporary, destination)
        return True, "copied and verified"
    except OSError as error:
        return False, f"Copy failed: {error}"
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def move_result(source, destination):
    """Keep move-first behavior; a saved copy is success even if cleanup is locked."""
    if not usable_output(source):
        return False, f"Source output is missing or empty: {source}"
    if os.path.normcase(os.path.abspath(source)) == os.path.normcase(os.path.abspath(destination)):
        return True, "already in target folder"
    if os.path.exists(destination):
        return copy_result(source, destination)
    try:
        shutil.move(source, destination)
        return True, "moved"
    except OSError as move_error:
        success, detail = copy_result(source, destination)
        if not success:
            return False, f"Move failed ({move_error}); {detail}"
        cleanup_error = None
        for attempt in range(5):
            try:
                os.remove(source)
                return True, f"copied after move failed: {move_error}"
            except OSError as error:
                cleanup_error = error
                if attempt < 4:
                    time.sleep(0.2 * (attempt + 1))
        return True, (
            "destination copy verified but original could not be deleted after "
            f"5 attempts; original retained: {cleanup_error}"
        )

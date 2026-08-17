"""Validation helpers for user-selected image imports."""

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from config import SUPPORTED_FORMATS


SUPPORTED_EXTENSIONS = frozenset(
    extension.lower()
    for extensions in SUPPORTED_FORMATS.values()
    for extension in extensions
)


def build_file_dialog_filter() -> str:
    """Build the shared QFileDialog filter for every image importer."""

    all_extensions = sorted(
        {
            f"*{extension}"
            for extensions in SUPPORTED_FORMATS.values()
            for extension in extensions
        }
    )
    filters = [f"All Supported Images ({' '.join(all_extensions)})"]
    filters.extend(
        f"{format_name.upper()} Files ({' '.join(f'*{ext}' for ext in extensions)})"
        for format_name, extensions in SUPPORTED_FORMATS.items()
    )
    filters.append("All Files (*)")
    return ";;".join(filters)


def validate_image_paths(image_paths):
    """Return canonical regular files and human-readable rejection reasons.

    The importer accepts only files selected by the user that still exist,
    resolve to regular files, use a supported extension, and can be opened by
    Pillow for standard image formats. RAW formats are validated by rawpy when
    they are decoded by the thumbnail/processing pipeline.
    """
    accepted = []
    rejected = []
    seen = set()
    raw_extensions = frozenset(SUPPORTED_FORMATS.get("raw", ()))

    for candidate in image_paths or []:
        try:
            path = Path(candidate).expanduser().resolve(strict=True)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            rejected.append((str(candidate), f"path tidak dapat diakses: {exc}"))
            continue

        if not path.is_file():
            rejected.append((str(path), "bukan file biasa"))
            continue

        extension = path.suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            rejected.append((str(path), "format file tidak didukung"))
            continue

        canonical_path = str(path)
        if canonical_path in seen:
            continue

        if extension not in raw_extensions:
            try:
                with Image.open(path) as image:
                    image.verify()
            except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
                rejected.append((canonical_path, f"isi gambar tidak valid: {exc}"))
                continue

        seen.add(canonical_path)
        accepted.append(canonical_path)

    return accepted, rejected

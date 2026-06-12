"""
Import/Export Controller.
Handles file import/export operations including validation and format conversion.
"""

from PySide6.QtCore import QObject, Signal, QThread
from typing import List, Tuple, Optional, Dict
import os
from config import SUPPORTED_FORMATS


class ImportExportController(QObject):
    """
    Controller for import/export operations.
    Handles file validation, format conversion, and threading.
    """

    # Signals for view communication
    validation_completed = Signal(list, list)  # (valid_paths, invalid_paths)
    duplicate_found = Signal(list)  # (duplicate_paths)
    conversion_started = Signal(str)  # (file_path)
    conversion_completed = Signal(str, str)  # (original_path, converted_path)
    conversion_error = Signal(str, str)  # (file_path, error_message)

    import_started = Signal(int)  # (total_files)
    import_progress = Signal(int, int)  # (current, total)
    import_completed = Signal(int)  # (successful_count)
    import_error = Signal(str)  # (error_message)

    export_started = Signal(str)  # (destination_path)
    export_completed = Signal(str)  # (saved_path)
    export_error = Signal(str)  # (error_message)

    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize controller.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self.import_thread: Optional[QThread] = None

    def validate_files(self, file_paths: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate file paths and formats.

        Args:
            file_paths: List of file paths to validate

        Returns:
            Tuple of (valid_paths, invalid_paths)
        """
        valid_paths = []
        invalid_paths = []

        for path in file_paths:
            if not os.path.exists(path):
                invalid_paths.append(path)
                continue

            if not os.path.isfile(path):
                invalid_paths.append(path)
                continue

            # Check if format is supported
            ext = os.path.splitext(path)[1].lower()
            is_supported = any(
                ext in extensions for extensions in SUPPORTED_FORMATS.values()
            )

            if is_supported:
                valid_paths.append(path)
            else:
                invalid_paths.append(path)

        self.validation_completed.emit(valid_paths, invalid_paths)
        return valid_paths, invalid_paths

    def check_duplicates(
        self, paths: List[str], existing_paths: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Check for duplicate files.

        Args:
            paths: List of paths to check
            existing_paths: List of already existing paths

        Returns:
            Tuple of (unique_paths, duplicate_paths)
        """
        existing_set = set(existing_paths)
        duplicates = [p for p in paths if p in existing_set]
        unique = [p for p in paths if p not in existing_set]

        if duplicates:
            self.duplicate_found.emit(duplicates)

        return unique, duplicates

    def group_by_format(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Group files by format.

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary mapping format type to list of paths
        """
        format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}

        for path in file_paths:
            lower_path = path.lower()
            for format_key, extensions in SUPPORTED_FORMATS.items():
                if any(lower_path.endswith(ext) for ext in extensions):
                    format_groups[format_key].append(path)
                    break

        return format_groups

    def needs_tiff_conversion(self, tiff_path: str) -> Tuple[bool, str]:
        """
        Check if TIFF file needs conversion.

        Args:
            tiff_path: Path to TIFF file

        Returns:
            Tuple of (needs_conversion, compression_type)
        """
        try:
            from PIL import Image

            with Image.open(tiff_path) as img:
                compression = img.info.get("compression", "none").lower()

                # Check if compression requires conversion
                if compression in ["tiff_lzw", "tiff_zip", "packbits", "jpeg"]:
                    return True, compression

                return False, compression
        except Exception as e:
            print(f"Error checking TIFF compression for {tiff_path}: {e}")
            return False, "unknown"

    def convert_tiff_to_uncompressed(
        self, tiff_paths: List[str], output_folder: str
    ) -> List[Tuple[bool, str]]:
        """
        Convert compressed TIFF files to uncompressed.

        Args:
            tiff_paths: List of TIFF file paths
            output_folder: Output folder for converted files

        Returns:
            List of tuples (success, result_path_or_error)
        """
        from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_import_service import (
            convert_tiff_to_uncompressed,
        )

        results = []

        for tiff_path in tiff_paths:
            needs_conversion, compression = self.needs_tiff_conversion(tiff_path)

            if not needs_conversion:
                # No conversion needed, use original
                results.append((True, tiff_path))
                continue

            self.conversion_started.emit(tiff_path)

            try:
                # Use existing conversion function
                conversion_generator = convert_tiff_to_uncompressed(
                    [tiff_path], output_folder
                )
                success, result = next(conversion_generator)

                if success:
                    self.conversion_completed.emit(tiff_path, result)
                    results.append((True, result))
                else:
                    self.conversion_error.emit(tiff_path, result)
                    results.append((False, result))
            except Exception as e:
                error_msg = f"Conversion failed: {str(e)}"
                self.conversion_error.emit(tiff_path, error_msg)
                results.append((False, error_msg))

        return results

    def start_import_thread(
        self,
        image_paths: List[str],
        database_manager,
        batch_size: int = 15,
        delay_ms: int = 25,
    ) -> None:
        """
        Start background import thread.

        Args:
            image_paths: List of image paths to import
            database_manager: Database manager instance
            batch_size: Number of images per batch
            delay_ms: Delay between batches in milliseconds
        """
        from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
            ImageImportThreading,
        )

        self.import_started.emit(len(image_paths))

        try:
            self.import_thread = ImageImportThreading(
                database_manager=database_manager,
                image_paths=image_paths,
                batch_size=batch_size,
                delay_ms=delay_ms,
            )

            # Connect signals
            self.import_thread.progress_signal.connect(self._on_import_progress)
            self.import_thread.completion_signal.connect(self._on_import_complete)

            # Start thread
            self.import_thread.start()

        except Exception as e:
            self.import_error.emit(f"Failed to start import: {str(e)}")

    def export_image(
        self,
        source_path: str,
        destination_path: str,
        quality: int = 98,
        optimize: bool = True,
    ) -> bool:
        """
        Export image with metadata preservation.

        Args:
            source_path: Source image path
            destination_path: Destination path
            quality: JPEG quality (for JPEG export)
            optimize: Whether to optimize (for JPEG/PNG)

        Returns:
            True if successful, False otherwise
        """
        self.export_started.emit(destination_path)

        try:
            import shutil
            import tifffile
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
                save_special_jpg_and_png,
            )

            dest_ext = os.path.splitext(destination_path)[1].lower()

            if dest_ext in [".tif", ".tiff"]:
                # Simple copy for TIFF
                shutil.copy2(source_path, destination_path)
            else:
                # Convert to JPEG/PNG with metadata
                source_data = tifffile.imread(source_path)
                save_special_jpg_and_png(
                    img_np=source_data,
                    dst_path=destination_path,
                    reference_image_path=source_path,
                    quality=quality,
                    optimize=optimize,
                )

            self.export_completed.emit(destination_path)
            return True

        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            self.export_error.emit(error_msg)
            return False

    def _on_import_progress(self, value: int, remaining: int) -> None:
        """Handle import progress updates."""
        total = value + remaining
        self.import_progress.emit(value, total)

    def _on_import_complete(self, successful_count: int) -> None:
        """Handle import completion."""
        self.import_completed.emit(successful_count)
        self.import_thread = None

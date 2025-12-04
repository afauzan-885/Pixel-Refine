import os
from config import SUPPORTED_FORMATS
from .multi_threading import ImageImportThreading

class ImageHandler:
    """
    Handles image import logic, including filtering, duplicate checking, and threading.
    """
    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.multi_thread_import_images = None

    def get_supported_extensions(self):
        """Returns a set of all supported extensions."""
        return {ext.lower() for fmt_list in SUPPORTED_FORMATS.values() for ext in fmt_list}

    def filter_valid_images(self, image_paths):
        """Filters paths to keep only those with supported extensions."""
        supported_extensions = self.get_supported_extensions()
        valid_paths = [
            path for path in image_paths
            if os.path.splitext(path)[1].lower() in supported_extensions
        ]
        return valid_paths

    def check_duplicates(self, valid_paths):
        """
        Checks for duplicates against the database.
        Returns (unique_files, duplicates).
        """
        try:
            existing_paths = self.database_manager.get_all_image_paths()
            existing_paths_set = set(existing_paths)
        except Exception as e:
            print(f"Error getting existing paths: {e}")
            return valid_paths, [] # Fail safe, assume all unique? Or fail?

        duplicates = [path for path in valid_paths if path in existing_paths_set]
        unique_files = [path for path in valid_paths if path not in existing_paths_set]
        return unique_files, duplicates

    def group_files_by_format(self, unique_files):
        """Groups files by their format key."""
        format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}
        for path in unique_files:
            file_ext_lower = os.path.splitext(path)[1].lower()
            for format_key, extensions in SUPPORTED_FORMATS.items():
                if file_ext_lower in extensions:
                    format_groups[format_key].append(path)
                    break
        return format_groups

    def select_dominant_format(self, format_groups, total_files_count):
        """Selects the dominant format or the first available one."""
        non_empty_groups = {k: v for k, v in format_groups.items() if v}
        if not non_empty_groups:
            return None, []

        dominant_format_key = max(non_empty_groups, key=lambda k: len(non_empty_groups[k]))
        
        if len(format_groups[dominant_format_key]) > total_files_count / 2:
            return dominant_format_key, format_groups[dominant_format_key]
        
        # Fallback to first available
        for key in SUPPORTED_FORMATS.keys():
            if format_groups[key]:
                return key, format_groups[key]
        
        return None, []

    def process_import(self, image_paths, callbacks=None):
        """
        Main entry point for processing imported images.
        callbacks: dict of callbacks for UI updates (on_progress, on_complete, on_error, on_message)
        """
        callbacks = callbacks or {}
        on_message = callbacks.get('on_message')
        
        # 1. Filter Valid
        valid_paths = self.filter_valid_images(image_paths)
        num_invalid = len(image_paths) - len(valid_paths)
        if num_invalid > 0 and on_message:
            on_message("Format Warning", f"{num_invalid} files were ignored due to unsupported format.")

        if not valid_paths:
            if on_message: on_message("No Valid Files", "No supported images selected.")
            return

        # 2. Check Duplicates
        unique_files, duplicates = self.check_duplicates(valid_paths)
        if duplicates and on_message:
            on_message("Duplicate Warning", f"{len(duplicates)} duplicate files were ignored.")

        if not unique_files:
            if on_message: on_message("Info", "No new unique files to import.")
            return

        # 3. Group & Select
        format_groups = self.group_files_by_format(unique_files)
        dominant_key, selected_files = self.select_dominant_format(format_groups, len(unique_files))

        if not selected_files:
            if on_message: on_message("Error", "Could not select files for import.")
            return

        if on_message:
            on_message("Importing", f"Importing {len(selected_files)} {dominant_key.upper()} files...")

        # 4. Start Thread
        try:
            self.multi_thread_import_images = ImageImportThreading(
                database_manager=self.database_manager,
                image_paths=selected_files,
                batch_size=15,
                delay_ms=25,
                on_progress=callbacks.get('on_progress'),
                on_completion=callbacks.get('on_completion'),
                on_error=callbacks.get('on_error')
            )
            self.multi_thread_import_images.start()
        except Exception as e:
            if callbacks.get('on_error'):
                callbacks['on_error'](str(e))

    def delete_images(self, selected_paths):
        """Deletes images from database."""
        if not selected_paths:
            return False
        
        self.database_manager.single_process_delete_path_images(selected_paths)
        return True

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from UI.settings.General.Language import language_config

from .multi_threading import ImageImportThreading
    
def handle_import_button(self):
    """Function to manage images import"""
    # Open file dialog and get image paths with filter
    file_dialog_filter = language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
    image_paths, _ = QFileDialog.getOpenFileNames(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, "", file_dialog_filter)
    
    if not image_paths:
        return

    # Extract file extensions from the filter string
    filter_extensions = [ext.strip().lower() for ext in file_dialog_filter.split("*") if ext.strip().startswith(".")]

    # Step 1: Validate duplicate files
    existing_paths = self.database_manager.get_all_image_paths()
    duplicates = [path for path in image_paths if path in existing_paths]
    unique_files = [path for path in image_paths if path not in duplicates]

    if duplicates:
        message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
        QMessageBox.warning(self,
                            language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE,
                            message)

    # Step 2: Group files by format based on selected file extensions
    format_groups = {ext: [] for ext in filter_extensions}

    for path in unique_files:
        for ext in filter_extensions:
            if path.lower().endswith(ext):
                format_groups[ext].append(path)
                break

    # Step 3: Determine dominant format
    dominant_format = max(format_groups, key=lambda ext: len(format_groups[ext]))

    # Step 4: Select files based on priority or dominant format
    selected_files = []
    if len(format_groups[dominant_format]) > len(unique_files) / 2:
        # If dominant format is more than half, prioritize it
        selected_files = format_groups[dominant_format]
    else:
        # Otherwise, follow the original priority order based on filter
        for ext in filter_extensions:
            if format_groups[ext]:
                selected_files = format_groups[ext]
                break

    # Step 5: Proceed with selected files
    if selected_files:
        # Inform user about the selected format and number of files to import
        message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT.format(
        
        count=len(selected_files),
        format=dominant_format)
        
        QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_SELECTED, message)
        
        # Proceed with importing the selected files
        self.multi_thread_import_images = ImageImportThreading(
            self.database_manager,
            selected_files,
            batch_size=15,
            delay_ms=25
        )

        # Connect signals to update progress and completion
        self.multi_thread_import_images.progress_signal.connect(self.update_progress_bar)
        self.multi_thread_import_images.completion_signal.connect(self.on_import_complete)

        # Start the thread
        self.multi_thread_import_images.start()
    else:
        QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED)

def handle_delete_button(self):
    """Function to delete images"""
    selected_paths = self.right_panel.get_select_image_list()
    if not selected_paths:
        title, message = language_config.HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED
        QMessageBox.information(self, title, message)
        return

    reply = QMessageBox.question(
        self,
        "Delete Images",
        language_config.HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE.format(count=len(selected_paths)),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        self.database_manager.delete_images(selected_paths)
        self.right_panel.remove_selected_images()

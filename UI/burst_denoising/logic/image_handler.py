from PyQt6.QtWidgets import QFileDialog, QMessageBox

from .multi_threading import ImageImportThreading
    
def handle_import_button(self):
        """Function to manage images import"""
        # Open file dialog and get image paths
        image_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Image Files (*.jpg *.jpeg *.png *.dng *.tiff)")
        if not image_paths:
            return

        # Step 1: Validate duplicate files
        existing_paths = self.database_manager.get_all_image_paths()
        duplicates = [path for path in image_paths if path in existing_paths]
        unique_files = [path for path in image_paths if path not in duplicates]

        if duplicates:
            QMessageBox.warning(self,
                                "Duplicate Files",
                                f"{len(duplicates)} file(s) already exist in the database and will be skipped.")

        # Step 2: Group files by format
        supported_formats = {".dng", ".tiff", ".png", ".jpg", ".jpeg"}
        format_groups = {ext: [] for ext in supported_formats}

        for path in unique_files:
            for ext in supported_formats:
                if path.lower().endswith(ext):
                    format_groups[ext].append(path)
                    break

        # Step 3: Determine dominant format
        dominant_format = max(format_groups, key=lambda ext: len(format_groups[ext]))

        # Step 4: Select files based on priority or dominant format
        selected_files = []
        priority_order = [".dng", ".tiff", ".png", ".jpg", ".jpeg"]
        if len(format_groups[dominant_format]) > len(unique_files) / 2:
            # If dominant format is more than half, prioritize it
            selected_files = format_groups[dominant_format]
        else:
            # Otherwise, follow the priority order
            for ext in priority_order:
                if format_groups[ext]:
                    selected_files = format_groups[ext]
                    break

        # Step 5: Proceed with selected files
        if selected_files:
            # Inform user about the selected format and number of files to import
            QMessageBox.information(self,
                                    "Selected Format",
                                    f"{len(selected_files)} file(s) with format '{dominant_format}' will be imported.")
            
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
            QMessageBox.information(self, "Error", "No valid files to import.")
            
def handle_delete_button(self):
        """Function to delete images"""
        selected_paths = self.right_panel.get_selected_image_paths()
        if not selected_paths:
            QMessageBox.information(self, "Error", "No images selected.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Images",
            f"Are you sure you want to delete the {len(selected_paths)} selected image(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.database_manager.delete_images(selected_paths)
            self.right_panel.remove_selected_images()
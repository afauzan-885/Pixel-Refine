"""Non-blocking batch deletion with progress reporting."""

import os

from PySide6.QtCore import QThread, Signal

from config import CACHE_DIR
from pixel_refine_desktop.enhance_stack.models.data_access.batch_repository import (
    BatchRepository,
)

BATCH_DELETE_TOAST_CATEGORY = "batch_delete"


def cleanup_batch_thumbnail_cache(image_paths, cache_dir=CACHE_DIR):
    """Remove every supported thumbnail-cache representation for image paths."""

    if not image_paths:
        return

    try:
        from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import (
            get_thumbnail_repo,
        )

        get_thumbnail_repo().delete_thumbnails(image_paths)
    except Exception as exc:
        print(f"[BatchDeleteWorker] Hashed thumbnail cleanup warning: {exc}")

    for image_path in image_paths:
        legacy_cache = os.path.join(
            cache_dir, os.path.basename(image_path) + ".jpg"
        )
        try:
            os.remove(legacy_cache)
        except FileNotFoundError:
            pass
        except OSError as exc:
            print(f"[BatchDeleteWorker] Legacy thumbnail cleanup warning: {exc}")


class BatchDeleteWorker(QThread):
    """Delete selected/all batch definitions one by one in a worker thread."""

    progress_updated = Signal(int, int, object)  # current, total, batch_id
    completed = Signal(int, int)  # deleted_count, failed_count
    error = Signal(str)

    def __init__(self, db_path, batch_ids=None, cache_dir=CACHE_DIR, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.batch_ids = None if batch_ids is None else list(dict.fromkeys(batch_ids))
        self.cache_dir = cache_dir

    def _resolve_batch_ids(self, repository):
        if self.batch_ids is not None:
            return list(self.batch_ids)
        return [batch_id for batch_id, _name in repository.get_all()]

    def _cleanup_thumbnail_cache(self, image_paths):
        """Remove both current hashed and legacy basename thumbnail caches."""
        cleanup_batch_thumbnail_cache(image_paths, self.cache_dir)

    def run(self):
        deleted_count = 0
        failed_count = 0

        try:
            repository = BatchRepository(self.db_path)
            batch_ids = self._resolve_batch_ids(repository)
            total = len(batch_ids)

            if total == 0:
                self.completed.emit(0, 0)
                return

            for current, batch_id in enumerate(batch_ids, start=1):
                if self.isInterruptionRequested():
                    break

                try:
                    image_rows = repository.get_batch_images(batch_id)
                    image_paths = [row[1] for row in image_rows]
                    deleted_rows = repository.delete(batch_id)
                    if deleted_rows > 0:
                        self._cleanup_thumbnail_cache(image_paths)
                        deleted_count += 1
                    else:
                        failed_count += 1
                except Exception as exc:
                    failed_count += 1
                    print(f"[BatchDeleteWorker] Failed to delete batch {batch_id}: {exc}")

                self.progress_updated.emit(current, total, batch_id)

            self.completed.emit(deleted_count, failed_count)
        except Exception as exc:
            self.error.emit(str(exc))
            self.completed.emit(deleted_count, failed_count + 1)

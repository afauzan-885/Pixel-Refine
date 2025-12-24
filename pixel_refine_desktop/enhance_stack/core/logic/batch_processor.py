"""
Batch Processor Logic
Handles background processing of image batches independently of the UI.
"""

from PySide6.QtCore import QThread, Signal, QObject, QMetaObject, Qt
import os


class BatchProcessingThread(QThread):
    """
    Worker thread that processes a list of batches sequentially.
    """

    # row_index, status_text, details_text, percent_in_batch, current_batch_num, total_batches
    progress_update = Signal(int, str, str, int, int, int)

    # row_index, success, result_message
    batch_finished = Signal(int, bool, str)

    # List of failed batches summary
    processing_complete = Signal(list)

    # Signal to request batch context switch in main thread (batch_id)
    batch_context_switch_requested = Signal(int)

    # Signal to request algorithm execution in main thread (batch_id)
    execute_algorithm_requested = Signal(int)

    # Signal from main thread when algorithm execution is complete
    algorithm_execution_completed = Signal()

    def __init__(self, panels_to_process, batch_page_layout, target_folder):
        super().__init__()
        self.panels_to_process = panels_to_process
        self.batch_page_layout = batch_page_layout
        self.target_folder = target_folder
        self._is_running = True
        self._algorithm_completed = False

    def stop(self):
        """Request the thread to stop smoothly."""
        self._is_running = False

    def run(self):
        failed_batches_summary = []
        total_batches_to_process = len(self.panels_to_process)

        for i, (panel, row) in enumerate(self.panels_to_process):
            if not self._is_running:
                break

            # For BatchModel: use index as seq_num and batch.id as batch_id
            batch = panel  # panel is actually a BatchModel
            seq_num = i + 1
            batch_id = batch.id if batch.id else "UNKNOWN"

            try:
                # Callback function to relay progress from the algorithm to the UI
                def sub_process_progress_callback(
                    percent_or_current, total=None, message=""
                ):
                    if not self._is_running:
                        return

                    percent = 0
                    msg = message

                    # Handle different callback signatures
                    if total is not None:
                        # (current, total, message)
                        percent = (
                            int((percent_or_current / total) * 100) if total > 0 else 0
                        )
                    else:
                        # (percent, message) or just (percent, )
                        percent = percent_or_current
                        if isinstance(total, str):  # if second arg was message
                            msg = total

                    current_num_for_ui = i + 1

                    self.progress_update.emit(
                        row,
                        "Processing",
                        msg,
                        percent,
                        current_num_for_ui,
                        total_batches_to_process,
                    )

                # CRITICAL: Load batch context in main thread to avoid QObject parent issues
                # Emit signal to request context switch, then wait briefly for it to complete
                self.batch_context_switch_requested.emit(batch_id)

                # Give main thread time to process the signal and load batch
                self.msleep(200)  # 200ms for UI to update

                # CRITICAL: Snapshot files BEFORE algorithm execution to detect new output
                files_before = set(self.batch_page_layout.get_files_in_stack_folder())

                # CRITICAL: Execute algorithm in MAIN THREAD to avoid nested worker thread issues
                # Many algorithms (Average, Median, AKAZE, etc.) spawn their own ThreadWorker
                # Calling them from this worker thread causes deadlock
                self._algorithm_completed = False
                self.execute_algorithm_requested.emit(batch_id)

                # Wait for algorithm to complete (main thread will signal when done)
                max_wait_seconds = 300  # 5 minutes timeout
                wait_interval_ms = 100
                waited_ms = 0

                while not self._algorithm_completed and waited_ms < (
                    max_wait_seconds * 1000
                ):
                    self.msleep(wait_interval_ms)
                    waited_ms += wait_interval_ms
                    if not self._is_running:
                        break

                if not self._algorithm_completed:
                    raise TimeoutError(
                        f"Algorithm execution timed out after {max_wait_seconds}s"
                    )

                # Snapshot files AFTER algorithm execution to detect new output
                files_after = set(self.batch_page_layout.get_files_in_stack_folder())
                new_files = list(files_after - files_before)

                if new_files:
                    output_file = new_files[0]
                    # Use layout helper to move file to target
                    move_success = self.batch_page_layout._move_single_batch_result(
                        output_file, self.target_folder
                    )

                    if move_success:
                        self.batch_finished.emit(row, True, "Success: Saved")
                    else:
                        self.batch_finished.emit(
                            row, False, "Error: Failed to move result."
                        )
                else:
                    self.batch_finished.emit(
                        row, False, "Error: No output file generated."
                    )

            except Exception as e:
                error_detail = str(e)
                failed_summary = {"seq": seq_num, "id": batch_id, "error": error_detail}
                failed_batches_summary.append(failed_summary)
                self.batch_finished.emit(row, False, f"Failed: {error_detail[:50]}...")

        self.processing_complete.emit(failed_batches_summary)

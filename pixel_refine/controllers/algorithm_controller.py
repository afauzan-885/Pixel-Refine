import threading
import time
from kivy.clock import Clock


class AlgorithmController:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.is_running = False

    def run_alignment(self, project_id, method, callback=None):
        if self.is_running:
            print("Algorithm already running")
            return

        self.is_running = True
        thread = threading.Thread(
            target=self._run_alignment_thread, args=(project_id, method, callback)
        )
        thread.start()

    def _run_alignment_thread(self, project_id, method, callback):
        print(f"Starting alignment with {method} for project {project_id}")

        # Simulate progress
        for i in range(0, 101, 10):
            time.sleep(0.2)  # Simulate work
            Clock.schedule_once(
                lambda dt, p=i: self.main_controller.update_progress(
                    p, f"Aligning... {p}%"
                )
            )

        # TODO: Call actual algorithm here
        # from pixel_refine.algorithm.alignment import AKAZE
        # result = AKAZE.align(...)

        print("Alignment complete")
        self.is_running = False
        Clock.schedule_once(
            lambda dt: self.main_controller.update_progress(100, "Alignment Complete")
        )

        if callback:
            Clock.schedule_once(lambda dt: callback(True))

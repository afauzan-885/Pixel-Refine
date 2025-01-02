import os

from UI.settings.General.Language import language_config
from .multi_threading import RunningAlgorithmThreading

def process_algorithm(self, virtualenv_path=r"venv/Scripts/python.exe", base_path="UI/enhance_stack/algorithm"):
    """Handle algorithm processing when 'Process' button is clicked."""

    # Get selected algorithms and stacking method
    alignment = self.left_panel.alignment_dropdown.currentText()
    multiFrame_super_resolution = self.left_panel.super_resolution_dropdown.currentText()
    multiFrame_noise_reduction = self.left_panel.denoising_dropdown.currentText()

    # Ensure mutual exclusivity between multiFrame_super_resolution and multiFrame_noise_reduction
    if multiFrame_super_resolution != "None":
        multiFrame_noise_reduction = "None"
    elif multiFrame_noise_reduction != "None":
        multiFrame_super_resolution = "None"

    # Validate dropdown selections
    if alignment == "None" and multiFrame_super_resolution == "None" and multiFrame_noise_reduction == "None":
        print(language_config.PROCESS_ALGORITHM_PROCESS_SKIPPED)
        return

    # Dynamically define paths for algorithms
    algorithm_alignment = {self.left_panel.alignment_dropdown.itemText(i): os.path.join(base_path, "alignment", 
                           f"{self.left_panel.alignment_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                         for i in range(self.left_panel.alignment_dropdown.count())}

    algorithm_multiFrame_super_resolution = {self.left_panel.super_resolution_dropdown.itemText(i): os.path.join(base_path, "super_resolution", 
                          f"{self.left_panel.super_resolution_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                        for i in range(self.left_panel.super_resolution_dropdown.count())}

    algorithm_multiFrame_noise_reduction = {self.left_panel.denoising_dropdown.itemText(i): os.path.join(base_path, "denoising", 
                         f"{self.left_panel.denoising_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                        for i in range(self.left_panel.denoising_dropdown.count())}

    # Prepare tasks for threading
    algorithm_tasks = []

    if alignment != "None" and alignment in algorithm_alignment:
        algorithm_tasks.append((virtualenv_path, algorithm_alignment[alignment], f"Alignment: {alignment}"))

    if multiFrame_super_resolution != "None" and multiFrame_super_resolution in algorithm_multiFrame_super_resolution:
        algorithm_tasks.append((virtualenv_path, algorithm_multiFrame_super_resolution[multiFrame_super_resolution], f"Super Resolution: {multiFrame_super_resolution}"))

    if multiFrame_noise_reduction != "None" and multiFrame_noise_reduction in algorithm_multiFrame_noise_reduction:
        algorithm_tasks.append((virtualenv_path, algorithm_multiFrame_noise_reduction[multiFrame_noise_reduction], f"Denoising: {multiFrame_noise_reduction}"))

    # Run algorithms in a separate thread
    self.algorithm_thread = RunningAlgorithmThreading(algorithm_tasks)
    self.algorithm_thread.progress_signal.connect(self.update_progress_bar)

    # Start the thread
    self.algorithm_thread.start()

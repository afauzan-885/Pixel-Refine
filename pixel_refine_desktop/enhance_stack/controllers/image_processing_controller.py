"""
Image Processing Controller.
Orchestrates image processing algorithms (alignment, denoising, super resolution).
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional, Dict, Any
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.AKAZE import (
    running_akaze,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.Light_Glue import (
    running_light_glue,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.ORB import (
    running_orb,
)
from pixel_refine_desktop.enhance_stack.models.algorithm_config_model import (
    AlgorithmConfig,
    AlgorithmType,
)


class ImageProcessingController(QObject):
    """
    Controller for image processing operations.
    Coordinates algorithm execution and workflow.
    """

    # Signals for view communication
    processing_started = Signal(str)  # (algorithm_name)
    processing_progress = Signal(int, int)  # (current, total)
    processing_completed = Signal(str, str)  # (algorithm_type, result_path)
    processing_error = Signal(str, str)  # (algorithm_name, error_message)

    workflow_started = Signal()
    workflow_step_completed = Signal(str)  # (step_name)
    workflow_completed = Signal(str)  # (final_result_path)
    workflow_error = Signal(str)  # (error_message)

    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize controller.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self.current_config: Optional[AlgorithmConfig] = None

    def execute_alignment(
        self,
        algorithm_name: str,
        parameters: Dict[str, Any],
        image_paths: list,
        single_process: bool = True,
    ) -> Optional[str]:
        """
        Execute alignment algorithm.

        Args:
            algorithm_name: Name of alignment algorithm (ORB, AKAZE, etc.)
            parameters: Algorithm parameters
            image_paths: List of image paths to align
            single_process: Whether this is single or batch processing

        Returns:
            Path to result or None if failed
        """
        self.current_config = AlgorithmConfig(
            AlgorithmType.ALIGNMENT, algorithm_name, parameters
        )

        self.processing_started.emit(algorithm_name)

        try:
            # Import the appropriate algorithm module
            result_path = self._run_alignment_algorithm(
                algorithm_name, parameters, single_process
            )

            if result_path:
                self.processing_completed.emit("alignment", result_path)
                return result_path
            else:
                self.processing_error.emit(
                    algorithm_name, "Algorithm returned no result"
                )
                return None

        except Exception as e:
            error_msg = f"Error executing {algorithm_name}: {str(e)}"
            self.processing_error.emit(algorithm_name, error_msg)
            return None

    def execute_denoising(
        self,
        algorithm_name: str,
        parameters: Dict[str, Any],
        image_paths: list,
        single_process: bool = True,
    ) -> Optional[str]:
        """
        Execute denoising algorithm.

        Args:
            algorithm_name: Name of denoising algorithm (Average, Median, Similarity)
            parameters: Algorithm parameters
            image_paths: List of image paths
            single_process: Whether this is single or batch processing

        Returns:
            Path to result or None if failed
        """
        self.current_config = AlgorithmConfig(
            AlgorithmType.DENOISING, algorithm_name, parameters
        )

        self.processing_started.emit(algorithm_name)

        try:
            result_path = self._run_denoising_algorithm(
                algorithm_name, parameters, single_process
            )

            if result_path:
                self.processing_completed.emit("denoising", result_path)
                return result_path
            else:
                self.processing_error.emit(
                    algorithm_name, "Algorithm returned no result"
                )
                return None

        except Exception as e:
            error_msg = f"Error executing {algorithm_name}: {str(e)}"
            self.processing_error.emit(algorithm_name, error_msg)
            return None

    def execute_super_resolution(
        self,
        algorithm_name: str,
        parameters: Dict[str, Any],
        image_path: str,
        single_process: bool = True,
    ) -> Optional[str]:
        """
        Execute super resolution algorithm.

        Args:
            algorithm_name: Name of super resolution algorithm
            parameters: Algorithm parameters
            image_path: Path to image
            single_process: Whether this is single or batch processing

        Returns:
            Path to result or None if failed
        """
        self.current_config = AlgorithmConfig(
            AlgorithmType.SUPER_RESOLUTION, algorithm_name, parameters
        )

        self.processing_started.emit(algorithm_name)

        try:
            result_path = self._run_super_resolution_algorithm(
                algorithm_name, parameters, single_process
            )

            if result_path:
                self.processing_completed.emit("super_resolution", result_path)
                return result_path
            else:
                self.processing_error.emit(
                    algorithm_name, "Algorithm returned no result"
                )
                return None

        except Exception as e:
            error_msg = f"Error executing {algorithm_name}: {str(e)}"
            self.processing_error.emit(algorithm_name, error_msg)
            return None

    def execute_workflow(
        self,
        alignment_config: Optional[AlgorithmConfig],
        denoising_config: Optional[AlgorithmConfig],
        super_res_config: Optional[AlgorithmConfig],
        image_paths: list,
        single_process: bool = True,
    ) -> Optional[str]:
        """
        Execute complete processing workflow.

        Args:
            alignment_config: Alignment algorithm configuration
            denoising_config: Denoising algorithm configuration
            super_res_config: Super resolution algorithm configuration
            image_paths: List of image paths
            single_process: Whether this is single or batch processing

        Returns:
            Path to final result or None if failed
        """
        self.workflow_started.emit()
        result_path = None

        try:
            # Step 1: Alignment
            if alignment_config and alignment_config.algorithm_name != "No Alignment":
                result_path = self.execute_alignment(
                    alignment_config.algorithm_name,
                    alignment_config.parameters,
                    image_paths,
                    single_process,
                )
                if result_path:
                    self.workflow_step_completed.emit("Alignment")

            # Step 2: Super Resolution
            if (
                super_res_config
                and super_res_config.algorithm_name != "No Super Resolution"
            ):
                result_path = self.execute_super_resolution(
                    super_res_config.algorithm_name,
                    super_res_config.parameters,
                    result_path or image_paths[0],
                    single_process,
                )
                if result_path:
                    self.workflow_step_completed.emit("Super Resolution")

            # Step 3: Denoising
            if denoising_config and denoising_config.algorithm_name != "No Denoising":
                result_path = self.execute_denoising(
                    denoising_config.algorithm_name,
                    denoising_config.parameters,
                    [result_path] if result_path else image_paths,
                    single_process,
                )
                if result_path:
                    self.workflow_step_completed.emit("Denoising")

            if result_path:
                self.workflow_completed.emit(result_path)
            else:
                self.workflow_error.emit("No algorithms were executed")

            return result_path

        except Exception as e:
            error_msg = f"Workflow error: {str(e)}"
            self.workflow_error.emit(error_msg)
            return None

    def _run_alignment_algorithm(
        self, algorithm_name: str, parameters: Dict, single_process: bool
    ) -> Optional[str]:
        """
        Internal method to run alignment algorithm.
        This will import and call the actual algorithm modules.
        """

        # Map algorithm names to functions
        algorithm_map = {
            "ORB": running_orb,
            "AKAZE": running_akaze,
            # "Farneback Optical Flow": running_farneback_flow,
            "Light Glue": running_light_glue,
        }

        algorithm_func = algorithm_map.get(algorithm_name)
        if not algorithm_func:
            raise ValueError(f"Unknown alignment algorithm: {algorithm_name}")

        # Note: The actual algorithm functions expect 'self' (the view object)
        # This will need to be refactored to not depend on view
        # For now, we'll need to pass the view object or refactor the algorithms
        # TODO: Refactor algorithm functions to be pure functions
        return None  # Placeholder

    def _run_denoising_algorithm(
        self, algorithm_name: str, parameters: Dict, single_process: bool
    ) -> Optional[str]:
        """Internal method to run denoising algorithm."""
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
            running_median,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
            running_similarity,
            running_mf_denoiser,
        )

        algorithm_map = {
            "Average": running_mf_denoiser,
            "Median": running_median,
            "Similarity": running_similarity,
        }

        algorithm_func = algorithm_map.get(algorithm_name)
        if not algorithm_func:
            raise ValueError(f"Unknown denoising algorithm: {algorithm_name}")

        # TODO: Refactor algorithm functions
        return None  # Placeholder

    def _run_super_resolution_algorithm(
        self, algorithm_name: str, parameters: Dict, single_process: bool
    ) -> Optional[str]:
        """Internal method to run super resolution algorithm."""
        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.Interpolation import (
            running_interpolation,
        )

        algorithm_map = {"Interpolation": running_interpolation}

        algorithm_func = algorithm_map.get(algorithm_name)
        if not algorithm_func:
            raise ValueError(f"Unknown super resolution algorithm: {algorithm_name}")

        # TODO: Refactor algorithm functions
        return None  # Placeholder

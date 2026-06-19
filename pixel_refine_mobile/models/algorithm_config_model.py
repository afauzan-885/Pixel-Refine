"""
pixel_refine_mobile/models/algorithm_config_model.py
----------------------------------------------------
Algorithm configuration model.
Direct port from desktop — same API, same behavior.
"""

from typing import Dict, Any, Optional
from enum import Enum


class AlgorithmType(Enum):
    """Algorithm types."""
    ALIGNMENT = "alignment"
    DENOISING = "denoising"
    SUPER_RESOLUTION = "super_resolution"


class AlgorithmConfig:
    """Data model for algorithm configuration."""

    def __init__(self, algorithm_type: AlgorithmType, algorithm_name: str,
                 parameters: Optional[Dict[str, Any]] = None):
        self.algorithm_type = algorithm_type
        self.algorithm_name = algorithm_name
        self.parameters = parameters or {}

    def get_parameter(self, key: str, default: Any = None) -> Any:
        return self.parameters.get(key, default)

    def set_parameter(self, key: str, value: Any) -> None:
        self.parameters[key] = value

    def validate(self) -> tuple:
        if not self.algorithm_name:
            return False, "Algorithm name is required"
        if not isinstance(self.algorithm_type, AlgorithmType):
            return False, "Invalid algorithm type"
        return True, None

    def to_dict(self) -> Dict:
        return {
            'algorithm_type': self.algorithm_type.value,
            'algorithm_name': self.algorithm_name,
            'parameters': self.parameters
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AlgorithmConfig':
        algorithm_type = AlgorithmType(data.get('algorithm_type', 'alignment'))
        return cls(
            algorithm_type=algorithm_type,
            algorithm_name=data.get('algorithm_name', ''),
            parameters=data.get('parameters', {})
        )

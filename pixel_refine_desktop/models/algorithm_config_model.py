"""
Algorithm configuration model.
Represents algorithm settings and parameters.
"""

from typing import Dict, Any, Optional
from enum import Enum


class AlgorithmType(Enum):
    """Algorithm types."""
    ALIGNMENT = "alignment"
    DENOISING = "denoising"
    SUPER_RESOLUTION = "super_resolution"


class AlgorithmConfig:
    """
    Data model for algorithm configuration.
    Stores algorithm selection and parameters.
    """
    
    def __init__(self, algorithm_type: AlgorithmType, algorithm_name: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize algorithm configuration.
        
        Args:
            algorithm_type: Type of algorithm
            algorithm_name: Name of the algorithm
            parameters: Algorithm parameters
        """
        self.algorithm_type = algorithm_type
        self.algorithm_name = algorithm_name
        self.parameters = parameters or {}
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """
        Get a parameter value.
        
        Args:
            key: Parameter name
            default: Default value if not found
            
        Returns:
            Parameter value or default
        """
        return self.parameters.get(key, default)
    
    def set_parameter(self, key: str, value: Any) -> None:
        """
        Set a parameter value.
        
        Args:
            key: Parameter name
            value: Parameter value
        """
        self.parameters[key] = value
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.algorithm_name:
            return False, "Algorithm name is required"
        
        if not isinstance(self.algorithm_type, AlgorithmType):
            return False, "Invalid algorithm type"
        
        return True, None
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'algorithm_type': self.algorithm_type.value,
            'algorithm_name': self.algorithm_name,
            'parameters': self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AlgorithmConfig':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with config data
            
        Returns:
            AlgorithmConfig instance
        """
        algorithm_type = AlgorithmType(data.get('algorithm_type', 'alignment'))
        return cls(
            algorithm_type=algorithm_type,
            algorithm_name=data.get('algorithm_name', ''),
            parameters=data.get('parameters', {})
        )
    
    def __repr__(self) -> str:
        return f"AlgorithmConfig({self.algorithm_type.value}: {self.algorithm_name})"

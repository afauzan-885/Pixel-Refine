"""
Image data model.
Represents an image entity with validation.
"""

import os
from typing import Optional, Dict


class ImageModel:
    """
    Data model for an image.
    Provides validation and serialization.
    """
    
    def __init__(self, id: Optional[int] = None, path: str = "", is_reference: bool = False):
        """
        Initialize image model.
        
        Args:
            id: Database ID (None for new images)
            path: File path
            is_reference: Whether this is a reference image
        """
        self.id = id
        self.path = path
        self.is_reference = is_reference
    
    @property
    def exists(self) -> bool:
        """Check if image file exists on disk."""
        return os.path.exists(self.path) if self.path else False
    
    @property
    def filename(self) -> str:
        """Get filename without path."""
        return os.path.basename(self.path) if self.path else ""
    
    @property
    def extension(self) -> str:
        """Get file extension."""
        return os.path.splitext(self.path)[1].lower() if self.path else ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate image data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.path:
            return False, "Image path is required"
        
        if not os.path.isabs(self.path):
            return False, "Image path must be absolute"
        
        return True, None
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'path': self.path,
            'is_reference': self.is_reference,
            'exists': self.exists,
            'filename': self.filename,
            'extension': self.extension
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ImageModel':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with image data
            
        Returns:
            ImageModel instance
        """
        return cls(
            id=data.get('id'),
            path=data.get('path', ''),
            is_reference=data.get('is_reference', False)
        )
    
    @classmethod
    def from_db_row(cls, row: tuple) -> 'ImageModel':
        """
        Create from database row.
        
        Args:
            row: Tuple from database query (id, path) or (id, path, is_reference)
            
        Returns:
            ImageModel instance
        """
        if len(row) >= 3:
            return cls(id=row[0], path=row[1], is_reference=bool(row[2]))
        elif len(row) >= 2:
            return cls(id=row[0], path=row[1])
        else:
            raise ValueError("Invalid database row format")
    
    def __repr__(self) -> str:
        ref_str = " (ref)" if self.is_reference else ""
        return f"ImageModel(id={self.id}, path='{self.filename}'{ref_str})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, ImageModel):
            return False
        return self.path == other.path
    
    def __hash__(self) -> int:
        return hash(self.path)

"""
Batch data model.
Represents a batch entity with images and validation.
"""

from typing import Optional, List, Dict
from .image_model import ImageModel


class BatchModel:
    """
    Data model for a batch.
    Manages batch data, images, and reference image.
    """
    
    def __init__(self, id: Optional[int] = None, name: str = "", images: Optional[List[ImageModel]] = None):
        """
        Initialize batch model.
        
        Args:
            id: Database ID (None for new batches)
            name: Batch name
            images: List of ImageModel instances
        """
        self.id = id
        self.name = name
        self.images = images or []
    
    @property
    def reference_image(self) -> Optional[ImageModel]:
        """Get the reference image for this batch."""
        for img in self.images:
            if img.is_reference:
                return img
        return None
    
    @property
    def image_count(self) -> int:
        """Get number of images in batch."""
        return len(self.images)
    
    @property
    def has_reference(self) -> bool:
        """Check if batch has a reference image."""
        return self.reference_image is not None
    
    def add_image(self, image: ImageModel) -> None:
        """
        Add an image to the batch.
        
        Args:
            image: ImageModel to add
        """
        if image not in self.images:
            # If no reference exists, make this the reference
            if not self.has_reference:
                image.is_reference = True
            self.images.append(image)
    
    def remove_image(self, image: ImageModel) -> bool:
        """
        Remove an image from the batch.
        
        Args:
            image: ImageModel to remove
            
        Returns:
            True if removed, False if not found
        """
        try:
            was_reference = image.is_reference
            self.images.remove(image)
            
            # If reference was removed and there are still images, set new reference
            if was_reference and self.images:
                self.images[0].is_reference = True
            
            return True
        except ValueError:
            return False
    
    def set_reference(self, image: ImageModel) -> bool:
        """
        Set an image as the reference.
        
        Args:
            image: ImageModel to set as reference
            
        Returns:
            True if successful, False if image not in batch
        """
        if image not in self.images:
            return False
        
        # Reset all references
        for img in self.images:
            img.is_reference = False
        
        # Set new reference
        image.is_reference = True
        return True
    
    def get_image_paths(self) -> List[str]:
        """
        Get list of all image paths.
        
        Returns:
            List of image file paths
        """
        return [img.path for img in self.images]
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate batch data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.name:
            return False, "Batch name is required"
        
        if not self.images:
            return False, "Batch must contain at least one image"
        
        # Validate all images
        for img in self.images:
            is_valid, error = img.validate()
            if not is_valid:
                return False, f"Invalid image: {error}"
        
        # Check that exactly one reference exists
        ref_count = sum(1 for img in self.images if img.is_reference)
        if ref_count == 0:
            return False, "Batch must have a reference image"
        if ref_count > 1:
            return False, "Batch can only have one reference image"
        
        return True, None
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'image_count': self.image_count,
            'has_reference': self.has_reference,
            'reference_image': self.reference_image.to_dict() if self.reference_image else None,
            'images': [img.to_dict() for img in self.images]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BatchModel':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with batch data
            
        Returns:
            BatchModel instance
        """
        images = [ImageModel.from_dict(img_data) for img_data in data.get('images', [])]
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            images=images
        )
    
    def __repr__(self) -> str:
        return f"BatchModel(id={self.id}, name='{self.name}', images={self.image_count})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BatchModel):
            return False
        return self.id == other.id if self.id else self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.id) if self.id else hash(self.name)

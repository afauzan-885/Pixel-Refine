import numpy as np
import cv2
from scipy.ndimage import fourier_shift

def subpixel_l2_alignment(ref_image, target_image, tile_size=16, search_radius=8, subpixel=True):
    """
    Subpixel L2 Alignment for aligning two images.

    Parameters:
    - ref_image: np.ndarray
        Reference image.
    - target_image: np.ndarray
        Target image to align with the reference.
    - tile_size: int
        Size of the tiles for local alignment.
    - search_radius: int
        Maximum displacement (in pixels) to search around each tile.
    - subpixel: bool
        Whether to enable subpixel alignment refinement.

    Returns:
    - aligned_image: np.ndarray
        Target image aligned to the reference image.
    - displacement_field: np.ndarray
        Displacement field showing the offset for each tile.
    """
    # Ensure images are grayscale and have the same dimensions
    ref_image = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY) if ref_image.ndim == 3 else ref_image
    target_image = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY) if target_image.ndim == 3 else target_image
    assert ref_image.shape == target_image.shape, "Input images must have the same dimensions"

    height, width = ref_image.shape
    displacement_field = np.zeros((height // tile_size, width // tile_size, 2), dtype=np.float32)

    # Iterate over tiles
    aligned_image = np.zeros_like(target_image)
    for i in range(0, height, tile_size):
        for j in range(0, width, tile_size):
            # Define tile bounds
            tile_ref = ref_image[i:i + tile_size, j:j + tile_size]
            tile_target = target_image[i:i + tile_size, j:j + tile_size]

            # Pad tiles to search radius
            pad_size = search_radius + tile_size
            padded_target = np.pad(tile_target, pad_size, mode='constant')

            # Find the best match using L2 norm
            min_error = float('inf')
            best_offset = (0, 0)
            for dx in range(-search_radius, search_radius + 1):
                for dy in range(-search_radius, search_radius + 1):
                    tile_search = padded_target[pad_size + dy:pad_size + dy + tile_size,
                                                pad_size + dx:pad_size + dx + tile_size]
                    error = np.sum((tile_ref - tile_search) ** 2)
                    if error < min_error:
                        min_error = error
                        best_offset = (dx, dy)

            # Subpixel refinement (optional)
            if subpixel:
                x, y = np.meshgrid(range(tile_size), range(tile_size))
                shifts = np.stack([x + best_offset[0], y + best_offset[1]])
                interpolated_offset = np.polyfit(shifts.ravel(), tile_ref.ravel(), 2)
                refined_dx = interpolated_offset[0] + best_offset[0]
                refined_dy = interpolated_offset[1] + best_offset[1]
                best_offset = (refined_dx, refined_dy)

            displacement_field[i // tile_size, j // tile_size] = best_offset

            # Align tile
            shift = fourier_shift(np.fft.fftn(tile_target), best_offset)
            aligned_tile = np.abs(np.fft.ifftn(shift))

            # Copy aligned tile to output image
            aligned_image[i:i + tile_size, j:j + tile_size] = aligned_tile[:tile_size, :tile_size]

    return aligned_image, displacement_field

# Example usage
if __name__ == "__main__":
    ref_img = cv2.imread("reference.jpg", cv2.IMREAD_GRAYSCALE)
    target_img = cv2.imread("target.jpg", cv2.IMREAD_GRAYSCALE)

    aligned_img, displacement = subpixel_l2_alignment(ref_img, target_img, tile_size=32, search_radius=10)

    cv2.imshow("Aligned Image", aligned_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

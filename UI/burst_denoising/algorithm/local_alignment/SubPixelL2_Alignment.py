import numpy as np
from scipy.fftpack import fft2, ifft2
from scipy.ndimage import gaussian_filter

class SubpixelL2Alignment:
    def __init__(self, tile_size=16, pyramid_levels=3, subpixel_method='quadratic'):
        """
        Initialize the Subpixel L2 Alignment class.

        Parameters:
        - tile_size (int): Size of each tile for local alignment.
        - pyramid_levels (int): Number of pyramid levels for coarse-to-fine alignment.
        - subpixel_method (str): Method for subpixel refinement ('quadratic' or 'spline').
        """
        self.tile_size = tile_size
        self.pyramid_levels = pyramid_levels
        self.subpixel_method = subpixel_method

    def _compute_l2_displacement(self, ref_tile, alt_tile):
        """
        Compute displacement using FFT-based cross-correlation.

        Parameters:
        - ref_tile (ndarray): Reference tile.
        - alt_tile (ndarray): Alternate tile to align.

        Returns:
        - displacement (tuple): Displacement (dy, dx) with subpixel accuracy.
        """
        fft_ref = fft2(ref_tile)
        fft_alt = fft2(alt_tile)
        cross_power_spectrum = fft_ref * np.conj(fft_alt)
        cross_correlation = ifft2(cross_power_spectrum / (np.abs(cross_power_spectrum) + 1e-8)).real
        
        max_idx = np.unravel_index(np.argmax(cross_correlation), cross_correlation.shape)
        dy, dx = max_idx[0] - ref_tile.shape[0] // 2, max_idx[1] - ref_tile.shape[1] // 2

        if self.subpixel_method == 'quadratic':
            dy, dx = self._quadratic_interpolation(cross_correlation, max_idx)

        return dy, dx

    def _quadratic_interpolation(self, cross_corr, max_idx):
        """
        Perform quadratic interpolation for subpixel accuracy.

        Parameters:
        - cross_corr (ndarray): Cross-correlation matrix.
        - max_idx (tuple): Index of the peak in cross-correlation.

        Returns:
        - subpixel_displacement (tuple): Subpixel displacement (dy, dx).
        """
        y, x = max_idx
        size_y, size_x = cross_corr.shape

        if 0 < y < size_y - 1 and 0 < x < size_x - 1:
            dy = (cross_corr[y + 1, x] - cross_corr[y - 1, x]) / (2 * (2 * cross_corr[y, x] - cross_corr[y + 1, x] - cross_corr[y - 1, x]))
            dx = (cross_corr[y, x + 1] - cross_corr[y, x - 1]) / (2 * (2 * cross_corr[y, x] - cross_corr[y, x + 1] - cross_corr[y, x - 1]))
        else:
            dy, dx = 0, 0

        return y + dy - size_y // 2, x + dx - size_x // 2

    def _build_pyramid(self, image):
        """
        Build a Gaussian pyramid for the image.

        Parameters:
        - image (ndarray): Input image.

        Returns:
        - pyramid (list): List of images at different resolutions.
        """
        pyramid = [image]
        for _ in range(1, self.pyramid_levels):
            image = gaussian_filter(image, sigma=1)[::2, ::2]
            pyramid.append(image)
        return pyramid

    def align(self, ref_image, alt_image):
        """
        Align two images using Subpixel L2 Alignment.

        Parameters:
        - ref_image (ndarray): Reference image.
        - alt_image (ndarray): Alternate image to align.

        Returns:
        - aligned_image (ndarray): Aligned alternate image.
        - displacement (list): List of displacements [(dy, dx)] for each tile.
        """
        ref_pyramid = self._build_pyramid(ref_image)
        alt_pyramid = self._build_pyramid(alt_image)

        displacement = []
        for level in range(self.pyramid_levels - 1, -1, -1):
            ref = ref_pyramid[level]
            alt = alt_pyramid[level]

            tiles_y = ref.shape[0] // self.tile_size
            tiles_x = ref.shape[1] // self.tile_size

            for i in range(tiles_y):
                for j in range(tiles_x):
                    y_start = i * self.tile_size
                    x_start = j * self.tile_size

                    ref_tile = ref[y_start:y_start + self.tile_size, x_start:x_start + self.tile_size]
                    alt_tile = alt[y_start:y_start + self.tile_size, x_start:x_start + self.tile_size]

                    dy, dx = self._compute_l2_displacement(ref_tile, alt_tile)
                    displacement.append((dy, dx))

        # Transform the alternate image (this step requires further implementation)
        aligned_image = alt_image  # Placeholder for actual transformation

        return aligned_image, displacement

# Example usage:
if __name__ == "__main__":
    ref_image = np.random.rand(128, 128)
    alt_image = np.roll(ref_image, shift=(5, -3), axis=(0, 1))  # Example shifted image

    aligner = SubpixelL2Alignment(tile_size=16, pyramid_levels=3, subpixel_method='quadratic')
    aligned_image, displacements = aligner.align(ref_image, alt_image)

    print("Displacements:", displacements)

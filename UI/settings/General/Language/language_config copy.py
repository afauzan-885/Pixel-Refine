# Main Content
UNDER_DEVELOPMENT = "{page_name} menu under development"

# Enhance Stack Page
TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "Import Image"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "Delete Image"

PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Start Process"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Save As"

HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "Image Files (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Select Images"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Duplicate Files"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} file(s) already exist in the database and will be skipped."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Selected Format"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} file(s) with format '{format}' will be imported."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Error", "No valid files to import."

HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Error", "No images selected."
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Are you sure you want to delete the {count} selected image(s)?"

UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Processing images, please wait..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "No images selected."

UPDATE_PROGRESS_BAR_STATUS = "{value}% ({images_left} process)"

ON_IMPORT_COMPLETE_STATUS = "Import complete"
ON_IMPORT_COMPLETE_MESSAGES = "{successful_images} images have been successfully imported."

PROCESS_ALGORITHM_PROCESS_SKIPPED = "No algorithm selected for processing"

# PARAMETER STACKING 
NOT_IMAGE_PREVIEW = "No images available"
MODULE_NOT_IMPLEMENT = "Module not yet implemented."
NO_ALIGNMENT_PROCESS = "Are you sure you don't want image alignment first?."

# General message
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Failed to load image"

SAVE_TO_HDF5_ALIGNED_SAVING = "Saving aligned image to HDF5"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "The {index}th image is stored in HDF5."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "All images were successfully saved to HDF5."
RESIZING_IMAGES_PROCESS = "Adjusting image size"

RUN_IMAGE_NOT_FOUND = "No images found in the database."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Reference image could not be loaded from {image_paths[0]}."
RUN_SAVING_REFERENCE_IMAGE = "Saving reference image to HDF5."
RUN_IMAGE_PROCESSING = "Processing image {i} of {total_images}..."
RUN_IMAGE_PROCESSING_FAILED = "Failed to load image {i} from {image_paths[i]}."
RUN_IMAGE_PROCESSING_SAVING = "The {i}th image is saved in HDF5."
RUN_IMAGE_PROCESSING_FINISHED = "Process Complete."

CANCEL_PROCESSING = "Are you sure you want to cancel the process?"

RUN_ERROR_STATUS = "An error occurred: {error}"
RUN_ERROR_MESSAGE = "An error occurred: {error}"

WINDOW_INITIATION = "Start..."
WINDOW_START_PROCESSING = "Starting processing..."
WINDOW_PROCESSING_COMPLETE = "Complete!"


# Farnerback Optical Flow
WINDOW_TITLE_FARNEBACK = "Farneback Optical Flow Alignment"

CALCULATE_OPTICAL_FLOW_STATUS = "Calculating optical flow using{device}..."
CALCULATE_OPTICAL_FLOW_FINISHED = "Optical flow calculation is complete."

COMPENSATE_MOTION_STATUS = "Performing motion compensation on the image {image_id}..."
COMPENSATE_MOTION_FINISHED = "Motion compensation completed for image {image_id}."



# AKAZE, ORB
WINDOW_TITLE_AKAZE = "AKAZE Alignment"
ALIGN_IMAGES_STATUS_AKAZE = "Aligning images {image_id} using AKAZE..."

WINDOW_TITLE_ORB = "ORB Alignment"
ALIGN_IMAGES_STATUS_ORB = "Aligning images {image_id} using ORB..."

ALIGN_IMAGES_CALCULATE_FAILED = "No features detected in any of the images for {image_id}. Returning original image."
ALIGN_IMAGES_CALCULATE_FINISHED = "Alignment complete for image {image_id}."
ALIGN_IMAGES_COMPENSATE_FAILED = "Homography could not be computed for image {image_id}. Returning original image."
ALIGN_IMAGES_MATCHING_FAILED = "Insufficient number of matches for image {image_id}. Returning original image."



# Algorithm Denoising
STACK_IMAGES_FAILED = "No images to process."
STACK_IMAGES_PROCESS = "Processing image {current}/{total}..."

RUN_IMAGE_PROCESS_STARTED = "Starting process..."
RUN_IMAGE_PROCESS_LOAD_HDF5 = "Loading images from HDF5..."
RUN_IMAGE_PROCESS_LOAD_PROGRESS = "Loading image {current}/{total}..."

RUN_IMAGE_PROCESS_LOAD_PATH = "Fetching image list from database..."
RUN_IMAGE_PROCESS_LOAD_FAILED = "No images found in the database."
RUN_IMAGE_PROCESS_STACK_SUCCESS = "Image stacking complete! Results saved at: {output_path}"

WINDOW_PROCESS_SUCCESS = "The process has been completed."

# Average, Median, Similarity Stacking
WINDOW_TITLE_AVERAGE = "Average Stacking"
WINDOW_TITLE_MEDIAN = "Median Stacking"
WINDOW_TITLE_WEIGHTED_AVERAGE = "Weighted Average Stacking"

WINDOW_TITLE_SIMILARITY = "Similarity Stacking"
IMAGE_LOAD_FAILED = "No images provided."
IMAGE_BIT_REQUIRED = "Images must be 8 Bit or 16 Bit."
SIMILARITY_MNFR_TILE_SLICE = "Image dimensions: {height}x{width}, Tile size: {tile_size}"
SIMILARITY_MNFR_SIZE_FAILED = "Image size {i} does not match the reference image."
IMAGE_PROCESS_IN_PROGRESS_SUCCESS = "Image {i}/{count} processed successfully."
IMAGE_PROCESS_FINISHED = "Stacking complete."
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Stacking batch to {current} from {total}"


# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Interpolation Super Resolution"

# ------------ Parameter Setting Algorithm --------------------- #
DEFAULT_PARAMETER_SETTING_LABEL = "Select an algorithm to view parameter settings."

# ORB Parameters
ORB_PARAMETER_SETTING_LABEL = "ORB Parameters"
ORB_NFEATURES_LABEL = "Number of Features"
ORB_NFEATURES_DESCRIPTION = """The number of features represents the amount of fine detail that can be recognized in an image.

A higher number of features enables the algorithm to identify more details, resulting in more precise image alignment.
However, detecting more features increases computation time.

Typically, a value between 500 and 1500 is sufficient for most applications.
For very high accuracy requirements, selecting a value between 2500 to 5000 might improve precision."""

ORB_SCALEFACTOR_LABEL = "Scale Factor"
ORB_SCALEFACTOR_DESCRIPTION = """Scale factor determines the rate at which the image is downscaled iteratively during processing.

- A value close to 1.0 means the image is downscaled gradually (more steps), allowing for finer detail detection but taking longer.
- A higher value downsamples the image more rapidly, leading to faster processing but potentially missing some fine details.

Common values range from 1.2 to 1.5."""

ORB_NLEVELS_LABEL = "Number of Levels"
ORB_NLEVELS_DESCRIPTION = """The number of levels indicates the layers in the image pyramid used for feature detection.

More levels enable the algorithm to capture details at various scales, which is beneficial when images vary in size,
but increased levels also mean longer processing times.

Typically, a value between 2 and 4 is ideal for most applications."""

ORB_TRANSFORMATION_LABEL = "Transformation Type"
ORB_TRANSFORMATION_DESCRIPTION = """Transformation Type determines the method used to align images.

Available options include:
- Homography: Allows perspective transformation, ideal for images taken from different angles.
- Affine: Permits rotation, scaling, and translation (shifting).
- Similarity: Only permits rotation, uniform scaling, and translation, preserving the image's aspect ratio.
- Euclidean: Only permits rotation and translation without scaling, offering the simplest option.

The choice of transformation depends on the differences among the images to be aligned. 
For most applications, Homography is often selected due to its flexibility in handling perspective differences."""

ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """The RANSAC Threshold determines how stringently the algorithm filters out outliers during image alignment.

- A lower value (e.g., 1-2) enforces stricter filtering, potentially discarding some key features.
- A higher value (e.g., 4-5) is more tolerant of outliers, allowing more features to be used but possibly reducing alignment precision.

Typically, a value between 1 and 3 is sufficient, depending on the noise level in the data."""


# Farneback Optical Flow
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback Parameters"

FARNEBACK_PYRAMID_SCALE_LABEL = "Pyramid Scale"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """The Pyramid Scale is the factor by which the image is reduced at each level of the pyramid.

- This value determines how much the image size is decreased from one level to the next.
  For example, if the value is 0.5, then each level will have half the size of the previous level.

- Smaller values (e.g., between 0.10 and 0.5) produce a larger size difference between levels,
  which can speed up the computation but may reduce the accuracy in capturing fine motion details.

- Values close to 1.00 produce minimal size changes between levels, allowing for more accurate motion detail capture,
  but require longer computational time.

Adjust this value according to your needs for a balance between processing speed and motion detection accuracy.
Recommended value: 0.5.
"""

FARNEBACK_LEVELS_LABEL = "Levels"
FARNEBACK_LEVELS_DESCRIPTION = """Levels determine the number of levels in the image pyramid used for optical flow computation.

- More levels allow the algorithm to detect motion at various scales, which is beneficial when the motion in the image is complex or covers a large area.
- However, increasing the number of levels also increases the computational time.

Typically, a value of 3 is used as a benchmark, but you can set it anywhere from 1 to 10 depending on your application's needs.
Recommended value: 3.
"""

FARNEBACK_WIN_SIZE_LABEL = "Window Size"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Window Size is the size of the pixel region (window) used to compute the optical flow.

- A larger window produces a more stable and smooth result by averaging information over a wider area.
- However, if the window is too large, it may obscure small motion details.

Choose a value that balances smoothness with sensitivity to fine details.
Recommended value: 15.
"""

FARNEBACK_ITERATIONS_LABEL = "Iterations"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterations specify how many times the optical flow calculation is refined at each pyramid level.

- More iterations yield a more accurate optical flow result.
- However, increasing iterations also increases the computational time.

Select a value that improves accuracy without significantly slowing down the process.
Recommended value: 3.
"""

FARNEBACK_POLY_N_LABEL = "Polynomial Expansion"
FARNEBACK_POLY_N_DESCRIPTION = """Polynomial Expansion (poly_n) defines the size of the pixel neighborhood used to estimate motion via polynomial expansion.

- This value determines how much of the surrounding pixel data is used for the calculation.
- Larger values produce smoother estimates but may reduce sensitivity to small motions.

Commonly used values are typically 5 or 7, depending on the desired level of detail and stability.
Recommended values: 5 or 7.
"""

FARNEBACK_POLY_SIGMA_LABEL = "Polynomial Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Polynomial Sigma controls the amount of smoothing applied before performing the polynomial expansion.

- It represents the standard deviation of the Gaussian filter applied to reduce noise in the pixel data.
- A higher sigma value can help reduce noise, but if set too high, important motion details may be lost.

Adjust this value to reduce noise without sacrificing significant motion details.
Recommended value: 1.2.
"""

FARNEBACK_FLAGS_LABEL = "Flags"
FARNEBACK_FLAGS_DESCRIPTION = """Flags are optional parameters that enable specific options in the Farneback algorithm.

- For example, a common flag is the use of a Gaussian filter for smoothing, which can produce a smoother optical flow.
- If you are not sure, this parameter is usually left at its default value (0).

Choose the appropriate flag if you wish to optimize the trade-off between processing speed and result quality.
Recommended value: 0.
"""

FARNEBACK_INTERPOLATION_LABEL = "Interpolation"
FARNEBACK_INTERPOLATION_DESCRIPTION = """Interpolation sets the method used to estimate optical flow values between pixels.

- Higher-quality interpolation methods (e.g., linear or cubic) can produce smoother motion transitions.
- However, more complex methods may also increase computational time.

Choose an interpolation method that balances smoothness and processing efficiency.
Recommended: Cubic Interpolation.
"""

AKAZE_PARAMETER_SETTING_LABEL = "AKAZE Parameters"

AKAZE_THRESHOLD_LABEL = "Threshold"
AKAZE_THRESHOLD_DESCRIPTION = """The Threshold parameter sets the minimum detector response required to accept a keypoint.

Lower values allow more keypoints to be detected (including weaker or noisy ones), 
while higher values restrict detection to only the strongest features. 

Recommended value: around 30."""

AKAZE_OCTAVE_LABEL = "Number of Octaves"
AKAZE_OCTAVE_DESCRIPTION = """This parameter specifies the number of octaves in the scale space. 

Each octave represents a halved resolution of the original image, allowing the detector to capture 
features at multiple scales. More octaves improve scale invariance but increase computational time. 

Recommended value: 4."""

AKAZE_LAYER_LABEL = "Layers per Octave"
AKAZE_LAYER_DESCRIPTION = """Layers per Octave defines the number of sub-levels within each octave. 

A higher number of layers provides a finer scale-space resolution, which can improve feature detection 
across scales, but it also increases computation. 

Recommended value: 4."""

AKAZE_RATIO_LABEL = "Ratio Threshold"
AKAZE_RATIO_DESCRIPTION = """The Ratio Threshold is used during the matching process to compare the distance of the best match 
to the second-best match for a keypoint's descriptor.

A lower ratio (closer to 0.50) means only highly distinctive, 
unambiguous matches are accepted, while a higher ratio (closer to 1.00) allows more matches 
but may include false positives. 

Recommended value: 0.80."""


APPLY_PARAMETER_BUTTON_TEXT = "Apply Settings"

# ------------ Parameter Setting Algorithm --------------------- #




# Deskripsi untuk Alignment Algorithm
ALIGNMENT_NAME = "Alignment Algorithm"
NONE_ALIGNMENT_DESCRIPTION = "No alignment will be applied."
FARNEBACK_DESCRIPTION = """This algorithm is suitable for high-level alignment that requires
precision and accuracy down to the pixel level.

But very weak against significant rotation and perspective differences"""
AKAZE_DESCRIPTION = """This algorithm is quite robust to large differences in rotation, perspective and scale

Good enough but not as good as farneback for pixel level"""
ORB_DESCRIPTION = """Fast algorithm but less accurate for significant differences

Suitable for images with minimal differences"""

# Deskripsi untuk Super Resolution
SUPER_RESOLUTION_NAME = "Super Resolution Algorithm"
NONE_SUPER_RESOLUTION_DESCRIPTION = "No super-resolution will be applied."
INTERPOLATION_DESCRIPTION = """A simple algorithm to increase resolution by interpolation, adding a little detail."""

# Deskripsi untuk Denoising
DENOISING_NAME = "Denoising Algorithm"
NONE_DENOISING_DESCRIPTION = "No noise reduction will be applied."
WEIGHTED_AVERAGE_DESCRIPTION = """The result of the simplification of the similarity stacking method is quite good for small movements

Quite good at dealing with small movements, but produces image artifacts in larger movements"""

AVERAGE_DESCRIPTION = """Very fast and effective stacking method for static objects and scenes

Not suitable for moving scenes or areas but can be combined with farneback alignment
to eliminate slight object movement."""

MEDIAN_DESCRIPTION = """Fast and effective for stacking, quite good on moving objects

Very effective at removing object movement up to 12 frames, but artifacts appear on moving
objects after that"""

SIMILARITY_DESCRIPTION = """Advanced stacking algorithm, very powerful in removing object movement (no ghosting in moving areas)
and very few artifacts produced up to 90%

Inspired by:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""
                        
                        
                        
# ------------------ Language Configuration ------------------ #

LANGUAGE_LABEL_ENGLISH = "Language"
LANGUAGE_LABEL_INDONESIA = "Bahasa"
LANGUAGE_LABEL_MELAYU = "Bahasa"
LANGUAGE_LABEL_FRENCH = "Langue"
LANGUAGE_LABEL_SPANISH = "Idioma"

# ------------------ Language Configuration ------------------ #
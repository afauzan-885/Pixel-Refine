# Main Content
UNDER_DEVELOPMENT = "Menu {page_name} is under development"

# Sidebar
SETTINGS_SIDEBAR_LABEL= "Settings"
HDR_SIDEBAR_LABEL= "HDR Reconstruction"

# Enhance Stack Page
TOPBAR_IMPORT_BUTTON_TEXT = "Import Image"
TOPBAR_DELETE_BUTTON_TEXT = "Delete Image"

PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Start Process"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Save As"

HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "Image Files (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Select Image"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Duplicate Image"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} images already exist in the database and will be skipped."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Selected Format"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} images with the '{format}' format will be imported."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Error", "No valid images selected for import."

HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Error", "No images selected."
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Are you sure you want to delete the {count} selected images?"

PREVIEW_PANEL_LABEL = "Preview Panel"

UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Processing image, please wait..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "No image selected."

UPDATE_PROGRESS_BAR_STATUS = "{value}% ({images_left} images remaining)"

ON_IMPORT_COMPLETE_STATUS = "Import complete"
ON_IMPORT_COMPLETE_MESSAGES = "{successful_images} images have been successfully imported."

PROCESS_ALGORITHM_PROCESS_SKIPPED = "No algorithm selected for processing"


# PARAMETER STACKING 
NOT_IMAGE_PREVIEW = "No images available"
MODULE_NOT_IMPLEMENT = "Module not implemented."
NO_ALIGNMENT_PROCESS = "Are you sure you don't want to align the images first?"

# General message
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Failed to load images"

SAVE_TO_HDF5_ALIGNED_SAVING = "Saving aligned images"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Image number {index} has been saved."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "All images have been successfully saved."

RUN_IMAGE_NOT_FOUND = "Image not found in the database."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Reference image cannot be loaded from {image_paths[0]}."
RUN_SAVING_REFERENCE_IMAGE = "Saving reference image."
RUN_IMAGE_PROCESSING = "Processing image {i} of {total_images}..."
RUN_IMAGE_PROCESSING_FAILED = "Failed to load image {i} from {image_paths[i]}."
RUN_IMAGE_PROCESSING_SAVING = "Image number {i} has been saved."
RUN_IMAGE_PROCESSING_FINISHED = "Process completed."

FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "Unable to calculate global motion for image {}"
FAIL_COMPENSATE_MOTION_PROCESS = "Motion compensation estimation failed for image {}"
UNRECOGNIZED_TRANSFORMATION = "Transformation type not recognized."
FAILED_TO_COMPUTE_TRANSFORMATION ="Transformation could not be computed."
FAILED_TO_COMPUTE_CROP = "Failed to compute valid crop. Process aborted."
FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "Transformation matrix file not found for image {}"
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS = "Aligning and cropping image {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION = "Saving image {}/{}"

FAIL_CROPPING_PROCESS = "Invalid crop: insufficient overlap"

CANCEL_PROCESSING = "Are you sure you want to cancel the process?"

RUN_ERROR_STATUS = "An error occurred: {error}"
RUN_ERROR_MESSAGE = "An error occurred: {error}"

WINDOW_START_PROCESSING = "Starting process..."
WINDOW_PROCESSING_COMPLETE = "Complete!"


# Farneback Optical Flow
WINDOW_TITLE_FARNEBACK = "Farneback Optical Flow Alignment"

COMPENSATE_MOTION_STATUS = "Performing motion compensation on image {image_id}..."
COMPENSATE_MOTION_FINISHED = "Motion compensation completed for image {image_id}."

# AKAZE, ORB
WINDOW_TITLE_AKAZE = "AKAZE Alignment"
WINDOW_TITLE_ORB = "ORB Alignment"

# Algorithm Denoising
STACK_IMAGES_FAILED = "No images available for processing."
STACK_IMAGES_PROCESS = "Processing image {current}/{total}..."

RUN_IMAGE_PROCESS_STARTED = "Starting process..."
RUN_IMAGE_PROCESS_LOAD_FAILED = "No images found in the database."
RUN_IMAGE_PROCESS_STACK_SUCCESS = "Image stacking completed! Results saved at: {output_path}"

# Average, Median, Similarity Stacking
WINDOW_TITLE_AVERAGE = "Average Stacking"
WINDOW_TITLE_MEDIAN = "Median Stacking"
WINDOW_TITLE_WEIGHTED_AVERAGE = "Weighted Average Stacking"

WINDOW_TITLE_SIMILARITY = "Similarity Stacking"
SIMILARITY_MNFR_LOAD_FAILED = "No images provided."
SIMILARITY_MNFR_BIT_REQUIRED = "Images must be either 8-bit or 16-bit."
SIMILARITY_MNFR_PROCESS_FINISHED = "Stacking completed."
SIMILARITY_MNFR_PROCESS = "Stacking in progress {}/{}"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Batch stacking {current} of {total}"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Super Resolution Interpolation"

# ------------ Parameter Setting Algorithm --------------------- #
DEFAULT_PARAMETER_SETTING_LABEL = """Select an algorithm to view its parameters."""

# ORB Parameters
ORB_PARAMETER_SETTING_LABEL = "ORB Parameters"
ORB_NFEATURES_LABEL = "Number of Features"
ORB_NFEATURES_DESCRIPTION = """This parameter determines how many subtle details can be detected in an image.

A higher number of features enables the algorithm to capture more details,
resulting in more precise image alignment, though it increases computation time.

Typically, a value between 500 and 1500 is sufficient for most scenes.
For extremely high accuracy, choosing a value between 2500 and 5000 may further improve precision."""
 
ORB_SCALEFACTOR_LABEL = "Scale Factor"
ORB_SCALEFACTOR_DESCRIPTION = """The Scale Factor determines the rate at which the image is progressively downscaled during processing.

- If the value is close to 1.0, the image is reduced gradually in more steps,
  allowing for finer detail detection but taking longer to process.

- If the value is larger, the image is downscaled more rapidly,
  resulting in shorter processing time, though some small details might be missed.

Typically, the Scale Factor ranges between 1.2 and 1.5."""
 
ORB_NLEVELS_LABEL = "Number of Levels"
ORB_NLEVELS_DESCRIPTION = """This parameter specifies the number of layers in the image pyramid used for feature detection.

- More levels allow the algorithm to capture details at various scales, which is useful when image sizes vary.
  
- However, increasing the number of levels also lengthens processing time.

For most scenes, a value between 2 and 4 is considered ideal."""

ORB_TRANSFORMATION_LABEL = "Transformation Type"
ORB_TRANSFORMATION_DESCRIPTION = """Choose a method to align the image according to your needs:

Available options include:
- HOMOGRAPHIC: Suitable for photos with quite extreme angle differences (e.g., a table from above vs. the side).

Can adjust the "perspective" effect.

- Afine: Can rotate, resize (can be non-uniform), and pan the image.
Example: fixing a tilted photo that needs to be enlarged partially.

- Similarity: Only allow rotation, uniform zooming/reducing, and panning.
aspect ratio is maintained.

- Euclidean: The simplest: only rotate and pan the image without resizing.
Suitable for fixing slightly tilted photos.

Selection Suggestions:
- For most cases (especially photos from quite extreme angles), choose Homography.
- If the image only needs a simple position/rotation adjustment, Euclidean or Similarity are more suitable.
- Use Afine only if you need flexible shape adjustments without effects perspective."""
 
ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """The RANSAC Threshold determines how strictly the algorithm filters out outlier data during image alignment.

- A lower value (e.g., 1-2) means stricter filtering, which might discard some important features.

- A higher value (e.g., 4-5) is more tolerant of outliers, allowing more features to be used,
  though it may reduce the overall alignment accuracy.

Typically, a value between 1 and 3 is sufficient, depending on the noise level in the data."""

# Farneback Optical Flow
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback Parameters"

FARNEBACK_PYRAMID_SCALE_LABEL = "Pyramid Scale"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """The Pyramid Scale is a factor that determines how much the image is downscaled at each level of the pyramid.

- This value dictates the reduction in image size from one level to the next.
  For example, if the value is 0.5, each level will have half the dimensions of the previous one.

- A smaller value (around 0.10 to 0.5) results in a greater size difference between levels,
  which can speed up computation but may reduce the accuracy in capturing subtle motion.

- A value closer to 1.00 results in smaller changes in size between levels,
  allowing for more accurate motion detection at the expense of increased processing time.

Adjust this value to balance processing speed with motion detection accuracy.
Recommended value: 0.5.
"""

FARNEBACK_LEVELS_LABEL = "Levels"
FARNEBACK_LEVELS_DESCRIPTION = """This parameter defines the number of layers in the image pyramid used by the Farneback algorithm to compute optical flow.

- More levels allow the algorithm to detect object movement across various scales and speeds,
  including complex or large-area motions, but they also increase computation time.
  
- Increasing the number of levels prolongs the processing time.

You can adjust this value between 1 and 10 based on your application’s requirements.
Generally, a value of 3 is considered standard.
"""

FARNEBACK_WIN_SIZE_LABEL = "Window Size"
FARNEBACK_WIN_SIZE_DESCRIPTION = """The Window Size specifies the area (in pixels) used for calculating optical flow.

- A larger window size results in a more stable and smoother motion estimation since it considers a wider area,
  though it might miss some finer movement details.
  
- A smaller window size is more sensitive to small movements but may interpret noise as motion, resulting in less stable estimates.

Choose a value that offers a balance between sensitivity to fine motion details and overall stability.
Recommended value: 15.
"""

FARNEBACK_ITERATIONS_LABEL = "Iterations"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterations determine how many times the optical flow calculation is refined at each level of the pyramid.

- More iterations can improve the accuracy of the optical flow estimation.
- However, increasing the number of iterations also extends the processing time.

Select a value that enhances accuracy without significantly slowing down the process.
Recommended value: 3.
"""

FARNEBACK_POLY_N_LABEL = "Polynomial Expansion"
FARNEBACK_POLY_N_DESCRIPTION = """The polynomial expansion parameter (poly_n) specifies the size of the pixel neighborhood used for motion estimation via polynomial expansion.

- A larger value uses more surrounding pixel data, resulting in a smoother motion estimation,
  but it may reduce sensitivity to small movements.

Typically, a value of 5 or 7 is used, depending on the desired level of detail and stability.
"""

FARNEBACK_POLY_SIGMA_LABEL = "Polynomial Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Polynomial Sigma controls the amount of smoothing applied before performing the polynomial expansion.

- This value represents the standard deviation of the Gaussian filter used to reduce noise in the pixel data.
- A higher sigma can help suppress noise,
  but if set too high, it may also remove important motion details.

Adjust this value carefully to reduce noise without losing significant motion details.
Recommended value: 1.2.
"""

FARNEBACK_FLAGS_LABEL = "Flags"
FARNEBACK_FLAGS_DESCRIPTION = """Flags are optional parameters that enable certain options in the Farneback algorithm.

- Flags are often used in conjunction with Gaussian filtering for smoothing,
  which can produce a smoother optical flow output.
  
- If you are unsure, leave this parameter at its default value (0).

Select the appropriate flag if you need to balance processing speed with result quality.
Recommended value: 0.
"""

# AKAZE Parameters
AKAZE_PARAMETER_SETTING_LABEL = "AKAZE Parameters"

AKAZE_THRESHOLD_LABEL = "Threshold"
AKAZE_THRESHOLD_DESCRIPTION = """The Threshold parameter determines how sensitive the detector is in identifying keypoints.

- Lower values increase the detection of more keypoints, even in images with few features and high noise.
- Higher values restrict detection to only the strongest features.

Recommended value: 30.
"""

AKAZE_OCTAVE_LABEL = "Number of Octaves"
AKAZE_OCTAVE_DESCRIPTION = """This parameter controls how many scale levels (octaves) are analyzed when searching for important features in an image.
Imagine viewing an image at various zoom levels; each zoom level is referred to as an "octave".

- Each octave represents a different zoom level, enabling the algorithm to detect features at various sizes. For example, small features become more noticeable when zoomed in, while larger features can be recognized even when viewed from farther out.
- Using more octaves allows the detection of features across a broader range of scales, but it increases the computational load and processing time.

Recommended value: 4.
"""

AKAZE_LAYER_LABEL = "Number of Layers per Octave"
AKAZE_LAYER_DESCRIPTION = """This parameter specifies the number of sub-levels within each octave.

- More layers provide a finer spatial resolution across scales, which can enhance feature detection.
- However, adding layers also increases the computational burden.

Recommended value: 4.
"""

AKAZE_RATIO_LABEL = "Threshold Ratio"
AKAZE_RATIO_DESCRIPTION = """The Threshold Ratio is used when matching keypoints between two images to ensure that the matches are truly reliable and not coincidental.

- A lower ratio (closer to 0.50) accepts only the most unambiguous matches, making the process more selective and reducing the likelihood of false matches.
- A higher ratio (closer to 1.00) is more tolerant, allowing more matches but increasing the risk of incorrect keypoint matches.

Recommended value: 0.80.
"""

KEEP_EDGES_LABEL = """Keep
Edges"""
IGNORE_EDGE_LABEL = """Ignore Edges"""

KEEP_EDGES_DESCRIPTION = """The Keep Edges feature allows the algorithm to
preserve the edges of the image during the alignment process."""

ENABLE_CROP_LABEL = """Enable 
Cropping"""
DISABLE_CROP_LABEL = """Disable 
Cropping"""
CROP_DESCRIPTION = """Enable Cropping to remove 
unused image borders."""


APPLY_PARAMETER_BUTTON_TEXT = "Apply Settings"


# ------------ Parameter Setting Algorithm --------------------- #

# Descriptions for Alignment Algorithm
ALIGNMENT_NAME = "Alignment Algorithm"
NONE_ALIGNMENT_DESCRIPTION = "No alignment will be applied."
FARNEBACK_DESCRIPTION = """This algorithm is well-suited for high-level alignment that demands precision and pixel-level accuracy.
However, it is quite sensitive to significant differences in rotation and perspective.
"""

AKAZE_DESCRIPTION = """This algorithm is fairly robust against substantial variations in rotation, perspective, and scale.
It performs adequately, though it does not achieve the pixel-level precision of Farneback.
"""
ORB_DESCRIPTION = """A fast algorithm, but less accurate when handling significant variations.
It is best suited for images with minimal differences and performs well on images with random textures.
"""

# Descriptions for Super Resolution
SUPER_RESOLUTION_NAME = "Super Resolution Algorithm"
NONE_SUPER_RESOLUTION_DESCRIPTION = "No super resolution will be applied."
INTERPOLATION_DESCRIPTION = """A simple algorithm for enhancing resolution using interpolation,
which adds a modest amount of detail.
"""

# Descriptions for Denoising
DENOISING_NAME = "Noise Reduction Algorithm"
NONE_DENOISING_DESCRIPTION = "No noise reduction will be applied."
WEIGHTED_AVERAGE_DESCRIPTION = """The result of simplifying the similarity stacking method.
It is quite effective at handling minor movements, but may produce image artifacts when the motion is more pronounced.
"""
                        
AVERAGE_DESCRIPTION = """A very fast and effective stacking method for static objects and scenes.
It is not ideal for dynamic scenes or areas with movement, but it can be combined with Farneback alignment to mitigate slight object motion.
"""

MEDIAN_DESCRIPTION = """A fast and effective stacking method that works reasonably well for moving objects.
It is very efficient at eliminating minor movements, but artifacts may appear when there is more substantial motion.
"""

SIMILARITY_DESCRIPTION = """An advanced stacking algorithm that is highly robust at eliminating object motion
(without ghosting in moving areas) and yields minimal artifacts—achieving up to an 85% reduction.
Inspired by:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336
"""
                        
                        
# ------------------ General Settings ------------------ #
SETTING_GENERAL_LABEL = "General"
LANGUAGE_LABEL = "Language"

LANGUAGE_TYPE = "English", "Indonesian", "Traditional Chinese", "Malay"

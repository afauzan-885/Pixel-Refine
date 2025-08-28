# -*- coding: utf-8 -*-

# ==============================================================================
# General UI Elements & Messages
# ==============================================================================
# Placeholder/General Info
UNDER_DEVELOPMENT = "The {page_name} menu is currently under development"
LOADING_THUMBNAIL = "Loading...."
NOT_IMAGE_PREVIEW = "No image available"
MODULE_NOT_IMPLEMENT = "Module has not been implemented yet."

# Buttons
ADD_IMAGE_BUTTON = "Add"
PREVIEW_IMAGE_BUTTON = "Preview"
DELETE_IMAGE_BUTTON = "Delete"
CLOSE_BUTTON = "Close"
APPLY_PARAMETER_BUTTON_TEXT = "Apply Settings"
APPY_PARAMETER = "Apply"
CANCEL_PARAMETER = "Cancel"

# Labels
PREVIEW_PANEL_LABEL = "Preview Panel"

# Window Messages
WINDOW_START_PROCESSING = "Starting process..."
WINDOW_PROCESSING_COMPLETE = "Complete!"

# Application Control
RESTART_APPLICATION_REQUIRED = "Restart Required"
RESTART_APPLICATION_DESCRIPTION = "Restart to apply changes"
ACCEPT_RESTART_APPLICATION = "Restart Now"
REJECT_APPLICATION_DESCRIPTION = "Later"
COMMAND_APPLICATION_DESCRIPTION = "Reloading Application..."
TRY_RESTART_APPLICATION = "Attempting to reload the application"
COMMAND_FAILED_IN_RESTART_APPLICATION = "System failed to restart."
RESTART_FAILED = "Restart Failed"
COMMAND_TO_RESTART_MANUALLY = "Could not restart the application automatically. Please restart it manually."

# ==============================================================================
# Sidebar UI
# ==============================================================================

SETTINGS_SIDEBAR_LABEL = "Settings"
PANORAMA_SIDEBAR_LABEL = "Panorama"

# ==============================================================================
# Topbar UI
# ==============================================================================
# Single Image Actions
TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "Import Image"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "Delete Image"

# Batch Actions
TOPBAR_BATCH_IMPORT_BUTTON_TEXT = "Import Images"
TOPBAR_BATCH_DELETE_BUTTON_TEXT = "Delete Batch"
TOPBAR_BATCH_START_PROCESS_BUTTON_TEXT = "Process Batch"
TOPBAR_BATCH_SAVE_BUTTON_TEXT = "Save To"

# ==============================================================================
# Batch Processing UI & Messages
# ==============================================================================
# General Batch Info & Status
NO_DATA_BATCH = "No saved batches."
UI_NO_CHANGE = "Unchanged"
UI_ALGORITHM_EDIT_HEADER = "Bulk Edit Algorithm"
UI_BATCH_HEADER = "Batch Process"
UI_ALGORIHM_EDIT = "Edit Algorithm"
UI_ALGORITHM_NOT_SET = "Algorithm not selected."
UI_FOLDER_PATH_NOT_SET = "Destination folder not set."
UI_BATCH_NOT_CONFIGURE = "Batch not configured."
UI_LABEL_BATCH_NO_PROCESS = "No batches are being processed!"
UI_LABEL_BATCH_SUCCES = "All batches have been processed!"
UI_LABEL_BATCH_PROCESS = "Processing {} batches..."
UI_LABEL_BATCH_PROGRESS = "{}/{} batches processed..."
UI_LABEL_MOVING_FILES = "Moving {} files to folder '{}'. Please wait..."
PROCESSING_BATCH = "--- Processing batch {}/{} (Completed: {}) ---"
NUMBER_OF_BATCHES_TO_BE_PROCESSED = "Number of batches to be processed: {}"
BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS = "batch_id must be present for batch processing"
SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED = "Skipping batch {} because no images were loaded."
BATCH_LABEL_FORMAT = "Batch {}   -   ({} images)"
BATCH_CANCELED_BY_USER = "Batch processing was canceled by the user."
BATCH_CANCELED_HEADER = "Batch Canceled"
BATCH_CANCELED_INFO = "Canceled"
BATCH_CANCELED_PROCESS = "Cancel Process"
BATCH_CANCELED_CONFIRMATION = "Are you sure you want to cancel all ongoing processes?"
BATCH_QUEUE = "Waiting"
BATCH_SUCCESS = "Batch processing complete."
BATCH_SUCCESS_HEADER = "Finished"

# --- Dialogue Title ---
SELECT_OUTPUT_FOLDER_TITLE = "Select Output Folder to Save Batch"
OUTPUT_FOLDER_SELECTION_CANCELLED = "Folder selection canceled. Process stopped."
ALGORITHM_SUCCESS_UPDATE = "Algorithm settings successfully updated for batches {} through {}."

# --- General Error Messages & Dialogs ---
BATCH_PROCESSING_ERROR_TITLE = "Batch Processing Error"
BATCH_PROCESSING_ERROR_MESSAGE = "Failed to process Batch {} (ID: {}):\n{}"
BATCH_SAVE_ERROR_TITLE = "Save Failed"
TARGET_FOLDER_NOT_ACCESSIBLE = "Target folder is not accessible:\n{}"
MOVE_FILE_ERROR_TITLE = "Failed to Move File"
COULD_NOT_SAVE_FILE_FOR_BATCH = "Could not save file '{}' for batch:\n{}"
SOURCE_FILE_DOES_NOT_EXIST = "Move failed: Source file '{}' does not exist."
TARGET_FOLDER_INVALID = "Move failed: Target folder '{}' is invalid."
BATCH_CONFIGURATION_INFO = "Batch has not been configured"

BATCH_PROCESSING_ERROR_REPORT_TITLE = "Batch Processing Error Report"
BATCH_PROCESSING_ERROR_REPORT_INTRO = "Processing finished with {num_failed} out of {num_total} batches failing to process. Details:"
BATCH_PROCESSING_ERROR_REPORT_ITEM = "• Batch #{seq} (ID: {id})\n  Reason: {error}"

# --- Log Message
LOG_BATCH_PROCESSING_START = "Starting processing for {} batches..."
LOG_PROCESSING_BATCH_DETAIL = "Processing Batch #{}, ID: {}, sequence ({}/{})..."
LOG_WARN_MULTIPLE_NEW_FILES = "Warning: More than 1 new file found for Batch {}. Moving the first one: {}"
LOG_BATCH_PROCESSED_NEW_OUTPUT = "Batch {} processed, new output: {}"
LOG_BATCH_PROCESSED_NO_OUTPUT = "Batch {} processed, but no new output file found in folder '{}'."
LOG_ERROR_PROCESSING_BATCH = "Error processing Batch {}: {}"
LOG_ALL_BATCH_ATTEMPTS_FINISHED = "All batch processing attempts have finished."

LOG_MOVE_SUCCESS = "Successfully moved '{}' to '{}'."
LOG_MOVE_FAILED = "Failed to move '{}' to '{}': {}"
LOG_SOURCE_FILE_NOT_FOUND = "Source file not found: {}"
LOG_TARGET_FOLDER_NOT_FOUND = "Target folder is invalid: {}"

# Toast message for process_all_batches
UI_LABEL_BATCH_NO_PROCESS = "No batches selected for processing."
UI_LABEL_BATCH_PROCESS_START = "Starting process for {} batches..."
UI_LABEL_BATCH_PROGRESS_DONE_SAVED = "Batch {} finished & saved ({}/{})."
UI_LABEL_BATCH_PROGRESS_SAVE_FAILED = "Batch {} finished, save failed ({}/{})."
UI_LABEL_BATCH_PROGRESS_NO_OUTPUT = "Batch {} finished, no output ({}/{})."
UI_LABEL_BATCH_PROGRESS_ERROR = "Error in Batch {} ({}/{})."

# Final Finished Toast Message
UI_LABEL_BATCH_ALL_SUCCESS_SPECIFIC = "All {} batches successfully processed & saved to {}."
UI_LABEL_BATCH_PARTIAL_SUCCESS_SPECIFIC = "{} of {} batches saved to {}. Some had issues."
UI_LABEL_BATCH_NO_SUCCESS_SPECIFIC = "Process finished. No batch results were saved to {}."
UI_LABEL_BATCH_NONE_PROCESSED = "No batches were processed."

# Batch Deletion
BATCH_DELETE_LABEL = "Confirm Batch Deletion", "Are you sure you want to delete batch {}?"
TITLE_BATCH_ALL_DELETE_BUTTON = "Delete All Batches"
CONFIRM_BATCH_ALL_DELETE_BUTTON = "Are you sure you want to delete {} batches?"
NO_DATA_BATCH_ALL_DELETE_BUTTON = "No saved batch data."

# Batch Parameters UI Labels
PARAMETER_BATCH_CROP_EDGE = "Crop Edge"
PARAMETER_BATCH_KEEP_EDGE = "Keep Edge"
PARAMETER_BATCH_DENOISING = "Denoising"
PARAMETER_BATCH_SUPER_RESOLUTION = "Super Resolution"
PARAMETER_BATCH_ALIGNMENT = "Align Images"
PARAMETER_BATCH_ALIGNMENT_TO_FOLDER = "Save Alignment Result to Folder"
PARAMETER_BATCH_ALIGNMENT_TO_PROCESS = "Use Alignment Result for Next Process"

# Batch Saving Feedback
UI_FAILED_TO_SAVE_IMAGE_BATCH = "Failed to save image: {}"
UI_SUCCES_TO_SAVE_IMAGE_BATCH = "Image saved successfully: {}"
UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH = "No image to save"
UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH = "System folder (database/stack) does not exist"
UI_NO_BATCH_PROCESS = "No batches available for processing"

# Batch Specific Errors/Warnings
ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F = "An error occurred while retrieving key {} from HDF5: {}"

# ==============================================================================
# Image Handling (Import/Delete) UI & Messages
# ==============================================================================
# Import
HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "Image Files (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES = """Drag & drop images here<br>
or<br>
Use the 'Import Images' button"""
SUPPORTED_IMAGE_EXTENSION = "Supported image formats"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Select Images"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Duplicate Images"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} images already exist in the database and will be skipped."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Format Selected"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} images with '{format}' format will be imported."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Failed", "No valid images to import." # Tuple for Title, Message
ON_IMPORT_COMPLETE_STATUS = "Import complete"
ON_IMPORT_COMPLETE_MESSAGES = "{} images have been successfully imported."

# Delete
HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Failed", "No images selected." # Tuple for Title, Message
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Are you sure you want to delete the {} selected images?"

# ==============================================================================
# Preview Panel UI & Messages
# ==============================================================================
UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Processing image, please wait..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "No image selected."

# ==============================================================================
# Progress & Status Messages (General)
# ==============================================================================
# Progress Bar
UPDATE_PROGRESS_BAR_STATUS = "{}% ({} processes remaining)"
OVERALL_PROGRESS = "Overall Progress:"

# Buttons in Progress Sections (if generic)
PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Start Process"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Save As"

# General Process Status/Feedback
PROCESS_ALGORITHM_PROCESS_SKIPPED = "No algorithm selected for processing"
PROCESS_TERMINATED_BY_USER = "Process Terminated by User"
LOADING_IMAGE_PATH = "Loading {num_in_this_batch} image paths..."
LOAD_IMAGE_FROM_HDF5 = "Loading {} images from HDF5..."
NO_IMAGE_PATH_PROCESSED_IMAGE = "No image paths to process."
PROCESSING_IMAGE_FROM_HDF5 = "Processing image from HDF5: {}"
OUTPUT_SAVE_WEIGHT_MAP = "Weight map will be saved to: {}"
OUTPUT_IMAGE_TO_BE_SAVED = "Output image will be saved to: {}"
NO_IMAGES_PROCESSED = "No images could be processed"
NUMBER_OF_IMAGES_TO_BE_PROCESSED = "Number of images to be processed: {}"
RETURNING_IMAGE_RESULTS = "Returning results ({}/{} images)."
FINISHING_ANALYSIS = "Finishing Analysis"
IMAGE_PROCESS_FINISHED = "Stacking finished."
IMAGE_PROCESS_IN_PROGRESS = "Processing image {} of {}"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Stacking batch {current} of {total}"

# ==============================================================================
# Core Processing Messages (Status & Logs)
# ==============================================================================
# General Logging
CONSOL_LOG_RUNNING_ALGORITHM = "Process {} selected, algorithm: {}"

# HDF5 Saving/Loading
SAVE_TO_HDF5_ALIGNED_SAVING = "Saving aligned images"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Image {index} has been saved."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "All images saved successfully."
NO_HDF5_FILE_PROCESSING_FROM_PATH = "HDF5 file not found. Processing from image paths..."

# Image Processing Steps
RUN_SAVING_REFERENCE_IMAGE = "Saving reference image."
RUN_IMAGE_PROCESSING = "Processing image {} of {}..."
RUN_IMAGE_PROCESSING_SAVING = "Image {i} has been saved."
RUN_IMAGE_PROCESSING_FINISHED = "Process finished."
RUN_IMAGE_PROCESS_STARTED = "Starting process..."
RUN_PROCESS_TRANSFORMATION = "[1/2] Computing transformation {}/{}"
RUN_SAVING_TRANSFORMATION = "[2/2] Saving result {}/{}"

# Motion Compensation / Alignment Steps
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS = "Aligning and cropping image {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION = "Saving image {}/{}"
COMPENSATE_MOTION_STATUS = "Performing motion compensation on image {image_id}..."
COMPENSATE_MOTION_FINISHED = "Motion compensation finished for image {image_id}."

# Stacking / Denoising Steps
STACK_IMAGES_PROCESS = "Processing image {current}/{total}..."
ENHANCEMENT = "Enhancing: {}"
STARTING_ENHANCEMENT = "Starting Enhancement"
START_IMAGE_ENHANCEMENT = "--- Starting Enhancement for {} images ---"
ANALYZING_IMAGE = "Analyzing image {}/{}..."
SAVING_WEIGHT_MAP = "Weight map saved"

# Analysis Steps (e.g., Similarity)
ANALYSIS_STEP_ONE = "Pass 1/2: Creating Scene Data..."
ANALYSIS_STEP_ONE_PROGRESS = "Pass 1/2: Analyzing frame {}/{}"
ANALYSIS_STEP_TWO = "{} Merging Data..."
ANALYSIS_STEP_TWO_PROGRESS = "{} Merging image {}/{}"
ANALYZING_COMPLETE = "Analysis Complete"

# ==============================================================================
# Error Messages
# ==============================================================================
# General Errors
RUN_ERROR_STATUS = "An error occurred: {error}"
RUN_ERROR_MESSAGE = "An error occurred: {error}"
FAILED_TO_SAVE_IMAGE = "Failed to save the final image."
FAILED_TO_CREATE_PROCESS_WINDOW = "Failed to create process window: {}"

# Image Loading / Preparation Errors
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Failed to load image"
RUN_IMAGE_NOT_FOUND = "Image not found in the database."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Reference image could not be loaded from {image_paths[0]}."
RUN_IMAGE_PROCESSING_FAILED = "Failed to load image {i} from {image_paths[i]}."
FAILED_WHILE_PREPARING_IMAGE = "Failed to prepare image: {}"
FAILED_TO_PREPARE_REFERENCE_IMAGE = "Failed to prepare reference image: {}"
IMAGE_LOAD_FAILED = "No images were loaded."
FIRST_IMAGE_CANNOT_BE_OBTAINED = "Could not obtain the first image: {}"
RUN_IMAGE_PROCESS_LOAD_FAILED = "No images found in the database."

# File / System Errors
ERROR_IN_READING_FILE_HDF5 = "Error reading HDF5: {}"
FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "Transformation matrix file not found for image #{}"
LIBRARY_FILE_NOT_FOUND = "Library file not found: {}"

# Processing / Algorithm Errors
ERROR_ACCUMULATE_IMAGE = "Accumulated image is None or total weights are invalid."
RUN_STACK_PROCESSING_FAILED = "Failed to perform image stacking"
FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "Motion calculation could not be computed for image #{}"
FAIL_COMPENSATE_MOTION_PROCESS = "Estimation failed on image #{}"
UNRECOGNIZED_TRANSFORMATION = "Unrecognized transformation type."
FAILED_TO_COMPUTE_TRANSFORMATION = "Transformation could not be computed."
FAILED_TO_COMPUTE_CROP = "Failed to compute a valid crop. Process canceled."
FAIL_CROPPING_PROCESS = "Invalid crop. Insufficient overlap."
ERROR_IN_FLOW_FIELD = "Error in image {}: Input flow field is None. Cannot compensate motion."
ERROR_IN_BASE_IMAGE = "Error in image {}: Input base_image is None. Cannot compensate motion."
STACK_IMAGES_FAILED = "No images to process."
DATA_FAILED_COMPLETION_CREATED = "Enhancement data failed to generate. Cannot perform enhancement."
FAILED_IMAGE_ENHANCEMENT = "Enhancement process failed."
ANALYSIS_FAILURE = "Analysis failed: No images were processed"
ERROR_AT_END_OF_CONVERSION = "Error at the end of conversion: {}"
UNEXPECTED_NUMBER_OF_BUFFER_CHANNELS = "Internal Error: Unexpected number of buffer channels."
UNABLE_TO_SAVE_WEIGHT_MAP = "Unable to save Weight Map: {}"
FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH = "Failed to save weight map to {}"
NORMALIZATION_FAILED = "Normalization Failed: {}"
FATAL_ERROR_DURING_NORMALIZATION = "FATAL ERROR during normalization: {}"
FAILED_TO_ACCUMULATE_IMAGE = "Image {} failed to accumulate"
COLOR_CHANNEL_DOES_NOT_MATCH = "Color channels do not match."
IMAGE_CHANNEL_DOES_NOT_SUPPORT = "Unsupported image channels: {}."
DATA_TYPE_NOT_SUPPORTED = "Data type not supported: {}."
IMAGE_BIT_REQUIRED = "Image must be 8-bit or 16-bit."

# Library / Dependency Errors
FAILED_TO_CONFIGURE_LIBRARY = "Failed to load/configure library {}: {}"
LIBRARY_FAILED_TO_LOAD_NORMALIZATION_FAILED = "C++ library not loaded. Normalization skipped."
LIBRARY_FAILED_TO_LOAD_ACCUMULATED_SKIPED = "C++ library not loaded. Accumulation skipped."

# GPU Errors
GPU_ERROR_AND_FALLBACK_TO_CPU = "Unexpected GPU error: {}. Falling back to CPU."

# Validation Errors
IMAGE_DATA_MUST_BE_VALID = "Items in the 'images' list must be valid image data (NumPy array)."

# ==============================================================================
# Confirmation Dialogs / Warnings
# ==============================================================================
NO_ALIGNMENT_PROCESS = "Are you sure you don't want to align the images first?"
CANCEL_PROCESSING = "Are you sure you want to cancel the process?"
# Note: Batch deletion confirmations are kept within the Batch section for context

# ==============================================================================
# Algorithm Specific Window Titles
# ==============================================================================
# Alignment
WINDOW_TITLE_FARNEBACK = "Farneback Optical Flow Alignment"
WINDOW_TITLE_AKAZE = "AKAZE Alignment"
WINDOW_TITLE_ORB = "ORB Alignment"
WINDOW_TITLE_LIGHT_GLUE = "LightGlue Alignment"

# Denoising / Stacking
WINDOW_TITLE_AVERAGE = "Average Stacking"
WINDOW_TITLE_MEDIAN = "Median Stacking"
WINDOW_TITLE_SIMILARITY = "Similarity Stacking"
WINDOW_TITLE_SIMILARITY_V2 = "Similarity Stacking V2"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Interpolation Super Resolution"

# ==============================================================================
# Algorithm Parameter Settings UI (Labels & Descriptions)
# ==============================================================================
DEFAULT_PARAMETER_SETTING_LABEL = """Select an algorithm to see its parameters."""

# --- ORB Parameters ---
ORB_PARAMETER_SETTING_LABEL = "ORB Parameters"
ORB_NFEATURES_LABEL = "Number of Features"
ORB_NFEATURES_DESCRIPTION = """The number of features determines how many fine details can be recognized in an image.

- A higher number of features allows the algorithm to find more details,
  resulting in more precise image alignment, but it increases computation time.

- Typically, a value between 500 and 1500 is sufficient for most scenes.
  For very high accuracy needs, values between 2500 and 5000 can improve precision."""
ORB_SCALEFACTOR_LABEL = "Scale Factor"
ORB_SCALEFACTOR_DESCRIPTION = """The Scale Factor determines the rate at which the image is downscaled during processing.

- A value closer to 1.0 means the image is downscaled slowly with more steps.
  This allows for the detection of finer details but takes longer.

- A larger value downscales the image more quickly, making processing faster,
  but some small details might be missed.

Typically, the Scale Factor value ranges from 1.2 to 1.5."""
ORB_NLEVELS_LABEL = "Number of Levels"
ORB_NLEVELS_DESCRIPTION = """The number of levels indicates the number of layers in the image pyramid used to detect features.

- More levels allow the algorithm to capture details at various scales,
  which is useful if the image sizes vary.

- However, a higher number of levels increases the processing time.

For most scenes, a value between 2 and 4 is ideal."""
ORB_TRANSFORMATION_LABEL = "Transformation Type"
ORB_TRANSFORMATION_DESCRIPTION = """Choose the method for aligning images based on your needs:

Available options include:
- HOMOGRAPHY: Suitable for photos with significant perspective differences (e.g., a table viewed from the top vs. from the side).
  It can adjust for "perspective" effects.

- AFFINE: Can rotate, resize (non-uniformly), and shift the image.
  Example: correcting a tilted photo that needs to be partially enlarged.

- SIMILARITY: Only allows rotation, uniform scaling, and translation.
  The aspect ratio is preserved.

- EUCLIDEAN: The simplest: only rotates and shifts the image without changing its size.
  Good for correcting slightly tilted photos.

Selection Advice:
- For most cases (especially photos with significant perspective changes), choose Homography.
- If the image only needs simple position/rotation adjustments, Euclidean or Similarity is more suitable.
- Use Affine only when flexible shape adjustments are needed without perspective effects."""
ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """The RANSAC Threshold determines how strictly the algorithm filters out outliers
(data points that deviate significantly) when aligning images.

- A lower value (e.g., 1-2) means stricter filtering, which might cause some important features to be ignored.

- A higher value (e.g., 4-5) is more tolerant of outliers, allowing more features to be used,
  but this can reduce alignment accuracy.

Typically, a value between 1 and 3 is sufficient, depending on the level of noise in the data."""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback Parameters"
FARNEBACK_PYRAMID_SCALE_LABEL = "Pyramid Scale"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """The Pyramid Scale is the factor that determines how much the image
is downscaled at each level of the pyramid.

- This value determines the downscale factor from one level to the next.
  For example, a value of 0.5 means each level will be half the size of the previous one.

- A smaller value (around 0.10 to 0.5) results in a larger size difference between levels.
  This can speed up computation but may reduce accuracy in capturing fine motion.

- A value closer to 1.00 results in smaller size changes between levels,
  allowing for more accurate motion detection at the cost of longer computation time.

Adjust this value to find the right balance between processing speed and
motion detection accuracy.
Recommended value: 0.5
"""
FARNEBACK_LEVELS_LABEL = "Levels"
FARNEBACK_LEVELS_DESCRIPTION = """The Levels parameter in the Farneback algorithm refers to the number of layers
in the image pyramid used to calculate optical flow.

- More levels: The algorithm can detect object motion at various sizes and speeds,
  including complex or large-area movements. However, this requires
  more computation time.

- As the number of levels increases, the computation time required also increases.

You can adjust it between 1 and 10 according to your application's needs.
In general, a value of 3 is considered standard.
"""
FARNEBACK_WIN_SIZE_LABEL = "Window Size"
FARNEBACK_WIN_SIZE_DESCRIPTION = """The Window Size determines the size of the pixel area (window)
used in the optical flow calculation.

- A larger window size: Results in a more stable and smooth motion estimation because
  information is calculated from a wider area. However, small motion details may be missed.

- A smaller window size: Is more sensitive to small movements,
  but noise might be misinterpreted as motion, leading to less stable results.

Choose a value that balances sensitivity to small motion details
with stable results.
Recommended value: 15.
"""
FARNEBACK_ITERATIONS_LABEL = "Iterations"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterations determine how many times the optical flow calculation is refined at each pyramid level.

- The more iterations, the more accurate the resulting optical flow will be.
- However, increasing the number of iterations can also slow down computation time.

Choose a value that improves accuracy without excessively slowing down the process.
Recommended value: 3.
"""
FARNEBACK_POLY_N_LABEL = "Polynomial Expansion"
FARNEBACK_POLY_N_DESCRIPTION = """Polynomial Expansion (poly_n) determines the size of the pixel neighborhood used
to approximate motion with a polynomial expansion method.

- This value defines how many neighboring pixel data points are used in the calculation.

- A larger value will result in a smoother motion estimation,
  but may reduce sensitivity to small movements.

Typically, values of 5 or 7 are used, depending on the desired level of detail and stability.
"""
FARNEBACK_POLY_SIGMA_LABEL = "Polynomial Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Polynomial Sigma controls the amount of smoothing
applied before the polynomial expansion is performed.

- This value is the standard deviation of the Gaussian filter used to reduce noise in the pixel data.
- A higher sigma can help suppress noise,

  but if it's too high, it might eliminate important motion details.

Adjust carefully to reduce noise without losing significant motion details.
Recommended value: 1.2.
"""
FARNEBACK_FLAGS_LABEL = "Flags"
FARNEBACK_FLAGS_DESCRIPTION = """Flags are optional parameters that enable
specific options within the Farneback algorithm.

- Flags are often used in applying a Gaussian filter for smoothing,
  which is used to produce a smoother optical flow.

- If you are unsure, leave this parameter at its default value (0).

Select the appropriate flag if you want to balance between processing speed and result quality.
Recommended value: 0.
"""

# --- AKAZE Parameters ---
AKAZE_PARAMETER_SETTING_LABEL = "AKAZE Parameters"
AKAZE_THRESHOLD_LABEL = "Threshold"
AKAZE_THRESHOLD_DESCRIPTION = """The Threshold parameter determines how sensitive the detector is
when searching for keypoints.

- A lower value increases the detection of more keypoints,
  including in images with few features or a lot of noise.

- A higher value restricts detection to only the strongest features.

Recommended value: 0.0010.
"""
AKAZE_OCTAVE_LABEL = "Number of Octaves"
AKAZE_OCTAVE_DESCRIPTION = """This parameter controls how many scale levels are analyzed
when searching for important features in an image. Imagine looking at an image at different zoom levels;
each zoom level is called an "octave".

- Each octave: Represents a different zoom level, allowing the algorithm to detect features at various sizes.
  For example, small features are visible when zoomed in, while large features can be recognized when zoomed out.

- More octaves: Provide the ability to detect features at more scales or sizes.
  However, this requires more computational work and increases processing time.

Recommended value: 4.
"""
AKAZE_LAYER_LABEL = "Number of Layers per Octave"
AKAZE_LAYER_DESCRIPTION = """Layers per Octave determines the number of sub-levels within each octave.

- More layers provide a finer scale-space resolution,
  which can improve feature detection across different scales.

- However, adding layers also increases the computational load.

Recommended value: 4.
"""
AKAZE_RATIO_LABEL = "Ratio Threshold"
AKAZE_RATIO_DESCRIPTION = """The Ratio Threshold is a value used when matching keypoints
between two images. Its purpose is to ensure that the found matches are truly accurate and not just a coincidence.

- A lower ratio (closer to 0.50): Only accepts very clear, unambiguous matches.
  In other words, it is more selective, reducing the chance of false positive matches.

- A higher ratio (closer to 1.00): Means we are more tolerant in accepting matches,
  so more matches are accepted. However, this also increases the likelihood of incorrect matches.

Recommended value: 0.80.
"""

# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "Overlap %"
OVERLAP_DESCRIPTION = """Helps to reduce tile artifacts (which cause a blocky effect in moving areas).

Increasing the overlap can reduce these artifacts but will increase computation time."""

TILE_SIZE_LABEL = "Tile Size"
TILE_SIZE_DESCRIPTION = """The smaller the tile size, the more detail can be detected in differences.

However, this will also increase computation time and the likelihood of errors in difference detection."""

MOTION_SENSIVITY_LABEL = "Motion Sensitivity"
MOTION_SENSIVITY_DESCRIPTION = """Motion sensitivity controls how aggressively the algorithm detects differences within a tile.

The lower the value, the more aggressive or sensitive it is in detecting differences,
but this may cause noise to be considered a difference."""

NOISE_OFFSET_LABEL = "Noise Offset"
NOISE_OFFSET_DESCRIPTION = """A threshold for ignoring the noise level in an image, so that higher noise is not considered as movement.

A higher value can result in a cleaner stack for images with extreme noise, but it may also reduce the detection of movement in the image."""

# --- General Alignment Options (Edges, Crop, Saving) ---
KEEP_EDGES_LABEL = "Keep Edges"
IGNORE_EDGE_LABEL = "Ignore Edges"
KEEP_EDGES_DESCRIPTION = """The Keep Edges feature allows the algorithm to keep the image edges
intact during the alignment process."""

ENABLE_CROP_LABEL = "Enable\nCropping"
DISABLE_CROP_LABEL = "Disable\nCropping"
CROP_DESCRIPTION = """Enable Cropping to remove
unused image borders.

Note: A cropping bug can sometimes occur (very rarely),
such as the resulting image being very small, or errors in the cropping calculation."""

ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "Save to folder"
DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "Don't save\nto folder"
SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER = "Browse..."
DEFAULT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Default Folder"
SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Select folder"
SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """Saves the aligned images to a folder.
The default folder is the Documents folder on your PC."""

ACTIVATE_SAVE_ALIGN_TO_PROCESS = "Save for\nnext process"
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = "Don't save for\nnext process"
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """Saves the image for the next
denoising or super-resolution process."""

# ==============================================================================
# Algorithm General Descriptions (Overview)
# ==============================================================================
# --- Alignment Algorithm Descriptions ---
ALIGNMENT_NAME = "Alignment Algorithm"
NONE_ALIGNMENT_DESCRIPTION = "No alignment will be applied."
FARNEBACK_DESCRIPTION = """This algorithm is suitable for high-level alignment that requires pixel-level precision and accuracy.
However, it is very weak against significant rotational and perspective differences."""
AKAZE_DESCRIPTION = """This algorithm is quite robust against large differences in rotation, perspective, and scale.

It performs well, but is not as precise as Farneback at the pixel level."""
ORB_DESCRIPTION = """A fast but less accurate algorithm for significant differences.

Suitable for images with minimal differences and accurate for images with random textures."""

LIGHT_GLUE_DESCRIPTION = """A neural network (Deep Learning) model for matching local features across images.

LightGlue is more robust than algorithms like AKAZE, capable of handling images with significant perspective differences and difficult conditions.
Warning: This process is optimized for powerful NVIDIA GPUs (CUDA). It can run on a CPU, but processing time will be significantly slower."""

# --- Super Resolution Algorithm Descriptions ---
SUPER_RESOLUTION_NAME = "Super Resolution Algorithm"
NONE_SUPER_RESOLUTION_DESCRIPTION = "No super resolution will be applied."
INTERPOLATION_DESCRIPTION = """A simple algorithm to increase resolution using interpolation methods,
adding minimal detail."""

# --- Denoising Algorithm Descriptions ---
DENOISING_NAME = "Denoising Algorithm"
NONE_DENOISING_DESCRIPTION = "No denoising will be applied."
WEIGHTED_AVERAGE_DESCRIPTION = """A simplified version of the similarity stacking method.
It handles small movements well but produces image artifacts with larger movements."""
AVERAGE_DESCRIPTION = """A very fast and effective stacking method for static objects and scenes.
Not suitable for moving scenes or areas, but can be combined with Farneback alignment
to eliminate light object movement."""
MEDIAN_DESCRIPTION = """Fast and effective for stacking, and performs reasonably well on moving objects.
Very effective at eliminating small object movements, but artifacts appear with larger movements."""
SIMILARITY_DESCRIPTION = """An advanced stacking algorithm, very robust in eliminating object movement
(very little ghosting in moving areas) and produces very few artifacts up to 85% of the time.

Inspired by:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""

SIMILARITY_MOTION_V2_DESCRIPTION = """Similarity V2 is an evolution of the Similarity v1 algorithm with several
significant improvements. This algorithm can produce cleaner images even from severely noisy inputs, thanks to its ability
to intelligently distinguish between noise, texture, and subtle motion. It is more reliable in low-light conditions, but its process is slower
than the v1 version."""

# ==============================================================================
# Application Settings UI
# ==============================================================================
SETTING_GENERAL_LABEL = "General"
LANGUAGE_LABEL = "Language"
LANGUAGE_TYPE = "English", "Indonesian", "Traditional Chinese", "Malay"
GPU_ACCELERATION_LABEL = "GPU Acceleration"
MULTI_CORE_CPU = "Multi-Core CPU Acceleration"
SETTINGS_SAVED = "Settings saved successfully."

CANT_READ_FILE_SETTINGS = "Warning: Cannot read settings file '{GENERAL_SETTINGS_FILE}'. Using default values."
MULTI_CORE_CPU_DESCRIPTION = """Enabling this will increase computation speed for image processing, but will slightly increase RAM usage.

If your computer has very limited RAM, it is recommended to leave this unchecked."""

GPU_ACCELERATION_DESCRIPTION = """Enabling this will significantly increase computation speed by using the GPU for processing.

NOTE: GPU usage is currently limited to the Farneback and Lightglue only. Implementation for other algorithms will follow."""

THUMBNAIL_LABEL = "Thumbnail"
THUMBNAIL_DESCRIPTION = """Image preview for the batch process, still EXPERIMENTAL.
It may sometimes cause flickering or lag when adding a new batch."""

NOISE_MAD_OFFSET_LABEL = "MAD Noise Factor"
NOISE_MAD_OFFSET_DESCRIPTION = """How sensitive the MAD detection is when handling high-noise images.

A higher value increases tolerance to noise (less sensitive in high-noise areas),
but will cause ghosting in those areas if motion occurs."""

MAD_SENSITIVITY_LABEL = "MAD Sensitivity"
MAD_SENSITIVITY_DESCRIPTION = """How sensitive MAD is in handling differences in an image.

A higher value will be more sensitive to subtle differences but increases detection errors
if the input image has high noise."""

CONF_SKIP_DFT_LABEL = "DFT Skip\nConfidence"
CONF_SKIP_DFT_DESCRIPTION = """Threshold for skipping DFT if the MBM process has already handled it well.

The higher the value, the more processing will be done by MAD. However, MAD is a coarse detection method;
it is sensitive to noise and low-contrast areas, but the advantage of more MAD processing is lighter computation."""

WIENER_C_FACTOR_LABEL = "Wiener C Factor"
WIENER_C_FACTOR_DESCRIPTION = """How sensitive the DCT Wiener calculation is in detecting differences in an image.

The lower the value, the more sensitive it is to detecting subtle movements, but this results in increased noise
because noise itself can cause false movements. The Wiener C Factor works in conjunction with MAD Sensitivity."""

COARSE_MARGIN_LABEL = "Coarse Align Margin"
COARSE_MARGIN_DESCRIPTION = """The margin window for alignment at the tile level.

This improves accuracy down to the tile level, enhancing stacking precision.
It can significantly impact performance if the search area is too large."""
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
EXIT_APPLICATION_TITLE = "Exit Application"
EXIT_APPLICATION_MESSAGE = "Do you want to exit the application?"
EXIT_APPLICATION_YES = "Yes"
EXIT_APPLICATION_NO = "No"
PROJECT_SAVE_CHANGES_TITLE = "Save Project"
PROJECT_SAVE_CHANGES_MESSAGE = "This project has unsaved changes. Save before exiting?"
PROJECT_SAVE_CHANGES_SAVE = "Save"
PROJECT_SAVE_CHANGES_DISCARD = "Don't Save"
PROJECT_SAVE_CHANGES_CANCEL = "Cancel"
EXIT_APPLICATION_APPLY_BACKEND_TITLE = "Backend Change"
MSG_BACKEND_EXIT_REQUIRED = "Exit the application, then open it again to apply the new backend selection?"

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
ORB_NFEATURES_DESCRIPTION = """The number of details recognized in an image.
- Higher: More precise alignment but increases processing time.
- Recommended: 500 to 1500 for normal images; 2500 to 5000 for high-precision needs."""
ORB_SCALEFACTOR_LABEL = "Scale Factor"
ORB_SCALEFACTOR_DESCRIPTION = """How fast the image size is reduced during processing.
- Closer to 1.0: Slower reduction, detects finer details, but takes longer.
- Larger value: Faster processing, but small details might be missed.
- Recommended: 1.2 to 1.5."""
ORB_NLEVELS_LABEL = "Number of Levels"
ORB_NLEVELS_DESCRIPTION = """Number of image pyramid layers used to detect features.
- Higher: Better detection for varying image sizes, but slows down processing.
- Recommended: 2 to 4."""
ORB_TRANSFORMATION_LABEL = "Transformation Type"
ORB_TRANSFORMATION_DESCRIPTION = """Select the alignment method based on your needs:
- HOMOGRAPHY: Best for perspective changes (e.g., tilted angles, top vs side view).
- AFFINE: Corrects rotation, scaling, and skewing.
- SIMILARITY: Allows only rotation, translation, and uniform scaling (aspect ratio is kept).
- EUCLIDEAN: Simple rotation and translation without changing size."""
ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """Strictness of filtering out misaligned points.
- Lower (1-2): Stricter filtering, high precision but might fail if details are low.
- Higher (4-5): More tolerant, increases success rate but may slightly reduce accuracy.
- Recommended: 1 to 3."""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback Parameters"
FARNEBACK_PYRAMID_SCALE_LABEL = "Pyramid Scale"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """The scale factor to reduce the image size at each level.
- Closer to 1.0: Fine size steps, high motion detection accuracy, but slower.
- Value of 0.5: Size is halved at each level, balanced speed and accuracy.
- Recommended: 0.5."""
FARNEBACK_LEVELS_LABEL = "Levels"
FARNEBACK_LEVELS_DESCRIPTION = """Number of pyramid layers used to calculate motion.
- More levels: Better at capturing large or complex motion, but increases computation.
- Recommended: 3."""
FARNEBACK_WIN_SIZE_LABEL = "Window Size"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Size of the pixel window used to compute optical flow.
- Larger: Smoother and more stable motion estimation, but misses fine details.
- Smaller: Sensitive to small movements, but may interpret noise as motion.
- Recommended: 15."""
FARNEBACK_ITERATIONS_LABEL = "Iterations"
FARNEBACK_ITERATIONS_DESCRIPTION = """Number of refinement passes at each pyramid level.
- Higher: More accurate motion estimation, but slower.
- Recommended: 3."""
FARNEBACK_POLY_N_LABEL = "Polynomial Expansion"
FARNEBACK_POLY_N_DESCRIPTION = """Neighborhood size used to find polynomial expansion.
- Larger: Smoother motion estimation but less sensitive to tiny movements.
- Recommended: 5 or 7."""
FARNEBACK_POLY_SIGMA_LABEL = "Polynomial Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Gaussian standard deviation used to smooth image details.
- Higher: Suppresses noise better but may blur out motion details.
- Recommended: 1.2."""
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
AKAZE_THRESHOLD_DESCRIPTION = """Sensitivity threshold for detecting keypoints.
- Lower: Detects more details (useful for low-contrast/noisy scenes).
- Higher: Restricts detection to only the most prominent features.
- Recommended: 0.001."""
AKAZE_OCTAVE_LABEL = "Number of Octaves"
AKAZE_OCTAVE_DESCRIPTION = """Number of zoom levels (octaves) analyzed.
- Higher: Detects features across wider scale differences, but increases processing time.
- Recommended: 4."""
AKAZE_LAYER_LABEL = "Number of Layers per Octave"
AKAZE_LAYER_DESCRIPTION = """Number of sub-levels within each octave.
- Higher: Finer scale detection, but increases computation.
- Recommended: 4."""
AKAZE_RATIO_LABEL = "Ratio Threshold"
AKAZE_RATIO_DESCRIPTION = """Strictness of keypoint matching between images.
- Lower (0.5 - 0.7): Stricter matching, reduces false connections.
- Higher (0.8 - 0.9): More tolerant, finds more matches but increases incorrect pairings.
- Recommended: 0.8."""

# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "Overlap %"
OVERLAP_DESCRIPTION = """Overlap area between tiles.
- Higher: Reduces blocky artifacts in moving areas, but increases processing time."""

TILE_SIZE_LABEL = "Tile Size"
TILE_SIZE_DESCRIPTION = """Processing block size.
- Smaller: Captures fine details and differences, but increases processing time.
- Larger: Faster processing, but might miss small motion details."""

MOTION_SENSIVITY_LABEL = "Motion Sensitivity"
MOTION_SENSIVITY_DESCRIPTION = """How sensitive the algorithm is in detecting movement.
- Lower value: More aggressive detection (may interpret noise as motion).
- Higher value: Less sensitive, ignores subtle movements."""

NOISE_OFFSET_LABEL = "Noise Offset"
NOISE_OFFSET_DESCRIPTION = """Threshold to ignore noise.
- Higher: Keeps stacks cleaner in extreme noise, but may ignore actual movements."""

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
SETTING_PERFORMANCE_LABEL = "Performance"
PROJECT_MENU_LABEL = "Project"
PROJECT_SAVE = "Save Project"
PROJECT_SAVE_AS = "Save Project As..."
PROJECT_OPEN = "Open Project..."
PROJECT_RECENT = "Recent Projects"
PROJECT_ABOUT = "About Pixel Refine"
LANGUAGE_LABEL = "Language"
LANGUAGE_TYPE = "English", "Indonesian", "Traditional Chinese", "Malay"
GPU_ACCELERATION_LABEL = "GPU Acceleration"
MULTI_CORE_CPU = "Multi-Core CPU Acceleration"
SETTINGS_SAVED = "Settings saved successfully."

CANT_READ_FILE_SETTINGS = "Warning: Cannot read settings file '{GENERAL_SETTINGS_FILE}'. Using default values."
MULTI_CORE_CPU_DESCRIPTION = """Enables multi-thread processing.
- On: Faster processing, but increases RAM usage. Disable if RAM is limited."""

GPU_ACCELERATION_DESCRIPTION = """Uses GPU to speed up computations.
- Note: Currently supported only for Farneback and LightGlue algorithms."""

THUMBNAIL_LABEL = "Thumbnail"
THUMBNAIL_DESCRIPTION = """Shows image previews during batch processing (Experimental).
- Note: May cause slight lag or flickering when loading new batches."""

NOISE_MAD_OFFSET_LABEL = "MAD Noise Factor"
NOISE_MAD_OFFSET_DESCRIPTION = """MAD threshold for noisy images.
- Higher: More tolerant to noise, but increases ghosting risk in moving areas."""

MAD_SENSITIVITY_LABEL = "MAD Sensitivity"
MAD_SENSITIVITY_DESCRIPTION = """MAD sensitivity to differences.
- Higher: Detects subtle changes, but increases errors in noisy images."""

CONF_SKIP_DFT_LABEL = "DFT Skip\nConfidence"
CONF_SKIP_DFT_DESCRIPTION = """Threshold to skip DFT when MBM is sufficient.
- Higher: More tasks processed by MAD (lighter computation but less precise)."""

WIENER_C_FACTOR_LABEL = "Wiener C Factor"
WIENER_C_FACTOR_DESCRIPTION = """Wiener filter sensitivity to differences.
- Lower: Sensitive to fine movements, but may increase noise."""

COARSE_MARGIN_LABEL = "Coarse Align Margin"
COARSE_MARGIN_DESCRIPTION = """Search margin for alignment at the tile level.
- Higher: More precise stacking, but significantly slows down processing."""

# --- Missing UI Keys ---
LBL_BATCH_MODE = "Batch Mode"
LBL_BULK_MODE = "Bulk Mode"
LBL_PARAMETER_ALIGNMENT = "Alignment Parameters"
LBL_ALIGNMENT_PLACEHOLDER = "Alignment parameters will\nappear here"
LBL_PARAMETER_ALGORITHM = "Algorithm Parameters"
LBL_ALGORITHM_PLACEHOLDER = "Parameters will appear here\nbased on selected algorithm"
BTN_START = "Start"
BTN_NEW_BATCH = "New Batch"
BTN_DELETE_BATCH = "Delete Batch"
LBL_ALGORITHM_SETTINGS = "Algorithm Settings"
BTN_PROCESS_ALL_BATCH = "Process All Batch"
LBL_FROM_PROJECT = "From Project #:"
LBL_TO_PROJECT = "To Project #:"
MSG_INVALID_RANGE = "The 'From' value cannot be greater than the 'To' value."
BTN_CLOSE = "Close"
LBL_STATUS_PROCESSING = "Processing"
BTN_BACK_TO_GRID = "Back to Grid"
BTN_IMPORT_IMAGES = "Import Images"
MSG_SUCCESS_SAVE_TO = "Image saved successfully to:"
LBL_DRAG_DROP_HERE = "Drop images here"
BTN_YES_DELETE = "Yes, Delete"
BTN_NO_CANCEL = "No, Cancel"
LBL_SELECTED_BATCHES_TITLE = "Complete List of Selected Batches"
LBL_CREATE_NEW_BATCH_TITLE = "Create New Batch"
LBL_BATCH_NAME = "Batch Name"
BTN_CREATE = "Create"
MSG_CONFIRM_DELETE_BATCH_COUNT = "Are you sure you want to delete {} batches?"
MSG_NO_BATCHES_AVAILABLE = "There are no batches available to process."
MSG_RENAME_FAILED = "Could not rename the batch. The name may be invalid or already in use."
TIP_CPU_CORES = "Number of CPU cores used for parallel processing."
LBL_SMART_NOISE_ALPHA = "Smart Noise Alpha (AI):"
TIP_SMART_NOISE_ALPHA = "Controls AI tolerance to noise.\nLow value = Sensitive to motion (less ghosting).\nHigh value = More noise cleanup (risk of ghosting)."
LBL_SMART_NOISE_AWARE = "Smart Noise Aware (AI):"
TIP_SMART_NOISE_AWARE = "Enable or disable noise estimation contribution to the AI model."
LBL_NOISE_CONTRIB = "Noise Contribution Strength (%):"
TIP_NOISE_CONTRIB = "Adjust how strongly noise estimation is applied (0% = Disabled, 100% = Full)."
LBL_LIGHT_GLUE_TITLE = "Light Glue Parameter Setting"
LBL_SELECT_REFERENCE_IMAGE = "Select Reference Image"
LBL_DELETE_IMAGES = "Delete Images"
MSG_CONFIRM_DELETE_IMAGE = "Are you sure you want to delete the selected images from this batch?"
TIP_RIGHT_CLICK_COPY = "Right-click to copy text"
MSG_UNSUPPORTED_FORMAT_IGNORED = "Unsupported file format or no valid extension provided."
MSG_NO_VALID_IMAGES_GROUP = "No valid images to import."
LBL_LOGGING_LEVEL = "Logging Level:"
BTN_RESET_TO_DEFAULT = "Reset to Default"
BTN_CLEAR_CACHE = "Clear Cache"
LBL_STATUS_READY = "Ready"
LBL_ITEMS_REMAINING = "items remaining"
LBL_SPLASH_LOADING = "L O A D I N G . . ."
MSG_EXIFTOOL_NOT_FOUND = "Exiftool not found. Please ensure it is installed and in your system's PATH."
MSG_NO_BATCHES_YET = "No batches yet"
MSG_NO_BATCHES_YET_DESC = "Create a new batch or import images to get started."
MSG_NO_BATCH_SELECTED = "No batch selected"
LBL_BATCH_IMAGE_COUNT_FORMAT = "Batch {}   -   ({} images)"
DESC_SUPER_RESOLUTION_CARD = "Enhance details and scale image resolution."
DESC_DENOISING_CARD = "Reduce image noise and align pixel layers."




# --- New UI & Bulk Core Keys ---
BULK_FROM = "From Project #:"
BULK_TO = "To Project #:"
BULK_MSG_RANGE_ERROR = "Start project number must be <= end number."
BULK_ERR_RETRIEVE = "Failed to load project images."
BULK_WARN_UNSUPPORTED = "Unsupported formats will be ignored."
CORE_SELECT_REF_IMAGE = "Set Reference"
CORE_DELETE_IMAGES = "Delete Selected"
CORE_MSG_CONFIRM_DELETE = "Delete selected images?"
CORE_TOOLTIP_COPY = "Right-click to copy"

# Alignment parameter tooltips
PARAMETER_DIRECT_EDIT_TOOLTIP = "You can type a value directly, then press Enter or move focus away to apply it."
AKAZE_THRESHOLD_TOOLTIP = "AKAZE feature sensitivity. Lower values detect more keypoints, useful for dark or low-texture images, but may add noisy matches. Higher values are stricter and faster."
AKAZE_OCTAVES_TOOLTIP = "Number of scale levels analyzed by AKAZE. More octaves help with larger scale changes between frames, but increase processing time."
AKAZE_OCTAVE_LAYERS_TOOLTIP = "Sub-levels inside each octave. Higher values refine scale detection, but can make feature extraction slower."
FEATURE_RATIO_THRESHOLD_TOOLTIP = "Lowe ratio test threshold for feature matching. Lower values keep only very confident matches; higher values keep more matches but may include mistakes."
FEATURE_MIN_MATCHES_TOOLTIP = "Minimum valid matches required before estimating image motion. Raise this for safer alignment; lower it only when images have very few features."
FEATURE_MAX_KEYPOINTS_TOOLTIP = "Maximum keypoints used for motion estimation. Higher values may improve difficult alignment, but increase CPU time."
FEATURE_RANSAC_THRESHOLD_TOOLTIP = "Allowed reprojection error for RANSAC. Lower is stricter and rejects more outliers; higher tolerates motion/noise but can accept wrong matches."
FEATURE_TRANSFORMATION_TOOLTIP = "Motion model used after matching. Homography handles perspective changes; affine is simpler and more stable for small camera shifts."
FEATURE_KEEP_EDGES_TOOLTIP = "Keep border pixels after warping. Disable it when you prefer cropping away uncertain edges."
FEATURE_ENABLE_CROPPING_TOOLTIP = "Crop unstable borders after alignment so the final stack uses the reliable shared image area."
PARAMETER_USE_MULTI_CORE_TOOLTIP = "Use multiple CPU cores when available. Faster on most machines, but may increase CPU usage."
ORB_NFEATURES_TOOLTIP = "Maximum ORB features to detect. Higher values give more match candidates for hard images, but require more processing."
ORB_SCALE_FACTOR_TOOLTIP = "Scale step between ORB pyramid levels. Smaller values are more detailed but slower; larger values are faster but less precise."
ORB_LEVELS_TOOLTIP = "Number of pyramid levels used by ORB. More levels help with scale changes, but increase runtime."
FARNEBACK_PYR_SCALE_TOOLTIP = "Image scale between pyramid levels. Lower values use stronger downscaling for larger motion; values near 0.5 are common."
FARNEBACK_LEVELS_TOOLTIP = "Number of pyramid levels for optical flow. More levels help track larger motion, but cost more memory and time."
FARNEBACK_WINSIZE_TOOLTIP = "Pixel window size used to estimate motion. Larger windows are smoother and robust to noise; smaller windows preserve local detail."
FARNEBACK_ITERATIONS_TOOLTIP = "Refinement passes per pyramid level. More iterations can improve flow accuracy but slow processing."
FARNEBACK_POLY_N_TOOLTIP = "Neighborhood size for polynomial expansion. 5 is sharper; 7 is smoother and more tolerant of noise."
FARNEBACK_POLY_SIGMA_TOOLTIP = "Gaussian smoothing for polynomial expansion. Higher values smooth noise but can soften fine motion."
FARNEBACK_FLAGS_TOOLTIP = "Optional Farneback flags. 0 is standard; 256 enables Gaussian windowing for smoother flow in some cases."
OPTICAL_FLOW_TILE_COLS_TOOLTIP = "Number of horizontal tiles for block flow processing. More tiles reduce memory per block but can add stitching overhead."
OPTICAL_FLOW_TILE_ROWS_TOOLTIP = "Number of vertical tiles for block flow processing. More tiles reduce memory per block but can add stitching overhead."
OPTICAL_FLOW_TILE_OVERLAP_TOOLTIP = "Tile overlap ratio. More overlap reduces seams between tiles, but increases repeated computation."
LIGHT_GLUE_MATCH_CONFIDENCE_TOOLTIP = "Light Glue match confidence threshold. Higher values keep only stronger feature pairs; lower values return more matches but may include more noise."
LIGHT_GLUE_USE_GPU_TOOLTIP = "Run Light Glue inference on the GPU when the backend is available. Useful for the neural model, but can use extra VRAM."
LUCAS_KANADE_GRID_STEP_TOOLTIP = "Distance between Lucas-Kanade grid points. Smaller values produce denser flow but run slower; larger values are faster."
LUCAS_KANADE_BORDER_MARGIN_TOOLTIP = "Safe distance from tile edges before grid points are created. A margin reduces tracking on less stable border areas."
LUCAS_KANADE_POINT_WORKERS_TOOLTIP = "Number of workers used to split grid-point tracking inside each tile. Raise it on many-core CPUs; lower it if CPU usage becomes too crowded or spiky."
LUCAS_KANADE_WIN_SIZE_TOOLTIP = "Lucas-Kanade search window size. Larger windows help wider motion; smaller windows preserve local detail."
LUCAS_KANADE_MAX_LEVEL_TOOLTIP = "Number of optical-flow pyramid levels. More levels help larger motion, but increase processing time."
LUCAS_KANADE_ITERATIONS_TOOLTIP = "Number of search iterations per tracked point. More iterations can improve accuracy, but slow the process."
LUCAS_KANADE_EPSILON_TOOLTIP = "Lucas-Kanade convergence threshold. Smaller values are more precise, but may need more iterations."
UI_STATUS_READY = "Ready"
UI_ITEMS_REMAINING = "remaining"
UI_SPLASH_LOADING = "Loading..."

PROGRESS_ALIGN = "Align: {}/{}"
PROGRESS_MERGING = "Merging: {}/{}"

# Missing Keys
MSG_DATABASE_ERROR = "Database Error"
MSG_DB_RETRIEVE_FAILED = "Failed to retrieve data from database."
MSG_FOLDER_ERROR = "Folder Error"
MSG_CREATE_FOLDER_TIFF_FAILED = "Failed to create folder for saving TIFF files."
MSG_TIFF_PROCESSING_ISSUES = "TIFF Processing Issues"
MSG_TIFF_PROCESS_FAILED_SOME = "Some TIFF files failed to process."
MSG_IMPORT_FAILED = "Import Failed"
MSG_NO_VALID_FILES_IMPORT = "No valid files found to import."
MSG_ERROR_TITLE = "Error"
MSG_IMPORT_ERROR_OCCURRED = "An error occurred during import."
MSG_CAUTION_TITLE = "Caution"
MSG_CONFIRM_TITLE = "Confirm"
MSG_WARNING_TITLE = "Warning"
MSG_ALIGN_ALGO_NOT_RECOGNIZED = "Alignment algorithm not recognized."
MSG_NO_PROCESSED_IMAGES_SAVE = "No processed images to save."
MSG_INVALID_FORMAT = "Invalid Format"
MSG_UNSUPPORTED_FORMAT_EXTENSION = "Unsupported file format or extension."
MSG_COULD_NOT_READ_SOURCE = "Could not read source file."
MSG_CLEANUP_ERROR = "Cleanup Error"
MSG_REMOVE_TEMP_FAILED = "Failed to remove temporary files."
MSG_SUCCESS_TITLE = "Success"
MSG_SUCCESS_SAVE = "Image saved successfully."
MSG_FAILED_SAVE_IMAGE = "Failed to save image."
BTN_CANCEL = "Cancel"
SIMILARITY_V2_GROUP_TITLE = "Similarity V2 Parameters"
RESET_TO_DEFAULTS_BUTTON_TEXT = "Reset to Defaults"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TITLE = "No Valid Images"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TEXT = "No valid images were selected for import."
DEVICE_ACCELERATION_LABEL = "GPU Acceleration"
BTN_TEST_BACKEND_HARDWARE = "Test Hardware Acceleration"
MSG_IMPORT_ERROR = "Import Error"
LBL_ANALYSIS_MODE = "Analysis Mode"
LBL_FAST = "Fast"
LBL_DEEP = "Deep"
MSG_HARDWARE_TEST_DEPTH = "Choose the hardware acceleration test depth:"
MSG_HARDWARE_TEST_FAST = "Quick backend compatibility check."
MSG_HARDWARE_TEST_DEEP = "Thorough per-backend validation."
MSG_BACKEND_RESTART_REQUIRED = "A restart is required to apply the new backend selection."
BTN_YES = "Yes"
BTN_NO = "No"
BTN_OK = "OK"
LBL_ETA = "ETA {0}"
LBL_TESTING = "Testing"
LBL_HARDWARE_PREPARING = "Preparing hardware backends..."
LBL_HARDWARE_BACKEND_ANALYSIS = "Hardware Backend Analysis"
MSG_BACKEND_TEST_CANCELLED = "Backend test cancelled."
LBL_INITIALIZATION_FAILED = "initialization failed"
LBL_RENDERER_UNAVAILABLE = "renderer unavailable"
LBL_UNKNOWN = "Unknown"
LBL_NO_BACKEND_RESULTS = "No backend results available."
LBL_BACKEND_COMPATIBILITY_RESULTS = "Backend Compatibility Results"
LBL_DIAGNOSTIC_LOGS = "Diagnostic logs"
MSG_BACKEND_TEST_FINISHED = "Backend test finished."
LBL_AUTO_FALLBACK = "Auto Fallback"
LBL_AUTO_FALLBACK_TIP = "When enabled, automatically fall back through CUDA, Vulkan, OpenGL, then CPU if the selected backend is unavailable."
AUTO_SHUTDOWN_LABEL = "Enable Auto Shutdown"
AUTO_SHUTDOWN_DESCRIPTION = "Close the application after the configured period without user activity."
AUTO_SHUTDOWN_TIMEOUT_LABEL = "Idle timeout (minutes)"

# --- Startup Splash Status Messages ---
SPLASH_STATUS_STARTING = "Starting application..."
SPLASH_STATUS_CHECKING_APP = "Checking application..."
SPLASH_STATUS_APP_ACTIVE = "Application active"
SPLASH_STATUS_CHECKING_PROJECT = "Checking project data..."
SPLASH_STATUS_PROJECT_READY = "Project data ready"
SPLASH_STATUS_PREPARING_EFFECTS = "Preparing visual effects..."
SPLASH_STATUS_EFFECTS_READY = "Visual effects ready"
SPLASH_STATUS_PREPARING_MODULES = "Preparing processing modules..."
SPLASH_STATUS_MODULES_READY = "Modules ready"
SPLASH_STATUS_LOADING_WINDOW = "Loading window display..."
SPLASH_STATUS_ADJUSTING_SCREEN = "Adjusting screen resolution..."
SPLASH_STATUS_SCREEN_READY = "Screen display ready"
SPLASH_STATUS_PREPARING_WORKSPACE = "Preparing workspace..."
SPLASH_STATUS_WORKSPACE_READY = "Workspace ready"
SPLASH_STATUS_LOADING_UI = "Loading main UI..."
SPLASH_STATUS_PREPARING_PAGE = "Preparing workspace page..."
SPLASH_STATUS_OPENING_MAIN_WORKSPACE = "Opening main workspace..."
SPLASH_STATUS_MAIN_WORKSPACE_READY = "Workspace ready to use"
SPLASH_STATUS_LOADING_SETTINGS = "Loading settings panel..."
SPLASH_STATUS_SETTINGS_READY = "Settings ready"
SPLASH_STATUS_ASSEMBLING_LAYOUT = "Assembling application layout..."
SPLASH_STATUS_FINISHING_SETUP = "Completing startup preparation..."
SPLASH_STATUS_PREPARING_THEME = "Preparing visual theme..."
SPLASH_STATUS_FINALIZING = "Finishing workspace setup..."

# -*- coding: utf-8 -*-

# ==============================================================================
# General UI Elements & Messages
# ==============================================================================
# Placeholder/General Info
UNDER_DEVELOPMENT = "Menu {page_name} is under development"
LOADING_THUMBNAIL = "Loading...."
NOT_IMAGE_PREVIEW = "No image available"
MODULE_NOT_IMPLEMENT = "Module not yet implemented."

# Buttons
ADD_IMAGE_BUTTON = "Add"
PREVIEW_IMAGE_BUTTON = "Preview"
DELETE_IMAGE_BUTTON = "Delete"
APPLY_PARAMETER_BUTTON_TEXT = "Apply Settings"

# Labels
PREVIEW_PANEL_LABEL = "Preview Panel"

# Window Messages
WINDOW_START_PROCESSING = "Starting process..."
WINDOW_PROCESSING_COMPLETE = "Complete!"

# Application Control
RESTART_APPLICATION_REQUIRED = "Restart Required"
RESTART_APPLICATION_DESCRIPTION = "Restart to see changes"
ACCEPT_RESTART_APPLICATION = "Restart Now"
REJECT_APPLICATION_DESCRIPTION = "Later"
COMMAND_APPLICATION_DESCRIPTION = "Reloading Application..."
TRY_RESTART_APPLICATION = "Attempting to reload application"
COMMAND_FAILED_IN_RESTART_APPLICATION = "System failed to restart."
RESTART_FAILED = "Restart Failed"
COMMAND_TO_RESTART_MANUALLY = "Could not restart the application automatically. Please restart manually."


# ==============================================================================
# Sidebar UI
# ==============================================================================
SETTINGS_SIDEBAR_LABEL= "Settings"
HDR_SIDEBAR_LABEL= "HDR Reconstruction"


# ==============================================================================
# Topbar UI
# ==============================================================================
# Single Image Actions
TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "Import Image"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "Delete Image"

# Batch Actions
TOPBAR_BATCH_IMPORT_BUTTON_TEXT = "Import Image"
TOPBAR_BATCH_DELETE_BUTTON_TEXT = "Delete Batch"
TOPBAR_BATCH_START_PROCESS_BUTTON_TEXT = "Process Batch"
TOPBAR_BATCH_SAVE_BUTTON_TEXT = "Save To"


# ==============================================================================
# Batch Processing UI & Messages
# ==============================================================================
# General Batch Info & Status
NO_DATA_BATCH = "No saved batches."
UI_LABEL_BATCH_NO_PROCESS = "No batches processed!"
UI_LABEL_BATCH_SUCCES = "All batches have been processed!"
UI_LABEL_BATCH_PROCESS = "Processing {} batches..."
UI_LABEL_MOVING_FILES = "Moving {} files to folder '{}'. Please wait..."
UI_LABEL_BATCH_PROGRESS = "{}/{} batches processed..."
PROCESSING_BATCH = "--- Processing batch {}/{} (Processed: {}) ---"
NUMBER_OF_BATCHES_TO_BE_PROCESSED = "Number of batches to be processed: {}"
BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS = "batch_id must be present for batch process"
SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED = "Skipping batch {} because no images were loaded."
BATCH_LABEL_FORMAT = "Batch {}   -   ({} images)"


SELECT_OUTPUT_FOLDER_TITLE = "Select Output Folder to Save Batch"
OUTPUT_FOLDER_SELECTION_CANCELLED = "Folder selection canceled. Process stopped."

BATCH_PROCESSING_ERROR_TITLE = "Batch Processing Error"
BATCH_PROCESSING_ERROR_MESSAGE = "Failed to process Batch {} (ID: {}):\n{}"
BATCH_SAVE_ERROR_TITLE = "Save Failed"
TARGET_FOLDER_NOT_ACCESSIBLE = "Target folder is not accessible:\n{}"
MOVE_FILE_ERROR_TITLE = "Failed to Move File"
COULD_NOT_SAVE_FILE_FOR_BATCH = "Failed to save file '{}' for batch:\n{}"
SOURCE_FILE_DOES_NOT_EXIST = "Move failed: Source file '{}' not found."
TARGET_FOLDER_INVALID = "Move failed: Target folder '{}' is invalid."

LOG_BATCH_PROCESSING_START = "Starting processing for {} batch(es)..."
LOG_PROCESSING_BATCH_DETAIL = "Processing Batch #{} (ID: {}), order ({}/{})..."
LOG_WARN_MULTIPLE_NEW_FILES = "Warning: >1 new file for Batch {}. Moved the first one: {}"
LOG_BATCH_PROCESSED_NEW_OUTPUT = "Batch {} completed, new output: {}"
LOG_BATCH_PROCESSED_NO_OUTPUT = "Batch {} completed, but no new output file in folder '{}'."
LOG_ERROR_PROCESSING_BATCH = "Error processing Batch {}: {}"
LOG_ALL_BATCH_ATTEMPTS_FINISHED = "All batch processing attempts are finished."

LOG_MOVE_SUCCESS = "Successfully moved '{}' to '{}'."
LOG_MOVE_FAILED = "Failed to move '{}' to '{}': {}"
LOG_SOURCE_FILE_NOT_FOUND = "Source file not found: {}"
LOG_TARGET_FOLDER_NOT_FOUND = "Invalid target folder: {}"

UI_LABEL_BATCH_NO_PROCESS = "No batch selected for processing."
UI_LABEL_BATCH_PROCESS_START = "Starting process for {} batch(es)..."
UI_LABEL_BATCH_PROGRESS_DONE_SAVED = "Batch {} done & saved ({}/{})."
UI_LABEL_BATCH_PROGRESS_SAVE_FAILED = "Batch {} done, save failed ({}/{})."
UI_LABEL_BATCH_PROGRESS_NO_OUTPUT = "Batch {} done, no output ({}/{})."
UI_LABEL_BATCH_PROGRESS_ERROR = "Error Batch {} ({}/{})."

UI_LABEL_BATCH_ALL_SUCCESS_SPECIFIC = "All {} batches processed & saved to {}."
UI_LABEL_BATCH_PARTIAL_SUCCESS_SPECIFIC = "{} of {} batches saved to {}. Some failed."
UI_LABEL_BATCH_NO_SUCCESS_SPECIFIC = "Process completed. No batch results saved to {}."
UI_LABEL_BATCH_NONE_PROCESSED = "No batches were processed."



# Batch Deletion
BATCH_DELETE_LABEL = "Confirm Batch Deletion", "Are you sure you want to delete batch {}?" # Tuple for Title, Message
TITLE_BATCH_ALL_DELETE_BUTTON = "Delete All Batches"
CONFIRM_BATCH_ALL_DELETE_BUTTON = "Are you sure you want to delete {} batches?"
NO_DATA_BATCH_ALL_DELETE_BUTTON = "No saved batch data."

# Batch Parameters UI Labels
PARAMETER_BATCH_CROP_EDGE = "Crop Edges"
PARAMETER_BATCH_KEEP_EDGE = "Keep Edges"
PARAMETER_BATCH_DENOISING = "Denoising"
PARAMETER_BATCH_SUPER_RESOLUTION = "Super Resolution"
PARAMETER_BATCH_ALIGNMENT = "Align Images"
PARAMETER_BATCH_ALIGNMENT_TO_FOLDER = "Save Alignment Results to Folder"
PARAMETER_BATCH_ALIGNMENT_TO_PROCESS = "Save Alignment Results for Next Process"

# Batch Saving Feedback
UI_FAILED_TO_SAVE_IMAGE_BATCH = "Failed to save image: {}"
UI_SUCCES_TO_SAVE_IMAGE_BATCH = "Image saved successfully: {}"
UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH = "No image"
UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH = "System folder (database/stack) does not exist"
UI_NO_BATCH_PROCESS = "No batch process avaiable"

# Batch Specific Errors/Warnings
ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F = "Error retrieving key {} from HDF5: {}"


# ==============================================================================
# Image Handling (Import/Delete) UI & Messages
# ==============================================================================
# Import
HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "Image Files (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES = """Drag & drop images here<br>
or<br>
Use the 'Import Image' button"""
SUPPORTED_IMAGE_EXTENSION = "Supported image formats"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Select Images"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Duplicate Images"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} images already exist in the database, will be skipped."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Selected Format"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} images with format '{format}' will be imported."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Failed", "No valid images to import." # Tuple for Title, Message
ON_IMPORT_COMPLETE_STATUS = "Import complete"
ON_IMPORT_COMPLETE_MESSAGES = "{} images were imported successfully."

# Delete
HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Failed", "No images selected." # Tuple for Title, Message
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Are you sure you want to delete the selected {} images?"


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

# Buttons in Progress Sections (if generic)
PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Start Process"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Save As"

# General Process Status/Feedback
PROCESS_ALGORITHM_PROCESS_SKIPPED = "No algorithm selected for processing"
PROCESS_TERMINATED_BY_USER = "Process Terminated By User"
LOADING_IMAGE_PATH = "Loading {num_in_this_batch} image paths..."
LOAD_IMAGE_FROM_HDF5 = "Loading {} images from HDF5..."
NO_IMAGE_PATH_PROCESSED_IMAGE = "No image paths to process."
PROCESSING_IMAGE_FROM_HDF5 = "Processing images from HDF5: {}"
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
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Image {index} saved."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "All images saved successfully."
NO_HDF5_FILE_PROCESSING_FROM_PATH = "HDF5 file not found. Processing from image paths..."

# Image Processing Steps
RUN_SAVING_REFERENCE_IMAGE = "Saving reference image."
RUN_IMAGE_PROCESSING = "Processing image {i} of {total_images}..."
RUN_IMAGE_PROCESSING_SAVING = "Image {i} saved."
RUN_IMAGE_PROCESSING_FINISHED = "Process finished."
RUN_IMAGE_PROCESS_STARTED = "Starting process..."
RUN_PROCESS_TRANSFORMATION = "[1/2] Calculating transformation {}/{}"
RUN_SAVING_TRANSFORMATION = "[2/2] Saving result {}/{}"


# Motion Compensation / Alignment Steps
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS ="Aligning and cropping image {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION ="Saving image {}/{}"
COMPENSATE_MOTION_STATUS = "Compensating motion for image {image_id}..."
COMPENSATE_MOTION_FINISHED = "Motion compensation finished for image {image_id}."

# Stacking / Denoising Steps
STACK_IMAGES_PROCESS = "Processing image {current}/{total}..."
ENHANCEMENT = "Enhancing: {}"
STARTING_ENHANCEMENT = "Starting Enhancement"
START_IMAGE_ENHANCEMENT = "--- Starting Enhancement for {} images ---"
ANALYZING_IMAGE = "Analyzing image {}/{}..."
SAVING_WEIGHT_MAP = "Weight map saved"

# Analysis Steps (e.g., Similarity)
ANALYZING_COMPLETE = "Analysis Complete"


# ==============================================================================
# Error Messages
# ==============================================================================
# General Errors
RUN_ERROR_STATUS = "An error occurred: {error}"
RUN_ERROR_MESSAGE = "An error occurred: {error}"
FAILED_TO_SAVE_IMAGE = "Failed to save final image."
FAILED_TO_CREATE_PROCESS_WINDOW = "Failed to create process window: {}"

# Image Loading / Preparation Errors
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Failed to load images"
RUN_IMAGE_NOT_FOUND = "Image not found in database."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Reference image could not be loaded from {image_paths[0]}."
RUN_IMAGE_PROCESSING_FAILED = "Failed to load image {i} from {image_paths[i]}."
FAILED_WHILE_PREPARING_IMAGE = "Failed preparing image: {}"
FAILED_TO_PREPARE_REFERENCE_IMAGE = "Failed to prepare reference image: {}"
IMAGE_LOAD_FAILED = "No images loaded."
FIRST_IMAGE_CANNOT_BE_OBTAINED = "Could not get the first image: {}"
RUN_IMAGE_PROCESS_LOAD_FAILED = "No images found in the database."

# File / System Errors
ERROR_IN_READING_FILE_HDF5 = "Error reading HDF5: {}"
FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "Transformation matrix file not found for image {}"
LIBRARY_FILE_NOT_FOUND = "Library file not found: {}"

# Processing / Algorithm Errors
ERROR_ACCUMULATE_IMAGE = "Accumulated image is None or total weights are invalid."
RUN_STACK_PROCESSING_FAILED = "Failed to stack images"
FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "Could not calculate motion for image {}"
FAIL_COMPENSATE_MOTION_PROCESS = "Estimation failed for image {}"
UNRECOGNIZED_TRANSFORMATION = "Unrecognized transformation type."
FAILED_TO_COMPUTE_TRANSFORMATION ="Could not compute transformation."
FAILED_TO_COMPUTE_CROP = "Failed to compute valid crop. Process cancelled."
FAIL_CROPPING_PROCESS = "Invalid crop. Not enough overlap."
ERROR_IN_FLOW_FIELD = "Error in image {}: Flow field input is none. Cannot compensate motion."
ERROR_IN_BASE_IMAGE = "Error in image {}: Base image input is none. Cannot compensate motion."
STACK_IMAGES_FAILED = "No images to process."
DATA_FAILED_COMPLETION_CREATED = "Completion data failed to generate. Cannot perform refinement."
FAILED_IMAGE_ENHANCEMENT = "Enhancement process failed."
ANALYSIS_FAILURE = "Analysis failed: No images were processed"
ERROR_AT_END_OF_CONVERSION = "Error at end of conversion: {}"
UNEXPECTED_NUMBER_OF_BUFFER_CHANNELS = "Internal Error: Unexpected number of buffer channels."
UNABLE_TO_SAVE_WEIGHT_MAP = "Unable to save Weight Map: {}"
FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH = "Failed to save weight map to {}"
NORMALIZATION_FAILED = "Normalization Failed: {}"
FATAL_ERROR_DURING_NORMALIZATION = "FATAL ERROR During normalization: {}"
FAILED_TO_ACCUMULATE_IMAGE= "Image {} failed to accumulate"
COLOR_CHANNEL_DOES_NOT_MATCH = "Color channels do not match."
IMAGE_CHANNEL_DOES_NOT_SUPPORT = "Unsupported image channels: {}."
DATA_TYPE_NOT_SUPPORTED = "Unsupported data type: {}."
IMAGE_BIT_REQUIRED = "Image must be 8 Bit or 16 Bit."

# Library / Dependency Errors
FAILED_TO_CONFIGURE_LIBRARY = "Failed to load/configure library {}: {}"
LIBRARY_FAILED_TO_LOAD_NORMALIZATION_FAILED = "C++ library not loaded. Skipping normalization."
LIBRARY_FAILED_TO_LOAD_ACCUMULATED_SKIPED = "C++ library not loaded. Skipping accumulation."

# GPU Errors
GPU_ERROR_AND_FALLBACK_TO_CPU = "Unexpected GPU error: {}. Falling back to CPU."

# Validation Errors
IMAGE_DATA_MUST_BE_VALID = "Items in 'images' list must be valid image data (NumPy array)."

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
  resulting in more precise image alignment. However, it increases computation time.

- Typically, a value between 500 and 1500 is sufficient for most image scenes.
  For very high accuracy needs, selecting a value between 2500 and 5000 can improve accuracy."""
ORB_SCALEFACTOR_LABEL = "Scale Factor"
ORB_SCALEFACTOR_DESCRIPTION = """Scale Factor determines the rate at which the image scale is gradually reduced during processing.

- If the value is close to 1.0, the image is downscaled slowly with more steps.
  This allows for the detection of finer details but takes longer.

- If the value is larger, the image is downscaled faster, making processing shorter,
  but some small details might be missed.

Typically, the Scale Factor value ranges between 1.2 and 1.5."""
ORB_NLEVELS_LABEL = "Number of Levels"
ORB_NLEVELS_DESCRIPTION = """The number of levels indicates the number of layers in the image pyramid used to detect features.

- More levels allow the algorithm to capture details at various scales,
  which is useful if the image sizes vary.

- However, the higher the number of levels, the longer the processing time.

For most scenes, a value between 2 and 4 is ideal."""
ORB_TRANSFORMATION_LABEL = "Transformation Type"
ORB_TRANSFORMATION_DESCRIPTION = """Select the method to align images according to your needs:

Available options include:
- HOMOGRAPHY: Suitable for photos with quite extreme angle differences (e.g., image of a table from above vs. side).
  Can adjust "perspective" effects.

- AFFINE: Can rotate, resize (can be non-uniform), and shift the image.
  Example: correcting a tilted photo that needs partial enlargement.

- SIMILARITY: Only allows uniform rotation, scaling (zoom in/out), and translation.
  Aspect ratio is maintained.

- EUCLIDEAN: The simplest: only rotates and shifts the image without changing size.
  Suitable for correcting slightly tilted photos.

Selection Advice:
- For most cases (especially photos from quite extreme angles), choose Homography.
- If the image only needs simple position/rotation adjustments, Euclidean or Similarity is more suitable.
- Use Affine only if flexible shape adjustment without perspective effects is needed."""
ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """RANSAC Threshold determines how strictly the algorithm filters out outliers
(data points that deviate significantly) when aligning images.

- A lower value (e.g., 1-2) means stricter filtering, so some important features might be ignored.

- A higher value (e.g., 4-5) is more tolerant of outliers, allowing more features to be used,
  but can reduce alignment accuracy.

Typically, a value between 1 and 3 is sufficient, depending on the level of noise in the data."""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Farneback Parameters"
FARNEBACK_PYRAMID_SCALE_LABEL = "Pyramid Scale"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Pyramid Scale is the factor that determines how much the image
is downscaled at each pyramid level.

- This value determines how much the image size is reduced (downscaled) from one level to the next.
  For example, if the value is 0.5, each level will be half the size of the previous one.

- Smaller values (around 0.10 to 0.5) cause larger size differences between levels.
  This can speed up computation but may reduce accuracy in capturing fine movements.

- Values closer to 1.00 result in smaller size changes between levels,
  allowing for more accurate motion detection, but with longer computation time.

Adjust this value according to your needs to find a balance between processing speed and
motion detection accuracy.
Recommended value: 0.5
"""
FARNEBACK_LEVELS_LABEL = "Levels"
FARNEBACK_LEVELS_DESCRIPTION = """The Levels parameter in the Farneback algorithm refers to the number of layers
  in the image pyramid used to compute optical flow.

- More levels: The algorithm can detect object movements at various sizes and speeds,
  including complex movements or those covering large areas. However, this requires
  longer computation time.

- However, the more levels used, the longer the computation time needed.

You can adjust it between 1 and 10 according to your application's needs.
Generally, a value of 3 is considered standard.
"""
FARNEBACK_WIN_SIZE_LABEL = "Window Size"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Window Size determines how large a pixel area (window)
is used in the optical flow calculation.

- Larger window size: Produces more stable and smoother motion estimation because
  information is calculated from a wider area. However, small motion details might be missed.

- Smaller window size: More sensitive to small movements,
  but noise might be mistaken for movement and it's less stable.

You can choose a value between sensitivity to small motion details
and stable results.
Recommended value: 15.
"""
FARNEBACK_ITERATIONS_LABEL = "Iterations"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterations determine how many times the optical flow calculation is refined at each pyramid level.

- More iterations lead to more accurate optical flow results.
- However, increasing the number of iterations can also slow down computation time.

Choose a value that improves accuracy without significantly slowing down the process.
Recommended value: 3.
"""
FARNEBACK_POLY_N_LABEL = "Polynomial Expansion"
FARNEBACK_POLY_N_DESCRIPTION = """Polynomial Expansion (poly_n) determines the size of the pixel neighborhood used
to estimate motion using the polynomial expansion method.

- This value determines how much surrounding pixel data is used in the calculation.

- A larger value will produce smoother motion estimates,
  but may reduce sensitivity to small movements.

Typically, values of 5 or 7 are used, depending on the desired level of detail and stability.
"""
FARNEBACK_POLY_SIGMA_LABEL = "Polynomial Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Polynomial Sigma controls the amount of smoothing
applied before the polynomial expansion is performed.

- This value is the standard deviation of the Gaussian filter used to reduce noise in the pixel data.
- A higher Sigma can help suppress noise,

  but if too high, it might remove important motion details.

Adjust carefully to reduce noise without losing significant motion details.
Recommended value: 1.2.
"""
FARNEBACK_FLAGS_LABEL = "Flags"
FARNEBACK_FLAGS_DESCRIPTION = """Flags is an optional parameter that allows
activating specific options in the Farneback algorithm.

- Flags are often used in applying a Gaussian filter for smoothing,
  this is used to produce smoother optical flow.

- If you are unsure, leave this parameter at its default value (0).

Choose the appropriate flag if you want to balance processing speed and result quality.
Recommended value: 0.
"""

# --- AKAZE Parameters ---
AKAZE_PARAMETER_SETTING_LABEL = "AKAZE Parameters"
AKAZE_THRESHOLD_LABEL = "Threshold"
AKAZE_THRESHOLD_DESCRIPTION = """The Threshold parameter determines how sensitive the detector
is when searching for a keypoint.

- Lower values increase the detection of more keypoints,
  including in images with few features and high noise.

- Higher values limit detection only to the strongest features.

Recommended value: 0.0010.
"""
AKAZE_OCTAVE_LABEL = "Number of Octaves"
AKAZE_OCTAVE_DESCRIPTION = """ parameter that controls how many scale levels will be analyzed
when searching for important features in an image. Imagine viewing an image at various zoom levels;
each zoom level is called an "octave".

- Each octave: Represents a different zoom level, allowing the algorithm to detect features at various sizes.
  For example, small features will be visible when zoomed in, while large features can be recognized at
  a further zoom level.

- More octaves: Provide the ability to detect features at more scales or sizes.
  However, the computer needs to work harder, and processing time becomes longer.

Recommended value: 4.
"""
AKAZE_LAYER_LABEL = "Layers per Octave"
AKAZE_LAYER_DESCRIPTION = """Layers per Octave determines the number of sub-levels within each octave.

- More layers provide finer scale-space resolution,
  which can improve feature detection across various scales.

- However, adding layers also increases computational load.

Recommended value: 4.
"""
AKAZE_RATIO_LABEL = "Ratio Threshold"
AKAZE_RATIO_DESCRIPTION = """Ratio Threshold is a value used when matching important features (keypoints)
between two images. The goal is to ensure that the found matches are truly accurate and not coincidental.

- Lower ratio (closer to 0.50): Only accepts very clear matches that are beyond doubt.
  In other words, it's more selective in choosing matches, reducing the likelihood of false
  keypoint matches.

- Higher ratio (closer to 1.00): Means we are more tolerant in accepting matches,
  so more matches are accepted. However, this also increases the chance of incorrect
  keypoint matches.

Recommended value: 0.80.
"""

# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "Overlap %"
OVERLAP_DESCRIPTION = """Used to reduce tile artifacts (which cause blocky effects on moving areas).

Increasing the overlap can reduce such effects but will also increase computation time."""

TILE_SIZE_LABEL = "Tile Size"
TILE_SIZE_DESCRIPTION = """The smaller the tile size, the more detailed the detection of differences.

However, it also increases computation time and the likelihood of detection errors."""

MOTION_SENSIVITY_LABEL = "Motion Sensitivity"
MOTION_SENSIVITY_DESCRIPTION = """Motion sensitivity controls how aggressively the algorithm detects differences within a tile.

Lower values make the detection more sensitive or aggressive, but may also treat noise as real differences."""

NOISE_OFFSET_LABEL = "Noise Offset"
NOISE_OFFSET_DESCRIPTION = """A threshold to ignore a certain level of noise in the image, so higher noise is not treated as motion.

Higher values can lead to cleaner stacking for extremely noisy images, but may reduce motion detection accuracy."""


# --- General Alignment Options (Edges, Crop, Saving) ---
KEEP_EDGES_LABEL = """Keep Edges"""
IGNORE_EDGE_LABEL= """Ignore Edges"""
KEEP_EDGES_DESCRIPTION = """The Keep Edges feature allows the algorithm to keep the image edges
intact during the alignment process."""

ENABLE_CROP_LABEL = """Enable
Cropping"""
DISABLE_CROP_LABEL = """Disable
Cropping"""
CROP_DESCRIPTION = """Enable Cropping to remove
unused image borders.

Note: Sometimes cropping bugs occur (very rare).
Such as very small images, or errors in cropping the image."""

ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "Save to folder"
DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = """Do not save
to folder"""
SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER = "Browse.."
DEFAULT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Default Folder"
SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Select folder"
SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """Save the aligned images to a folder.
The default folder is the Documents folder on your PC."""

ACTIVATE_SAVE_ALIGN_TO_PROCESS = """Save for
next process"""
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = """Do not save for
next process"""
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """Save images for the
denoising or super resolution process"""


# ==============================================================================
# Algorithm General Descriptions (Overview)
# ==============================================================================
# --- Alignment Algorithm Descriptions ---
ALIGNMENT_NAME = "Alignment Algorithm"
NONE_ALIGNMENT_DESCRIPTION = "No alignment will be applied."
FARNEBACK_DESCRIPTION = """This algorithm is suitable for high-level alignment requiring pixel-level precision and accuracy.
However, it is very weak against significant rotation and perspective differences."""
AKAZE_DESCRIPTION = """This algorithm is quite robust against large differences in rotation, perspective, and scale.

Quite good, but not as good as Farneback for pixel-level accuracy."""
ORB_DESCRIPTION = """Fast algorithm but less accurate for significant differences.

Suitable for images with minimal differences, and accurate on images with random textures."""

# --- Super Resolution Algorithm Descriptions ---
SUPER_RESOLUTION_NAME = "Super Resolution Algorithm"
NONE_SUPER_RESOLUTION_DESCRIPTION = "No super resolution will be applied."
INTERPOLATION_DESCRIPTION = """A simple algorithm to increase resolution using interpolation methods,
adding slight detail."""

# --- Denoising Algorithm Descriptions ---
DENOISING_NAME = "Noise Reduction Algorithm"
NONE_DENOISING_DESCRIPTION = "No noise reduction will be applied."
WEIGHTED_AVERAGE_DESCRIPTION = """Result of simplifying the similarity stacking method.
Quite good at handling small movements, but produces image artifacts on larger movements."""
AVERAGE_DESCRIPTION = """A very fast and effective stacking method for static objects and scenes.
Not suitable for moving scenes or areas, but can be combined with Farneback alignment
to remove light object movement."""
MEDIAN_DESCRIPTION = """Fast and effective for stacking, quite good on moving objects.
Very effective at removing small object movements, but artifacts appear on larger movements."""
SIMILARITY_DESCRIPTION = """Advanced stacking algorithm, very powerful in removing object movement
(very little ghosting in moving areas) and produces very few artifacts up to 85%.

Inspired by:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""
SIMILARITY_MOTION_V2_DESCRIPTION = """Similarity V2 is the result of development from the similarity v1 algorithm with several
significant improvements. This algorithm can produce cleaner images even if the input contains severe noise, thanks to its ability
to intelligently distinguish between noise, texture, and subtle movements. More reliable in low lighting, but the process runs slower
compared to the v1 version."""


# ==============================================================================
# Application Settings UI
# ==============================================================================
SETTING_GENERAL_LABEL = "General"
LANGUAGE_LABEL = "Language"
LANGUAGE_TYPE = "English", "Indonesian", "Traditional Chinese", "Malay"

GPU_ACCELERATION_LABEL = "GPU Acceleration"
MULTI_CORE_CPU = "Multi-Core CPU"
SETTINGS_SAVED = "Settings saved successfully."

CANT_READ_FILE_SETTINGS = "Warning: Unable to read the settings file '{GENERAL_SETTINGS_FILE}'. Using default values."
MULTI_CORE_CPU_DESCRIPTION = """Enabling this will boost computation speed in image processing, though it will slightly increase RAM usage.

If the computer has very limited RAM, it is recommended not to enable it."""

GPU_ACCELERATION_DESCRIPTION = """Enabling this will significantly boost computation speed, as it utilizes the GPU in its processing.

NOTE: GPU usage is currently limited to the Farneback process only; other algorithms will be implemented later."""

THUMBNAIL_LABEL = "Thumbnail"
THUMBNAIL_DESCRIPTION = """Image preview for batch process, still EXPERIMENTAL
Sometimes causes flicker or lag when adding new batch"""


NOISE_MAD_OFFSET_LABEL = "MAD Noise Factor"
NOISE_MAD_OFFSET_DESCRIPTION = """How sensitive the MAD detection is when handling high-noise images.

Higher values allow greater tolerance toward noise (i.e., less sensitivity in high-noise areas),
but they may lead to ghosting effects in those regions when motion occurs.
"""

MAD_SENSITIVITY_LABEL = "MAD Sensitivity"
MAD_SENSITIVITY_DESCRIPTION = """Determines how sensitive MAD is to differences within an image.

Higher values increase sensitivity to subtle differences, but may also raise the chance of misdetections
if the input image contains high noise.
"""

CONF_SKIP_DFT_LABEL = "Confidence to Skip DFT Process"
CONF_SKIP_DFT_DESCRIPTION = """The threshold used to bypass the DFT process when the MBM process is handling it well.

A higher value causes more processing to be carried out by MAD. Note that MAD is a coarse detection method:
it is sensitive to noise and low-contrast areas, but its advantage lies in lower computational demands.
"""

WIENER_C_FACTOR_LABEL = "Wiener C Factor"
WIENER_C_FACTOR_DESCRIPTION = """Determines how sensitive the DCT Wiener computation is in detecting differences in an image.

Lower values make it more sensitive to subtle movements, although this may increase noise
since noise itself can trigger false movements. The Wiener C Factor works in tandem with MAD Sensitivity.
"""

COARSE_MARGIN_LABEL = "Coarse Align Margin"
COARSE_MARGIN_DESCRIPTION = """The margin window used for alignment at the tile level.

It improves accuracy down to the tile level, enhancing stacking precision.
However, it can significantly impact performance if the search area is too large.
"""

# Main Content
UNDER_DEVELOPMENT = "{page_name} menu under development"

# Enhance Stack Page
TOPBAR_IMPORT_BUTTON_TEXT = "Import Image"
TOPBAR_DELETE_BUTTON_TEXT = "Delete Image"

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
RUN_PROCESS_STOPPED = "Process stopped"
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

DELETE_DEBUG_IMAGES_STATUS = "Deleting debug images..."
DELETE_DEBUG_IMAGES_ONE_BY_ONE = "Deleting debug image {image_id}..."
DELETE_DEBUG_IMAGES_FINISHED = "Debug images have been successfully deleted."

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
STACK_AVERAGE_IMAGES_PROCESS = "Processing image {current}/{total}..."

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
SIMILARITY_MNFR_LOAD_FAILED = "No images provided."
SIMILARITY_MNFR_BIT_REQUIRED = "Images must be 8 Bit or 16 Bit."
SIMILARITY_MNFR_TILE_SLICE = "Image dimensions: {height}x{width}, Tile size: {tile_size}"
SIMILARITY_MNFR_SIZE_FAILED = "Image size {i} does not match the reference image."
SIMILARITY_MNFR_PROCESS_SUCCESS = "Image {i}/{count} processed successfully."
SIMILARITY_MNFR_PROCESS_FINISHED = "Stacking complete."
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Stacking batch to {current} from {total}"


# Super Resolution

WINDOW_TITLE_INTERPOLATION = "Interpolation Super Resolution"


# Deskripsi untuk Alignment Algorithm
ALIGNMENT_NAME = "Alignment Algorithm"
NONE_ALIGNMENT_DESCRIPTION = "No alignment will be applied."
FARNEBACK_DESCRIPTION = "This algorithm is suitable for high-level alignment that requires\
                        \nprecision and accuracy down to the pixel level.\
                        \n\
                        \nBut very weak against significant rotation and perspective differences"
AKAZE_DESCRIPTION = "This algorithm is quite robust to large differences in rotation, perspective and scale\
                    \n\
                    \nGood enough but not as good as farneback for pixel level."
ORB_DESCRIPTION = "Fast algorithm but less accurate for significant differences\
                    \n\
                    \nSuitable for images with minimal differences"

# Deskripsi untuk Super Resolution
SUPER_RESOLUTION_NAME = "Super Resolution Algorithm"
NONE_SUPER_RESOLUTION_DESCRIPTION = "No super-resolution will be applied."
INTERPOLATION_DESCRIPTION = "A simple algorithm to increase resolution by interpolation, adding a little detail."

# Deskripsi untuk Denoising
DENOISING_NAME = "Denoising Algorithm" 
NONE_DENOISING_DESCRIPTION = "No noise reduction will be applied."                    
WEIGHTED_AVERAGE_DESCRIPTION = "The result of the simplification of the similarity stacking method is quite good for small movements\
                        \n\
                        \nQuite good at dealing with small movements, but produces image artifacts in larger movements"
                    
AVERAGE_DESCRIPTION = "Very fast and effective stacking method for static objects and scenes\
                    \n\
                    \nNot suitable for moving scenes or areas but can be combined with farneback alignment\
                    \nto eliminate slight object movement."

MEDIAN_DESCRIPTION = "Fast and effective for stacking, quite good on moving objects\
                    \n\
                    \nVery effective at removing object movement up to 12 frames, but artifacts appear on moving\
                    \nobjects after that"
                    
SIMILARITY_DESCRIPTION = "Advanced stacking algorithm, very powerful in removing object movement (no ghosting in moving areas)\
                        \nand very few artifacts produced up to 90%\
                        \n\nInspired by:\
                        \nMonod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.\
                        \nImage Processing On Line, 11, 142–169. https://doi.org/10.5201/ipol.2021.336"
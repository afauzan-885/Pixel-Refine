# -*- coding: utf-8 -*-

# ==============================================================================
# General UI Elements & Messages
# ==============================================================================
# Placeholder/General Info
UNDER_DEVELOPMENT = "Menu {page_name} sedang dalam pembangunan"
LOADING_THUMBNAIL = "Memuatkan...."
NOT_IMAGE_PREVIEW = "Tiada imej tersedia"
MODULE_NOT_IMPLEMENT = "Modul belum dilaksanakan."

# Buttons
ADD_IMAGE_BUTTON = "Tambah"
PREVIEW_IMAGE_BUTTON = "Pratonton"
DELETE_IMAGE_BUTTON = "Padam"
CLOSE_BUTTON = "Tutup"
APPLY_PARAMETER_BUTTON_TEXT = "Guna Tetapan"
APPY_PARAMETER = "Guna"
CANCEL_PARAMETER = "Batal"

# Labels
PREVIEW_PANEL_LABEL = "Panel Pratonton"

# Window Messages
WINDOW_START_PROCESSING = "Memulakan proses..."
WINDOW_PROCESSING_COMPLETE = "Selesai!"

# Application Control
RESTART_APPLICATION_REQUIRED = "Mula Semula Diperlukan"
RESTART_APPLICATION_DESCRIPTION = "Mula semula untuk melihat perubahan"
ACCEPT_RESTART_APPLICATION = "Mula Semula"
REJECT_APPLICATION_DESCRIPTION = "Nanti"
COMMAND_APPLICATION_DESCRIPTION = "Memuat Semula Aplikasi..."
TRY_RESTART_APPLICATION = "Mencuba memuat semula aplikasi"
COMMAND_FAILED_IN_RESTART_APPLICATION = "Sistem gagal dimulakan semula."
RESTART_FAILED = "Mula Semula Gagal"
COMMAND_TO_RESTART_MANUALLY = "Tidak dapat memulakan semula aplikasi secara automatik. Sila mulakan semula secara manual."
EXIT_APPLICATION_TITLE = "Keluar Aplikasi"
EXIT_APPLICATION_MESSAGE = "Adakah anda mahu keluar dari aplikasi?"
EXIT_APPLICATION_YES = "Ya"
EXIT_APPLICATION_NO = "Tidak"
PROJECT_SAVE_CHANGES_TITLE = "Simpan Projek"
PROJECT_SAVE_CHANGES_MESSAGE = "Projek ini mempunyai perubahan yang belum disimpan. Simpan sebelum keluar?"
PROJECT_SAVE_CHANGES_SAVE = "Simpan"
PROJECT_SAVE_CHANGES_DISCARD = "Jangan Simpan"
PROJECT_SAVE_CHANGES_CANCEL = "Batal"
EXIT_APPLICATION_APPLY_BACKEND_TITLE = "Perubahan Backend"
MSG_BACKEND_EXIT_REQUIRED = "Keluar dari aplikasi dan jalankan semula untuk menggunakan pemilihan backend baharu?"

# ==============================================================================
# Sidebar UI
# ==============================================================================

SETTINGS_SIDEBAR_LABEL = "Tetapan"
PANORAMA_SIDEBAR_LABEL = "Panorama"

# ==============================================================================
# Topbar UI
# ==============================================================================
# Single Image Actions
TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "Import Imej"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "Padam Imej"

# Batch Actions
TOPBAR_BATCH_IMPORT_BUTTON_TEXT = "Import Imej"
TOPBAR_BATCH_DELETE_BUTTON_TEXT = "Padam Batch"
TOPBAR_BATCH_START_PROCESS_BUTTON_TEXT = "Proses Batch"
TOPBAR_BATCH_SAVE_BUTTON_TEXT = "Simpan Ke"

# ==============================================================================
# Batch Processing UI & Messages
# ==============================================================================
# General Batch Info & Status
NO_DATA_BATCH = "Tiada batch yang disimpan."
UI_NO_CHANGE = "Tidak Berubah"
UI_ALGORITHM_EDIT_HEADER = "Edit Algoritma secara pukal"
UI_BATCH_HEADER = "Proses Batch"
UI_ALGORIHM_EDIT = "Edit Algoritma"
UI_ALGORITHM_NOT_SET = "Algoritma belum dipilih."
UI_FOLDER_PATH_NOT_SET = "Folder destinasi belum ditetapkan."
UI_BATCH_NOT_CONFIGURE = "Batch belum dikonfigurasi."
UI_LABEL_BATCH_NO_PROCESS = "Tiada batch yang sedang diproses!"
UI_LABEL_BATCH_SUCCES = "Semua batch telah diproses!"
UI_LABEL_BATCH_PROCESS = "Memproses {} batch..."
UI_LABEL_BATCH_PROGRESS = "{}/{} batch telah diproses..."
UI_LABEL_MOVING_FILES = "Memindahkan {} fail ke folder '{}'. Sila tunggu..."
PROCESSING_BATCH = "--- Memproses batch {}/{} (Telah diproses: {}) ---"
NUMBER_OF_BATCHES_TO_BE_PROCESSED = "Bilangan batch yang akan diproses: {}"
BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS = "batch_id mesti ada untuk proses batch"
SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED = "Melangkau batch {} kerana tiada imej yang dimuatkan."
BATCH_LABEL_FORMAT = "Batch {}   -   ({} imej)"
BATCH_CANCELED_BY_USER = "Proses batch dibatalkan oleh pengguna."
BATCH_CANCELED_HEADER = "Batch Dibatalkan"
BATCH_CANCELED_INFO = "Dibatalkan"
BATCH_CANCELED_PROCESS = "Batalkan Proses"
BATCH_CANCELED_CONFIRMATION = "Adakah anda pasti mahu membatalkan semua proses yang sedang berjalan?"
BATCH_QUEUE = "Menunggu"
BATCH_SUCCESS = "Proses batch selesai."
BATCH_SUCCESS_HEADER = "Selesai"

# --- Dialogue Title ---
SELECT_OUTPUT_FOLDER_TITLE = "Pilih Folder Output untuk Simpan Batch"
OUTPUT_FOLDER_SELECTION_CANCELLED = "Pemilihan folder dibatalkan. Proses dihentikan."
ALGORITHM_SUCCESS_UPDATE = "Tetapan algoritma berjaya dikemas kini untuk batch {} hingga {}."

# --- General Error Messages & Dialogs ---
BATCH_PROCESSING_ERROR_TITLE = "Ralat Pemprosesan Batch"
BATCH_PROCESSING_ERROR_MESSAGE = "Gagal memproses Batch {} (ID: {}):\n{}"
BATCH_SAVE_ERROR_TITLE = "Gagal Menyimpan"
TARGET_FOLDER_NOT_ACCESSIBLE = "Folder destinasi tidak dapat diakses:\n{}"
MOVE_FILE_ERROR_TITLE = "Gagal Memindahkan Fail"
COULD_NOT_SAVE_FILE_FOR_BATCH = "Gagal menyimpan fail '{}' untuk batch:\n{}"
SOURCE_FILE_DOES_NOT_EXIST = "Gagal pindah: Fail sumber '{}' tidak ditemui."
TARGET_FOLDER_INVALID = "Gagal pindah: Folder destinasi '{}' tidak sah."
BATCH_CONFIGURATION_INFO = "Batch belum dikonfigurasi"

BATCH_PROCESSING_ERROR_REPORT_TITLE = "Laporan Ralat Pemprosesan Batch"
BATCH_PROCESSING_ERROR_REPORT_INTRO = "Proses selesai dengan {num_failed} daripada {num_total} batch gagal diproses. Butiran:"
BATCH_PROCESSING_ERROR_REPORT_ITEM = "• Batch #{seq} (ID: {id})\n  Sebab: {error}"

# --- Log Message
LOG_BATCH_PROCESSING_START = "Memulakan pemprosesan untuk {} batch..."
LOG_PROCESSING_BATCH_DETAIL = "Memproses Batch ke-{} (ID: {}), urutan ({}/{})..."
LOG_WARN_MULTIPLE_NEW_FILES = "Amaran: Terdapat >1 fail baharu untuk Batch {}. Memindahkan yang pertama: {}"
LOG_BATCH_PROCESSED_NEW_OUTPUT = "Batch {} selesai, output baharu: {}"
LOG_BATCH_PROCESSED_NO_OUTPUT = "Batch {} selesai, tetapi tiada fail output baharu dijumpai dalam folder '{}'."
LOG_ERROR_PROCESSING_BATCH = "Ralat semasa memproses Batch {}: {}"
LOG_ALL_BATCH_ATTEMPTS_FINISHED = "Semua percubaan pemprosesan batch telah selesai."

LOG_MOVE_SUCCESS = "Berjaya memindahkan '{}' ke '{}'."
LOG_MOVE_FAILED = "Gagal memindahkan '{}' ke '{}': {}"
LOG_SOURCE_FILE_NOT_FOUND = "Fail sumber tidak ditemui: {}"
LOG_TARGET_FOLDER_NOT_FOUND = "Folder destinasi tidak sah: {}"

# Toast message for process_all_batches
UI_LABEL_BATCH_NO_PROCESS = "Tiada batch dipilih untuk diproses."
UI_LABEL_BATCH_PROCESS_START = "Memulakan proses untuk {} batch..."
UI_LABEL_BATCH_PROGRESS_DONE_SAVED = "Batch {} selesai & disimpan ({}/{})."
UI_LABEL_BATCH_PROGRESS_SAVE_FAILED = "Batch {} selesai, gagal simpan ({}/{})."
UI_LABEL_BATCH_PROGRESS_NO_OUTPUT = "Batch {} selesai, tanpa output ({}/{})."
UI_LABEL_BATCH_PROGRESS_ERROR = "Ralat Batch {} ({}/{})."

# Final Finished Toast Message
UI_LABEL_BATCH_ALL_SUCCESS_SPECIFIC = "Semua {} batch berjaya diproses & disimpan ke {}."
UI_LABEL_BATCH_PARTIAL_SUCCESS_SPECIFIC = "{} daripada {} batch disimpan ke {}. Sebahagiannya bermasalah."
UI_LABEL_BATCH_NO_SUCCESS_SPECIFIC = "Proses selesai. Tiada hasil batch yang disimpan ke {}."
UI_LABEL_BATCH_NONE_PROCESSED = "Tiada batch yang diproses."

# Batch Deletion
BATCH_DELETE_LABEL = "Sahkan Padam Batch", "Adakah anda pasti mahu memadam batch {}?"
TITLE_BATCH_ALL_DELETE_BUTTON = "Padam Semua Batch"
CONFIRM_BATCH_ALL_DELETE_BUTTON = "Anda pasti mahu memadam {} batch?"
NO_DATA_BATCH_ALL_DELETE_BUTTON = "Tiada data batch yang disimpan."

# Batch Parameters UI Labels
PARAMETER_BATCH_CROP_EDGE = "Potong Tepi"
PARAMETER_BATCH_KEEP_EDGE = "Kekalkan Tepi"
PARAMETER_BATCH_DENOISING = "Denoising"
PARAMETER_BATCH_SUPER_RESOLUTION = "Super Resolusi"
PARAMETER_BATCH_ALIGNMENT = "Jajarkan Imej"
PARAMETER_BATCH_ALIGNMENT_TO_FOLDER = "Simpan Hasil Penjajaran ke dalam Folder"
PARAMETER_BATCH_ALIGNMENT_TO_PROCESS = "Simpan Hasil Penjajaran untuk proses Seterusnya"

# Batch Saving Feedback
UI_FAILED_TO_SAVE_IMAGE_BATCH = "Gagal menyimpan imej: {}"
UI_SUCCES_TO_SAVE_IMAGE_BATCH = "Imej berjaya disimpan: {}"
UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH = "Tiada imej untuk disimpan"
UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH = "Folder sistem (pangkalan data/tindanan) tidak wujud"
UI_NO_BATCH_PROCESS = "Tiada batch yang tersedia"

# Batch Specific Errors/Warnings
ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F = "Berlaku ralat semasa mengambil kunci {} dari HDF5: {}"

# ==============================================================================
# Image Handling (Import/Delete) UI & Messages
# ==============================================================================
# Import
HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "Fail Imej (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES = """Seret & lepas imej ke sini<br>
atau<br>
Gunakan butang 'Import Imej'"""
SUPPORTED_IMAGE_EXTENSION = "Format imej yang disokong"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Pilih Imej"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Imej Pendua"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} imej sudah wujud dalam pangkalan data, akan dilangkau."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Format Terpilih"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} imej dengan format '{format}' akan diimport."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Gagal", "Tiada imej yang sah untuk diimport." # Tuple for Title, Message
ON_IMPORT_COMPLETE_STATUS = "Import selesai"
ON_IMPORT_COMPLETE_MESSAGES = "{} imej telah berjaya diimport."

# Delete
HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Gagal", "Tiada imej yang dipilih." # Tuple for Title, Message
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Adakah anda pasti mahu memadam {} imej yang dipilih?"

# ==============================================================================
# Preview Panel UI & Messages
# ==============================================================================
UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Memproses imej, sila tunggu..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "Tiada imej yang dipilih."

# ==============================================================================
# Progress & Status Messages (General)
# ==============================================================================
# Progress Bar
UPDATE_PROGRESS_BAR_STATUS = "{}% ({} proses berbaki)"
OVERALL_PROGRESS = "Kemajuan keseluruhan:"

# Buttons in Progress Sections (if generic)
PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Mula Proses"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Simpan Sebagai"

# General Process Status/Feedback
PROCESS_ALGORITHM_PROCESS_SKIPPED = "Tiada algoritma yang dipilih untuk pemprosesan"
PROCESS_TERMINATED_BY_USER = "Proses Ditamatkan Oleh Pengguna"
LOADING_IMAGE_PATH = "Memuatkan {num_in_this_batch} laluan imej..."
LOAD_IMAGE_FROM_HDF5 = "Memuatkan {} imej dari HDF5..."
NO_IMAGE_PATH_PROCESSED_IMAGE = "Tiada laluan imej untuk diproses."
PROCESSING_IMAGE_FROM_HDF5 = "Memproses imej dari HDF5: {}"
OUTPUT_SAVE_WEIGHT_MAP = "Peta pemberat akan disimpan ke: {}"
OUTPUT_IMAGE_TO_BE_SAVED = "Output imej akan disimpan ke: {}"
NO_IMAGES_PROCESSED = "Tiada imej yang boleh diproses"
NUMBER_OF_IMAGES_TO_BE_PROCESSED = "Bilangan imej yang akan diproses: {}"
RETURNING_IMAGE_RESULTS = "Mengembalikan hasil ({}/{} imej)."
FINISHING_ANALYSIS = "Menyelesaikan Analisis"
IMAGE_PROCESS_FINISHED = "Penindanan selesai."
IMAGE_PROCESS_IN_PROGRESS = "Memproses imej {} dari {}"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Menindan batch ke-{current} dari {total}"

# ==============================================================================
# Core Processing Messages (Status & Logs)
# ==============================================================================
# General Logging
CONSOL_LOG_RUNNING_ALGORITHM = "Proses {} dipilih, algoritma: {}"

# HDF5 Saving/Loading
SAVE_TO_HDF5_ALIGNED_SAVING = "Menyimpan imej yang telah dijajarkan"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Imej ke-{index} telah disimpan."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "Semua imej berjaya disimpan."
NO_HDF5_FILE_PROCESSING_FROM_PATH = "Fail HDF5 tidak ditemui. Memproses dari laluan imej..."

# Image Processing Steps
RUN_SAVING_REFERENCE_IMAGE = "Menyimpan imej rujukan."
RUN_IMAGE_PROCESSING = "Memproses imej {} dari {}..."
RUN_IMAGE_PROCESSING_SAVING = "Imej ke-{i} telah disimpan."
RUN_IMAGE_PROCESSING_FINISHED = "Proses selesai."
RUN_IMAGE_PROCESS_STARTED = "Memulakan proses..."
RUN_PROCESS_TRANSFORMATION = "[1/2] Kira transformasi {}/{}"
RUN_SAVING_TRANSFORMATION = "[2/2] Simpan hasil {}/{}"

# Motion Compensation / Alignment Steps
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS = "Menjajarkan dan memotong imej {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION = "Menyimpan imej {}/{}"
COMPENSATE_MOTION_STATUS = "Melakukan pampasan gerakan pada imej {image_id}..."
COMPENSATE_MOTION_FINISHED = "Pampasan gerakan selesai untuk imej {image_id}."

# Stacking / Denoising Steps
STACK_IMAGES_PROCESS = "Memproses imej {current}/{total}..."
ENHANCEMENT = "Mempertingkat: {}"
STARTING_ENHANCEMENT = "Memulakan Peningkatan"
START_IMAGE_ENHANCEMENT = "--- Memulakan Peningkatan {} imej ---"
ANALYZING_IMAGE = "Menganalisis imej {}/{}..."
SAVING_WEIGHT_MAP = "Peta pemberat disimpan"

# Analysis Steps (e.g., Similarity)
ANALYSIS_STEP_ONE = "Laluan 1/2: Mencipta Data Adegan..."
ANALYSIS_STEP_ONE_PROGRESS = "Laluan 1/2: Menganalisis bingkai {}/{}"
ANALYSIS_STEP_TWO = "{} Menggabungkan Data..."
ANALYSIS_STEP_TWO_PROGRESS = "{} Menggabungkan imej {}/{}"
ANALYZING_COMPLETE = "Analisis Selesai"

# ==============================================================================
# Error Messages
# ==============================================================================
# General Errors
RUN_ERROR_STATUS = "Berlaku ralat: {error}"
RUN_ERROR_MESSAGE = "Berlaku ralat: {error}"
FAILED_TO_SAVE_IMAGE = "Gagal menyimpan imej akhir."
FAILED_TO_CREATE_PROCESS_WINDOW = "Gagal mencipta tetingkap proses: {}"

# Image Loading / Preparation Errors
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Gagal memuatkan imej"
RUN_IMAGE_NOT_FOUND = "Imej tidak ditemui dalam pangkalan data."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Imej rujukan tidak dapat dimuatkan dari {image_paths[0]}."
RUN_IMAGE_PROCESSING_FAILED = "Gagal memuatkan imej {i} dari {image_paths[i]}."
FAILED_WHILE_PREPARING_IMAGE = "Gagal menyediakan imej: {}"
FAILED_TO_PREPARE_REFERENCE_IMAGE = "Gagal menyediakan imej rujukan: {}"
IMAGE_LOAD_FAILED = "Tiada imej yang dimuatkan."
FIRST_IMAGE_CANNOT_BE_OBTAINED = "Tidak dapat memperoleh imej pertama: {}"
RUN_IMAGE_PROCESS_LOAD_FAILED = "Tidak ditemui imej dalam pangkalan data."

# File / System Errors
ERROR_IN_READING_FILE_HDF5 = "Ralat membaca HDF5: {}"
FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "Fail matriks transformasi tidak ditemui untuk imej ke-{}"
LIBRARY_FILE_NOT_FOUND = "Fail pustaka tidak ditemui: {}"

# Processing / Algorithm Errors
ERROR_ACCUMULATE_IMAGE = "Imej terkumpul adalah None atau jumlah pemberat tidak sah."
RUN_STACK_PROCESSING_FAILED = "Gagal melakukan penindanan imej"
FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "Pengiraan gerakan tidak dapat dihitung untuk imej ke-{}"
FAIL_COMPENSATE_MOTION_PROCESS = "Anggaran gagal pada imej ke-{}"
UNRECOGNIZED_TRANSFORMATION = "Jenis transformasi tidak dikenali."
FAILED_TO_COMPUTE_TRANSFORMATION = "Transformasi tidak dapat dihitung."
FAILED_TO_COMPUTE_CROP = "Gagal mengira potongan yang sah. Proses dibatalkan."
FAIL_CROPPING_PROCESS = "Potongan tidak sah. Pertindihan tidak mencukupi"
ERROR_IN_FLOW_FIELD = "Ralat pada imej {}: Input medan aliran adalah none. Tidak dapat memberi pampasan gerakan."
ERROR_IN_BASE_IMAGE = "Ralat pada imej {}: Input imej_asas adalah none. Tidak dapat memberi pampasan gerakan."
STACK_IMAGES_FAILED = "Tiada imej untuk diproses."
DATA_FAILED_COMPLETION_CREATED = "Data peningkatan gagal dijana. Tidak dapat melakukan peningkatan."
FAILED_IMAGE_ENHANCEMENT = "Proses peningkatan gagal."
ANALYSIS_FAILURE = "Analisis gagal: Tiada imej yang diproses"
ERROR_AT_END_OF_CONVERSION = "Ralat pada akhir penukaran: {}"
UNEXPECTED_NUMBER_OF_BUFFER_CHANNELS = "Ralat Dalaman: Bilangan saluran penimbal yang tidak dijangka."
UNABLE_TO_SAVE_WEIGHT_MAP = "Tidak dapat menyimpan Peta Pemberat: {}"
FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH = "Gagal menyimpan peta pemberat ke {}"
NORMALIZATION_FAILED = "Penormalan Gagal: {}"
FATAL_ERROR_DURING_NORMALIZATION = "RALAT KRITIKAL Semasa penormalan: {}"
FAILED_TO_ACCUMULATE_IMAGE = "Pada imej {} gagal dikumpulkan"
COLOR_CHANNEL_DOES_NOT_MATCH = "Saluran warna tidak sepadan."
IMAGE_CHANNEL_DOES_NOT_SUPPORT = "Saluran warna yang tidak disokong: {}."
DATA_TYPE_NOT_SUPPORTED = "Jenis data tidak disokong: {}."
IMAGE_BIT_REQUIRED = "Imej mestilah bersaiz 8 Bit atau 16 Bit."

# Library / Dependency Errors
FAILED_TO_CONFIGURE_LIBRARY = "Gagal memuat/mengkonfigurasi pustaka {}: {}"
LIBRARY_FAILED_TO_LOAD_NORMALIZATION_FAILED = "Pustaka C++ tidak dimuatkan. Penormalan dilangkau."
LIBRARY_FAILED_TO_LOAD_ACCUMULATED_SKIPED = "Pustaka C++ tidak dimuatkan. Pengumpulan dilangkau."

# GPU Errors
GPU_ERROR_AND_FALLBACK_TO_CPU = "Ralat GPU yang tidak dijangka: {}. Proses menggunakan CPU."

# Validation Errors
IMAGE_DATA_MUST_BE_VALID = "Item dalam senarai 'imej' mestilah data imej yang sah (tatasusunan NumPy)."

# ==============================================================================
# Confirmation Dialogs / Warnings
# ==============================================================================
NO_ALIGNMENT_PROCESS = "Adakah anda pasti tidak mahu menjajarkan imej terlebih dahulu?"
CANCEL_PROCESSING = "Adakah anda pasti mahu membatalkan proses?"
# Note: Batch deletion confirmations are kept within the Batch section for context

# ==============================================================================
# Algorithm Specific Window Titles
# ==============================================================================
# Alignment
WINDOW_TITLE_FARNEBACK = "Penjajaran Aliran Optik Farneback"
WINDOW_TITLE_AKAZE = "Penjajaran AKAZE"
WINDOW_TITLE_ORB = "Penjajaran ORB"
WINDOW_TITLE_LIGHT_GLUE = "Penjajaran Light Glue"

# Denoising / Stacking
WINDOW_TITLE_AVERAGE = "Penindanan Purata"
WINDOW_TITLE_MEDIAN = "Penindanan Median"
WINDOW_TITLE_SIMILARITY = "Penindanan Keserupaan"
WINDOW_TITLE_SIMILARITY_V2 = "Penindanan Keserupaan V2"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Super Resolusi Interpolasi"

# ==============================================================================
# Algorithm Parameter Settings UI (Labels & Descriptions)
# ==============================================================================
DEFAULT_PARAMETER_SETTING_LABEL = """Pilih algoritma untuk melihat parameternya."""

# --- ORB Parameters ---
ORB_PARAMETER_SETTING_LABEL = "Parameter ORB"
ORB_NFEATURES_LABEL = "Bilangan Ciri"
ORB_NFEATURES_DESCRIPTION = """Jumlah butiran imej yang dikenal pasti.
- Lebih Tinggi: Penyelarasan lebih tepat, tetapi proses menjadi lambat.
- Cadangan: 500 hingga 1500 (biasa); 2500 hingga 5000 (ketepatan tinggi)."""
ORB_SCALEFACTOR_LABEL = "Faktor Skala"
ORB_SCALEFACTOR_DESCRIPTION = """Kadar pengecilan saiz imej semasa diproses.
- Dekat 1.0: Pengecilan perlahan, butiran sangat terjaga, tetapi proses lambat.
- Lebih Tinggi: Proses lebih cepat, butiran kecil mungkin terlepas.
- Cadangan: 1.2 hingga 1.5."""
ORB_NLEVELS_LABEL = "Bilangan Aras"
ORB_NLEVELS_DESCRIPTION = """Bilangan lapisan saiz imej (lapisan piramid) untuk mengesan ciri.
- Lebih Tinggi: Kesan lebih baik untuk saiz berbeza, tetapi proses lambat.
- Cadangan: 2 hingga 4."""
ORB_TRANSFORMATION_LABEL = "Jenis Transformasi"
ORB_TRANSFORMATION_DESCRIPTION = """Pilih kaedah penyelarasan imej mengikut keperluan:
- HOMOGRAPHY: Terbaik untuk sudut pandang berbeza (senget/perspektif).
- AFFINE: Membetulkan putaran, skala, dan kecondongan imej.
- SIMILARITY: Mengekalkan nisbah saiz imej semasa putaran dan peralihan.
- EUCLIDEAN: Hanya memutar dan menggeser imej tanpa mengubah saiz."""
ORB_RANSAC_LABEL = "Ambang RANSAC"
ORB_RANSAC_DESCRIPTION = """Tahap ketat penapisan titik yang tidak selaras.
- Rendah (1-2): Sangat ketat, ketepatan tinggi, tetapi mudah gagal jika imej kurang butiran.
- Tinggi (4-5): Lebih bertoleransi, meningkatkan kadar kejayaan tetapi ketepatan berkurang sedikit.
- Cadangan: 1 hingga 3."""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Parameter Farneback"
FARNEBACK_PYRAMID_SCALE_LABEL = "Skala Piramid"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Faktor skala pengecilan imej pada setiap tahap piramid.
- Dekat 1.0: Perubahan lancar, ketepatan gerak tinggi, tetapi proses lambat.
- Nilai 0.5: Imej mengecil separuh pada setiap tahap, seimbang antara kelajuan dan ketepatan.
- Cadangan: 0.5."""
FARNEBACK_LEVELS_LABEL = "Aras"
FARNEBACK_LEVELS_DESCRIPTION = """Bilangan lapisan piramid untuk mengira pergerakan objek.
- Lebih Banyak: Kesan gerakan besar atau kompleks dengan lebih baik, proses lebih lama.
- Cadangan: 3."""
FARNEBACK_WIN_SIZE_LABEL = "Saiz Tetingkap"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Saiz tetingkap piksel yang digunakan untuk mengira gerakan.
- Lebih Besar: Anggaran gerakan lebih stabil, tetapi butiran kecil terlepas.
- Lebih Kecil: Sensitif pada gerakan kecil, tetapi noise mudah dianggap sebagai gerakan.
- Cadangan: 15."""
FARNEBACK_ITERATIONS_LABEL = "Lelaran"
FARNEBACK_ITERATIONS_DESCRIPTION = """Bilangan ulangan pengiraan gerakan pada setiap tahap piramid.
- Lebih Banyak: Hasil gerakan lebih tepat, tetapi proses lambat.
- Cadangan: 3."""
FARNEBACK_POLY_N_LABEL = "Pengembangan Polinomial"
FARNEBACK_POLY_N_DESCRIPTION = """Saiz kawasan piksel untuk menganggarkan model gerakan.
- Lebih Besar: Gerakan lebih lancar, tetapi kurang sensitif pada gerakan sangat kecil.
- Cadangan: 5 atau 7."""
FARNEBACK_POLY_SIGMA_LABEL = "Sigma Polinomial"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Tahap perataan Gaussian untuk menapis noise imej.
- Lebih Tinggi: Noise ditapis lebih bersih, tetapi butiran gerakan penting boleh kabur.
- Cadangan: 1.2."""
FARNEBACK_FLAGS_LABEL = "Bendera (Flag)"
FARNEBACK_FLAGS_DESCRIPTION = """Bendera (Flag) ialah parameter pilihan yang membolehkan
pengaktifan opsyen tertentu dalam algoritma Farneback.

- Bendera sering digunakan dalam penerapan penapis Gaussian untuk pelicinan,
  ini digunakan untuk menghasilkan aliran optik yang lebih licin.

- Jika anda ragu-ragu, biarkan parameter ini pada nilai lalai (0).

Pilih bendera yang sesuai jika anda ingin mengimbangi antara kelajuan proses dan kualiti hasil.
Nilai yang disyorkan: 0.
"""

# --- AKAZE Parameters ---
AKAZE_PARAMETER_SETTING_LABEL = "Parameter AKAZE"
AKAZE_THRESHOLD_LABEL = "Ambang"
AKAZE_THRESHOLD_DESCRIPTION = """Tahap sensitiviti pengesan dalam mencari titik ciri imej.
- Lebih Rendah: Lebih sensitif (sesuai untuk imej kurang butiran/tinggi noise).
- Lebih Tinggi: Hanya mengesan ciri yang sangat ketara.
- Cadangan: 0.001."""
AKAZE_OCTAVE_LABEL = "Bilangan Oktaf"
AKAZE_OCTAVE_DESCRIPTION = """Bilangan tahap zoom imej yang dianalisis.
- Lebih Banyak: Kesan ciri pada pelbagai skala dengan konsisten, tetapi proses lambat.
- Cadangan: 4."""
AKAZE_LAYER_LABEL = "Bilangan Lapisan setiap Oktaf"
AKAZE_LAYER_DESCRIPTION = """Bilangan sub-lapisan dalam setiap tahap zoom.
- Lebih Banyak: Kesan skala imej lebih halus, pengiraan bertambah.
- Cadangan: 4."""
AKAZE_RATIO_LABEL = "Ambang Nisbah"
AKAZE_RATIO_DESCRIPTION = """Keketatan padanan ciri antara imej.
- Rendah (0.5 - 0.7): Padanan sangat ketat, mengelakkan padanan palsu.
- Tinggi (0.8 - 0.9): Lebih bertoleransi, padanan lebih banyak tetapi risiko padanan palsu naik.
- Cadangan: 0.8."""

# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "Pertindihan %"
OVERLAP_DESCRIPTION = """Kawasan bertindih antara petak (tile).
- Lebih Tinggi: Mengurangkan kesan kotak pada kawasan bergerak, proses lambat."""

TILE_SIZE_LABEL = "Saiz Jubin (tile)"
TILE_SIZE_DESCRIPTION = """Saiz blok pemrosesan imej.
- Lebih Kecil: Mengesan perbezaan lebih halus, tetapi proses lambat.
- Lebih Besar: Proses cepat, tetapi perbezaan kecil mungkin terlepas."""

MOTION_SENSIVITY_LABEL = """Kepekaan Gerakan"""
MOTION_SENSIVITY_DESCRIPTION = """Sensitiviti sistem dalam mengesan perbezaan gerakan.
- Nilai Rendah: Sangat sensitif (noise boleh dianggap sebagai gerakan).
- Nilai Tinggi: Kurang sensitif (mengabaikan gerakan halus)."""

NOISE_OFFSET_LABEL = """Ofset Hingar"""
NOISE_OFFSET_DESCRIPTION = """Had untuk mengabaikan noise imej.
- Lebih Tinggi: Hasil stacking lebih bersih pada keadaan ekstrem, tetapi kesan gerakan menurun."""

# --- General Alignment Options (Edges, Crop, Saving) ---
KEEP_EDGES_LABEL = "Kekalkan Tepi"
IGNORE_EDGE_LABEL = "Abaikan Tepi"
KEEP_EDGES_DESCRIPTION = """Ciri Kekalkan Tepi membolehkan algoritma menjaga tepi imej
tetap utuh semasa proses penjajaran."""

ENABLE_CROP_LABEL = "Aktifkan\nPemotongan"
DISABLE_CROP_LABEL = "Nyahaktifkan\nPemotongan"
CROP_DESCRIPTION = """Aktifkan Pemotongan untuk membuang
sempadan imej yang tidak terpakai.

Nota: Kadangkala berlaku pepijat pemotongan (sangat jarang).
Seperti imej menjadi sangat kecil, atau kesilapan dalam memotong imej."""

ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "Simpan ke folder"
DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "Jangan simpan\nke folder"
SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER = "Cari.."
DEFAULT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Folder Lalai"
SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Pilih folder"
SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """Menyimpan imej hasil penjajaran ke dalam folder.
Folder lalai ialah folder Dokumen di PC anda."""

ACTIVATE_SAVE_ALIGN_TO_PROCESS = "Simpan untuk\nproses seterusnya"
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = "Jangan simpan\nproses seterusnya"
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """Menyimpan imej untuk proses
denoising ataupun super resolusi."""

# ==============================================================================
# Algorithm General Descriptions (Overview)
# ==============================================================================
# --- Alignment Algorithm Descriptions ---
ALIGNMENT_NAME = "Algoritma Penjajaran"
NONE_ALIGNMENT_DESCRIPTION = "Tiada penjajaran akan diterapkan."
FARNEBACK_DESCRIPTION = """Algoritma ini sesuai untuk penjajaran tahap tinggi yang memerlukan ketepatan dan kejituan hingga ke tahap piksel.
Namun, sangat lemah terhadap perbezaan putaran dan perspektif yang signifikan."""
AKAZE_DESCRIPTION = """Algoritma ini agak teguh terhadap perbezaan besar dalam putaran, perspektif, dan skala.

Agak baik, tetapi tidak sebaik Farneback untuk tahap piksel."""
ORB_DESCRIPTION = """Algoritma yang pantas tetapi kurang tepat untuk perbezaan yang signifikan.

Sesuai untuk imej dengan perbezaan minimum, dan jitu pada imej dengan tekstur rawak."""

LIGHT_GLUE_DESCRIPTION = """Model Rangkaian Saraf (Deep Learning) untuk memadankan ciri-ciri tempatan di seluruh imej.

Light Glue ini lebih mantap berbanding algoritma AKAZE, mampu mengendalikan imej dengan perbezaan perspektif dan keadaan imej yang sukar sekalipun.
Amaran: Proses ini hanya menyokong GPU NVIDIA (CUDA) yang cukup berkuasa, boleh dijalankan pada CPU namun masa prosesnya lebih perlahan."""

# --- Super Resolution Algorithm Descriptions ---
SUPER_RESOLUTION_NAME = "Algoritma Super Resolusi"
NONE_SUPER_RESOLUTION_DESCRIPTION = "Tiada super resolusi akan diterapkan."
INTERPOLATION_DESCRIPTION = """Algoritma ringkas untuk meningkatkan resolusi dengan kaedah interpolasi,
menambah sedikit perincian."""

# --- Denoising Algorithm Descriptions ---
DENOISING_NAME = "Algoritma Pengurangan Hingar"
NONE_DENOISING_DESCRIPTION = "Tiada pengurangan hingar akan diterapkan."
WEIGHTED_AVERAGE_DESCRIPTION = """Hasil daripada penyederhanaan kaedah penindanan keserupaan.
Agak baik dalam menangani pergerakan kecil, tetapi menghasilkan artifak imej pada pergerakan yang lebih besar."""
AVERAGE_DESCRIPTION = """Kaedah penindanan yang sangat pantas dan berkesan untuk objek dan babak statik.
Tidak sesuai untuk babak atau kawasan yang bergerak, tetapi boleh digabungkan dengan penjajaran
Farneback untuk menghilangkan pergerakan objek yang ringan."""
MEDIAN_DESCRIPTION = """Pantas dan berkesan untuk penindanan, agak baik pada objek yang bergerak.
Sangat berkesan dalam menghilangkan pergerakan kecil pada objek, namun artifak muncul pada pergerakan yang lebih besar."""
SIMILARITY_DESCRIPTION = """Algoritma penindanan canggih, sangat kuat dalam menghilangkan pergerakan objek
(sangat sedikit kesan 'ghosting' di kawasan yang bergerak) dan menghasilkan sangat sedikit artifak sehingga 85%.

Diinspirasikan oleh:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""

SIMILARITY_MOTION_V2_DESCRIPTION = """Similarity V2 merupakan hasil pembangunan daripada algoritma Similarity v1 dengan beberapa
peningkatan yang signifikan. Algoritma ini mampu menghasilkan imej yang lebih bersih walaupun input mengandungi hingar yang teruk, berkat keupayaannya
secara bijak membezakan antara hingar, tekstur, dan pergerakan halus. Lebih andal dengan pencahayaan minimum, namun prosesnya berjalan lebih perlahan
berbanding versi v1."""

# ==============================================================================
# Application Settings UI
# ==============================================================================
SETTING_GENERAL_LABEL = "Umum"
SETTING_PERFORMANCE_LABEL = "Prestasi"
PROJECT_MENU_LABEL = "Projek"
PROJECT_SAVE = "Simpan Projek"
PROJECT_SAVE_AS = "Simpan Projek Sebagai..."
PROJECT_OPEN = "Buka Projek..."
PROJECT_RECENT = "Projek Terkini"
PROJECT_ABOUT = "Tentang Pixel Refine"
LANGUAGE_LABEL = "Bahasa"
LANGUAGE_TYPE = "Inggeris", "Indonesia", "Cina Tradisional", "Melayu"
GPU_ACCELERATION_LABEL = "Pecutan GPU"
MULTI_CORE_CPU = "Pecutan Multi-Teras CPU"
SETTINGS_SAVED = "Tetapan berjaya disimpan."

CANT_READ_FILE_SETTINGS = "Amaran: Tidak dapat membaca fail tetapan '{GENERAL_SETTINGS_FILE}'. Menggunakan nilai lalai."
MULTI_CORE_CPU_DESCRIPTION = """Membolehkan pemprosesan selari pada CPU.
- Aktif: Proses lebih cepat, penggunaan RAM bertambah. Matikan jika RAM terhad."""

GPU_ACCELERATION_DESCRIPTION = """Menggunakan kad grafik (GPU) untuk mempercepatkan proses.
- Nota: Setakat ini hanya disokong oleh algoritma Farneback dan LightGlue."""

THUMBNAIL_LABEL = "Imej Kenit (Thumbnail)"
THUMBNAIL_DESCRIPTION = """Memaparkan pratonton imej semasa proses batch (Eksperimen).
- Nota: Boleh menyebabkan lag semasa mendapat batch baru."""

NOISE_MAD_OFFSET_LABEL = "Faktor Hingar MAD"
NOISE_MAD_OFFSET_DESCRIPTION = """Toleransi pengesanan MAD terhadap imej dengan noise tinggi.
- Lebih Tinggi: Lebih toleran noise, risiko bayangan gerakan (ghosting) meningkat."""

MAD_SENSITIVITY_LABEL = "Kepekaan MAD"
MAD_SENSITIVITY_DESCRIPTION = """Sensitiviti MAD terhadap perbezaan imej.
- Lebih Tinggi: Lebih peka pada perbezaan halus, kadar ralat naik jika noise tinggi."""

CONF_SKIP_DFT_LABEL = "Keyakinan Melangkau\nProses DFT"
CONF_SKIP_DFT_DESCRIPTION = """Had melangkau proses DFT jika MBM sudah cukup baik.
- Lebih Tinggi: Lebih banyak proses dilakukan oleh MAD (pengiraan ringan tetapi kasar)."""

WIENER_C_FACTOR_LABEL = "Faktor Wiener C"
WIENER_C_FACTOR_DESCRIPTION = """Sensitiviti penapis Wiener terhadap gerakan.
- Lebih Rendah: Lebih peka gerakan halus, mudah terjejas oleh noise."""

COARSE_MARGIN_LABEL = "Margin Jajar Kasar"
COARSE_MARGIN_DESCRIPTION = """Margin carian penyelarasan pada tahap petak (tile).
- Lebih Tinggi: Stacking lebih tepat, tetapi melambatkan proses dengan ketara."""

# --- Missing UI Keys ---
LBL_BATCH_MODE = "Mode Batch"
LBL_BULK_MODE = "Mode Bulk"
LBL_PARAMETER_ALIGNMENT = "Tetapan Penjajaran Imej"
LBL_ALIGNMENT_PLACEHOLDER = "Tetapan penjajaran imej akan dipaparkan di sini"
LBL_PARAMETER_ALGORITHM = "Tetapan Kaedah Proses"
LBL_ALGORITHM_PLACEHOLDER = "Tetapan terperinci akan dipaparkan selepas anda memilih kaedah proses di atas"
BTN_START = "Mula Proses"
BTN_NEW_BATCH = "Buat Batch Baharu"
BTN_DELETE_BATCH = "Padam Batch"
LBL_ALGORITHM_SETTINGS = "Tetapan Kaedah Penindanan & Penjajaran"
BTN_PROCESS_ALL_BATCH = "Proses Semua Batch"
LBL_FROM_PROJECT = "Dari Projek No:"
LBL_TO_PROJECT = "Ke Projek No:"
MSG_INVALID_RANGE = "Nilai nombor awal projek tidak boleh lebih besar daripada nombor akhir."
BTN_CLOSE = "Tutup"
LBL_STATUS_PROCESSING = "Memproses"
BTN_BACK_TO_GRID = "Kembali ke Grid"
BTN_IMPORT_IMAGES = "Import Imej"
MSG_SUCCESS_SAVE_TO = "Imej berjaya disimpan ke:"
LBL_DRAG_DROP_HERE = "Lepaskan imej di sini untuk menambah"
BTN_YES_DELETE = "Ya, Padam"
BTN_NO_CANCEL = "Tidak, Batalkan"
LBL_SELECTED_BATCHES_TITLE = "Senarai Penuh Batch Terpilih"
LBL_CREATE_NEW_BATCH_TITLE = "Buat Batch Baharu"
LBL_BATCH_NAME = "Nama Batch"
BTN_CREATE = "Buat"
MSG_CONFIRM_DELETE_BATCH_COUNT = "Adakah anda pasti mahu memadam {} batch?"
MSG_NO_BATCHES_AVAILABLE = "Tiada senarai batch yang boleh diproses."
MSG_RENAME_FAILED = "Gagal menukar nama batch. Nama mungkin tidak sah atau telah digunakan."
TIP_CPU_CORES = "Jumlah mesin pemproses (CPU) yang digunakan secara serentak. Pilihan 'Automatik' amat disyorkan."
LBL_SMART_NOISE_ALPHA = "Smart Noise Alpha (AI):"
TIP_SMART_NOISE_ALPHA = "Mengawal toleransi AI terhadap hingar (noise).\nNilai rendah = Lebih peka gerakan (kurangkan ghosting).\nNilai tinggi = Lebih bersih hingar (risiko ghosting)."
LBL_SMART_NOISE_AWARE = "Smart Noise Aware (AI):"
TIP_SMART_NOISE_AWARE = "Aktifkan atau nyahaktifkan sumbangan anggaran hingar kepada model AI."
LBL_NOISE_CONTRIB = "Noise Contribution Strength (%):"
TIP_NOISE_CONTRIB = "Melaraskan kekuatan AI dalam menapis hingar (0% = Dinyahaktifkan, 100% = Pembersihan Penuh)."
LBL_LIGHT_GLUE_TITLE = "Tetapan Kaedah LightGlue"
LBL_SELECT_REFERENCE_IMAGE = "Pilih Imej Rujukan"
LBL_DELETE_IMAGES = "Padam Imej"
MSG_CONFIRM_DELETE_IMAGE = "Adakah anda pasti mahu memadam imej yang dipilih daripada batch ini?"
TIP_RIGHT_CLICK_COPY = "Klik kanan untuk menyalin teks"
MSG_UNSUPPORTED_FORMAT_IGNORED = "Format fail tidak disokong atau tiada pelanjutan yang sah."
MSG_NO_VALID_IMAGES_GROUP = "Tiada imej yang sah untuk diimport."
LBL_LOGGING_LEVEL = "Logging Level:"
BTN_RESET_TO_DEFAULT = "Reset ke Lalai"
BTN_CLEAR_CACHE = "Bersihkan Cache"
LBL_STATUS_READY = "Sedia"
LBL_ITEMS_REMAINING = "proses berbaki"
LBL_SPLASH_LOADING = "M E M U A T K A N . . ."
MSG_EXIFTOOL_NOT_FOUND = "Exiftool tidak ditemui. Sila pastikan ia telah dipasang dan ada dalam PATH sistem anda."
MSG_NO_BATCHES_YET = "Belum ada batch"
MSG_NO_BATCHES_YET_DESC = "Buat batch baharu atau import imej untuk bermula."
MSG_NO_BATCH_SELECTED = "Tiada batch yang dipilih"
LBL_BATCH_IMAGE_COUNT_FORMAT = "Batch {}   -   ({} imej)"
DESC_SUPER_RESOLUTION_CARD = "Tingkatkan perincian dan skala resolusi imej."
DESC_DENOISING_CARD = "Kurangkan hingar imej dan jajarkan lapisan piksel."




# --- New UI & Bulk Core Keys ---
BULK_FROM = "Dari No:"
BULK_TO = "Ke No:"
BULK_MSG_RANGE_ERROR = "Nombor awal mestilah <= nombor akhir."
BULK_ERR_RETRIEVE = "Gagal memuatkan imej projek."
BULK_WARN_UNSUPPORTED = "Format tidak disokong akan diabaikan."
CORE_SELECT_REF_IMAGE = "Set Rujukan"
CORE_DELETE_IMAGES = "Padam Terpilih"
CORE_MSG_CONFIRM_DELETE = "Padam imej terpilih?"
CORE_TOOLTIP_COPY = "Klik kanan untuk salin"

# Tooltip parameter penjajaran
PARAMETER_DIRECT_EDIT_TOOLTIP = "Nilai boleh ditaip terus, kemudian tekan Enter atau alihkan fokus untuk menerapkannya."
AKAZE_THRESHOLD_TOOLTIP = "Kepekaan ciri AKAZE. Nilai lebih rendah mengesan lebih banyak keypoint, sesuai untuk imej gelap atau kurang tekstur, tetapi boleh menambah padanan noise. Nilai lebih tinggi lebih ketat dan pantas."
AKAZE_OCTAVES_TOOLTIP = "Bilangan tahap skala yang dianalisis AKAZE. Lebih banyak octave membantu perubahan saiz besar antara frame, tetapi proses menjadi lebih lambat."
AKAZE_OCTAVE_LAYERS_TOOLTIP = "Sub-tahap dalam setiap octave. Nilai lebih tinggi memperhalus pengesanan skala, tetapi ekstraksi ciri lebih perlahan."
FEATURE_RATIO_THRESHOLD_TOOLTIP = "Ambang Lowe ratio test untuk padanan ciri. Nilai lebih rendah hanya menerima padanan sangat yakin; nilai lebih tinggi menerima lebih banyak padanan tetapi boleh membawa ralat."
FEATURE_MIN_MATCHES_TOOLTIP = "Jumlah padanan sah minimum sebelum gerakan imej dianggarkan. Naikkan untuk penjajaran lebih selamat; turunkan hanya jika imej sangat kurang ciri."
FEATURE_MAX_KEYPOINTS_TOOLTIP = "Jumlah keypoint maksimum untuk anggaran gerakan. Nilai lebih tinggi boleh membantu penjajaran sukar, tetapi menambah masa CPU."
FEATURE_RANSAC_THRESHOLD_TOOLTIP = "Had ralat reprojection untuk RANSAC. Nilai lebih rendah lebih ketat; nilai lebih tinggi lebih toleran terhadap noise/gerakan tetapi boleh menerima padanan salah."
FEATURE_TRANSFORMATION_TOOLTIP = "Model gerakan selepas matching. Homography sesuai untuk perubahan perspektif; affine lebih ringkas dan stabil untuk anjakan kamera kecil."
FEATURE_KEEP_EDGES_TOOLTIP = "Kekalkan piksel tepi selepas warping. Matikan jika mahu membuang kawasan tepi yang kurang pasti."
FEATURE_ENABLE_CROPPING_TOOLTIP = "Potong tepi tidak stabil selepas penjajaran supaya hasil stack menggunakan kawasan imej yang sama-sama sah."
PARAMETER_USE_MULTI_CORE_TOOLTIP = "Gunakan beberapa core CPU jika tersedia. Biasanya lebih pantas, tetapi penggunaan CPU meningkat."
ORB_NFEATURES_TOOLTIP = "Jumlah maksimum ciri ORB yang dikesan. Nilai lebih tinggi memberi lebih banyak calon padanan untuk imej sukar, tetapi proses lebih berat."
ORB_SCALE_FACTOR_TOOLTIP = "Langkah skala antara tahap piramid ORB. Nilai lebih kecil lebih terperinci tetapi lambat; nilai lebih besar lebih cepat tetapi kurang tepat."
ORB_LEVELS_TOOLTIP = "Bilangan tahap piramid ORB. Lebih banyak tahap membantu perubahan skala, tetapi menambah runtime."
FARNEBACK_PYR_SCALE_TOOLTIP = "Skala imej antara tahap piramid. Nilai lebih rendah menggunakan downscale lebih kuat untuk gerakan besar; 0.5 lazim digunakan."
FARNEBACK_LEVELS_TOOLTIP = "Bilangan tahap piramid untuk optical flow. Lebih banyak tahap membantu gerakan besar, tetapi menggunakan lebih banyak memori dan masa."
FARNEBACK_WINSIZE_TOOLTIP = "Saiz tetingkap piksel untuk anggaran gerakan. Tetingkap besar lebih licin dan tahan noise; tetingkap kecil mengekalkan detail tempatan."
FARNEBACK_ITERATIONS_TOOLTIP = "Bilangan refinement pada setiap tahap piramid. Lebih banyak lelaran boleh meningkatkan ketepatan flow tetapi melambatkan proses."
FARNEBACK_POLY_N_TOOLTIP = "Saiz kawasan untuk pengembangan polinomial. 5 lebih tajam; 7 lebih licin dan lebih tahan noise."
FARNEBACK_POLY_SIGMA_TOOLTIP = "Perataan Gaussian untuk pengembangan polinomial. Nilai lebih tinggi mengurangkan noise tetapi boleh melembutkan gerakan kecil."
FARNEBACK_FLAGS_TOOLTIP = "Flag pilihan Farneback. 0 ialah standard; 256 menggunakan Gaussian window untuk flow lebih licin dalam sesetengah kes."
OPTICAL_FLOW_TILE_COLS_TOOLTIP = "Bilangan tile mendatar untuk pemprosesan flow per blok. Lebih banyak tile mengurangkan memori per blok tetapi menambah overhead cantuman."
OPTICAL_FLOW_TILE_ROWS_TOOLTIP = "Bilangan tile menegak untuk pemprosesan flow per blok. Lebih banyak tile mengurangkan memori per blok tetapi menambah overhead cantuman."
OPTICAL_FLOW_TILE_OVERLAP_TOOLTIP = "Nisbah overlap antara tile. Overlap lebih besar mengurangkan seam antara tile, tetapi menambah pengiraan berulang."
LIGHT_GLUE_MATCH_CONFIDENCE_TOOLTIP = "Ambang keyakinan padanan Light Glue. Nilai lebih tinggi hanya menerima pasangan ciri yang lebih yakin; nilai lebih rendah memberi lebih banyak padanan tetapi boleh membawa noise."
LIGHT_GLUE_USE_GPU_TOOLTIP = "Jalankan inferens Light Glue pada GPU jika backend tersedia. Sesuai untuk model neural, tetapi boleh menggunakan VRAM tambahan."
LUCAS_KANADE_GRID_STEP_TOOLTIP = "Jarak antara titik grid yang dijejaki Lucas-Kanade. Nilai lebih kecil memberi flow lebih padat tetapi lebih perlahan; nilai lebih besar lebih pantas."
LUCAS_KANADE_BORDER_MARGIN_TOOLTIP = "Jarak selamat dari tepi tile sebelum titik grid dibuat. Margin membantu mengurangkan tracking pada kawasan tepi yang kurang stabil."
LUCAS_KANADE_POINT_WORKERS_TOOLTIP = "Bilangan worker untuk membahagi tracking titik grid di dalam setiap tile. Naikkan untuk CPU banyak core; turunkan jika CPU terlalu penuh atau berlaku spike."
LUCAS_KANADE_WIN_SIZE_TOOLTIP = "Saiz tetingkap carian Lucas-Kanade. Tetingkap besar membantu gerakan lebih jauh; tetingkap kecil mengekalkan detail tempatan."
LUCAS_KANADE_MAX_LEVEL_TOOLTIP = "Bilangan level piramid optical flow. Lebih banyak level membantu gerakan besar, tetapi menambah masa proses."
LUCAS_KANADE_ITERATIONS_TOOLTIP = "Bilangan iterasi carian bagi setiap titik. Lebih banyak iterasi boleh meningkatkan ketepatan, tetapi proses lebih perlahan."
LUCAS_KANADE_EPSILON_TOOLTIP = "Ambang konvergensi Lucas-Kanade. Nilai lebih kecil lebih tepat, tetapi boleh memerlukan lebih banyak iterasi."
UI_STATUS_READY = "Sedia"
UI_ITEMS_REMAINING = "berbaki"
UI_SPLASH_LOADING = "Memuatkan..."

PROGRESS_ALIGN = "Penyelarasan: {}/{}"
PROGRESS_MERGING = "Penggabungan: {}/{}"

# Missing Keys
MSG_DATABASE_ERROR = "Ralat Pangkalan Data"
MSG_DB_RETRIEVE_FAILED = "Gagal mengambil data dari pangkalan data."
MSG_FOLDER_ERROR = "Ralat Folder"
MSG_CREATE_FOLDER_TIFF_FAILED = "Gagal mencipta folder untuk menyimpan fail TIFF."
MSG_TIFF_PROCESSING_ISSUES = "Isu Pemprosesan TIFF"
MSG_TIFF_PROCESS_FAILED_SOME = "Beberapa fail TIFF gagal diproses."
MSG_IMPORT_FAILED = "Import Gagal"
MSG_NO_VALID_FILES_IMPORT = "Tiada fail sah ditemui untuk diimport."
MSG_ERROR_TITLE = "Ralat"
MSG_IMPORT_ERROR_OCCURRED = "Ralat berlaku semasa import."
MSG_CAUTION_TITLE = "Amaran"
MSG_CONFIRM_TITLE = "Sahkan"
MSG_WARNING_TITLE = "Amaran"
MSG_ALIGN_ALGO_NOT_RECOGNIZED = "Algoritma penyelarasan tidak dikenali."
MSG_NO_PROCESSED_IMAGES_SAVE = "Tiada imej diproses untuk disimpan."
MSG_INVALID_FORMAT = "Format Tidak Sah"
MSG_UNSUPPORTED_FORMAT_EXTENSION = "Format fail atau sambungan tidak disokong."
MSG_COULD_NOT_READ_SOURCE = "Tidak dapat membaca fail sumber."
MSG_CLEANUP_ERROR = "Ralat Pembersihan"
MSG_REMOVE_TEMP_FAILED = "Gagal memadam fail sementara."
MSG_SUCCESS_TITLE = "Berjaya"
MSG_SUCCESS_SAVE = "Imej berjaya disimpan."
MSG_FAILED_SAVE_IMAGE = "Gagal menyimpan imej."
BTN_CANCEL = "Batal"
SIMILARITY_V2_GROUP_TITLE = "Parameter Similarity V2"
RESET_TO_DEFAULTS_BUTTON_TEXT = "Reset ke Default"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TITLE = "Tiada Imej Sah"
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED_TEXT = "Tiada imej sah dipilih untuk import."
DEVICE_ACCELERATION_LABEL = "Pecutan GPU"
BTN_TEST_BACKEND_HARDWARE = "Uji Pecutan Perkakasan"
MSG_IMPORT_ERROR = "Ralat Import"
LBL_ANALYSIS_MODE = "Mod Analisis"
LBL_FAST = "Pantas"
LBL_DEEP = "Mendalam"
MSG_HARDWARE_TEST_DEPTH = "Pilih kedalaman ujian pecutan perkakasan:"
MSG_HARDWARE_TEST_FAST = "Pemeriksaan keserasian backend secara pantas."
MSG_HARDWARE_TEST_DEEP = "Validasi menyeluruh setiap backend."
MSG_BACKEND_RESTART_REQUIRED = "Mula semula diperlukan untuk menggunakan pemilihan backend baharu."
BTN_YES = "Ya"
BTN_NO = "Tidak"
BTN_OK = "OK"
LBL_ETA = "Anggaran {0}"
LBL_TESTING = "Menguji"
LBL_HARDWARE_PREPARING = "Menyediakan backend perkakasan..."
LBL_HARDWARE_BACKEND_ANALYSIS = "Analisis Backend Perkakasan"
MSG_BACKEND_TEST_CANCELLED = "Ujian backend dibatalkan."
LBL_INITIALIZATION_FAILED = "pemulaan gagal"
LBL_RENDERER_UNAVAILABLE = "renderer tidak tersedia"
LBL_UNKNOWN = "Tidak Diketahui"
LBL_NO_BACKEND_RESULTS = "Tiada hasil backend tersedia."
LBL_BACKEND_COMPATIBILITY_RESULTS = "Keputusan Keserasian Backend"
LBL_DIAGNOSTIC_LOGS = "Log diagnostik"
MSG_BACKEND_TEST_FINISHED = "Ujian backend selesai."
LBL_AUTO_FALLBACK = "Fallback Automatik"
LBL_AUTO_FALLBACK_TIP = "Jika diaktifkan, automatik beralih melalui CUDA, Vulkan, OpenGL, kemudian CPU jika backend yang dipilih tidak tersedia."
AUTO_SHUTDOWN_LABEL = "Aktifkan Shutdown Automatik"
AUTO_SHUTDOWN_DESCRIPTION = "Tutup aplikasi selepas tiada aktiviti pengguna selama tempoh yang ditetapkan."
AUTO_SHUTDOWN_TIMEOUT_LABEL = "Had idle (minit)"

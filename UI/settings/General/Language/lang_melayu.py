# -*- coding: utf-8 -*-

# ==============================================================================
# General UI Elements & Messages
# ==============================================================================
# Placeholder/General Info
UNDER_DEVELOPMENT = "Menu {page_name} sedang dibangunkan"
LOADING_THUMBNAIL = "Memuatkan...."
NOT_IMAGE_PREVIEW = "Tiada imej tersedia"
MODULE_NOT_IMPLEMENT = "Modul belum dilaksanakan."

# Buttons
ADD_IMAGE_BUTTON = "Tambah"
PREVIEW_IMAGE_BUTTON = "Pratonton"
DELETE_IMAGE_BUTTON = "Padam"
APPLY_PARAMETER_BUTTON_TEXT = "Guna Tetapan"

# Labels
PREVIEW_PANEL_LABEL = "Panel Pratonton"

# Window Messages
WINDOW_START_PROCESSING = "Memulakan proses..."
WINDOW_PROCESSING_COMPLETE = "Selesai!"

# Application Control
RESTART_APPLICATION_REQUIRED = "Mula Semula Diperlukan"
RESTART_APPLICATION_DESCRIPTION = "Mula semula untuk melihat perubahan"
ACCEPT_RESTART_APPLICATION = "Mula Semula Sekarang"
REJECT_APPLICATION_DESCRIPTION = "Nanti"
COMMAND_APPLICATION_DESCRIPTION = "Memuat Semula Aplikasi..."
TRY_RESTART_APPLICATION = "Mencuba memuat semula aplikasi"
COMMAND_FAILED_IN_RESTART_APPLICATION = "Sistem gagal dimulakan semula."
RESTART_FAILED = "Mula Semula Gagal"
COMMAND_TO_RESTART_MANUALLY = "Tidak dapat memulakan semula aplikasi secara automatik. Sila mulakan semula secara manual."


# ==============================================================================
# Sidebar UI
# ==============================================================================
SETTINGS_SIDEBAR_LABEL= "Tetapan"
HDR_SIDEBAR_LABEL= "Recontruction HDR"


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
UI_LABEL_BATCH_NO_PROCESS = "Tiada batch yang diproses!"
UI_LABEL_BATCH_SUCCES = "Semua batch telah diproses!"
UI_LABEL_BATCH_PROCESS = "Memproses {} batch..."
UI_LABEL_MOVING_FILES = "Memindahkan {} fail ke folder '{}'. Sila tunggu..."
UI_LABEL_BATCH_PROGRESS = "{}/{} batch telah diproses..."
PROCESSING_BATCH = "--- Memproses batch {}/{} (Telah diproses: {}) ---"
NUMBER_OF_BATCHES_TO_BE_PROCESSED = "Jumlah batch yang akan diproses: {}"
BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS = "batch_id mesti ada untuk proses batch"
SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED = "Melangkau batch {} kerana tiada imej dimuatkan."
BATCH_LABEL_FORMAT = "Batch {}   -   ({} imej)"



SELECT_OUTPUT_FOLDER_TITLE = "Pilih Folder Output untuk Simpan Batch"
OUTPUT_FOLDER_SELECTION_CANCELLED = "Pemilihan folder dibatalkan. Proses dihentikan."

BATCH_PROCESSING_ERROR_TITLE = "Ralat Proses Batch"
BATCH_PROCESSING_ERROR_MESSAGE = "Gagal memproses Batch {} (ID: {}):\n{}"
BATCH_SAVE_ERROR_TITLE = "Gagal Menyimpan"
TARGET_FOLDER_NOT_ACCESSIBLE = "Folder sasaran tidak dapat diakses:\n{}"
MOVE_FILE_ERROR_TITLE = "Gagal Alih Fail"
COULD_NOT_SAVE_FILE_FOR_BATCH = "Gagal menyimpan fail '{}' untuk batch:\n{}"
SOURCE_FILE_DOES_NOT_EXIST = "Gagal alih: Fail sumber '{}' tidak dijumpai."
TARGET_FOLDER_INVALID = "Gagal alih: Folder sasaran '{}' tidak sah."

LOG_BATCH_PROCESSING_START = "Memulakan pemprosesan untuk {} batch..."
LOG_PROCESSING_BATCH_DETAIL = "Memproses Batch ke-{} (ID: {}), urutan ({}/{})..."
LOG_WARN_MULTIPLE_NEW_FILES = "Amaran: >1 fail baharu untuk Batch {}. Yang pertama dialihkan: {}"
LOG_BATCH_PROCESSED_NEW_OUTPUT = "Batch {} selesai, output baharu: {}"
LOG_BATCH_PROCESSED_NO_OUTPUT = "Batch {} selesai, tetapi tiada fail output baharu dalam folder '{}'."
LOG_ERROR_PROCESSING_BATCH = "Ralat semasa memproses Batch {}: {}"
LOG_ALL_BATCH_ATTEMPTS_FINISHED = "Semua percubaan pemprosesan batch telah selesai."

LOG_MOVE_SUCCESS = "Berjaya mengalihkan '{}' ke '{}'."
LOG_MOVE_FAILED = "Gagal mengalihkan '{}' ke '{}': {}"
LOG_SOURCE_FILE_NOT_FOUND = "Fail sumber tidak dijumpai: {}"
LOG_TARGET_FOLDER_NOT_FOUND = "Folder sasaran tidak sah: {}"

UI_LABEL_BATCH_NO_PROCESS = "Tiada batch dipilih untuk diproses."
UI_LABEL_BATCH_PROCESS_START = "Memulakan proses untuk {} batch..."
UI_LABEL_BATCH_PROGRESS_DONE_SAVED = "Batch {} selesai & disimpan ({}/{})."
UI_LABEL_BATCH_PROGRESS_SAVE_FAILED = "Batch {} selesai, gagal simpan ({}/{})."
UI_LABEL_BATCH_PROGRESS_NO_OUTPUT = "Batch {} selesai, tiada output ({}/{})."
UI_LABEL_BATCH_PROGRESS_ERROR = "Ralat Batch {} ({}/{})."

UI_LABEL_BATCH_ALL_SUCCESS_SPECIFIC = "Semua {} batch berjaya diproses & disimpan ke {}."
UI_LABEL_BATCH_PARTIAL_SUCCESS_SPECIFIC = "{} dari {} batch disimpan ke {}. Beberapa bermasalah."
UI_LABEL_BATCH_NO_SUCCESS_SPECIFIC = "Proses selesai. Tiada hasil batch disimpan ke {}."
UI_LABEL_BATCH_NONE_PROCESSED = "Tiada batch yang diproses."


# Batch Deletion
BATCH_DELETE_LABEL = "Sahkan Pemadaman Batch", "Adakah anda pasti mahu memadam batch {}?" # Tuple for Title, Message
TITLE_BATCH_ALL_DELETE_BUTTON = "Padam Semua Batch"
CONFIRM_BATCH_ALL_DELETE_BUTTON = "Adakah anda pasti mahu memadam {} batch?"
NO_DATA_BATCH_ALL_DELETE_BUTTON = "Tiada data batch yang disimpan."

# Batch Parameters UI Labels
PARAMETER_BATCH_CROP_EDGE = "Potong Tepi"
PARAMETER_BATCH_KEEP_EDGE = "Kekalkan Tepi"
PARAMETER_BATCH_DENOISING = "Denoising"
PARAMETER_BATCH_SUPER_RESOLUTION = "Super Resolution"
PARAMETER_BATCH_ALIGNMENT = "Jajarkan Imej"
PARAMETER_BATCH_ALIGNMENT_TO_FOLDER = "Simpan Hasil Penjajaran ke Folder"
PARAMETER_BATCH_ALIGNMENT_TO_PROCESS = "Simpan Hasil Penjajaran untuk Proses Seterusnya"

# Batch Saving Feedback
UI_FAILED_TO_SAVE_IMAGE_BATCH = "Gagal menyimpan imej: {}"
UI_SUCCES_TO_SAVE_IMAGE_BATCH = "Imej berjaya disimpan: {}"
UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH = "Tiada imej"
UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH = "Folder sistem (database/stack) tidak wujud"
UI_NO_BATCH_PROCESS = "Tiada proses batch tersedia"

# Batch Specific Errors/Warnings
ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F = "Ralat mengambil kunci {} daripada HDF5: {}"


# ==============================================================================
# Image Handling (Import/Delete) UI & Messages
# ==============================================================================
# Import
HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "Fail Imej (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES = """Seret & lepas imej di sini<br>
atau<br>
Gunakan butang 'Import Imej'"""
SUPPORTED_IMAGE_EXTENSION = "Format imej yang disokong"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Pilih Imej"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Imej Pendua"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} imej sudah ada dalam pangkalan data, akan dilangkau."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Format Terpilih"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} imej dengan format '{format}' akan diimport."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Gagal", "Tiada imej sah untuk diimport." # Tuple for Title, Message
ON_IMPORT_COMPLETE_STATUS = "Import selesai"
ON_IMPORT_COMPLETE_MESSAGES = "{} imej telah berjaya diimport."

# Delete
HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Gagal", "Tiada imej dipilih." # Tuple for Title, Message
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Adakah anda pasti mahu memadam {} imej yang dipilih?"


# ==============================================================================
# Preview Panel UI & Messages
# ==============================================================================
UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Memproses imej, sila tunggu..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "Tiada imej dipilih."


# ==============================================================================
# Progress & Status Messages (General)
# ==============================================================================
# Progress Bar
UPDATE_PROGRESS_BAR_STATUS = "{}% ({} proses berbaki)"

# Buttons in Progress Sections (if generic)
PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Mula Proses"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Simpan Sebagai"

# General Process Status/Feedback
PROCESS_ALGORITHM_PROCESS_SKIPPED = "Tiada algoritma dipilih untuk pemprosesan"
PROCESS_TERMINATED_BY_USER = "Proses Ditamatkan Oleh Pengguna"
LOADING_IMAGE_PATH = "Memuatkan {num_in_this_batch} laluan imej..."
LOAD_IMAGE_FROM_HDF5 = "Memuatkan {} imej daripada HDF5..."
NO_IMAGE_PATH_PROCESSED_IMAGE = "Tiada laluan imej untuk diproses."
PROCESSING_IMAGE_FROM_HDF5 = "Memproses imej daripada HDF5: {}"
OUTPUT_SAVE_WEIGHT_MAP = "Peta pemberat (Weight Map) akan disimpan ke: {}"
OUTPUT_IMAGE_TO_BE_SAVED = "Imej output akan disimpan ke: {}"
NO_IMAGES_PROCESSED = "Tiada imej dapat diproses"
NUMBER_OF_IMAGES_TO_BE_PROCESSED = "Jumlah imej yang akan diproses: {}"
RETURNING_IMAGE_RESULTS = "Mengembalikan hasil ({}/{} imej)."
FINISHING_ANALYSIS = "Menyelesaikan Analisis"
IMAGE_PROCESS_FINISHED = "Penindanan selesai."
IMAGE_PROCESS_IN_PROGRESS = "Memproses imej {} daripada {}"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Menindan batch ke-{current} daripada {total}"


# ==============================================================================
# Core Processing Messages (Status & Logs)
# ==============================================================================
# General Logging
CONSOL_LOG_RUNNING_ALGORITHM = "Proses {} dipilih, algoritma: {}"

# HDF5 Saving/Loading
SAVE_TO_HDF5_ALIGNED_SAVING = "Menyimpan imej yang telah dijajarkan"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Imej ke-{index} telah disimpan."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "Semua imej berjaya disimpan."
NO_HDF5_FILE_PROCESSING_FROM_PATH = "Fail HDF5 tidak ditemui. Memproses daripada laluan imej..."

# Image Processing Steps
RUN_SAVING_REFERENCE_IMAGE = "Menyimpan imej rujukan."
RUN_IMAGE_PROCESSING = "Memproses imej {i} daripada {total_images}..."
RUN_IMAGE_PROCESSING_SAVING = "Imej ke-{i} telah disimpan."
RUN_IMAGE_PROCESSING_FINISHED = "Proses selesai."
RUN_IMAGE_PROCESS_STARTED = "Memulakan proses..."
RUN_PROCESS_TRANSFORMATION = "[1/2] Kira transformasi {}/{}"
RUN_SAVING_TRANSFORMATION = "[2/2] Simpan hasil {}/{}"


# Motion Compensation / Alignment Steps
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS ="Menjajarkan dan memotong imej {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION ="Menyimpan imej {}/{}"
COMPENSATE_MOTION_STATUS = "Melakukan pampasan gerakan pada imej {image_id}..."
COMPENSATE_MOTION_FINISHED = "Pampasan gerakan selesai untuk imej {image_id}."

# Stacking / Denoising Steps
STACK_IMAGES_PROCESS = "Memproses imej {current}/{total}..."
ENHANCEMENT = "Mempertingkat: {}"
STARTING_ENHANCEMENT = "Memulakan Peningkatan"
START_IMAGE_ENHANCEMENT = "--- Memulakan Peningkatan untuk {} imej ---"
ANALYZING_IMAGE = "Menganalisis imej {}/{}..."
SAVING_WEIGHT_MAP = "Peta pemberat (Weight Map) disimpan"

# Analysis Steps (e.g., Similarity)
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
IMAGE_LOAD_FAILED = "Tiada imej dimuatkan."
FIRST_IMAGE_CANNOT_BE_OBTAINED = "Tidak dapat memperoleh imej pertama: {}"
RUN_IMAGE_PROCESS_LOAD_FAILED = "Tidak ditemui imej dalam pangkalan data."

# File / System Errors
ERROR_IN_READING_FILE_HDF5 = "Ralat membaca HDF5: {}"
FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "Fail transformation matrix tidak ditemui untuk imej {}"
LIBRARY_FILE_NOT_FOUND = "Fail library tidak ditemui: {}"

# Processing / Algorithm Errors
ERROR_ACCUMULATE_IMAGE = "Imej terkumpul (Accumulated image) adalah None atau jumlah pemberat (total weights) tidak sah."
RUN_STACK_PROCESSING_FAILED = "Gagal melakukan penindanan imej"
FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "Pengiraan gerakan tidak dapat dikira untuk imej ke-{}"
FAIL_COMPENSATE_MOTION_PROCESS = "Anggaran gagal pada imej ke-{}"
UNRECOGNIZED_TRANSFORMATION = "Jenis transformasi tidak dikenali."
FAILED_TO_COMPUTE_TRANSFORMATION ="Transformasi tidak dapat dikira."
FAILED_TO_COMPUTE_CROP = "Gagal mengira potongan (crop) yang sah. Proses dibatalkan."
FAIL_CROPPING_PROCESS = "Potongan (Crop) tidak sah. Pertindihan tidak mencukupi."
ERROR_IN_FLOW_FIELD = "Ralat pada imej {}: Input Field flow adalah none. Tidak dapat memampas gerakan."
ERROR_IN_BASE_IMAGE = "Ralat pada imej {}: Input base_image adalah none. Tidak dapat memampas gerakan."
STACK_IMAGES_FAILED = "Tiada imej untuk diproses."
DATA_FAILED_COMPLETION_CREATED = "Data penyempurnaan gagal dijana. Tidak dapat melakukan penyempurnaan."
FAILED_IMAGE_ENHANCEMENT = "Proses penyempurnaan gagal."
ANALYSIS_FAILURE = "Analisis gagal: Tiada imej diproses"
ERROR_AT_END_OF_CONVERSION = "Ralat pada akhir penukaran: {}"
UNEXPECTED_NUMBER_OF_BUFFER_CHANNELS = "Ralat Dalaman: Jumlah saluran penimbal (buffer channels) tidak dijangka."
UNABLE_TO_SAVE_WEIGHT_MAP = "Tidak dapat menyimpan Peta Pemberat (Weight Map): {}"
FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH = "Gagal menyimpan peta pemberat (weight map) ke {}"
NORMALIZATION_FAILED = "Normalisasi Gagal: {}"
FATAL_ERROR_DURING_NORMALIZATION = "RALAT KRITIKAL Semasa normalisasi: {}"
FAILED_TO_ACCUMULATE_IMAGE= "Pada imej {}, gagal mengakumulasi"
COLOR_CHANNEL_DOES_NOT_MATCH = "Saluran warna tidak sepadan."
IMAGE_CHANNEL_DOES_NOT_SUPPORT = "Saluran imej tidak disokong: {}."
DATA_TYPE_NOT_SUPPORTED = "Jenis data tidak disokong: {}."
IMAGE_BIT_REQUIRED = "Imej mestilah 8 Bit atau 16 Bit."

# Library / Dependency Errors
FAILED_TO_CONFIGURE_LIBRARY = "Gagal memuat/mengkonfigurasi pustaka {}: {}"
LIBRARY_FAILED_TO_LOAD_NORMALIZATION_FAILED = "Library C++ tidak dimuatkan. Normalisasi dilangkau."
LIBRARY_FAILED_TO_LOAD_ACCUMULATED_SKIPED = "Library C++ tidak dimuatkan. Akumulasi dilangkau."

# GPU Errors
GPU_ERROR_AND_FALLBACK_TO_CPU = "Ralat GPU tidak dijangka: {}. Proses menggunakan CPU."

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
WINDOW_TITLE_FARNEBACK = "Penjajaran Farneback Optical Flow"
WINDOW_TITLE_AKAZE = "Penjajaran AKAZE"
WINDOW_TITLE_ORB = "Penjajaran ORB"

# Denoising / Stacking
WINDOW_TITLE_AVERAGE = "Penindanan Average"
WINDOW_TITLE_MEDIAN = "Penindanan Median"
WINDOW_TITLE_SIMILARITY = "Penindanan Similarity"
WINDOW_TITLE_SIMILARITY_V2 = "Penindanan Similarity V2"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Super Resolusi Interpolasi"


# ==============================================================================
# Algorithm Parameter Settings UI (Labels & Descriptions)
# ==============================================================================
DEFAULT_PARAMETER_SETTING_LABEL = """Pilih algoritma untuk melihat parameternya."""

# --- ORB Parameters ---
ORB_PARAMETER_SETTING_LABEL = "Parameter ORB"
ORB_NFEATURES_LABEL = "Jumlah Ciri"
ORB_NFEATURES_DESCRIPTION = """Jumlah ciri mencari seberapa banyak butiran halus yang dapat dikenali dalam sesebuah imej.

- Jumlah ciri yang lebih tinggi membolehkan algoritma mencari lebih banyak butiran,
  menghasilkan penjajaran imej yang lebih jitu. Namun, meningkatkan masa pengiraan.

- Biasanya, nilai antara 500 hingga 1500 sudah cukup untuk kebanyakan babak imej.
  Untuk keperluan ketepatan yang sangat tinggi, memilih nilai antara 2500 hingga 5000 boleh meningkatkan ketepatan."""
ORB_SCALEFACTOR_LABEL = "Scale Factor"
ORB_SCALEFACTOR_DESCRIPTION = """Scale Factor menentukan kadar penurunan skala imej secara beransur-ansur semasa pemprosesan.

- Jika nilainya menghampiri 1.0, imej dikecilkan secara perlahan dengan lebih banyak langkah.
  Ini membolehkan pengesanan butiran yang lebih halus, tetapi mengambil masa lebih lama.

- Jika nilainya lebih besar, imej dikecilkan lebih cepat, menjadikan pemprosesan lebih singkat,
  tetapi mungkin ada beberapa butiran kecil yang terlepas.

Biasanya, nilai Scale Factor berkisar antara 1.2 hingga 1.5."""
ORB_NLEVELS_LABEL = "Jumlah Level"
ORB_NLEVELS_DESCRIPTION = """Jumlah level menunjukkan jumlah lapisan dalam piramid imej yang digunakan untuk mengesan ciri.

- Semakin banyak level, semakin banyak butiran yang dapat ditangkap oleh algoritma pada pelbagai skala,
  ini berguna jika saiz imej berbeza-beza.

- Namun, semakin tinggi jumlah level, semakin lama masa pemprosesannya.

Untuk kebanyakan babak, nilai antara 2 hingga 4 sudah cukup ideal."""
ORB_TRANSFORMATION_LABEL = "Jenis Transformasi"
ORB_TRANSFORMATION_DESCRIPTION = """Pilih kaedah untuk menjajarkan imej mengikut keperluan anda:

Opsi yang tersedia termasuk:
- HOMOGRAPHY: Sesuai untuk foto dengan perbezaan sudut yang agak ekstrem (misalnya: gambar meja dari atas vs. sisi).
  Boleh melaraskan kesan "perspektif".

- AFFINE: Boleh diputar, mengubah saiz (boleh tidak seragam), dan mengalih imej.
  Contoh: membetulkan foto yang senget dan perlu dibesarkan sebahagian.

- SIMILARITY: Hanya benarkan putaran, pembesaran/pengecilan yang seragam, dan peralihan.
  Nisbah aspek dikekalkan.

- EUCLIDEAN: Paling ringkas: hanya putar dan alih imej tanpa mengubah saiz.
  Sesuai untuk membetulkan foto yang sedikit senget.

Saranan Pemilihan:
- Untuk kebanyakan kes (terutamanya foto dari sudut yang agak ekstrem), pilih Homography.
- Jika imej hanya perlu dilaraskan kedudukan/putaran ringkas, Euclidean atau Similarity lebih sesuai.
- Gunakan Affine hanya jika perlu penyesuaian bentuk fleksibel tanpa kesan perspektif."""
ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """RANSAC Threshold menentukan sejauh mana ketatnya algoritma menapis nilai terpencil (outlier)
(data yang menyimpang jauh) semasa menjajarkan imej.

- Nilai lebih rendah (misalnya, 1-2) bermakna penapisan lebih ketat, sehingga beberapa ciri penting mungkin terabai.

- Nilai lebih tinggi (misalnya, 4-5) lebih bertoleransi terhadap outlier, membenarkan lebih banyak ciri digunakan,
  tetapi boleh mengurangkan ketepatan penjajaran.

Biasanya, nilai antara 1 hingga 3 sudah cukup, bergantung pada tahap hingar (noise) dalam data."""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Parameter Farneback"
FARNEBACK_PYRAMID_SCALE_LABEL = "Skala Piramid"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Skala Piramid adalah faktor yang menentukan sejauh mana imej
diperkecil pada setiap level piramid.

- Nilai ini menentukan sejauh mana mengurangkan saiz imej (downscale) dari satu level ke level berikutnya.
  Misalnya, jika nilainya 0.5, maka setiap level akan mempunyai saiz separuh daripada level sebelumnya.

- Nilai yang lebih kecil (sekitar 0.10 hingga 0.5) menyebabkan perbezaan saiz antara level lebih besar.
  Ini boleh mempercepatkan pengiraan, tetapi mungkin mengurangkan ketepatan dalam menangkap gerakan halus.

- Nilai yang menghampiri 1.00 menghasilkan perubahan saiz yang lebih kecil antara level,
  membolehkan pengesanan gerakan yang lebih tepat, dengan masa pengiraan yang lebih lama.

Laraskan nilai ini mengikut keperluan anda untuk mencari keseimbangan antara kelajuan pemprosesan dan
ketepatan pengesanan gerak.
Nilai yang disyorkan: 0.5
"""
FARNEBACK_LEVELS_LABEL = "Level"
FARNEBACK_LEVELS_DESCRIPTION = """Parameter Level dalam algoritma Farneback merujuk kepada jumlah lapisan
  (layers) dalam piramid imej yang digunakan untuk mengira optical flow.

- Lebih banyak level: Algoritma dapat mengesan gerakan objek pada pelbagai saiz dan kelajuan,
  termasuk gerakan yang kompleks atau meliputi kawasan yang luas. Namun, ini memerlukan
  masa pengiraan yang lebih lama.

- Namun, semakin banyak level yang digunakan, semakin lama masa pengiraan yang diperlukan.

Anda boleh melaraskannya antara 1 hingga 10 mengikut keperluan aplikasi anda.
Secara umum, nilai 3 dianggap sebagai standard.
"""
FARNEBACK_WIN_SIZE_LABEL = "Saiz Tetingkap"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Saiz Tetingkap menentukan sejauh mana kawasan piksel (tetingkap)
yang digunakan dalam pengiraan optical flow.

- Saiz tetingkap yang lebih besar: Menghasilkan anggaran pergerakan yang lebih stabil dan licin kerana
  maklumat dikira dari kawasan yang lebih luas. Namun, butiran pergerakan kecil mungkin terlepas.

- Saiz tetingkap yang lebih kecil: Lebih sensitif terhadap pergerakan kecil,
  namun hingar (noise) boleh dianggap sebagai gerakan dan kurang stabil.

Anda boleh memilih nilai antara sensitif terhadap butiran gerakan kecil
dan hasil yang stabil.
Nilai yang disyorkan: 15.
"""
FARNEBACK_ITERATIONS_LABEL = "Iterasi"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterasi menentukan berapa kali pengiraan optical flow diperbaiki pada setiap level piramid.

- Semakin banyak iterasi, semakin tepat hasil optical flow yang diperoleh.
- Namun, peningkatan jumlah iterasi juga boleh melambatkan masa pengiraan.

Pilih nilai yang dapat meningkatkan ketepatan tanpa terlalu melambatkan proses.
Nilai yang disyorkan: 3.
"""
FARNEBACK_POLY_N_LABEL = "Ekspansi Polinomial"
FARNEBACK_POLY_N_DESCRIPTION = """Ekspansi Polinomial (poly_n) menentukan saiz kawasan piksel yang digunakan,
untuk menganggar gerakan dengan kaedah ekspansi polinomial.

- Nilai ini menentukan sejauh mana data piksel di sekitar yang digunakan dalam pengiraan.

- Nilai yang lebih besar akan menghasilkan anggaran gerakan yang lebih licin,
  tetapi dapat mengurangkan kepekaan terhadap gerakan kecil.

Biasanya, nilai yang digunakan adalah 5 atau 7, bergantung pada tahap butiran dan kestabilan yang diinginkan.
"""
FARNEBACK_POLY_SIGMA_LABEL = "Sigma Polinomial"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Sigma Polinomial mengawal sejauh mana pelicinan (smoothing)
yang diterapkan sebelum ekspansi polinomial dilakukan.

- Nilai ini merupakan sisihan piawai (standard deviation) penapis Gaussian yang digunakan untuk mengurangkan hingar (noise) pada data piksel.
- Sigma yang lebih tinggi dapat membantu meredam hingar,

  tetapi jika terlalu tinggi boleh menghilangkan butiran gerakan yang penting.

Atur dengan teliti untuk mengurangkan hingar tanpa kehilangan butiran gerakan yang signifikan.
Nilai yang disyorkan: 1.2.
"""
FARNEBACK_FLAGS_LABEL = "Flag"
FARNEBACK_FLAGS_DESCRIPTION = """Flag adalah parameter pilihan yang membolehkan
mengaktifkan opsi tertentu dalam algoritma Farneback.

- Flag sering digunakan dalam penerapan penapis Gaussian untuk pelicinan,
  ini digunakan untuk mendapatkan hasil optical flow yang lebih licin.

- Jika anda ragu, biarkan parameter ini pada nilai lalai (0).

Pilih flag yang sesuai jika anda ingin menyeimbangkan antara kelajuan proses dan kualiti hasil.
Nilai yang disyorkan: 0.
"""

# --- AKAZE Parameters ---
AKAZE_PARAMETER_SETTING_LABEL = "Parameter AKAZE"
AKAZE_THRESHOLD_LABEL = "Threshold"
AKAZE_THRESHOLD_DESCRIPTION = """Parameter Threshold menentukan sejauh mana sensitifnya pengesan
untuk mencari sebuah titik kunci (keypoint).

- Nilai yang lebih rendah meningkatkan pengesanan titik kunci yang lebih banyak,
  termasuk imej yang mempunyai ciri yang sedikit dan banyak hingar (noise).

- Nilai yang lebih tinggi hanya mengehadkan pengesanan hanya pada ciri yang paling kuat.

Nilai yang disyorkan: 0.0010.
"""
AKAZE_OCTAVE_LABEL = "Jumlah Oktaf"
AKAZE_OCTAVE_DESCRIPTION = """ Parameter yang mengatur berapa banyak tahap skala yang akan dianalisis
semasa mencari ciri-ciri penting dalam sebuah imej. Bayangkan anda melihat imej dengan pelbagai tahap zum;
setiap tahap zum ini disebut "oktaf".

- Setiap oktaf: Mewakili tahap zum yang berbeza, membolehkan algoritma mengesan ciri pada pelbagai saiz.
  Misalnya, ciri kecil akan kelihatan semasa diperbesar, manakala ciri besar dapat dikenali pada Zum
  yang lebih jauh.

- Lebih banyak oktaf: Memberikan keupayaan untuk mengesan ciri pada lebih banyak skala atau saiz.
  Namun, komputer perlu bekerja lebih keras dan masa pemprosesan menjadi lebih lama.

Nilai yang disyorkan: 4.
"""
AKAZE_LAYER_LABEL = "Jumlah Lapisan per Oktaf"
AKAZE_LAYER_DESCRIPTION = """Lapisan per Oktaf menentukan jumlah sub-level dalam setiap oktaf.

- Lebih banyak lapisan memberikan resolusi ruang skala yang lebih halus,
  sehingga dapat meningkatkan pengesanan ciri di pelbagai skala.

- Namun, menambah lapisan juga meningkatkan beban pengiraan.

Nilai yang disyorkan: 4.
"""
AKAZE_RATIO_LABEL = "Nisbah Threshold"
AKAZE_RATIO_DESCRIPTION = """Nisbah Threshold merupakan nilai yang digunakan semasa memadankan ciri-ciri penting (keypoint)
antara dua imej. Tujuannya untuk memastikan bahawa padanan yang ditemui benar-benar tepat dan bukan satu kebetulan.

- Nisbah lebih rendah (mendekati 0.50): Hanya menerima padanan yang sangat jelas yang tidak diragui lagi.
  Dengan kata lain, lebih selektif dalam memilih padanan, sehingga kemungkinan mendapat kesilapan dalam memadankan
  keypoint palsu lebih kecil.

- Nisbah lebih tinggi (mendekati 1.00): Bermakna kita lebih bertoleransi dalam menerima padanan,
  sehingga lebih banyak padanan diterima. Namun, ini juga meningkatkan kemungkinan kesilapan
  dalam memadankan keypoint.

Nilai yang disyorkan: 0.80.
"""


# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "Peratus Overlap"
OVERLAP_DESCRIPTION = """Digunakan untuk mengurangkan artifak petak (yang menyebabkan kesan berkotak pada kawasan yang bergerak).

Meningkatkan overlap boleh mengurangkan kesan ini, tetapi juga akan menambah masa pemprosesan."""

TILE_SIZE_LABEL = "Saiz Petak (Tile)"
TILE_SIZE_DESCRIPTION = """Semakin kecil saiz petak, semakin halus perbezaan dapat dikesan.

Namun, ini juga meningkatkan masa pemprosesan dan kebarangkalian kesilapan dalam pengesanan perbezaan."""

MOTION_SENSIVITY_LABEL = "Sensitiviti Pergerakan"
MOTION_SENSIVITY_DESCRIPTION = """Sensitiviti pergerakan mengawal betapa agresif algoritma mengesan perbezaan dalam setiap petak.

Nilai yang lebih rendah menjadikan pengesanan lebih sensitif atau agresif, tetapi boleh menyebabkan bunyi (noise) dianggap sebagai perbezaan sebenar."""

NOISE_OFFSET_LABEL = "Offset Noise"
NOISE_OFFSET_DESCRIPTION = """Ambang untuk mengabaikan tahap noise dalam imej supaya noise yang tinggi tidak dianggap sebagai pergerakan.

Nilai yang lebih tinggi boleh menghasilkan gabungan imej yang lebih bersih untuk gambar yang sangat bising, tetapi boleh menjejaskan ketepatan pengesanan pergerakan."""


# --- General Alignment Options (Edges, Crop, Saving) ---
KEEP_EDGES_LABEL = """Kekalkan Tepi"""
IGNORE_EDGE_LABEL= """Abaikan Tepi"""
KEEP_EDGES_DESCRIPTION = """Fitur Kekalkan Tepi membolehkan algoritma menjaga tepi imej
tetap utuh semasa proses penjajaran."""

ENABLE_CROP_LABEL = """Aktifkan
Pemotongan"""
DISABLE_CROP_LABEL = """Nyahaktifkan
Pemotongan"""
CROP_DESCRIPTION = """Aktifkan Pemotongan untuk menghilangkan
sempadan imej yang tidak terpakai.

Nota: Kadang-kadang pepijat pemotongan berlaku (sangat jarang).
Seperti imej yang sangat kecil, atau kesilapan dalam memotong imej."""

ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "Simpan ke folder"
DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = """Tidak menyimpan
ke folder"""
SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER = "Layari.."
DEFAULT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Folder Lalai"
SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Pilih folder"
SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """Menyimpan imej hasil penjajaran ke dalam folder.
Folder lalai adalah folder Dokumen di PC anda."""

ACTIVATE_SAVE_ALIGN_TO_PROCESS = """Simpan untuk
proses seterusnya"""
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = """Tidak menyimpan
proses seterusnya"""
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """Menyimpan imej untuk proses
denoising ataupun super resolusi"""


# ==============================================================================
# Algorithm General Descriptions (Overview)
# ==============================================================================
# --- Alignment Algorithm Descriptions ---
ALIGNMENT_NAME = "Algoritma Penjajaran"
NONE_ALIGNMENT_DESCRIPTION = "Tiada penjajaran akan digunakan."
FARNEBACK_DESCRIPTION = """Algoritma ini sesuai untuk penjajaran tahap tinggi yang memerlukan ketepatan dan kejituan hingga tahap piksel.
Namun, sangat lemah terhadap perbezaan putaran dan perspektif yang signifikan."""
AKAZE_DESCRIPTION = """Algoritma ini agak tahan terhadap perbezaan besar dalam putaran, perspektif, dan skala.

Cukup baik, tetapi tidak sebaik Farneback untuk tahap piksel."""
ORB_DESCRIPTION = """Algoritma cepat namun kurang tepat untuk perbezaan yang signifikan.

Sesuai untuk imej dengan perbezaan minimum, dan tepat pada imej dengan tekstur rawak."""

# --- Super Resolution Algorithm Descriptions ---
SUPER_RESOLUTION_NAME = "Algoritma Super Resolution"
NONE_SUPER_RESOLUTION_DESCRIPTION = "Tiada super resolution akan digunakan."
INTERPOLATION_DESCRIPTION = """Algoritma ringkas untuk meningkatkan resolusi dengan kaedah interpolasi,
menambah sedikit butiran."""

# --- Denoising Algorithm Descriptions ---
DENOISING_NAME = "Algoritma Denoising"
NONE_DENOISING_DESCRIPTION = "Tiada pengurangan hingar (denoising) akan digunakan."
WEIGHTED_AVERAGE_DESCRIPTION = """Hasil daripada penyederhanaan kaedah penindanan similarity.
Cukup baik dalam menangani pergerakan kecil, tetapi menghasilkan artefak imej pada pergerakan yang lebih besar."""
AVERAGE_DESCRIPTION = """Kaedah penindanan yang sangat cepat dan berkesan untuk objek dan babak statik.
Tidak sesuai untuk babak atau kawasan yang bergerak, tetapi boleh digabungkan dengan penjajaran
Farneback untuk menghilangkan pergerakan objek yang ringan."""
MEDIAN_DESCRIPTION = """Cepat dan berkesan untuk penindanan, cukup baik pada objek yang bergerak.
Sangat berkesan dalam menghilangkan pergerakan kecil pada objek, namun artefak muncul pada pergerakan yang lebih besar."""
SIMILARITY_DESCRIPTION = """Algoritma penindanan canggih, sangat kuat dalam menghilangkan pergerakan objek
(sangat sedikit ghosting di kawasan yang bergerak) dan menghasilkan sangat sedikit artefak hingga 85%.

Diinspirasikan oleh:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""
SIMILARITY_MOTION_V2_DESCRIPTION = """Similarity V2 merupakan hasil pengembangan daripada algoritma similarity v1 dengan sejumlah
peningkatan signifikan. Algoritma ini mampu menghasilkan imej yang lebih bersih walaupun input mengandungi hingar (noise) yang teruk, berkat keupayaannya
secara bijak membezakan antara hingar, tekstur, dan pergerakan halus. Lebih andal dengan pencahayaan minimum, namun prosesnya berjalan lebih lambat
berbanding versi v1."""


# ==============================================================================
# Application Settings UI
# ==============================================================================
SETTING_GENERAL_LABEL = "Umum"
LANGUAGE_LABEL = "Bahasa"
LANGUAGE_TYPE = "Inggeris", "Indonesia", "Cina Tradisional", "Melayu"
GPU_ACCELERATION_LABEL = "Penggunaan GPU"
MULTI_CORE_CPU = "Penggunaan CPU Multicore"
SETTINGS_SAVED = "Settings telah disimpan."

CANT_READ_FILE_SETTINGS = "Amaran: Tidak dapat membaca fail tetapan '{GENERAL_SETTINGS_FILE}'. Menggunakan nilai lalai."

MULTI_CORE_CPU_DESCRIPTION = """Mengaktifkan fungsi ini akan meningkatkan kelajuan pengiraan dalam memproses imej, tetapi ia juga akan menambah sedikit penggunaan RAM.

Jika komputer mempunyai RAM yang sangat terhad, disyorkan untuk tidak mengaktifkannya."""
GPU_ACCELERATION_DESCRIPTION = """Mengaktifkan fungsi ini akan sangat meningkatkan kelajuan pengiraan kerana ia menggunakan GPU dalam prosesnya.

NOTA: Penggunaan GPU adalah terhad kepada proses Farneback sahaja, algoritma lain akan mendapat implementasi kelak."""

THUMBNAIL_LABEL = "Thumbnail"
THUMBNAIL_DESCRIPTION = """Pratonton imej untuk proses kelompok, masih EKSPERIMEN
Kadangkala menyebabkan kelipan atau ketinggalan apabila menambah kumpulan baharu"""

NOISE_MAD_OFFSET_LABEL = "Faktor Noise MAD"
NOISE_MAD_OFFSET_DESCRIPTION = """Menentukan seberapa sensitif pengesanan MAD dalam mengendalikan imej dengan noise tinggi.

Nilai yang lebih tinggi membolehkan toleransi yang lebih besar terhadap noise (iaitu, kurang sensitif dalam kawasan dengan noise tinggi),
tetapi boleh menyebabkan kesan ghosting di kawasan tersebut apabila berlaku pergerakan.
"""

MAD_SENSITIVITY_LABEL = "Sensitiviti MAD"
MAD_SENSITIVITY_DESCRIPTION = """Menentukan sensitiviti MAD dalam mengesan perbezaan dalam imej.

Nilai yang lebih tinggi meningkatkan sensitiviti terhadap perbezaan halus, tetapi juga boleh meningkatkan kemungkinan kesilapan
jika imej input mengandungi noise yang tinggi.
"""

CONF_SKIP_DFT_LABEL = """Kepercayaan untuk
Melangkau Proses DFT"""
CONF_SKIP_DFT_DESCRIPTION = """Ambang untuk melangkau proses DFT sekiranya proses MBM telah mengendalikan dengan baik.

Nilai yang lebih tinggi bermaksud lebih banyak proses akan dijalankan oleh MAD. Walaupun begitu, MAD adalah kaedah pengesanan kasar
yang sensitif terhadap noise dan kawasan dengan kontras rendah, tetapi kelebihannya adalah pengiraan yang lebih ringan.
"""

WIENER_C_FACTOR_LABEL = "Faktor Wiener C"
WIENER_C_FACTOR_DESCRIPTION = """Menentukan seberapa sensitif pengiraan DCT Wiener dalam mengesan perbezaan dalam imej.

Nilai yang lebih rendah menjadikannya lebih sensitif terhadap pergerakan halus, walaupun ini juga boleh meningkatkan noise
kerana noise itu sendiri boleh mencetuskan pergerakan palsu. Faktor Wiener C berfungsi bersama dengan Sensitiviti MAD.
"""

COARSE_MARGIN_LABEL = "Margin Penjajaran Kasar"
COARSE_MARGIN_DESCRIPTION = """Tetingkap margin untuk penjajaran pada tahap tile.

Ia meningkatkan ketepatan sehingga ke peringkat tile, sekaligus mempertingkatkan keakuratan stacking.
Prestasi mungkin terjejas jika kawasan carian terlalu luas.
"""


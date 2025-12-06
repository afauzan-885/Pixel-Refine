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
ORB_NFEATURES_DESCRIPTION = """Bilangan ciri menentukan berapa banyak perincian halus yang dapat dikenal pasti dalam sesebuah imej.

- Bilangan ciri yang lebih tinggi membolehkan algoritma mencari lebih banyak perincian,
  menghasilkan penjajaran imej yang lebih jitu. Walau bagaimanapun, ini meningkatkan masa pengkomputeran.

- Biasanya, nilai antara 500 hingga 1500 sudah mencukupi untuk kebanyakan babak imej.
  Untuk keperluan ketepatan yang sangat tinggi, memilih nilai antara 2500 hingga 5000 boleh meningkatkan ketepatan."""
ORB_SCALEFACTOR_LABEL = "Faktor Skala"
ORB_SCALEFACTOR_DESCRIPTION = """Faktor Skala menentukan kadar penurunan skala imej secara beransur-ansur semasa pemprosesan.

- Jika nilainya menghampiri 1.0, imej dikecilkan secara perlahan dengan lebih banyak langkah.
  Ini membolehkan pengesanan perincian yang lebih halus, tetapi memerlukan masa yang lebih lama.

- Jika nilainya lebih besar, imej dikecilkan dengan lebih cepat, menjadikan pemprosesan lebih singkat,
  tetapi mungkin ada beberapa perincian kecil yang terlepas.

Biasanya, nilai Faktor Skala adalah antara 1.2 hingga 1.5."""
ORB_NLEVELS_LABEL = "Bilangan Aras"
ORB_NLEVELS_DESCRIPTION = """Bilangan aras menunjukkan jumlah lapisan dalam piramid imej yang digunakan untuk mengesan ciri.

- Semakin banyak aras, semakin banyak perincian yang dapat ditangkap oleh algoritma pada pelbagai skala,
  ini berguna jika saiz imej berbeza-beza.

- Namun, semakin tinggi bilangan aras, semakin lama masa pemprosesannya.

Untuk kebanyakan babak, nilai antara 2 hingga 4 sudah cukup ideal."""
ORB_TRANSFORMATION_LABEL = "Jenis Transformasi"
ORB_TRANSFORMATION_DESCRIPTION = """Pilih kaedah untuk menjajarkan imej mengikut keperluan anda:

Pilihan yang tersedia termasuk:
- HOMOGRAFI: Sesuai untuk foto dengan perbezaan sudut yang agak ekstrem (cth: gambar meja dari atas lwn. dari sisi).
  Boleh melaraskan kesan "perspektif".

- AFIN: Boleh diputar, diubah saiz (boleh jadi tidak seragam), dan dialihkan.
  Contoh: membetulkan foto yang senget dan perlu dibesarkan sebahagiannya.

- KESERUPAAN (Similarity): Hanya membenarkan putaran, pembesaran/pengecilan yang seragam, dan peralihan.
  Nisbah aspek dikekalkan.

- EUCLIDEAN: Paling ringkas: hanya putar dan alihkan imej tanpa mengubah saiz.
  Sesuai untuk membetulkan foto yang sedikit senget.

Saranan Pemilihan:
- Untuk kebanyakan kes (terutamanya foto dari sudut yang agak ekstrem), pilih Homografi.
- Jika imej hanya perlu dilaraskan kedudukan/putaran yang ringkas, Euclidean atau Keserupaan lebih sesuai.
- Gunakan Afin hanya jika perlu pelarasan bentuk yang fleksibel tanpa kesan perspektif."""
ORB_RANSAC_LABEL = "Ambang RANSAC"
ORB_RANSAC_DESCRIPTION = """Ambang RANSAC menentukan sejauh mana ketatnya algoritma menapis nilai-nilai terpencil
(data yang menyimpang jauh) semasa menjajarkan imej.

- Nilai lebih rendah (contohnya, 1-2) bermakna penapisan lebih ketat, jadi beberapa ciri penting mungkin terabai.

- Nilai lebih tinggi (contohnya, 4-5) lebih bertolak ansur terhadap nilai terpencil, membolehkan lebih banyak ciri digunakan,
  tetapi boleh mengurangkan ketepatan penjajaran.

Biasanya, nilai antara 1 hingga 3 sudah mencukupi, bergantung pada tahap hingar dalam data."""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Parameter Farneback"
FARNEBACK_PYRAMID_SCALE_LABEL = "Skala Piramid"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Skala Piramid ialah faktor yang menentukan sejauh mana imej
dikecilkan pada setiap aras piramid.

- Nilai ini menentukan betapa besar pengurangan saiz imej (downscale) dari satu aras ke aras berikutnya.
  Contohnya, jika nilainya 0.5, maka setiap aras akan mempunyai saiz separuh daripada aras sebelumnya.

- Nilai yang lebih kecil (sekitar 0.10 hingga 0.5) menyebabkan perbezaan saiz antara aras lebih besar.
  Ini boleh mempercepatkan pengkomputeran, tetapi mungkin mengurangkan ketepatan dalam menangkap gerakan halus.

- Nilai yang menghampiri 1.00 menghasilkan perubahan saiz yang lebih kecil antara aras,
  membolehkan pengesanan gerakan yang lebih tepat, dengan masa pengkomputeran yang lebih lama.

Laraskan nilai ini mengikut keperluan anda untuk mencari keseimbangan antara kelajuan pemprosesan dan
ketepatan pengesanan gerak.
Nilai yang disyorkan: 0.5
"""
FARNEBACK_LEVELS_LABEL = "Aras"
FARNEBACK_LEVELS_DESCRIPTION = """Parameter Aras dalam algoritma Farneback merujuk kepada bilangan lapisan
dalam piramid imej yang digunakan untuk mengira aliran optik.

- Lebih banyak aras: Algoritma dapat mengesan pergerakan objek pada pelbagai saiz dan kelajuan,
  termasuk gerakan yang kompleks atau meliputi kawasan yang luas. Walau bagaimanapun, ini memerlukan
  masa pengkomputeran yang lebih lama.

- Namun, semakin banyak aras yang digunakan, semakin lama masa pengkomputeran yang diperlukan.

Anda boleh melaraskannya antara 1 hingga 10 mengikut keperluan aplikasi anda.
Secara umum, nilai 3 dianggap sebagai standard.
"""
FARNEBACK_WIN_SIZE_LABEL = "Saiz Tetingkap"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Saiz Tetingkap menentukan berapa banyak kawasan piksel (tetingkap)
yang digunakan dalam pengiraan aliran optik.

- Saiz tetingkap yang lebih besar: Menghasilkan anggaran pergerakan yang lebih stabil dan licin kerana
  maklumat dikira dari kawasan yang lebih luas. Namun, butiran pergerakan kecil mungkin terlepas.

- Saiz tetingkap yang lebih kecil: Lebih sensitif terhadap pergerakan kecil,
  namun hingar boleh dianggap sebagai gerakan dan kurang stabil.

Anda boleh memilih nilai antara sensitif terhadap butiran gerakan kecil
dan hasil yang stabil.
Nilai yang disyorkan: 15.
"""
FARNEBACK_ITERATIONS_LABEL = "Lelaran"
FARNEBACK_ITERATIONS_DESCRIPTION = """Lelaran (Iterations) menentukan berapa kali pengiraan aliran optik diperbaiki pada setiap aras piramid.

- Semakin banyak lelaran, semakin tepat hasil aliran optik yang diperoleh.
- Namun, peningkatan jumlah lelaran juga boleh melambatkan masa pengkomputeran.

Pilih nilai yang dapat meningkatkan ketepatan tanpa terlalu melambatkan proses.
Nilai yang disyorkan: 3.
"""
FARNEBACK_POLY_N_LABEL = "Pengembangan Polinomial"
FARNEBACK_POLY_N_DESCRIPTION = """Pengembangan Polinomial (poly_n) menentukan saiz kawasan piksel yang digunakan,
untuk menganggarkan gerakan dengan kaedah pengembangan polinomial.

- Nilai ini menentukan berapa banyak data piksel di sekitar yang digunakan dalam pengiraan.

- Nilai yang lebih besar akan menghasilkan anggaran gerakan yang lebih licin,
  tetapi dapat mengurangkan kepekaan terhadap gerakan kecil.

Biasanya, nilai yang digunakan ialah 5 atau 7, bergantung pada tahap perincian dan kestabilan yang diinginkan.
"""
FARNEBACK_POLY_SIGMA_LABEL = "Sigma Polinomial"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Sigma Polinomial mengawal sejauh mana pelicinan
yang diterapkan sebelum pengembangan polinomial dilakukan.

- Nilai ini merupakan sisihan piawai bagi penapis Gaussian yang digunakan untuk mengurangkan hingar pada data piksel.
- Sigma yang lebih tinggi boleh membantu meredam hingar,

  tetapi jika terlalu tinggi boleh menghilangkan butiran gerakan yang penting.

Tetapkan dengan teliti untuk mengurangkan hingar tanpa kehilangan butiran gerakan yang signifikan.
Nilai yang disyorkan: 1.2.
"""
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
AKAZE_THRESHOLD_DESCRIPTION = """Parameter Ambang menentukan kepekaan pengesan
untuk mencari titik kunci (keypoint).

- Nilai yang lebih rendah meningkatkan pengesanan titik kunci yang lebih banyak,
  termasuk imej yang mempunyai ciri yang sedikit dan banyak hingar.

- Nilai yang lebih tinggi hanya mengehadkan pengesanan kepada ciri yang paling kuat sahaja.

Nilai yang disyorkan: 0.0010.
"""
AKAZE_OCTAVE_LABEL = "Bilangan Oktaf"
AKAZE_OCTAVE_DESCRIPTION = """Parameter yang mengawal berapa banyak aras skala yang akan dianalisis
semasa mencari ciri-ciri penting dalam sesebuah imej. Bayangkan anda melihat imej dengan pelbagai aras zum;
setiap aras zum ini dipanggil "oktaf".

- Setiap oktaf: Mewakili aras zum yang berbeza, membolehkan algoritma mengesan ciri pada pelbagai saiz.
  Contohnya, ciri kecil akan kelihatan semasa imej dibesarkan, manakala ciri besar dapat dikenali pada Zum
  yang lebih jauh.

- Lebih banyak oktaf: Memberi keupayaan untuk mengesan ciri pada lebih banyak skala atau saiz.
  Namun, komputer perlu bekerja lebih keras dan masa pemprosesan menjadi lebih lama.

Nilai yang disyorkan: 4.
"""
AKAZE_LAYER_LABEL = "Bilangan Lapisan setiap Oktaf"
AKAZE_LAYER_DESCRIPTION = """Lapisan setiap Oktaf menentukan bilangan sub-aras dalam setiap oktaf.

- Lebih banyak lapisan memberikan resolusi ruang skala yang lebih halus,
  supaya dapat meningkatkan pengesanan ciri di pelbagai skala.

- Namun, menambah lapisan juga meningkatkan beban pengkomputeran.

Nilai yang disyorkan: 4.
"""
AKAZE_RATIO_LABEL = "Ambang Nisbah"
AKAZE_RATIO_DESCRIPTION = """Ambang Nisbah merupakan nilai yang digunakan semasa memadankan ciri-ciri penting (keypoint)
antara dua imej. Tujuannya untuk memastikan bahawa padanan yang ditemui benar-benar tepat dan bukan satu kebetulan.

- Nisbah lebih rendah (menghampiri 0.50): Hanya menerima padanan yang sangat jelas dan tidak diragui lagi.
  Dengan kata lain, lebih memilih dalam memilih padanan, jadi kemungkinan mendapat kesilapan dalam memadankan
  titik kunci palsu lebih kecil.

- Nisbah lebih tinggi (menghampiri 1.00): Bermakna kita lebih bertolak ansur dalam menerima padanan,
  jadi lebih banyak padanan yang diterima. Namun, ini juga meningkatkan kemungkinan kesilapan
  dalam memadankan titik kunci.

Nilai yang disyorkan: 0.80.
"""

# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "Pertindihan %"
OVERLAP_DESCRIPTION = """Berfungsi untuk mengurangkan artifak jubin (yang menyebabkan kesan petak-petak pada kawasan yang bergerak).

Meningkatkan pertindihan boleh mengurangkan kesan tersebut, namun akan meningkatkan masa pengkomputeran."""

TILE_SIZE_LABEL = "Saiz Jubin (tile)"
TILE_SIZE_DESCRIPTION = """Semakin kecil saiz jubin, semakin terperinci pengesanan perbezaan.

Namun ini juga akan meningkatkan masa pengkomputeran dan meningkatkan kemungkinan ralat dalam pengesanan perbezaan."""

MOTION_SENSIVITY_LABEL = """Kepekaan Gerakan"""
MOTION_SENSIVITY_DESCRIPTION = """Kepekaan gerakan mengawal seberapa agresif algoritma dalam mengesan perbezaan dalam sebuah jubin.

Semakin rendah nilainya, semakin agresif atau peka dalam mengesan perbezaan,
namun hal ini menyebabkan hingar akan turut dianggap sebagai perbezaan."""

NOISE_OFFSET_LABEL = """Ofset Hingar"""
NOISE_OFFSET_DESCRIPTION = """Ambang batas untuk mengabaikan tahap hingar pada imej, supaya hingar yang lebih tinggi tidak dianggap sebagai pergerakan.

Semakin tinggi nilainya, hasil penindanan boleh menjadi lebih bersih untuk imej dengan hingar ekstrem, namun ini juga boleh mengurangkan pengesanan pergerakan pada imej."""

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
LANGUAGE_LABEL = "Bahasa"
LANGUAGE_TYPE = "Inggeris", "Indonesia", "Cina Tradisional", "Melayu"
GPU_ACCELERATION_LABEL = "Pecutan GPU"
MULTI_CORE_CPU = "Pecutan Multi-Teras CPU"
SETTINGS_SAVED = "Tetapan berjaya disimpan."

CANT_READ_FILE_SETTINGS = "Amaran: Tidak dapat membaca fail tetapan '{GENERAL_SETTINGS_FILE}'. Menggunakan nilai lalai."
MULTI_CORE_CPU_DESCRIPTION = """Mengaktifkannya akan meningkatkan kelajuan pengkomputeran dalam memproses imej, namun akan menambah sedikit penggunaan RAM.

Jika Komputer mempunyai RAM yang sangat terhad, disyorkan untuk tidak menandakannya."""

GPU_ACCELERATION_DESCRIPTION = """Mengaktifkannya akan sangat meningkatkan kelajuan pengkomputeran, kerana menggunakan GPU dalam prosesnya.

NOTA: Penggunaan GPU hanya terhad pada proses Farneback dan lightglue sahaj, algoritma lain akan menyusul pelaksanaannya."""

THUMBNAIL_LABEL = "Imej Kenit (Thumbnail)"
THUMBNAIL_DESCRIPTION = """Pratonton imej untuk proses batch, masih bersifat EKSPERIMEN.
Kadangkala menimbulkan kelipan atau lengah masa (lag) semasa menambah batch baharu."""

NOISE_MAD_OFFSET_LABEL = "Faktor Hingar MAD"
NOISE_MAD_OFFSET_DESCRIPTION = """Tahap kepekaan pengesanan MAD dalam mengendalikan imej dengan hingar tinggi.

Nilai yang lebih tinggi menyebabkan toleransi terhadap hingar (tidak terlalu sensitif di kawasan dengan hingar yang tinggi),
namun akan menyebabkan kesan 'ghosting' pada kawasan tersebut jika berlaku gerakan."""

MAD_SENSITIVITY_LABEL = "Kepekaan MAD"
MAD_SENSITIVITY_DESCRIPTION = """Tahap kepekaan MAD dalam mengendalikan perbezaan pada sebuah imej.

Nilai yang lebih tinggi akan lebih peka terhadap perbezaan halus, namun meningkatkan ralat pengesanan
jika imej input mempunyai hingar yang tinggi."""

CONF_SKIP_DFT_LABEL = "Keyakinan Melangkau\nProses DFT"
CONF_SKIP_DFT_DESCRIPTION = """Ambang untuk melangkau DFT jika proses MBM sudah menanganinya dengan baik.

Semakin tinggi nilainya, maka semakin banyak prosesnya akan dilakukan oleh MAD. Namun MAD adalah pengesanan kasar;
ia sensitif terhadap hingar dan kawasan kontras rendah, tetapi kelebihan dengan banyaknya proses MAD ialah pengkomputeran
yang lebih ringan."""

WIENER_C_FACTOR_LABEL = "Faktor Wiener C"
WIENER_C_FACTOR_DESCRIPTION = """Tahap kepekaan pengiraan DCT Wiener dalam mengesan perbezaan dalam sebuah imej.

Semakin rendah nilainya, maka semakin peka dalam mengesan pergerakan halus, namun hal ini memberi kesan dengan peningkatan hingar
kerana hingar itu sendiri menyebabkan pergerakan palsu. Nilai Faktor Wiener C bekerjasama dengan Kepekaan MAD."""

COARSE_MARGIN_LABEL = "Margin Jajar Kasar"
COARSE_MARGIN_DESCRIPTION = """Tetingkap Margin untuk penjajaran di tahap jubin.

Kesan ini adalah untuk meningkatkan ketepatan hingga ke tahap jubin, meningkatkan ketepatan penindanan.
Akan memberi kesan yang agak besar pada prestasi jika kawasan carian terlalu luas."""
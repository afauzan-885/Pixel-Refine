# -*- coding: utf-8 -*-

# ==============================================================================
# General UI Elements & Messages
# ==============================================================================
# Placeholder/General Info
UNDER_DEVELOPMENT = "Menu {page_name} sedang dalam pengembangan"
LOADING_THUMBNAIL = "Memuat...."
NOT_IMAGE_PREVIEW = "Tidak ada gambar tersedia"
MODULE_NOT_IMPLEMENT = "Modul belum diimplementasikan."

# Buttons
ADD_IMAGE_BUTTON = "Tambah"
PREVIEW_IMAGE_BUTTON = "Pratinjau"
DELETE_IMAGE_BUTTON = "Hapus"
CLOSE_BUTTON = "Tutup"
APPLY_PARAMETER_BUTTON_TEXT = "Terapkan Pengaturan"
APPY_PARAMETER = "Terapkan"
CANCEL_PARAMETER = "Batal"

# Labels
PREVIEW_PANEL_LABEL = "Panel Pratinjau"

# Window Messages
WINDOW_START_PROCESSING = "Memulai proses..."
WINDOW_PROCESSING_COMPLETE = "Selesai!"

# Application Control
RESTART_APPLICATION_REQUIRED = "Mulai ulang Diperlukan"
RESTART_APPLICATION_DESCRIPTION = "Mulai ulang untuk melihat perubahan"
ACCEPT_RESTART_APPLICATION = "Mulai Ulang"
REJECT_APPLICATION_DESCRIPTION = "Nanti saja"
COMMAND_APPLICATION_DESCRIPTION = "Muat Ulang Aplikasi..."
TRY_RESTART_APPLICATION = "Mencoba memuat ulang aplikasi"
COMMAND_FAILED_IN_RESTART_APPLICATION = "Sistem gagal dimulai ulang."
RESTART_FAILED = "Mulai ulang Gagal"
COMMAND_TO_RESTART_MANUALLY = "Tidak dapat memulai ulang aplikasi secara otomatis. Silakan mulai ulang secara manual."



# ==============================================================================
# Sidebar UI
# ==============================================================================

SETTINGS_SIDEBAR_LABEL= "Pengaturan"
PANORAMA_SIDEBAR_LABEL= "Panorama"


# ==============================================================================
# Topbar UI
# ==============================================================================
# Single Image Actions
TOPBAR_SINGLE_IMPORT_BUTTON_TEXT = "Impor Gambar"
TOPBAR_SINGLE_DELETE_BUTTON_TEXT = "Hapus Gambar"

# Batch Actions
TOPBAR_BATCH_IMPORT_BUTTON_TEXT = "Impor Gambar"
TOPBAR_BATCH_DELETE_BUTTON_TEXT = "Hapus Batch"
TOPBAR_BATCH_START_PROCESS_BUTTON_TEXT = "Proses Batch"
TOPBAR_BATCH_SAVE_BUTTON_TEXT = "Simpan Ke"


# ==============================================================================
# Batch Processing UI & Messages
# ==============================================================================
# General Batch Info & Status
NO_DATA_BATCH = "Tidak ada batch yang tersimpan."
UI_NO_CHANGE = "Tidak Berubah"
UI_ALGORITHM_EDIT_HEADER = "Edit Algoritma secara massal"
UI_BATCH_HEADER = "Proses Batch"
UI_ALGORIHM_EDIT = "Edit Algoritma"
UI_ALGORITHM_NOT_SET = "Algoritma belum dipilih."
UI_FOLDER_PATH_NOT_SET = "Folder tujuan belum diatur."
UI_BATCH_NOT_CONFIGURE = "Batch belum diatur."
UI_LABEL_BATCH_NO_PROCESS = "Tidak ada batch yang diproses!"
UI_LABEL_BATCH_SUCCES = "Semua batch telah diproses!"
UI_LABEL_BATCH_PROCESS = "Memproses {} batch..."
UI_LABEL_BATCH_PROGRESS = "{}/{} batch telah diproses..."
UI_LABEL_MOVING_FILES = "Memindahkan {} file ke folder '{}'. Harap tunggu..."
PROCESSING_BATCH = "--- Memproses batch {}/{} (Telah di proses: {}) ---"
NUMBER_OF_BATCHES_TO_BE_PROCESSED = "Jumlah batch yang akan diproses: {}"
BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS = "batch_id harus ada untuk proses batch"
SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED = "Melewati batch {} karena gambar tidak ada yang dimuat."
BATCH_LABEL_FORMAT = "Batch {}   -   ({} gambar)"
BATCH_CANCELED_BY_USER = "Proses batch dibatalkan."
BATCH_CANCELED_HEADER = "Batch Dibatalkan"
BATCH_CANCELED_INFO = "Dibatalkan"
BATCH_CANCELED_PROCESS = "Batalkan Proses" 
BATCH_CANCELED_CONFIRMATION = "Apakah Anda yakin ingin membatalkan semua proses yang sedang berlangsung?"
BATCH_QUEUE = "Menunggu"
BATCH_SUCCESS = "Proses batch selesai."
BATCH_SUCCESS_HEADER = "Selesai"



# --- Dialogue Title ---
SELECT_OUTPUT_FOLDER_TITLE = "Pilih Folder Output untuk Simpan Batch"
OUTPUT_FOLDER_SELECTION_CANCELLED = "Pemilihan folder dibatalkan. Proses dihentikan."
ALGORITHM_SUCCESS_UPDATE = "Pengaturan algoritma berhasil diperbarui untuk batch {} hingga {}."

# --- General Error Messages & Dialogs ---
BATCH_PROCESSING_ERROR_TITLE = "Kesalahan Proses Batch"
BATCH_PROCESSING_ERROR_MESSAGE = "Gagal memproses Batch {} (ID: {}):\n{}" 
BATCH_SAVE_ERROR_TITLE = "Gagal Menyimpan"
TARGET_FOLDER_NOT_ACCESSIBLE = "Folder tujuan tidak dapat diakses:\n{}" 
MOVE_FILE_ERROR_TITLE = "Gagal Memindahkan File"
COULD_NOT_SAVE_FILE_FOR_BATCH = "Gagal menyimpan file '{}' untuk batch:\n{}" 
SOURCE_FILE_DOES_NOT_EXIST = "Gagal pindah: File sumber '{}' tidak ditemukan."
TARGET_FOLDER_INVALID = "Gagal pindah: Folder tujuan '{}' tidak valid."
BATCH_CONFIGURATION_INFO = "Batch belum dikonfigurasi"

BATCH_PROCESSING_ERROR_REPORT_TITLE = "Laporan Kesalahan Pemrosesan Batch"
BATCH_PROCESSING_ERROR_REPORT_INTRO = "Proses selesai dengan {num_failed} dari {num_total} batch gagal diproses. Detail:"
BATCH_PROCESSING_ERROR_REPORT_ITEM = "• Batch #{seq} (ID: {id})\n  Penyebab: {error}"

# --- Log Message
LOG_BATCH_PROCESSING_START = "Memulai pemrosesan untuk {} batch..." 
LOG_PROCESSING_BATCH_DETAIL = "Memproses Batch ke-{} (ID: {}), urutan ({}/{})..."
LOG_WARN_MULTIPLE_NEW_FILES = "Peringatan: Ada >1 file baru untuk Batch {}. Dipindahkan yang pertama: {}"
LOG_BATCH_PROCESSED_NEW_OUTPUT = "Batch {} selesai, output baru: {}"
LOG_BATCH_PROCESSED_NO_OUTPUT = "Batch {} selesai, tapi tidak ada file output baru di folder '{}'." 
LOG_ERROR_PROCESSING_BATCH = "Error saat memproses Batch {}: {}" 
LOG_ALL_BATCH_ATTEMPTS_FINISHED = "Semua pemrosesan batch telah selesai."

LOG_MOVE_SUCCESS = "Berhasil memindahkan '{}' ke '{}'."
LOG_MOVE_FAILED = "Gagal memindahkan '{}' ke '{}': {}" 
LOG_SOURCE_FILE_NOT_FOUND = "File sumber tidak ditemukan: {}" 
LOG_TARGET_FOLDER_NOT_FOUND = "Folder tujuan tidak valid: {}"


# Toast message for process_all_batches
UI_LABEL_BATCH_NO_PROCESS = "Tidak ada batch dipilih untuk diproses."
UI_LABEL_BATCH_PROCESS_START = "Memulai proses untuk {} batch..." 
UI_LABEL_BATCH_PROGRESS_DONE_SAVED = "Batch {} selesai & disimpan ({}/{})." 
UI_LABEL_BATCH_PROGRESS_SAVE_FAILED = "Batch {} selesai, gagal simpan ({}/{})."
UI_LABEL_BATCH_PROGRESS_NO_OUTPUT = "Batch {} selesai, tanpa output ({}/{})." 
UI_LABEL_BATCH_PROGRESS_ERROR = "Error Batch {} ({}/{})." 

# Final Finished Toast Message
UI_LABEL_BATCH_ALL_SUCCESS_SPECIFIC = "Semua {} batch berhasil diproses & disimpan ke {}." 
UI_LABEL_BATCH_PARTIAL_SUCCESS_SPECIFIC = "{} dari {} batch disimpan ke {}. Beberapa bermasalah."
UI_LABEL_BATCH_NO_SUCCESS_SPECIFIC = "Proses selesai. Tidak ada hasil batch yang disimpan ke {}."
UI_LABEL_BATCH_NONE_PROCESSED = "Tidak ada batch yang diproses."



# Batch Deletion
BATCH_DELETE_LABEL = "Konfirmasi Hapus Batch", "Apakah Anda yakin ingin menghapus batch {}?"
TITLE_BATCH_ALL_DELETE_BUTTON = "Hapus Semua Batch"
CONFIRM_BATCH_ALL_DELETE_BUTTON = "Anda yakin ingin menghapus {} batch?"
NO_DATA_BATCH_ALL_DELETE_BUTTON = "Tidak ada data batch yang tersimpan."

# Batch Parameters UI Labels
PARAMETER_BATCH_CROP_EDGE = "Potong Tepi"
PARAMETER_BATCH_KEEP_EDGE = "Pertahankan Tepi"
PARAMETER_BATCH_DENOISING = "Denoising"
PARAMETER_BATCH_SUPER_RESOLUTION = "Super Resolusi"
PARAMETER_BATCH_ALIGNMENT = "Selaraskan Gambar"
PARAMETER_BATCH_ALIGNMENT_TO_FOLDER = "Simpan Hasil Penyelarasan ke dalam Folder"
PARAMETER_BATCH_ALIGNMENT_TO_PROCESS = "Simpan Hasil Penyelarasan untuk proses Selanjutnya"

# Batch Saving Feedback
UI_FAILED_TO_SAVE_IMAGE_BATCH = "Gagal menyimpan gambar: {}"
UI_SUCCES_TO_SAVE_IMAGE_BATCH = "Gambar berhasil disimpan: {}"
UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH = "Gambar Tidak ada"
UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH = "Folder sistem (database/stack) tidak ada"
UI_NO_BATCH_PROCESS = "Tidak ada batch yang tersedia"

# Batch Specific Errors/Warnings
ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F = "Terjadi kesalahan saat mngambil kunci {} dari HDF5: {}"


# ==============================================================================
# Image Handling (Import/Delete) UI & Messages
# ==============================================================================
# Import
HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "File Gambar (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES = """Seret & lepas gambar ke sini<br>
atau<br>
Gunakan tombol 'Import Gambar'"""
SUPPORTED_IMAGE_EXTENSION = "Format gambar yang didukung"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Pilih Gambar"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Gambar Duplikat"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} gambar sudah ada di database, akan dilewati."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Format Terpilih"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} gambar dengan format '{format}' akan diimpor."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Gagal", "Tidak ada gambar yang valid untuk diimpor." # Tuple for Title, Message
ON_IMPORT_COMPLETE_STATUS = "Impor selesai"
ON_IMPORT_COMPLETE_MESSAGES = "{} gambar telah berhasil diimpor."

# Delete
HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Gagal", "Tidak ada gambar yang dipilih." # Tuple for Title, Message
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Apakah Anda yakin ingin menghapus {} gambar yang dipilih?"


# ==============================================================================
# Preview Panel UI & Messages
# ==============================================================================
UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Memproses gambar, harap tunggu..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "Tidak ada gambar yang dipilih."


# ==============================================================================
# Progress & Status Messages (General)
# ==============================================================================
# Progress Bar
UPDATE_PROGRESS_BAR_STATUS = "{}% ({} proses tersisa)"
OVERALL_PROGRESS = "Progress keseluruhan:"

# Buttons in Progress Sections (if generic)
PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Mulai Proses"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Simpan Sebagai"

# General Process Status/Feedback
PROCESS_ALGORITHM_PROCESS_SKIPPED = "Tidak ada algoritma yang dipilih untuk pemrosesan"
PROCESS_TERMINATED_BY_USER = "Proses Dihentikan Oleh User"
LOADING_IMAGE_PATH = "Memuat {num_in_this_batch} path gambar..."
LOAD_IMAGE_FROM_HDF5 = "Memuat {} gambar dari HDF5..."
NO_IMAGE_PATH_PROCESSED_IMAGE = "Tidak ada path gambar untuk diproses."
PROCESSING_IMAGE_FROM_HDF5 = "Memproses gambar dari HDF5: {}"
OUTPUT_SAVE_WEIGHT_MAP = "Peta bobot akan disimpan ke: {}"
OUTPUT_IMAGE_TO_BE_SAVED = "Output gambar akan disimpan ke: {}"
NO_IMAGES_PROCESSED = "Tidak ada gambar yang dapat diproses"
NUMBER_OF_IMAGES_TO_BE_PROCESSED = "Jumlah gambar yang akan diproses: {}"
RETURNING_IMAGE_RESULTS = "Mengembalikan hasil ({}/{} gambar)."
FINISHING_ANALYSIS = "Menyelesaikan Analisis"
IMAGE_PROCESS_FINISHED = "Penumpukan selesai."
IMAGE_PROCESS_IN_PROGRESS = "Memproses gambar {} dari {}"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Menumpuk batch ke {current} dari {total}"


# ==============================================================================
# Core Processing Messages (Status & Logs)
# ==============================================================================
# General Logging
CONSOL_LOG_RUNNING_ALGORITHM = "Proses {} dipilih, algoritma: {}"

# HDF5 Saving/Loading
SAVE_TO_HDF5_ALIGNED_SAVING = "Menyimpan gambar yang telah diselaraskan"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Gambar ke-{index} telah disimpan."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "Semua gambar berhasil disimpan."
NO_HDF5_FILE_PROCESSING_FROM_PATH = "File HDF5 tidak ditemukan. Memproses dari path gambar..."

# Image Processing Steps
RUN_SAVING_REFERENCE_IMAGE = "Menyimpan gambar referensi."
RUN_IMAGE_PROCESSING = "Memproses gambar {} dari {}..."
RUN_IMAGE_PROCESSING_SAVING = "Gambar ke-{i} telah disimpan."
RUN_IMAGE_PROCESSING_FINISHED = "Proses selesai."
RUN_IMAGE_PROCESS_STARTED = "Memulai proses..."
RUN_PROCESS_TRANSFORMATION = "[1/2] Hitung transformasi {}/{}"
RUN_SAVING_TRANSFORMATION = "[2/2] Simpan hasil {}/{}"


# Motion Compensation / Alignment Steps
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS ="Menyelaraskan dan crop gambar {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION ="Menyimpan gambar {}/{}"
COMPENSATE_MOTION_STATUS = "Melakukan kompensasi gerakan pada gambar {image_id}..."
COMPENSATE_MOTION_FINISHED = "Kompensasi gerakan selesai untuk gambar {image_id}."

# Stacking / Denoising Steps
STACK_IMAGES_PROCESS = "Memproses gambar {current}/{total}..."
ENHANCEMENT = "Menyempurnakan: {}"
STARTING_ENHANCEMENT = "Memulai Penyempurnaan"
START_IMAGE_ENHANCEMENT = "--- Memulai Penyempurnaan {} gambar ---"
ANALYZING_IMAGE = "Menganalisis gambar {}/{}..."
SAVING_WEIGHT_MAP = "Peta bobot disimpan"

# Analysis Steps (e.g., Similarity)
ANALYSIS_STEP_ONE = "Pass 1/2: Membuat Data Adegan..."
ANALYSIS_STEP_ONE_PROGRESS = "Pass 1/2: Menganalisis frame {}/{}"
ANALYSIS_STEP_TWO = "{} Menggabungkan Data..."
ANALYSIS_STEP_TWO_PROGRESS = "{} Menggabungkan gambar {}/{}"
ANALYZING_COMPLETE = "Analisis Selesai"


# ==============================================================================
# Error Messages
# ==============================================================================
# General Errors
RUN_ERROR_STATUS = "Terjadi kesalahan: {error}"
RUN_ERROR_MESSAGE = "Terjadi kesalahan: {error}"
FAILED_TO_SAVE_IMAGE = "Gagal menyimpan gambar akhir."
FAILED_TO_CREATE_PROCESS_WINDOW = "Gagal membuat window proses: {}"

# Image Loading / Preparation Errors
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Gagal memuat gambar"
RUN_IMAGE_NOT_FOUND = "Gambar tidak ditemukan di database."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Gambar referensi tidak dapat dimuat dari {image_paths[0]}."
RUN_IMAGE_PROCESSING_FAILED = "Gagal memuat gambar {i} dari {image_paths[i]}."
FAILED_WHILE_PREPARING_IMAGE = "Gagal menyiapkan gambar: {}"
FAILED_TO_PREPARE_REFERENCE_IMAGE = "Gagal menyiapkan gambar referensi: {}"
IMAGE_LOAD_FAILED = "Tidak ada gambar yang dimuat."
FIRST_IMAGE_CANNOT_BE_OBTAINED = "Tidak bisa mendapatkan gambar pertama: {}"
RUN_IMAGE_PROCESS_LOAD_FAILED = "Tidak ditemukan gambar di database."

# File / System Errors
ERROR_IN_READING_FILE_HDF5 = "Kesalahan membaca HDF5: {}"
FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "File transformation matrix tidak ditemukan untuk gambar ke-{}"
LIBRARY_FILE_NOT_FOUND = "File library tidak ditemukan: {}"

# Processing / Algorithm Errors
ERROR_ACCUMULATE_IMAGE = "Accumulated image is None atau total weights tidak valid."
RUN_STACK_PROCESSING_FAILED = "Gagal melakukan penumpukan gambar"
FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "Kalkulasi gerakan tidak dapat dihitung untuk gambar ke-{}"
FAIL_COMPENSATE_MOTION_PROCESS = "Estimasi gagal pada gambar ke-{}"
UNRECOGNIZED_TRANSFORMATION = "Jenis transformasi tidak dikenali."
FAILED_TO_COMPUTE_TRANSFORMATION ="Transformasi tidak dapat dihitung."
FAILED_TO_COMPUTE_CROP = "Gagal menghitung crop yang valid. Proses dibatalkan."
FAIL_CROPPING_PROCESS = "Crop tidak valid. Overlap tidak cukup"
ERROR_IN_FLOW_FIELD = "Kesalahan pada gambar {}: Input Field flow adalah none. Tidak dapat mengompensasi gerakan."
ERROR_IN_BASE_IMAGE = "Kesalahan pada gambar {}: Input base_image adalah none. Tidak dapat mengompensasi gerakan."
STACK_IMAGES_FAILED = "Tidak ada gambar untuk diproses."
DATA_FAILED_COMPLETION_CREATED = "Data penyempurnaan gagal di generate. Tidak dapat melakukan penyempurnaan."
FAILED_IMAGE_ENHANCEMENT = "Proses penyempurnaan gagal."
ANALYSIS_FAILURE = "Analisis gagal: Tidak ada gambar yang diproses"
ERROR_AT_END_OF_CONVERSION = "Kesalahan pada akhir konversi: {}"
UNEXPECTED_NUMBER_OF_BUFFER_CHANNELS = "Kesalahan Internal: Jumlah channel buffer tak terduga."
UNABLE_TO_SAVE_WEIGHT_MAP = "Tidak dapat menyimpan Peta Bobot: {}"
FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH = "Gagal menyimpan peta bobot ke {}"
NORMALIZATION_FAILED = "Normalisasi Gagal: {}"
FATAL_ERROR_DURING_NORMALIZATION = "KESALAHAN FATAL Selama normalisasi: {}"
FAILED_TO_ACCUMULATE_IMAGE= "Pada gambar {} gagal diakumulasi"
COLOR_CHANNEL_DOES_NOT_MATCH = "Channel warna tidak cocok."
IMAGE_CHANNEL_DOES_NOT_SUPPORT = "Channel warna yang tidak didukung: {}."
DATA_TYPE_NOT_SUPPORTED = "Tipe data tidak didukung: {}."
IMAGE_BIT_REQUIRED = "Gambar harus berukuran 8 Bit atau 16 Bit."

# Library / Dependency Errors
FAILED_TO_CONFIGURE_LIBRARY = "Gagal memuat/mengkonfigurasi pustaka {}: {}"
LIBRARY_FAILED_TO_LOAD_NORMALIZATION_FAILED = "Library C++ tidak dimuat. Normalisasi dilewati."
LIBRARY_FAILED_TO_LOAD_ACCUMULATED_SKIPED = "Library C++ tidak dimuat. Akumulasi dilewati."

# GPU Errors
GPU_ERROR_AND_FALLBACK_TO_CPU = "Kesalahan GPU yang tak terduga: {}. Proses menggunakan CPU."

# Validation Errors
IMAGE_DATA_MUST_BE_VALID = "Item pada daftar 'gambar' harus berupa data gambar yang valid (array NumPy)."

# ==============================================================================
# Confirmation Dialogs / Warnings
# ==============================================================================
NO_ALIGNMENT_PROCESS = "Anda yakin tidak ingin menyelaraskan gambar terlebih dahulu?"
CANCEL_PROCESSING = "Apakah Anda yakin ingin membatalkan proses?"
# Note: Batch deletion confirmations are kept within the Batch section for context


# ==============================================================================
# Algorithm Specific Window Titles
# ==============================================================================
# Alignment
WINDOW_TITLE_FARNEBACK = "Penyelarasan Farneback Optical Flow"
WINDOW_TITLE_AKAZE = "Penyelarasan AKAZE"
WINDOW_TITLE_ORB = "Penyelarasan ORB"
WINDOW_TITLE_LIGHT_GLUE = "Penyelarasan Light Glue"

# Denoising / Stacking
WINDOW_TITLE_AVERAGE = "Penumpukan Average"
WINDOW_TITLE_MEDIAN = "Penumpukan Median"
WINDOW_TITLE_SIMILARITY = "Penumpukan Similarity"
WINDOW_TITLE_SIMILARITY_V2 = "Penumpukan Similarity V2"

# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Super Resolusi Interpolasi"


# ==============================================================================
# Algorithm Parameter Settings UI (Labels & Descriptions)
# ==============================================================================
DEFAULT_PARAMETER_SETTING_LABEL = """Pilih algoritma untuk melihat parameter."""

# --- ORB Parameters ---
ORB_PARAMETER_SETTING_LABEL = "Parameter ORB"
ORB_NFEATURES_LABEL = "Jumlah Fitur"
ORB_NFEATURES_DESCRIPTION = """Jumlah detail gambar yang dikenali.
- Lebih Tinggi: Penyelarasan lebih presisi, tetapi proses lebih lambat.
- Rekomendasi: 500 hingga 1500 (standar); 2500 hingga 5000 (akurasi sangat tinggi)."""
ORB_SCALEFACTOR_LABEL = "Scale Factor"
ORB_SCALEFACTOR_DESCRIPTION = """Kecepatan pengecilan ukuran gambar secara bertahap saat diproses.
- Mendekati 1.0: Pengecilan perlahan, detail sangat terjaga, tetapi proses lambat.
- Lebih Tinggi: Proses lebih cepat, namun detail kecil mungkin terlewat.
- Rekomendasi: 1.2 hingga 1.5."""
ORB_NLEVELS_LABEL = "Jumlah Level"
ORB_NLEVELS_DESCRIPTION = """Jumlah lapisan ukuran gambar (lapisan piramida) untuk mendeteksi fitur.
- Lebih Tinggi: Deteksi lebih baik pada gambar dengan ukuran bervariasi, tetapi proses lambat.
- Rekomendasi: 2 hingga 4."""
ORB_TRANSFORMATION_LABEL = "Jenis Transformasi"
ORB_TRANSFORMATION_DESCRIPTION = """Pilih metode penyelarasan gambar sesuai kebutuhan:
- HOMOGRAPHY: Terbaik untuk perbedaan sudut pandang ekstrem (tilted/perspektif).
- AFFINE: Mengoreksi rotasi, skala, dan kemiringan gambar.
- SIMILARITY: Membatasi pada rotasi dan pergeseran dengan rasio tetap (presisi).
- EUCLIDEAN: Hanya memutar dan menggeser gambar tanpa mengubah ukuran."""
ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """Tingkat ketatnya penyaringan titik yang tidak sejajar.
- Rendah (1-2): Sangat ketat, presisi tinggi, tetapi rentan gagal jika gambar minim detail.
- Tinggi (4-5): Lebih toleran, memperbesar peluang berhasil tetapi akurasi sedikit berkurang.
- Rekomendasi: 1 hingga 3."""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Parameter Farneback"
FARNEBACK_PYRAMID_SCALE_LABEL = "Skala Piramida"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Faktor skala pengecilan gambar pada setiap level piramida.
- Mendekati 1.0: Perubahan halus, akurasi gerak tinggi, tetapi proses lambat.
- Nilai 0.5: Gambar diperkecil setengahnya di tiap tahap, seimbang antara kecepatan dan akurasi.
- Rekomendasi: 0.5."""
FARNEBACK_LEVELS_LABEL = "Level"
FARNEBACK_LEVELS_DESCRIPTION = """Jumlah lapisan piramida untuk menghitung gerakan objek.
- Lebih Banyak: Mendeteksi gerakan objek besar atau kompleks lebih baik, proses lebih lama.
- Rekomendasi: 3."""
FARNEBACK_WIN_SIZE_LABEL = "Ukuran Jendela"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Ukuran jendela piksel yang digunakan untuk mendeteksi gerakan.
- Lebih Besar: Estimasi gerakan lebih stabil dan halus, detail kecil terlewat.
- Lebih Kecil: Sensitif terhadap gerakan kecil, tetapi noise mudah terbaca sebagai gerakan.
- Rekomendasi: 15."""
FARNEBACK_ITERATIONS_LABEL = "Iterasi"
FARNEBACK_ITERATIONS_DESCRIPTION = """Jumlah pengulangan perhitungan gerakan di setiap level piramida.
- Lebih Banyak: Hasil deteksi gerakan lebih akurat, tetapi proses lebih lambat.
- Rekomendasi: 3."""
FARNEBACK_POLY_N_LABEL = "Ekspansi Polinomial"
FARNEBACK_POLY_N_DESCRIPTION = """Ukuran area piksel untuk memperkirakan model gerakan.
- Lebih Besar: Gerakan lebih halus, tetapi kurang peka pada gerakan yang sangat kecil.
- Rekomendasi: 5 atau 7."""
FARNEBACK_POLY_SIGMA_LABEL = "Sigma Polinomial"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Ketebalan efek perataan untuk menyaring noise pada gambar.
- Lebih Tinggi: Noise tersaring lebih bersih, tetapi detail gerakan penting bisa kabur.
- Rekomendasi: 1.2."""
FARNEBACK_FLAGS_LABEL = "Flag"
FARNEBACK_FLAGS_DESCRIPTION = """Flag adalah parameter opsional yang memungkinkan
mengaktifkan opsi tertentu dalam algoritma Farneback.

- flag sering digunakan dalam penerapan filter Gaussian untuk perataan,
  ini digunakan untuk mendapatkan menghasilkan optical flow yang lebih halus.
  
- Jika Anda ragu, biarkan parameter ini pada nilai default (0).

Pilih flag yang sesuai jika Anda ingin menyeimbangkan antara kecepatan proses dan kualitas hasil.
Nilai yang direkomendasikan: 0.
"""

# --- AKAZE Parameters ---
AKAZE_PARAMETER_SETTING_LABEL = "Parameter AKAZE"
AKAZE_THRESHOLD_LABEL = "Threshold"
AKAZE_THRESHOLD_DESCRIPTION = """Sensitivitas detektor dalam mencari titik kunci fitur gambar.
- Lebih Rendah: Lebih sensitif (cocok untuk gambar minim detail/tinggi noise).
- Lebih Tinggi: Hanya mendeteksi fitur yang sangat menonjol saja.
- Rekomendasi: 0.001."""
AKAZE_OCTAVE_LABEL = "Jumlah Oktav"
AKAZE_OCTAVE_DESCRIPTION = """Jumlah tingkat zoom gambar yang dianalisis.
- Lebih Banyak: Deteksi lebih konsisten di berbagai ukuran, tetapi proses lebih lambat.
- Rekomendasi: 4."""
AKAZE_LAYER_LABEL = "Jumlah Lapisan per Oktav"
AKAZE_LAYER_DESCRIPTION = """Jumlah sub-lapisan di dalam setiap tingkat zoom.
- Lebih Banyak: Deteksi skala gambar lebih halus, komputasi bertambah.
- Rekomendasi: 4."""
AKAZE_RATIO_LABEL = "Rasio Threshold"
AKAZE_RATIO_DESCRIPTION = """Tingkat ketatnya pencocokan fitur antar gambar.
- Rendah (0.5 - 0.7): Pencocokan sangat ketat, menghindari salah sambung.
- Tinggi (0.8 - 0.9): Lebih toleran, hasil cocok lebih banyak namun risiko salah sambung naik.
- Rekomendasi: 0.8."""


# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "Overlap %"
OVERLAP_DESCRIPTION = """Area tumpang tindih antar petak (tile).
- Lebih Tinggi: Mengurangi efek patah/kotak di area bergerak, waktu proses bertambah."""

TILE_SIZE_LABEL = "Ukurat petak (tile)"
TILE_SIZE_DESCRIPTION = """Ukuran blok pemrosesan gambar.
- Lebih Kecil: Mendeteksi detail perbedaan lebih halus, tetapi proses lebih lambat.
- Lebih Besar: Proses lebih cepat, namun detail perbedaan kecil bisa terlewat."""

MOTION_SENSIVITY_LABEL = """Sensitivitas Pergerakan"""
MOTION_SENSIVITY_DESCRIPTION = """Sensitivitas sistem dalam mendeteksi perbedaan gerakan.
- Nilai Rendah: Sangat sensitif (noise bisa dianggap sebagai gerakan).
- Nilai Tinggi: Kurang sensitif (mengabaikan gerakan halus)."""

NOISE_OFFSET_LABEL = """Offset Noise"""
NOISE_OFFSET_DESCRIPTION = """Ambang batas untuk mengabaikan noise gambar.
- Lebih Tinggi: Hasil tumpuk lebih bersih di kondisi ekstrim, tetapi deteksi gerak menurun."""


# --- General Alignment Options (Edges, Crop, Saving) ---
KEEP_EDGES_LABEL = """Pertahankan tepi"""
IGNORE_EDGE_LABEL= """Abaikan Tepi"""
KEEP_EDGES_DESCRIPTION = """Fitur Pertahankan Tepi memungkinkan algoritma menjaga tepi gambar
tetap utuh selama proses penyelarasan."""

ENABLE_CROP_LABEL = """Aktifkan 
Pemotongan"""
DISABLE_CROP_LABEL = """Nonaktifkan 
Pemotongan"""
CROP_DESCRIPTION = """Aktifkan Pemotongan untuk menghilangkan
batas gambar yang tidak terpakai

Note: Terkadang terjadi bug pemotongan (sangat jarang). 
Seperti gambar yang sangat kecil, atau kesalahan dalam memotong gambar """

ACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = "Simpan ke folder"
DEACTIVATE_SAVE_ALIGN_IMAGE_TO_FOLDER = """Tidak menyimpan
ke folder"""
SEARCH_SAVE_ALIGN_IMAGE_TO_FOLDER = "Cari.."
DEFAULT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Folder Bawaan"
SELECT_SAVE_ALIGN_IMAGE_TO_FOLDER = "Pilih folder"
SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """Menyimpan gambar hasil penyelarasan ke dalam folder
Folder default adalah folder dokumen di PC"""

ACTIVATE_SAVE_ALIGN_TO_PROCESS = """Simpan untuk 
proses selanjutnya"""
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = """Tidak menyimpan 
proses selanjutnya"""
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """Menyimpan gambar untuk proses 
denoising ataupun super resolusi"""


# ==============================================================================
# Algorithm General Descriptions (Overview)
# ==============================================================================
# --- Alignment Algorithm Descriptions ---
ALIGNMENT_NAME = "Algoritma Penyelarasan"
NONE_ALIGNMENT_DESCRIPTION = "Tidak akan ada penyelarasan yang diterapkan."
FARNEBACK_DESCRIPTION = """Algoritma ini cocok untuk penyelarasan tingkat tinggi yang memerlukan ketepatan dan akurasi hingga level piksel.
Namun, sangat lemah terhadap perbedaan rotasi dan perspektif yang signifikan."""
AKAZE_DESCRIPTION = """Algoritma ini cukup tangguh terhadap perbedaan besar dalam rotasi, perspektif, dan skala.

Cukup baik, tetapi tidak sebaik Farneback untuk level piksel."""
ORB_DESCRIPTION = """Algoritma cepat namun kurang akurat untuk perbedaan yang signifikan.

Cocok untuk gambar dengan perbedaan minimal, dan akurat pada gambar dengan tekstur acak."""


LIGHT_GLUE_DESCRIPTION = """Model Jaringan saraf (Deep Learning) untuk mencocokan fitur lokal di seluruh gambar.

Light Glue ini lebih kuat dibandingkan algoritma AKAZE, mampu menangani gambar dengan perbedaan perspektif dan kondisi gambar yang sulit sekalipun.
Peringatan: Proses ini hanya mendukung GPU NVIDIA (CUDA) yang cukup kuat, bisa dijalankan pada CPU namun waktu prosesnya lebih lambat"""

# --- Super Resolution Algorithm Descriptions ---
SUPER_RESOLUTION_NAME = "Algoritma Super Resolusi"
NONE_SUPER_RESOLUTION_DESCRIPTION = "Tidak akan ada super resolusi yang diterapkan."
INTERPOLATION_DESCRIPTION = """Algoritma sederhana untuk meningkatkan resolusi dengan metode interpolasi,
menambahkan sedikit detail."""

# --- Denoising Algorithm Descriptions ---
DENOISING_NAME = "Algoritma Pengurangan Noise"
NONE_DENOISING_DESCRIPTION = "Tidak akan ada pengurangan noise yang diterapkan."
WEIGHTED_AVERAGE_DESCRIPTION = """Hasil dari penyederhanaan metode penumpukan similarity
Cukup baik dalam menangani pergerakan kecil, tetapi menghasilkan artefak gambar pada pergerakan yang lebih besar."""
AVERAGE_DESCRIPTION = """Metode penumpukan yang sangat cepat dan efektif untuk objek dan adegan statis
Tidak cocok untuk adegan atau area yang bergerak, tetapi dapat dikombinasikan dengan penyelarasan 
Farneback untuk menghilangkan pergerakan objek yang ringan."""
MEDIAN_DESCRIPTION = """Cepat dan efektif untuk penumpukan, cukup baik pada objek yang bergerak
Sangat efektif dalam menghilangkan pergerakan kecil pada objek, namun artefak muncul pada pergerakan yang lebih besar."""
SIMILARITY_DESCRIPTION = """Algoritma penumpukan canggih, sangat kuat dalam menghilangkan pergerakan objek 
(sangat sedikit ghosting di area yang bergerak) dan menghasilkan sangat sedikit artefak hingga 85%

Terinspirasi oleh:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""

SIMILARITY_MOTION_V2_DESCRIPTION = """Similarity V2 merupakan hasil pengembangan dari algoritma similarity v1 dengan sejumlah 
peningkatan signifikan. Algoritma ini mampu menghasilkan gambar yang lebih bersih meskipun input mengandung noise yang parah, berkat kemampuannya 
secara cerdas membedakan antara noise, tekstur, dan pergerakan halus. Lebih andal dengan pencahayaan minim, namun prosesnya berjalan lebih lambat 
dibandingkan versi v1."""


# ==============================================================================
# Application Settings UI
# ==============================================================================
SETTING_GENERAL_LABEL = "Umum"
LANGUAGE_LABEL = "Bahasa"
LANGUAGE_TYPE = "Inggris", "Indonesia", "China Tradisional", "Melayu"
GPU_ACCELERATION_LABEL = "Akselerasi GPU"
MULTI_CORE_CPU = "Akselerasi Multi-Core CPU"
SETTINGS_SAVED = "Pengaturan berhasil disimpan."

CANT_READ_FILE_SETTINGS = "Peringatan: Tidak dapat membaca berkas pengaturan '{GENERAL_SETTINGS_FILE}'. Menggunakan nilai default."
MULTI_CORE_CPU_DESCRIPTION = """Mengaktifkan pemrosesan paralel pada CPU.
- Aktif: Proses jauh lebih cepat, konsumsi RAM bertambah. Matikan jika RAM terbatas."""

GPU_ACCELERATION_DESCRIPTION = """Menggunakan kartu grafis (GPU) untuk mempercepat proses.
- Catatan: Saat ini hanya didukung oleh algoritma Farneback dan LightGlue."""

THUMBNAIL_LABEL = "Thumbnail"
THUMBNAIL_DESCRIPTION = """Menampilkan pratinjau gambar saat proses batch (Eksperimental).
- Catatan: Dapat menyebabkan sedikit lag saat menambahkan batch baru."""

NOISE_MAD_OFFSET_LABEL = "MAD Noise Factor"
NOISE_MAD_OFFSET_DESCRIPTION = """Toleransi deteksi MAD terhadap gambar dengan noise tinggi.
- Lebih Tinggi: Lebih toleran noise, risiko bayangan gerakan (ghosting) meningkat."""

MAD_SENSITIVITY_LABEL = "MAD Sensitivity"
MAD_SENSITIVITY_DESCRIPTION = """Sensitivitas MAD terhadap perbedaan gambar.
- Lebih Tinggi: Lebih peka pada perbedaan halus, tingkat kesalahan deteksi naik jika noise tinggi."""

CONF_SKIP_DFT_LABEL = """Kepercayaan melewati
Proses DFT"""
CONF_SKIP_DFT_DESCRIPTION = """Ambang batas melewati proses DFT jika MBM sudah cukup baik.
- Lebih Tinggi: Lebih banyak proses dikerjakan oleh MAD (komputasi ringan tapi kasar)."""

WIENER_C_FACTOR_LABEL = "Wiener C Factor"
WIENER_C_FACTOR_DESCRIPTION = """Sensitivitas filter Wiener terhadap gerakan.
- Lebih Rendah: Lebih peka gerakan halus, rentan terhadap noise."""

COARSE_MARGIN_LABEL = "Coarse Align Margin"
COARSE_MARGIN_DESCRIPTION = """Margin pencarian penyelarasan di level petak (tile).
- Lebih Tinggi: Stacking lebih presisi, tetapi memperlambat proses secara signifikan."""

# --- Missing UI Keys ---
LBL_BATCH_MODE = "Mode Batch"
LBL_BULK_MODE = "Mode Bulk"
LBL_PARAMETER_ALIGNMENT = "Pengaturan Penyelarasan Gambar"
LBL_ALIGNMENT_PLACEHOLDER = "Pengaturan penyelarasan gambar akan muncul di sini"
LBL_PARAMETER_ALGORITHM = "Pengaturan Metode Proses"
LBL_ALGORITHM_PLACEHOLDER = "Pengaturan detail akan muncul setelah Anda memilih metode proses di atas"
BTN_START = "Mulai Proses"
BTN_NEW_BATCH = "Buat Batch Baru"
BTN_DELETE_BATCH = "Hapus Batch"
LBL_ALGORITHM_SETTINGS = "Pengaturan Metode Stacking & Penyelarasan"
BTN_PROCESS_ALL_BATCH = "Proses Semua Batch"
LBL_FROM_PROJECT = "Dari Project No:"
LBL_TO_PROJECT = "Ke Project No:"
MSG_INVALID_RANGE = "Nilai nomor awal project tidak boleh lebih besar dari nomor akhir."
BTN_CLOSE = "Tutup"
LBL_STATUS_PROCESSING = "Memproses"
BTN_BACK_TO_GRID = "Kembali ke Grid"
BTN_IMPORT_IMAGES = "Impor Gambar"
MSG_SUCCESS_SAVE_TO = "Gambar berhasil disimpan ke:"
LBL_DRAG_DROP_HERE = "Lepaskan gambar di sini untuk menambahkan"
BTN_YES_DELETE = "Ya, Hapus"
BTN_NO_CANCEL = "Tidak, Batalkan"
LBL_SELECTED_BATCHES_TITLE = "Daftar Lengkap Batch Terpilih"
LBL_CREATE_NEW_BATCH_TITLE = "Buat Batch Baru"
LBL_BATCH_NAME = "Nama Batch"
BTN_CREATE = "Buat"
MSG_CONFIRM_DELETE_BATCH_COUNT = "Apakah Anda yakin ingin menghapus {} batch?"
MSG_NO_BATCHES_AVAILABLE = "Tidak ada daftar batch yang dapat diproses."
MSG_RENAME_FAILED = "Gagal mengubah nama batch. Nama mungkin tidak valid atau sudah digunakan."
TIP_CPU_CORES = "Jumlah mesin pemroses (CPU) yang digunakan secara bersamaan. Pilihan 'Otomatis' adalah yang paling disarankan."
LBL_SMART_NOISE_ALPHA = "Smart Noise Alpha (AI):"
TIP_SMART_NOISE_ALPHA = "Mengatur seberapa toleran kecerdasan buatan (AI) terhadap bintik gangguan (noise).\nNilai rendah = Lebih peka gerakan (kurangi ghosting).\nNilai tinggi = Lebih bersih noise (risiko ghosting)."
LBL_SMART_NOISE_AWARE = "Smart Noise Aware (AI):"
TIP_SMART_NOISE_AWARE = "Aktifkan atau nonaktifkan analisis otomatis terhadap gangguan gambar oleh AI."
LBL_NOISE_CONTRIB = "Noise Contribution Strength (%):"
TIP_NOISE_CONTRIB = "Mengatur kekuatan AI dalam menyaring bintik gangguan (0% = Tidak Aktif, 100% = Pembersihan Penuh)."
LBL_LIGHT_GLUE_TITLE = "Pengaturan Metode LightGlue"
LBL_SELECT_REFERENCE_IMAGE = "Pilih Gambar Referensi"
LBL_DELETE_IMAGES = "Hapus Gambar"
MSG_CONFIRM_DELETE_IMAGE = "Apakah Anda yakin ingin menghapus gambar yang dipilih dari batch ini?"
TIP_RIGHT_CLICK_COPY = "Klik kanan untuk menyalin teks"
MSG_UNSUPPORTED_FORMAT_IGNORED = "Format file tidak didukung atau ekstensi tidak valid."
MSG_NO_VALID_IMAGES_GROUP = "Tidak ada gambar yang valid untuk diimpor."
LBL_LOGGING_LEVEL = "Logging Level:"
BTN_RESET_TO_DEFAULT = "Reset ke Default"
BTN_CLEAR_CACHE = "Bersihkan Cache"
LBL_STATUS_READY = "Siap"
LBL_ITEMS_REMAINING = "proses tersisa"
LBL_SPLASH_LOADING = "M E M U A T . . ."
MSG_EXIFTOOL_NOT_FOUND = "Exiftool tidak ditemukan. Harap pastikan telah terinstal dan terdaftar di PATH sistem Anda."
MSG_NO_BATCHES_YET = "Belum ada batch"
MSG_NO_BATCHES_YET_DESC = "Buat batch baru atau impor gambar untuk memulai."
MSG_NO_BATCH_SELECTED = "Tidak ada batch yang dipilih"
LBL_BATCH_IMAGE_COUNT_FORMAT = "Batch {}   -   ({} gambar)"
DESC_SUPER_RESOLUTION_CARD = "Tingkatkan detail dan perbesar resolusi gambar."
DESC_DENOISING_CARD = "Kurangi noise gambar dan selaraskan lapisan piksel."




# --- New UI & Bulk Core Keys ---
BULK_FROM = "Dari No:"
BULK_TO = "Ke No:"
BULK_MSG_RANGE_ERROR = "Nomor awal harus <= nomor akhir."
BULK_ERR_RETRIEVE = "Gagal memuat gambar proyek."
BULK_WARN_UNSUPPORTED = "Format tidak didukung akan diabaikan."
CORE_SELECT_REF_IMAGE = "Jadikan Acuan"
CORE_DELETE_IMAGES = "Hapus Terpilih"
CORE_MSG_CONFIRM_DELETE = "Hapus gambar terpilih?"
CORE_TOOLTIP_COPY = "Klik kanan untuk salin"

# Tooltip parameter alignment
PARAMETER_DIRECT_EDIT_TOOLTIP = "Nilai bisa diketik langsung, lalu tekan Enter atau pindahkan fokus untuk menerapkannya."
AKAZE_THRESHOLD_TOOLTIP = "Sensitivitas fitur AKAZE. Nilai lebih rendah mendeteksi lebih banyak keypoint, berguna untuk gambar gelap atau minim tekstur, tetapi bisa menambah match noise. Nilai lebih tinggi lebih ketat dan cepat."
AKAZE_OCTAVES_TOOLTIP = "Jumlah level skala yang dianalisis AKAZE. Octave lebih banyak membantu perubahan ukuran antar frame yang besar, tetapi proses lebih lama."
AKAZE_OCTAVE_LAYERS_TOOLTIP = "Sub-level di dalam setiap octave. Nilai lebih tinggi membuat deteksi skala lebih halus, tetapi ekstraksi fitur lebih lambat."
FEATURE_RATIO_THRESHOLD_TOOLTIP = "Ambang Lowe ratio test untuk pencocokan fitur. Nilai lebih rendah hanya menerima match sangat yakin; nilai lebih tinggi menerima lebih banyak match tetapi bisa membawa kesalahan."
FEATURE_MIN_MATCHES_TOOLTIP = "Jumlah match valid minimum sebelum gerakan gambar dihitung. Naikkan untuk alignment lebih aman; turunkan hanya jika gambar sangat minim fitur."
FEATURE_MAX_KEYPOINTS_TOOLTIP = "Jumlah keypoint maksimum yang dipakai untuk estimasi gerakan. Nilai lebih tinggi bisa membantu alignment sulit, tetapi menambah waktu CPU."
FEATURE_RANSAC_THRESHOLD_TOOLTIP = "Batas error reproyeksi untuk RANSAC. Nilai lebih rendah lebih ketat dan membuang outlier; nilai lebih tinggi lebih toleran terhadap noise/gerakan tetapi bisa menerima match salah."
FEATURE_TRANSFORMATION_TOOLTIP = "Model gerakan setelah matching. Homography cocok untuk perubahan perspektif; affine lebih sederhana dan stabil untuk pergeseran kamera kecil."
FEATURE_KEEP_EDGES_TOOLTIP = "Pertahankan piksel tepi setelah warping. Matikan jika ingin membuang area tepi yang kurang pasti."
FEATURE_ENABLE_CROPPING_TOOLTIP = "Potong tepi tidak stabil setelah alignment agar hasil stack memakai area gambar yang sama-sama valid."
PARAMETER_USE_MULTI_CORE_TOOLTIP = "Gunakan beberapa core CPU jika tersedia. Umumnya lebih cepat, tetapi penggunaan CPU meningkat."
ORB_NFEATURES_TOOLTIP = "Jumlah maksimum fitur ORB yang dideteksi. Nilai lebih tinggi memberi kandidat match lebih banyak untuk gambar sulit, tetapi proses lebih berat."
ORB_SCALE_FACTOR_TOOLTIP = "Jarak skala antar level piramida ORB. Nilai lebih kecil lebih detail tetapi lambat; nilai lebih besar lebih cepat tetapi kurang presisi."
ORB_LEVELS_TOOLTIP = "Jumlah level piramida ORB. Level lebih banyak membantu perubahan skala, tetapi menambah runtime."
FARNEBACK_PYR_SCALE_TOOLTIP = "Skala gambar antar level piramida. Nilai lebih rendah memakai downscale lebih kuat untuk gerakan besar; 0.5 umum dipakai."
FARNEBACK_LEVELS_TOOLTIP = "Jumlah level piramida untuk optical flow. Level lebih banyak membantu gerakan besar, tetapi memakai lebih banyak memori dan waktu."
FARNEBACK_WINSIZE_TOOLTIP = "Ukuran jendela piksel untuk estimasi gerakan. Jendela besar lebih halus dan tahan noise; jendela kecil menjaga detail lokal."
FARNEBACK_ITERATIONS_TOOLTIP = "Jumlah refinement di setiap level piramida. Iterasi lebih banyak bisa meningkatkan akurasi flow tetapi memperlambat proses."
FARNEBACK_POLY_N_TOOLTIP = "Ukuran area untuk ekspansi polinomial. 5 lebih tajam; 7 lebih halus dan lebih tahan noise."
FARNEBACK_POLY_SIGMA_TOOLTIP = "Perataan Gaussian untuk ekspansi polinomial. Nilai lebih tinggi meredam noise tetapi bisa melembutkan gerakan kecil."
FARNEBACK_FLAGS_TOOLTIP = "Flag opsional Farneback. 0 adalah standar; 256 memakai Gaussian window agar flow lebih halus pada beberapa kasus."
OPTICAL_FLOW_TILE_COLS_TOOLTIP = "Jumlah tile horizontal untuk pemrosesan flow per blok. Tile lebih banyak mengurangi memori per blok tetapi menambah overhead penggabungan."
OPTICAL_FLOW_TILE_ROWS_TOOLTIP = "Jumlah tile vertikal untuk pemrosesan flow per blok. Tile lebih banyak mengurangi memori per blok tetapi menambah overhead penggabungan."
OPTICAL_FLOW_TILE_OVERLAP_TOOLTIP = "Rasio overlap antar tile. Overlap lebih besar mengurangi seam antar tile, tetapi menambah komputasi berulang."
LIGHT_GLUE_MATCH_CONFIDENCE_TOOLTIP = "Ambang keyakinan match Light Glue. Nilai lebih tinggi hanya menerima pasangan fitur yang lebih yakin; nilai lebih rendah memberi lebih banyak match tetapi lebih berisiko noise."
LIGHT_GLUE_USE_GPU_TOOLTIP = "Jalankan inferensi Light Glue di GPU jika backend tersedia. Cocok untuk model neural, tetapi bisa memakai VRAM tambahan."
LUCAS_KANADE_GRID_STEP_TOOLTIP = "Jarak antar titik grid yang dilacak Lucas-Kanade. Nilai lebih kecil memberi flow lebih rapat tetapi lebih lambat; nilai lebih besar lebih cepat."
LUCAS_KANADE_BORDER_MARGIN_TOOLTIP = "Jarak aman dari tepi tile sebelum titik grid dibuat. Margin membantu mengurangi tracking di area tepi yang kurang stabil."
LUCAS_KANADE_POINT_WORKERS_TOOLTIP = "Jumlah worker untuk membagi tracking titik grid di dalam setiap tile. Naikkan untuk CPU banyak core; turunkan jika CPU terlalu penuh atau terjadi spike."
LUCAS_KANADE_WIN_SIZE_TOOLTIP = "Ukuran jendela pencarian Lucas-Kanade. Jendela besar membantu gerakan lebih jauh; jendela kecil menjaga detail lokal."
LUCAS_KANADE_MAX_LEVEL_TOOLTIP = "Jumlah level piramida optical flow. Level lebih banyak membantu gerakan besar, tetapi menambah waktu proses."
LUCAS_KANADE_ITERATIONS_TOOLTIP = "Jumlah iterasi pencarian pada setiap titik. Iterasi lebih banyak bisa meningkatkan akurasi, tetapi proses lebih lambat."
LUCAS_KANADE_EPSILON_TOOLTIP = "Ambang konvergensi Lucas-Kanade. Nilai kecil lebih teliti, tetapi bisa butuh iterasi lebih banyak."
UI_STATUS_READY = "Siap"
UI_ITEMS_REMAINING = "tersisa"
UI_SPLASH_LOADING = "Memuat..."

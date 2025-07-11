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
APPLY_PARAMETER_BUTTON_TEXT = "Terapkan Pengaturan"

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


# --- Dialogue Title ---
SELECT_OUTPUT_FOLDER_TITLE = "Pilih Folder Output untuk Simpan Batch"
OUTPUT_FOLDER_SELECTION_CANCELLED = "Pemilihan folder dibatalkan. Proses dihentikan."

# --- General Error Messages & Dialogs ---
BATCH_PROCESSING_ERROR_TITLE = "Kesalahan Proses Batch"
BATCH_PROCESSING_ERROR_MESSAGE = "Gagal memproses Batch {} (ID: {}):\n{}" 
BATCH_SAVE_ERROR_TITLE = "Gagal Menyimpan"
TARGET_FOLDER_NOT_ACCESSIBLE = "Folder tujuan tidak dapat diakses:\n{}" 
MOVE_FILE_ERROR_TITLE = "Gagal Memindahkan File"
COULD_NOT_SAVE_FILE_FOR_BATCH = "Gagal menyimpan file '{}' untuk batch:\n{}" 
SOURCE_FILE_DOES_NOT_EXIST = "Gagal pindah: File sumber '{}' tidak ditemukan."
TARGET_FOLDER_INVALID = "Gagal pindah: Folder tujuan '{}' tidak valid."

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
RUN_IMAGE_PROCESSING = "Memproses gambar {i} dari {total_images}..."
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
ORB_NFEATURES_DESCRIPTION = """Jumlah fitur mencari seberapa banyak detail halus yang dapat dikenali dalam sebuah gambar.

- Jumlah fitur yang lebih tinggi memungkinkan algoritma untuk mencari lebih banyak detail,
  menghasilkan penyelarasan gambar yang lebih presisi. Namun, meningkatkan waktu komputasi.

- Biasanya, nilai antara 500 hingga 1500 sudah cukup untuk sebagian besar scene gambar.
  Untuk kebutuhan akurasi yang sangat tinggi, memilih nilai antara 2500 hingga 5000 dapat meningkatkan akurasi."""
ORB_SCALEFACTOR_LABEL = "Scale Factor"
ORB_SCALEFACTOR_DESCRIPTION = """Scale Factor menentukan tingkat penurunan skala gambar secara bertahap selama pemrosesan.

- Jika nilainya mendekati 1.0, gambar diperkecil secara perlahan dengan lebih banyak langkah.
  Hal ini memungkinkan deteksi detail yang lebih halus, tetapi membutuhkan waktu lebih lama.

- Jika nilainya lebih besar, gambar diperkecil lebih cepat, sehingga pemrosesan menjadi lebih singkat,
  tetapi mungkin ada beberapa detail kecil yang terlewat.

Biasanya, nilai Scale Factor berkisar antara 1.2 hingga 1.5."""
ORB_NLEVELS_LABEL = "Jumlah Level"
ORB_NLEVELS_DESCRIPTION = """Jumlah level menunjukkan jumlah lapisan dalam piramida gambar yang digunakan untuk mendeteksi fitur.

- Semakin banyak level, semakin banyak detail yang dapat ditangkap algoritma pada berbagai skala, 
  hal ini berguna jika ukuran gambar bervariasi. 
  
- Namun, semakin tinggi jumlah level, semakin lama waktu pemrosesannya.

Untuk sebagian besar scene, nilai antara 2 hingga 4 sudah cukup ideal."""
ORB_TRANSFORMATION_LABEL = "Jenis Transformasi"
ORB_TRANSFORMATION_DESCRIPTION = """Pilih metode untuk menyelaraskan gambar sesuai kebutuhan Anda:

Opsi yang tersedia meliputi:
- HOMOGRAPHI: Cocok untuk foto dengan perbedaan sudut yang cukup ekstrem (misal: gambar meja dari atas vs. samping).
  Bisa menyesuaikan efek "perspektif".

- Afine: Bisa diputar, mengubah ukuran (bisa tidak seragam), dan menggeser gambar.
  Contoh: memperbaiki foto yang miring dan perlu dibesarkan sebagian.

- Similarity: Hanya bolehkan putar, perbesaran/perkecilan yang seragam, dan geser.
  aspek rasio tetap terjaga.
  
- Euclidean: Paling sederhana: hanya putar dan geser gambar tanpa mengubah ukuran.
  Cocok untuk memperbaiki foto yang sedikit miring.

Saran Pemilihan:
- Untuk kebanyakan kasus (terutama foto dari sudut yang cukup ekstrem), pilih Homografi.
- Jika gambar hanya perlu disesuaikan posisi/rotasi sederhana, Euclidean atau Similarity lebih cocok.
- Gunakan Afine hanya jika perlu penyesuaian bentuk fleksibel tanpa efek perspektif."""
ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """RANSAC Threshold menentukan seberapa ketat algoritma menyaring nilai outlier
(data yang menyimpang jauh) saat menyelaraskan gambar.

- Nilai lebih rendah (misalnya, 1-2) berarti penyaringan lebih ketat, sehingga beberapa fitur penting mungkin terabaikan.

- Nilai lebih tinggi (misalnya, 4-5) lebih toleran terhadap outlier, memungkinkan lebih banyak fitur digunakan,
  tetapi bisa mengurangi akurasi penyelarasan.

Biasanya, nilai antara 1 hingga 3 sudah cukup, tergantung pada tingkat noise dalam data."""

# --- Farneback Optical Flow Parameters ---
FARNEBACK_PARAMETER_SETTING_LABEL = "Parameter Farneback"
FARNEBACK_PYRAMID_SCALE_LABEL = "Skala Piramida"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Skala Piramida adalah faktor yang menentukan seberapa banyak gambar
yang diperkecil pada setiap level piramida.

- Nilai ini menentukan seberapa besar mengurangi ukuran gambar (downscale) dari satu level ke level berikutnya.
  Misalnya, jika nilainya 0.5, maka setiap level akan memiliki ukuran setengah dari level sebelumnya.

- Nilai yang lebih kecil (sekitar 0.10 hingga 0.5) menyebabkan perbedaan ukuran antar level lebih besar.
  Ini dapat mempercepat komputasi, tetapi mungkin mengurangi akurasi dalam menangkap gerakan halus.

- Nilai yang mendekati 1.00 menghasilkan perubahan ukuran yang lebih kecil antar level,
  memungkinkan deteksi gerakan yang lebih akurat, dengan waktu komputasi yang lebih lama.

Sesuaikan nilai ini sesuai kebutuhan Anda untuk menemukan keseimbangan antara kecepatan pemrosesan dan
akurasi deteksi gerak.
Nilai yang direkomendasikan: 0.5
"""
FARNEBACK_LEVELS_LABEL = "Level"
FARNEBACK_LEVELS_DESCRIPTION = """Parameter Level dalam algoritma Farneback merujuk pada jumlah lapisan
  (layers) dalam piramida gambar yang digunakan untuk menghitung optical flow.

- Lebih banyak level: Algoritma dapat mendeteksi gerakan objek pada berbagai ukuran dan kecepatan,
  termasuk gerakan yang kompleks atau mencakup area yang luas. Namun, ini memerlukan
  waktu komputasi yang lebih lama.
  
- Namun, semakin banyak level yang digunakan, semakin lama waktu komputasi yang dibutuhkan.

Anda dapat menyesuaikannya antara 1 hingga 10 sesuai dengan kebutuhan aplikasi Anda.
Secara umum, nilai 3 dianggap sebagai standar,
"""
FARNEBACK_WIN_SIZE_LABEL = "Ukuran Jendela"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Ukuran Jendela menentukan seberapa banyak area piksel (jendela)
yang digunakan dalam perhitungan optical flow.

- Ukuran jendela yang lebih besar: Menghasilkan estimasi pergerakan yang lebih stabil dan halus karena
  informasi dihitung dari area yang lebih luas. Namun, detail pergerakan kecil mungkin terlewatkan.
  
- Ukuran jendela yang lebih kecil: Lebih sensitif terhadap pergerakan kecil, 
  namun noise bisa dianggap sebagai gerakan dan kurang stabil.

Anda bisa memilih nilai antara sensitif terhadap detail gerakan kecil
dan hasil yang stabil.
Nilai yang direkomendasikan: 15.
"""
FARNEBACK_ITERATIONS_LABEL = "Iterasi"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterasi menentukan berapa kali perhitungan optical flow diperbaiki pada setiap level piramida

- Semakin banyak iterasi, semakin akurat hasil optical flow yang diperoleh.
- Namun, peningkatan jumlah iterasi juga dapat memperlambat waktu komputasi.

Pilih nilai yang dapat meningkatkan akurasi tanpa terlalu memperlambat proses.
Nilai yang direkomendasikan: 3.
"""
FARNEBACK_POLY_N_LABEL = "Ekspansi Polinomial"
FARNEBACK_POLY_N_DESCRIPTION = """Ekspansi Polinomial (poly_n) menentukan ukuran area piksel yang digunakan,
untuk memperkirakan gerakan dengan metode ekspansi polinomial.

- Nilai ini menentukan seberapa banyak data piksel di sekitar yang digunakan dalam perhitungan.

- Nilai yang lebih besar akan menghasilkan estimasi gerakan yang lebih halus,
  tetapi dapat mengurangi sensitivitas terhadap gerakan kecil.

Biasanya, nilai yang digunakan adalah 5 atau 7, tergantung pada tingkat detail dan kestabilan yang diinginkan.
"""
FARNEBACK_POLY_SIGMA_LABEL = "Sigma Polinomial"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Sigma Polinomial mengontrol seberapa besar perataan
yang diterapkan sebelum ekspansi polinomial dilakukan.

- Nilai ini merupakan deviasi standar dari filter Gaussian yang digunakan untuk mengurangi noise pada data piksel.
- Sigma yang lebih tinggi dapat membantu meredam noise,

  tetapi jika terlalu tinggi bisa menghilangkan detail gerakan yang penting.

Atur dengan cermat untuk mengurangi noise tanpa kehilangan detail gerakan yang signifikan.
Nilai yang direkomendasikan: 1.2.
"""
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
AKAZE_THRESHOLD_DESCRIPTION = """Parameter Threshold menentukan seberapa sensitifnya detektor
untuk mencari sebuah titik kunci (keypoint).

- Nilai yang lebih rendah meningkatkan deteksi titik kunci yang lebih banyak,
  termasuk gambar yang memiliki fitur yang sedikit dan banyak noise.

- Nilai yang lebih tinggi hanya membatasi deteksi hanya pada fitur yang paling kuat.

Nilai yang direkomendasikan: 0.0010.
"""
AKAZE_OCTAVE_LABEL = "Jumlah Oktav"
AKAZE_OCTAVE_DESCRIPTION = """ parameter yang mengatur berapa banyak tingkat skala yang akan dianalisis
saat mencari fitur-fitur penting dalam sebuah gambar. Bayangkan Anda melihat gambar dengan berbagai tingkat zoom;
setiap tingkat zoom ini disebut "oktav"

- Setiap oktav: Mewakili tingkat zoom yang berbeda, memungkinkan algoritma mendeteksi fitur pada berbagai ukuran.
  Misalnya, fitur kecil akan terlihat pada saat diperbesar, sedangkan fitur besar dapat dikenali pada Zoom
  yang lebih jauh.

- Lebih banyak oktav: Memberikan kemampuan untuk mendeteksi fitur pada lebih banyak skala atau ukuran.
  Namun, komputer perlu bekerja lebih keras dan waktu pemrosesan menjadi lebih lama.

Nilai yang direkomendasikan: 4.
"""
AKAZE_LAYER_LABEL = "Jumlah Lapisan per Oktav"
AKAZE_LAYER_DESCRIPTION = """Lapisan per Oktav menentukan jumlah sub-level dalam setiap oktav.

- Lebih banyak lapisan memberikan resolusi ruang skala yang lebih halus,
  sehingga dapat meningkatkan deteksi fitur di berbagai skala.

- Namun, menambahkan lapisan juga meningkatkan beban komputasi.

Nilai yang direkomendasikan: 4.
"""
AKAZE_RATIO_LABEL = "Rasio Threshold"
AKAZE_RATIO_DESCRIPTION = """Rasio Threshold merupakan nilai yang digunakan saat mencocokkan fitur-fitur penting (keypoint)
antara dua gambar. Tujuannya untuk memastikan bahwa kecocokan yang ditemukan benar-benar akurat dan bukan sebuah kebetulan.

- Rasio lebih rendah (mendekati 0,50): Hanya menerima kecocokan yang sangat jelas yang tidak diragukan lagi.
  Dengan kata lain, lebih selektif dalam memilih kecocokan, sehingga kemungkinan mendapatkan kesalahan dalam mencocokan
  keypoint palsu lebih kecil.

- Rasio lebih tinggi (mendekati 1,00): Berarti kita lebih toleran dalam menerima kecocokan,
  sehingga lebih banyak kecocokan yang diterima. Namun, ini juga meningkatkan kemungkinan kesalahan
  dalam mencocokan keypoint.

Nilai yang direkomendasikan: 0.80.
"""


# DENOISING
# --- Denoising Parameters ---
OVERLAP_LABEL = "Overlap %"
OVERLAP_DESCRIPTION = """Berfungsi untuk mengurangi artefak tile (yang menyebabkan efek kotak-kotak pada area yang bergerak). 

Meningkatkan overlap dapat mengurangi efek tersebut, namun akan meningkatkan waktu komputasi """

TILE_SIZE_LABEL = "Ukurat petak (tile)"
TILE_SIZE_DESCRIPTION = """Semakin kecil ukuran tile, semakin detail dalam mendeteksi perbedaan. 

Namun ini juga akan meningkatkan waktu komputasi dan meningkatkan kemungkinan kesalahan dalam deteksi perbedaan"""

MOTION_SENSIVITY_LABEL = """Sensitivitas Pergerakan"""
MOTION_SENSIVITY_DESCRIPTION = """Sensivitas pergerakan mengatur seberapa agresifnya algoritma dalam mendeteksi perbedaan dalam sebuah petak. 

Semakin rendah nilainya, semakin agresif atau sensitif dalam mendeteksi perbedaan,
namun hal ini menyebabkan noise akan ikut dianggap sebagai perbedaan"""

NOISE_OFFSET_LABEL = """Offset Noise"""
NOISE_OFFSET_DESCRIPTION = """Ambang batas dalam mengabaikan tingkat noise pada gambar, sehingga noise yang lebih tinggi tidak dianggap sebagai pergerakan.

Semakin tinggi nilainya, hasil stacking bisa lebih bersih untuk gambar dengan noise ekstrim, namun ini juga dapat mengurangi deteksi pergerakan pada gambar."""


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
MULTI_CORE_CPU_DESCRIPTION = """Mengaktifkan akan meningkatkan kecepatan komputasi dalam memproses gambar, namun akan menambah sedikit penggunaan RAM 

Jika Komputer memiliki RAM yang sangat terbatas, disarankan untuk tidak mencentangnya"""

GPU_ACCELERATION_DESCRIPTION = """Mengaktifkan akan sangat meningkatkan kecepatan komputasi, karena menggunakan GPU dalam prosesnya. 

CATATAN: Penggunaan GPU hanya terbatas pada proses Farneback saja, algoritma lain akan menyusul implementasinya"""

THUMBNAIL_LABEL = "Thumbnail"
THUMBNAIL_DESCRIPTION = """Preview gambar untuk proses batch, masih bersifat EKSPERIMENTAL
Terkadang menimbulkan seperti flicker atau lag saat menambahkan batch baru"""

NOISE_MAD_OFFSET_LABEL = "MAD Noise Factor"
NOISE_MAD_OFFSET_DESCRIPTION = """Seberapa sensitifnya deteksi MAD dalam menangani gambar dengan noise tinggi

Nilai yang lebih tinggi menyebabkan toleransi terhadap noise (tidak terlalu sensitif di area dengan noise yang tinggi),
namun akan menyebabkan ghosting pada area tersebut jika terjadi gerakan."""

MAD_SENSITIVITY_LABEL = "MAD Sensitivity"
MAD_SENSITIVITY_DESCRIPTION = """Seberapa sensitifnya MAD dalam menangani perbedaan pada sebuah gambar

Nilai yang lebih tinggi akan lebih sensitif terhadap perbedaan halus, namun meningkatkan kesalahan deteksi 
jika gambar input memiliki noise yang tinggi"""

CONF_SKIP_DFT_LABEL = """Kepercayaan melewati
Proses DFT"""
CONF_SKIP_DFT_DESCRIPTION = """Threshold untuk melewati DFT jika proses MBM sudah menangani dengan baik

Semakin tinggi nilainya, maka semakin banyak prosesnya akan dilakukan oleh MAD. Namun MAD adalah deteksi kasar
ia sensitif terhadap noise dan area kontras rendah, namun keuntungan dengan banyaknya proses MAD adalah komputasi 
yang lebih ringan"""

WIENER_C_FACTOR_LABEL = "Wiener C Factor"
WIENER_C_FACTOR_DESCRIPTION = """Seberapa sensitifnya perhitungan DCT Wiener dalam mendeteksi perbedaan dalam sebuah gambar

Semakin rendah nilainya, maka semakin sensitifnya dalam mendeteksi pergerakan halus, namun hal ini berdampak dengan peningkatan noise
karena noise sendiri menyebabkan pergerakan palsu. Nilai Wiener C Factor bekerja sama dengan MAD Sensitivity"""

COARSE_MARGIN_LABEL = "Coarse Align Margin"
COARSE_MARGIN_DESCRIPTION = """Jendela Margin untuk penyelarasan di level tile

Efeknya untuk meningkatkan akurasi hingga level tile, meningkatkan akurasi stacking.
Akan cukup berdampak pada performa jika area pencarian terlalu luas."""
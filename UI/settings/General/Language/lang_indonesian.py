# Main Content
UNDER_DEVELOPMENT = "Menu {page_name} sedang dalam pengembangan"

# Sidebar
SETTINGS_SIDEBAR_LABEL= "Pengaturan"
HDR_SIDEBAR_LABEL= "Rekontruksi HDR"


# Main Content
TOPBAR_IMPORT_BUTTON_TEXT = "Impor Gambar"
TOPBAR_DELETE_BUTTON_TEXT = "Hapus Gambar"

PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Mulai Proses"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Simpan Sebagai"

HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "File Gambar (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Pilih Gambar"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Gambar Duplikat"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} gambar sudah ada di database, akan dilewati."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Format Terpilih"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} gambar dengan format '{format}' akan diimpor."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Error", "Tidak ada gambar yang valid untuk diimpor."

HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Error", "Tidak ada gambar yang dipilih."
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Apakah Anda yakin ingin menghapus {count} gambar yang dipilih?"

PREVIEW_PANEL_LABEL = "Panel Pratinjau"

UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Memproses gambar, harap tunggu..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "Tidak ada gambar yang dipilih."

UPDATE_PROGRESS_BAR_STATUS = "{value}% ({images_left} proses tersisa)"

ON_IMPORT_COMPLETE_STATUS = "Impor selesai"
ON_IMPORT_COMPLETE_MESSAGES = "{successful_images} gambar telah berhasil diimpor."

PROCESS_ALGORITHM_PROCESS_SKIPPED = "Tidak ada algoritma yang dipilih untuk pemrosesan"


# PARAMETER STACKING 
NOT_IMAGE_PREVIEW = "Tidak ada gambar tersedia"
MODULE_NOT_IMPLEMENT = "Modul belum diimplementasikan."
NO_ALIGNMENT_PROCESS = "Anda yakin tidak ingin menyelaraskan gambar terlebih dahulu?"

# General message
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Gagal memuat gambar"

SAVE_TO_HDF5_ALIGNED_SAVING = "Menyimpan gambar yang telah diselaraskan"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Gambar ke-{index} telah disimpan."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "Semua gambar berhasil disimpan."

RUN_IMAGE_NOT_FOUND = "Gambar tidak ditemukan di database."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Gambar referensi tidak dapat dimuat dari {image_paths[0]}."
RUN_SAVING_REFERENCE_IMAGE = "Menyimpan gambar referensi."
RUN_IMAGE_PROCESSING = "Memproses gambar {i} dari {total_images}..."
RUN_IMAGE_PROCESSING_FAILED = "Gagal memuat gambar {i} dari {image_paths[i]}."
RUN_IMAGE_PROCESSING_SAVING = "Gambar ke-{i} telah disimpan."
RUN_IMAGE_PROCESSING_FINISHED = "Proses selesai."

FAIL_CALCULATE_GLOBAL_MOTION_PROCESS = "Kalkulasi gerakan tidak dapat dihitung untuk gambar ke-{}"
FAIL_COMPENSATE_MOTION_PROCESS = "Estimasi gagal pada gambar ke-{}"

UNRECOGNIZED_TRANSFORMATION = "Jenis transformasi tidak dikenali."
FAILED_TO_COMPUTE_TRANSFORMATION ="Transformasi tidak dapat dihitung."
FAILED_TO_COMPUTE_CROP = "Gagal menghitung crop yang valid. Proses dibatalkan."

FAIL_LOAD_TRANSFORMATION_MATRIX_FILE = "File transformation matrix tidak ditemukan untuk gambar ke-{}"
PROGRESS_CALCULATE_AND_COMPENSATE_MOTION_PROCESS ="Menyelaraskan dan crop gambar {}/{}"
PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION ="Menyimpan gambar {}/{}"

FAIL_CROPPING_PROCESS ="Crop tidak valid. Overlap tidak cukup"

CANCEL_PROCESSING = "Apakah Anda yakin ingin membatalkan proses?"

RUN_ERROR_STATUS = "Terjadi kesalahan: {error}"
RUN_ERROR_MESSAGE = "Terjadi kesalahan: {error}"

WINDOW_START_PROCESSING = "Memulai proses..."
WINDOW_PROCESSING_COMPLETE = "Selesai!"


# Farneback Optical Flow
WINDOW_TITLE_FARNEBACK = "Penyelarasan Optical Flow Farneback"

COMPENSATE_MOTION_STATUS = "Melakukan kompensasi gerakan pada gambar {image_id}..."
COMPENSATE_MOTION_FINISHED = "Kompensasi gerakan selesai untuk gambar {image_id}."

# AKAZE, ORB
WINDOW_TITLE_AKAZE = "Penyelarasan AKAZE"
WINDOW_TITLE_ORB = "Penyelarasan ORB"


# Algorithm Denoising
STACK_IMAGES_FAILED = "Tidak ada gambar untuk diproses."
STACK_IMAGES_PROCESS = "Memproses gambar {current}/{total}..."

RUN_IMAGE_PROCESS_STARTED = "Memulai proses..."
RUN_IMAGE_PROCESS_LOAD_FAILED = "Tidak ditemukan gambar di database."
RUN_IMAGE_PROCESS_STACK_SUCCESS = "Penumpukan gambar selesai! Hasil disimpan di: {output_path}"

# Average, Median, Similarity Stacking
WINDOW_TITLE_AVERAGE = "Penumpukan Average"
WINDOW_TITLE_MEDIAN = "Penumpukan Median"
WINDOW_TITLE_WEIGHTED_AVERAGE = "Penumpukan Weighted Average"

WINDOW_TITLE_SIMILARITY = "Penumpukan Similarity"
SIMILARITY_MNFR_LOAD_FAILED = "Tidak ada gambar yang disediakan."
SIMILARITY_MNFR_BIT_REQUIRED = "Gambar harus berukuran 8 Bit atau 16 Bit."
SIMILARITY_MNFR_PROCESS_FINISHED = "Penumpukan selesai."
SIMILARITY_MNFR_PROCESS = "Memproses gambar {} dari {}"
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Menumpuk batch ke {current} dari {total}"


# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Super Resolusi Interpolasi"

# ------------ Parameter Setting Algorithm --------------------- #
DEFAULT_PARAMETER_SETTING_LABEL = """Pilih algoritma untuk melihat parameter."""

# ORB Parameters
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

# Farneback Optical Flow
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

# AKAZE Parameters
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

ACTIVATE_SAVE_ALIGN_TO_PROCESS = """Simpan untuk 
proses selanjutnya"""
DEACTIVATE_SAVE_ALIGN_TO_PROCESS = """Tidak menyimpan 
proses selanjutnya"""
SAVE_ALIGN_TO_PROCESS_DESCRIPTION = """Menyimpan gambar untuk proses 
denoising ataupun super resolusi"""


SAVE_ALIGN_IMAGE_TO_FOLDER_DESCRIPTION = """Menyimpan gambar hasil penyelarasan ke dalam folder
Folder default adalah folder dokumen di PC"""

APPLY_PARAMETER_BUTTON_TEXT = "Terapkan Pengaturan"

RESTART_APPLICATION_REQUIRED = "Restart Diperlukan"
RESTART_APPLICATION_DESCRIPTION = "Mulai ulang untuk melihat perubahan"
ACCEPT_RESTART_APPLICATION = "Mulai Ulang"
REJECT_APPLICATION_DESCRIPTION = "Nanti saja"
COMMAND_APPLICATION_DESCRIPTION = "Muat Ulang Aplikasi..."

# ------------ Parameter Setting Algorithm --------------------- #


# Deskripsi untuk Alignment Algorithm
ALIGNMENT_NAME = "Algoritma Penyelarasan"
NONE_ALIGNMENT_DESCRIPTION = "Tidak akan ada penyelarasan yang diterapkan."
FARNEBACK_DESCRIPTION = """Algoritma ini cocok untuk penyelarasan tingkat tinggi yang memerlukan ketepatan dan akurasi hingga level piksel.
Namun, sangat lemah terhadap perbedaan rotasi dan perspektif yang signifikan."""

AKAZE_DESCRIPTION = """Algoritma ini cukup tangguh terhadap perbedaan besar dalam rotasi, perspektif, dan skala.

Cukup baik, tetapi tidak sebaik Farneback untuk level piksel."""
ORB_DESCRIPTION = """Algoritma cepat namun kurang akurat untuk perbedaan yang signifikan.

Cocok untuk gambar dengan perbedaan minimal, dan akurat pada gambar dengan tekstur acak."""

# Deskripsi untuk Super Resolution
SUPER_RESOLUTION_NAME = "Algoritma Super Resolusi"
NONE_SUPER_RESOLUTION_DESCRIPTION = "Tidak akan ada super resolusi yang diterapkan."
INTERPOLATION_DESCRIPTION = """Algoritma sederhana untuk meningkatkan resolusi dengan metode interpolasi,
menambahkan sedikit detail."""

# Deskripsi untuk Denoising
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
(tanpa ghosting di area yang bergerak) dan menghasilkan sangat sedikit artefak hingga 85%

Terinspirasi oleh:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336""" 
                        
                        
# ------------------ General Settings ------------------ #
SETTING_GENERAL_LABEL = "Umum"
LANGUAGE_LABEL = "Bahasa"
LANGUAGE_TYPE = "Inggris", "Indonesia", "China Tradisional", "Melayu"

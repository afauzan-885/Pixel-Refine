# Main Content
UNDER_DEVELOPMENT = "Menu {page_name} sedang dalam pengembangan"

# Enhance Stack Page
TOPBAR_IMPORT_BUTTON_TEXT = "Impor Gambar"
TOPBAR_DELETE_BUTTON_TEXT = "Hapus Gambar"

PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Mulai Proses"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Simpan Sebagai"

HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "Berkas Gambar (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Pilih Gambar"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Berkas Duplikat"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} berkas sudah ada di basis data dan akan dilewati."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Format Terpilih"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} berkas dengan format '{format}' akan diimpor."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Error", "Tidak ada berkas yang valid untuk diimpor."

HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Error", "Tidak ada gambar yang dipilih."
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Apakah Anda yakin ingin menghapus {count} gambar yang dipilih?"

UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Memproses gambar, harap tunggu..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "Tidak ada gambar yang dipilih."

UPDATE_PROGRESS_BAR_STATUS = "{value}% ({images_left} proses tersisa)"

ON_IMPORT_COMPLETE_STATUS = "Impor selesai"
ON_IMPORT_COMPLETE_MESSAGES = "{successful_images} gambar telah berhasil diimpor."

PROCESS_ALGORITHM_PROCESS_SKIPPED = "Tidak ada algoritma yang dipilih untuk pemrosesan"

# PARAMETER STACKING 
RUN_PROCESS_STOPPED = "Proses dihentikan"
NOT_IMAGE_PREVIEW = "Tidak ada gambar tersedia"
MODULE_NOT_IMPLEMENT = "Modul belum diimplementasikan."
NO_ALIGNMENT_PROCESS = "Apakah Anda yakin tidak ingin menyelaraskan gambar terlebih dahulu?"

# General message
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Gagal memuat gambar"

SAVE_TO_HDF5_ALIGNED_SAVING = "Menyimpan gambar yang telah diselaraskan ke HDF5"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Gambar ke-{index} telah disimpan di HDF5."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "Semua gambar telah berhasil disimpan di HDF5."
RESIZING_IMAGES_PROCESS = "Menyesuaikan ukuran gambar"

RUN_IMAGE_NOT_FOUND = "Tidak ditemukan gambar di basis data."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Gambar referensi tidak dapat dimuat dari {image_paths[0]}."
RUN_SAVING_REFERENCE_IMAGE = "Menyimpan gambar referensi ke HDF5."
RUN_IMAGE_PROCESSING = "Memproses gambar {i} dari {total_images}..."
RUN_IMAGE_PROCESSING_FAILED = "Gagal memuat gambar {i} dari {image_paths[i]}."
RUN_IMAGE_PROCESSING_SAVING = "Gambar ke-{i} telah disimpan di HDF5."
RUN_IMAGE_PROCESSING_FINISHED = "Proses selesai."

CANCEL_PROCESSING = "Apakah Anda yakin ingin membatalkan proses?"

RUN_ERROR_STATUS = "Terjadi kesalahan: {error}"
RUN_ERROR_MESSAGE = "Terjadi kesalahan: {error}"

DELETE_DEBUG_IMAGES_STATUS = "Menghapus gambar debug..."
DELETE_DEBUG_IMAGES_ONE_BY_ONE = "Menghapus gambar debug {image_id}..."
DELETE_DEBUG_IMAGES_FINISHED = "Gambar debug telah berhasil dihapus."

WINDOW_INITIATION = "Memulai..."
WINDOW_START_PROCESSING = "Memulai pemrosesan..."
WINDOW_PROCESSING_COMPLETE = "Selesai!"


# Farneback Optical Flow
WINDOW_TITLE_FARNEBACK = "Penyelarasan Optical Flow Farneback"

CALCULATE_OPTICAL_FLOW_STATUS = "Menghitung optical flow menggunakan {device}..."
CALCULATE_OPTICAL_FLOW_FINISHED = "Perhitungan optical flow selesai."

COMPENSATE_MOTION_STATUS = "Melakukan kompensasi gerak pada gambar {image_id}..."
COMPENSATE_MOTION_FINISHED = "Kompensasi gerak selesai untuk gambar {image_id}."


# AKAZE, ORB
WINDOW_TITLE_AKAZE = "Penyelarasan AKAZE"
ALIGN_IMAGES_STATUS_AKAZE = "Menyelaraskan gambar {image_id} menggunakan AKAZE..."

WINDOW_TITLE_ORB = "Penyelarasan ORB"
ALIGN_IMAGES_STATUS_ORB = "Menyelaraskan gambar {image_id} menggunakan ORB..."

ALIGN_IMAGES_CALCULATE_FAILED = "Tidak ada fitur yang terdeteksi pada gambar {image_id}. Mengembalikan gambar asli."
ALIGN_IMAGES_CALCULATE_FINISHED = "Penyelarasan selesai untuk gambar {image_id}."
ALIGN_IMAGES_COMPENSATE_FAILED = "Homografi tidak dapat dihitung untuk gambar {image_id}. Mengembalikan gambar asli."
ALIGN_IMAGES_MATCHING_FAILED = "Jumlah kecocokan tidak mencukupi untuk gambar {image_id}. Mengembalikan gambar asli."


# Algorithm Denoising
STACK_IMAGES_FAILED = "Tidak ada gambar untuk diproses."
STACK_AVERAGE_IMAGES_PROCESS = "Memproses gambar {current}/{total}..."

RUN_IMAGE_PROCESS_STARTED = "Memulai proses..."
RUN_IMAGE_PROCESS_LOAD_HDF5 = "Memuat gambar dari HDF5..."
RUN_IMAGE_PROCESS_LOAD_PROGRESS = "Memuat gambar {current}/{total}..."

RUN_IMAGE_PROCESS_LOAD_PATH = "Mengambil daftar gambar dari basis data..."
RUN_IMAGE_PROCESS_LOAD_FAILED = "Tidak ditemukan gambar di basis data."
RUN_IMAGE_PROCESS_STACK_SUCCESS = "Penumpukan gambar selesai! Hasil disimpan di: {output_path}"

WINDOW_PROCESS_SUCCESS = "Proses telah selesai."

# Average, Median, Similarity Stacking
WINDOW_TITLE_AVERAGE = "Penumpukan Rata-Rata"
WINDOW_TITLE_MEDIAN = "Penumpukan Median"
WINDOW_TITLE_WEIGHTED_AVERAGE = "Penumpukan Rata-Rata Tertimbang"

WINDOW_TITLE_SIMILARITY = "Penumpukan Similarity"
SIMILARITY_MNFR_LOAD_FAILED = "Tidak ada gambar yang disediakan."
SIMILARITY_MNFR_BIT_REQUIRED = "Gambar harus berukuran 8 Bit atau 16 Bit."
SIMILARITY_MNFR_TILE_SLICE = "Dimensi gambar: {height}x{width}, Ukuran ubin: {tile_size}"
SIMILARITY_MNFR_SIZE_FAILED = "Ukuran gambar {i} tidak sesuai dengan gambar referensi."
SIMILARITY_MNFR_PROCESS_SUCCESS = "Gambar {i}/{count} berhasil diproses."
SIMILARITY_MNFR_PROCESS_FINISHED = "Penumpukan selesai."
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Penumpukan batch ke {current} dari {total}"


# Super Resolution
WINDOW_TITLE_INTERPOLATION = "Super Resolusi Interpolasi"

# ------------ Parameter Setting Algorithm --------------------- #
DEFAULT_PARAMETER_SETTING_LABEL = """Pilih algoritma untuk melihat 
pengaturan parameter."""

# ORB Parameters
ORB_PARAMETER_SETTING_LABEL = "Parameter ORB"
ORB_NFEATURES_LABEL = "Jumlah Fitur"
ORB_NFEATURES_DESCRIPTION = """Jumlah fitur menggambarkan seberapa banyak detail halus yang dapat dikenali dalam sebuah gambar.

Jumlah fitur yang lebih tinggi memungkinkan algoritma untuk mengenali lebih banyak detail, menghasilkan penyelarasan gambar yang lebih tepat.
Namun, mendeteksi lebih banyak fitur meningkatkan waktu komputasi.

Biasanya, nilai antara 500 hingga 1500 sudah cukup untuk sebagian besar aplikasi.
Untuk kebutuhan akurasi yang sangat tinggi, memilih nilai antara 2500 hingga 5000 dapat meningkatkan ketepatan."""

ORB_SCALEFACTOR_LABEL = "Faktor Skala"
ORB_SCALEFACTOR_DESCRIPTION = """Faktor skala menentukan laju penurunan skala gambar secara iteratif selama pemrosesan.

- Nilai yang mendekati 1.0 berarti gambar diturunkan skalanya secara bertahap (lebih banyak langkah), memungkinkan deteksi detail halus yang lebih baik namun memerlukan waktu lebih lama.
- Nilai yang lebih tinggi mengurangi skala gambar dengan lebih cepat, menghasilkan pemrosesan yang lebih cepat namun mungkin melewatkan beberapa detail halus.

Nilai umum berkisar antara 1.2 hingga 1.5."""

ORB_NLEVELS_LABEL = "Jumlah Level"
ORB_NLEVELS_DESCRIPTION = """Jumlah level menunjukkan lapisan dalam piramida gambar yang digunakan untuk deteksi fitur.

Lebih banyak level memungkinkan algoritma untuk menangkap detail pada berbagai skala
Berguna ketika ukuran gambar bervariasi, tetapi peningkatan level juga berarti waktu pemrosesan yang lebih lama.

Biasanya, nilai antara 2 hingga 4 sudah ideal untuk sebagian besar aplikasi."""

ORB_TRANSFORMATION_LABEL = "Tipe Transformasi"
ORB_TRANSFORMATION_DESCRIPTION = """Tipe transformasi menentukan metode yang digunakan untuk menyelaraskan gambar.

Opsi yang tersedia meliputi:
- Homografi: Memungkinkan transformasi perspektif, ideal untuk gambar yang diambil dari sudut yang berbeda.
- Afine: Memungkinkan rotasi, penskalaan, dan translasi (pergeseran).
- Similarity: Hanya memungkinkan rotasi, penskalaan seragam, dan translasi, dengan mempertahankan rasio aspek gambar.
- Euclidean: Hanya memungkinkan rotasi dan translasi tanpa penskalaan, menawarkan opsi yang paling sederhana.

Pilihan transformasi bergantung pada perbedaan antara gambar yang akan diselaraskan.
Untuk sebagian besar aplikasi, Homografi sering dipilih karena fleksibilitasnya dalam menangani perbedaan perspektif."""

ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """RANSAC Threshold menentukan seberapa ketat algoritma menyaring nilai-nilai pencilan selama penyelarasan gambar.

- Nilai yang lebih rendah (misalnya, 1-2) menerapkan penyaringan yang lebih ketat, yang mungkin mengabaikan beberapa fitur kunci.
- Nilai yang lebih tinggi (misalnya, 4-5) lebih toleran terhadap pencilan, memungkinkan lebih banyak fitur digunakan namun mungkin
  mengurangi ketepatan penyelarasan.

Biasanya, nilai antara 1 hingga 3 sudah cukup, tergantung pada tingkat kebisingan dalam data."""

# Farneback Optical Flow
FARNEBACK_PARAMETER_SETTING_LABEL = "Parameter Farneback"

FARNEBACK_PYRAMID_SCALE_LABEL = "Skala Piramida"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Skala Piramida adalah faktor yang menentukan seberapa besar gambar dikurangi pada setiap level piramida.

- Nilai ini menentukan seberapa banyak ukuran gambar berkurang dari satu level ke level berikutnya.
  Misalnya, jika nilainya 0.5, maka setiap level akan memiliki setengah ukuran dari level sebelumnya.

- Nilai yang lebih kecil (misalnya, antara 0.10 dan 0.5) menghasilkan perbedaan ukuran yang lebih besar antar level,
  yang dapat mempercepat komputasi namun mungkin mengurangi ketepatan dalam menangkap detail gerak halus.

- Nilai yang mendekati 1.00 menghasilkan perubahan ukuran yang minimal antar level, memungkinkan penangkapan detail gerak yang lebih akurat,
  namun memerlukan waktu komputasi yang lebih lama.

Sesuaikan nilai ini sesuai kebutuhan Anda untuk mencapai keseimbangan antara kecepatan pemrosesan dan akurasi deteksi gerak.
Nilai yang direkomendasikan: 0.5.
"""

FARNEBACK_LEVELS_LABEL = "Level"
FARNEBACK_LEVELS_DESCRIPTION = """Level menentukan jumlah level dalam piramida gambar yang digunakan untuk perhitungan optical flow.

- Lebih banyak level memungkinkan algoritma mendeteksi gerak pada berbagai skala, yang berguna ketika gerak dalam gambar kompleks
  atau mencakup area yang luas.
- Peningkatan jumlah level juga meningkatkan waktu komputasi.

Biasanya, nilai 3 digunakan sebagai patokan, namun Anda dapat mengaturnya antara 1 hingga 10 tergantung kebutuhan aplikasi Anda.
"""

FARNEBACK_WIN_SIZE_LABEL = "Ukuran Jendela"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Ukuran Jendela adalah ukuran wilayah piksel (jendela) yang digunakan untuk menghitung optical flow.

- Jendela yang lebih besar menghasilkan hasil yang lebih stabil dan halus dengan cara merata-ratakan informasi di area yang lebih luas.
- Namun, jika jendelanya terlalu besar, mungkin akan menyembunyikan detail gerak yang kecil.

Pilih nilai yang seimbang antara kelancaran dan sensitivitas terhadap detail halus.
Nilai yang direkomendasikan: 15.
"""

FARNEBACK_ITERATIONS_LABEL = "Iterasi"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterasi menentukan berapa kali perhitungan optical flow diperbaiki pada setiap level piramida.

- Lebih banyak iterasi menghasilkan hasil optical flow yang lebih akurat.
- Namun, peningkatan jumlah iterasi juga meningkatkan waktu komputasi.

Pilih nilai yang meningkatkan akurasi tanpa secara signifikan memperlambat proses.
Nilai yang direkomendasikan: 3.
"""

FARNEBACK_POLY_N_LABEL = "Ekspansi Polinomial"
FARNEBACK_POLY_N_DESCRIPTION = """Ekspansi Polinomial (poly_n) menentukan ukuran lingkungan piksel yang digunakan untuk memperkirakan gerak melalui ekspansi polinomial.

- Nilai ini menentukan seberapa banyak data piksel di sekitarnya yang digunakan untuk perhitungan.
- Nilai yang lebih besar menghasilkan estimasi yang lebih halus namun mungkin mengurangi sensitivitas terhadap gerak kecil.

Nilai umum yang digunakan biasanya 5 atau 7, tergantung pada tingkat detail dan kestabilan yang diinginkan.
"""

FARNEBACK_POLY_SIGMA_LABEL = "Sigma Polinomial"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Sigma Polinomial mengontrol jumlah perataan yang diterapkan sebelum melakukan ekspansi polinomial.

- Nilai ini mewakili deviasi standar dari filter Gaussian yang diterapkan untuk mengurangi kebisingan dalam data piksel.
- Nilai sigma yang lebih tinggi dapat membantu mengurangi kebisingan, namun jika diatur terlalu tinggi, detail gerak yang penting mungkin hilang.

Sesuaikan nilai ini untuk mengurangi kebisingan tanpa mengorbankan detail gerak yang signifikan.
Nilai yang direkomendasikan: 1.2.
"""

FARNEBACK_FLAGS_LABEL = "Flag"
FARNEBACK_FLAGS_DESCRIPTION = """Flag adalah parameter opsional yang mengaktifkan opsi tertentu dalam algoritma Farneback.

- Misalnya, flag yang umum digunakan adalah penggunaan filter Gaussian untuk perataan, yang dapat menghasilkan optical flow yang lebih halus.
- Jika Anda tidak yakin, parameter ini biasanya dibiarkan pada nilai default (0).

Pilih flag yang sesuai jika Anda ingin mengoptimalkan keseimbangan antara kecepatan pemrosesan dan kualitas hasil.
Nilai yang direkomendasikan: 0.
"""

FARNEBACK_INTERPOLATION_LABEL = "Interpolasi"
FARNEBACK_INTERPOLATION_DESCRIPTION = """Interpolasi menentukan metode yang digunakan untuk memperkirakan nilai optical flow di antara piksel.

- Metode interpolasi berkualitas tinggi (misalnya, linear atau kubik) dapat menghasilkan transisi gerak yang lebih halus.
- Namun, metode yang lebih kompleks juga dapat meningkatkan waktu komputasi.

Pilih metode interpolasi yang seimbang antara kelancaran dan efisiensi pemrosesan.
Direkomendasikan: Interpolasi Kubik.
"""


# -------------------------- AKAZE -------------------------- #

AKAZE_PARAMETER_SETTING_LABEL = "Parameter AKAZE"

AKAZE_THRESHOLD_LABEL = "Threshold"
AKAZE_THRESHOLD_DESCRIPTION = """Parameter Threshold menentukan respons minimum detektor yang diperlukan untuk menerima sebuah titik kunci.

Nilai yang lebih rendah memungkinkan lebih banyak titik kunci terdeteksi (termasuk yang lebih lemah atau bising),
sedangkan nilai yang lebih tinggi membatasi deteksi hanya pada fitur yang paling kuat.

Nilai yang direkomendasikan: sekitar 30.
"""

AKAZE_OCTAVE_LABEL = "Jumlah Oktav"
AKAZE_OCTAVE_DESCRIPTION = """Parameter ini menentukan jumlah oktav dalam ruang skala.

Setiap oktav mewakili resolusi setengah dari gambar asli, memungkinkan detektor untuk menangkap fitur pada berbagai skala.
Lebih banyak oktav meningkatkan invariansi skala namun juga meningkatkan waktu komputasi.

Nilai yang direkomendasikan: 4.
"""

AKAZE_LAYER_LABEL = "Jumlah Lapisan per Oktav"
AKAZE_LAYER_DESCRIPTION = """Lapisan per Oktav menentukan jumlah sub-level dalam setiap oktav.

Jumlah lapisan yang lebih tinggi memberikan resolusi ruang skala yang lebih halus, yang dapat meningkatkan deteksi fitur pada berbagai skala, namun juga meningkatkan komputasi.

Nilai yang direkomendasikan: 4.
"""

AKAZE_RATIO_LABEL = "Rasio Threshold"
AKAZE_RATIO_DESCRIPTION = """Rasio Threshold digunakan selama proses pencocokan untuk membandingkan jarak antara kecocokan terbaik dengan kecocokan terbaik kedua dari deskriptor titik kunci.

Rasio yang lebih rendah (mendekati 0.50) berarti hanya kecocokan yang sangat khas dan tidak ambigu yang diterima, sedangkan rasio yang lebih tinggi (mendekati 1.00) memungkinkan lebih banyak kecocokan namun mungkin menyertakan positif palsu.

Nilai yang direkomendasikan: 0.80.
"""

APPLY_PARAMETER_BUTTON_TEXT = "Terapkan Pengaturan"

# ------------ Parameter Setting Algorithm --------------------- #


# Deskripsi untuk Alignment Algorithm
ALIGNMENT_NAME = "Algoritma Penyelarasan"
NONE_ALIGNMENT_DESCRIPTION = "Tidak akan ada penyelarasan yang diterapkan."
FARNEBACK_DESCRIPTION = """Algoritma ini cocok untuk penyelarasan tingkat tinggi yang memerlukan ketepatan dan akurasi hingga level piksel.

Namun, sangat lemah terhadap perbedaan rotasi dan perspektif yang signifikan."""

AKAZE_DESCRIPTION = """Algoritma ini cukup tangguh terhadap perbedaan besar dalam rotasi, perspektif, dan skala.

Cukup baik, tetapi tidak sebaik Farneback untuk level piksel."""
ORB_DESCRIPTION = """Algoritma cepat namun kurang akurat untuk perbedaan yang signifikan.

Cocok untuk gambar dengan perbedaan minimal."""

# Deskripsi untuk Super Resolution
SUPER_RESOLUTION_NAME = "Algoritma Super Resolusi"
NONE_SUPER_RESOLUTION_DESCRIPTION = "Tidak akan ada super resolusi yang diterapkan."
INTERPOLATION_DESCRIPTION = "Algoritma sederhana untuk meningkatkan resolusi melalui interpolasi, menambahkan sedikit detail."

# Deskripsi untuk Denoising
DENOISING_NAME = "Algoritma Pengurangan Noise"
NONE_DENOISING_DESCRIPTION = "Tidak akan ada pengurangan noise yang diterapkan."
WEIGHTED_AVERAGE_DESCRIPTION = """Hasil dari penyederhanaan metode penumpukan similarity cukup baik untuk pergerakan kecil

Cukup baik dalam menangani pergerakan kecil, tetapi menghasilkan artefak gambar pada pergerakan yang lebih besar."""
                        
AVERAGE_DESCRIPTION = """Metode penumpukan yang sangat cepat dan efektif untuk objek dan adegan statis

Tidak cocok untuk adegan atau area yang bergerak, tetapi dapat dikombinasikan dengan penyelarasan Farneback untuk menghilangkan pergerakan objek yang ringan."""

MEDIAN_DESCRIPTION = """Cepat dan efektif untuk penumpukan, cukup baik pada objek yang bergerak

Sangat efektif dalam menghilangkan pergerakan objek hingga 12 frame, namun artefak muncul pada objek yang bergerak setelah itu"""

SIMILARITY_DESCRIPTION = """Algoritma penumpukan canggih, sangat kuat dalam menghilangkan pergerakan objek (tanpa ghosting di area yang bergerak) dan menghasilkan sangat sedikit artefak hingga 90%

Terinspirasi oleh:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). An Analysis and Implementation of the HDR+ Burst Denoising Method.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336""" 
                        
                        
# ------------------ General Settings ------------------ #
SETTING_GENERAL_LABEL = "Umum"
LANGUAGE_LABEL = "Bahasa"

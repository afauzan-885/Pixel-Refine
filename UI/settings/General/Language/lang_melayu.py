# Kandungan Utama
UNDER_DEVELOPMENT = "{page_name} menu dalam pembangunan"

# Halaman Susun Penambahbaikan
TOPBAR_IMPORT_BUTTON_TEXT = "Import Imej"
TOPBAR_DELETE_BUTTON_TEXT = "Padam Imej"

PROGRESS_SECTION_PROCESS_BUTTON_TEXT = "Mula Proses"
PROGRESS_SECTION_SAVE_BUTTON_TEXT = "Simpan Sebagai"

HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION = "Fail Imej (*.jpg; *.jpeg; *.png; *.bmp; *.tif; *.tiff)"
HANDLE_IMPORT_BUTTON_IMAGE_PATH = "Pilih Imej"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE = "Fail Berganda"
HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE = "{count} fail sudah wujud dalam pangkalan data dan akan dilangkau."
HANDLE_IMPORT_BUTTON_IMAGE_SELECTED = "Format Dipilih"
HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT = "{count} fail dengan format '{format}' akan diimport."
HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED = "Ralat", "Tiada fail yang sah untuk diimport."

HANDLE_DELETE_BUTTON_IMAGE_NO_VALID_SELECTED = "Ralat", "Tiada imej dipilih."
HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE = "Adakah anda pasti mahu memadam {count} imej yang dipilih?"

UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE = "Memproses imej, sila tunggu..."
UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED = "Tiada imej dipilih."

UPDATE_PROGRESS_BAR_STATUS = "{value}% ({images_left} proses)"

ON_IMPORT_COMPLETE_STATUS = "Import selesai"
ON_IMPORT_COMPLETE_MESSAGES = "{successful_images} imej telah berjaya diimport."

PROCESS_ALGORITHM_PROCESS_SKIPPED = "Tiada algoritma dipilih untuk pemprosesan"

# PARAMETER STACKING 
RUN_PROCESS_STOPPED = "Proses dihentikan"
NOT_IMAGE_PREVIEW = "Tiada imej tersedia"
MODULE_NOT_IMPLEMENT = "Modul belum dilaksanakan."
NO_ALIGNMENT_PROCESS = "Adakah anda pasti tidak mahu penjajaran imej terlebih dahulu?"

# Mesej Umum
LOAD_IMAGES_FROM_PATHS_LOAD_FAILED = "Gagal memuatkan imej"

SAVE_TO_HDF5_ALIGNED_SAVING = "Menyimpan imej yang telah dijajarkan ke HDF5"
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING = "Imej ke-{index} telah disimpan dalam HDF5."
SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED = "Semua imej telah berjaya disimpan ke HDF5."
RESIZING_IMAGES_PROCESS = "Melaraskan saiz imej"

RUN_IMAGE_NOT_FOUND = "Tiada imej ditemui dalam pangkalan data."
RUN_REFERENCE_IMAGE_NOT_FOUND = "Imej rujukan tidak dapat dimuatkan dari {image_paths[0]}."
RUN_SAVING_REFERENCE_IMAGE = "Menyimpan imej rujukan ke HDF5."
RUN_IMAGE_PROCESSING = "Memproses imej {i} daripada {total_images}..."
RUN_IMAGE_PROCESSING_FAILED = "Gagal memuatkan imej {i} dari {image_paths[i]}."
RUN_IMAGE_PROCESSING_SAVING = "Imej ke-{i} telah disimpan dalam HDF5."
RUN_IMAGE_PROCESSING_FINISHED = "Proses Selesai."

CANCEL_PROCESSING = "Adakah anda pasti mahu membatalkan proses?"

RUN_ERROR_STATUS = "Ralat berlaku: {error}"
RUN_ERROR_MESSAGE = "Ralat berlaku: {error}"

DELETE_DEBUG_IMAGES_STATUS = "Memadam imej debug..."
DELETE_DEBUG_IMAGES_ONE_BY_ONE = "Memadam imej debug {image_id} satu per satu..."
DELETE_DEBUG_IMAGES_FINISHED = "Imej debug telah berjaya dipadam."

WINDOW_INITIATION = "Mula..."
WINDOW_START_PROCESSING = "Memulakan pemprosesan..."
WINDOW_PROCESSING_COMPLETE = "Selesai!"


# Aliran Optik Farneback
WINDOW_TITLE_FARNEBACK = "Penjajaran Aliran Optik Farneback"

CALCULATE_OPTICAL_FLOW_STATUS = "Mengira aliran optik menggunakan {device}..."
CALCULATE_OPTICAL_FLOW_FINISHED = "Pengiraan aliran optik telah selesai."

COMPENSATE_MOTION_STATUS = "Melakukan pampasan pergerakan pada imej {image_id}..."
COMPENSATE_MOTION_FINISHED = "Pampasan pergerakan selesai untuk imej {image_id}."


# AKAZE, ORB
WINDOW_TITLE_AKAZE = "Penjajaran AKAZE"
ALIGN_IMAGES_STATUS_AKAZE = "Menjajarkan imej {image_id} menggunakan AKAZE..."

WINDOW_TITLE_ORB = "Penjajaran ORB"
ALIGN_IMAGES_STATUS_ORB = "Menjajarkan imej {image_id} menggunakan ORB..."

ALIGN_IMAGES_CALCULATE_FAILED = "Tiada ciri dikesan dalam sebarang imej untuk {image_id}. Mengembalikan imej asal."
ALIGN_IMAGES_CALCULATE_FINISHED = "Penjajaran selesai untuk imej {image_id}."
ALIGN_IMAGES_COMPENSATE_FAILED = "Homografi tidak dapat dikira untuk imej {image_id}. Mengembalikan imej asal."
ALIGN_IMAGES_MATCHING_FAILED = "Bilangan padanan tidak mencukupi untuk imej {image_id}. Mengembalikan imej asal."


# Algoritma Pengurangan Bising
STACK_IMAGES_FAILED = "Tiada imej untuk diproses."
STACK_AVERAGE_IMAGES_PROCESS = "Memproses imej {current}/{total}..."

RUN_IMAGE_PROCESS_STARTED = "Memulakan proses..."
RUN_IMAGE_PROCESS_LOAD_HDF5 = "Memuatkan imej dari HDF5..."
RUN_IMAGE_PROCESS_LOAD_PROGRESS = "Memuatkan imej {current}/{total}..."

RUN_IMAGE_PROCESS_LOAD_PATH = "Mengambil senarai imej dari pangkalan data..."
RUN_IMAGE_PROCESS_LOAD_FAILED = "Tiada imej ditemui dalam pangkalan data."
RUN_IMAGE_PROCESS_STACK_SUCCESS = "Penyusunan imej selesai! Hasil disimpan di: {output_path}"

WINDOW_PROCESS_SUCCESS = "Proses telah selesai."


# Penyusunan Purata, Median, Persamaan
WINDOW_TITLE_AVERAGE = "Penyusunan Purata"
WINDOW_TITLE_MEDIAN = "Penyusunan Median"
WINDOW_TITLE_WEIGHTED_AVERAGE = "Penyusunan Purata Berwajaran"

WINDOW_TITLE_SIMILARITY = "Penyusunan Persamaan"
SIMILARITY_MNFR_LOAD_FAILED = "Tiada imej yang disediakan."
SIMILARITY_MNFR_BIT_REQUIRED = "Imej mesti 8 Bit atau 16 Bit."
SIMILARITY_MNFR_TILE_SLICE = "Dimensi imej: {height}x{width}, Saiz jubin: {tile_size}"
SIMILARITY_MNFR_SIZE_FAILED = "Saiz imej {i} tidak sepadan dengan imej rujukan."
SIMILARITY_MNFR_PROCESS_SUCCESS = "Imej {i}/{count} diproses dengan jayanya."
SIMILARITY_MNFR_PROCESS_FINISHED = "Penyusunan selesai."
RUN_IMAGE_PROCESS_BATCH_PROGRESS = "Menyusun batch ke {current} daripada {total}"


# Super Resolusi
WINDOW_TITLE_INTERPOLATION = "Super Resolusi Interpolasi"

# ------------ Tetapan Parameter Algoritma --------------------- #
DEFAULT_PARAMETER_SETTING_LABEL = "Pilih algoritma untuk melihat tetapan parameter."

# Parameter ORB
ORB_PARAMETER_SETTING_LABEL = "Parameter ORB"
ORB_NFEATURES_LABEL = "Bilangan Ciri"
ORB_NFEATURES_DESCRIPTION = """Bilangan ciri mewakili jumlah perincian halus yang boleh dikenal pasti dalam imej.

Bilangan ciri yang lebih tinggi membolehkan algoritma mengenal pasti lebih banyak perincian, menghasilkan penjajaran imej yang lebih tepat.
Walau bagaimanapun, mengesan lebih banyak ciri meningkatkan masa pengiraan.

Secara amnya, nilai antara 500 dan 1500 adalah mencukupi untuk kebanyakan aplikasi.
Untuk keperluan ketepatan yang sangat tinggi, memilih nilai antara 2500 hingga 5000 mungkin dapat meningkatkan ketepatan."""
ORB_SCALEFACTOR_LABEL = "Faktor Skala"
ORB_SCALEFACTOR_DESCRIPTION = """Faktor skala menentukan kadar di mana imej dikecilkan secara iteratif semasa pemprosesan.

- Nilai yang hampir dengan 1.0 bermaksud imej dikecilkan secara beransur-ansur (lebih banyak langkah), membolehkan pengesanan perincian halus tetapi mengambil masa yang lebih lama.
- Nilai yang lebih tinggi mengecilkan imej dengan lebih cepat, membawa kepada pemprosesan yang lebih pantas tetapi berpotensi mengabaikan beberapa perincian halus.

Nilai biasa berkisar antara 1.2 hingga 1.5."""
ORB_NLEVELS_LABEL = "Bilangan Tahap"
ORB_NLEVELS_DESCRIPTION = """Bilangan tahap menunjukkan lapisan dalam piramid imej yang digunakan untuk pengesanan ciri.

Lebih banyak tahap membolehkan algoritma menangkap perincian pada pelbagai skala, yang bermanfaat apabila imej berbeza saiz,
tetapi tahap yang meningkat juga bermaksud masa pemprosesan yang lebih lama.

Secara amnya, nilai antara 2 dan 4 adalah ideal untuk kebanyakan aplikasi."""
ORB_TRANSFORMATION_LABEL = "Jenis Transformasi"
ORB_TRANSFORMATION_DESCRIPTION = """Jenis transformasi menentukan kaedah yang digunakan untuk menjajarkan imej.

Pilihan yang tersedia termasuk:
- Homografi: Membenarkan transformasi perspektif, ideal untuk imej yang diambil dari sudut yang berbeza.
- Afine: Membenarkan pusingan, pengubahan saiz, dan penterjemahan (pergeseran).
- Persamaan: Hanya membenarkan pusingan, pengubahan saiz seragam, dan penterjemahan, mengekalkan nisbah aspek imej.
- Euclidean: Hanya membenarkan pusingan dan penterjemahan tanpa pengubahan saiz, menawarkan pilihan yang paling mudah.

Pilihan transformasi bergantung pada perbezaan antara imej yang hendak dijajarkan.
Untuk kebanyakan aplikasi, Homografi sering dipilih kerana fleksibilitinya dalam menangani perbezaan perspektif."""
ORB_RANSAC_LABEL = "RANSAC Threshold"
ORB_RANSAC_DESCRIPTION = """RANSAC Threshold menentukan sejauh mana algoritma menapis outlier semasa penjajaran imej.

- Nilai yang lebih rendah (contoh, 1-2) melaksanakan penapisan yang lebih ketat, berpotensi membuang beberapa ciri utama.
- Nilai yang lebih tinggi (contoh, 4-5) lebih toleran terhadap outlier, membenarkan lebih banyak ciri digunakan tetapi mungkin mengurangkan ketepatan penjajaran.

Secara amnya, nilai antara 1 dan 3 adalah mencukupi, bergantung pada tahap gangguan dalam data."""
  

# Parameter Aliran Optik Farneback
FARNEBACK_PARAMETER_SETTING_LABEL = "Parameter Farneback"
FARNEBACK_PYRAMID_SCALE_LABEL = "Skala Piramid"
FARNEBACK_PYRAMID_SCALE_DESCRIPTION = """Skala Piramid adalah faktor di mana imej dikecilkan pada setiap tahap piramid.

- Nilai ini menentukan berapa banyak saiz imej dikurangkan dari satu tahap ke tahap berikutnya.
  Sebagai contoh, jika nilainya 0.5, maka setiap tahap akan mempunyai saiz separuh daripada tahap sebelumnya.

- Nilai yang lebih kecil (contohnya, antara 0.10 dan 0.5) menghasilkan perbezaan saiz yang lebih besar antara tahap,
  yang boleh mempercepatkan pengiraan tetapi mungkin mengurangkan ketepatan dalam menangkap perincian pergerakan halus.

- Nilai yang hampir dengan 1.00 menghasilkan perubahan saiz yang minimum antara tahap, membolehkan penangkapan perincian pergerakan yang lebih tepat,
  tetapi memerlukan masa pengiraan yang lebih lama.

Sesuaikan nilai ini mengikut keperluan anda untuk keseimbangan antara kelajuan pemprosesan dan ketepatan pengesanan pergerakan.
Nilai disarankan: 0.5."""
FARNEBACK_LEVELS_LABEL = "Tahap"
FARNEBACK_LEVELS_DESCRIPTION = """Tahap menentukan bilangan tahap dalam piramid imej yang digunakan untuk pengiraan aliran optik.

- Lebih banyak tahap membolehkan algoritma mengesan pergerakan pada pelbagai skala, yang bermanfaat apabila pergerakan dalam imej adalah kompleks atau meliputi kawasan yang luas.
- Walau bagaimanapun, peningkatan bilangan tahap juga meningkatkan masa pengiraan.

Secara amnya, nilai 3 digunakan sebagai penanda aras, tetapi anda boleh menetapkannya antara 1 hingga 10 bergantung kepada keperluan aplikasi anda."""
FARNEBACK_WIN_SIZE_LABEL = "Saiz Tetingkap"
FARNEBACK_WIN_SIZE_DESCRIPTION = """Saiz Tetingkap adalah saiz kawasan piksel (tetingkap) yang digunakan untuk mengira aliran optik.

- Tetingkap yang lebih besar menghasilkan keputusan yang lebih stabil dan licin dengan mengagihkan maklumat ke atas kawasan yang lebih luas.
- Walau bagaimanapun, jika tetingkap terlalu besar, ia mungkin menenggelamkan perincian pergerakan kecil.

Pilih nilai yang seimbang antara kelicinan dan kepekaan terhadap perincian halus.
Nilai disarankan: 15."""
FARNEBACK_ITERATIONS_LABEL = "Iterasi"
FARNEBACK_ITERATIONS_DESCRIPTION = """Iterasi menentukan berapa kali pengiraan aliran optik ditapis semula pada setiap tahap piramid.

- Lebih banyak iterasi menghasilkan keputusan aliran optik yang lebih tepat.
- Walau bagaimanapun, peningkatan iterasi juga meningkatkan masa pengiraan.

Pilih nilai yang meningkatkan ketepatan tanpa melambatkan proses dengan ketara.
Nilai disarankan: 3."""
FARNEBACK_POLY_N_LABEL = "Pengembangan Polinomial"
FARNEBACK_POLY_N_DESCRIPTION = """Pengembangan Polinomial (poly_n) menentukan saiz kawasan sekeliling piksel yang digunakan untuk menganggarkan pergerakan melalui pengembangan polinomial.

- Nilai ini menentukan berapa banyak data piksel sekeliling yang digunakan untuk pengiraan.
- Nilai yang lebih besar menghasilkan anggaran yang lebih licin tetapi mungkin mengurangkan kepekaan terhadap pergerakan kecil.

Nilai yang biasa digunakan biasanya 5 atau 7, bergantung kepada tahap perincian dan kestabilan yang dikehendaki."""
FARNEBACK_POLY_SIGMA_LABEL = "Polinomial Sigma"
FARNEBACK_POLY_SIGMA_DESCRIPTION = """Polinomial Sigma mengawal tahap kelicinan yang dikenakan sebelum melakukan pengembangan polinomial.

- Ia mewakili sisihan piawai penapis Gaussian yang digunakan untuk mengurangkan gangguan dalam data piksel.
- Nilai sigma yang lebih tinggi boleh membantu mengurangkan gangguan, tetapi jika ditetapkan terlalu tinggi, perincian pergerakan yang penting mungkin hilang.

Sesuaikan nilai ini untuk mengurangkan gangguan tanpa mengorbankan perincian pergerakan yang penting.
Nilai disarankan: 1.2."""
FARNEBACK_FLAGS_LABEL = "Bendera"
FARNEBACK_FLAGS_DESCRIPTION = """Bendera adalah parameter pilihan yang membolehkan pilihan khusus dalam algoritma Farneback.

- Sebagai contoh, bendera biasa adalah penggunaan penapis Gaussian untuk kelicinan, yang boleh menghasilkan aliran optik yang lebih licin.
- Jika anda tidak pasti, parameter ini biasanya dibiarkan pada nilai lalai (0).

Pilih bendera yang sesuai jika anda ingin mengoptimumkan keseimbangan antara kelajuan pemprosesan dan kualiti keputusan.
Nilai disarankan: 0."""
FARNEBACK_INTERPOLATION_LABEL = "Interpolasi"
FARNEBACK_INTERPOLATION_DESCRIPTION = """Interpolasi menetapkan kaedah yang digunakan untuk menganggarkan nilai aliran optik antara piksel.

- Kaedah interpolasi berkualiti tinggi (contohnya, linear atau kubik) boleh menghasilkan peralihan pergerakan yang lebih licin.
- Walau bagaimanapun, kaedah yang lebih kompleks juga boleh meningkatkan masa pengiraan.

Pilih kaedah interpolasi yang seimbang antara kelicinan dan kecekapan pemprosesan.
Disarankan: Interpolasi Kubik."""


# Parameter AKAZE
AKAZE_PARAMETER_SETTING_LABEL = "Parameter AKAZE"
AKAZE_THRESHOLD_LABEL = "Threshold"
AKAZE_THRESHOLD_DESCRIPTION = """Parameter Threshold menetapkan respons minimum pengesan yang diperlukan untuk menerima satu titik kunci.

Nilai yang lebih rendah membolehkan lebih banyak titik kunci dikesan (termasuk yang lebih lemah atau bising), 
manakala nilai yang lebih tinggi menghadkan pengesanan kepada ciri-ciri yang paling kuat sahaja.

Nilai disarankan: sekitar 30."""
AKAZE_OCTAVE_LABEL = "Bilangan Oktav"
AKAZE_OCTAVE_DESCRIPTION = """Parameter ini menentukan bilangan oktav dalam ruang skala. 

Setiap oktav mewakili resolusi imej asal yang dikurangkan separuh, membolehkan pengesan menangkap 
ciri-ciri pada pelbagai skala. Lebih banyak oktav meningkatkan ketetapan skala tetapi meningkatkan masa pengiraan. 

Nilai disarankan: 4."""
AKAZE_LAYER_LABEL = "Lapisan setiap Oktav"
AKAZE_LAYER_DESCRIPTION = """Lapisan setiap Oktav menentukan bilangan sub-tahap dalam setiap oktav.

Bilangan lapisan yang lebih tinggi menyediakan resolusi ruang skala yang lebih halus, yang boleh meningkatkan pengesanan ciri-ciri 
merentas skala, tetapi ia juga meningkatkan pengiraan. 

Nilai disarankan: 4."""
AKAZE_RATIO_LABEL = "Nisbah Threshold"
AKAZE_RATIO_DESCRIPTION = """Nisbah threshold digunakan semasa proses pemadanan untuk membandingkan jarak padanan terbaik 
dengan padanan kedua terbaik bagi deskriptor titik kunci.

Nisbah yang lebih rendah (hampir 0.50) bermaksud hanya padanan yang sangat tersendiri dan jelas diterima, 
manakala nisbah yang lebih tinggi (hampir 1.00) membenarkan lebih banyak padanan 
tetapi mungkin termasuk padanan palsu.

Nilai disarankan: 0.80."""

KEEP_EDGES_LABEL = "Menyimpan Tepi"
KEEP_EDGES_DESCRIPTION = """Pilihan ini membenarkan penjajaran imej
untuk menyimpan ciri tepi imej."""


APPLY_PARAMETER_BUTTON_TEXT = "Terapkan Tetapan"

# Deskripsi untuk Algoritma Penjajaran
ALIGNMENT_NAME = "Algoritma Penjajaran"
NONE_ALIGNMENT_DESCRIPTION = "Tiada penjajaran akan digunakan."
FARNEBACK_DESCRIPTION = """Algoritma ini sesuai untuk penjajaran tahap tinggi yang memerlukan
ketepatan dan keakuratan hingga ke tahap piksel.

Tetapi sangat lemah terhadap perbezaan pusingan dan perspektif yang signifikan"""

AKAZE_DESCRIPTION = """Algoritma ini cukup kukuh terhadap perbezaan besar dalam pusingan, perspektif dan skala

Cukup baik tetapi tidak sebaik Farneback untuk tahap piksel"""
ORB_DESCRIPTION = """Algoritma yang pantas tetapi kurang tepat untuk perbezaan yang signifikan

Sesuai untuk imej dengan perbezaan yang minimum"""

# Deskripsi untuk Super Resolusi
SUPER_RESOLUTION_NAME = "Algoritma Super Resolusi"
NONE_SUPER_RESOLUTION_DESCRIPTION = "Tiada super-resolusi akan digunakan."
INTERPOLATION_DESCRIPTION = """Algoritma mudah untuk meningkatkan resolusi melalui interpolasi, menambah sedikit perincian."""

# Deskripsi untuk Pengurangan Bising
DENOISING_NAME = "Algoritma Pengurangan Bising"
NONE_DENOISING_DESCRIPTION = "Tiada pengurangan bising akan digunakan."
WEIGHTED_AVERAGE_DESCRIPTION = """Hasil penyederhanaan kaedah penyusunan persamaan agak baik untuk pergerakan kecil

Cukup baik untuk menangani pergerakan kecil, tetapi menghasilkan artifak imej pada pergerakan yang lebih besar"""
  
AVERAGE_DESCRIPTION = """Kaedah penyusunan yang sangat pantas dan berkesan untuk objek dan pemandangan yang statik

Tidak sesuai untuk adegan atau kawasan yang bergerak tetapi boleh digabungkan dengan penjajaran Farneback
untuk menghapuskan pergerakan objek yang sedikit."""
MEDIAN_DESCRIPTION = """Penyusunan yang pantas dan berkesan, agak baik untuk objek yang bergerak

Sangat berkesan untuk menghapuskan pergerakan objek sehingga 12 bingkai, tetapi artifak muncul pada objek bergerak selepas itu"""
SIMILARITY_DESCRIPTION = """Algoritma penyusunan lanjutan, sangat berkuasa dalam menghapuskan pergerakan objek (tiada ghosting di kawasan bergerak)
dan menghasilkan sangat sedikit artifak sehingga 90%

Diilhamkan oleh:
Monod, Antoine, Delon, Julie, & Veit, Thomas. (2021). Analisis dan Pelaksanaan Kaedah Pengurangan Bising HDR+ Burst.
Image Processing On Line, 11, 142-169. https://doi.org/10.5201/ipol.2021.336"""
                        
# ------------------ Tetapan Umum ------------------ #

SETTING_GENERAL_LABEL = "Umum"
LANGUAGE_LABEL = "Bahasa"

import os
import subprocess
import logging

# --- Konfigurasi Logging (Sama seperti skrip Anda) ---
log_file = "build_nuitka_log.txt"
logging.basicConfig(
    filename=log_file,
    filemode='w',
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)


# --- Konfigurasi Build Nuitka ---

# Informasi Dasar
main_script = "main.py"
output_name = "Pixel Refine"
icon_path = os.path.abspath("UI/resources/image/Logo_Pixel_Refine.png")

excluded_modules = [
    "tkinter",
    "distutils",
    "http",
    "train_model_standalone",
    "watcher",
    "test_database",
    "download_model",
    "UI.enhance_stack.algorithm.model_trainer.mobile_net_v2",
    "UI.enhance_stack.algorithm.model_trainer.inspect_model",
    "UI.enhance_stack.algorithm.denoising.extra_code.Compiler",
    "torch",
    "scipy",
    "pyopencl",
    "watchdog",
    "sklearn",
]

# Modul yang harus disertakan secara paksa (untuk hidden imports)
included_modules = [
    "h5py._npystrings",
    "h5py.defs",
    "h5py.utils",
    "h5py._proxy",
]

# File atau direktori data yang akan disertakan
# Format: ('path_sumber', 'path_tujuan_di_dalam_build')
data_dirs = [
    ("UI", "UI"),
    ("database", "database"), # <-- PENTING: Jangan lupa folder database
    ("test_algorithm", "test_algorithm"),
]

# File data yang secara eksplisit TIDAK akan disertakan
excluded_data_files = [
    "UI/enhance_stack/algorithm/model_trainer/mobile_net_v2.py",
    "UI/enhance_stack/algorithm/model_trainer/inspect_model.py",
    "train_model_standalone.py",
    "UI/enhance_stack/algorithm/denoising/extra_code/Compiler/*",
    "download_model.py",
    "test_database.py",
    "watcher.py",
]


def build_nuitka():
    """
    Membangun daftar perintah Nuitka dan menjalankannya.
    """
    logging.info("🚀 Memulai proses build dengan Nuitka...")

    # Memulai perintah dasar
    command = [
        "python",
        "-m",
        "nuitka",
        "--standalone",
        "--windows-disable-console", # Ekuivalen dengan --windowed di PyInstaller
        "--plugin-enable=pyside6",
        "--output-filename", output_name,
        "--windows-icon-from-ico", icon_path,
    ]

    # Menambahkan modul yang di-exclude (--nofollow-import-to)
    for mod in excluded_modules:
        command.append(f"--nofollow-import-to={mod}")

    # Menambahkan modul yang di-include (--include-module)
    for mod in included_modules:
        command.append(f"--include-module={mod}")

    # Menambahkan direktori data (--include-data-dir)
    for src, dst in data_dirs:
        command.append(f"--include-data-dir={src}={dst}")
        
    # Menambahkan file data yang di-exclude (--noinclude-data-files)
    for f in excluded_data_files:
        command.append(f"--noinclude-data-files={f}")

    # Menambahkan skrip utama di akhir
    command.append(main_script)

    logging.info(f"Perintah Nuitka yang akan dieksekusi:\n{' '.join(command)}")

    try:
        # Menjalankan proses build
        subprocess.run(command, check=True)
        logging.info("✅ Build Nuitka berhasil diselesaikan.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Build Nuitka gagal: Proses mengembalikan kode error. Lihat log di atas untuk detail.")
        logging.error(f"   Detail Error: {e}")
    except FileNotFoundError:
        logging.error("❌ Gagal: Perintah 'python' atau 'nuitka' tidak ditemukan. Pastikan Python dan Nuitka terinstal dan ada di PATH.")
    except Exception as e:
        logging.error(f"❌ Terjadi kesalahan yang tidak terduga: {e}")

if __name__ == "__main__":
    build_nuitka()
import subprocess
import os
import sys
import logging

# Logging setup
log_file = "build_log.txt"
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

# Configuration
main_script = "main.py"
output_dir = "build"
output_name = "Pixel Refine"
upx_path = r"C:\upx-5.0.1\upx.exe"
icon_path = r"UI\resources\image\Logo_Pixel_Refine.png"

# ⛔ Daftar file atau modul yang ingin dikecualikan (tanpa .pyc atau .pyd, cukup .py)
EXCLUDED_FILES = [
    "UI/enhance_stack/algorithm/model_trainer/mobile_net_v2.py",
    "UI/enhance_stack/algorithm/denoising/extra_code/Compiler/*",
    "UI/enhance_stack/algorithm/model_trainer/inspect_model.py",
    "train_model_standalone.py",
    "watcher.py",
    "test_database.py",
    "build_exe.py",
    "download_model.py",
]

# 🔁 Ubah EXCLUDED_FILES menjadi argumen Nuitka
exclude_args = []
for path in EXCLUDED_FILES:
    if "*" in path:
        exclude_args.append(f"--noinclude-data-files={path}")
    elif os.path.sep in path or "/" in path:
        module_path = path.replace("/", ".").replace("\\", ".").removesuffix(".py")
        exclude_args.append(f"--nofollow-import-to={module_path}")
        exclude_args.append(f"--noinclude-data-files={path}")
    else:
        module_path = path.removesuffix(".py")
        exclude_args.append(f"--nofollow-import-to={module_path}")
        exclude_args.append(f"--noinclude-data-files={path}")

# Perintah build Nuitka
nuitka_command = [
    sys.executable, "-m", "nuitka", main_script,
    "--standalone",
    f"--output-dir={output_dir}",
    f"--output-filename={output_name}",
    "--include-data-dir=UI=UI",
    "--plugin-enable=pyqt6",
    "--plugin-enable=anti-bloat",
    "--nofollow-import-to=tkinter",
    "--nofollow-import-to=distutils",
    "--nofollow-import-to=http",
    "--nofollow-import-to=email",
    "--nofollow-import-to=idlelib",
    "--noinclude-default-mode=nofollow",
    "--no-pyi-file",
    f"--windows-icon-from-ico={icon_path}",
    "--clang",
    # "--remove-output",
    "--show-memory",
    "--python-flag=-OO",
    "--assume-yes-for-downloads",
    "--report=build-report.xml"
] + exclude_args  # 🔁 Tambahkan pengecualian di sini

def check_python():
    try:
        subprocess.run(["python", "--version"], check=True, stdout=subprocess.DEVNULL)
        logging.info("Python is available.")
    except subprocess.CalledProcessError:
        logging.error("Python is not found in PATH.")
        sys.exit(1)

def run_nuitka_build():
    logging.info("Starting Nuitka compilation process...")
    try:
        subprocess.run(nuitka_command, check=True)
        logging.info("Nuitka compilation completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error("Build process failed.")
        logging.error(str(e))
        sys.exit(1)

def compress_with_upx():
    exe_path = os.path.join(output_dir, f"{output_name}.dist", f"{output_name}.exe")
    dll_dir = os.path.join(output_dir, f"{output_name}.dist")

    if os.path.exists(upx_path):
        logging.info("Compressing executable and DLLs using UPX...")
        try:
            subprocess.run([upx_path, "--best", "--lzma", exe_path], check=True)
            logging.info(f"Compressed: {exe_path}")
            for file in os.listdir(dll_dir):
                if file.endswith(".dll"):
                    dll_path = os.path.join(dll_dir, file)
                    subprocess.run([upx_path, "--best", "--lzma", dll_path], check=True)
                    logging.info(f"Compressed: {dll_path}")
            logging.info("UPX compression finished.")
        except subprocess.CalledProcessError as e:
            logging.error(f"UPX compression failed: {e}")
    else:
        logging.warning(f"UPX not found at {upx_path}. Skipping compression.")

def main():
    logging.info("========== Build Process Started ==========")
    check_python()
    run_nuitka_build()
    compress_with_upx()
    logging.info(f"Build completed. Check the '{output_dir}\\{output_name}.dist' folder.")
    logging.info("========== Build Process Finished ==========")

if __name__ == "__main__":
    main()

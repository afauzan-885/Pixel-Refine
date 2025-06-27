import os
import subprocess
import logging

# Logging setup
log_file = "build_pyinstaller_log.txt"
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
output_name = "Pixel Refine.exe"
icon_path = os.path.abspath("UI/resources/image/Logo_Pixel_Refine.png")
excluded_modules = [
    "train_model_standalone",
    "watcher",
    "test_database",
    "build_exe",
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
extra_data = [
    ("UI", "UI"),
    # ("test_algorithm", "test_algorithm"),
    ("config.py", "."),
]

def build_pyinstaller():
    logging.info("🚀 Starting PyInstaller build...")

    excludes = []
    for mod in excluded_modules:
        excludes.extend(["--exclude-module", mod])

    datas = []
    for src, dst in extra_data:
        src_path = os.path.abspath(src)
        datas.extend(["--add-data", f"{src_path};{dst}"])

    command = [
        "pyinstaller",
        "--name", output_name.replace(".exe", ""),
        "--noconfirm",
        # "--windowed",
        "--clean",
        # "--onefile",
        "--icon", icon_path
    ] + datas + excludes + [main_script]

    try:
        subprocess.run(command, check=True)
        logging.info("✅ PyInstaller build completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ PyInstaller build failed: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    build_pyinstaller()
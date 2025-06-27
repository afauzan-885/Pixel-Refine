import os
import logging
from cx_Freeze import setup, Executable

# Logging setup
log_file = "build_cx_freeze_log.txt"
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
output_name = "Pixel Refine"
icon_path = os.path.abspath("UI/resources/image/Logo_Pixel_Refine.png")

# Excluded modules to reduce size
excluded_modules = [
    "tkinter",
    "unittest",
    "doctest",
    "pydoc",
    "test",
    "email",
    "html",
    "http",
    "xml",
    "torch",
    "torchvision",
    "torchaudio",
    "tensorflow",
    "keras",
    "sklearn",
    "joblib",
    "scipy",
    "IPython"
]

# Include additional files (e.g., UI, database)
include_files = [
    ("UI", "UI"),
    ("database", "database")
]

# Build options
build_exe_options = {
    "packages": [],
    "excludes": excluded_modules,
    "include_files": include_files,
    "optimize": 2,  # 0 = no optimization, 1 = assert removal, 2 = assert removal + docstrings removal
    "zip_include_packages": ["*"],
    "zip_exclude_packages": []
}

# Define the executable
target = Executable(
    script=main_script,
    base=None,  # or "Win32GUI" for no console window
    target_name=output_name,
    icon=icon_path
)

def build_with_cx_freeze():
    logging.info("🚀 Starting cx_Freeze build...")
    try:
        setup(
            name=output_name,
            version="1.0",
            description="Pixel Refine Application",
            options={"build_exe": build_exe_options},
            executables=[target]
        )
        logging.info("✅ cx_Freeze build script executed successfully.")
        print("\n🟢 Build initiated.\nRun this script with:\n  python build_cx_freeze.py build\n")
    except Exception as e:
        logging.error(f"❌ cx_Freeze build failed: {e}")
        print(f"❌ cx_Freeze build failed: {e}")

if __name__ == "__main__":
    build_with_cx_freeze()

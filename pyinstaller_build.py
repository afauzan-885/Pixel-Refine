"""Target-qualified PyInstaller release builder for Pixel Refine.

The native AOT payload is planned by the same manifest-driven helper used by
``nuitka_build.py``.  This keeps PyInstaller and Nuitka from shipping different
sets of TCM/bridge files and prevents compiler intermediates from entering a
release directory.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

from taichi_vision.release_bundle import (
    cleanup_aot_bundle,
    plan_aot_bundle,
    plan_runtime_payload,
    validate_entrypoint,
)


PROJECT_ROOT = Path(__file__).resolve().parent
MAIN_SCRIPT = PROJECT_ROOT / "main_desktop.py"
OUTPUT_NAME = os.environ.get("PIXEL_REFINE_PYINSTALLER_NAME", "Pixel Refine")
ICON_PATH = PROJECT_ROOT / "resources" / "assets" / "images" / "Logo_Pixel_Refine.ico"
AOT_TCM_ROOT = PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
AOT_DLL_ROOT = PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py" / "aot_dll"
MANIFEST_PATH = AOT_TCM_ROOT / "target_manifest.json"
LLVM20_RELEASE_ROOT = Path(
    os.environ.get("PIXEL_REFINE_RUNTIME_ROOT", "")
    or (PROJECT_ROOT / "runtime")
)
_release_candidate = LLVM20_RELEASE_ROOT / "release"
if (_release_candidate / "RELEASE_MANIFEST.json").is_file() and (
    _release_candidate / "bundles"
).is_dir():
    LLVM20_RELEASE_ROOT = _release_candidate

LOG_FILE = PROJECT_ROOT / "build_pyinstaller_log.txt"


def _configure_logging():
    """Configure build logging only when a build is actually requested.

    Importing this module is used by release-planner tests and dry-runs; it
    must not create an empty log artifact as an import side effect.
    """

    root_logger = logging.getLogger()
    if not any(getattr(handler, "_pixel_refine_pyinstaller", False) for handler in root_logger.handlers):
        file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        file_handler._pixel_refine_pyinstaller = True
        root_logger.addHandler(file_handler)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        console._pixel_refine_pyinstaller = True
        root_logger.addHandler(console)
    root_logger.setLevel(logging.INFO)


EXCLUDED_MODULES = (
    # The repository venv still carries the historical pip Taichi Python
    # package (LLVM15).  The production application uses the target-qualified
    # LLVM20 AOT bridge/TCM payload directly; bundling this optional JIT
    # package would silently reintroduce LLVM15 binaries into the EXE.
    "taichi",
    "train_model_standalone",
    "watcher",
    "test_database",
    "build_exe",
    "download_model",
    "torch",
    "torchvision",
    "torchaudio",
    "pyopencl",
    "watchdog",
    "sklearn",
)


def _pyinstaller_data_args(bundle):
    """Convert shared planner data dirs to PyInstaller's ``src;dest`` form."""

    args = []
    for source, destination in bundle.data_dirs:
        args.extend(["--add-data", f"{source};{destination}"])
    return args


def build_command(bundle):
    """Build a deterministic command without starting PyInstaller."""

    entrypoint = validate_entrypoint(PROJECT_ROOT, MAIN_SCRIPT)
    if not ICON_PATH.is_file():
        raise FileNotFoundError(f"application icon does not exist: {ICON_PATH}")

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        OUTPUT_NAME,
        "--noconfirm",
        "--clean",
        "--paths",
        str(PROJECT_ROOT),
        "--add-data",
        f"{PROJECT_ROOT / 'pixel_refine_desktop'};pixel_refine_desktop",
        "--add-data",
        f"{PROJECT_ROOT / 'resources'};resources",
        "--add-data",
        f"{PROJECT_ROOT / 'config.py'};.",
        "--icon",
        str(ICON_PATH),
    ]
    # Keep packaging intermediates and the final executable outside the
    # repository by default when a release job supplies explicit staging
    # paths.  The options are additive and preserve PyInstaller's historical
    # defaults when the variables are unset.
    output_paths = (
        ("PIXEL_REFINE_PYINSTALLER_DISTPATH", "--distpath"),
        ("PIXEL_REFINE_PYINSTALLER_WORKPATH", "--workpath"),
        ("PIXEL_REFINE_PYINSTALLER_SPECPATH", "--specpath"),
    )
    for env_name, option in output_paths:
        value = os.environ.get(env_name, "").strip()
        if value:
            command.extend([option, value])
    if os.environ.get("PIXEL_REFINE_PYINSTALLER_ONEFILE", "0").strip() == "1":
        command.append("--onefile")
    if os.environ.get("PIXEL_REFINE_PYINSTALLER_WINDOWED", "0").strip() == "1":
        command.append("--windowed")
    command.extend(_pyinstaller_data_args(bundle))
    for module in EXCLUDED_MODULES:
        command.extend(["--exclude-module", module])
    command.append(str(entrypoint))
    return command


def build_pyinstaller():
    _configure_logging()
    logging.info("Starting target-qualified PyInstaller build")
    bundle = None
    try:
        preflight_all = os.environ.get("PIXEL_REFINE_BUNDLE_PREFLIGHT_ALL", "0").strip() == "1"
        if preflight_all:
            logging.info("Manifest-wide AOT preflight enabled (PIXEL_REFINE_BUNDLE_PREFLIGHT_ALL=1)")
        if (LLVM20_RELEASE_ROOT / "RELEASE_MANIFEST.json").is_file() and (
            LLVM20_RELEASE_ROOT / "bundles"
        ).is_dir():
            logging.info("Using isolated LLVM20 release payload: %s", LLVM20_RELEASE_ROOT)
            bundle = plan_runtime_payload(runtime_root=LLVM20_RELEASE_ROOT)
        else:
            logging.info("Using legacy flat AOT source payload: %s", AOT_TCM_ROOT)
            bundle = plan_aot_bundle(
                tcm_root=AOT_TCM_ROOT,
                dll_root=AOT_DLL_ROOT,
                manifest_path=MANIFEST_PATH,
                preflight_all=preflight_all,
            )
        logging.info(
            "AOT payload: backends=%s targets=%s modules=%s artifacts=%d bridges=%d",
            ",".join(bundle.backends),
            ",".join(bundle.target_ids),
            ",".join(bundle.modules),
            len(bundle.artifacts),
            len(bundle.bridges),
        )
        command = build_command(bundle)
        logging.info("PyInstaller command: %s", " ".join(command))
        subprocess.run(command, cwd=str(PROJECT_ROOT), check=True)
        logging.info("PyInstaller build completed successfully")
        return 0
    except (FileNotFoundError, ValueError) as error:
        logging.error("Release payload validation failed: %s", error)
        return 2
    except subprocess.CalledProcessError as error:
        logging.error("PyInstaller build failed with exit code %s", error.returncode)
        return int(error.returncode or 1)
    except Exception:
        logging.exception("Unexpected PyInstaller build error")
        return 1
    finally:
        cleanup_aot_bundle(bundle)


if __name__ == "__main__":
    raise SystemExit(build_pyinstaller())

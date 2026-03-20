import subprocess
import os
import sys

def run_command(command, shell=False):
    """Jalankan perintah sistem dan tampilkan outputnya secara real-time."""
    print(f"[Running] {' '.join(command) if isinstance(command, list) else command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=shell,
        universal_newlines=True,
        encoding='utf-8',
        errors='replace'
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    return process.returncode

def get_wsl_path(win_path):
    """Ubah path Windows ke format WSL (/mnt/c/...)"""
    try:
        result = subprocess.run(['wsl', 'wslpath', '-u', win_path], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error converting path: {e}")
        return None

def main():
    print("=== Pixel Refine: Android Build Automator (via WSL) ===")
    
    # 1. Cek apakah WSL terinstall
    try:
        subprocess.run(['wsl', '--status'], capture_output=True, check=True)
    except:
        print("Error: WSL tidak terdeteksi. Silakan install WSL terlebih dahulu.")
        sys.exit(1)

    # 2. Dapatkan path proyek saat ini dalam format WSL
    current_dir = os.path.dirname(os.path.abspath(__file__))
    wsl_dir = get_wsl_path(current_dir)
    
    if not wsl_dir:
        print("Error: Gagal mengkonversi path ke WSL.")
        sys.exit(1)
        
    print(f"WSL Path: {wsl_dir}")

    # 3. Instruksi Build
    # Kita menggunakan 'cd' di WSL dulu, lalu jalankan buildozer
    # --user ditambahkan agar bisa eksekusi buildozer jika diinstall via pip user
    build_cmd = [
        'wsl', 
        'bash', '-c', 
        f'cd "{wsl_dir}" && ~/.local/bin/buildozer android debug'
    ]

    print("\n[INFO] Memulai proses build. Build pertama kali mungkin memakan waktu lama (10-30 menit)")
    print("[INFO] karena Buildozer harus mendownload Android SDK & NDK.\n")

    return_code = run_command(build_cmd)
    
    if return_code == 0:
        print("\n[SUCCESS] Build selesai! Cek folder 'bin/' untuk file APK Anda.")
    else:
        print(f"\n[FAILED] Build gagal dengan exit code {return_code}.")
        print("Tips: Pastikan dependencies sudah terinstall di WSL.")
        print("Gunakan perintah ini di WSL untuk install awal:")
        print("sudo apt update && sudo apt install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0-gstreamer-lite-dev libgstreamer-plugins-base1.0-dev openjdk-17-jdk unzip libncurses5 zip virtualenv")
        print("pip3 install --user buildozer")

if __name__ == "__main__":
    main()

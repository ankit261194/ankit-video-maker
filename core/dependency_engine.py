import os
import sys

# Prevent OpenBLAS / MKL memory allocation errors on Windows
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import subprocess
import importlib

# Essential dependencies mapping: (import_name, pip_package_name)
REQUIRED_PACKAGES = [
    ("customtkinter", "customtkinter"),
    ("edge_tts", "edge-tts"),
    ("imageio_ffmpeg", "imageio-ffmpeg"),
    ("PIL", "pillow"),
    ("google.genai", "google-genai"),
    ("requests", "requests")
]

def install_silently(package_name):
    """
    Installs a Python package silently in the background without user interaction.
    """
    try:
        cmd = [sys.executable, "-m", "pip", "install", package_name, "--quiet", "--no-warn-script-location"]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        return False

def ensure_package(import_name, pip_name=None):
    """
    Dynamic dependency loader. If a package is missing during runtime,
    it automatically installs it silently and returns the loaded module.
    """
    if pip_name is None:
        pip_name = import_name

    try:
        return importlib.import_module(import_name)
    except ImportError:
        print(f"[AVM Engine] Automatically deploying required component: {pip_name}...")
        success = install_silently(pip_name)
        if success:
            try:
                importlib.invalidate_caches()
                return importlib.import_module(import_name)
            except Exception as e:
                print(f"[AVM Engine] Warning: Failed to import {import_name} after install: {e}")
        return None

def verify_and_heal_environment():
    """
    Runs at application startup to verify all core dependencies.
    Silently installs any missing components.
    """
    healed_count = 0
    for imp_name, pkg_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(imp_name)
        except ImportError:
            print(f"[AVM Engine] Installing missing package silently: {pkg_name}")
            if install_silently(pkg_name):
                healed_count += 1

    # Verify FFmpeg binary
    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        if not ffmpeg_bin or not os.path.exists(ffmpeg_bin):
            print("[AVM Engine] Resolving FFmpeg multimedia binary...")
    except Exception:
        pass

    return healed_count

if __name__ == "__main__":
    verify_and_heal_environment()

import subprocess
import os
import sys
import shutil


# =========================
# BASE DIR (EXE SAFE)
# =========================
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(".")


# =========================
# RESOURCE PATH (FOR BUNDLED FILES)
# =========================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# =========================
# PATHS
# =========================
BASE_DIR = get_base_dir()

SLICER_PATH = os.path.join(
    get_base_dir(),
    "prusaslicer",
    "prusa-slicer-console.exe"
)

CONFIG_DIR = os.path.join(BASE_DIR, "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "my_config.ini")

DEFAULT_CONFIG = resource_path("assets/default_config.ini")


# =========================
# ENSURE CONFIG EXISTS
# =========================
def ensure_config():

    # create config folder if missing
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # if config doesn't exist → copy default
    if not os.path.exists(CONFIG_PATH):
        print("⚠ Config not found, creating default...")

        try:
            shutil.copy(DEFAULT_CONFIG, CONFIG_PATH)
            print("✅ Default config created at:", CONFIG_PATH)
        except Exception as e:
            print("❌ Failed to copy default config:", e)


# =========================
# MAIN FUNCTION
# =========================
def run_slicer(flat_files, temp_dir):

    print("\n🌸 Running slicer_runner")

    gcode_files = []

    # ===== CHECK SLICER =====
    if not os.path.exists(SLICER_PATH):
        print("❌ PrusaSlicer not found at:")
        print(SLICER_PATH)
        return []

    # ===== ENSURE CONFIG =====
    ensure_config()

    # ===== VERIFY CONFIG =====
    if not os.path.exists(CONFIG_PATH):
        print("❌ Config still missing after attempt:")
        print(CONFIG_PATH)
        return []

    print("Using slicer:", SLICER_PATH)
    print("Using config:", CONFIG_PATH)

    # ===== LOOP FILES =====
    for i, stl_path in enumerate(flat_files):

        if not os.path.exists(stl_path):
            print(f"❌ Missing STL: {stl_path}")
            continue

        gcode_path = os.path.join(temp_dir, f"part_{i+1}.gcode")

        print(f"\n🔄 Slicing {stl_path}")

        command = [
            SLICER_PATH,
            "--load", CONFIG_PATH,
            "--dont-arrange",
            "--no-ensure-on-bed",
            "--export-gcode",
            stl_path,
            "--output", gcode_path
        ]

        print("CMD:", " ".join(command))

        try:
            result = subprocess.run(command, capture_output=True, text=True)

            print("Return code:", result.returncode)

            if result.stdout:
                print("STDOUT:", result.stdout)

            if result.stderr:
                print("STDERR:", result.stderr)

            if result.returncode == 0 and os.path.exists(gcode_path):
                print(f"✅ Saved: {gcode_path}")
                gcode_files.append(gcode_path)
            else:
                print(f"❌ Failed slicing: {stl_path}")

        except Exception as e:
            print(f"❌ Exception while slicing: {e}")

    print("\n✨ slicer_runner DONE")

    return gcode_files

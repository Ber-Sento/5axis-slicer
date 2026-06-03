import tkinter as tk
from tkinter import ttk
import os
import sys


# ============================================================
# RESOURCE PATH
# ============================================================

def resource_path(relative_path):

    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ============================================================
# CONFIG PATH
# ============================================================

BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")

CONFIG_DIR = os.path.join(BASE_DIR, "config")

CONFIG_PATH = os.path.join(CONFIG_DIR, "my_config.ini")

# ============================================================
# ENSURE CONFIG EXISTS
# ============================================================

def ensure_config_exists():

    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_PATH):

        default_config = resource_path("assets/default_config.ini")

        if os.path.exists(default_config):

            import shutil

            shutil.copy(default_config, CONFIG_PATH)

            print("✅ Default config copied")

        else:
            print("❌ default_config.ini missing")

# ============================================================
# SETTINGS
# ============================================================

SETTINGS = {
    "layer_height": "0.15",
    "fill_density": "5%",
    "fill_pattern": "grid",
    "external_perimeter_speed": "25",
    "perimeter_speed": "45",
    "infill_speed": "80",
    "solid_infill_speed": "80",
    "top_solid_infill_speed": "40",
    "travel_speed": "180",
    "first_layer_speed": "20",
    "perimeter_acceleration": "800",
    "default_acceleration": "1000",
    "filament_max_volumetric_speed": "11",
}


# ============================================================
# INFILL OPTIONS
# ============================================================

INFILL_PATTERNS = [
    "grid",
    "gyroid",
    "rectilinear",
    "cubic",
    "adaptivecubic",
    "honeycomb",
    "lightning"
]


# ============================================================
# LOAD CURRENT VALUES
# ============================================================

def load_current_values():

    values = SETTINGS.copy()

    if not os.path.exists(CONFIG_PATH):
        return values

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        key = key.strip()
        value = value.strip()

        if key in values:
            values[key] = value

    return values


# ============================================================
# SAVE CONFIG
# ============================================================

def save_config(entries, window):

    if not os.path.exists(CONFIG_PATH):
        print("❌ Config file not found")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []

    for line in lines:

        if "=" not in line:
            updated_lines.append(line)
            continue

        key, value = line.split("=", 1)

        key_strip = key.strip()

        if key_strip in entries:

            new_value = entries[key_strip].get().strip()

            updated_lines.append(f"{key_strip} = {new_value}\n")

        else:
            updated_lines.append(line)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print("✅ Config updated")

    window.destroy()


# ============================================================
# OPEN WINDOW
# ============================================================

def open_config_editor(root):
    
    ensure_config_exists()
    
    values = load_current_values()

    window = tk.Toplevel(root)

    window.title("Slicer Settings")
    window.geometry("450x620")
    window.resizable(False, False)

    entries = {}

    row = 0

    # ========================================================
    # TITLE
    # ========================================================

    tk.Label(
        window,
        text="Bernat TA Quick Settings",
        font=("Arial", 14, "bold")
    ).grid(
        row=row,
        column=0,
        columnspan=2,
        pady=15
    )

    row += 1

    # ========================================================
    # CREATE SETTINGS UI
    # ========================================================

    for key, default in values.items():

        # Label
        tk.Label(
            window,
            text=key
        ).grid(
            row=row,
            column=0,
            padx=12,
            pady=6,
            sticky="w"
        )

        # ====================================================
        # INFILL DROPDOWN
        # ====================================================

        if key == "fill_pattern":

            combo = ttk.Combobox(
                window,
                width=25,
                state="readonly",
                values=INFILL_PATTERNS
            )

            combo.set(default)

            combo.grid(
                row=row,
                column=1,
                padx=12,
                pady=6
            )

            entries[key] = combo

        # ====================================================
        # NORMAL ENTRY
        # ====================================================

        else:

            entry = tk.Entry(
                window,
                width=28
            )

            entry.insert(0, default)

            entry.grid(
                row=row,
                column=1,
                padx=12,
                pady=6
            )

            entries[key] = entry

        row += 1

    # ========================================================
    # SAVE BUTTON
    # ========================================================

    tk.Button(
        window,
        text="Save Config",
        command=lambda: save_config(entries, window),
        bg="#4CAF50",
        fg="white",
        width=20,
        height=2
    ).grid(
        row=row,
        column=0,
        columnspan=2,
        pady=25
    )

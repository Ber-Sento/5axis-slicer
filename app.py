import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from stl import mesh
import numpy as np

from pipeline import run_pipeline
from config_editor import open_config_editor


class App:
    def __init__(self, root):

        self.root = root
        self.root.title("5-Axis Slicer")

        self.stl = ""
        self.out = ""

        # ===== FILE SELECT =====
        tk.Button(root, text="Import STL", command=self.pick_stl).pack(pady=5)

        tk.Button(root, text="Select Output Folder", command=self.pick_out).pack(pady=5)

        # ===== CONFIG EDITOR =====
        tk.Button(
            root,
            text="Slicer Settings",
            command=lambda: open_config_editor(root)
        ).pack(pady=5)

        # ===== LAYER HEIGHT =====
        tk.Label(root, text="Layer Height (mm)").pack()

        self.layer_entry = tk.Entry(root)
        self.layer_entry.insert(0, "5")
        self.layer_entry.pack()

        # ===== PIVOT INPUT =====
        tk.Label(root, text="Pivot Y Offset (mm)").pack()

        self.pivot_y_entry = tk.Entry(root)
        self.pivot_y_entry.insert(0, "0")
        self.pivot_y_entry.pack()

        tk.Label(root, text="Pivot Z Offset (mm)").pack()

        self.pivot_z_entry = tk.Entry(root)
        self.pivot_z_entry.insert(0, "0")
        self.pivot_z_entry.pack()

        # ===== START BUTTON =====
        tk.Button(root, text="Start Slicing", command=self.start).pack(pady=10)

        # ===== LOG =====
        self.log_box = tk.Text(root, height=12)
        self.log_box.pack(fill="both", expand=True)

        # ===== PROGRESS =====
        self.progress = tk.DoubleVar()

        self.progress_bar = tk.Scale(
            root,
            variable=self.progress,
            from_=0,
            to=100,
            orient="horizontal"
        )

        self.progress_bar.pack(fill="x")

    # =========================================================
    # LOG
    # =========================================================

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    # =========================================================
    # PROGRESS
    # =========================================================

    def set_progress(self, val):
        self.progress.set(val)
        self.root.update_idletasks()

    # =========================================================
    # STL SIZE CHECK
    # =========================================================

    def validate_stl_size(self, stl_path):

        try:

            your_mesh = mesh.Mesh.from_file(stl_path)

            points = your_mesh.points.reshape(-1, 3)

            x_min = np.min(points[:, 0])
            x_max = np.max(points[:, 0])

            y_min = np.min(points[:, 1])
            y_max = np.max(points[:, 1])

            z_min = np.min(points[:, 2])
            z_max = np.max(points[:, 2])

            width_x = x_max - x_min
            width_y = y_max - y_min
            height_z = z_max - z_min

            # =====================================================
            # CHECK XY RADIUS
            # =====================================================

            max_radius = 0

            for p in points:

                x = p[0]
                y = p[1]

                r = np.sqrt(x**2 + y**2)

                if r > max_radius:
                    max_radius = r

            # =====================================================
            # LOG DIMENSIONS
            # =====================================================

            self.log("========== STL SIZE ==========")

            self.log(f"X Size : {width_x:.2f} mm")
            self.log(f"Y Size : {width_y:.2f} mm")
            self.log(f"Z Size : {height_z:.2f} mm")

            self.log(f"Max XY Radius : {max_radius:.2f} mm")

            # =====================================================
            # LIMIT CHECK
            # =====================================================

            errors = []

            if max_radius > 100:
                errors.append(
                    f"XY radius exceeds printer limit (100 mm)\nCurrent: {max_radius:.2f} mm"
                )

            if z_min < 0:
                errors.append(
                    f"STL goes below Z=0\nLowest Z: {z_min:.2f} mm"
                )

            if z_max > 100:
                errors.append(
                    f"STL exceeds max Z height (100 mm)\nCurrent: {z_max:.2f} mm"
                )

            # =====================================================
            # SHOW WARNING
            # =====================================================

            if errors:

                full_msg = "\n\n".join(errors)

                messagebox.showwarning(
                    "STL Too Large",
                    full_msg
                )

                self.log("⚠ STL exceeds printer limits")

            else:
                self.log("✅ STL fits printer volume")

        except Exception as e:
            self.log(f"STL validation failed: {e}")

    # =========================================================
    # PICK STL
    # =========================================================

    def pick_stl(self):

        self.stl = filedialog.askopenfilename(
            filetypes=[("STL", "*.stl")]
        )

        self.log(f"STL Selected: {self.stl}")

        if self.stl:
            self.validate_stl_size(self.stl)

    # =========================================================
    # PICK OUTPUT
    # =========================================================

    def pick_out(self):

        self.out = filedialog.askdirectory()

        self.log(f"Output Folder: {self.out}")

    # =========================================================
    # START
    # =========================================================

    def start(self):

        try:

            layer = float(self.layer_entry.get())

            pivot_y = float(self.pivot_y_entry.get())
            pivot_z = float(self.pivot_z_entry.get())

            pivot_offset = (pivot_y, pivot_z)

            run_pipeline(
                self.stl,
                self.out,
                layer,
                pivot_offset,
                self.log,
                self.set_progress
            )

        except Exception as e:
            self.log(f"ERROR: {e}")

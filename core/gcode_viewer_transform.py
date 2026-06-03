import re
import numpy as np
import os


# =========================
# PARSE / SET
# =========================
def get_val(line, axis):
    m = re.search(rf'{axis}([-+]?\d*\.?\d+)', line)
    return float(m.group(1)) if m else None


def set_xyz(line, x, y, z):
    line = re.sub(r'X[-+]?\d*\.?\d+', '', line)
    line = re.sub(r'Y[-+]?\d*\.?\d+', '', line)
    line = re.sub(r'Z[-+]?\d*\.?\d+', '', line)
    return line.strip() + f" X{x:.4f} Y{y:.4f} Z{z:.4f}\n"


# =========================
# ROTATION MATRIX (UNCHANGED)
# =========================
def build_rotation(theta_m, psi_m):

    t = np.radians(theta_m)
    p = np.radians(psi_m)

    Ry = np.array([
        [ np.cos(t), 0, np.sin(t)],
        [ 0,         1, 0        ],
        [-np.sin(t), 0, np.cos(t)]
    ])

    Rz = np.array([
        [np.cos(p), -np.sin(p), 0],
        [np.sin(p),  np.cos(p), 0],
        [0, 0, 1]
    ])

    return Rz @ Ry


# =========================
# MAIN FUNCTION
# =========================
def run_viewer_transform(global_gcode_files, planes, temp_dir):

    print("\n🌸 Running gcode_viewer_transform")

    output_files = []

    for i, g_in in enumerate(global_gcode_files):

        if not os.path.exists(g_in):
            print(f"❌ Missing {g_in}")
            continue

        g_out = os.path.join(temp_dir, f"part_{i+1}_viewer.gcode")

        print(f"\n🔄 Processing part {i+1}")

        # =========================
        # GET FROM PLANES
        # =========================
        _, _, _, theta, psi = planes[i]

        # viewer mapping (your working version)
        theta_m = -theta
        psi_m   = psi

        R = build_rotation(theta_m, psi_m)
        R_inv = np.linalg.inv(R)

        print(f"B={theta}, C={psi}")

        with open(g_in) as f:
            lines = f.readlines()

        cx = cy = cz = 0.0
        out = []
        inserted = False

        for line in lines:

            # insert BC once
            if not inserted and (line.startswith("G0") or line.startswith("G1")):
                out.append(f"G1 B{theta:.2f} C{psi:.2f} F2000\n")
                inserted = True

            if line.startswith("G0") or line.startswith("G1"):

                x = get_val(line, 'X')
                y = get_val(line, 'Y')
                z = get_val(line, 'Z')

                if x is not None: cx = x
                if y is not None: cy = y
                if z is not None: cz = z

                p = np.array([cx, cy, cz])

                # GLOBAL → VIEWER
                p_new = R_inv @ p

                line = set_xyz(line, *p_new)

            out.append(line)

        with open(g_out, "w") as f:
            f.writelines(out)

        print(f"✅ Saved: {g_out}")
        output_files.append(g_out)

    print("\n✨ VIEWER transform DONE")

    return output_files

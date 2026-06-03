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
# ROTATION MATRIX
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
# APPLY PIVOT ROTATION
# =========================
def apply_pivot_rotation(p, R_inv, offset):

    # offset = (pivot_y, pivot_z)
    pivot = np.array([0.0, offset[0], offset[1]])

    # move to pivot
    p_shift = p + pivot

    # rotate
    p_rot = R_inv @ p_shift

    # move back
    p_new = p_rot - pivot

    return p_new


# =========================
# CONVERT ONE PART
# =========================
def convert_part(i, theta, psi, offset, input_dir, output_dir):

    g_in  = os.path.join(input_dir, f"part_{i}_global.gcode")
    g_out = os.path.join(output_dir, f"part_{i}_machine.gcode")

    if not os.path.exists(g_in):
        print(f"❌ Missing {g_in}")
        return None

    print(f"\n🔄 Processing part {i}")

    # convert to machine coords
    theta_m = -theta
    psi_m   = -psi

    R = build_rotation(theta_m, psi_m)
    R_inv = np.linalg.inv(R)

    print(f"B={theta}, C={psi}")
    print(f"Pivot offset (Y,Z): {offset}")

    with open(g_in) as f:
        lines = f.readlines()

    cx = cy = cz = 0.0
    out = []
    inserted = False

    for line in lines:

        # insert rotation command once
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

            # APPLY PIVOT ROTATION
            p_new = apply_pivot_rotation(p, R_inv, offset)

            line = set_xyz(line, *p_new)

        out.append(line)

    with open(g_out, "w") as f:
        f.writelines(out)

    print(f"✅ Saved: {g_out}")

    return g_out


# =========================
# PIPELINE FUNCTION
# =========================
def run_machine_transform(global_gcode_files, planes, temp_dir, pivot_offset=(0, 0)):

    print("\n🌸 Running MACHINE transform")

    outputs = []

    for i, gfile in enumerate(global_gcode_files, start=1):

        _, _, _, theta, psi = planes[i-1]

        out = convert_part(
            i=i,
            theta=theta,
            psi=psi,
            offset=pivot_offset,   # 🔥 THIS IS THE KEY
            input_dir=temp_dir,
            output_dir=temp_dir
        )

        if out:
            outputs.append(out)

    print("\n✨ MACHINE transform DONE")
    return outputs

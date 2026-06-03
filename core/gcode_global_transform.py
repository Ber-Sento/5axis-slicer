import numpy as np
import re
import os


# =========================
# LOAD TRANSFORM
# =========================
def load_transform(file):
    FULL = np.load(file)
    return np.linalg.inv(FULL)


# =========================
# TRANSFORM POINT
# =========================
def transform_point(x, y, z, T):
    p = np.array([x, y, z, 1.0])
    p_new = T @ p
    return p_new[:3]


# =========================
# MAIN FUNCTION
# =========================
def run_global_transform(gcode_files, transform_files, temp_dir):

    print("\n🌸 Running gcode_global_transform")

    output_files = []

    for i, gcode_path in enumerate(gcode_files):

        if not os.path.exists(gcode_path):
            print(f"❌ Missing: {gcode_path}")
            continue

        transform_path = transform_files[i]

        if not os.path.exists(transform_path):
            print(f"❌ Missing transform: {transform_path}")
            continue

        output_path = os.path.join(temp_dir, f"part_{i+1}_global.gcode")

        T = load_transform(transform_path)

        current_x = 0.0
        current_y = 0.0
        current_z = 0.0

        with open(gcode_path, 'r') as f:
            lines = f.readlines()

        new_lines = []

        for line in lines:

            if line.startswith("G0") or line.startswith("G1"):

                x_match = re.search(r'X([-+]?[0-9]*\.?[0-9]+)', line)
                y_match = re.search(r'Y([-+]?[0-9]*\.?[0-9]+)', line)
                z_match = re.search(r'Z([-+]?[0-9]*\.?[0-9]+)', line)

                if x_match:
                    current_x = float(x_match.group(1))
                if y_match:
                    current_y = float(y_match.group(1))
                if z_match:
                    current_z = float(z_match.group(1))

                new_x, new_y, new_z = transform_point(
                    current_x, current_y, current_z, T
                )

                line = re.sub(r'X[-+]?[0-9]*\.?[0-9]+', f'X{new_x:.4f}', line)
                line = re.sub(r'Y[-+]?[0-9]*\.?[0-9]+', f'Y{new_y:.4f}', line)
                line = re.sub(r'Z[-+]?[0-9]*\.?[0-9]+', f'Z{new_z:.4f}', line)

                if not z_match:
                    line = line.strip() + f' Z{new_z:.4f}\n'

            new_lines.append(line)

        with open(output_path, 'w') as f:
            f.writelines(new_lines)

        print(f"✅ Saved: {output_path}")
        output_files.append(output_path)

    print("\n✨ gcode_global_transform DONE")

    return output_files

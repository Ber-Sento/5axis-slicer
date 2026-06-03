import re
import os


# =========================
# PARSE B/C
# =========================
def get_val(line, axis):
    m = re.search(rf'{axis}([-+]?\d*\.?\d+)', line)
    return float(m.group(1)) if m else None


# =========================
# FORCE B C ON EVERY LINE
# =========================
def inject_bc(lines):

    B = 0.0
    C = 0.0
    output = []

    for line in lines:

        b = get_val(line, 'B')
        c = get_val(line, 'C')

        if b is not None: B = b
        if c is not None: C = c

        if line.startswith("G0") or line.startswith("G1"):

            line = re.sub(r'B[-+]?\d*\.?\d+', '', line)
            line = re.sub(r'C[-+]?\d*\.?\d+', '', line)

            line = line.strip() + f" B{B:.2f} C{C:.2f}\n"

        output.append(line)

    return output


# =========================
# MERGE CORE
# =========================
def merge_list(file_list, output_path):

    merged = []

    for i, filepath in enumerate(file_list):

        if not os.path.exists(filepath):
            print(f"❌ Missing {filepath}")
            continue

        print(f"🔄 Adding {filepath}")

        with open(filepath) as f:
            lines = f.readlines()

        lines = inject_bc(lines)

        merged.append(f"\n; ===== PART {i+1} =====\n")
        merged.extend(lines)

    with open(output_path, "w") as f:
        f.writelines(merged)

    print(f"\n✅ Saved: {output_path}")


# =========================
# MAIN FUNCTION
# =========================
def run_merge(machine_files, viewer_files, output_dir):

    print("\n🌸 Running merge")

    machine_out = os.path.join(output_dir, "merged_machine.gcode")
    viewer_out  = os.path.join(output_dir, "merged_viewer.gcode")

    print("\n=== MERGING MACHINE ===")
    merge_list(machine_files, machine_out)

    print("\n=== MERGING VIEWER ===")
    merge_list(viewer_files, viewer_out)

    print("\n✨ Merge DONE")

    return machine_out, viewer_out

import numpy as np
import trimesh
import os


# =========================
# THETA + PSI → NORMAL
# =========================
def normal_from_theta_psi(theta_deg, psi_deg):
    theta = np.radians(theta_deg)
    psi = np.radians(psi_deg)

    n = np.array([0, 0, 1])

    Ry = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

    Rz = np.array([
        [np.cos(psi), -np.sin(psi), 0],
        [np.sin(psi),  np.cos(psi), 0],
        [0, 0, 1]
    ])

    normal = Rz @ (Ry @ n)
    return normal / np.linalg.norm(normal)


# =========================
# ALIGN NORMAL TO Z
# =========================
def align_to_z(normal):
    target = np.array([0, 0, 1])

    axis = np.cross(normal, target)
    norm = np.linalg.norm(axis)

    if norm < 1e-6:
        return np.eye(4)

    axis = axis / norm
    angle = np.arccos(np.clip(np.dot(normal, target), -1, 1))

    return trimesh.transformations.rotation_matrix(angle, axis)


# =========================
# MAIN FUNCTION
# =========================
def run_rotate_batch(part_files, planes, temp_dir):

    print("\n🌸 Running rotate_batch")

    output_flat_files = []
    transform_files = []

    for i, part_path in enumerate(part_files):

        print(f"\n--- Part {i+1} ---")

        if not os.path.exists(part_path):
            print(f"❌ Missing {part_path}")
            continue

        mesh = trimesh.load(part_path, force='mesh')
        print(f"Loaded: {part_path}")

        # =========================
        # GET ROTATION FROM PLANES
        # =========================
        _, _, _, theta, psi = planes[i]

        normal = normal_from_theta_psi(theta, psi)

        # =========================
        # STEP 1: ROTATION
        # =========================
        R = align_to_z(normal)

        mesh_rotated = mesh.copy()
        mesh_rotated.apply_transform(R)

        # =========================
        # STEP 2: CENTERING
        # =========================
        min_pt = mesh_rotated.bounds[0]
        max_pt = mesh_rotated.bounds[1]
        center = (min_pt + max_pt) / 2

        T_center = np.eye(4)
        T_center[:3, 3] = -center

        mesh_rotated.apply_transform(T_center)

        # =========================
        # STEP 3: LIFT TO Z >= 0
        # =========================
        min_z = mesh_rotated.bounds[0][2]

        T_z = np.eye(4)
        T_z[2, 3] = -min_z

        mesh_rotated.apply_transform(T_z)

        # =========================
        # STEP 4: MOVE TO BED
        # =========================
        T_bed = np.eye(4)
        T_bed[:3, 3] = [150, 150, 0]

        mesh_rotated.apply_transform(T_bed)

        # =========================
        # FULL TRANSFORM
        # =========================
        FULL = T_bed @ T_z @ T_center @ R

        # =========================
        # SAVE
        # =========================
        flat_path = os.path.join(temp_dir, f"part_{i+1}_flat.stl")
        mat_path  = os.path.join(temp_dir, f"part_{i+1}_transform.npy")

        mesh_rotated.export(flat_path)
        np.save(mat_path, FULL)

        print(f"✅ Saved: {flat_path}")
        print(f"💾 Saved: {mat_path}")

        output_flat_files.append(flat_path)
        transform_files.append(mat_path)

    print("\n✨ rotate_batch DONE")

    return output_flat_files, transform_files

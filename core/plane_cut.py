import numpy as np
import trimesh
import os


# =========================
# VALIDATION
# =========================
def is_valid(m):
    return (
        m is not None and
        isinstance(m, trimesh.Trimesh) and
        len(m.faces) > 0 and
        len(m.vertices) > 0
    )


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
# SAFE SLICE
# =========================
def safe_slice(mesh, origin, normal):
    try:
        m = mesh.slice_plane(plane_origin=origin, plane_normal=normal, cap=True)
        if m is None or len(m.faces) == 0:
            return None
        return m
    except:
        return None


# =========================
# MAIN FUNCTION
# =========================
def run_plane_cut(stl_path, planes, output_dir):

    print("\n🌸 Running plane_cut")

    # =========================
    # LOAD MESH
    # =========================
    mesh = trimesh.load(stl_path, force='mesh')

    mesh.remove_degenerate_faces()
    mesh.remove_duplicate_faces()
    mesh.merge_vertices()

    print("Watertight:", mesh.is_watertight)

    # =========================
    # PREP PLANES
    # =========================
    prepared_planes = []

    for (ox, oy, oz, theta, psi) in planes:
        origin = np.array([ox, oy, oz])
        normal = normal_from_theta_psi(theta, psi)

        prepared_planes.append((oz, origin, normal))

    # sort by Z
    prepared_planes.sort(key=lambda x: x[0])

    # =========================
    # CUTTING
    # =========================
    remaining = mesh
    part_id = 1
    output_files = []

    for z, origin, normal in prepared_planes:

        print(f"\n🔪 Cutting at Z={z}")

        upper = safe_slice(remaining, origin, normal)
        lower = safe_slice(remaining, origin, -normal)

        if is_valid(lower):
            lower.remove_unreferenced_vertices()

            out_path = os.path.join(output_dir, f"part_{part_id}.stl")
            lower.export(out_path)

            print(f"✅ Saved part_{part_id}.stl")

            output_files.append(out_path)
            part_id += 1
        else:
            print("⚠ Lower part invalid, skipped")

        remaining = upper

    # =========================
    # FINAL PART
    # =========================
    if is_valid(remaining):
        remaining.remove_unreferenced_vertices()

        out_path = os.path.join(output_dir, f"part_{part_id}.stl")
        remaining.export(out_path)

        print(f"✅ Saved final part_{part_id}.stl")

        output_files.append(out_path)
    else:
        print("⚠ Final part invalid")

    print("\n✨ plane_cut DONE")

    return output_files

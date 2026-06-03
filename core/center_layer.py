import trimesh
import numpy as np


# =========================
# MAIN FUNCTION
# =========================
def generate_planes_from_stl(stl_path, layer_height=5.0, theta_limit=50):

    print("\n🌸 Running center_layer")

    mesh = trimesh.load(stl_path, force='mesh')

    z_min, z_max = mesh.bounds[:, 2]

    prev_center = None
    prev_theta = 0
    prev_psi = 0

    z = z_min
    planes = []

    last_valid_center = None

    while z <= z_max:
    
        section = mesh.section(
            plane_origin=[0, 0, z],
            plane_normal=[0, 0, 1]
        )

        if section is None or len(section.vertices) == 0:
            z += layer_height
            continue

        points_3D = section.vertices
        min_pt = points_3D.min(axis=0)
        max_pt = points_3D.max(axis=0)
        center = (min_pt + max_pt) / 2

        X, Y = center[0], center[1]

        # =========================
        # ROTATION CALCULATION
        # =========================
        if last_valid_center is None:
            theta = 0
            psi = 0
        else:
            direction = center - last_valid_center
            norm = np.linalg.norm(direction)

            if norm < 1e-6:
                theta = prev_theta
                psi = prev_psi
            else:
                direction = direction / norm
                dx, dy, dz = direction

                psi = np.degrees(np.arctan2(dy, dx))
                if psi < 0:
                    psi += 360

                theta = np.degrees(np.arccos(dz))
                theta = min(theta, theta_limit)

        print(f"Z={z:.2f} → X={X:.2f}, Y={Y:.2f}")
        print(f"Z={z:.2f} → Theta={theta:.2f}, Psi={psi:.2f}")

        planes.append((X, Y, z, theta, psi))

        # update ONLY when valid
        last_valid_center = center
        prev_theta = theta
        prev_psi = psi

        z += layer_height
        
    print("\n✨ center_layer DONE")
    print(f"Generated {len(planes)} planes")

    return planes

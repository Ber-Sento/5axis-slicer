import numpy as np

mat = np.load("part_2_transform.npy")
np.set_printoptions(precision=4, suppress=True)
print(mat)

R = mat[:3, :3]
t = mat[:3, 3]

print("Rotation:\n", R)
print("Translation:\n", t)

inv = np.linalg.inv(mat)
print(inv @ mat)

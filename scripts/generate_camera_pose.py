import numpy as np
import argparse
import os


def unit_vector(vector):
    """ Returns the unit vector of the vector. """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::
        - angle_between((1, 0, 0), (0, 1, 0)): 1.5707963267948966
        - angle_between((1, 0, 0), (1, 0, 0)): 0.0
        - angle_between((1, 0, 0), (-1, 0, 0)): 3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='parser for camera pose generation')
    parser.add_argument('--out_folder', type=str, required=True, default='')
    args = parser.parse_args()

    # `object_x` and `object_y` needs 
    object_x, object_y, object_z = 2.0864, 0.55584, 1.0
    radius = 2.05

    n_samples = 10
    angles = np.linspace(0, 2*np.pi, n_samples+1)

    lines = []

    for i, angle in enumerate(angles[:-1]):
        camera_x = object_x + radius * np.cos(angle)
        camera_y = object_y + radius * np.sin(angle)
        camera_z = 1.616

        # `euler_x` is fixed, so we can use special case that camera and human are aligned along y axis to compute it
        euler_x = angle_between(np.array([0, 0, -1]), np.array([0, radius, object_z-camera_z]))
        euler_y = 0
        # when the object locates at the side of (+)x axis, the computed `euler_z` should take its negative
        euler_z = angle_between(np.array([0, 1, 0]), np.array([object_x-camera_x, object_y-camera_y, 0]))
        euler_z = euler_z if camera_x > object_x else -euler_z

        lines.append("{} {} {} {} {} {}\n".format(camera_x, camera_y, camera_z, euler_x, euler_y, euler_z))

    with open(os.path.join(args.out_folder, 'camera_positions'), 'w') as f:
        f.writelines(lines)

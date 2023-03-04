import blenderproc as bproc
import argparse
import os
import numpy as np
import json


parser = argparse.ArgumentParser()
parser.add_argument("--digital_human_path", help="Path to the digital human folder.")
parser.add_argument("--digital_human_config", help="Path to the digital human configuration.")
parser.add_argument("--camera_param_path", help="Path to the camera parameters (h, w, K) file.")
parser.add_argument("--camera_poses_path", help="Path to the camera poses file.")
parser.add_argument("--output_dir", help="Path to where the data should be saved")
args = parser.parse_args()


bproc.init()


with open(args.camera_param_path, 'r') as file:
    camera_params = json.load(file)

# define the camera resolution
bproc.camera.set_resolution(image_width=camera_params['w'], image_height=camera_params['h'])

# set intrinsics via K matrix
bproc.camera.set_intrinsics_from_K_matrix(
    K=camera_params['K'],
    image_width=camera_params['w'],
    image_height=camera_params['h']
)


# read the camera positions file and convert into homogeneous camera-world transformation
with open(args.camera_poses_path, "r") as f:
    for line in f.readlines():
        line = [float(x) for x in line.split()]
        position, euler_rotation = line[:3], line[3:6]
        matrix_world = bproc.math.build_transformation_mat(position, euler_rotation)
        bproc.camera.add_camera_pose(matrix_world)


# load the synthetic human
loaded_humans = bproc.loader.load_obj(filepath=args.digital_human_path)

with open(args.digital_human_config, 'r') as file:
    human_configs = json.load(file)

# Find human object
human = bproc.filter.one_by_attr(loaded_humans, "name", human_configs['name'])

# Set its location and rotation
human.set_location(np.array([human_configs['offset_x'], human_configs['offset_y'], 0]))


# set all the lights
lights = []
offset = [[2.5, 2.5], [2.5, -2.5], [-2.5, 2.5], [-2.5, -2.5]]
for i in range(4):
    lights.append(bproc.types.Light())
    lights[i].set_type("POINT")
    lights[i].set_location(location=[human_configs['offset_x']+offset[i][0], human_configs['offset_y']+offset[i][1], 2.5])
    lights[i].set_energy(200)


# Also render normals
bproc.renderer.enable_normals_output()
bproc.renderer.enable_distance_output(activate_antialiasing=True)

# render the whole pipeline
data = bproc.renderer.render()

# write the data to a .hdf5 container
bproc.writer.write_hdf5(args.output_dir, data)

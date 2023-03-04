import blenderproc as bproc
import argparse
import os
import numpy as np
import json


parser = argparse.ArgumentParser()
parser.add_argument("--front", help="Path to the 3D front file")
parser.add_argument("--future_folder", help="Path to the 3D Future Model folder.")
parser.add_argument("--front_3D_texture_path", help="Path to the 3D FRONT texture folder.")
parser.add_argument("--camera_param_path", help="Path to the camera parameters (h, w, K) file.")
parser.add_argument("--camera_poses_path", help="Path to the camera poses file.")
parser.add_argument("--output_dir", help="Path to where the data should be saved")
args = parser.parse_args()

if not os.path.exists(args.front) or not os.path.exists(args.future_folder):
    raise Exception("One of the two folders does not exist!")

bproc.init()
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping.csv"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

# set the light bounces
bproc.renderer.set_light_bounces(diffuse_bounces=200, glossy_bounces=200, max_bounces=200,
                                  transmission_bounces=200, transparent_max_bounces=200)

# load the front 3D objects
loaded_objects = bproc.loader.load_front3d(
    json_path=args.front,
    future_model_path=args.future_folder,
    front_3D_texture_path=args.front_3D_texture_path,
    label_mapping=mapping
)


# Init sampler for sampling locations inside the loaded front3D house
point_sampler = bproc.sampler.Front3DPointInRoomSampler(loaded_objects)

# Init bvh tree containing all mesh objects
bvh_tree = bproc.object.create_bvh_tree_multi_objects([o for o in loaded_objects if isinstance(o, bproc.types.MeshObject)])

poses = 0
tries = 0


def check_name(name):
    for category_name in ["chair", "sofa", "table", "bed"]:
        if category_name in name.lower():
            return True
    return False


with open(args.camera_param_path, 'r') as file:
    camera_params = json.load(file)
# define the camera resolution
bproc.camera.set_resolution(image_width=camera_params['w'], image_height=camera_params['h'])
# Set intrinsics via K matrix
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


# Also render normals
bproc.renderer.enable_normals_output()
bproc.renderer.enable_distance_output(activate_antialiasing=True)

# render the whole pipeline
data = bproc.renderer.render()

# write the data to a .hdf5 container
bproc.writer.write_hdf5(args.output_dir, data)

import blenderproc as bproc
import argparse, json, os
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils.camera_utils import write_camera


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera_intri_path', type=str, default='', help='path to the camera intrinsic configuration.')
    parser.add_argument('--camera_extri_path', type=str, default='', help='path to the camera extrinsic configuration.')
    parser.add_argument('--output_path', type=str, default='', help='path to the output folder.')
    parser.add_argument('--is_test', type=bool, default=False)
    args = parser.parse_args()

    
    # read the camera intrinsic configuration
    with open(args.camera_intri_path, 'r') as file:
        camera_params = json.load(file)
    # fetch camera intrinsic and resolution
    image_width, image_height = camera_params['w'], camera_params['h']
    K = np.array(camera_params['K'])


    opengl_camera2worlds = []    
    # read the camera positions file and convert into homogeneous camera-world transformation
    with open(args.camera_extri_path, "r") as f:
        for line in f.readlines():
            line = [float(x) for x in line.split()]
            position, euler_rotation = line[:3], line[3:6]
            # this camera2world matrix is in OpenGL convention
            matrix_world = bproc.math.build_transformation_mat(position, euler_rotation)
            opengl_camera2worlds.append(matrix_world)


    cameras = {}
    opencv_world2cameras = []
    for view in range(len(opengl_camera2worlds)):
        # transform from OpenGL coordinate to OpenCV coordinate
        opencv_camera2world = bproc.math.change_source_coordinate_frame_of_transformation_matrix(opengl_camera2worlds[view], ["X", "-Y", "-Z"])
        # convert from camera2world to world2camera
        opencv_world2camera = np.linalg.inv(opencv_camera2world)
        cameras[f'{view:02d}'] = {
            'K': K,
            'dist': np.zeros((5, 1)),
            'R': opencv_world2camera[:3, :3],
            'T': opencv_world2camera[:3, 3]
        }
        opencv_world2cameras.append(opencv_world2camera)


    # write the processed camera parameters
    print(cameras)
    if not args.is_test:
        write_camera(cameras, args.output_path)
    else:
        np.save(os.path.join(args.output_path, 'render_w2cs_{:03d}.npy'.format(len(opencv_world2cameras))), opencv_world2cameras)

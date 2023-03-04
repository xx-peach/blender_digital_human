import numpy as np
import os, argparse, tqdm
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils.camera_utils import read_camera
from EasyMocap.easymocap.smplmodel import load_model
from EasyMocap.easymocap.mytools import read_json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_folder', type=str, default='', help='path to the original image data')
    args = parser.parse_args()

    # read the camera intrinsics and extrinsics
    intri_path = os.path.join(args.data_folder, 'intri.yml')
    extri_path = os.path.join(args.data_folder, 'extri.yml')
    cameras = read_camera(intri_name=intri_path, extri_name=extri_path)

    # fetch some frame information
    frames = sorted(os.listdir(os.path.join(args.data_folder, 'images', cameras['basenames'][0])))

    K, R, T, D = [], [], [], []
    ims = [{"ims": []} for _ in range(len(frames))]
    for cam_id in cameras['basenames']:
        # fetch and append intrinsic, extrinsic and distortion of the current camera
        K.append(cameras[cam_id]['K'])
        R.append(cameras[cam_id]['R'])
        T.append(cameras[cam_id]['T'] * 1000)           # TODO: special attention
        D.append(cameras[cam_id]['dist'])
        # record image path of all frames recorded by the current camera
        for i, name in enumerate(os.listdir(os.path.join(args.data_folder, 'images', cam_id))):
            new_path = os.path.join('images', cam_id, name.split('/')[-1])
            ims[i]['ims'].append(new_path)

    # write the `easymocap` format annots to the disk
    cams = {'K': K, 'R': R, 'T':T, 'D': D}
    annot = {'cams': cams, 'ims': ims}
    np.save(os.path.join(args.data_folder, 'annots.npy'), annot)


    # generate `motion.npz` used by `phdeform`
    smpl_folder = os.path.join(args.data_folder, 'output-output-smpl-3d', 'smplfull')
    poses, Rh, Th, shapes = [], [], [], []

    for smpl in tqdm.tqdm(sorted(os.listdir(smpl_folder))):
        smpl_params = read_json(os.path.join(smpl_folder, smpl))['annots'][0]
        poses.append(smpl_params['poses'][0])
        shapes.append(smpl_params['shapes'][0])
        Rh.append(smpl_params['Rh'][0])
        Th.append(smpl_params['Th'][0])

    motion = {
        'poses': np.array(poses).astype(np.float32),
        'Rh': np.array(Rh).astype(np.float32),
        'Th': np.array(Th).astype(np.float32),
        'shapes': np.array(shapes).astype(np.float32)
    }
    np.savez(os.path.join(args.data_folder, "motion.npz"), **motion)

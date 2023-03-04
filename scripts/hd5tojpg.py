import numpy as np
import h5py, os, cv2, argparse
import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='parser for hdf5tojpg')
    parser.add_argument('--raw_folder', type=str, required=True, default='')
    parser.add_argument('--out_folder', type=str, required=True, default='')
    args = parser.parse_args()

    frame_names = sorted(os.listdir(args.raw_folder))
    frame_count = len(frame_names)
    os.makedirs(args.out_folder, exist_ok=True)

    for frame in tqdm.tqdm(frame_names):
        hdf_file_path = os.path.join(args.raw_folder, frame)
        jpg_file_path = os.path.join(args.out_folder, frame[:-5]+'.jpg')

        with h5py.File(hdf_file_path, 'r') as file:
            cv2.imwrite(jpg_file_path, np.array(file['colors'])[..., ::-1])

    print(f'all {frame_count} translation finish.')

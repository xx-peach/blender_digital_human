import os, argparse
from PIL import Image
import imageio.v2 as imageio
import numpy as np
import tqdm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--nb_rendered_human_path', type=str, default='')
    parser.add_argument('--blender_rendered_env_path', type=str, default='')
    parser.add_argument('--frame_index', type=int, default=11)
    parser.add_argument('--output_folder', type=str, default='')
    args = parser.parse_args()

    # read in the background images rendered by blender
    backgrounds = []
    for i in range(len(os.listdir(args.blender_rendered_env_path))):
        background = np.array(Image.open(os.path.join(args.blender_rendered_env_path, f'{i}.jpg')))
        backgrounds.append(background)

    # read in the foreground human images rendered by neuralbody,
    # and generate the human mask at the same time
    foregrounds, masks = [], []
    for i in range(len(os.listdir(os.path.join(args.nb_rendered_human_path, f'frame_{args.frame_index:04d}/rendering')))):
        foreground = np.array(Image.open(os.path.join(args.nb_rendered_human_path, f'frame_{args.frame_index:04d}/rendering', f'{i:04d}.png')).convert('RGB'))
        # # foreground image erosion
        # kernel = np.ones((10, 10), np.uint8)
        # foreground = cv2.erode(foreground, kernel)
        mask = foreground.sum(axis=-1) > 5
        foregrounds.append(foreground)
        masks.append(mask)

    # generate the output images
    output_path = os.path.join(args.output_folder, f'frame_{args.frame_index:02d}')
    os.makedirs(f'{output_path}/images', exist_ok=True)
    for i in tqdm.tqdm(range(len(backgrounds))):
        result = (masks[i][..., None] * foregrounds[i] + (1-masks[i])[..., None] * backgrounds[i]).astype(np.uint8)
        imageio.imwrite(os.path.join(output_path, f'images/{i:03d}.jpg'), result)

    # generate the output video
    result_str = f'"{output_path}/images/*.jpg"'
    cmd = [
        '/usr/bin/ffmpeg',
        '-framerate', 30,
        '-f', 'image2',
        '-pattern_type', 'glob',
        '-y',
        '-r', 30,
        '-i', result_str,
        '-c:v', 'libx264',
        '-crf', '17',
        '-pix_fmt', 'yuv420p',
        '-vf', '"pad=ceil(iw/2)*2:ceil(ih/2)*2"',
        os.path.join(output_path, 'video.mp4'),
    ]
    os.system(' '.join(list(map(str, cmd))))

import os, argparse
from PIL import Image
import imageio.v2 as imageio
import numpy as np
import tqdm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--nb_rendered_human_path', type=str, default='')
    parser.add_argument('--blender_rendered_env_path', type=str, default='')
    parser.add_argument('--n_frames', type=int, default=30)
    parser.add_argument('--render_view', type=int, default=-1, help='render all test views if -1')
    parser.add_argument('--output_folder', type=str, default='')
    args = parser.parse_args()

    # read in the background images rendered by blender
    backgrounds = []
    interval = len(os.listdir(args.blender_rendered_env_path)) // args.n_frames
    for i in range(0, len(os.listdir(args.blender_rendered_env_path)), interval):
        view_idx = args.render_view * interval if args.render_view != -1 else i
        background = np.array(Image.open(os.path.join(args.blender_rendered_env_path, f'{view_idx}.jpg')))
        backgrounds.append(background)

    # read in the foreground human images rendered by neuralbody,
    # and generate the human mask at the same time
    foregrounds, masks = [], []
    for i in range(args.n_frames):
        view_idx = args.render_view if args.render_view != -1 else i
        foreground = np.array(Image.open(os.path.join(args.nb_rendered_human_path, f'rendering', f'{i+1:03d}_{view_idx:03d}.png')).convert('RGB'))
        mask = foreground.sum(axis=-1) > 5
        foregrounds.append(foreground)
        masks.append(mask)

    # define and create the output folder
    if args.render_view == -1:
        output_path = os.path.join(args.output_folder, f'pose_sequence/circle')
    else:
        output_path = os.path.join(args.output_folder, f'pose_sequence/fixed_view_{args.render_view:02d}')
    
    if os.path.exists(output_path):
        os.system(f'rm -rf {output_path}/images')
    os.makedirs(f'{output_path}/images', exist_ok=True)

    # generate the output images
    for i in tqdm.tqdm(range(len(backgrounds))):
        result = (masks[i][..., None] * foregrounds[i] + (1-masks[i])[..., None] * backgrounds[i]).astype(np.uint8)
        imageio.imwrite(os.path.join(output_path, f'images/{i:03d}.jpg'), result)

    # generate the output video
    fps = 10
    result_str = f'"{output_path}/images/*.jpg"'
    cmd = [
        '/usr/bin/ffmpeg',
        '-framerate', fps,
        '-f', 'image2',
        '-pattern_type', 'glob',
        '-y',
        '-r', fps,
        '-i', result_str,
        '-c:v', 'libx264',
        '-crf', '17',
        '-pix_fmt', 'yuv420p',
        '-vf', '"pad=ceil(iw/2)*2:ceil(ih/2)*2"',
        os.path.join(output_path, 'video.mp4'),
    ]
    os.system(' '.join(list(map(str, cmd))))

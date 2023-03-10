# blender_digital_human

here is a demo of blendering digital human `nathan` into a `3d-front` environment, it shows 120 novel view results of frame 11 (the flicker around 1 second is because the corresponding novel camera position collides with walls, I may need to adjust the camera surrounding radius and generate new camera poses), the left one is the ground truth result rendered by `blender`:

<img src="https://github.com/xx-peach/blender_digital_human/blob/main/demo/ground_truth_frame_11.gif" alt="ground_truth" style="zoom:175%;"> <img src="https://github.com/xx-peach/blender_digital_human/blob/main/demo/novel_views_frame_11.gif" alt="predicted" style="zoom:175%;">

and I show two fixed view pose sequence results and one pose sequence result where camera and human both moves below:

<img src="https://github.com/xx-peach/blender_digital_human/blob/main/demo/pose_sequence_view_05.gif" alt="ground_truth" style="zoom:175%;"> <img src="https://github.com/xx-peach/blender_digital_human/blob/main/demo/pose_sequence_view_20.gif" alt="ground_truth" style="zoom:175%;">

<img src="https://github.com/xx-peach/blender_digital_human/blob/main/demo/pose_sequence_circle.gif" alt="ground_truth" style="">

## Installtion

```shell
# create the conda env first
conda create -n easyvv python=3.9 -y
conda activate easyvv

# install `pytorch3d` first, https://github.com/facebookresearch/pytorch3d/blob/main/INSTALL.md
conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3 -c pytorch -y
conda install -c fvcore -c iopath -c conda-forge fvcore iopath -y
conda install pytorch3d -c pytorch3d -y

# install `easyvv` dependences
cat enviroments/requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install

# need to use EasyMocap to generate the datasets
git clone https://github.com/zju3dv/EasyMocap.git

# install `easymocap` dependences
pip3 install -r ./EasyMocap/requirements.txt
pip3 install -r ./EasyMocap/requirements_neuralbody.txt
python3 ./EasyMocap/setup.py develop

# install `blenderproc` dependences
pip3 install blenderproc

# install other useful tools
pip3 install nvitop
```

## Usage

1. use blender to (1) choose a suitable (has enough space to place the human and a set of cameras, I chose `ffe76c93` in this demo) 3d-front layout, and (2) manually place the human in a suitable position and record the `[x, y, z]` coordinate in blender, (3) place the camera in a suitable place and change the camera intrinsic parameter if you want, or just use the default value defined in the first block of `process.ipynb`, and compute the `xy` plane distance (radius) between the camera and human which will be used to generate a circle of surrounding camera poses in the following procedures:

   ```shell
   # run the second block of `process.ipynb` to generate the default camera intrinsic

   # use the `debug` mode provided by `blenderproc v2`, which will open blender gui
   blenderproc debug human_env_visualizer.py \
       --front {PATH_TO_3D-Front-Json-File} \
       --future_folder {PATH_TO_3D-Future} \
       --front_3D_texture_path {PATH_TO_3D-Front-texture} \
       --digital_human_path {PATH_TO_Digital_Human_OBJ-File} \
       --digital_human_config {PATH_TO_Digital_Human_Config} \
       --camera_param_path {PATH_TO_Camera_Params} \
       --camera_poses_path {PATH_TO_Camera_Poses} \
       --output_dir {Output_PATH}/hdf5
   ```

   the eight arguments afterwards are used by  `human_env_blend_visualizer.py` file:

   + `front`: path to the specific 3D-Front json file which you choose;
   + `future_folder`: path to the folder where all 3D-Future objects are stored;
   + `front_3D_texture_path`: path to the folder where all 3D-Front textures are stored;
   + `digital_human_path`: path to a specific frame `.obj` file of a digital human;
   + `digital_human_config`: path to the config of the digital human, which includes its object name and `x`, `y` position, you can **randomly choose one for the `debug` mode** since it's decided after the first process;
   + `camera_param_path`: path to the camera parameter file, which includes camera reoslution and intrinsic, you can generate it using the second block in `process.ipynb`;
   + `camera_poses_path`: path to the camera poses file, your can **randomly choose one for the `debug` mode** since it's decided after the first process;
   + `output_dir`: path to the output directory which contains the `.hdf5` format outputs;

   there will be no output after this step, what you need to do is to determine the human position, camera surrounding radius and possibly camera intrinsics.
2. generate the digital human config and camera poses after you record the human position and camera surrounding radius by:

   ```shell
   # use the third block of `process.ipynb` to generate the digital human config

   # use the `scripts/generate_camera_pose.py` to generate the camera poses
   python ./scripts/generate_camera_pose.py \
       --is_test False \
       --n_views 10 \
       --out_folder ./configs
   ```

   the three arguments afterwards are used by  `generate_camera_pose.py` file:

   + `is_test`: `True` if you want to generate poses for testing/rendering, and the output camera poses file will have some postfix like `_test_{n_views}`, `False` if you just want training poses;
   + `n_views`: int type, controls the number of poses you want to generate;
   + `out_folder`: str type, the root folder of the outputs;

   the setting I used in this demo is `--n_views 10` for training, and `--n_views 120` for testing, you can see the outputs in `./configs/` folder, namely `configs/camera_parameters.json` and `configs/camera_positions{...}`. note that all these output configs generated are used for `blenderproc`, we'll generate specific `easymocap` format data later;
3. use `blenderproc` api to render the re-positioned digital human only (without the 3d-front background), it is the raw image + mask data for `neuralbody`, all the commands are listed in `scripts/render_human_only.sh`:

   ```shell
   # you can render the digital human simply by
   # the output will be saved at `./data/synthetic_human/{human}`
   ./scripts/render_human_only.sh
   ```

   the raw data which includes images and masks will be saved at `./data/synthetic_human/{human}`, I dub it here as `DATA_FOLDER`.
4. now since we have the raw training data, we need to convert it to the `neuralbody` format, which includes (1) camera intrinsic and extrinsic annots, (2) `smpl` human body parameters (shapes, poses), you can follow the instructions, first convert the camera parameter format:

   ```shell
   # generate easymocap format camera parameters, it is actually a middle format
   # the output will be saved at `DATA_FOLDER/intri.yml` and `DATA_FOLDER/extri.yml`
   blenderproc run ./scripts/generate_camera_params.py \
       --camera_intri_path ./configs/camera_parameters.json \
       --camera_extri_path ./configs/camera_positions{...} \
       --output_path {DATA_FOLDER} \
       --is_test False
   ```

   + `camera_intri_path`: the input blender format camera intrinsic path;
   + `camera_extri_path`: the input blender format camera extrinsic path;
   + `output_path`: the output path, namely `DATA_FOLDER`;
   + `is_test`: `True` if for training, `False` for testing/rendering, and will not generate the `intri.yml` and `extra.yml`, but `render_w2cs_{n_view}.npy` instead, which will be used by `neuralbody` when rendering;

   then, prepare the dataset that can be used by `neuralbody`:

   ```shell
   # etract keypoints from the raw rendered images, you can see
   # https://chingswy.github.io/easymocap-public-doc/quickstart/prepare_mocap.html
   # for more detal
   cd ./EasyMocap
   python3 apps/preprocess/extract_keypoints.py {DATA_FOLDER} --mode mp-holistic
   ```

   + `{DATA_FOLDER}`: path to the `blenderproc` rendered data, NOTE, this path must be absolute path or you will get error as https://github.com/zju3dv/EasyMocap/issues/225;
   + `mode`: I choose `mp-holistic` model here because `openpose` is difficult to install and may fail to produce the right result (as in my experiments);

   after you have extracted keypoints, you can run easymocap to generate `smpl` parameters:

   ```shell
   # compute the smpl parameters
   python3 apps/demo/mocap.py {DATA_ROOT} --mode smplh-3d --ranges 0 31 1
   ```

   finally, use the script I provided to generate `annots.npy` and `motion.npy` needed by `neuralbody` (xuzhen's version):

   ```shell
   cd ..
   # generate `annots.py` and `motion.py` used by `phdeform` version `neuralbody`
   python3 scripts/generate_annots_motion.py --data_folder {DATA_FOLDER}
   ```

   now, we have `annots.npy` and `motion.npy` under `DATA_FOLDER`.
5. train a `neuralbody` model and render test view results, you can generate the test camera poses using commands list in procedure 2, 4, remember to set `is_test=True`. Since `phdeform` is now private now, I don't provide training/testing commands here.
6. now you have the `neuralbody` rendered human, what you need is `blenderproc` rendered environment, you can get it by:

   ```shell
   # use blenderproc to render test view environments only
   blenderproc run env_only_renderer.py \
       --front {PATH_TO_3D-Front-Json-File} \
       --future_folder {PATH_TO_3D-Future} \
       --front_3D_texture_path {PATH_TO_3D-Front-texture} \
       --digital_human_path {PATH_TO_Digital_Human_OBJ-File} \
       --digital_human_config {PATH_TO_Digital_Human_Config} \
       --camera_param_path {PATH_TO_Camera_Params} \
       --camera_poses_path {PATH_TO_Camera_Poses} \
       --output_dir {Output_PATH}/hdf5

   # convert the raw `.hdf5` output to `.jpg` images
   python3 ./scripts/hd5tojpg.py \
   		--raw_folder {Output_PATH}/hdf5 \
   		--out_folder {Output_PATH}/images
   ```
7. finally, you can blender the `neuralbody` rendered digital human and `blenderproc` rendered environment together, you can generate the novel view visualization by:

   ```shell
   # novel view visualization, namely a fixed human frame, but a moving camera
   python3 ./scripts/demo_visualizer.py \
   		--nb_rendered_human_path {PATH_TO_NB_Rendered_Human} \
   		--blender_rendered_env_path {PATH_TO_blenderproc_Rendered_Env} \
   		--frame_index 11 \
   		--output_folder {Output_PATH}
   ```

   or, you can generate the pose sequence visualization, fixed camera or moving camera by:

   ```shell
   # pose sequence visualization, namely a moving human
   python3 ./scripts/pose_visualizer.py \
   		--nb_rendered_human_path {PATH_TO_NB_Rendered_Human} \
   		--blender_rendered_env_path {PATH_TO_blenderproc_Rendered_Env} \
   		--n_frames 30 \
   		--render_view 20 \
   		--output_folder {Output_PATH}
   ```

   + `render_view`: render a moving camera if `render_view=-1`, or a specific fixed view if `>0`;

You can find and modify all the instructions list above in `command.ipynb`, enjoy.

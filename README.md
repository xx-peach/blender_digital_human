# blender_digital_human

here is a demo of blendering digital human `nathan` into a `3d-front` environment, it shows 120 novel view results of frame 11 (the flicker around 1 second is because the corresponding novel camera position collides with walls, I may need to adjust the camera surrounding radius and generate new camera poses), left is the ground truth result rendered by `blender`:

<img src="https://github.com/xx-peach/blender_digital_human/blob/main/demo/ground_truth_frame_11.gif" alt="ground_truth" style="">	                                		<img src="https://github.com/xx-peach/blender_digital_human/blob/main/demo/novel_views_frame_11.gif" alt="ground_truth" style="">

and this is the pose sequence result where camera and human both moves:

<img src="https://github.com/xx-peach/blender_digital_human/blob/main/demo/pose_sequence.gif" alt="ground_truth" style="">

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

1. use blender to choose a suitable (has enough space to place the human and a set of cameras, I chose `ffe76c93` in this demo) 3d-front layout, and manually place the human in a suitable position and record the `[x, y, z]` coordinate in blender:

   ```shell
   # use the `debug` mode provided by `blenderproc v2`, which will open blender gui
   blenderproc debug human_env_blend_visualizer.py \
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
2. generate the digital human config and camera poses after you record the human position and surrounding camera radius

   ```shell
   # use the **third** block of `process.ipynb` to generate the digital human config

   # use the `scripts/generate_camera_pose.py` to generate the camera poses
   python ./scripts/generate_camera_pose.py \
       --is_test False \
       --n_views 10 \
       --out_folder ./configs
   ```
   the setting I used in this demo is `--n_views 10` for training, and `--n_views 120` for testing, you can see the outputs in `./configs/` folder, note that all these output configs generated are used for `blenderproc`, we'll generate specific `easymocap` format data later;
3. use `blenderproc` api to render the re-positioned digital human only (without the 3d-front background), it's the raw image + mask data for `neuralbody`, all the commands are listed in `scripts/render_human_only.sh`:

   ```shell
   # you can render the digital human simply by
   ./scripts/render_human_only.sh
   ```
   the raw data will be saved at `data/synthetic_human/{human}`.
4.

# blender_digital_human

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

import modal
import subprocess

app = modal.App(
    name="kohya_ss", 
    image = (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("git",
                     "wget",
                     "cmake",
        )
        .pip_install(
            "dadaptation==3.1",
            "diffusers[torch]==0.17.1",
            "easygui==0.98.3",
            "einops==0.6.0",
            "fairscale==0.4.13",
            "ftfy==6.1.1", 
            "gradio==3.36.1",
            "huggingface-hub==0.14.1",
            "lion-pytorch==0.0.6",
            "lycoris_lora==1.8.0.dev6",
            "open-clip-torch==2.20.0",
            "prodigyopt==1.0",
            "pytorch-lightning==1.9.0",
            "safetensors==0.3.1",
            "timm==0.6.12",
            "tk==0.1.0",
            "transformers==4.30.2",
            "voluptuous==0.13.1",
            "wandb==0.15.0",
            "xformers==0.0.20",
            "omegaconf",
        )
        .run_commands(
            "cd /content && git clone -b 0.41.0 https://github.com/TimDettmers/bitsandbytes",
            "cd /content/bitsandbytes && CUDA_VERSION=118 make cuda11x",
            "cd /content/bitsandbytes && python setup.py install",
            
        )
        .run_commands(
            "cd /content && git clone -b v1.0 https://github.com/camenduru/kohya_ss",
# %cd /content/kohya_ss

        )
    )
)
volume = modal.Volume.from_name("kohya-storage", create_if_missing=True)

@app.function(
        volumes = {"/root/content": volume},
        gpu = "T4",
        allow_concurrent_inputs = 100,
        concurrency_limit = 1,
        keep_warm = 1,
        timeout = 6000,
        )
@modal.web_server(8080, startup_timeout = 1000)
def web():
    start_kohya()

def start_kohya():
    start_cmd = "cd /content/kohya_ss && python kohya_gui.py --share --headless"
    subprocess.run(start_cmd, shell=True, check=True)

# Commented out IPython magic to ensure Python compatibility.
#@title Train with Kohya's Stable Diffusion Trainers
# %cd /content

#from google.colab import drive
#drive.mount('/content/drive')

!pip install dadaptation==3.1 diffusers[torch]==0.17.1 easygui==0.98.3 einops==0.6.0 fairscale==0.4.13 ftfy==6.1.1 gradio==3.36.1 huggingface-hub==0.14.1
!pip install lion-pytorch==0.0.6 lycoris_lora==1.8.0.dev6 open-clip-torch==2.20.0 prodigyopt==1.0 pytorch-lightning==1.9.0 safetensors==0.3.1 timm==0.6.12
!pip install tk==0.1.0 transformers==4.30.2 voluptuous==0.13.1 wandb==0.15.0 xformers==0.0.20 omegaconf

# %cd /content
!git clone -b 0.41.0 https://github.com/TimDettmers/bitsandbytes
# %cd /content/bitsandbytes
!CUDA_VERSION=118 make cuda11x
!python setup.py install

# %cd /content
!git clone -b v1.0 https://github.com/camenduru/kohya_ss
# %cd /content/kohya_ss

!python kohya_gui.py --share --headless

#@title Convert Safetensors to Diffusers
from_safetensors_url = '' #@param {type:"string"}
!wget -q https://raw.githubusercontent.com/huggingface/diffusers/v0.17.1/scripts/convert_original_stable_diffusion_to_diffusers.py
!wget {from_safetensors_url} -O /content/model.safetensors
!python3 convert_original_stable_diffusion_to_diffusers.py --half --from_safetensors --checkpoint_path model.safetensors --dump_path /content/model

# Commented out IPython magic to ensure Python compatibility.
#@title Test with WebUI

# %cd /content

# %env TF_CPP_MIN_LOG_LEVEL=1

!apt -y update -qq
!wget https://github.com/camenduru/gperftools/releases/download/v1.0/libtcmalloc_minimal.so.4 -O /content/libtcmalloc_minimal.so.4
# %env LD_PRELOAD=/content/libtcmalloc_minimal.so.4

!apt -y install -qq aria2 libcairo2-dev pkg-config python3-dev
!pip install -q xformers==0.0.20 triton==2.0.0 -U

!git clone -b v2.5 https://dagshub.com/camenduru/ui
!git clone https://github.com/camenduru/tunnels /content/ui/extensions/tunnels
# %cd /content/ui

model = '/content/train/model/last.safetensors' #@param {type:"string"}
!cp {model} /content/ui/models/Stable-diffusion

!sed -i -e '''/from modules import launch_utils/a\import os''' /content/ui/launch.py
!sed -i -e '''/        prepare_environment()/a\        os.system\(f\"""sed -i -e ''\"s/dict()))/dict())).cuda()/g\"'' /content/ui/repositories/stable-diffusion-stability-ai/ldm/util.py""")''' /content/ui/launch.py
!sed -i -e 's/\["sd_model_checkpoint"\]/\["sd_model_checkpoint","sd_vae","CLIP_stop_at_last_layers"\]/g' /content/ui/modules/shared.py

!python launch.py --listen --xformers --enable-insecure-extension-access --theme dark --gradio-queue --multiple

#@title Push to HF.co

import os
from huggingface_hub import create_repo, upload_folder

hf_token = 'HF_WRITE_TOKEN' #@param {type:"string"}
repo_id = 'username/reponame' #@param {type:"string"}
commit_message = '\u2764' #@param {type:"string"}
create_repo(repo_id, private=True, token=hf_token)
model_path = '/content/train/model' #@param {type:"string"}
upload_folder(folder_path=f'{model_path}', path_in_repo='', repo_id=repo_id, commit_message=commit_message, token=hf_token)

#@title Push to DagsHub.com

!pip -q install dagshub
from dagshub.upload import Repo, create_repo

repo_id = 'reponame' #@param {type:"string"}
org_name = 'orgname' #@param {type:"string"}
commit_message = '\u2764' #@param {type:"string"}
create_repo(f"{repo_id}", org_name=f"{org_name}")
repo = Repo(f"{org_name}", f"{repo_id}")
model_path = '/content/train/model' #@param {type:"string"}
repo.upload("/content/models", remote_path="data", commit_message=f"{commit_message}", force=True)

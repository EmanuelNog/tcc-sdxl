# %%
# !! {"metadata":{
# !!   "id":"cc-imports"
# !! }}

#<cc-imports>

import os
import subprocess

# %%
# !! {"metadata":{
# !!   "id": "NrgcDwZxgDOe"
# !! }}

import modal

app = modal.App(name="kohya_ss", image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git",
                 "wget",
                 "cmake",
                 )
    ))
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



#@title Train with Kohya's Stable Diffusion Trainers
os.chdir('/content') #<cc-cm>

#drive.mount('/content/drive')

sub_p_res = subprocess.run(['pip', 'install', 'dadaptation==3.1', 'diffusers[torch]==0.17.1', 'easygui==0.98.3', 'einops==0.6.0', 'fairscale==0.4.13', 'ftfy==6.1.1', 'gradio==3.36.1', 'huggingface-hub==0.14.1'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['pip', 'install', 'lion-pytorch==0.0.6', 'lycoris_lora==1.8.0.dev6', 'open-clip-torch==2.20.0', 'prodigyopt==1.0', 'pytorch-lightning==1.9.0', 'safetensors==0.3.1', 'timm==0.6.12'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['pip', 'install', 'tk==0.1.0', 'transformers==4.30.2', 'voluptuous==0.13.1', 'wandb==0.15.0', 'xformers==0.0.20', 'omegaconf'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>

os.chdir('/content') #<cc-cm>
sub_p_res = subprocess.run(['git', 'clone', '-b', '0.41.0', 'https://github.com/TimDettmers/bitsandbytes'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
os.chdir('/content/bitsandbytes') #<cc-cm>
sub_p_res = subprocess.run(['CUDA_VERSION=118', 'make', 'cuda11x'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['python', 'setup.py', 'install'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>

os.chdir('/content') #<cc-cm>
sub_p_res = subprocess.run(['git', 'clone', '-b', 'v1.0', 'https://github.com/camenduru/kohya_ss'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
os.chdir('/content/kohya_ss') #<cc-cm>

sub_p_res = subprocess.run(['python', 'kohya_gui.py', '--share', '--headles'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>


# %%
# !! {"metadata":{
# !!   "id": "IxIdNsrO-fWd"
# !! }}
#@title Convert Safetensors to Diffusers
from_safetensors_url = '' #@param {type:"string"}
sub_p_res = subprocess.run(['wget', '-q', 'https://raw.githubusercontent.com/huggingface/diffusers/v0.17.1/scripts/convert_original_stable_diffusion_to_diffusers.py'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['wget', '{from_safetensors_url}', '-O', '/content/model.safetensors'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['python3', 'convert_original_stable_diffusion_to_diffusers.py', '--half', '--from_safetensors', '--checkpoint_path', 'model.safetensors', '--dump_path', '/content/mode'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>


# %%
# !! {"metadata":{
# !!   "id": "r9xWHPkW-fWf"
# !! }}
#@title Test with WebUI

os.chdir('/content') #<cc-cm>

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' #<cc-cm>

sub_p_res = subprocess.run(['apt', '-y', 'update', '-qq'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['wget', 'https://github.com/camenduru/gperftools/releases/download/v1.0/libtcmalloc_minimal.so.4', '-O', '/content/libtcmalloc_minimal.so.4'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
os.environ['LD_PRELOAD'] = '/content/libtcmalloc_minimal.so.4' #<cc-cm>

sub_p_res = subprocess.run(['apt', '-y', 'install', '-qq', 'aria2', 'libcairo2-dev', 'pkg-config', 'python3-dev'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['pip', 'install', '-q', 'xformers==0.0.20', 'triton==2.0.0', '-U'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>

sub_p_res = subprocess.run(['git', 'clone', '-b', 'v2.5', 'https://dagshub.com/camenduru/ui'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['git', 'clone', 'https://github.com/camenduru/tunnels', '/content/ui/extensions/tunnels'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
os.chdir('/content/ui') #<cc-cm>

model = '/content/train/model/last.safetensors' #@param {type:"string"}
sub_p_res = subprocess.run(['cp', '{model}', '/content/ui/models/Stable-diffusion'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>

sub_p_res = subprocess.run(['sed', '-i', '-e', "'''/from", 'modules', 'import', 'launch_utils/a\\import', "os'''", '/content/ui/launch.py'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['sed', '-i', '-e', "'''/", '', '', '', '', '', '', '', 'prepare_environment()/a\\', '', '', '', '', '', '', '', 'os.system\\(f\\"""sed', '-i', '-e', '\'\'\\"s/dict()))/dict())).cuda()/g\\"\'\'', '/content/ui/repositories/stable-diffusion-stability-ai/ldm/util.py""")\'\'\'', '/content/ui/launch.py'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>
sub_p_res = subprocess.run(['sed', '-i', '-e', '\'s/\\["sd_model_checkpoint"\\]/\\["sd_model_checkpoint","sd_vae","CLIP_stop_at_last_layers"\\]/g\'', '/content/ui/modules/shared.py'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>

sub_p_res = subprocess.run(['python', 'launch.py', '--listen', '--xformers', '--enable-insecure-extension-access', '--theme', 'dark', '--gradio-queue', '--multipl'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
print(sub_p_res) #<cc-cm>


# %%
# !! {"metadata":{
# !!   "id": "1dU9t3d_-fWh"
# !! }}
#@title Push to HF.co

#import os
#from huggingface_hub import create_repo, upload_folder
#
#hf_token = 'HF_WRITE_TOKEN' #@param {type:"string"}
#repo_id = 'username/reponame' #@param {type:"string"}
#commit_message = '\u2764' #@param {type:"string"}
#create_repo(repo_id, private=True, token=hf_token)
#model_path = '/content/train/model' #@param {type:"string"}
#upload_folder(folder_path=f'{model_path}', path_in_repo='', repo_id=repo_id, commit_message=commit_message, token=hf_token)

# %%
# !! {"metadata":{
# !!   "id": "MzyrUayz-fWh"
# !! }}
#@title Push to DagsHub.com

#sub_p_res = subprocess.run(['pip', '-q', 'install', 'dagshub'], stdout=subprocess.PIPE).stdout.decode('utf-8') #<cc-cm>
#print(sub_p_res) #<cc-cm>
#from dagshub.upload import Repo, create_repo
#
#repo_id = 'reponame' #@param {type:"string"}
#org_name = 'orgname' #@param {type:"string"}
#commit_message = '\u2764' #@param {type:"string"}
#create_repo(f"{repo_id}", org_name=f"{org_name}")
#repo = Repo(f"{org_name}", f"{repo_id}")
#model_path = '/content/train/model' #@param {type:"string"}
#repo.upload("/content/models", remote_path="data", commit_message=f"{commit_message}", force=True)

# %%
# !! {"main_metadata":{
# !!   "accelerator": "GPU",
# !!   "colab": {
# !!     "gpuType": "T4",
# !!     "provenance": []
# !!   },
# !!   "kernelspec": {
# !!     "display_name": "Python 3",
# !!     "name": "python3"
# !!   },
# !!   "language_info": {
# !!     "name": "python"
# !!   }
# !! }}

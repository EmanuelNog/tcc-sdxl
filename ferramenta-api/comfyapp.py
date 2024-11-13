import json
import subprocess
import uuid
from pathlib import Path
from typing import Dict
import glob
import os

import modal

image = (  
    modal.Image.debian_slim(  
        python_version="3.12"
    )
    .apt_install("git","wget")  
    .pip_install("comfy-cli==1.2.3") 
    .run_commands(
        "comfy --skip-prompt install --nvidia"
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors --relative-path models/checkpoints",
        "comfy --skip-prompt model download --url https://huggingface.co/TheMistoAI/MistoLine/resolve/main/mistoLine_fp16.safetensors --relative-path models/controlnet",
        
        "comfy --skip-prompt model download --url https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors --relative-path models/ipadapter",
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/laion/CLIP-ViT-H-14-laion2B-s32B-b79K/resolve/main/open_clip_pytorch_model.safetensors --relative-path models/clip_vision",
        "cd /root/comfy/ComfyUI/models/clip_vision && mv open_clip_pytorch_model.safetensors CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors", 
        "comfy --skip-prompt model download --url https://huggingface.co/laion/CLIP-ViT-bigG-14-laion2B-39B-b160k/resolve/main/open_clip_pytorch_model.safetensors --relative-path models/clip_vision",
        "cd /root/comfy/ComfyUI/models/clip_vision && mv open_clip_pytorch_model.safetensors CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors",
        "cd /root/comfy/ComfyUI/models/clip_vision && ls" 
        )
    .run_commands(  
        "comfy node install comfyui_controlnet_aux",
        "comfy node install ComfyUI_Noise",
        "comfy node install ComfyUI-Custom-Scripts",
        "comfy node install ComfyUI_IPAdapter_plus",
        "comfy node install comfyui-inpaint-nodes",
        "comfy node install ComfyUI_essentials",
        "comfy node install ComfyUI-clip-interrogator",
        "comfy node install image-resize-comfyui",
        "comfy node install ComfyUI-load-image-from-url",
        "comfy node install comfyui-art-venture",
    )
    .run_commands(
        "cd /root/comfy/ComfyUI/custom_nodes && git clone https://github.com/unanan/ComfyUI-clip-interrogator.git",
        "comfy --skip-prompt model download --url https://huggingface.co/ai-forever/Real-ESRGAN/resolve/main/RealESRGAN_x2.pth --relative-path models/upscale_models",
        "comfy --skip-prompt model download --url https://huggingface.co/ai-forever/Real-ESRGAN/resolve/main/RealESRGAN_x4.pth --relative-path models/upscale_models",
        "cd /root/comfy/ComfyUI/input && wget -O watercolor_portrait_woman.jpg https://files.catbox.moe/ze5u8n.jpg && ls",
    )
)

app = modal.App(name="comfy-ui-api", image=image)

mount_workflow = modal.Mount.from_local_file(
            Path(__file__).parent / "workflow_api.json",
            "/root/workflow_api.json",
        )
mount_file = modal.Mount.from_local_dir(
            Path(__file__).parents[1] / "pecs_activities_trimmed_numbered",
            remote_path = "/root/comfy/ComfyUI/input"
        )

@app.function(
    allow_concurrent_inputs=10,
    concurrency_limit=1,
    container_idle_timeout=30,
    timeout=3600,
    gpu="T4",
    mounts=[mount_file, mount_workflow ]
)
@modal.web_server(8000, startup_timeout=60)
def ui():
    #os.system("cd /root/comfy/ComfyUI/input && wget -O watercolor_portrait_woman.jpg https://files.catbox.moe/ze5u8n.jpg && ls")
    subprocess.Popen("comfy launch -- --listen 0.0.0.0 --port 8000", shell=True)

bignumbr = 0
@app.cls(
    allow_concurrent_inputs=10,
    container_idle_timeout=300,
    gpu="T4",
    mounts=[mount_file, mount_workflow ]
)
class ComfyUI:
    @modal.enter()
    def launch_comfy_background(self):
        #os.system("cd /root/comfy/ComfyUI/input && wget -O watercolor_portrait_woman.jpg https://files.catbox.moe/ze5u8n.jpg && ls")
        cmd = "comfy launch --background"
        subprocess.run(cmd, shell=True, check=True)

    @modal.method()
    def infer(self, workflow_path: str = "/root/workflow_api.json"):
        cmd = f"comfy run --workflow {workflow_path} --wait --timeout 1200"
        subprocess.run(cmd, shell=True, check=True)

#        output_dir = "/root/comfy/ComfyUI/output"
        output_dir = "/root/comfy/ComfyUI/output/*"

#        workflow = json.loads(Path(workflow_path).read_text())
#        file_prefix = [
#            node.get("inputs")
#            for node in workflow.values()
#                if node.get("class_type") == "SaveImage"
#        ][0]["filename_prefix"]

#        for f in Path(output_dir).iterdir():
#            if f.name.startswith(file_prefix):
#                    return f.read_bytes()
        
        glob_of_files = glob.glob(output_dir)
        latest_file = max(glob_of_files, key=os.path.getctime)
        return Path(latest_file).read_bytes()

    @modal.web_endpoint(method="POST")
    def api(self, item: Dict):
        from fastapi import Response

        workflow_data = json.loads(
            (Path(__file__).parent / "workflow_api.json").read_text()
        )

#        if item["prompt"] is not None:
#            workflow_data["231"]["inputs"]["url_or_path"] = item["prompt"] 
        client_id = uuid.uuid4().hex
#        #save img no upscale
#        workflow_data["234"]["inputs"]["filename_prefix"] = client_id
#        #save img upsacale
#        workflow_data["235"]["inputs"]["filename_prefix"] = client_id

        workflow_data["3"]["inputs"]["image"] = item["prompt"]

        # save this updated workflow to a new file
#        new_workflow_file = f"{client_id}.json"
        new_workflow_file = f"{client_id}.json"
        json.dump(workflow_data, Path(new_workflow_file).open("w"))

        # run inference on the currently running container
        img_bytes = self.infer.local(new_workflow_file)

        return Response(img_bytes, media_type="image/jpeg")

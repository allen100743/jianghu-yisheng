"""
ComfyUI 圖片生成工具 — 供 Claude Code 呼叫
用法: python tools/comfyui_generate.py "prompt" output_filename.png
"""
import sys
import json
import time
import urllib.request
import urllib.error

COMFYUI_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = "assets/art/generated"

CHECKPOINT = "dreamshaper_8.safetensors"
LORA = "wuxia_v2.safetensors"
LORA_STRENGTH = 0.75

def generate(prompt_text: str, output_name: str, negative: str = "photorealistic, photo, 3d render, western style, anime, deformed, extra limbs, text, watermark, blurry, low quality"):
    workflow = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT}
        },
        "10": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["4", 0],
                "clip": ["4", 1],
                "lora_name": LORA,
                "strength_model": LORA_STRENGTH,
                "strength_clip": LORA_STRENGTH
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 512, "height": 768, "batch_size": 1}
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt_text, "clip": ["10", 1]}
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["10", 1]}
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int(time.time()),
                "steps": 28,
                "cfg": 6.5,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["10", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": output_name.replace(".png", ""), "images": ["8", 0]}
        }
    }

    # 送出任務
    data = json.dumps({"prompt": workflow, "client_id": "claude-code"}).encode()
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data,
                                  headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req)
        prompt_id = json.loads(resp.read())["prompt_id"]
        print(f"任務送出：{prompt_id}")
    except urllib.error.URLError:
        print("ERROR: ComfyUI 未啟動，請先開啟 ComfyUI")
        sys.exit(1)

    # 等待完成
    print("生成中", end="", flush=True)
    for _ in range(120):
        time.sleep(2)
        print(".", end="", flush=True)
        try:
            resp = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}")
            history = json.loads(resp.read())
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        filename = node_output["images"][0]["filename"]
                        # 下載圖片
                        img_url = f"{COMFYUI_URL}/view?filename={filename}&type=output"
                        save_path = f"{OUTPUT_DIR}/{output_name}"
                        urllib.request.urlretrieve(img_url, save_path)
                        print(f"\n完成：{save_path}")
                        return save_path
        except Exception:
            pass
    print("\nERROR: 生成逾時")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python tools/comfyui_generate.py \"prompt\" output.png")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])

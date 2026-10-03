# AI Empire · LoRA Trainer (Krea 2)

Guides and the full course: https://joinaiempire.com

Image: `ghcr.io/justlinuxnoob/lora-training:latest` (built by GitHub Actions on every push + every Monday, always on the newest official AI Toolkit).

It's the official AI Toolkit (Ostris) with our extras:
- 📦 Drop the Dataset Maker `.zip` in `datasets/` → it unzips itself into its own folder (images + `.txt` captions only), then the zip is deleted.
- 💾 Everything is on `/workspace/aitk` (datasets, LoRAs, the job list, model downloads), so a restart loses nothing.
- ⬇️ Krea 2 Raw downloads in the background on first boot, with the Qwen3-VL text encoder and the VAE. **No Hugging Face account or token needed** (open Comfy-Org repack of the same weights).
- 🔓 Krea 2 jobs you make in the UI (Krea 2 Raw or Turbo) load that open repack too, so they never ask for a token.

You set up the training job yourself in AI Toolkit. Nothing is made for you (see "Auto jobs" at the end if you want that).

## RunPod template (My Templates → New Template)
| Field | Value |
|---|---|
| Name | AI Empire · LoRA Trainer (Krea 2) |
| Type | Pod |
| Container image | `ghcr.io/justlinuxnoob/lora-training:latest` |
| Container disk | 30 GB |
| Volume disk | 100 GB, mounted at `/workspace` |
| Expose HTTP ports | `8675,8888` (8675 = AI Toolkit, 8888 = JupyterLab) |
| Env `AI_TOOLKIT_AUTH` | leave empty; students set a password (without one, anyone with the pod URL can open it) |
| Env `JUPYTER_PASSWORD` | same idea, for JupyterLab |
| Visibility | **Public** (needed for the creator 1%) |

Share it as `https://console.runpod.io/deploy?template=2zexf8lq3z&ref=9s65jq8z`.

GPU: **RTX PRO 6000 (96 GB)** or **H100 / A100 80 GB** = full quality. **RTX 5090 (32 GB)** and 48 GB cards work too, but you turn on fp8 quantization (transformer and text encoder) and **Low VRAM** in the job yourself (slightly lower quality, slower).
The image uses CUDA 13 wheels, so the host needs a recent driver. If the pod log says the CUDA driver is too old, deploy again with the CUDA version filter set to 13.0.

## Student steps
1. Deploy the template → pick the GPU → (optional: set the two passwords) → Deploy.
2. Port **8888** (JupyterLab) → drag your dataset `.zip` into `datasets/`. Wait a few seconds: it unzips into `datasets/<zip name>/`. Or use AI Toolkit → Datasets → upload.
3. Port **8675** (AI Toolkit) → New Job. Pick Krea 2, pick your dataset, then check these fields:
   - **Trigger Word:** empty by default. Type your trigger word, the same one your captions start with (e.g. `zvx woman`).
   - **Save every:** 250 steps by default. Fine as it is.
   - **Max Step Saves to Keep:** 4 by default, so older saves get deleted. Raise it to **12** to keep every save of a 3,000-step run.
   - **32-48 GB card:** turn on fp8 quantization and **Low VRAM**.
4. Create the job → ▶ **Start**. Check the sample images as they come in.
5. When it's done, download the LoRA from `output/<job>/` (JupyterLab or the job page).
6. Stop **and terminate** the pod.

Logs: `/workspace/aitk/aiempire.log` (our helper), and the job page in AI Toolkit.

## Picking the best checkpoint
Training saves `<job>_000000250.safetensors`, `_000000500`, … and the final `<job>.safetensors`. Only the last few step saves stay, as many as Max Step Saves to Keep.
Train on **Raw**, test on **Turbo** (or our Krea2 workflow): try 1500 / 2000 / 2500 / final with the same 3 prompts and seed, LoRA strength 0.8–1.0.
Too-early = face not quite her. Too-late = same background/outfit/expression creeping into every image, plastic skin. Pick the last one before that starts.

## Prompting the finished LoRA
Trigger word, then one short hair-and-eyes line, then the scene (photo type, pose, outfit, place, light, framing), ending with `candid smartphone photo, natural skin texture`.
Example start: `zvx woman, long wavy dark brown hair, middle part, hazel eyes, ...`
Don't describe her face, makeup, skin or body. The LoRA knows her face.
Training captions are different: they never describe her face or hair.

## Template env vars (all optional)
| Env | What it does |
|---|---|
| `AI_TOOLKIT_AUTH` | password for AI Toolkit (port 8675) |
| `JUPYTER_PASSWORD` | password for JupyterLab (port 8888) |
| `HF_TOKEN` | not needed; if set, it's passed on to AI Toolkit and the downloads |
| `AIEMPIRE_NO_DOWNLOAD=1` | skip the background Krea 2 download |
| `AIEMPIRE_AUTOJOB=1` | turn auto jobs on (below) |

## Auto jobs (off by default)
With `AIEMPIRE_AUTOJOB=1`, every dataset folder with images and `.txt` captions gets a ready job named `<dataset>_krea2`. The trigger word is read from the first caption (the text before the first comma). You only press **Start**.
Its settings: Krea 2 Raw · LoRA rank 64 / alpha 64 · 3000 steps · lr 1e-4 · timestep sigmoid · resolution 1024 · saves every 250 steps, 12 kept · 4 sample images every 500 steps. On cards under 70 GB it turns on fp8 quantization + Low VRAM by itself; otherwise both are off.
Extra env vars, used only in this mode: `AIEMPIRE_STEPS` (default 3000), `AIEMPIRE_RANK` (default 64), `AIEMPIRE_QUANTIZE=1` (force fp8 + Low VRAM).

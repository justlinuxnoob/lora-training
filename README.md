# Krea 2 LoRA Training on RunPod: AI Toolkit Template for Character LoRAs

A RunPod template for training a Krea 2 character LoRA with AI Toolkit (Ostris). Deploy it, drop your dataset `.zip` in, set up the job in the AI Toolkit UI and press Start. You rent the GPU by the hour, and you don't need a Hugging Face account or token.

**Deploy:** https://console.runpod.io/deploy?template=2zexf8lq3z&ref=9s65jq8z

Image: `ghcr.io/justlinuxnoob/lora-training:latest`. GitHub Actions rebuilds it on every code push and every Monday, always from the newest official `ostris/aitoolkit:latest`.

## What this AI Toolkit RunPod template does

It's the official AI Toolkit image with a small helper on top:

- **Krea 2 built in.** If the base image ever lacks Krea 2 support, the build updates AI Toolkit to a version that has it.
- **No Hugging Face token.** Krea 2 Raw and Krea 2 Turbo jobs you make in the UI load Comfy-Org's open repack of the same weights (`Comfy-Org/Krea-2`), so they never ask for a token.
- **Models download in the background.** On first boot it fetches Krea 2 Raw (about 26 GB), the Qwen3-VL-4B text encoder and the Qwen-Image VAE, so training starts sooner. It tries 3 times; if all fail, the models download when training starts instead.
- **Zip in, dataset out.** Drop a dataset `.zip` (for example from the [Dataset Maker](https://github.com/justlinuxnoob/aiempire-dataset-maker)) into `datasets/`. It unzips into its own folder, keeps only images and `.txt` captions, then deletes the zip.
- **A restart loses nothing.** Datasets, LoRAs, the job list and model downloads all live on `/workspace/aitk`.
- **JupyterLab on port 8888** for uploading datasets and downloading LoRAs. AI Toolkit is on port 8675.

You set up the training job yourself in AI Toolkit. Nothing is made for you unless you turn on auto jobs (see below).

## Which GPU to pick for Krea 2 LoRA training

| GPU | VRAM | What to do |
|---|---|---|
| RTX PRO 6000 | 96 GB | Full quality. Leave quantization off. |
| H100 or A100 80 GB | 80 GB | Full quality. Leave quantization off. |
| 48 GB cards (L40S, A6000) | 48 GB | Turn on fp8 quantization (transformer and text encoder) and **Low VRAM** in the job. |
| RTX 5090 | 32 GB | Same: fp8 quantization and **Low VRAM**. |

On 32-48 GB cards Krea 2 only fits quantized. It works, but quality is slightly lower and training is slower.

The image uses CUDA 13 wheels, so the host needs a recent driver. See troubleshooting if the log says the driver is too old.

## AI Toolkit settings for a Krea 2 character LoRA

Most AI Toolkit defaults are fine. Check these fields when you make the job:

| Field | AI Toolkit default | What to set |
|---|---|---|
| Model | | Krea 2 (Raw) |
| Trigger Word | empty | Type your trigger word, the same one your captions start with (e.g. `zvx woman`) |
| Save every | 250 steps | Leave it at 250 |
| Max Step Saves to Keep | 4 | Raise it to **12**, so a 3,000-step run keeps every save |
| Quantization (fp8) and Low VRAM | off | On for 32-48 GB cards, off for 80-96 GB cards |

With Max Step Saves to Keep at 4, older saves get deleted as training goes on. You'd lose the early checkpoints you want to compare.

## How to train a character LoRA on RunPod, step by step

1. Open the deploy link, pick a GPU, optionally set the two passwords (`AI_TOOLKIT_AUTH`, `JUPYTER_PASSWORD`), then Deploy.
2. Open port **8888** (JupyterLab). Drag your dataset `.zip` into `datasets/`. Wait a few seconds: it unzips into `datasets/<zip name>/`. You can also upload through AI Toolkit → Datasets.
3. Open port **8675** (AI Toolkit) → New Job. Pick Krea 2, pick your dataset, and set the fields from the table above.
4. Create the job and press **Start**. Watch the sample images as they come in.
5. When it's done, download the LoRA from `output/<job>/` (in JupyterLab or on the job page).
6. Stop **and terminate** the pod so it stops billing. Terminating deletes `/workspace`, so download first.

## How to pick the best Krea 2 LoRA checkpoint

Training saves `<job>_000000250.safetensors`, `<job>_000000500.safetensors` and so on, plus the final `<job>.safetensors`. Only the newest saves stay, as many as Max Step Saves to Keep.

Train on **Raw**, test on **Turbo** (or our Krea 2 workflow):

1. Load each checkpoint: 1500, 2000, 2500 and the final one.
2. Use the same 3 prompts and the same seed for all of them.
3. Set LoRA strength between 0.8 and 1.0.

Too early: the face isn't quite her yet. Too late: the same background, outfit or expression creeps into every image, and skin looks plastic. Pick the last checkpoint before that starts.

## How to prompt your finished character LoRA

Start with the trigger word, then one short hair-and-eyes line, then the scene: photo type, pose, outfit, place, light, framing. End with `candid smartphone photo, natural skin texture`. Prompts run about 40 to 55 words.

Example start:

```
zvx woman, long wavy dark brown hair, middle part, hazel eyes, ...
```

A full prompt:

```
zvx woman, long wavy dark brown hair, middle part, hazel eyes, mirror selfie, standing, holding phone at chest height, oversized grey hoodie and black leggings, bright apartment hallway, soft daylight from a window, vertical framing, candid smartphone photo, natural skin texture
```

Don't describe her face, makeup, skin or body. The LoRA already knows her face.

**Training captions are different.** They start with the trigger word and describe the scene, but never her face or hair. For example: `zvx woman, close-up selfie, ...`

## Environment variables

All optional. Set them on the template or when you deploy.

| Env | What it does |
|---|---|
| `AI_TOOLKIT_AUTH` | Password for AI Toolkit (port 8675). Empty = anyone with the pod URL can open it. |
| `JUPYTER_PASSWORD` | Password for JupyterLab (port 8888). Empty = no password. |
| `HF_TOKEN` | Not needed. If set, it's passed on to AI Toolkit and the downloads. |
| `AIEMPIRE_NO_DOWNLOAD=1` | Skip the background Krea 2 download. |
| `AIEMPIRE_AUTOJOB=1` | Turn auto jobs on (below). |
| `AIEMPIRE_POLL` | Seconds between checks of `datasets/` for new zips (default 10). |

## Auto jobs (off by default)

With `AIEMPIRE_AUTOJOB=1`, every dataset folder that has images and `.txt` captions gets a ready job named `<dataset>_krea2`. The trigger word is read from the first caption: the text before the first comma. You only press **Start**.

Auto job settings:

- Krea 2 Raw (Comfy-Org open repack)
- LoRA rank 64, alpha 64
- 3,000 steps, learning rate 1e-4, AdamW 8-bit
- Timestep type sigmoid, resolution 1024
- Saves every 250 steps, 12 kept
- 4 sample images every 500 steps (1024 x 1280, seed 42)
- Under 70 GB of VRAM it turns on fp8 quantization and Low VRAM by itself. On bigger cards both stay off.

Extra env vars, used only in this mode:

| Env | Default | What it does |
|---|---|---|
| `AIEMPIRE_STEPS` | 3000 | Training steps |
| `AIEMPIRE_RANK` | 64 | LoRA rank (alpha matches it) |
| `AIEMPIRE_QUANTIZE=1` | off | Force fp8 quantization and Low VRAM on any card |

## Make your own copy of the template

RunPod → My Templates → New Template:

| Field | Value |
|---|---|
| Name | AI Empire · LoRA Trainer (Krea 2) |
| Type | Pod |
| Container image | `ghcr.io/justlinuxnoob/lora-training:latest` |
| Container disk | 30 GB |
| Volume disk | 100 GB, mounted at `/workspace` |
| Expose HTTP ports | `8675,8888` (8675 = AI Toolkit, 8888 = JupyterLab) |
| Env `AI_TOOLKIT_AUTH` | Leave empty; students set their own password |
| Env `JUPYTER_PASSWORD` | Same idea, for JupyterLab |
| Visibility | **Public** (needed for the creator 1%) |

## Troubleshooting and FAQ

### The pod log says the CUDA driver is too old

The image uses CUDA 13 wheels. Deploy again with the CUDA version filter set to 13.0, so you get a host with a recent driver.

### Does it ask for a Hugging Face token?

No. Krea 2 Raw and Turbo load from Comfy-Org's open repack, and the Qwen3-VL text encoder and Qwen-Image VAE are open too. You only need `HF_TOKEN` if you pick a different, gated model yourself.

### My zip didn't unzip

It waits until the file size stops changing, so a zip that's still uploading is left alone. Give it a few seconds after the upload ends. Only `.jpg`, `.jpeg`, `.png`, `.webp` and `.txt` files are kept; subfolders are flattened and hidden or `__MACOSX` files are skipped. If the zip is broken, the log says so and it retries.

### Will I lose my work if the pod restarts?

No. Datasets, trained LoRAs, the AI Toolkit job list and the model downloads are all on `/workspace/aitk`, the volume. A restart keeps them. Terminating the pod deletes the volume, so download your LoRA first.

### Where are the logs?

`/workspace/aitk/aiempire.log` for our helper (zips, downloads, auto jobs), `/workspace/aitk/jupyter.log` for JupyterLab, and the job page in AI Toolkit for training.

## More

Step-by-step video and guides: https://joinaiempire.com/video

Made by AI Empire: https://joinaiempire.com

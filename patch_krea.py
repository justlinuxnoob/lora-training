"""Build-time patch: point Krea 2 hub downloads at the open Comfy-Org repack (same weights, no token).
Jobs made by hand in the UI default to krea/Krea-2-Raw, which is gated on Hugging Face."""
p = "/app/ai-toolkit/extensions_built_in/diffusion_models/krea2/krea2.py"
s = open(p).read()
anchor = "    fname = filename or ("
assert anchor in s, "AI Toolkit Krea 2 loader changed: update patch_krea.py"
patch = '''    # AI Empire: krea/* is gated on Hugging Face -> use Comfy-Org's open repack of the same weights
    _open = {
        "krea/Krea-2-Raw": ("Comfy-Org/Krea-2", "diffusion_models/krea2_raw_bf16.safetensors"),
        "krea/Krea-2-Turbo": ("Comfy-Org/Krea-2", "diffusion_models/krea2_turbo_bf16.safetensors"),
    }
    if name_or_path in _open and filename is None:
        name_or_path, filename = _open[name_or_path]
'''
if "AI Empire: krea/*" not in s:
    s = s.replace(anchor, patch + anchor, 1)
open(p, "w").write(s)
print("patched", p)

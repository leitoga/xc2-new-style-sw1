"""Mythra New Style textures laid onto the Switch 1 image slots (file name = image index)."""
import glob, os, numpy as np
from PIL import Image
def tx(i): return np.array(Image.open(glob.glob(f"nsM/{i}.*.png")[0]).convert("RGBA")).astype(float)
def orig(i): return np.load(f"orig-texM/{i}.npy") * 255
def save(i, a):
    a = np.clip(a, 0, 255).astype(np.uint8)
    a = a.copy(); a[..., 3] = 255
    Image.fromarray(a, "RGBA").save(f"tex-m/{i}.png")
def solid(rgb, s=16):
    a = np.zeros((s, s, 4)); a[:] = (*rgb, 255); return a
os.makedirs("tex-m", exist_ok=True)
col = tx(13)
skin = ((col[..., 0] > 200) & (col[..., 0] - col[..., 2] > 35) & (col[..., 1] > 130))[..., None]
spec = col.copy(); spec[..., :3] *= 0.8; spec[..., :3] *= ~skin
save(0, col); save(1, tx(21)); save(9, spec)
for dst, src in zip((2, 3, 4, 5, 6, 10), (14, 15, 16, 17, 19, 18)): save(dst, tx(src))
save(7, solid((0, 0, 0))); save(8, solid((0, 0, 0)))
for i in (31, 32): save(i, solid(np.median(orig(i).reshape(-1, 4), 0)[:3]))
save(12, tx(41))
# wings
save(15, tx(38)); save(16, tx(39)); w = tx(38); w[..., :3] *= 0.65; save(17, w); save(18, tx(40)); save(34, tx(47))
save(19, tx(0)); save(21, tx(1)); save(25, tx(7))
# hair: white outside, aqua inside
save(30, tx(11))
hb = tx(12); lum = hb[..., :3] @ np.array((0.30, 0.59, 0.11)); rel = np.clip(lum / np.median(lum), 0.7, 1.2)[..., None]
hb[..., :3] = np.array((168, 226, 220), float) * rel
save(35, hb)
save(36, tx(9)); save(45, tx(10))      # metal pieces still use the old body atlas
S = 1024
def gray(i): return np.array(Image.fromarray(tx(i).astype(np.uint8)).convert("L").resize((S, S), Image.LANCZOS)).astype(float)[..., None] / 255
# light sky: pale blue with soft white clouds
c = np.clip(gray(26) * 1.3, 0, 1)
sky = np.array((176, 192, 232), float) * (1 - c) + np.array((246, 244, 250), float) * c
sky = np.dstack([sky, np.full((S, S), 255.0)]); save(37, sky); s = sky.copy(); s[..., :3] *= (0.70, 0.72, 0.86); save(38, s)
# dark sky: deep teal with fine specks
d = np.array((10, 48, 72), float) + gray(26) * np.array((6, 52, 60), float)
r = np.random.default_rng(7).random((S, S)); specks = (r > 0.9965)[..., None] * np.array((110, 225, 225), float)
dark = np.dstack([np.clip(d + specks, 0, 255), np.full((S, S), 255.0)]); save(39, dark); s = dark.copy(); s[..., :3] *= 0.7; save(40, s)
save(41, solid((86, 70, 66))); save(42, solid((52, 42, 42)))   # tights
save(43, solid((128, 128, 0))); save(44, solid((0, 0, 0)))

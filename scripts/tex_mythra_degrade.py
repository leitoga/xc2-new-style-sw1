"""Leg sides: galaxy over a gradient, light blue at the top to silver grey at the ankle (by 3D height)."""
import json, glob, numpy as np
from PIL import Image, ImageDraw, ImageFilter
S = 1024
# row 0 = top of the body (light blue), last row = feet (grey); UVs are set from height in the build
t = np.clip(((1 - np.linspace(0, 1, S)) * 1.4 - 0.20) / 0.65, 0, 1); t = t * t * (3 - 2 * t)
w = np.repeat(t[:, None, None], S, axis=1)
def layer(i): return np.array(Image.open(glob.glob(f"nsM/{i}.*.png")[0]).convert("RGB").resize((S, S), Image.LANCZOS)).astype(float)
base = np.array((166, 172, 180), float) * (1 - w) + np.array((152, 196, 236), float) * w
clouds = np.clip(layer(26)[..., :1] / 255 * 1.2, 0, 1)
neb = np.clip(layer(23).mean(-1, keepdims=True) / 90, 0, 1)
a = base * (1 - 0.55 * clouds) + np.array((226, 232, 242), float) * 0.55 * clouds
a = a * (1 - 0.30 * neb) + np.array((138, 142, 196), float) * 0.30 * neb
a = a + (np.random.default_rng(11).random((S, S))[..., None] > 0.9972) * 75
def save(i, img):
    img = np.clip(img, 0, 255)
    Image.fromarray(np.dstack([img, np.full(img.shape[:2], 255.0)]).astype(np.uint8), "RGBA").save(f"tex-m8/{i}.png")
save(37, a); save(38, a * (0.86, 0.88, 0.94))

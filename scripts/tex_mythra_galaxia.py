"""Mythra's galaxy pieces in the same tone as the rest (#506877): soft nebula and fine aqua specks."""
import glob, numpy as np
from PIL import Image
S = 1024
cloud = np.array(Image.open(glob.glob("nsM/26.*.png")[0]).convert("L").resize((S, S), Image.LANCZOS)).astype(float)[..., None] / 255
a = np.array((80, 104, 119), float) + (cloud - cloud.mean()) * np.array((30, 40, 44), float)
r = np.random.default_rng(7).random((S, S))[..., None]
a = a + (r > 0.9965) * np.array((60, 130, 120), float)
def save(i, x):
    x = np.clip(x, 0, 255)
    Image.fromarray(np.dstack([x, np.full(x.shape[:2], 255.0)]).astype(np.uint8), "RGBA").save(f"tex-m21/{i}.png")
save(39, a); save(40, a * 0.91)

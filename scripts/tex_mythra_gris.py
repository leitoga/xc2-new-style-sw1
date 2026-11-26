"""All formerly light-blue pieces: dark slate grey with tonal variation (not flat), no clouds, no birds."""
import numpy as np
from PIL import Image
S = 1024
rng = np.random.default_rng(9)
def noise(cu, cv):
    g = rng.random((cv + 1, cu)); g = np.concatenate([g, g[:, :1]], 1)
    x = np.linspace(0, cu, S, endpoint=False); y = np.linspace(0, cv, S, endpoint=False)
    xi, yi = x.astype(int), y.astype(int); fx, fy = x - xi, y - yi
    fx = fx * fx * (3 - 2 * fx); fy = (fy * fy * (3 - 2 * fy))[:, None]
    a = g[yi][:, xi] * (1 - fx) + g[yi][:, xi + 1] * fx
    b = g[yi + 1][:, xi] * (1 - fx) + g[yi + 1][:, xi + 1] * fx
    return a * (1 - fy) + b * fy
# u: 1 texture = 0.25 m, v: 1 texture = 1.4 m  ->  features of 5-10 cm
big = 0.8 * noise(2, 7) + 0.2 * noise(4, 15)
fine = noise(16, 90)
t = np.clip((big - 0.28) / 0.44, 0, 1)[..., None]
a = np.array((52, 68, 82), float) * (1 - t) + np.array((74, 94, 108), float) * t     # dark slate, soft tones
a += ((fine - 0.5) * 4)[..., None]
sheen = np.exp(-(((np.arange(S) / S * 2) % 1 - 0.5) / 0.14) ** 2)                     # soft metallic highlight bands
a += sheen[None, :, None] * np.array((22, 30, 34), float)
specks = (rng.random((S, S)) > 0.9988)[..., None]
a = a + specks * np.array((40, 120, 110), float)
def save(i, x):
    x = np.clip(x, 0, 255)
    Image.fromarray(np.dstack([x, np.full(x.shape[:2], 255.0)]).astype(np.uint8), "RGBA").save(f"tex-m15/{i}.png")
save(37, a); save(38, a * 0.80)

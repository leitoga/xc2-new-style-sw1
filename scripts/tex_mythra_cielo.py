"""Sky pieces as in the Switch 2 art: smooth periwinkle, soft cumulus only low on the legs, a few small
white bird shapes, no star field. u: 1 texture = 0.25 m; v: 1 texture = 1.4 m of height (row 0 = top)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
S = 1024
rng = np.random.default_rng(3)
height = (1 - np.linspace(0, 1, S))[:, None] * 1.4            # metres, per row

def noise(cu, cv):  # value noise, periodic in u, cu x cv cells over the texture
    g = rng.random((cv + 1, cu)); g = np.concatenate([g, g[:, :1]], 1)
    x = np.linspace(0, cu, S, endpoint=False); y = np.linspace(0, cv, S, endpoint=False)
    xi, yi = x.astype(int), y.astype(int); fx, fy = x - xi, y - yi
    fx = fx * fx * (3 - 2 * fx); fy = (fy * fy * (3 - 2 * fy))[:, None]
    a = g[yi][:, xi] * (1 - fx) + g[yi][:, xi + 1] * fx
    b = g[yi + 1][:, xi] * (1 - fx) + g[yi + 1][:, xi + 1] * fx
    return a * (1 - fy) + b * fy

def mix(a, colour, w): return a * (1 - w[..., None]) + np.array(colour, float) * w[..., None]
def smooth(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)

# smooth gradient: silver grey at the ankle, periwinkle above
t = smooth((height - 0.15) / 0.55)
a = np.array((178, 184, 196), float) * (1 - t[..., None]) + np.array((160, 184, 232), float) * t[..., None]
a = np.repeat(a, S, axis=1)
# cumulus: round puffs, only on the lower legs
n = 0.55 * noise(4, 22) + 0.30 * noise(9, 50) + 0.15 * noise(20, 112)
low = smooth((0.62 - height) / 0.30)
a = mix(a, (246, 232, 238), smooth((n - 0.48) / 0.16) * low)
a = mix(a, (255, 252, 252), smooth((n - 0.62) / 0.12) * low)
# birds: two small flocks (thigh and chest height)
img = Image.new("L", (S, S), 0); d = ImageDraw.Draw(img)
pu, pv = S / 0.25, S / 1.4                                      # pixels per metre
def bird(u, z, size):
    cx, cy = u * pu, (1 - z / 1.4) * S
    rx, ry = size * pu / 2, size * pv / 2
    for ox in (-S, 0, S):
        d.polygon([(cx + ox - rx, cy - ry * .15), (cx + ox - rx * .15, cy - ry * .25), (cx + ox, cy - ry),
                   (cx + ox + rx * .15, cy - ry * .25), (cx + ox + rx, cy - ry * .15), (cx + ox + rx * .15, cy + ry * .2),
                   (cx + ox, cy + ry * .6), (cx + ox - rx * .15, cy + ry * .2)], fill=255)
for z0 in (0.80, 1.22):
    for du, dz, size in ((0.02, 0.040, 0.020), (0.07, 0.015, 0.016), (0.10, 0.050, 0.013), (0.13, -0.010, 0.018), (0.19, 0.030, 0.012)):
        bird(du, z0 + dz, size)
a = mix(a, (252, 253, 255), np.array(img) / 255)

def save(i, x):
    x = np.clip(x, 0, 255)
    Image.fromarray(np.dstack([x, np.full(x.shape[:2], 255.0)]).astype(np.uint8), "RGBA").save(f"tex-m12/{i}.png")
save(37, a); save(38, a * (0.84, 0.86, 0.94))
# skirt panel: smooth silver white with a faint hazy veil, nothing drawn on it
p = np.zeros((S, S, 3)) + (214, 216, 220)
veil = smooth((0.55 - np.abs(noise(2, 9) - 0.5) * 2) / 0.55)
p = mix(p, (240, 240, 246), 0.5 * veil)
p = mix(p, (236, 237, 244), np.repeat(smooth(1 - np.abs(height - 0.90) / 0.12), S, axis=1) * 0.7)
save(41, p); save(42, p * 0.80)

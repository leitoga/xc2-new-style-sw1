"""Legs only (v26: lighter silver grey at the ankle). Leg sides (user choice: galaxy) with the vertical gradient measured on the Switch 2 reference.
UV v = height / 1.4 (row 0 = 1.4 m). Sleeves and chest (above the legs) keep the galaxy tone #506877."""
import glob, numpy as np
from PIL import Image
S = 1024
z = (1 - (np.arange(S) + 0.5) / S) * 1.4
stops = [(0.02, (150, 158, 171)), (0.18, (150, 158, 171)), (0.24, (142, 152, 169)), (0.31, (127, 142, 168)),
         (0.39, (133, 150, 180)), (0.49, (150, 170, 200)), (0.55, (112, 134, 174)), (0.65, (104, 127, 170)),
         (0.83, (102, 126, 176)), (1.40, (102, 126, 176))]
col = np.stack([np.interp(z, [s[0] for s in stops], [s[1][c] for s in stops]) for c in range(3)], 1)
a = np.repeat(col[:, None], S, 1)
# the same galaxy as the other pieces: soft nebula and fine aqua specks
cloud = np.array(Image.open(glob.glob("nsM/26.*.png")[0]).convert("L").resize((S, S // 4), Image.LANCZOS)).astype(float)
cloud = np.tile(cloud, (4, 1))[..., None] / 255
a = a + (cloud - cloud.mean()) * np.array((32, 42, 48), float)
r = np.random.default_rng(7).random((S, S))[..., None]
a = a + (r > 0.9975) * np.array((60, 130, 120), float)
def save(i, x):
    x = np.clip(x, 0, 255)
    Image.fromarray(np.dstack([x, np.full(x.shape[:2], 255.0)]).astype(np.uint8), "RGBA").save(f"tex-m25/{i}.png")
save(37, a); save(38, a * 0.91)

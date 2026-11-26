"""Dithered opacity of the skirt veil: nothing at its top edge, denser below, gone again at the hem.
v = height / 1.4 (row 0 = top of the texture = 1.4 m)."""
import numpy as np
from PIL import Image
S = 1024
z = (1 - (np.arange(S) + 0.5) / S) * 1.4
def smooth(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
density = smooth((1.025 - z) / 0.11) * smooth((z - 0.822) / 0.035) * 0.72
rng = np.random.default_rng(21)
# dots about 1.4 mm on the model: 6 texels wide, 1 texel tall
noise = np.repeat(rng.random((S, S // 6 + 1)), 6, axis=1)[:, :S]
mask = np.where(noise < density[:, None], 255, 0).astype(np.uint8)
Image.fromarray(np.dstack([mask, mask, mask, np.full_like(mask, 255)]), "RGBA").save("tex-m14/49.png")
for row in (z > 1.0, (z > 0.86) & (z < 0.91)):
    print("opacidad media %.2f" % (mask[row] > 0).mean())

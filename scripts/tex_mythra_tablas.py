"""Skirt panel: carry the bodice's vertical pleats down, in colour and relief (replaces images 41, 42; adds 48)."""
import numpy as np
from PIL import Image
S = 1024
u = np.arange(S) / S * 0.25                        # metres across (1 texture = 0.25 m)
phase = (u / 0.025) % 1.0                          # one pleat every 2.5 cm
seam = np.exp(-((phase - 0.5) / 0.055) ** 2)       # thin groove
side = np.sin(2 * np.pi * phase)                   # gentle rounding of each pleat
col = np.array((214, 216, 219), float) + (side * 6)[:, None]
col = col * (1 - seam[:, None]) + np.array((150, 156, 170), float) * seam[:, None]
col = np.repeat(col[None], S, 0)
def save(i, a):
    a = np.clip(a, 0, 255)
    Image.fromarray(np.dstack([a, np.full(a.shape[:2], 255.0)]).astype(np.uint8), "RGBA").save(f"tex-m13/{i}.png")
save(41, col); save(42, col * 0.80)
nx = 128 + 38 * np.cos(2 * np.pi * phase) + 60 * seam * np.sign(phase - 0.5)
nrm = np.zeros((S, S, 3)); nrm[..., 0] = nx; nrm[..., 1] = 128
save(48, nrm)

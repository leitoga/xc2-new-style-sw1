"""New Style textures laid onto the Switch 1 material slots (indices = image index)."""
import os, numpy as np
from PIL import Image
T = "/home/leo/Documentos/Proyecto predeterminado/xc2-new-style/rebuild/texturas/bl140101."
def tx(n): return Image.open(T + n + ".png").convert("RGBA")
def arr(im): return np.array(im).astype(float)
def save(i, a): Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA").save(f"tex-v9/{i}.png")
os.makedirs("tex-v9", exist_ok=True)
def shade(a):  # toon shadow colour, same layout as the lit colour
    s = a.copy(); s[..., :3] *= (0.66, 0.56, 0.72); return s
col = arr(tx("26.BL140101_COL"))
save(9, arr(tx("14.BL140101_HAIR")))
save(13, col); save(23, shade(col)); save(24, shade(col))
save(14, arr(tx("27.BL140101_GLO"))); save(15, arr(tx("28.BL140101_GLOC"))); save(22, arr(tx("29.BL140101_NRM")))
save(25, arr(tx("11.BL000101_HAIR_COL")))
flat = np.zeros((1024, 1024, 4)); flat[:] = (247, 0, 0, 255); save(33, flat)
# galaxy: dark indigo blobs (COL_PLUS2) + the two star layers
def layer(n, size, tile=1):
    im = tx(n).resize((size // tile, size // tile), Image.LANCZOS)
    return np.tile(arr(im)[..., :3], (tile, tile, 1))
S = 1024
g = np.array((11, 15, 52), float) + layer("16.COL_PLUS2", S) * 0.55
stars = np.maximum(layer("19.STAR_02", S, 2) * 2.5, layer("20.STAR_01", S, 2) * 1.2)
g = np.clip(g + stars, 0, 255)
g = np.dstack([g, np.full((S, S), 255.0)])
save(34, g); save(35, shade(g))
save(36, arr(tx("15.BL140101_HAIRB")))
save(37, arr(tx("31.BL140101_HAIRACCE_COL")))
n = np.zeros((16, 16, 4)); n[:] = (128, 128, 0, 255); save(38, n)
k = np.zeros((16, 16, 4)); k[:] = (0, 0, 0, 255); save(39, k)
# cape: coloured trim where the AO mask is set, galaxy elsewhere
b = arr(tx("23.BL140101_B_COL")); m = arr(tx("25.BL140101_B_AO"))[..., :1] / 255
gc = np.array(Image.fromarray(g.astype(np.uint8)).resize((b.shape[1], b.shape[0]))).astype(float)
cape = gc * (1 - m) + b * m
save(40, cape); save(41, shade(cape))

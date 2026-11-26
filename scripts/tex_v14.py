"""New Style textures laid onto the Switch 1 material slots (indices = image index)."""
import os, numpy as np
from PIL import Image
T = "/home/leo/Documentos/Proyecto predeterminado/xc2-new-style/rebuild/texturas/bl140101."
def tx(n): return Image.open(T + n + ".png").convert("RGBA")
def arr(im): return np.array(im).astype(float)
def save(i, a): Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA").save(f"tex-v14/{i}.png")
os.makedirs("tex-v14", exist_ok=True)
def shade(a):  # toon shadow colour, same layout as the lit colour
    s = a.copy(); s[..., :3] *= (0.66, 0.56, 0.72); return s
col = arr(tx("26.BL140101_COL"))
save(13, col); save(23, shade(col)); save(24, shade(col))
save(14, arr(tx("27.BL140101_GLO"))); save(15, arr(tx("28.BL140101_GLOC"))); save(22, arr(tx("29.BL140101_NRM")))
save(25, arr(tx("11.BL000101_HAIR_COL")))
flat = np.zeros((1024, 1024, 4)); flat[:] = (247, 0, 0, 255); save(33, flat)
# galaxy: dark indigo blobs (COL_PLUS2) + the two star layers
def layer(n, size, tile=1):
    im = tx(n).resize((size // tile, size // tile), Image.LANCZOS)
    return np.tile(arr(im)[..., :3], (tile, tile, 1))
S = 1024
g = np.array((17, 24, 50), float) + layer("16.COL_PLUS2", S) * (0.30, 0.22, 0.36)
fine = np.maximum(layer("19.STAR_02", S, 4).max(-1) * 2.2, layer("20.STAR_01", S, 2).max(-1) * 1.0)
stars = fine[..., None] / 255 * np.array((60, 215, 190), float)
g = np.clip(g + stars, 0, 255)
g = np.dstack([g, np.full((S, S), 255.0)])
save(34, g); save(35, shade(g))
hb = arr(tx("15.BL140101_HAIRB"))
lum = hb[..., :3] @ np.array((0.30, 0.59, 0.11))
rel = np.clip(lum / np.median(lum), 0.7, 1.25)[..., None]
hb[..., :3] = np.array((255, 150, 28), float) * rel
hb = np.clip(hb, 0, 255)
save(36, hb)
import json
from PIL import ImageDraw, ImageFilter
d = json.load(open("hairuv.json"))
ha = arr(tx("14.BL140101_HAIR"))
H, W = ha.shape[:2]
acc = np.zeros((H, W)); cnt = np.zeros((H, W))
for t in d["tris"]:
    z = np.mean([v[2] for v in t]); h = (z - d["zmin"]) / (d["zmax"] - d["zmin"])
    w = np.clip((0.55 - h) / 0.25, 0, 1); w = w * w * (3 - 2 * w)
    pts = [((v[0] % 1) * W, (v[1] % 1) * H) for v in t]
    x0 = max(int(min(p[0] for p in pts)) - 2, 0); y0 = max(int(min(p[1] for p in pts)) - 2, 0)
    x1 = min(int(max(p[0] for p in pts)) + 3, W); y1 = min(int(max(p[1] for p in pts)) + 3, H)
    if x1 <= x0 or y1 <= y0:
        continue
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in pts], fill=1, outline=1)
    m = np.array(m); acc[y0:y1, x0:x1] += m * w; cnt[y0:y1, x0:x1] += m
w = np.where(cnt > 0, acc / np.maximum(cnt, 1), 0)
w = np.array(Image.fromarray((w * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)))[..., None] / 255
hbig = np.array(Image.fromarray(hb.astype(np.uint8)).resize((W, H))).astype(float)
ha[..., :3] = ha[..., :3] * (1 - w) + hbig[..., :3] * w
save(9, ha)
save(37, arr(tx("31.BL140101_HAIRACCE_COL")))
n = np.zeros((16, 16, 4)); n[:] = (128, 128, 0, 255); save(38, n)
k = np.zeros((16, 16, 4)); k[:] = (0, 0, 0, 255); save(39, k)
# cape: coloured trim where the AO mask is set, galaxy elsewhere
b = arr(tx("23.BL140101_B_COL")); m = arr(tx("25.BL140101_B_AO"))[..., :1] / 255
gc = np.array(Image.fromarray(g.astype(np.uint8)).resize((b.shape[1], b.shape[0]))).astype(float)
cape = gc * (1 - m) + b * m
save(40, cape); save(41, shade(cape))

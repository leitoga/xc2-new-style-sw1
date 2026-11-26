"""extex.py model_name outdir : textures of a Switch 2 .wismt as <index>.<name>.png"""
import io, os, re, struct, sys
import numpy as np
from PIL import Image
from drsm import P, streams

FMT = {37: (4, 1, 28), 66: (8, 4, 71), 68: (16, 4, 77), 73: (8, 4, 80), 75: (16, 4, 83), 77: (16, 4, 98)}

def deswizzle(raw, w, h, fmt):
    bpb, bw, _ = FMT[fmt]
    wb, hb = (w + bw - 1) // bw, (h + bw - 1) // bw
    t = hb + hb // 2
    bh = 16 if t >= 128 else 8 if t >= 64 else 4 if t >= 32 else 2 if t >= 16 else 1
    gw = (wb * bpb + 63) // 64
    X, Y = np.meshgrid(np.arange(wb) * bpb, np.arange(hb))
    gob = (Y // (8 * bh)) * gw * 512 * bh + (X // 64) * 512 * bh + ((Y % (8 * bh)) // 8) * 512
    xx, yy = X % 64, Y % 8
    o = gob + ((xx % 64) // 32) * 256 + ((yy % 8) // 2) * 64 + ((xx % 32) // 16) * 32 + (yy % 2) * 16 + (xx % 16)
    a = np.frombuffer(raw, np.uint8)
    idx = o.reshape(-1)[:, None] + np.arange(bpb)
    assert idx.max() < len(a), (w, h, fmt, idx.max(), len(a))
    return a[idx].tobytes()

def to_image(data, w, h, fmt):
    dxgi = FMT[fmt][2]
    hdr = struct.pack("<4s7I44x", b"DDS ", 124, 0x81007, h, w, len(data), 0, 1)
    hdr += struct.pack("<2I4s5I", 32, 4, b"DX10", 0, 0, 0, 0, 0) + struct.pack("<5I", 0x1000, 0, 0, 0, 0)
    hdr += struct.pack("<5I", dxgi, 3, 0, 1, 0)
    return Image.open(io.BytesIO(hdr + data)).convert("RGBA")

def mibls(raw):
    out, i = [], raw.find(b"LBIM")
    while i >= 0:
        f = struct.unpack_from("<10I", raw, i - 36)
        end = i + 4
        start = end - (f[0] + 40 + 4095) // 4096 * 4096
        out.append(dict(w=f[2], h=f[3], fmt=f[6], data=raw[start:start + f[0]]))
        i = raw.find(b"LBIM", i + 4)
    return out

name, out = sys.argv[1], sys.argv[2]
d, s = streams(P + name + ".wismt")
low, mid = mibls(s[0][4]), mibls(s[1][4])
names = re.findall(rb"[A-Z][A-Za-z0-9_]*|temp\d+", d[: s[0][0]])
h = struct.unpack_from("<24I", d, 0)
# texture_ids: u16 array, one entry per middle texture
count = len(mid)
ids = None
for off in range(0x10, s[0][0] - 2 * count):
    v = struct.unpack_from("<%dH" % count, d, off)
    if len(set(v)) == count and max(v) < len(low) and sorted(v) == list(v):
        ids = v
        break
assert ids, "texture ids not found"
wimdo = open(P + name + ".wimdo", "rb").read()
tn = [m.group().decode() for m in re.finditer(rb"(?:BL|PC|SPACE|STAR|EX_|DEKO|CRISTAL|temp|MAT|COL_)[A-Za-z0-9_]*", wimdo)]
first = next(i for i, n in enumerate(tn) if n.startswith(("BL0", "BL1")))
tn = tn[first:]
os.makedirs(out, exist_ok=True)
for i, t in enumerate(low):
    w, h_, fmt, data = t["w"], t["h"], t["fmt"], t["data"]
    if i in ids:
        k = ids.index(i)
        m = mid[k]
        w, h_, fmt, data = m["w"], m["h"], m["fmt"], m["data"]
        if len(s) > 2 + k:
            w, h_, data = w * 2, h_ * 2, s[2 + k][4]
    label = tn[i] if i < len(tn) else f"tex{i}"
    try:
        to_image(deswizzle(data, w, h_, fmt), w, h_, fmt).save(f"{out}/{i}.{label}.png")
        print(i, label, w, h_, fmt)
    except Exception as e:
        print("FAIL", i, label, w, h_, fmt, repr(e)[:90])

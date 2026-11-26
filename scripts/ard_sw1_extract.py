import os, struct, subprocess, sys, zlib

R = "/home/leo/Games/XC2 RECOMP/XC2PC/romfs/romfs.bin"
ARD = 512
ARH, N = 11038102656, 2150288
f = open(R, "rb")
f.seek(ARH)
h = bytearray(f.read(N))
magic, _, nnodes, soff, slen, noff, nlen, foff, fcnt, key = struct.unpack_from("<4s9I", h, 0)
key ^= 0xF3F35353
for off, ln in ((soff, slen), (noff, nlen)):
    for i in range(off, off + ln, 4):
        struct.pack_into("<I", h, i, struct.unpack_from("<I", h, i)[0] ^ key)


def node(i):
    return struct.unpack_from("<ii", h, noff + i * 8)


def lookup(p):
    cur = i = 0
    while node(cur)[0] >= 0:
        n = node(cur)[0] ^ (ord(p[i]) if i < len(p) else 0)
        if node(n)[1] != cur:
            return None
        cur, i = n, i + 1
    o = soff - node(cur)[0]
    e = h.index(0, o)
    if p[i:] != h[o:e].decode():
        return None
    return struct.unpack_from("<I", h, e + 1)[0]


def read(p):
    fid = lookup(p)
    if fid is None:
        raise KeyError(p)
    off, csz, usz, typ, _ = struct.unpack_from("<QIIII", h, foff + fid * 24)
    f.seek(ARD + off)
    d = f.read(csz + (48 if usz else 0))
    if d[:4] == b"xbc1":
        t, u, c = struct.unpack_from("<III", d, 4)
        body = d[48:48 + c]
        if t == 1:
            d = zlib.decompress(body)
        else:
            d = subprocess.run(["zstd", "-d", "-c"], input=body, capture_output=True, check=True).stdout
    return d


if __name__ == "__main__":
    out = sys.argv[1]
    for p in sys.argv[2:]:
        try:
            d = read(p)
        except KeyError:
            print("no", p)
            continue
        q = os.path.join(out, p.lstrip("/"))
        os.makedirs(os.path.dirname(q), exist_ok=True)
        open(q, "wb").write(d)
        print("ok", p, len(d))

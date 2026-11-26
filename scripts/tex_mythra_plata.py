import glob, numpy as np
from PIL import Image
S = 1024
def layer(i):  # Switch 2 texture i of Mythra, resized
    return np.array(Image.open(glob.glob(f"nsM/{i}.*.png")[0]).convert("RGB").resize((S, S), Image.LANCZOS)).astype(float)
def save(i, a):
    a = np.clip(a, 0, 255); Image.fromarray(np.dstack([a, np.full(a.shape[:2], 255.0)]).astype(np.uint8), "RGBA").save(f"tex-m6/{i}.png")
# silver galaxy of the legs: grey-green silver, soft lighter clouds, faint lilac nebula, fine glints
clouds = np.clip(layer(26)[..., :1] / 255 * 1.2, 0, 1)
blobs = layer(23); blobs = np.clip(blobs.mean(-1, keepdims=True) / 90, 0, 1)
a = np.array((152, 166, 170), float) * (1 - clouds) + np.array((205, 214, 212), float) * clouds
neb = np.clip(0.35 + 0.65 * blobs, 0, 1)
a = a * (1 - 0.7 * neb) + np.array((146, 148, 190), float) * 0.7 * neb + clouds * 22
r = np.random.default_rng(11).random((S, S))[..., None]
a = a + (r > 0.9975) * 70
save(37, a); save(38, a * (0.86, 0.88, 0.94))       # lit colour and a bright "specular" for the metallic look
panel = np.zeros((16, 16, 3)) + (178, 185, 194)
save(41, panel); save(42, panel * 0.88)
chest = np.zeros((16, 16, 3)) + (150, 158, 170)
save(46, chest); save(47, chest * 0.9)

"""variant.py name base_rgb_expr moving_rgb_expr : v10 model with images 42 / 43 replaced.
Each expression is python on t (HxWx3 float, 0..255, the v10 texture)."""
import sys, os, numpy as np, bpy
sys.path.insert(0, "/home/leo/.config/blender/5.2/scripts/addons/xenoblade_blender")
import xc3_model_py as xm
xm = getattr(xm, "xc3_model_py", xm)
name, e42, e43 = sys.argv[sys.argv.index("--") + 1:]
r = xm.load_model("v10/bl000101.wimdo", None)
imgs = list(r.image_textures)
for i, expr in ((42, e42), (43, e43)):
    im = bpy.data.images.load(os.path.abspath(f"tex-v10/{i}.png"))
    w, h = im.size
    px = np.zeros(w * h * 4, np.float32)
    im.pixels.foreach_get(px)
    t = np.flip(px.reshape(h, w, 4), 0)[..., :3] * 255
    c = np.clip(eval(expr, {"t": t, "np": np}) + np.zeros_like(t), 0, 255) / 255
    a = np.dstack([c, np.ones((h, w))]).astype(np.float32)
    old = imgs[i]
    imgs[i] = xm.encode_images_rgbaf32([xm.EncodeSurfaceRgba32FloatArgs(
        w, h, 1, xm.ViewDimension.D2, old.image_format, True, np.ascontiguousarray(a).reshape(-1), old.name, old.usage)])[0]
r.image_textures = imgs
os.makedirs(f"var/{name}", exist_ok=True)
a, b = r.to_mxmd_model(xm.Mxmd.from_file("v10/bl000101.wimdo"), xm.Msrd.from_file("v10/bl000101.wismt"))
a.save(f"var/{name}/bl000101.wimdo")
b.save(f"var/{name}/bl000101.wismt")

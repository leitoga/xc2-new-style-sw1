"""postM3 plus: the skirt panel gets an alpha test with its dithered mask (image 49, no mipmaps)."""
import numpy as np
import postM3
from postM3 import body
from xenoblade_blender import xc3_model_py as xm
xm = getattr(xm, "xc3_model_py", xm)
def run(path, wanted):
    postM3.run(path, wanted)
    root = xm.load_model(path, None)
    images = list(root.image_textures)
    mask = images[49]
    px = np.array(xm.decode_images_rgbaf32([mask])[0], np.float32)
    px = px.reshape(mask.height, mask.width, 4)[:, :, :]
    px = np.where(px > 0.5, 1.0, 0.0).astype(np.float32)
    px[..., 3] = 1.0
    images[49] = xm.encode_images_rgbaf32([xm.EncodeSurfaceRgba32FloatArgs(
        mask.width, mask.height, 1, xm.ViewDimension.D2, mask.image_format, False,
        np.ascontiguousarray(px).reshape(-1), mask.name, mask.usage)])[0]
    root.image_textures = images
    done = 0
    for m in root.models.materials:
        if m.name == "Body_TS_ns72":
            m.alpha_test = xm.material.Texture(49, 0, 0)
            m.alpha_test_ref = 0.5
            flags = m.flags
            flags.alpha_mask = True
            flags.separate_mask = True
            m.flags = flags
            done += 1
            print("ALPHA", m.name, m.flags.alpha_mask, m.alpha_test.image_texture_index, getattr(m, "alpha_test_ref", None))
    assert done == 1
    a, b = root.to_mxmd_model(xm.Mxmd.from_file(path), xm.Msrd.from_file(path[:-6] + ".wismt"))
    a.save(path)
    b.save(path[:-6] + ".wismt")

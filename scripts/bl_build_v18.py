"""blender -b --factory-startup --python build.py -- original.wimdo textures_from.wimdo new.glb out.wimdo

New Style geometry on top of the Switch 1 model: every new mesh takes the slot
(flags, lod, ext, material) of an original LOD0 mesh; no materials are added.
"""
import os
import re
import shutil
import sys

import bpy

base, texsrc, glb, out, *rest = sys.argv[sys.argv.index("--") + 1:]
texdir = rest[0] if rest else None  # optional folder with <image index>.png overrides

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="xenoblade_blender")
from xenoblade_blender import xc3_model_py as xm
xm = getattr(xm, "xc3_model_py", xm)

# 0) Switch 1 model with the already prepared New Style textures
root = xm.load_model(base, None)
root.image_textures = xm.load_model(texsrc, None).image_textures
if texdir:
    import numpy as np
    images = list(root.image_textures)
    for f in sorted(os.listdir(texdir), key=lambda f: int(f.split(".")[0])):
        i = int(f.split(".")[0])
        assert i <= len(images)
        old = images[i] if i < len(images) else None
        im = bpy.data.images.load(os.path.join(texdir, f))
        w, h = im.size
        px = np.zeros(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        px = np.flip(px.reshape(h, w, 4), axis=0).reshape(-1)  # top row first
        args = xm.EncodeSurfaceRgba32FloatArgs(
            w, h, 1, xm.ViewDimension.D2, old.image_format if old else xm.ImageFormat.BC7Unorm,
            True, px, old.name if old else f"NS_{i}", old.usage if old else xm.material.TextureUsage.Col)
        new = xm.encode_images_rgbaf32([args])[0]
        if old:
            images[i] = new
        else:
            images.append(new)
        print("TEX", i, new.name, w, h)
    root.image_textures = images
os.makedirs(os.path.dirname(out), exist_ok=True)
tmp = os.path.join(os.path.dirname(out), "base_tex.wimdo")
mxmd = xm.Mxmd.from_file(base)
msrd = xm.Msrd.from_file(base[:-6] + ".wismt")
a, b = root.to_mxmd_model(mxmd, msrd)
a.save(tmp)
b.save(tmp[:-6] + ".wismt")
shutil.copy(base[:-6] + ".arc", tmp[:-6] + ".arc")

orig_meshes = list(root.models.models[0].meshes)
mats = [m.name for m in root.models.materials]

bpy.ops.import_scene.wimdo(filepath=tmp, files=[{"name": os.path.basename(tmp)}],
                           image_folder="", pack_images=False, import_all_meshes=False)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)

before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=glb)
imported = set(bpy.data.objects) - before


def matname(o):
    if not o.data.materials or o.data.materials[0] is None:
        return None
    return re.sub(r"\.\d+$", "", o.data.materials[0].name)


# glb material -> original mesh slot(s). Several slots = one per piece, in order.
SLOTS = {
    "_ho_face_TS1": [0], "_ho_face_TS1_shape": [1], "phong23_shape": [2],
    "_ho_eye_brm2_shape": [3], "_ho_eye_TS1": [4], "_ho_eye_brm2": [5], "phong37": [6],
    "_ho_mayu_TS5_shape": [7], "_ho_mayu_TS5_shape_clean": [83],
    "deko_aza_mat": [9, 8], "deko_aza_mat_clean": [81, 82], "phong34": [12],
    "EX_houtai_mat": [26], "_earring": [27, 29], "phong4": [28, 30],
}


def slot_for(name, nv):
    if name in SLOTS:
        s = SLOTS[name]
        slot = s[0]
        if len(s) > 1:
            SLOTS[name] = s[1:] + s[:1]
        return slot
    n = name.lower()
    if "hair" in n:
        return 11 if nv > 1900 else 10
    if "skin" in n:
        return 15
    if "gold" in n:
        return 17
    if name == "ho_red":
        return 18
    if name == "_phong22":
        return 22  # chest crystal
    if name == "body_blm":
        return 20  # glow lines
    if name == "phong38":
        return 24  # hair accessory, own texture (post.py)
    return 19  # white cloth; galaxy and cape get their own material (post.py)


meshes = [o for o in imported if o.type == "MESH"]
junk = [o for o in meshes if matname(o) is None]  # glTF bone-shape Icosphere
outlines = [o for o in meshes if matname(o) and "_outline" in matname(o)]
meshes = [o for o in meshes if o not in junk and o not in outlines]
outlined = {len(o.data.vertices): o for o in outlines}

meshes.sort(key=lambda o: o.name)
used = {}
for o in meshes:
    name = matname(o)
    nv = len(o.data.vertices)
    slot = slot_for(name, nv)
    om = orig_meshes[slot]
    mi = om.material_index

    world = o.matrix_world.copy()
    o.parent = arm
    o.matrix_world = world
    for md in list(o.modifiers):
        o.modifiers.remove(md)
    o.modifiers.new(name="Armature", type="ARMATURE").object = arm

    full = f"{mi}.{mats[mi]}"
    mat = bpy.data.materials.get(full)
    if mat is None:
        mat = bpy.data.materials.new(full)
        mat.use_nodes = True
    assert mat.name == full, (mat.name, full)
    o.data.materials.clear()
    o.data.materials.append(mat)

    # Morphs only on slots whose original mesh is flagged as morphed.
    morphed = bool(om.flags1 & 0x01000000)
    if o.data.shape_keys is not None and not morphed:
        o.shape_key_clear()
    if not o.data.uv_layers:
        # pieces without UVs would get zero tangents and render black: give them a planar projection
        layer = o.data.uv_layers.new(name="TexCoord0")
        for loop in o.data.loops:
            co = o.data.vertices[loop.vertex_index].co
            layer.data[loop.index].uv = ((co.x + co.y) * 4.0, (co.z + co.y * 0.5) * 4.0)
    for i, uv in enumerate(o.data.uv_layers):
        uv.name = f"TexCoord{i}"
    for i, c in enumerate(o.data.color_attributes):
        c.name = "VertexColor" if i == 0 else f"Color{i}"

    has_outline = outlined.pop(nv, None) is not None
    if has_outline:
        o.modifiers.new(name="Solidify", type="SOLIDIFY")
        col = o.data.color_attributes.new("OutlineVertexColor", "BYTE_COLOR", "CORNER")
        for d in col.data:
            d.color = (0.0, 0.0, 0.0, 0.5)

    k = used.get(slot, 0)
    used[slot] = k + 1
    o.name = f"{slot}.m{k}_{re.sub(r'[^A-Za-z0-9_]', '_', name)}"
    print("MAP", o.name, "mat", mi, mats[mi], "nv", nv, "morph", o.data.shape_keys is not None,
          "outline", has_outline)

print("outlines without a base mesh:", list(outlined))
drop = list(imported - set(meshes))
bpy.data.batch_remove(drop)

bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
r = bpy.ops.export_scene.wimdo(filepath=out, original_wimdo=tmp, export_images=False, image_folder="")
print("export", r, os.path.exists(out) and os.path.getsize(out))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import post18
post18.run(out)

"""blender -b --factory-startup --python build.py -- original.wimdo textures_from.wimdo new.glb out.wimdo

New Style geometry on top of the Switch 1 model: every new mesh takes the slot
(flags, lod, ext, material) of an original LOD0 mesh; no materials are added.
"""
import os
import re
import shutil
import sys

import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


SLOTS = {
    "_hikari_face_TS4": [14], "_hikari_face_TS4_shape": [16], "_hikari_eye_TS2": [12], "_hikari_eye_blm": [13],
    "_hikari_eye_blm_shape": [15], "phong21_shape": [17], "_hikari_mayu_TS_shape": [28],
    "_hikari_mayu_TS_shape_clean": [76], "deko_aza_mat": [26, 27], "deko_aza_mat_clean": [77, 78], "phong34": [18],
    "EX_houtai_mat": [7], "_earring1": [19, 21], "phong4": [20, 22], "_phong27": [23],
    "hikari_hair_new": [29], "hikari_hair_inside": [29], "Mt_body": [1], "Mt_skin": [3], "Metal_PBR": [0],
    "Mt_sky": [10], "Mt_sky_dark": [10], "Mt_pamts": [10], "Mt_mantA": [11], "Mt_holo": [5], "Mt_holo_B": [5], "Mt_chest": [10],
}


def slot_for(name, nv):
    s = SLOTS[name]
    slot = s[0]
    if len(s) > 1:
        SLOTS[name] = s[1:] + s[:1]
    return slot



# the dark-sky pieces on the chest are silver grey in Switch 2: split them from the ribbons and legs
chest_src = next(o for o in imported if o.type == "MESH" and o.data.materials and o.data.materials[0]
                 and o.data.materials[0].name.split(".")[0] == "Mt_sky_dark")
zs = [(chest_src.matrix_world @ v.co).z for v in chest_src.data.vertices]
print("SKYDARK height %.2f-%.2f" % (min(zs), max(zs)))
before_split = set(bpy.data.objects)
bpy.ops.object.select_all(action="DESELECT")
chest_src.select_set(True)
bpy.context.view_layer.objects.active = chest_src
for v in chest_src.data.vertices: v.select = False
for e in chest_src.data.edges: e.select = False
for poly in chest_src.data.polygons:
    poly.select = min((chest_src.matrix_world @ chest_src.data.vertices[i].co).z for i in poly.vertices) > 1.08
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.separate(type="SELECTED")
bpy.ops.object.mode_set(mode="OBJECT")
chest = (set(bpy.data.objects) - before_split).pop()
mat = bpy.data.materials.new("Mt_chest")
chest.data.materials.clear()
chest.data.materials.append(mat)
imported.add(chest)
print("CHEST verts", len(chest.data.vertices), "rest", len(chest_src.data.vertices))

meshes = [o for o in imported if o.type == "MESH"]
junk = [o for o in meshes if matname(o) is None]  # glTF bone-shape Icosphere
outlines = [o for o in meshes if matname(o) and "_outline" in matname(o)]
meshes = [o for o in meshes if o not in junk and o not in outlines]
outlined = {len(o.data.vertices): o for o in outlines}

meshes.sort(key=lambda o: o.name)
own = {}
used = {}
for o in meshes:
    name = matname(o)
    nv = len(o.data.vertices)
    slot = slot_for(name, nv)
    om = orig_meshes[slot]
    import postM3
    spec = {
        "hikari_hair_inside": ({0: 35}, None),
        "Metal_PBR": ({0: 36, 1: 45}, None),
        "Mt_sky": (postM3.body(37, 38), None),
        "Mt_sky_dark": (postM3.body(39, 40), None),
        "Mt_pamts": (postM3.body(41, 42), None),
        "Mt_chest": (postM3.body(46, 47), None),
        "Mt_holo": ({0: 43}, [0.0, 0.98, 0.78, 1.0]),
        "Mt_holo_B": ({0: 43}, [0.34, 0.98, 0.85, 1.0]),
    }.get(name)
    if spec:
        assert nv not in own, nv
        own[nv] = spec
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
    if name == "Mt_sky":  # vertical coordinate = height, for a clean gradient
        data = o.data.uv_layers[0].data
        for loop in o.data.loops:
            co = o.matrix_world @ o.data.vertices[loop.vertex_index].co
            data[loop.index].uv = ((co.x + co.y) * 1.5, min(max(co.z / 1.4, 0.005), 0.995))
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

postM3.run(out, own)

import bpy, sys, os, re

argv = sys.argv[sys.argv.index("--")+1:]
base_wimdo, glb, out, texdir = argv[0], argv[1], argv[2], argv[3]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="xenoblade_blender")

def load_tex(prefix):
    """busca un png con ese sufijo en texdir y lo carga"""
    for f in os.listdir(texdir):
        if prefix.lower() in f.lower() and f.lower().endswith(".png"):
            return bpy.data.images.load(os.path.join(texdir, f), check_existing=True)
    return None

COL  = load_tex("BL140101_COL")
NRM  = load_tex("BL140101_NRM")
GLO  = load_tex("BL140101_GLO.")
GLOC = load_tex("BL140101_GLOC")
MTL  = load_tex("BL140101_MTL")
SPM  = load_tex("BL140101_SPM") or load_tex("COL_PLUS2")
HAIR = load_tex("BL140101_HAIR.")
HAIRB= load_tex("BL140101_HAIRB")
HAIRA= load_tex("BL140101_HAIRACCE_COL")
HAIRAN=load_tex("BL140101_HAIRACCE_NRM")
FACE = load_tex("BL000101_FACE")
CONFIG = {"COL":COL,"NRM":NRM,"GLO":GLO,"GLOC":GLOC,"MTL":MTL,"SPM":SPM,"HAIR":HAIR,"HAIRB":HAIRB,"HAIRACCE":HAIRA,"HAIRACCEN":HAIRAN,"FACE":FACE}
print({k:(v.name if v else None) for k,v in CONFIG.items()})

bpy.ops.import_scene.wimdo(filepath=base_wimdo, files=[{"name": os.path.basename(base_wimdo)}],
                           image_folder="", pack_images=False, import_all_meshes=True)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
base_meshes = [o for o in bpy.data.objects if o.type == "MESH"]

bpy.ops.import_scene.gltf(filepath=glb)
new_meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name not in {m.name for m in base_meshes}]
new_arms = [o for o in bpy.data.objects if o.type == "ARMATURE" and o is not arm]
print("nuevos:", len(new_meshes))

def pick(name):
    n = name.lower(); outline = "outline" in n
    if "skin" in n:   return 18 if outline else 17
    if "hair" in n:   return 14 if outline else 13
    if "face" in n:   return 3 if outline else 1
    if "eye" in n:    return 7 if outline else 10
    if "mayu" in n:   return 9 if outline else 32
    if "gold" in n:   return 21 if outline else 20
    if "red" in n:    return 23 if outline else 22
    if "earring" in n:return 31
    if "houtai" in n: return 30
    if "deko" in n:   return 33
    if "cristal" in n or "space" in n: return 19 if outline else 16
    return 25 if outline else 24

def tex_for(mat_name, label):
    """elige textura segun familia de material y slot"""
    n = mat_name.lower()
    hair = ("hair" in n)
    if label == "s0":
        if "face" in n: return CONFIG["FACE"]
        if "hair" in n: return CONFIG["HAIR"]
        return CONFIG["COL"]
    if label == "s1": return CONFIG["GLO"]
    if label == "s2": return CONFIG["GLOC"]
    if label == "s3":
        if "hair" in n: return CONFIG["HAIRB"]
        return CONFIG["NRM"]
    if label == "s4": return CONFIG["MTL"]
    if label == "s5": return CONFIG["SPM"]
    if label == "s9": return CONFIG["NRM"]
    return None

MATCACHE = {}
for o in new_meshes:
    o.parent = arm; o.parent_type = "OBJECT"
    if not any(m.type == "ARMATURE" for m in o.modifiers):
        md = o.modifiers.new(name="Armature", type="ARMATURE"); md.object = arm
    src = o.material_slots[0].material.name if o.material_slots and o.material_slots[0].material else "default"
    src = re.sub(r"\.\d+$", "", src)
    idx = pick(src)
    key = (idx, src)
    new_mat = MATCACHE.get(key)
    if new_mat is None:
        base = next((m for m in bpy.data.materials if m.name.startswith(f"bl000101.{idx}.")), None)
        new_mat = bpy.data.materials.new(f"{idx}.{src.replace('.', '_')}")
        new_mat.use_nodes = True
        if base and base.use_nodes and base.node_tree:
            for nd in base.node_tree.nodes:
                if nd.type == "TEX_IMAGE":
                    nn = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
                    nn.label = nd.label
                    t = tex_for(src, nd.label or "")
                    nn.image = t if t else nd.image
        MATCACHE[key] = new_mat
    o.data.materials.clear(); o.data.materials.append(new_mat)
    o.name = re.sub(r"^\d+\.", "", o.name)
    for i, uv in enumerate(o.data.uv_layers): uv.name = f"TexCoord{i}"
    for i, c in enumerate(o.data.color_attributes): c.name = "VertexColor" if i == 0 else f"Color{i}"

for a in new_arms:
    for c in list(a.children): c.parent = arm
    bpy.data.objects.remove(a, do_unlink=True)
for o in base_meshes: bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
for o in bpy.data.objects: o.select_set(True)
bpy.context.view_layer.objects.active = arm
arm["original_wimdo"] = base_wimdo
os.makedirs(os.path.dirname(out), exist_ok=True)
r = bpy.ops.export_scene.wimdo(filepath=out, original_wimdo=base_wimdo, export_images=True, image_folder="")
print("export:", r, os.path.getsize(out) if os.path.exists(out) else 0)

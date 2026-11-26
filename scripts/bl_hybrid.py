import bpy, sys, os, re

argv = sys.argv[sys.argv.index("--")+1:]
base_wimdo, glb, out = argv[0], argv[1], argv[2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="xenoblade_blender")

# 1) modelo base de Switch 1 (armature + materiales/shaders validos)
bpy.ops.import_scene.wimdo(filepath=base_wimdo, files=[{"name": os.path.basename(base_wimdo)}],
                           image_folder="", pack_images=False, import_all_meshes=True)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
base_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
print("base:", arm.name, "meshes", len(base_meshes))

# 2) geometria nueva desde el glb
bpy.ops.import_scene.gltf(filepath=glb)
new_meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name not in {m.name for m in base_meshes}]
new_arms = [o for o in bpy.data.objects if o.type == "ARMATURE" and o is not arm]
print("nuevos meshes:", len(new_meshes), "armaduras extra:", [a.name for a in new_arms])

# mapas de material: nombre del material nuevo -> indice del material base de switch 1
MAP = [
    ("outline", {"skin": 18, "hair": 14, "eye": 7, "face": 3, "gold": 21, "red": 23, "white": 25, "default": 25}),
]
def pick(name):
    n = name.lower()
    outline = "outline" in n
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

MATCACHE = {}
# 3) reasignar: padre, modificador de armadura, materiales con prefijo de indice
for o in new_meshes:
    o.parent = arm
    o.parent_type = "OBJECT"
    if not any(m.type == "ARMATURE" for m in o.modifiers):
        m = o.modifiers.new(name="Armature", type="ARMATURE")
        m.object = arm
    src = o.material_slots[0].material.name if o.material_slots and o.material_slots[0].material else "default"
    src = re.sub(r"\.\d+$", "", src)
    idx = pick(src)
    base_name = bpy.data.materials[f"bl000101.{idx}." + bpy.data.materials.keys()[0].split(".")[2]] if False else None
    # buscar el material base por indice
    target = None
    for m in bpy.data.materials:
        if m.name.startswith(f"bl000101.{idx}."):
            target = m; break
    if target is None:
        print("  !! sin material base para", idx, src); continue
    key = (idx, src)
    new_mat = MATCACHE.get(key)
    if new_mat is None:
        new_mat = bpy.data.materials.new(f"{idx}.{src.replace(chr(46), chr(95))}")
        MATCACHE[key] = new_mat
        new_mat.use_nodes = True
    # copiar nodos del material base para conservar etiquetas s0..s9
    if new_mat.use_nodes and target.use_nodes and target.node_tree:
        for n in target.node_tree.nodes:
            if n.type == "TEX_IMAGE":
                nn = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
                nn.image = n.image; nn.label = n.label
    o.data.materials.clear()
    o.data.materials.append(new_mat)
    o.name = re.sub(r"^\d+\.", "", o.name)
    for i, uv in enumerate(o.data.uv_layers):
        uv.name = f"TexCoord{i}"
    for i, c in enumerate(o.data.color_attributes):
        c.name = "VertexColor" if i == 0 else f"Color{i}"

# 4) borrar armaduras extra del glb
for a in new_arms:
    for c in list(a.children):
        c.parent = arm
    bpy.data.objects.remove(a, do_unlink=True)

# 5) ocultar/eliminar los meshes del modelo base para que no se exporten duplicados
for o in base_meshes:
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
for o in bpy.data.objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
arm["original_wimdo"] = base_wimdo

os.makedirs(os.path.dirname(out), exist_ok=True)
r = bpy.ops.export_scene.wimdo(filepath=out, original_wimdo=base_wimdo, export_images=False, image_folder="")
print("export:", r, os.path.exists(out), os.path.getsize(out) if os.path.exists(out) else 0)

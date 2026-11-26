import bpy, sys, os

argv = sys.argv[sys.argv.index("--")+1:]
path = argv[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="xenoblade_blender")
bpy.ops.import_scene.wimdo(filepath=path, files=[{"name": os.path.basename(path)}], image_folder="", pack_images=False, import_all_meshes=True)

print("=== OBJETOS")
for o in bpy.data.objects:
    print(f"  {o.type:9} {o.name}")
print("=== MESHES / MATERIALES")
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    mats = [ms.material.name if ms.material else None for ms in o.material_slots]
    groups = len(o.vertex_groups)
    print(f"  {o.name}  verts={len(o.data.vertices)} uv={[u.name for u in o.data.uv_layers]} groups={groups} mats={mats}")
print("=== MATERIALES")
for m in bpy.data.materials:
    imgs = []
    for n in m.node_tree.nodes if m.use_nodes and m.node_tree else []:
        if n.type == "TEX_IMAGE" and n.image:
            imgs.append(f"{n.label or '?'}:{n.image.name}")
    print(f"  {m.name}  imgs={len(imgs)}  {imgs[:6]}")
print("=== ARMATURE")
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        print("  ", o.name, "bones", len(o.data.bones), "prop original_wimdo=", o.get("original_wimdo"))

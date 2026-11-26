import bpy, sys, os
argv = sys.argv[sys.argv.index("--")+1:]
src, out = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="xenoblade_blender")
bpy.ops.import_scene.wimdo(filepath=src, files=[{"name": os.path.basename(src)}],
                           image_folder="", pack_images=False, import_all_meshes=True)
print("importado: objetos", len(bpy.data.objects))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.data.objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
r = bpy.ops.export_scene.wimdo(filepath=out, original_wimdo=src, export_images=True, image_folder="")
print("export:", r, "->", os.path.exists(out), os.path.getsize(out) if os.path.exists(out) else 0)

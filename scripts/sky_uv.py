import bpy,sys,json
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index("--")+1])
tris=[]; zs=[]
for o in bpy.data.objects:
    if o.type!="MESH" or o.name.split(".")[0] != "Mt_sky": continue
    m=o.data; m.calc_loop_triangles(); uv=m.uv_layers[0].data
    for t in m.loop_triangles:
        p=[o.matrix_world@m.vertices[v].co for v in t.vertices]
        tris.append([[uv[l].uv.x,1-uv[l].uv.y,q.z] for l,q in zip(t.loops,p)]); zs+= [q.z for q in p]
json.dump({"tris":tris,"zmin":min(zs),"zmax":max(zs)},open("skyuv.json","w"))
print(len(tris),min(zs),max(zs))

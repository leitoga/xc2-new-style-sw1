"""tile.py in.wimdo out.wimdo factor : repeat the animated galaxy `factor` times over the suit."""
import sys, numpy as np
sys.path.insert(0, "/home/leo/.config/blender/5.2/scripts/addons/xenoblade_blender")
import xc3_model_py as xm
xm = getattr(xm, "xc3_model_py", xm)
src, dst, k = sys.argv[sys.argv.index("--") + 1:]
r = xm.load_model(src, None)
done = set()
for mesh in r.models.models[0].meshes:
    name = r.models.materials[mesh.material_index].name
    if name not in ("_phong22_ns404", "_phong22_ns1565") or mesh.vertex_buffer_index in done:
        continue
    done.add(mesh.vertex_buffer_index)
    for a in r.buffers.vertex_buffers[mesh.vertex_buffer_index].attributes:
        if str(a.attribute_type).endswith("TexCoord0"):
            a.data = np.array(a.data, np.float32) * float(k)
            print("UV", name, np.array(a.data).max(0))
assert len(done) == 2
a, b = r.to_mxmd_model(xm.Mxmd.from_file(src), xm.Msrd.from_file(src[:-6] + ".wismt"))
a.save(dst)
b.save(dst[:-6] + ".wismt")

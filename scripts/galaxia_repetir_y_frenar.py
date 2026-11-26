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
# slow down: scale the two small constants of the animated material (galaxy copies only)
for m in r.models.materials:
    if m.name in ("_phong22_ns404", "_phong22_ns1565"):
        w = np.array(m.work_values, np.float32)
        i = int(np.argmin(np.abs(w - 0.18)))
        assert abs(w[i] - 0.18) < 1e-4 and abs(w[i + 1] - 0.04) < 1e-4, w
        w[i : i + 2] *= 0.15
        m.work_values = w
        print("WV", m.name, w[: i + 3])
a, b = r.to_mxmd_model(xm.Mxmd.from_file(src), xm.Msrd.from_file(src[:-6] + ".wismt"))
a.save(dst)
b.save(dst[:-6] + ".wismt")

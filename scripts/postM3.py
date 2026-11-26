"""Private material copies for the Mythra pieces that sample their own image."""
import copy
import numpy as np
from xenoblade_blender import xc3_model_py as xm
xm = getattr(xm, "xc3_model_py", xm)
def body(c, s): return {0: c, 1: 44, 2: 44, 3: 44, 4: 44, 5: 44, 6: 44, 7: 44, 8: 43, 10: s}
def run(path, wanted):
    """wanted: vertex count -> (source material index or None, {slot: image}, colour or None)"""
    root = xm.load_model(path, None)
    mats, meshes = root.models.materials, root.models.models[0].meshes
    done = set()
    for mesh in meshes:
        if mats[mesh.material_index].name.endswith("_outline"):
            continue
        nv = len(root.buffers.vertex_buffers[mesh.vertex_buffer_index].attributes[0].data)
        if nv not in wanted or nv in done:
            continue
        done.add(nv)
        slots, colour = wanted[nv]
        m = copy.deepcopy(mats[mesh.material_index])
        for slot, image in slots.items():
            m.textures[slot].image_texture_index = image
        if colour:
            m.color = colour
        m.name = f"{m.name}_ns{nv}"
        mesh.material_index = len(mats)
        mats.append(m)
        print("MAT", nv, m.name, [t.image_texture_index for t in m.textures])
    assert done == set(wanted), set(wanted) - done
    # toon gradient rows of the Switch 2 materials (the rows exist in the Switch 1 table too)
    def row(m, value):
        w = np.array(m.work_values, np.float32)
        for c in m.work_callbacks:
            if str(c.callback_type).endswith("ToonId"):
                w[c.value : c.value + 2] = value
                m.work_values = w
                print("TOON", m.name, value)
    for i, m in enumerate(mats):
        if m.name.startswith("_hikari_hair_NEW2_ns"):
            row(m, 231)
        elif m.name == "_hikari_hair_NEW2":
            row(m, 228)
        elif m.name == "Body_TS":
            row(m, 234)
    a, b = root.to_mxmd_model(xm.Mxmd.from_file(path), xm.Msrd.from_file(path[:-6] + ".wismt"))
    a.save(path)
    b.save(path[:-6] + ".wismt")

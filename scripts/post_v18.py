"""post.py model.wimdo : give the pieces that use their own texture a private copy of the material."""
import sys, copy
from xenoblade_blender import xc3_model_py as xm
xm = getattr(xm, "xc3_model_py", xm)
def run(path):
    root = xm.load_model(path, None)
    mats = root.models.materials
    meshes = root.models.models[0].meshes
    # vertex count of the piece -> {texture slot: image index}
    galaxy = {0: 34, 1: 39, 2: 39, 3: 38, 5: 35}
    cape = {0: 40, 1: 44, 2: 45, 3: 38, 5: 41}
    tiara = {0: 46, 1: 47, 2: 48, 3: 49, 5: 50}
    lines = {0: 42, 1: 42, 2: 43, 3: 38, 5: 42}
    wanted = {404: galaxy, 1565: galaxy, 262: cape, 2231: {0: 36}, 312: tiara, 502: lines, 395: lines}
    cloth = next(i for i, m in enumerate(mats) if m.name == "ho_BL_TS2")
    cloth_flags = next((x.flags1, x.flags2) for x in meshes if x.material_index == cloth)
    done = set()
    for mesh in meshes:
        if mats[mesh.material_index].name.endswith("_outline"):
            continue
        nv = len(root.buffers.vertex_buffers[mesh.vertex_buffer_index].attributes[0].data)
        if nv not in wanted or nv in done:
            continue
        done.add(nv)
        source = mesh.material_index
        if wanted[nv] is lines or wanted[nv] is tiara:
            source = cloth
            mesh.flags1, mesh.flags2 = cloth_flags
        m = copy.deepcopy(mats[source])
        for slot, image in wanted[nv].items():
            m.textures[slot].image_texture_index = image
        m.name = f"{m.name}_ns{nv}"
        mesh.material_index = len(mats)
        mats.append(m)
        print("MAT", nv, m.name, [t.image_texture_index for t in m.textures])
    assert done == set(wanted), set(wanted) - done
    # Switch 1 row 0 shades to a dark blue-grey; Switch 2 shades Pyra's suit with row 228
    import numpy as np
    for m in mats:
        if m.name.startswith(("ho_BL_TS2", "ho_red1")):
            w = np.array(m.work_values, np.float32)
            for c in m.work_callbacks:
                if str(c.callback_type).endswith("ToonId"):
                    w[c.value : c.value + 2] = 228
                    m.work_values = w
                    print("TOON", m.name)
    a, b = root.to_mxmd_model(xm.Mxmd.from_file(path), xm.Msrd.from_file(path[:-6] + ".wismt"))
    a.save(path)
    b.save(path[:-6] + ".wismt")

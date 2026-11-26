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
    cape = {0: 40, 1: 39, 2: 39, 3: 38, 5: 41}
    animated = {0: 42, 1: 43}  # crystal material: base + moving layer
    crystal = next(i for i, m in enumerate(mats) if m.name == "_phong22")
    flags = next((x.flags1, x.flags2) for x in meshes if x.material_index == crystal)
    wanted = {404: animated, 1565: animated, 262: cape, 2231: {0: 36}, 312: {0: 37}}
    done = set()
    for mesh in meshes:
        if mats[mesh.material_index].name.endswith("_outline"):
            continue
        nv = len(root.buffers.vertex_buffers[mesh.vertex_buffer_index].attributes[0].data)
        if nv not in wanted or nv in done:
            continue
        done.add(nv)
        source = mesh.material_index
        if wanted[nv] is animated:
            source = crystal
            mesh.flags1, mesh.flags2 = flags
        m = copy.deepcopy(mats[source])
        for slot, image in wanted[nv].items():
            m.textures[slot].image_texture_index = image
        m.name = f"{m.name}_ns{nv}"
        mesh.material_index = len(mats)
        mats.append(m)
        print("MAT", nv, m.name, [t.image_texture_index for t in m.textures])
    assert done == set(wanted), set(wanted) - done
    a, b = root.to_mxmd_model(xm.Mxmd.from_file(path), xm.Msrd.from_file(path[:-6] + ".wismt"))
    a.save(path)
    b.save(path[:-6] + ".wismt")

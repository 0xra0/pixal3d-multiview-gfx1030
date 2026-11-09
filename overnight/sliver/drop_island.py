"""Drop detached islands far from the main body of a single-primitive GLB, keeping vertex sharing intact."""
import json, struct, sys
import numpy as np
src, dst = sys.argv[1:3]
b = open(src, "rb").read()
L = struct.unpack_from("<I", b, 12)[0]
j = json.loads(b[20:20 + L])
binstart = 20 + L + 8
prim = j["meshes"][0]["primitives"][0]
assert len(j["meshes"]) == 1 and len(j["meshes"][0]["primitives"]) == 1 and len(j["buffers"]) == 1
DT = {5125: np.uint32, 5126: np.float32, 5121: np.uint8, 5123: np.uint16}
NC = {"SCALAR": 1, "VEC3": 3, "VEC4": 4, "VEC2": 2}
def read(i):
    a = j["accessors"][i]; v = j["bufferViews"][a["bufferView"]]
    off = binstart + v.get("byteOffset", 0) + a.get("byteOffset", 0)
    assert "byteStride" not in v
    return np.frombuffer(b, DT[a["componentType"]], a["count"] * NC[a["type"]], off).reshape(a["count"], -1)
tri = read(prim["indices"]).reshape(-1, 3).astype(np.int64)
pos = read(prim["attributes"]["POSITION"])
n = len(pos)
parent = np.arange(n)
def find(x):
    root = x
    while parent[root] != root: root = parent[root]
    while parent[x] != root: parent[x], x = root, parent[x]
    return root
for a, c in ((0, 1), (1, 2)):
    for u, v in zip(tri[:, a], tri[:, c]):
        ru, rv = find(u), find(v)
        if ru != rv: parent[ru] = rv
roots = np.array([find(i) for i in range(n)])
troot = roots[tri[:, 0]]
ids, counts = np.unique(troot, return_counts=True)
main = ids[counts.argmax()]
mv = pos[np.unique(tri[troot == main])]
mlo, mhi = mv.min(0), mv.max(0); diag = np.linalg.norm(mhi - mlo)
drop = []
for r in ids:
    if r == main: continue
    v = pos[np.unique(tri[troot == r])]
    gap = np.maximum(np.maximum(mlo - v.max(0), v.min(0) - mhi), 0).max()
    if gap > .05 * diag:
        drop.append(r); print("drop island", int((troot == r).sum()), "triangles, gap", round(float(gap), 4))
keep_tri = tri[~np.isin(troot, drop)]
used = np.unique(keep_tri)
remap = -np.ones(n, np.int64); remap[used] = np.arange(len(used))
new = {"indices": remap[keep_tri].astype(np.uint32).reshape(-1, 1)}
for name, acc in prim["attributes"].items():
    new[name] = read(acc)[used]
blob, views, accessors = b"", [], []
order = [("indices", prim["indices"])] + list(prim["attributes"].items())
for name, acc in order:
    data = np.ascontiguousarray(new[name]); old = j["accessors"][acc]
    views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": data.nbytes})
    blob += data.tobytes(); blob += b"\0" * (-len(blob) % 4)
    a = {k: v for k, v in old.items() if k not in ("byteOffset", "min", "max")}
    a.update(bufferView=len(views) - 1, count=len(data))
    a["min"] = data.min(0).tolist(); a["max"] = data.max(0).tolist()
    if name == "indices": a["min"], a["max"] = [int(a["min"][0])], [int(a["max"][0])]
    accessors.append(a)
prim["indices"] = 0
prim["attributes"] = {name: i + 1 for i, (name, _) in enumerate(order[1:])}
j["accessors"], j["bufferViews"], j["buffers"] = accessors, views, [{"byteLength": len(blob)}]
js = json.dumps(j, separators=(",", ":")).encode(); js += b" " * (-len(js) % 4)
with open(dst, "wb") as f:
    f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
    f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
    f.write(struct.pack("<II", len(blob), 0x004E4942)); f.write(blob)
print("triangles", len(tri), "->", len(keep_tri), "vertices", n, "->", len(used))

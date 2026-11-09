import json, struct, sys
def bounds(path):
    with open(path, "rb") as f:
        f.read(12); n, _ = struct.unpack("<II", f.read(8)); g = json.loads(f.read(n))
    acc = [g["accessors"][p["attributes"]["POSITION"]] for m in g["meshes"] for p in m["primitives"]]
    lo = [min(a["min"][i] for a in acc) for i in range(3)]; hi = [max(a["max"][i] for a in acc) for i in range(3)]
    return lo, hi
for p in sys.argv[1:]:
    lo, hi = bounds(p); print([round(v, 4) for v in lo], [round(v, 4) for v in hi], p.split("/")[-3])

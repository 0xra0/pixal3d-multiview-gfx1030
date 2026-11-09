"""Compare two GLBs: accessor data, non-image JSON, and each image's bytes. usage: python3 -I glb_cmp.py old.glb new.glb [png...]"""
import json, struct, sys, hashlib
def load(p):
    b = open(p, "rb").read(); L = struct.unpack_from("<I", b, 12)[0]; j = json.loads(b[20:20 + L])
    bl = struct.unpack_from("<I", b, 20 + L)[0]; binc = b[28 + L:28 + L + bl]
    view = lambda i: binc[j["bufferViews"][i].get("byteOffset", 0):][:j["bufferViews"][i]["byteLength"]]
    return j, view
(ja, va), (jb, vb) = load(sys.argv[1]), load(sys.argv[2])
acc = all(va(a["bufferView"]) == vb(b["bufferView"]) and {k: v for k, v in a.items() if k != "bufferView"} == {k: v for k, v in b.items() if k != "bufferView"}
          for a, b in zip(ja["accessors"], jb["accessors"])) and len(ja["accessors"]) == len(jb["accessors"])
strip = lambda j: {k: v for k, v in j.items() if k not in ("bufferViews", "buffers", "accessors", "images", "asset")}
imgs = {i["name"]: (va(i["bufferView"]) == vb(k["bufferView"]), hashlib.sha256(vb(k["bufferView"])).hexdigest()[:12]) for i, k in zip(ja["images"], jb["images"])}
pngs = {hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]: p.split("/")[-2] + "/" + p.split("/")[-1] for p in sys.argv[3:]}
print("GLBCMP", sys.argv[2].split("/")[-1], "accessors identical", acc, "other json identical", strip(ja) == strip(jb),
      "images (same bytes?, new sha -> png)", {n: (s, pngs.get(h, h)) for n, (s, h) in imgs.items()})

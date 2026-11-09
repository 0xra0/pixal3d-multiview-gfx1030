import json,sys
r=json.load(open(sys.argv[1]))
def walk(o,p=""):
    if isinstance(o,dict):
        for k,v in o.items(): yield from walk(v,p+"."+k)
    elif isinstance(o,list):
        for i,v in enumerate(o[:8]): yield from walk(v,f"{p}[{i}]")
    else: yield p,o
for p,v in walk(r):
    if any(s in p.lower() for s in ("triangles","fallback","miss","issues")) and "parts[" not in p: print(p,v)

# Submit a ComfyUI API prompt and wait; prints output files.  usage: qrun.py prompt.json
import json, sys, time, urllib.request
P = json.load(open(sys.argv[1]))
req = urllib.request.Request("http://127.0.0.1:8188/prompt", json.dumps({"prompt": P}).encode(), {"Content-Type": "application/json"})
try:
    pid = json.load(urllib.request.urlopen(req))["prompt_id"]
except urllib.error.HTTPError as e:
    print(e.read().decode()[:3000]); sys.exit(1)
t0 = time.time()
while True:
    time.sleep(5)
    h = json.load(urllib.request.urlopen(f"http://127.0.0.1:8188/history/{pid}"))
    if pid in h:
        st = h[pid]["status"]
        print("status", st.get("status_str"), f"{time.time()-t0:.0f}s")
        for m in st.get("messages", []):
            if m[0] == "execution_error": print(json.dumps(m[1])[:2000])
        for nid, o in h[pid]["outputs"].items():
            for k in ("images", "3d", "result"):
                for it in o.get(k, []) if isinstance(o.get(k), list) else []:
                    print(nid, it if not isinstance(it, dict) else it.get("subfolder", "") + "/" + it.get("filename", ""))
        break

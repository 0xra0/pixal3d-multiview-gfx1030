"""Why does loading qwen-image-2.1-Q8_0.gguf (7.6 GB) to the GPU grow RAM past 18 GB?
Loads it the way ComfyUI does (same CLI flags) and dumps the Python stack every 30 s;
exits hard if RSS passes LIMIT_GB so earlyoom never has to step in."""
import os, sys, threading, time, faulthandler
EXTRA = os.environ.get("PROBE_FLAGS", "--disable-dynamic-vram --disable-async-offload --disable-pinned-memory").split()
sys.argv = ["main.py", "--reserve-vram", "2", "--cpu-vae", "--fp32-vae"] + EXTRA
os.chdir("/mnt/ssd/ComfyUI"); sys.path.insert(0, "/mnt/ssd/ComfyUI")
LIMIT_GB = float(os.environ.get("LIMIT_GB", "16"))
def rss_gb():
    for l in open("/proc/self/status"):
        if l.startswith("RssAnon"): return int(l.split()[1]) / 1e6
def watch():
    t0 = time.time()
    while True:
        r = rss_gb(); print(f"[probe] t={time.time()-t0:5.0f}s RssAnon={r:.2f} GB", flush=True)
        if r > LIMIT_GB:
            print("[probe] RSS limit hit, stack:", flush=True); faulthandler.dump_traceback(all_threads=True); os._exit(3)
        time.sleep(10)
threading.Thread(target=watch, daemon=True).start()
faulthandler.dump_traceback_later(45, repeat=True)
import comfy.options; comfy.options.enable_args_parsing()
import main  # noqa: applies env/setup like the server does (does not start it)
import nodes, asyncio
asyncio.run(nodes.load_custom_node("/mnt/ssd/ComfyUI/custom_nodes/ComfyUI-GGUF"))
import comfy.model_management as mm
t = time.time()
(model,) = nodes.NODE_CLASS_MAPPINGS["UnetLoaderGGUF"]().load_unet("qwen-image-2.1-Q8_0.gguf")
print(f"[probe] state dict loaded {time.time()-t:.0f}s RssAnon={rss_gb():.2f}", flush=True)
t = time.time()
mm.load_models_gpu([model])
faulthandler.cancel_dump_traceback_later()
print(f"[probe] load_models_gpu done {time.time()-t:.0f}s RssAnon={rss_gb():.2f} vram={mm.torch.cuda.memory_allocated()/1e9:.2f} GB", flush=True)

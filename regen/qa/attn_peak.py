"""Peak VRAM of UltraTex's single-block q/k/v hand-off, as written vs v made contiguous first (sizes of the failing run)."""
import torch
n, H, D = 68349, 32, 128
def norm(x):  # stands in for block.norm: an elementwise op, keeps the permuted layout
    return x * torch.rsqrt(x.float().pow(2).mean(-1, keepdim=True) + 1e-6).to(x.dtype)
def sla(q, k, v):  # what SpargeLinearAttention.forward does first
    q = q.contiguous(); k = k.contiguous(); v = v.contiguous()
    return torch.empty_like(q)
def run(early):
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    base = torch.cuda.memory_allocated()
    qkv = torch.randn(1, n, 3 * H * D, device="cuda", dtype=torch.float16)
    q, k, v = qkv.view(1, n, 3, H, -1).permute(2, 0, 3, 1, 4)
    del qkv
    q, k = norm(q), norm(k)
    if early:
        v = v.contiguous(); q = q.contiguous(); k = k.contiguous()
    out = sla(q, k, v)
    del q, k, v
    peak = (torch.cuda.max_memory_allocated() - base) / 2**20
    ref = out; del out
    return peak
unit = n * H * D * 2 / 2**20
for early in (False, True):
    print(f"{'v first' if early else 'as written'}: peak {run(early):.0f} MiB = {run(early) / unit:.1f} units of {unit:.0f} MiB")

"""Does UltraTex's vendored SLA Triton kernel compute correct attention on this GPU (ROCm)?

topk=1.0 keeps every key block, so the output must match exact attention up to bf16 rounding.
A large error there means the kernel itself is wrong here, not just approximate.
Also reports the per-query-block error at topk 0.2, ordered by token position: errors that
cluster in whole 128-token query blocks would paint rows (image tokens are row-major).
"""
import sys
import torch
import torch.nn.functional as F

sys.path.insert(0, "/mnt/ssd/ComfyUI/custom_nodes/ComfyUI-UltraTex/ultratex_core")
from sparse_attention import SparseLinearAttention  # noqa: E402

torch.manual_seed(0)
dev = "cuda"
print("torch", torch.__version__, "hip", torch.version.hip, torch.cuda.get_device_name(0))
import triton  # noqa: E402
print("triton", triton.__version__)


def rel(a, b):
    return ((a.float() - b.float()).norm() / b.float().norm()).item()


for L in (4096, 8192 + 77):  # second one has a partial tail block
    q, k, v = (torch.randn(1, 4, L, 128, device=dev, dtype=torch.bfloat16) for _ in range(3))
    # Give keys some structure so top-k selection is meaningful (smooth along the sequence, like images).
    k = (k + torch.cumsum(torch.randn_like(k.float()), dim=2).to(k.dtype) * 0.05).contiguous()
    ref = F.scaled_dot_product_attention(q.float(), k.float(), v.float()).to(torch.bfloat16)
    sdpa_bf16 = F.scaled_dot_product_attention(q, k, v)
    print(f"\nL={L}  bf16 SDPA vs fp32 ref: {rel(sdpa_bf16, ref):.4f}  (rounding floor)")
    for topk in (1.0, 0.5, 0.2):
        out = SparseLinearAttention(head_dim=128, topk=topk, BLKQ=128, BLKK=64)(q, k, v)
        torch.cuda.synchronize()
        err = rel(out, ref)
        per_block = ((out.float() - ref.float()).norm(dim=-1) / ref.float().norm(dim=-1).clamp_min(1e-6))
        per_block = per_block.mean(dim=(0, 1))[: (L // 128) * 128].view(-1, 128).mean(dim=1)
        print(f"  topk {topk:.1f}: rel err {err:.4f}  nan {torch.isnan(out).any().item()}  "
              f"per-128-block err min {per_block.min():.3f} max {per_block.max():.3f}")

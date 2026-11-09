"""Sparse-mode SLA vs exact attention restricted to the same block map (should match to bf16 rounding)."""
import sys
import torch
import torch.nn.functional as F
sys.path.insert(0, "/mnt/ssd/ComfyUI/custom_nodes/ComfyUI-UltraTex/ultratex_core")
from sparse_attention import SparseLinearAttention  # noqa: E402
from sparse_attention.utils import get_block_map, mean_pool  # noqa: E402

torch.manual_seed(0)
BQ, BK = 128, 64
for L in (4096, 8192 + 77):
    q, k, v = (torch.randn(1, 4, L, 128, device="cuda", dtype=torch.bfloat16) for _ in range(3))
    k = (k + torch.cumsum(torch.randn_like(k.float()), dim=2).to(k.dtype) * 0.05).contiguous()
    # pooled means vs torch
    pm = mean_pool(q, BQ).float()
    nb = (L + BQ - 1) // BQ
    qpad = F.pad(q.float(), (0, 0, 0, nb * BQ - L))
    cnt = torch.full((nb,), BQ, device="cuda"); cnt[-1] = L - (nb - 1) * BQ
    tm = qpad.view(1, 4, nb, BQ, 128).sum(3) / cnt[None, None, :, None]
    print(f"L={L} mean_pool rel err {((pm - tm).norm() / tm.norm()).item():.2e}")
    for topk in (0.2, 0.5):
        smap, lut, real = get_block_map(q, k, topk_ratio=topk, BLKQ=BQ, BLKK=BK)
        out = SparseLinearAttention(head_dim=128, topk=topk, BLKQ=BQ, BLKK=BK)(q, k, v)
        mask = smap.bool().repeat_interleave(BQ, 2).repeat_interleave(BK, 3)[:, :, :L, :L]
        ref = F.scaled_dot_product_attention(q.float(), k.float(), v.float(), attn_mask=mask)
        e = (out.float() - ref).norm(dim=-1) / ref.norm(dim=-1).clamp_min(1e-6)
        blk = e.mean((0, 1))[: (L // BQ) * BQ].view(-1, BQ).mean(1)
        print(f"  topk {topk}: kept {real}/{smap.shape[-1]} blocks, rel err {((out.float()-ref).norm()/ref.norm()).item():.4f}, "
              f"worst q-block {blk.max().item():.4f} at {blk.argmax().item()}")

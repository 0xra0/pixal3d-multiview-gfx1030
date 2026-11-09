#!/bin/bash
M=/mnt/ssd/ComfyUI/models
B=https://huggingface.co/Comfy-Org/Pixal3D/resolve/main
for f in vae/trellis_2_texture_vae_bf16.safetensors vae/trellis_2_shape_vae_bf16.safetensors clip_vision/dino_v3_L_naf_fp32.safetensors diffusion_models/pixal3d_multiview_int8_convrot.safetensors; do
  mkdir -p $M/$(dirname $f)
  [ -f $M/$f ] && { echo "have $f"; continue; }
  curl -fL -sS -C - -o $M/$f.part $B/$f && mv $M/$f.part $M/$f && echo "done $f" || echo "FAIL $f"
done
f=background_removal/birefnet.safetensors; mkdir -p $M/background_removal
[ -f $M/$f ] || { curl -fL -sS -C - -o $M/$f.part https://huggingface.co/Comfy-Org/BiRefNet/resolve/main/$f && mv $M/$f.part $M/$f && echo "done $f" || echo "FAIL $f"; }
echo ALLDONE

# Pixal3D MultiView GFX1030 Suite

[![Hardware: AMD Radeon RX 6800 (gfx1030)](https://img.shields.io/badge/GPU-AMD%20Radeon%20RX%206800%20(gfx1030)-ED1C24.svg)](https://www.amd.com/)
[![ROCm: HIP PyTorch](https://img.shields.io/badge/ROCm-6.x%20%7C%20HIP-005A9C.svg)](https://rocm.docs.amd.com/)
[![VRAM: 16 GB Optimized](https://img.shields.io/badge/VRAM-16%20GB%20Optimized-green.svg)]()
[![Engines: Cyberpunk 2077 | Witcher 3 | Generic](https://img.shields.io/badge/Engines-REDengine%20%7C%20Unreal%20%7C%20Unity%20%7C%20Godot-orange.svg)]()
[![Blender: 4.2+ LTS](https://img.shields.io/badge/Blender-4.2%2B%20%7C%205.2-E87D0D.svg)](https://www.blender.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An end-to-end, production-grade 3D generative asset pipeline combining **Pixal3D MultiView**, **Qwen-Image 2.1**, **UltraTex**, **LLM/VLM Visual Mesh Judging**, and automated **Blender/xatlas** game asset conditioning—fully tuned and optimized for **AMD Radeon RX 6800 (gfx1030, 16 GB VRAM)** on Linux ROCm.

This repository merges all core components, historical overnight evaluation runs, regeneration tools, visual test fixtures, quantization benchmarks, and high-poly sculpting experiments into a unified workspace.

---

## Table of Contents
- [Architecture & Workflow](#architecture--workflow)
- [Repository Structure](#repository-structure)
- [AMD gfx1030 / RX 6800 Optimizations](#amd-gfx1030--rx-6800-optimizations)
- [Installation & Setup](#installation--setup)
- [Quick Start & CLI Reference](#quick-start--cli-reference)
- [Detailed Module Documentation](#detailed-module-documentation)
  - [1. pixal3d-mv (Core Engine)](#1-pixal3d-mv-core-engine)
  - [2. judge-test (Visual Evaluation Fixtures)](#2-judge-test-visual-evaluation-fixtures)
  - [3. loopcut-local (Schemas & Agent Benchmarks)](#3-loopcut-local-schemas--agent-benchmarks)
  - [4. overnight (Batch Runs & SLA Benchmarks)](#4-overnight-batch-runs--sla-benchmarks)
  - [5. regen (Iterative Regeneration & Repair)](#5-regen-iterative-regeneration--repair)
  - [6. scratch (Early Tooling & Recovery Scripts)](#6-scratch-early-tooling--recovery-scripts)
  - [7. sculpt (Sculpting & Remesh Benchmarks)](#7-sculpt-sculpting--remesh-benchmarks)
- [Major Engineering Fixes](#major-engineering-fixes)
- [Game Engine Handoffs](#game-engine-handoffs)
- [GitHub Releases & Large Models](#github-releases--large-models)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Architecture & Workflow

```
                        ┌─────────────────────────────────────────────────────────┐
                        │                Single Front Image or Prompt             │
                        └────────────────────────────┬────────────────────────────┘
                                                     ▼
                        ┌─────────────────────────────────────────────────────────┐
                        │         Stage 1: Qwen-Image 2.1 Multi-View Sheet        │
                        │           (2048×1024 4-view: Front|Left|Back|Right)     │
                        └────────────────────────────┬────────────────────────────┘
                                                     ▼
                        ┌─────────────────────────────────────────────────────────┐
                        │         Stage 2: View Splitting & Alpha Cutout          │
                        │    (rembg background removal, transparency enforcement) │
                        └────────────────────────────┬────────────────────────────┘
                                                     ▼
                        ┌─────────────────────────────────────────────────────────┐
                        │         Stage 3: Pixal3D MultiView Reconstruction       │
                        │      (1536 cascade, corrected camera azimuths on ROCm)  │
                        └────────────────────────────┬────────────────────────────┘
                                                     ▼
                        ┌─────────────────────────────────────────────────────────┐
                        │      Stage 4: LLM/VLM Visual Mesh Judge (Multi-Try)     │
                        │   (CPU clay render + Strata / Antigravity Gemini 3.8)   │
                        └────────────────────────────┬────────────────────────────┘
                                                     ▼
                        ┌─────────────────────────────────────────────────────────┐
                        │    Stage 5: Automated Blender Geometry & xatlas UVs     │
                        │  (Manifold weld, bowtie repair, fold-free xatlas UV)    │
                        └────────────────────────────┬────────────────────────────┘
                                                     ▼
                        ┌─────────────────────────────────────────────────────────┐
                        │         Stage 6: UltraTex 2048/1536 PBR Texture Bake    │
                        │ (BaseColor, Roughness, Metalness, high-to-low AO/Normal)│
                        └────────────────────────────┬────────────────────────────┘
                                                     ▼
                        ┌─────────────────────────────────────────────────────────┐
                        │     Stage 7: Production LODs & Game Engine Packaging    │
                        │ (Cyberpunk 2077, Witcher 3 Remastered, Unreal, Unity)   │
                        └─────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
.
├── README.md                      # Complete system documentation
├── .gitignore                     # Git rules (excludes heavy temp arrays & caches)
├── judge-test/                    # Visual judge test suites and reference views
│   ├── bail_zoom.png              # Zoomed bail attachment test
│   ├── chest_v2.png               # Vampire chestplate ground truth
│   ├── medallion_m2.png           # Medallion v2 multi-view comparison
│   └── medallion_v2_views.png     # Reference 4-view cutout
├── loopcut-local/                 # Headless agent evaluation and schema dumps
│   ├── dump_schemas.py            # Tool schema character and token analyzer
│   ├── probe_gs.py                # Gaussian splatting / geometry probe
│   ├── prep_iq2_xs.sh             # llama.cpp IQ2_XS quantization script
│   ├── verify_facts*.py           # Blender 5.2 shader and geometry node facts
│   └── runs/                      # Agent execution logs and traces
├── overnight/                     # Extended overnight batch runs and benchmarks
│   ├── a1/ ... a8/                # Vampire chestplate multi-iteration runs
│   ├── n3/ ... n8/                # Medallion necklace multi-iteration runs
│   ├── backup_*_w3_*/             # Witcher 3 LOD and sliver-fix backports
│   ├── cmp_ref_front.py           # Horizontal band frequency artifact detector
│   ├── sla_check.py               # Sparse Linear Attention Triton kernel validator
│   ├── yaw_check.py               # Asset yaw and coordinate orientation validator
│   └── uvcmp.py                   # UV atlas distortion comparison
├── pixal3d-mv/                    # Core toolkit & production CLI
│   ├── pa.py                      # Main unified CLI orchestrator
│   ├── asset_bake.py              # Component-aware high-to-low PBR baking
│   ├── asset_config.py            # Preset LOD budgets and collision specifications
│   ├── asset_geometry.py          # Mesh cleanup, manifold repair, decimation
│   ├── asset_quality.py           # Validation gates, UV overlap tests, manifold check
│   ├── build_asset.py             # Asset build orchestrator
│   ├── mesh_judge.py              # LLM/VLM visual judge with CPU clay renderer
│   ├── prep_mesh.py               # Blender mesh preparation and repair pipeline
│   ├── redengine_handoff.py       # Cyberpunk 2077 & Witcher 3 handoff packager
│   ├── launch_comfy_qwen.sh       # Tuned ComfyUI launcher for gfx1030
│   ├── setup_models.sh            # Automated weight downloader (Qwen, mmproj, Trellis2)
│   ├── setup_ultratex.sh          # UltraTex node installer and patcher
│   └── workflows/                 # ComfyUI JSON workflows (Front, Sheet, Mesh, Texture)
├── regen/                         # Automated regeneration and mesh repair
│   ├── regen.sh                   # Full end-to-end regeneration pipeline
│   ├── rebuild_until_match.sh     # Iterative rebuild harness with automatic score matching
│   ├── repair/                    # Mesh decimation, smoothing, and flattening variants
│   ├── chain/                     # Procedural Blender chain generation for necklaces
│   └── qa/                        # Attention peak memory and VRAM analysis scripts
├── scratch/                       # Early prototyping and recovery utilities
│   ├── taper_tip.py               # Blade and weapon tip sharpening script
│   ├── split_sheet.py             # Standalone 4-view splitter
│   ├── gguf_load_probe.py         # GGUF tensor loading test
│   └── step*.json                 # Modular pipeline step descriptions
└── sculpt/                        # High-poly sculpting & UV benchmarks
    ├── mesh_stats.py              # Watertightness, edge CV, and cKDTree drift analyzer
    ├── top_level.py               # Scene hierarchy and mesh topology check
    └── uv*_sculpt.blend           # Blender sculpting and multires UV unwrap tests
```

---

## AMD gfx1030 / RX 6800 Optimizations

Generating 3D models with high-resolution diffusion and sparse 3D transformers on consumer AMD hardware requires precise memory and kernel tuning:

1. **16 GB VRAM Envelope**:
   - Standard setups assume 24 GB (RTX 3090/4090). On 16 GB, running UltraTex at 2048×2048 causes out-of-memory allocations in sparse attention query/key/value buffers.
   - We enforce `PA_TEXTURE_MEMORY_FACTOR=16`, offloading model weights dynamically to keep VRAM usage below 14.5 GB during peak cross-attention steps.
2. **ROCm ComfyUI Launcher (`launch_comfy_qwen.sh`)**:
   - Starts ComfyUI with `--cache-none` to prevent PyTorch CUDA/HIP caching memory leaks between pipeline stages.
   - Enforces real NAF (`TRELLIS2_REAL_NAF=1 TRELLIS2_NATTEN_IMPL=flex`) instead of legacy bilinear approximations.
3. **Qwen3-VL GGUF Q8 Text Encoder**:
   - Uses 8-bit quantized GGUF text encoders and vision projections. Integer int8 and w4a8 encoders suffer severe ROCm latency penalties, whereas Q8 achieves near-FP16 quality with fast execution.
4. **Sparse Linear Attention (SLA) Triton Kernel Validation**:
   - Includes `overnight/sla_check.py` to test Triton attention kernels under ROCm/HIP, ensuring relative errors against float32 reference implementations remain within numerical limits (`rel err < 0.05`).
5. **CPU Clay Renders for LLM Judging**:
   - Because ComfyUI holds VRAM locks during generation, `mesh_judge.py` renders 4-view clay evaluation images entirely on the CPU using a custom painter's algorithm, avoiding GPU VRAM contention.

---

## Installation & Setup

### Prerequisites
- **OS**: Linux (Ubuntu 22.04 / 24.04, Arch Linux, or openSUSE)
- **GPU**: AMD Radeon RX 6800 (gfx1030) or compatible RDNA2/RDNA3 card
- **ROCm**: ROCm 6.0+ with PyTorch HIP support
- **Blender**: Blender 4.2 LTS or Blender 5.2
- **Python**: Python 3.10 to 3.12 (inside a dedicated conda/venv environment)
- **External Tools**: `xatlas`, `trimesh`, `moderngl`, `scipy`, `Pillow`, `rembg`

### Step 1: Clone the Repository
```bash
git clone https://github.com/0xra0/pixal3d-multiview-gfx1030.git
cd pixal3d-multiview-gfx1030
```

### Step 2: Download Model Weights
Run the automated model setup script to download Qwen3-VL, Trellis2-GGUF, and Pixal3D multi-view components (~10 GB):
```bash
cd pixal3d-mv
bash setup_models.sh
```
Verify that all model files report `have` or `ok`.

### Step 3: Install UltraTex & Patches
```bash
cd pixal3d-mv
bash setup_ultratex.sh
```

### Step 4: System Self-Check
```bash
python3 pa.py check
```
This inspects all 15 model files, checks ComfyUI node registrations, validates xatlas and Blender paths, and tests the ComfyUI API endpoint.

---

## Quick Start & CLI Reference

All generation commands are driven by `pixal3d-mv/pa.py`. Set your Python environment pointing to your ComfyUI environment:
```bash
cd pixal3d-mv
export P=/mnt/ssd/conda-envs/ComfyUI/bin/python3.12
```

### 1. Launch ComfyUI
In a dedicated terminal:
```bash
bash launch_comfy_qwen.sh
```

### 2. End-to-End Generation (`all`)
Generate all 4 views, reconstruct 3D mesh with LLM judging, repair geometry, and bake PBR textures:
```bash
# From an existing concept image
$P pa.py all vampire_cuirass ~/refs/cuirass.png "ornate vampire chestplate with bat motifs and red gems"

# From text prompt alone
$P pa.py all gothic_lantern "text:an ornate gothic iron lantern with stained glass" "gothic lantern"
```

### 3. Step-by-Step Pipeline

#### A. Generate Front View from Text (Optional)
```bash
$P pa.py front lantern "an iron oil lantern with a glass body"
```

#### B. Generate 4-View Sheet
```bash
$P pa.py sheet lantern ~/refs/lantern.png "an iron oil lantern with a glass body"
```

#### C. Split and Transparent Cutout
```bash
$P pa.py split lantern /path/to/lantern_02_sheet_00001_.png
```

#### D. 3D Mesh Reconstruction with Multi-Try LLM Judge
```bash
$P pa.py mesh lantern --tries 3
```

#### E. High-Resolution Texture Baking (UltraTex)
```bash
$P pa.py texture lantern 2048
```

#### F. Production Game Asset Packaging
```bash
$P pa.py asset lantern --preset prop --engine witcher3 --pivot base
```

---

## Detailed Module Documentation

### 1. `pixal3d-mv` (Core Engine)
The primary production orchestrator.
- **`pa.py`**: Dispatches tasks to ComfyUI, monitors websocket progression, runs quality assurance gates, and triggers post-processing.
- **`mesh_judge.py`**: Visual LLM judge. Generates CPU clay renders from 4 cameras, creates a 2×4 comparison panel against reference views, and queries Strata, Antigravity CLI (Gemini 3.8 Flash High), or Codex. Re-rolls candidate seeds automatically if defects (melted relief, missing geometry, inverted orientation) are detected.
- **`asset_geometry.py`**: BMesh cleanup engine. Removes degenerate faces, isolates non-manifold vertices, fills small planar holes without self-capping, separates bowtie vertices, and decimates components proportionally.
- **`asset_bake.py`**: Computes high-to-low ray-cast PBR maps (Normal, Roughness, Metalness, Ambient Occlusion). Batches non-overlapping mesh components to accelerate CPU baking.
- **`xatlas_worker.py`**: Standalone xatlas process that isolates UV foldovers, normalizes island texel density, and enforces clean pixel padding.

### 2. `judge-test` (Visual Evaluation Fixtures)
Contains reference test sets and multi-view comparisons used to calibrate `mesh_judge.py`:
- `bail_zoom.png`: Extreme close-up of a pendant bail loop, testing whether small toroidal holes survive reconstruction.
- `chest_v2.png`: Ornate vampire cuirass reference used for evaluating fine filigree relief.
- `medallion_v2_views.png`: Pre-cut 4-view set for testing camera coordinate alignment.

### 3. `loopcut-local` (Schemas & Agent Benchmarks)
Tooling for automated agent evaluation and quantization:
- `dump_schemas.py`: Computes character and token budgets for OpenAI/Anthropic/Gemini tool calling schemas.
- `verify_facts*.py`: Automated unit tests verifying Blender 5.2 API behavior (Principled BSDF inputs, geometry node socket trees).
- `prep_iq2_xs.sh`: Shell script to quantize large foundation models into llama.cpp IQ2_XS format for minimal VRAM footprints.

### 4. `overnight` (Batch Runs & SLA Benchmarks)
Contains the benchmark corpus from extended overnight stress tests on gfx1030:
- **`cmp_ref_front.py`**: Measures horizontal band energy ($d/dy$ vs $d/dx$) on generated textures to catch striping artifacts.
- **`sla_check.py`**: Verifies Sparse Linear Attention numerical precision across sequence lengths up to 8,269 tokens.
- **`yaw_check.py`**: Verifies bounding box dimensions and enforces upright $Z$-up alignment across glTF exports.
- **Run Iterations (`a1`–`a8`, `n3`–`n8`)**: Historical test records containing full logs, vertex counts, LOD ratios, and `review.html` reports.

### 5. `regen` (Iterative Regeneration & Repair)
Automation scripts for unattended regeneration loops:
- **`regen.sh`**: Robust Bash script that boots ComfyUI, runs multi-try mesh generation, monitors for completion, triggers UltraTex baking, and compiles asset packages.
- **`rebuild_until_match.sh`**: Continues re-running generation until the LLM judge gives a passing score.
- **`repair/`**: Standalone GLB variants testing different Laplacian smoothing and planar flattening algorithms.

### 6. `scratch` (Early Tooling & Recovery Scripts)
Collection of specialized utilities developed during early bring-up:
- **`taper_tip.py`**: Fixes the known Pixal3D limitation where thin tips (such as sword blades or pendant points) are truncated. Uses vertex gradient slicing to taper ends to a sharp edge.
- **`split_sheet.py`**: Standalone OpenCV-based view splitter.
- **`gguf_load_probe.py`**: Tests low-level GGUF tensor loading on ROCm.

### 7. `sculpt` (Sculpting & Remesh Benchmarks)
Blender high-poly sculpting, remeshing experiments, and topological analytics:
- **`mesh_stats.py`**: Measures watertightness, boundary edges, non-manifold edges, edge length variance, and surface shape drift using scipy `cKDTree` sampling.
- **`top_level.py`**: Validates root object transforms and UV island packing efficiency.

---

## Major Engineering Fixes

### 1. Camera Projection Coordinate Inversion
- **Issue**: Pixal3D's internal coordinate system places the front camera at $-Y$. Consequently, the object's physical left side is at $+X$, where the azimuth 90° (`right_image`) camera is situated. Passing `left.png` to `left_image` mirrored both profiles and caused front ornaments (skulls, medallions) to be reconstructed onto the rear of the mesh.
- **Fix**: Calibrated `pa.py` to route `right.png` to node 2 (`left_image`) and `left.png` to node 4 (`right_image`), while updating `view_qa.py` and `mesh_judge.py` camera matrices to maintain consistent coordinate geometry.

### 2. Alpha Masking Cutout Threshold
- **Issue**: Qwen-Image 2.1 saves RGBA images with background alpha values of 247–255. The sheet splitter previously assumed any pixel $<255$ was already transparent, skipping `rembg` and passing white background blocks into the reconstruction network.
- **Fix**: Enforced a strict threshold requiring $\ge 1\%$ of pixels to have $\alpha \le 32$ before considering an image pre-cut.

### 3. Thin Shell LOD Decimation Collapse
- **Issue**: Thin double-sided shells (such as cuirasses and armour plates) collapsed through themselves when reduced to aggressive LOD budgets (LOD2/LOD3), creating faceted planar grey shards.
- **Fix**: Replaced naive global quadric decimation with component-aware, area-weighted allocation:
  $$\text{LOD Ratios} = [1.0, 0.5, 0.35, 0.15]$$
  Closed parts enforce a 4-triangle minimum to prevent topology self-destruction.

---

## Game Engine Handoffs

The suite outputs production-ready assets tailored for modern game engines:

### CD Projekt Red REDengine (Cyberpunk 2077 & Witcher 3)
```bash
python3 pa.py asset vampire_chestplate --engine witcher3 --pivot base
```
- Creates WolvenKit/REDkit-ready folder structures.
- Generates JSON asset manifests, collision geometry (`meshes/*_COL.glb`), and calibrated LOD0–LOD3 hierarchies.
- Maps PBR channels: `BaseColor`, `Normal` (DirectX/OpenGL conversion), `Roughness`, and `AmbientOcclusion`.

### Generic / Unreal Engine 5 / Unity / Godot
```bash
python3 pa.py asset prop_lantern --engine generic --preset prop
```
- Exports standard glTF 2.0 (`.glb`), FBX, and `.blend` files.
- Includes clean UV layout reports (`asset_report.json`) and an interactive HTML 3D viewer (`review.html`).

---

## GitHub Releases & Large Models

Large high-resolution 3D benchmark models and multires sculpt meshes exceed standard Git repository thresholds:
- **`sculpt-highres-models-v1.0.0.tar.gz`** (257 MB) is available directly under [GitHub Releases](https://github.com/0xra0/pixal3d-multiview-gfx1030/releases/tag/v1.0.0).
- Contents:
  - `top.glb` (131 MB raw sculpt)
  - `top_uv.glb` (162 MB unwrapped test mesh)
  - `top_v2.glb` (131 MB remeshed variant)

To download and extract:
```bash
gh release download v1.0.0 -p "sculpt-highres-models-v1.0.0.tar.gz"
tar -xzf sculpt-highres-models-v1.0.0.tar.gz -C sculpt/
```

---

## Troubleshooting

| Problem | Cause | Resolution |
|---|---|---|
| ComfyUI killed with exit 144 | Linux `earlyoom` triggered by RAM exhaustion | Close browser tabs, Blender, or games before running; reduce system RAM usage |
| Black or NaN textures in mesh | Random non-deterministic VAE NaN (approx 2 in 9 runs) | Re-run `pa.py mesh <name> --tries 3` with LLM judge enabled |
| UltraTex Out-of-Memory on GFX1030 | Sparse attention peak memory exceeded at 2048 | Set `PA_TEXTURE_MEMORY_FACTOR=16` or bake at 1536 resolution |
| Thin blade tip is blunt / cut off | Marching cubes voxel truncation at grid boundary | Run `python3 scratch/taper_tip.py <mesh.glb>` to restore sharp taper |
| Texture shows horizontal stripes | Triton SLA kernel rounding drift on ROCm | Check kernel status with `python3 overnight/sla_check.py` |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

### Acknowledgments
- **PixelArtistry**: Upstream Pixal3D MultiView architecture.
- **Trellis2 & ComfyUI-Trellis2-GGUF**: Foundation 3D representations.
- **Qwen-Image**: 4-view concept generation.
- **UltraTex**: Multi-view texture projection and refinement.

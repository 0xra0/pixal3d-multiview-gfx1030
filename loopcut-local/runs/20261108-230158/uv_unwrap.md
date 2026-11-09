## user
Give Crate a UV map: every face unwrapped, no overlapping islands, everything inside 0-1.

## assistant
Crate is a plain cube (8 verts, 6 faces). I'll smart-project its faces into a packed layout, then audit for overlaps and out-of-range UVs.

## tool uv_unwrap [done]
UV unwrap Crate (smart)

## assistant
Done — `Crate` now has a UV map named **UVMap**.

Audit at 1024 px with 8 px padding:
- 6 faces → 6 separate islands, one per face, smart-projected at 66°
- All UVs inside 0–1, no overlaps, no zero-area or flipped faces
- Stretch: 1.00 (none), even texel density 333 px/m across all faces
- Coverage 64% of the tile, min gutter 8.0 px, 4.0 px border margin

The cube looks unchanged in the viewport because there's no texture yet — the UVs only show up once an image or checker texture is applied. Say the word if you want a checker map to eyeball the layout, or a different packing (seams-based, or all six faces in a cross shape for a specific texture).

## changes
1 changed

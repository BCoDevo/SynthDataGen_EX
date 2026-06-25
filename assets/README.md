# Demo assets

Bundled teaching assets live here so students get everything in one clone.

## Environment — `Scene_Morning.blend`

| Path | Purpose |
|------|---------|
| `Scene_Morning.blend` | **Default demo environment** — terrain, materials, baked camera |
| `HDRs/*.hdr` | Sky lighting (`kloppenheim_02_2k`, `spruit_sunrise_4k`) |
| `Textures/` | Polyhaven-style ground/plank PBR maps + grass PNG |

**Default tank placement:** `[0, 3, 0.2]` on the open ground near the scene origin.

**Environment rotation:** The blend was authored for its baked scene camera (south side). The demo
uses a top-down camera from the southeast, so the script rotates all environment objects **+45.9°**
around the tank pivot so the scene faces the demo camera as it did originally.

## Tank — ZTZ-99A (`objects/tank/cn_ztz_99a/`)

| File | Purpose |
|------|---------|
| `ztz_99a_0.obj` + `.mtl` | **Default demo mesh** — intact tank |
| `textures/*.dds` | War Thunder DDS textures (color + normal maps) |

**Audit (checked in):**
- All 23 texture paths referenced in `ztz_99a_0.mtl` resolve to files on disk
- OBJ is ASCII format with relative `textures/` paths (loads correctly from its folder)
- Folder size: ~320 MB (large DDS color maps; expect slower first load)

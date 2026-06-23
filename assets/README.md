# Demo assets

Bundled teaching assets live here so students get everything in one clone.

## Environment — `Scene_Morning.blend`

| Path | Purpose |
|------|---------|
| `Scene_Morning.blend` | **Default demo environment** — terrain, materials, baked camera |
| `HDRs/*.hdr` | Sky lighting (`kloppenheim_02_2k`, `spruit_sunrise_4k`) |
| `Textures/` | Polyhaven-style ground/plank PBR maps + grass PNG |

**Audit (checked in):**
- Blend opens with `Morning` world + scene camera
- Texture paths in the `.blend` originally pointed at `Pictures\Blender Textures\` on the author's machine
- The render script **relinks** them to `assets/environment/Textures/` by filename at runtime
- Tree/leaf textures not bundled use fallbacks (planks/grass) so nothing renders purple
- Sky lighting comes from `HDRs/spruit_sunrise_4k.hdr` (scene has no lamps)
- ~93 MB total

**Default tank placement:** `[0, 3, 0.2]` on the open ground near the scene origin.

## Tank — ZTZ-99A (`objects/tank/cn_ztz_99a/`)

| File | Purpose |
|------|---------|
| `ztz_99a_0.obj` + `.mtl` | **Default demo mesh** — intact tank |
| `ztz_99a_dmg_0.obj` | Damaged variant (optional) |
| `ztz_99a_xray_0.obj` | X-ray variant (optional) |
| `textures/*.dds` | War Thunder DDS textures (color + normal maps) |
| `*.dmf` | War Thunder metadata — **not used** by BlenderProc |

**Audit (checked in):**
- All 23 texture paths referenced in `ztz_99a_0.mtl` resolve to files on disk
- OBJ is ASCII format with relative `textures/` paths (loads correctly from its folder)
- Folder size: ~320 MB (large DDS color maps; expect slower first load)

## Checklist before pushing

- [x] Environment blend + HDR/texture support files present
- [x] Tank OBJ + MTL + textures present and path-validated
- [x] Combined scene renders with bundled camera (`Camera.001`)
- [ ] License OK to redistribute War Thunder extracted assets for teaching

## Optional

Add `output/render.png` from a successful run as a README preview image.
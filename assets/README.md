# Demo assets

Bundled teaching assets live here so students get everything in one clone.

## Tank — ZTZ-99A (`cn_ztz_99a/`)

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

**Notes for instructors:**
- DDS textures load in Blender 4.x; if materials look flat, open the OBJ in Blender GUI once to verify node setup
- `ussr_camo_green.dds` is present but not directly mapped in the MTL (camo is baked into the `_c.dds` maps)
- AO maps (`*_ao.dds`) are included but not wired in the MTL — optional enhancement

## Environment (not bundled yet)

```
environment/scene.blend     # full Blender environment — add when ready
```

Until then, students can preview the tank with:

```bash
blenderproc run scripts/render_demo.py -- --tank-only
```

## Checklist before pushing

- [x] Tank OBJ + MTL + textures present and path-validated
- [ ] Environment opens cleanly in Blender 4.x+
- [ ] Combined scene looks correct when tank is at `[0, 0, 0]` (default)
- [ ] License OK to redistribute War Thunder extracted assets for teaching

## Optional

Add `output/render.png` from a successful run as a README preview image.
# Instructor notes — Synthetic data hands-on lesson

**Audience:** College graduates / technical professionals  
**Duration:** 60–90 min  
**Student doc:** `LESSON.md`  
**Live Blender demo:** `lesson/BLENDER_GUI.md` (instructor only — not a student Blender lab)

---

## Learning objectives

1. Locate bundled assets; explain MTL → relative texture paths
2. Run `blenderproc` with explicit flags (including the `--` separator)
3. Predict and verify `--tank-location` and `--camera-offset`
4. Explain instance segmentation → YOLO bbox export (see below)
5. Connect CLI parameters to the 3D scene (Exercise 8 live demo — observe, do not self-navigate Blender)

---

## Instance segmentation → YOLO (teach during Exercise 2; seg *visuals* in Exercise 5 / 7)

**Instance segmentation** assigns each pixel to an object instance ID (which mesh, which unique object in the scene). Unlike semantic segmentation (all “tanks” share one label), each tank *instance* gets its own ID.

**What this demo does:**

1. `label_tank_objects()` sets BlenderProc custom property `category_id = 1` on the tank mesh.
2. After the RGB render, `render_segmentation_maps()` runs a fast second pass:
   - Non-tank meshes are temporarily removed from the scene so only the tank is colorized.
   - BlenderProc renders an **instance ID map** (each object → unique color → decoded ID).
3. `yolo_writer.py` reads the tank instance mask, fits an axis-aligned **bounding box** in pixels, normalizes to `[0,1]`, and writes YOLO format: `class x_center y_center width height` (`category_id` 1 → YOLO class `0` / `tank`).

**Exercise 5 only** (`--export-seg`): `images/render_seg.png`, `images/render_seg_overlay.png`, and `instance_segmaps` merged into `0.hdf5` for Exercise 7 / `blenderproc vis hdf5`. Earlier lesson folders stay RGB + labels only.

Students do **not** draw boxes manually — segmentation is ground truth from the 3D mesh projection.

**One-liner for class:** “We render which pixels belong to the tank mesh, then take the smallest rectangle around those pixels.”

---

## HDR (teach at Exercise 1 or 5)

**HDR** = **High Dynamic Range** image. A 360° environment map (`.hdr`) storing bright sky and dim ground in one file. Blender uses it as the **world background** for image-based lighting — here it replaces scene lamps in `Scene_Morning.blend`.

Default file: `assets/environment/HDRs/spruit_sunrise_4k.hdr`

---

## Command reference (copy-ready)

Single-line commands for live copy-paste. Forward slashes work on Linux, macOS, and Windows.

**Checkpoint 0**

```bash
ls assets/environment assets/objects/tank/cn_ztz_99a
```

**Exercise 1**

```bash
python scripts/lesson_check.py paths --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr
```

**Exercise 2** — note the `--` before script flags; no `--export-seg`:

```bash
blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --resolution 640 360 --samples 16 --output output/lesson_02
```

```bash
python scripts/lesson_check.py render --output output/lesson_02
python scripts/visualize_yolo.py output/lesson_02/images/render.png
```

**Exercise 3** (three runs — baseline, raised Z, shifted X):

```bash
blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --resolution 640 360 --samples 16 --output output/lesson_03a
```

```bash
blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.8 --resolution 640 360 --samples 16 --output output/lesson_03b
```

```bash
blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 5 3 0.2 --resolution 640 360 --samples 16 --output output/lesson_03c
```

**Exercise 4a / 4b** (camera comparison):

```bash
blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --camera-offset 10 0 4 --resolution 640 360 --samples 16 --output output/lesson_04a
```

```bash
blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --camera-offset 0 -10 4 --resolution 640 360 --samples 16 --output output/lesson_04b
```

**Exercise 5** — full environment; **`--export-seg`** for seg PNGs + HDF5 (Exercise 7):

```bash
blenderproc run scripts/render_demo.py -- --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --resolution 1280 720 --samples 32 --export-seg --output output/lesson_05
```

```bash
python scripts/lesson_check.py render --output output/lesson_05
python scripts/visualize_yolo.py output/lesson_05/images/render.png
```

Live demo talking point: open `output/lesson_05/images/render_seg_overlay.png` next to `render_annotated.png`.

**Exercise 6** (example — brighter HDR; no `--export-seg`):

```bash
blenderproc run scripts/render_demo.py -- --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --hdr-strength 2.0 --resolution 640 360 --samples 16 --output output/lesson_06_hdr
```

**Exercise 7** — uses `lesson_05` HDF5

Inspect HDF5 structure:

```bash
python -c "import h5py; f=h5py.File('output/lesson_05/0.hdf5'); print(list(f.keys())); print(f['colors'].shape, f['colors'].dtype)"
```

View RGB + instance segmap:

```bash
blenderproc vis hdf5 output/lesson_05/0.hdf5
```

Export RGB to PNG:

```bash
python scripts/export_hdf5_image.py output/lesson_05/0.hdf5 -o output/lesson_05/from_hdf5.png
```

**Exercise 8 — live demo** (~5–10 min; see `lesson/BLENDER_GUI.md` for talking points):

```bash
blenderproc debug scripts/render_demo.py -- --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --camera-offset 10 -10 4
```

Scripting → **Run BlenderProc** → Layout → point at Outliner, transform, camera, textures → close Blender. Students watch; they do not drive the UI.

---

## Exercise 7 — Why HDF5 and PNG?

**HDF5** (`0.hdf5`) is BlenderProc’s native output: named arrays (RGB; with `--export-seg`, `instance_segmaps` too) in one machine-readable file per frame.

**PNG** (`render.png`, `images/render.png`) is added by our demo script for humans and trainers: double-click preview, YOLO folder layout (`images/` + `labels/`), easy sharing. Same RGB bytes as `colors` in the HDF5.

**Model answer for wrap-up:** *HDF5 is the structured frame archive for pipelines; PNG is a convenience copy of the RGB channel for viewing and YOLO tooling.*

| Format | Written by | Best for |
|--------|------------|----------|
| `0.hdf5` | BlenderProc (+ optional seg merge) | Pipelines, Exercise 7 viewer |
| `render.png` | `render_demo.py` | Quick visual check |
| `images/render.png` | `render_demo.py` | YOLO dataset layout |
| `images/render_seg_overlay.png` | `render_demo.py` with `--export-seg` | Exercise 5 live demo only |

---

## Answer key (short)

| Ex | Key points |
|----|------------|
| 1 | Paths in command reference above; MTL uses relative `textures/` |
| 2 | `--tank-only` = studio plane; gray floor; tank textures must load (not flat gray mesh) |
| 3 | Z↑ float; Z↓ clip; X/Y shift bbox center |
| 4 | `10 0 4` vs `0 -10 4` — different orbit sides; bbox size/shape changes with perspective |
| 5 | Texture relink + HDR sky; outdoor terrain vs studio; `--export-seg` → overlay PNG + HDF5 seg |
| 7 | HDF5 = pipeline archive; `instance_segmaps` only in `lesson_05`; `blenderproc vis hdf5` |
| 8 | Tank in Outliner = `--tank`; Transform ≈ `--tank-location`; demo camera = `--camera-offset` |

---

## Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Flat gray tank, `Cannot load image file` | Missing `--` or paths not resolved to repo root | Use `blenderproc run scripts/render_demo.py -- --tank-only ...` |
| `HDR not found` with relative path | Same CWD issue | Fixed by `resolve_project_path`; still need `--` separator |
| YOLO shows `0` not `tank` | `classes.txt` not found in lesson subfolder | Pass explicit image path under `output/lesson_XX/images/` |
| No `instance_segmaps` in HDF5 | Ran without `--export-seg` | Re-run Exercise 5 command with `--export-seg` |
| Debug shows empty scene | Script not run yet | Scripting → Run BlenderProc; wait for `Inspect-only` |
| `undo_push.poll() failed` during YOLO in debug | Segmap needs undo stack; unavailable in GUI debug | YOLO auto-skipped in debug; use `blenderproc run` for labels |
| Flags ignored | No `--` before `--tank-only` | BlenderProc consumes args; `--` separates blenderproc args from script args |
| PowerShell `ParserError` | Used `\` for line continuation | Use single-line commands in this doc |

---

## Pacing

| Block | Ex | Min |
|-------|-----|-----|
| Setup | 0–1 | 10 |
| First render + YOLO talk | 2 | 15 |
| Spatial | 3–4 | 20 |
| Full scene + seg overlay | 5 | 20 |
| Extension | 6–7 | 10 |
| Live Blender demo | 8 | 5–10 |
| Wrap-up | — | 10 |

---

## Assessment rubric

| Criterion | Meets |
|-----------|--------|
| Commands | Uses `--` separator; `lesson_check paths` passes |
| Textures | Tank renders with DDS materials in Ex 2 |
| Labels | `visualize_yolo` shows **tank** label |
| Live demo | Worksheet note from Exercise 8 (one CLI ↔ scene connection) |
| Concepts | Can explain instance seg → bbox in one sentence |

---

## Optional extensions

- Alternate HDR: `assets/environment/HDRs/kloppenheim_02_2k.hdr`
- **Extra credit — multi-view orbit** (production-style dataset):

```bash
blenderproc run scripts/render_demo.py -- --tank-only --views 8 --seed 42 --camera-distance 3 --camera-elevation 0.35 --camera-azimuth-jitter 15 --resolution 640 360 --samples 32 --output output/extra_multiview
```

Full scaling path: **[ROADMAP_TO_PRODUCTION.md](../ROADMAP_TO_PRODUCTION.md)**.

- Ultralytics: `yolo detect train data=output/lesson_05/data.yaml model=yolov8n.pt epochs=10 imgsz=640`
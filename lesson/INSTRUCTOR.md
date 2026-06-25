# Instructor notes — Synthetic data hands-on lesson

**Audience:** College graduates / technical professionals  
**Duration:** 60–90 min  
**Student doc:** `LESSON.md`  
**Blender GUI:** `lesson/BLENDER_GUI.md`

---

## Learning objectives

1. Locate bundled assets; explain MTL → relative texture paths
2. Run `blenderproc` with explicit flags (including the `--` separator)
3. Predict and verify `--tank-location` and `--camera-offset`
4. Explain instance segmentation → YOLO bbox export (see below)
5. Connect CLI parameters to Blender outliner / viewport (Exercise 8)

---

## Instance segmentation → YOLO (teach during Exercise 2)

**Instance segmentation** assigns each pixel to an object instance ID (which mesh, which unique object in the scene). Unlike semantic segmentation (all “tanks” share one label), each tank *instance* gets its own ID.

**What this demo does:**

1. `label_tank_objects()` sets BlenderProc custom property `category_id = 1` on the tank mesh.
2. After the RGB render, `render_segmentation_maps()` runs a fast second pass:
   - Non-tank meshes are temporarily removed from the scene so only the tank is colorized.
   - BlenderProc renders an **instance ID map** (each object → unique color → decoded ID).
3. `yolo_writer.py` reads the tank instance mask, fits an axis-aligned **bounding box** in pixels, normalizes to `[0,1]`, and writes YOLO format: `class x_center y_center width height`.
4. `category_id` 1 maps to YOLO class index `0` (`tank` in `classes.txt`).

Students do **not** draw boxes manually — segmentation is ground truth from the 3D mesh projection.

**One-liner for class:** “We render which pixels belong to the tank mesh, then take the smallest rectangle around those pixels.”

---

## HDR (teach at Exercise 1 or 5)

**HDR** = **High Dynamic Range** image. A 360° environment map (`.hdr`) storing bright sky and dim ground in one file. Blender uses it as the **world background** for image-based lighting — here it replaces scene lamps in `Scene_Morning.blend`.

Default file: `assets/environment/HDRs/spruit_sunrise_4k.hdr`

---

## Command reference (copy-ready)

Replace nothing — these are the intended classroom commands. Students still plug in `<tank-path>` etc. from Exercise 1.

**Checkpoint 0**

```bash
dir assets\environment
dir assets\objects\tank\cn_ztz_99a
```

**Exercise 1**

```bash
python scripts/lesson_check.py paths \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --environment assets/environment/Scene_Morning.blend \
  --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr
```

**Exercise 2** — note the `--` before script flags:

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_02
```

```bash
python scripts/lesson_check.py render --output output/lesson_02
python scripts/visualize_yolo.py output/lesson_02/images/render.png
```

Annotated image should show label **tank**, not `0` (reads `lesson_02/classes.txt`).

**Exercise 3** (example run B — raised Z):

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.8 \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_03b
```

**Exercise 4a / 4b** (camera comparison):

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --camera-offset 10 -10 4 \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_04a
```

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --camera-offset 20 -20 8 \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_04b
```

**Exercise 5**

```bash
blenderproc run scripts/render_demo.py -- \
  --environment assets/environment/Scene_Morning.blend \
  --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --resolution 1280 720 \
  --samples 32 \
  --output output/lesson_05
```

```bash
python scripts/lesson_check.py render --output output/lesson_05
python scripts/visualize_yolo.py output/lesson_05/images/render.png
```

**Exercise 6** (example — brighter HDR):

```bash
blenderproc run scripts/render_demo.py -- \
  --environment assets/environment/Scene_Morning.blend \
  --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --hdr-strength 2.0 \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_06_hdr
```

**Exercise 7**

```bash
python scripts/export_hdf5_image.py output/lesson_05/0.hdf5 -o output/lesson_05/from_hdf5.png
```

**Exercise 8** (pause before render — use with `debug`):

```bash
blenderproc debug scripts/render_demo.py -- \
  --environment assets/environment/Scene_Morning.blend \
  --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --camera-offset 10 -10 4 \
  --resolution 640 360 \
  --samples 4 \
  --pause-before-render \
  --output output/lesson_08
```

See `lesson/BLENDER_GUI.md` for viewport steps.

---

## Answer key (short)

| Ex | Key points |
|----|------------|
| 1 | Paths in command reference above; MTL uses relative `textures/` |
| 2 | `--tank-only` = studio plane; gray floor; tank textures must load (not flat gray mesh) |
| 3 | Z↑ float; Z↓ clip; X/Y shift bbox center |
| 4 | Higher camera Z → more top-down; bbox size changes with perspective |
| 5 | Texture relink + HDR sky; outdoor terrain vs studio |
| 8 | Transform panel matches `--tank-location`; camera view ≈ render PNG |

---

## Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Flat gray tank, `Cannot load image file` | Missing `--` or paths not resolved to repo root | Use `blenderproc run scripts/render_demo.py -- --tank-only ...`; update `render_demo.py` (chdir + relink) |
| `HDR not found` with relative path | Same CWD issue | Fixed by `resolve_project_path`; still need `--` separator |
| YOLO shows `0` not `tank` | `classes.txt` not found in lesson subfolder | Fixed in `visualize_yolo.py` — pass explicit image path under `output/lesson_XX/images/` |
| Debug shows empty scene | Script not run | Scripting → Run BlenderProc; wait for pause message |
| Flags ignored | No `--` before `--tank-only` | BlenderProc consumes args; `--` separates blenderproc args from script args |

---

## Pacing

| Block | Ex | Min |
|-------|-----|-----|
| Setup | 0–1 | 10 |
| First render + YOLO talk | 2 | 15 |
| Spatial | 3–4 | 20 |
| Full scene | 5 | 20 |
| Extension | 6–7 | 10 |
| Blender capstone | 8 | 15–20 |
| Wrap-up | — | 10 |

---

## Assessment rubric

| Criterion | Meets |
|-----------|--------|
| Commands | Uses `--` separator; `lesson_check paths` passes |
| Textures | Tank renders with DDS materials in Ex 2 |
| Labels | `visualize_yolo` shows **tank** label |
| Blender | Completes 8a with pause; worksheet note filled |
| Concepts | Can explain instance seg → bbox in one sentence |

---

## Optional extensions

- Alternate HDR: `assets/environment/HDRs/kloppenheim_02_2k.hdr`
- Batch random `--camera-offset` loop
- Ultralytics: `yolo detect train data=output/lesson_05/data.yaml model=yolov8n.pt epochs=10 imgsz=640`
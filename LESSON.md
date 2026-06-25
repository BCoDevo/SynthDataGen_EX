# Hands-on lesson: Synthetic data with BlenderProc

**Time:** ~60–90 minutes  
**Goal:** Generate a labeled synthetic image and understand what each pipeline parameter controls.

---

## What you are building

A minimal object-detection dataset:

| Piece | File | Role |
|-------|------|------|
| RGB image | `output/images/render.png` | Rendered camera view |
| Label | `output/labels/render.txt` | Tank bounding box (YOLO format) |
| Manifest | `output/data.yaml` | Dataset paths for trainers |

**Pipeline:** Blender loads a 3D scene → places a tank → renders RGB → instance segmentation → YOLO label export.

---

## Before you start

- Python 3.10+
- ~2 GB free disk (BlenderProc downloads Blender on first run)
- Terminal at the **repo root** (`scripts/`, `assets/` visible)

```bash
git clone https://github.com/BCoDevo/SynthDataGen_EX.git
cd SynthDataGen_EX
```

Create a venv, activate it, then:

```bash
pip install -r requirements.txt
```

**Checkpoint 0:** Confirm bundled assets are present:

```bash
# Windows
dir assets\environment
dir assets\objects\tank\cn_ztz_99a

# macOS / Linux
ls assets/environment
ls assets/objects/tank/cn_ztz_99a
```

---

## Exercise 1 — Map the assets (10 min)

Open `assets/README.md` and record these paths in `lesson/worksheet.md` (copy from `lesson/worksheet.example.md`). Paths are relative to the repo root.

| What | Path |
|------|------|
| Tank mesh (intact) | `assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj` |
| Environment scene | `assets/environment/Scene_Morning.blend` |
| HDR sky image | `assets/environment/HDRs/spruit_sunrise_4k.hdr` |
| Main render script | `scripts/render_demo.py` |

**HDR** (High Dynamic Range) — a 360° environment image used for sky lighting in Exercise 5. The `.hdr` format stores a wide brightness range so sun and ground can light the scene realistically.

**Question:** Why must `textures/` stay next to `ztz_99a_0.obj`?  
*(Check `ztz_99a_0.mtl`)*

```bash
python scripts/lesson_check.py paths --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr
```

---

## Exercise 2 — First render (tank-only, fast settings)

**Important:** BlenderProc requires `--` before script flags:

```text
blenderproc run scripts/render_demo.py -- --tank-only ...
```

Without `--`, flags may be swallowed and textures/HDR paths can fail to resolve.

**PowerShell:** use a **backtick** `` ` `` for line breaks, not `\` (which bash uses). Or put the command on one line:

```powershell
blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --resolution 640 360 --samples 16 --output output/lesson_02
```

Before running:

1. What does `--tank-only` skip?
2. Why use lower resolution and sample count for early iterations?

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_02
```

**Predict:** Studio ground plane or outdoor grass? Run and check.

```bash
python scripts/lesson_check.py render --output output/lesson_02
python scripts/visualize_yolo.py output/lesson_02/images/render.png
```

Compare `render.png` and `render_annotated.png`.

### YOLO labels (reference)

The render script exports detection labels automatically. Each line in `labels/render.txt`:

```
<class> <x_center> <y_center> <width> <height>
```

All coordinates are normalized to `[0, 1]` against image width/height. Class `0` is `tank` (see `output/classes.txt`).

Flow: `render_demo.py` tags the tank with `category_id` → instance segmentation pass → `yolo_writer.py` fits a bounding box → `visualize_yolo.py` draws it for review. No manual label editing required for this demo.

To decode a line programmatically: `python scripts/lesson_check.py yolo --label output/lesson_02/labels/render.txt --width 640 --height 360`

---

## Exercise 3 — Move the tank

Blender is **Z-up**. Default placement: `[0, 3, 0.2]` as `(x, y, z)`.

Run three variants with separate output folders:

| Run | `--tank-location` | Output folder |
|-----|-------------------|---------------|
| A | `0 3 0.2` | `output/lesson_03a` |
| B | `0 3 0.8` | `output/lesson_03b` |
| C | `5 3 0.2` | `output/lesson_03c` |

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.8 \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_03b
```

Note whether the tank clips, floats, or shifts in frame. Labels update automatically when YOLO export is enabled.

---

## Exercise 4 — Move the camera

The demo camera is computed from the tank center plus an offset (default `[10, -10, 4]` in `render_demo.py`):

```
camera_position = tank_center + camera_offset
```

Run two renders — same tank location, different offsets:

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --camera-offset 10 0 4 \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_04a
```

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --camera-offset 0 -10 4 \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_04b
```

How does camera position around the tank change framing? How does perspective affect the bounding box in `render.txt`?

---

## Exercise 5 — Full environment

Use explicit paths for all inputs. **`--export-seg`** adds segmentation previews and merges `instance_segmaps` into HDF5 (used in Exercise 7):

```bash
blenderproc run scripts/render_demo.py -- \
  --environment assets/environment/Scene_Morning.blend \
  --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --resolution 1280 720 \
  --samples 32 \
  --export-seg \
  --output output/lesson_05
```

While rendering, read the log:

- `Sky lighting: ...` — **HDR** world background; the blend has no scene lamps

```bash
python scripts/lesson_check.py render --output output/lesson_05
python scripts/visualize_yolo.py output/lesson_05/images/render.png
```

Compare `lesson_02` vs `lesson_05` — note two visual differences (lighting, terrain, clutter, etc.).

Open `images/render_seg_overlay.png` (green mask = pixels the YOLO box is fit from). Only `lesson_05` includes seg exports — earlier exercises stay minimal.

---

## Exercise 6 — Parameter experiment

Pick one flag from `--help` and run a comparison render (no `--export-seg` unless you want a second full-scene folder):

```bash
blenderproc run scripts/render_demo.py -- --help
```

| Idea | Flag |
|------|------|
| Brighter sky | `--hdr-strength` |
| Scene rotation | `--env-rotation` |
| Blend's baked camera | `--use-scene-camera` |
| Skip labels | `--no-yolo` |
| Higher quality | `--samples` |

Example — brighter HDR:

```bash
blenderproc run scripts/render_demo.py -- \
  --environment assets/environment/Scene_Morning.blend \
  --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --hdr-strength 2.0 \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_06_hdr
```

Record the parameter, value, and observable change in your worksheet.

---

## Exercise 7 — HDF5 export

Uses **`output/lesson_05`** from Exercise 5 (`--export-seg`).

```bash
python scripts/export_hdf5_image.py output/lesson_05/0.hdf5 -o output/lesson_05/from_hdf5.png
```

Confirm `from_hdf5.png` matches `render.png`.

```bash
python -c "import h5py; f=h5py.File('output/lesson_05/0.hdf5'); print(list(f.keys())); print(f['colors'].shape)"
```

Expect keys like `colors` and `instance_segmaps`. View in BlenderProc’s viewer:

```bash
blenderproc vis hdf5 output/lesson_05/0.hdf5
```

Why does the pipeline write both HDF5 and PNG?

---

## Exercise 8 — See the 3D scene (live demo)

**Instructor-led** — not a Blender skills lab. Watch the live demo: the same CLI flags from Exercises 3–5 show up as objects, transforms, and materials in Blender. You are not expected to navigate Blender on your own; use YouTube or Blender docs if you want to go deeper later.

**Instructor script:** `lesson/BLENDER_GUI.md`

While you watch, note how these connect:

| CLI flag | What you should see in Blender |
|----------|--------------------------------|
| `--tank` | Tank mesh in the Outliner — the object being labeled |
| `--tank-location` | Object transform location on the ground |
| `--camera-offset` | Demo camera framing (vs. the blend’s baked scene camera) |
| Environment + HDR | Outdoor terrain and lighting (not the studio plane from Exercise 2) |

**Worksheet:** Describe one thing visible in the live demo that the terminal log alone does not make obvious.

---

## Wrap-up

1. What is *synthetic* about this data vs. a real photograph?
2. What breaks if `--tank-location` Z is too low in the full environment?
3. Would a model trained only on `lesson_02` generalize to `lesson_05`? What would you randomize across 1000 images?
4. After Exercise 8 — what did the live demo clarify about `--camera-offset` or `--env-rotation`?

---

## Worksheet template

Copy `lesson/worksheet.example.md` → `lesson/worksheet.md`.

---

## Quick reference

| Task | Command |
|------|---------|
| Fast preview | `blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --resolution 640 360 --samples 16 --output output/lesson_02` |
| Full scene + seg | `blenderproc run scripts/render_demo.py -- --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --resolution 1280 720 --samples 32 --export-seg --output output/lesson_05` |
| Draw boxes | `python scripts/visualize_yolo.py output/lesson_05/images/render.png` |
| HDF5 viewer | `blenderproc vis hdf5 output/lesson_05/0.hdf5` |
| Self-check | `python scripts/lesson_check.py --help` |
| Live Blender demo (instructor) | `lesson/BLENDER_GUI.md` |

Troubleshooting: `README.md`, `output/README.md`. Instructor notes: `lesson/INSTRUCTOR.md`.
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
| Tank mesh (intact) | `assets/objects/tank/cn_ztz_99a/____________` |
| Environment scene | `assets/environment/____________________` |
| HDR sky image | `assets/environment/HDRs/________________` |
| Main render script | `scripts/________________` |

**HDR** (High Dynamic Range) — a 360° environment image used for sky lighting in Exercise 5. The `.hdr` format stores a wide brightness range so sun and ground can light the scene realistically.

**Question:** Why must `textures/` stay next to `ztz_99a_0.obj`?  
*(Check `ztz_99a_0.mtl`)*

```bash
python scripts/lesson_check.py paths --tank <tank-path> --environment <env-path> --hdr <hdr-path>
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
# Multi-line (PowerShell)
blenderproc run scripts/render_demo.py -- `
  --tank-only `
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj `
  --resolution 640 360 `
  --samples 16 `
  --output output/lesson_02
```

```powershell
# Single line — works everywhere
blenderproc run scripts/render_demo.py -- --tank-only --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --resolution 640 360 --samples 16 --output output/lesson_02
```

Before running:

1. What does `--tank-only` skip?
2. Why use lower resolution and sample count for early iterations?

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank <tank-path> \
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

| Run | `--tank-location` | Expected effect |
|-----|-------------------|-----------------|
| A | `0 3 0.2` | baseline |
| B | `0 3 0.8` | raised — float or sit higher? |
| C | `5 3 0.2` | shifted in X |

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank <tank-path> \
  --tank-location <X> <Y> <Z> \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_03
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
  --tank <tank-path> \
  --tank-location 0 3 0.2 \
  --camera-offset <X1> <Y1> <Z1> \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_04a
```

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank <tank-path> \
  --tank-location 0 3 0.2 \
  --camera-offset <X2> <Y2> <Z2> \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_04b
```

Which offset is more top-down? How does perspective affect the bounding box in `render.txt`?

---

## Exercise 5 — Full environment

Use explicit paths for all inputs:

```bash
blenderproc run scripts/render_demo.py -- \
  --environment <env-path> \
  --hdr <hdr-path> \
  --tank <tank-path> \
  --tank-location 0 3 0.2 \
  --resolution 1280 720 \
  --samples 32 \
  --output output/lesson_05
```

While rendering, read the log:

- `Sky lighting: ...` — **HDR** (High Dynamic Range) world background; the blend has no scene lamps

```bash
python scripts/lesson_check.py render --output output/lesson_05
python scripts/visualize_yolo.py output/lesson_05/images/render.png
```

Compare `lesson_02` vs `lesson_05` — note two visual differences (lighting, terrain, clutter, etc.).

---

## Exercise 6 — Parameter experiment

Pick one flag from `--help` and run a comparison render:

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

Record the parameter, value, and observable change in your worksheet.

---

## Exercise 7 — HDF5 export

```bash
python scripts/export_hdf5_image.py output/lesson_05/0.hdf5 -o output/lesson_05/from_hdf5.png
```

Confirm `from_hdf5.png` matches `render.png`. Optional:

```bash
python -c "import h5py; f=h5py.File('output/lesson_05/0.hdf5'); print(list(f.keys())); print(f['colors'].shape)"
```

Why does the pipeline write both HDF5 and PNG?

---

## Exercise 8 — Inspect assets in Blender (capstone)

Connect CLI parameters to the underlying 3D data. Step-by-step viewport guide: **`lesson/BLENDER_GUI.md`**.

### 8a — Pipeline view (`blenderproc debug`)

Opens the same Blender build used by your renders. **Debug defaults to inspect-only** — scene setup runs, no Cycles render, Blender stays open until you close it.

```bash
blenderproc debug scripts/render_demo.py -- --environment <env-path> --hdr <hdr-path> --tank <tank-path> --tank-location 0 3 0.2 --camera-offset 10 -10 4
```

Use forward slashes in paths on Linux and macOS.

1. Blender opens on **Scripting** (empty viewport — expected).
2. Click **Run BlenderProc**.
3. Log prints `Inspect-only — viewport set to camera view`. You should see the same framing as Exercise 5’s render (`lesson/BLENDER_GUI.md`). **Numpad 0** toggles camera view.
4. Close Blender when finished. Use `blenderproc run` when you need PNG labels, not debug.

### 8b — Environment `.blend` on its own

Open the scene file directly. Your first `blenderproc run` log prints the Blender path, e.g.:

```
Using blender in C:\Users\...\blender-4.2.1-windows-x64\...
```

Launch that `blender.exe` with the environment file (adjust path from your log):

```bash
# Windows example
& "<path-to-blender>\blender.exe" assets\environment\Scene_Morning.blend
```

```bash
# macOS / Linux example
"<path-to-blender>/blender" assets/environment/Scene_Morning.blend
```

In the viewport:

1. Find the scene camera object — how does its angle differ from the demo camera?
2. Navigate to roughly `[0, 3, 0]` on the ground — this is where the script places the tank pivot.
3. **Shading** workspace on terrain: note how materials reference texture files under `assets/environment/Textures/`.

### 8c — Tank mesh on its own

Import the OBJ into a fresh Blender session (**File → Import → Wavefront (.obj)**) or open via CLI:

```bash
/path/to/blender --factory-startup assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj
```

Check real-world scale (properties panel) and that DDS textures loaded on the materials. This is the asset your labels refer to — segmentation is mask-derived from this mesh in the render.

**Worksheet:** Sketch or describe one thing you saw in Blender that the CLI log alone does not make obvious.

---

## Wrap-up

1. What is *synthetic* about this data vs. a real photograph?
2. What breaks if `--tank-location` Z is too low in the full environment?
3. Would a model trained only on `lesson_02` generalize to `lesson_05`? What would you randomize across 1000 images?
4. After Exercise 8 — how does inspecting the `.blend` change how you would set `--camera-offset` or `--env-rotation`?

---

## Worksheet template

Copy `lesson/worksheet.example.md` → `lesson/worksheet.md`.

---

## Quick reference

| Task | Command |
|------|---------|
| Fast preview | `blenderproc run scripts/render_demo.py -- --tank-only --resolution 640 360 --samples 16` |
| Full scene | `blenderproc run scripts/render_demo.py` |
| Draw boxes | `python scripts/visualize_yolo.py <image.png>` |
| Self-check | `python scripts/lesson_check.py --help` |
| Blender inspect | `blenderproc debug scripts/render_demo.py -- --environment ... --tank ...` |
| GUI walkthrough | `lesson/BLENDER_GUI.md` |

Troubleshooting: `README.md`, `output/README.md`. Instructor notes: `lesson/INSTRUCTOR.md`.
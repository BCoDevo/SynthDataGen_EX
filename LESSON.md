# Hands-on lesson: Synthetic data with BlenderProc

**Time:** ~60–90 minutes  
**Goal:** Generate one labeled synthetic image and understand *what you changed* at each step.

This is not a copy-paste demo. You will look up paths, assemble commands, predict outcomes, and inspect files before moving on.

---

## What you are building

A tiny synthetic dataset for object detection:

| Piece | File | Role |
|-------|------|------|
| RGB image | `output/images/render.png` | What a camera “saw” |
| Label | `output/labels/render.txt` | Where the tank is (YOLO format) |
| Manifest | `output/data.yaml` | Tells trainers where images/labels live |

**Pipeline in one sentence:** Blender loads a 3D scene → places a tank → renders a photo → derives a bounding box from segmentation → writes YOLO text.

---

## Before you start

- Python 3.10+ installed
- ~2 GB free disk (BlenderProc downloads Blender on first run)
- Terminal open at the **repo root** (the folder that contains `scripts/` and `assets/`)

Clone once (this is the only full command block):

```bash
git clone https://github.com/BCoDevo/SynthDataGen_EX.git
cd SynthDataGen_EX
```

Then create and activate a venv, and install deps — but **type the activate line for your OS yourself** (see `README.md` if unsure), then:

```bash
pip install -r requirements.txt
```

**Checkpoint 0:** From the repo root, run:

```bash
# Windows PowerShell
dir assets\environment
dir assets\objects\tank\cn_ztz_99a

# macOS / Linux
ls assets/environment
ls assets/objects/tank/cn_ztz_99a
```

You should see `Scene_Morning.blend`, HDR files, and `ztz_99a_0.obj`.

---

## Exercise 1 — Map the assets (10 min)

Open `assets/README.md` and the folder tree. **Write these paths yourself** in `lesson/worksheet.md` (create it from the template below). Use **relative paths from the repo root**.

| What | Your path (you fill in) |
|------|-------------------------|
| Tank mesh (intact) | `assets/objects/tank/cn_ztz_99a/____________` |
| Environment scene | `assets/environment/____________________` |
| Morning HDR sky | `assets/environment/HDRs/________________` |
| Main render script | `scripts/________________` |

**Think:** Why does the tank path include `textures/` next to the `.obj`?  
*(Hint: open `ztz_99a_0.mtl` and look at one `map_Kd` line.)*

Verify your paths exist:

```bash
python scripts/lesson_check.py paths --tank <your-tank-path> --environment <your-env-path> --hdr <your-hdr-path>
```

All three should print `OK`.

---

## Exercise 2 — Your first render (tank only, fast settings)

Before running anything, answer in your worksheet:

1. What does `--tank-only` skip?
2. Why start with a low resolution and few samples?

Now **build this command yourself** — plug in the paths from Exercise 1 and choose the numbers in brackets:

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank <your-tank-path> \
  --resolution [WIDTH] [HEIGHT] \
  --samples [NUMBER] \
  --output output/lesson_02
```

Suggested first run: `640` `360` and `16` samples (fast). Do **not** use defaults yet — pick values explicitly.

**Predict:** Will the background be grass or a gray studio floor? Write your guess, then run.

**Checkpoint 2:**

```bash
python scripts/lesson_check.py render --output output/lesson_02
python scripts/visualize_yolo.py output/lesson_02/images/render.png
```

Open `output/lesson_02/render.png` and `output/lesson_02/images/render_annotated.png`.  
Was your prediction correct?

---

## Exercise 3 — Read a YOLO label by hand (15 min)

Open `output/lesson_02/labels/render.txt`. One line looks like:

```
<class> <x_center> <y_center> <width> <height>
```

All five numbers are **normalized** to 0–1 relative to image width/height.

Using your image size from Exercise 2, convert to pixels:

```
x_center_px = x_center × image_width
width_px    = width    × image_width
```

Do the same for `y_center` and `height` with image height.

**Worksheet tasks:**

1. Write the raw line from your `render.txt`.
2. Compute bounding box in pixels: `(x_min, y_min, x_max, y_max)`.
3. Open the annotated PNG — does the box cover the tank hull (not necessarily the whole image)?

Optional check:

```bash
python scripts/lesson_check.py yolo --label output/lesson_02/labels/render.txt --width 640 --height 360
```

This prints a decoded box so you can compare your math.

**Think:** Where in `scripts/render_demo.py` is the tank assigned `category_id`? What YOLO class index does that become?  
*(Trace: `TANK_CATEGORY_ID` → `yolo_writer.py` → `classes.txt`.)*

---

## Exercise 4 — Move the tank (cause and effect)

Blender uses **Z-up** coordinates (meters). Default placement is `[0, 3, 0.2]` → `(x, y, z)`.

Pick **three** different `--tank-location` values for three runs. Example pattern (change the numbers yourself):

| Run | `--tank-location` | What you expect to see |
|-----|-------------------|------------------------|
| A | `0 3 0.2` | baseline (compare to Ex 2) |
| B | `0 3 _____` | higher Z — tank floats or sits? |
| C | `_____ 3 0.2` | shifted X — tank moves where in frame? |

Use a **different** `--output` folder per run, e.g. `output/lesson_04a`.

Command shape (fill in everything in brackets):

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank <your-tank-path> \
  --tank-location [X] [Y] [Z] \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_04[b]
```

**Checkpoint 4:** For run B, did the tank clip into the ground or float? For run C, did the bounding box move in `render.txt`?

---

## Exercise 5 — Move the camera

The demo camera is **not** inside the `.blend` file. It is placed relative to the tank:

```
camera_position = tank_center + camera_offset
```

Default offset: `[10, -10, 4]` (see top of `scripts/render_demo.py`).

Run two renders with the **same** tank location but **different** offsets you choose:

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank <your-tank-path> \
  --tank-location 0 3 0.2 \
  --camera-offset [X1] [Y1] [Z1] \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_05a
```

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-only \
  --tank <your-tank-path> \
  --tank-location 0 3 0.2 \
  --camera-offset [X2] [Y2] [Z2] \
  --resolution 640 360 \
  --samples 16 \
  --output output/lesson_05b
```

**Worksheet:**

1. Which offset gave a more top-down view? How can you tell from the image?
2. Did the YOLO box width/height change a lot between 05a and 05b? Why?

---

## Exercise 6 — Full environment (manual paths)

Now use the morning scene. **Every asset path must be typed by you** — no defaults assumed.

```bash
blenderproc run scripts/render_demo.py -- \
  --environment <your-env-path> \
  --hdr <your-hdr-path> \
  --tank <your-tank-path> \
  --tank-location 0 3 0.2 \
  --resolution 1280 720 \
  --samples 32 \
  --output output/lesson_06
```

This takes longer than tank-only. While it runs, read the log:

- `Relinked N environment texture(s)` — what problem is the script solving?
- `Sky lighting: ...` — where does light come from if the blend has no lamps?

**Checkpoint 6:**

```bash
python scripts/lesson_check.py render --output output/lesson_06
python scripts/visualize_yolo.py output/lesson_06/images/render.png
```

**Compare** `lesson_02` vs `lesson_06` side by side. List **two** visual differences (lighting, ground, background clutter, etc.).

---

## Exercise 7 — One knob you choose

Pick **one** parameter to experiment with. Look up its flag with:

```bash
blenderproc run scripts/render_demo.py -- --help
```

Examples:

| Idea | Flag to try |
|------|-------------|
| Brighter sky | `--hdr-strength` |
| Scene faces another way | `--env-rotation` |
| Author’s camera from the blend | `--use-scene-camera` |
| Skip labels for speed | `--no-yolo` |
| Higher quality | `--samples` |

Document in your worksheet:

1. Parameter name and value you tried  
2. Command you ran (full line)  
3. What changed in the output  

---

## Exercise 8 — Inspect the data layer (no Blender)

```bash
python scripts/export_hdf5_image.py output/lesson_06/0.hdf5 -o output/lesson_06/from_hdf5.png
```

Open `from_hdf5.png` next to `render.png`. Should match.

Optional — peek inside HDF5:

```bash
python -c "import h5py; f=h5py.File('output/lesson_06/0.hdf5'); print(list(f.keys())); print(f['colors'].shape)"
```

**Think:** Why does the script write *both* HDF5 and PNG?

---

## Wrap-up questions

Answer in your own words (3–5 sentences each):

1. What is *synthetic* about this image compared to a photo from a phone?
2. What could go wrong if `--tank-location` Z is too low in the full environment?
3. If you trained YOLO on only `lesson_02` images, would it work on `lesson_06`? What would you change to make a more useful dataset?
4. What is one thing you would randomize if you generated **1000** images?

---

## Worksheet template

Copy this into `lesson/worksheet.md` and fill it in as you go:

```markdown
# SynthDataGen worksheet — [your name]

## Exercise 1 paths
- Tank: 
- Environment: 
- HDR: 
- Script: 

## Exercise 2
- Resolution: 
- Samples: 
- Prediction (background): 
- Actual result: 

## Exercise 3
- Raw label line: 
- Box in pixels (x_min, y_min, x_max, y_max): 

## Exercise 4
- Run B Z value:  Effect: 
- Run C X value:  Effect: 

## Exercise 5
- Offset A: 
- Offset B: 
- More top-down: 

## Exercise 6
- Two visual differences vs tank-only: 
  1. 
  2. 

## Exercise 7
- Parameter: 
- Value: 
- Observed change: 

## Wrap-up
1. 
2. 
3. 
4. 
```

---

## Quick reference (after you understand the lesson)

| Task | Command shape |
|------|----------------|
| Fast preview | `blenderproc run scripts/render_demo.py -- --tank-only --resolution 640 360 --samples 16` |
| Full scene | `blenderproc run scripts/render_demo.py` |
| Draw boxes | `python scripts/visualize_yolo.py <path-to-image.png>` |
| Self-check | `python scripts/lesson_check.py --help` |

Full troubleshooting: `README.md` and `output/README.md`.

Instructor notes and answer key: `lesson/INSTRUCTOR.md`.
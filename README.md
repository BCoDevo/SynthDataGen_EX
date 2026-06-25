# Synthetic Data Demo (BlenderProc)

Minimal hands-on demo for generating a single synthetic image: one War Thunder tank placed in a Blender environment.

Students clone the repo (assets are bundled — no separate download) and run one script.

**Teaching this in a class?** Start with **[LESSON.md](LESSON.md)** — guided exercises from asset paths through CLI parameters to a live Blender demo (instructor shows how flags map to the 3D scene). Instructor notes: `lesson/INSTRUCTOR.md`.

**Scaling beyond one frame?** See **[ROADMAP_TO_PRODUCTION.md](ROADMAP_TO_PRODUCTION.md)** — how this teaching example grows into a wider synthetic dataset pipeline.

## Project layout

```
.
├── assets/
│   ├── environment/
│   │   ├── Scene_Morning.blend  # bundled morning outdoor scene
│   │   ├── HDRs/                # sky HDRIs
│   │   └── Textures/            # PBR ground/material maps
│   └── objects/
│       └── tank/
│           └── cn_ztz_99a/      # bundled ZTZ-99A (War Thunder export)
│               └── ztz_99a_0.obj
├── scripts/
│   ├── render_demo.py           # the demo pipeline (+ YOLO labels)
│   ├── yolo_writer.py           # instance seg → YOLO txt
│   ├── visualize_yolo.py        # draw boxes on render (no Blender)
│   ├── export_hdf5_image.py     # HDF5 → PNG/JPG (no Blender needed)
│   └── lesson_check.py          # self-check for LESSON.md exercises
├── output/                      # renders land here (see output/README.md)
├── lesson/                      # worksheet template + instructor notes
├── LESSON.md                    # hands-on student workbook (~60–90 min)
├── ROADMAP_TO_PRODUCTION.md     # scaling the demo to a production SDG pipeline
├── requirements.txt
└── README.md
```

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/BCoDevo/SynthDataGen_EX.git
cd SynthDataGen_EX

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

On first run, BlenderProc downloads Blender automatically (~500 MB). This is normal.

### 2. Render tank in environment (default)

```bash
blenderproc run scripts/render_demo.py
```

Uses `Scene_Morning.blend` with a **top-down demo camera** (same framing as `--tank-only`). Tank is placed at `[0, 3, 0.2]` by default. Default resolution is **1920×1080** at 128 Cycles samples — expect ~1 minute on a mid-range GPU.

### 3. Tank-only preview (no environment)

```bash
blenderproc run scripts/render_demo.py -- --tank-only
```

### 4. Outputs

Every successful render writes (see `output/README.md` for details):

- `output/render.png` — quick visual check
- `output/images/render.png` — same image, YOLO dataset layout
- `output/0.hdf5` — BlenderProc frame (RGB; add `--export-seg` for `instance_segmaps` — see Exercise 5 in `LESSON.md`)
- `output/labels/render.txt` — YOLO bbox labels (on by default; disable with `--no-yolo`)
- `output/data.yaml` — YOLO dataset config

Preview annotations (run after `blenderproc run ...` — does not re-render):

```bash
python scripts/visualize_yolo.py
```

**Export PNG from an existing HDF5** (e.g. after `blenderproc quickstart`):

```bash
python scripts/export_hdf5_image.py output/0.hdf5
```

### 5. Live Blender demo (instructors)

`blenderproc debug` loads the script for a **live class demo** — see `lesson/BLENDER_GUI.md`. Not required for students to operate Blender themselves.

## Customization

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-location 0 5 0.3 \
  --camera-offset 8 -8 9 \
  --use-scene-camera \
  --resolution 1920 1080 \
  --samples 256 \
  --no-yolo \
  --output output/run_01
```

Edit the constants at the top of `scripts/render_demo.py` to change default tank placement, environment rotation, and fallback camera.

## Asset prep tips

**Environment (`Scene_Morning.blend`)**
- Keep `HDRs/` and `Textures/` alongside the blend file so relative paths resolve
- The **demo camera** frames the tank from above by default; pass `--use-scene-camera` for the blend's baked camera
- Environment objects are rotated **+45.9°** on Z around the tank pivot so the scene faces the demo camera (override with `--env-rotation`)

**Tank (War Thunder export)**
- Default mesh: `ztz_99a_0.obj` with DDS textures in `textures/`
- Adjust `--tank-location` if the tank floats or clips into terrain

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Environment not found` | Check `assets/environment/Scene_Morning.blend` exists |
| `Tank asset not found` | Check `assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj` exists |
| Only `.hdf5`, no PNG | Run `python scripts/export_hdf5_image.py output/0.hdf5` |
| Tank invisible / wrong size | Adjust `--tank-location` |
| Wrong framing | Adjust `--camera-offset` (default `10 -10 4`) or try `--use-scene-camera` |
| Purple grass / missing textures | Ensure `Textures/` and `HDRs/` stay next to `Scene_Morning.blend` |
| Flat / dark lighting | Script applies `spruit_sunrise_4k.hdr` automatically; try `--hdr-strength 2.0` |
| Render looks grainy | Default is 128 samples + OPTIX denoise; try `--samples 256` |
| Render takes forever | Scene has a 250-frame timeline; script resets to 1 frame |
| First run is slow | BlenderProc is downloading Blender |
| YOLO step fails on large scenes | Fixed in current script — update repo; or skip with `--no-yolo` |

## License

Demo code: MIT (suggested). BlenderProc is [GPL-3.0](https://github.com/DLR-RM/BlenderProc). War Thunder asset usage must comply with Gaijin's terms — use only assets you are permitted to redistribute for teaching.
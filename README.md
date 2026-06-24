# Synthetic Data Demo (BlenderProc)

Minimal hands-on demo for generating a single synthetic image: one War Thunder tank placed in a Blender environment.

Students clone the repo, pull bundled test assets, and run one script.

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
│   └── export_hdf5_image.py     # HDF5 → PNG/JPG (no Blender needed)
├── output/                      # renders land here (see output/README.md)
├── requirements.txt
└── README.md
```

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/BCoDevo/SynthDataGen_EX.git
cd synthetic-data-demo

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

Uses `Scene_Morning.blend` with a **top-down demo camera** (same framing as `--tank-only`). Tank is placed at `[0, 3, 0.2]` by default.

### 3. Tank-only preview (no environment)

```bash
blenderproc run scripts/render_demo.py -- --tank-only
```

Outputs (see `output/README.md` for details):

- `output/render.png` — quick visual check
- `output/0.hdf5` — full BlenderProc frame
- `output/labels/render.txt` — YOLO bbox labels (on by default)
- `output/data.yaml` — YOLO dataset config

Preview annotations (run after `blenderproc run ...` — does not re-render):

```bash
python scripts/visualize_yolo.py
```

**Export PNG from an existing HDF5** (e.g. after `blenderproc quickstart`):

```bash
python scripts/export_hdf5_image.py output/0.hdf5
```

### 4. Debug in Blender GUI (optional)

```bash
blenderproc debug scripts/render_demo.py
```

Opens Blender with the script loaded. Press **Run BlenderProc** in the scripting tab.

## Customization

```bash
blenderproc run scripts/render_demo.py -- \
  --tank-location 0 5 0.3 \
  --camera-offset 8 -8 9 \
  --use-scene-camera \
  --resolution 1920 1080 \
  --output output/run_01
```

Edit the constants at the top of `scripts/render_demo.py` to change default tank placement and fallback camera.

## Asset prep tips

**Environment (`Scene_Morning.blend`)**
- Keep `HDRs/` and `Textures/` alongside the blend file so relative paths resolve
- Default camera auto-frames the tank from above; pass `--use-scene-camera` for the blend's baked camera

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

## License

Demo code: MIT (suggested). BlenderProc is [GPL-3.0](https://github.com/DLR-RM/BlenderProc). War Thunder asset usage must comply with Gaijin's terms — use only assets you are permitted to redistribute for teaching.
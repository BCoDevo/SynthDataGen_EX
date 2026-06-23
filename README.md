# Synthetic Data Demo (BlenderProc)

Minimal hands-on demo for generating a single synthetic image: one War Thunder tank placed in a Blender environment.

Students clone the repo, drop in the bundled test assets, and run one script.

## Project layout

```
.
├── assets/
│   ├── environment/
│   │   └── scene.blend          # your environment (required)
│   └── objects/
│       └── tank/
│           └── tank.blend       # your tank model (required)
├── scripts/
│   └── render_demo.py           # the demo pipeline
├── output/                      # renders land here (gitignored)
├── requirements.txt
└── README.md
```

## Quick start

### 1. Clone and install

```bash
git clone <your-repo-url>
cd synthetic-data-demo

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

On first run, BlenderProc downloads Blender automatically (~500 MB). This is normal.

### 2. Add the demo assets

Place your files at these **fixed paths** (the script hard-links to them):

| Asset | Path | Format |
|-------|------|--------|
| Environment | `assets/environment/scene.blend` | `.blend` |
| Tank | `assets/objects/tank/tank.blend` | `.blend`, `.obj`, or `.ply` |

If your tank export uses a different filename, either rename it to `tank.blend` or pass `--tank` (see below).

### 3. Render one image

From the project root:

```bash
blenderproc run scripts/render_demo.py
```

Outputs:

- `output/render.png` — quick visual check
- `output/0.hdf5` — full BlenderProc frame (view with `blenderproc vis hdf5 output/0.hdf5`)

### 4. Debug in Blender GUI (optional)

```bash
blenderproc debug scripts/render_demo.py
```

Opens Blender with the script loaded. Press **Run BlenderProc** in the scripting tab.

## Customization

All defaults are overridable:

```bash
blenderproc run scripts/render_demo.py -- \
  --tank assets/objects/tank/my_panzer.obj \
  --tank-location 2 0 0.1 \
  --camera-position 10 -6 3 \
  --resolution 1920 1080 \
  --output output/run_01
```

Edit the constants at the top of `scripts/render_demo.py` to change default camera pose and tank placement for your scene.

## Asset prep tips

**Environment (`scene.blend`)**
- Save the full scene: ground, backdrop, lighting, etc.
- Origin and scale should match where you want the tank placed (default tank position is `[0, 0, 0]`).

**Tank (War Thunder export)**
- Export as `.blend` (preferred), `.obj`, or `.ply`.
- Apply scale in Blender before committing; tanks are often exported very large or very small.
- Center the mesh at its origin in the tank file so placement is predictable.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Environment not found` | Add `assets/environment/scene.blend` |
| `Tank asset not found` | Add model under `assets/objects/tank/` |
| Tank invisible / wrong size | Adjust `--tank-location` and re-export with applied scale |
| Dark render | Tune the SUN light in `render_demo.py` or add lights in `scene.blend` |
| First run is slow | BlenderProc is downloading Blender |

## License

Demo code: MIT (suggested). BlenderProc is [GPL-3.0](https://github.com/DLR-RM/BlenderProc). War Thunder asset usage must comply with Gaijin's terms — use only assets you are permitted to redistribute for teaching.
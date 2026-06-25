# Output folder

BlenderProc writes rendered frames here. Contents are gitignored except this README.

## What you get per run

| File | Description |
|------|-------------|
| `0.hdf5` | Full frame data (RGB, and more if enabled in the script) |
| `render.png` | Quick-view image (written by `scripts/render_demo.py`) |
| `images/render.png` | Same image, YOLO dataset layout |
| `labels/render.txt` | YOLO bbox labels (`class x_center y_center w h`, normalized) |
| `images/render_seg.png` | Colorized instance segmap (**`--export-seg` only**, e.g. `lesson_05`) |
| `images/render_seg_overlay.png` | RGB + green mask — live demo / Exercise 7 |
| `classes.txt` | Class names (`tank`) |
| `data.yaml` | YOLOv8-style dataset config |

Disable YOLO export: `blenderproc run scripts/render_demo.py -- --no-yolo`

> **Note:** `blenderproc quickstart` only writes `.hdf5` — it does not create a PNG. Use the export options below.

## View an HDF5 file

### Option 1 — BlenderProc viewer (interactive)

```bash
blenderproc vis hdf5 output/0.hdf5
```

Opens a viewer for RGB and, when `--export-seg` was used, `instance_segmaps` (jet colormap).

### Option 2 — Export to PNG/JPG (recommended for sharing)

No Blender needed:

```bash
python scripts/export_hdf5_image.py output/0.hdf5
python scripts/export_hdf5_image.py output/0.hdf5 -o output/render.jpg --format jpg
```

### Option 3 — Python one-liner

```bash
python -c "import h5py, numpy as np; from PIL import Image; f='output/0.hdf5'; d=h5py.File(f); Image.fromarray(np.array(d['colors'][0])).save('output/render.png')"
```

## HDF5 contents

A typical RGB-only frame contains:

```python
import h5py
with h5py.File("output/0.hdf5") as f:
    print(list(f.keys()))  # e.g. ['colors', 'instance_segmaps']
```

YOLO labels use a seg pass on every run; **`instance_segmaps` in HDF5** and seg PNGs require **`--export-seg`** (Exercise 5).

## YOLO annotations

Each label line is one detected tank:

```
0 0.556250 0.548333 0.852500 0.710000
```

Preview boxes on the image (does **not** re-render — annotates the PNG already on disk):

```bash
python scripts/visualize_yolo.py
```

Uses the newest of `render.png` / `images/render.png`. After scene changes, run
`blenderproc run scripts/render_demo.py` first, then visualize. Writes `*_annotated.png`
next to the source image.

Train with Ultralytics (example):

```bash
yolo detect train data=output/data.yaml model=yolov8n.pt epochs=50 imgsz=640
```
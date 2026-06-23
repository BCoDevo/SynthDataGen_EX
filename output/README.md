# Output folder

BlenderProc writes rendered frames here. Contents are gitignored except this README.

## What you get per run

| File | Description |
|------|-------------|
| `0.hdf5` | Full frame data (RGB, and more if enabled in the script) |
| `render.png` | Quick-view image (written by `scripts/render_demo.py`) |

> **Note:** `blenderproc quickstart` only writes `.hdf5` — it does not create a PNG. Use the export options below.

## View an HDF5 file

### Option 1 — BlenderProc viewer (interactive)

```bash
blenderproc vis hdf5 output/0.hdf5
```

Opens a simple viewer for the RGB image (and depth/normals if present).

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
    print(list(f.keys()))  # e.g. ['colors']
```

If depth or normals are enabled in the render script, those arrays appear as additional keys.
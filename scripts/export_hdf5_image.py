"""
Export a PNG/JPG from a BlenderProc .hdf5 frame (no Blender required).

Usage:
    python scripts/export_hdf5_image.py output/0.hdf5
    python scripts/export_hdf5_image.py output/0.hdf5 -o output/render.png
"""

import argparse
from pathlib import Path

import h5py
import numpy as np
from PIL import Image


def load_colors(hdf5_path: Path) -> np.ndarray:
    with h5py.File(hdf5_path, "r") as handle:
        if "colors" not in handle:
            raise KeyError(
                f"No 'colors' dataset in {hdf5_path}. "
                f"Available keys: {list(handle.keys())}"
            )
        colors = np.array(handle["colors"])

    if colors.ndim == 4:
        colors = colors[0]

    if colors.dtype != np.uint8:
        colors = np.clip(colors, 0, 255).astype(np.uint8)

    return colors


def main():
    parser = argparse.ArgumentParser(description="Export RGB image from BlenderProc HDF5.")
    parser.add_argument("hdf5", type=Path, help="Path to .hdf5 file (e.g. output/0.hdf5)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output image path (default: same name as hdf5, .png)",
    )
    parser.add_argument(
        "--format",
        choices=["png", "jpg", "jpeg"],
        default="png",
        help="Image format (default: png)",
    )
    args = parser.parse_args()

    if not args.hdf5.exists():
        raise FileNotFoundError(args.hdf5)

    out = args.output
    if out is None:
        suffix = ".jpg" if args.format in ("jpg", "jpeg") else ".png"
        out = args.hdf5.with_suffix(suffix)

    colors = load_colors(args.hdf5)
    Image.fromarray(colors).save(out)
    print(f"Wrote {out} ({colors.shape[1]}x{colors.shape[0]})")


if __name__ == "__main__":
    main()
"""
Self-check helpers for LESSON.md exercises (no Blender required).

Usage:
    python scripts/lesson_check.py paths --tank <path> --environment <path> --hdr <path>
    python scripts/lesson_check.py render --output output/lesson_02
    python scripts/lesson_check.py yolo --label output/lesson_02/labels/render.txt --width 640 --height 360
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def check_paths(tank: str, environment: str, hdr: str) -> int:
    checks = [
        ("tank", tank, "Tank mesh (.obj)"),
        ("environment", environment, "Environment (.blend)"),
        ("hdr", hdr, "HDR sky"),
    ]
    failed = 0
    for name, raw, label in checks:
        path = _resolve(raw)
        if path.exists():
            print(f"OK   {label}: {path}")
        else:
            print(f"FAIL {label}: not found at {path}", file=sys.stderr)
            failed += 1
    if failed:
        print(f"\n{failed} path(s) missing. Re-read Exercise 1 in LESSON.md.", file=sys.stderr)
        return 1
    print("\nAll paths OK — continue to Exercise 2.")
    return 0


def check_render(output: str) -> int:
    out = _resolve(output)
    required = [
        ("render.png", "Quick-view PNG"),
        ("images/render.png", "YOLO layout image"),
        ("labels/render.txt", "YOLO labels"),
        ("data.yaml", "Dataset config"),
        ("0.hdf5", "BlenderProc frame"),
    ]
    failed = 0
    for rel, label in required:
        path = out / rel
        if path.exists():
            print(f"OK   {label}: {path}")
        else:
            print(f"FAIL {label}: missing ({path})", file=sys.stderr)
            failed += 1
    if failed:
        print(f"\n{failed} file(s) missing. Did the render finish? Check --output folder.", file=sys.stderr)
        return 1

    seg_overlay = out / "images" / "render_seg_overlay.png"
    if seg_overlay.exists():
        print(f"OK   Segmentation overlay: {seg_overlay}")
    elif (out / "labels" / "render.txt").exists():
        print("     (no seg overlay — expected unless you used --export-seg, e.g. lesson_05)")

    try:
        import h5py

        hdf5_path = out / "0.hdf5"
        with h5py.File(hdf5_path, "r") as handle:
            if "instance_segmaps" in handle:
                print(f"OK   HDF5 instance_segmaps: {tuple(handle['instance_segmaps'].shape)}")
    except ImportError:
        pass

    lines = (out / "labels" / "render.txt").read_text(encoding="utf-8").strip().splitlines()
    print(f"\nRender OK — {len(lines)} label line(s). Continue with visualize_yolo or Exercise 3.")
    return 0


def check_yolo(label: str, width: int, height: int) -> int:
    path = _resolve(label)
    if not path.exists():
        print(f"FAIL label file not found: {path}", file=sys.stderr)
        return 1

    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        print("FAIL label file is empty (was --no-yolo used?)", file=sys.stderr)
        return 1

    parts = lines[0].split()
    if len(parts) != 5:
        print(f"FAIL expected 5 values per line, got: {lines[0]!r}", file=sys.stderr)
        return 1

    class_id = int(parts[0])
    x_c, y_c, w, h = map(float, parts[1:])
    x_min = int((x_c - w / 2) * width)
    y_min = int((y_c - h / 2) * height)
    x_max = int((x_c + w / 2) * width)
    y_max = int((y_c + h / 2) * height)

    print(f"Label file: {path}")
    print(f"Raw line:   {lines[0]}")
    print(f"Class id:   {class_id}  (0 = tank in this demo)")
    print(f"Image size: {width} x {height}")
    print(f"Pixel box:  x_min={x_min}, y_min={y_min}, x_max={x_max}, y_max={y_max}")
    print(f"Box size:   {x_max - x_min} x {y_max - y_min} px")
    print("\nCompare with your manual math in Exercise 3.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Self-check helpers for LESSON.md")
    sub = parser.add_subparsers(dest="command", required=True)

    p_paths = sub.add_parser("paths", help="Exercise 1 — verify asset paths exist")
    p_paths.add_argument("--tank", required=True)
    p_paths.add_argument("--environment", required=True)
    p_paths.add_argument("--hdr", required=True)

    p_render = sub.add_parser("render", help="Exercise 2+ — verify render output folder")
    p_render.add_argument("--output", required=True, help="e.g. output/lesson_02")

    p_yolo = sub.add_parser("yolo", help="Exercise 3 — decode first YOLO label line")
    p_yolo.add_argument("--label", required=True)
    p_yolo.add_argument("--width", type=int, required=True)
    p_yolo.add_argument("--height", type=int, required=True)

    args = parser.parse_args()
    if args.command == "paths":
        return check_paths(args.tank, args.environment, args.hdr)
    if args.command == "render":
        return check_render(args.output)
    if args.command == "yolo":
        return check_yolo(args.label, args.width, args.height)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
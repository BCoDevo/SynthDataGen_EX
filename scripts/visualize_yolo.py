"""
Draw YOLO boxes on a rendered image (no Blender required).

Does NOT re-render — it annotates whatever PNG is already on disk.
After changing the scene, run blenderproc first, then this script.

Usage:
    python scripts/visualize_yolo.py
    python scripts/visualize_yolo.py output/render.png
    python scripts/visualize_yolo.py output/images/render.png -o output/render_annotated.png
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "output"


def resolve_latest_render_image(output_dir: Path) -> Path:
    """Pick the newest render PNG (output/render.png or output/images/render.png)."""
    candidates = [
        output_dir / "render.png",
        output_dir / "images" / "render.png",
    ]
    existing = [p for p in candidates if p.exists()]
    if not existing:
        raise FileNotFoundError(
            f"No render image found under {output_dir}. "
            "Run: blenderproc run scripts/render_demo.py"
        )
    return max(existing, key=lambda p: p.stat().st_mtime)


def load_yolo_labels(label_path: Path, image_size: tuple[int, int]) -> list[tuple[int, tuple[int, int, int, int]]]:
    """Parse YOLO txt into (class_id, (x1, y1, x2, y2)) pixel boxes."""
    width, height = image_size
    boxes = []
    if not label_path.exists():
        return boxes

    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        class_id = int(parts[0])
        x_c, y_c, w, h = map(float, parts[1:])
        x1 = int((x_c - w / 2) * width)
        y1 = int((y_c - h / 2) * height)
        x2 = int((x_c + w / 2) * width)
        y2 = int((y_c + h / 2) * height)
        boxes.append((class_id, (x1, y1, x2, y2)))
    return boxes


def main():
    parser = argparse.ArgumentParser(
        description="Visualize YOLO labels on an image (annotates existing render, does not re-render)."
    )
    parser.add_argument(
        "image",
        type=Path,
        nargs="?",
        default=None,
        help="Render image path (default: newest of output/render.png or output/images/render.png)",
    )
    parser.add_argument(
        "labels",
        type=Path,
        nargs="?",
        default=None,
        help="Label file (default: output/labels/<image_stem>.txt)",
    )
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output image path")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output folder to search when image is omitted (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--classes",
        type=Path,
        default=None,
        help="classes.txt path (default: <output-dir>/classes.txt)",
    )
    args = parser.parse_args()

    image_path = args.image or resolve_latest_render_image(args.output_dir)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    label_path = args.labels
    if label_path is None:
        label_path = image_path.parent.parent / "labels" / f"{image_path.stem}.txt"
        if not label_path.exists():
            label_path = args.output_dir / "labels" / f"{image_path.stem}.txt"

    classes_path = args.classes or args.output_dir / "classes.txt"
    class_names = []
    if classes_path.exists():
        class_names = [ln.strip() for ln in classes_path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    boxes = load_yolo_labels(label_path, image.size)

    if label_path.exists() and not boxes:
        print(f"Warning: {label_path} has no boxes for this image size ({image.size[0]}x{image.size[1]}).")
        print("Re-run blenderproc with --yolo to refresh labels after scene changes.")

    for class_id, (x1, y1, x2, y2) in boxes:
        name = class_names[class_id] if class_id < len(class_names) else str(class_id)
        draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=3)
        draw.text((x1, max(0, y1 - 14)), name, fill=(0, 255, 0))

    out = args.output or image_path.with_name(f"{image_path.stem}_annotated.png")
    image.save(out)
    print(f"Source: {image_path}")
    print(f"Labels: {label_path if label_path.exists() else '(missing)'}")
    print(f"Wrote {out} ({len(boxes)} box(es))")


if __name__ == "__main__":
    main()
"""
Draw YOLO boxes on a rendered image (no Blender required).

Usage:
    python scripts/visualize_yolo.py output/images/render.png output/labels/render.txt
    python scripts/visualize_yolo.py output/images/render.png -o output/render_annotated.png
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


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
    parser = argparse.ArgumentParser(description="Visualize YOLO labels on an image.")
    parser.add_argument("image", type=Path, help="Path to image (e.g. output/images/render.png)")
    parser.add_argument(
        "labels",
        type=Path,
        nargs="?",
        default=None,
        help="Path to label file (default: matching file under labels/)",
    )
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output image path")
    parser.add_argument(
        "--classes",
        type=Path,
        default=None,
        help="classes.txt path (default: output/classes.txt next to labels)",
    )
    args = parser.parse_args()

    if not args.image.exists():
        raise FileNotFoundError(args.image)

    label_path = args.labels
    if label_path is None:
        label_path = args.image.parent.parent / "labels" / f"{args.image.stem}.txt"

    classes_path = args.classes or label_path.parent.parent / "classes.txt"
    class_names = []
    if classes_path.exists():
        class_names = [ln.strip() for ln in classes_path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    image = Image.open(args.image).convert("RGB")
    draw = ImageDraw.Draw(image)
    boxes = load_yolo_labels(label_path, image.size)

    for class_id, (x1, y1, x2, y2) in boxes:
        name = class_names[class_id] if class_id < len(class_names) else str(class_id)
        draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=3)
        draw.text((x1, max(0, y1 - 14)), name, fill=(0, 255, 0))

    out = args.output or args.image.with_name(f"{args.image.stem}_annotated.png")
    image.save(out)
    print(f"Wrote {out} ({len(boxes)} box(es))")


if __name__ == "__main__":
    main()
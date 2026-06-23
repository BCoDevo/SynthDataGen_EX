"""Convert BlenderProc instance segmentation output to YOLO detection labels."""

from __future__ import annotations

from pathlib import Path

import numpy as np

# BlenderProc category_id on tank mesh(es) -> YOLO class index (0-based)
DEFAULT_CATEGORY_TO_YOLO = {1: 0}
DEFAULT_CLASS_NAMES = ["tank"]


def bbox_from_mask(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    """Return pixel bbox as (x_min, y_min, width, height) or None if empty."""
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any() or not cols.any():
        return None
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]
    return int(x_min), int(y_min), int(x_max - x_min + 1), int(y_max - y_min + 1)


def bbox_to_yolo_line(
    class_id: int,
    x: int,
    y: int,
    w: int,
    h: int,
    image_width: int,
    image_height: int,
) -> str:
    """YOLO format: class x_center y_center width height (all normalized)."""
    x_c = (x + w / 2) / image_width
    y_c = (y + h / 2) / image_height
    return f"{class_id} {x_c:.6f} {y_c:.6f} {w / image_width:.6f} {h / image_height:.6f}"


def instance_segmap_to_yolo_lines(
    instance_segmap: np.ndarray,
    instance_attribute_map: list[dict],
    category_to_yolo: dict[int, int] | None = None,
    min_area: int = 100,
) -> list[str]:
    """Build YOLO label lines for one frame."""
    if category_to_yolo is None:
        category_to_yolo = DEFAULT_CATEGORY_TO_YOLO

    attr_by_idx = {int(entry["idx"]): entry for entry in instance_attribute_map}
    height, width = instance_segmap.shape
    lines: list[str] = []

    for inst_id in np.unique(instance_segmap):
        inst_id = int(inst_id)
        if inst_id == 0:
            continue

        attrs = attr_by_idx.get(inst_id)
        if attrs is None:
            continue

        category_id = int(attrs.get("class", attrs.get("category_id", 0)))
        if category_id not in category_to_yolo:
            continue

        mask = instance_segmap == inst_id
        if mask.sum() < min_area:
            continue

        bbox = bbox_from_mask(mask.astype(np.uint8))
        if bbox is None:
            continue

        yolo_class = category_to_yolo[category_id]
        lines.append(bbox_to_yolo_line(yolo_class, *bbox, width, height))

    return lines


def write_yolo_label_file(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_classes_file(path: Path, class_names: list[str] | None = None) -> None:
    names = class_names or DEFAULT_CLASS_NAMES
    path.write_text("\n".join(names) + "\n", encoding="utf-8")


def write_data_yaml(path: Path, class_names: list[str] | None = None, dataset_root: Path | None = None) -> None:
    """Write a minimal YOLOv8-style data.yaml pointing at output/images."""
    names = class_names or DEFAULT_CLASS_NAMES
    root = dataset_root or path.parent
    names_block = "\n".join(f"  {i}: {name}" for i, name in enumerate(names))
    content = (
        f"path: {root.resolve()}\n"
        "train: images\n"
        "val: images\n"
        "\n"
        "names:\n"
        f"{names_block}\n"
    )
    path.write_text(content, encoding="utf-8")


def write_yolo_dataset(
    output_dir: Path,
    image_stem: str,
    instance_segmap: np.ndarray,
    instance_attribute_map: list[dict],
    class_names: list[str] | None = None,
) -> Path:
    """
    Write YOLO labels for one frame.

    Layout:
        output_dir/images/<stem>.png   (image written separately)
        output_dir/labels/<stem>.txt
        output_dir/classes.txt
        output_dir/data.yaml
    """
    labels_dir = output_dir / "labels"
    label_path = labels_dir / f"{image_stem}.txt"

    lines = instance_segmap_to_yolo_lines(instance_segmap, instance_attribute_map)
    write_yolo_label_file(label_path, lines)
    write_classes_file(output_dir / "classes.txt", class_names)
    write_data_yaml(output_dir / "data.yaml", class_names, output_dir)

    return label_path
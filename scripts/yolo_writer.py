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


def write_yolo_multi_frame(
    output_dir: Path,
    image_stems: list[str],
    instance_segmaps: list[np.ndarray],
    instance_attribute_maps: list[list[dict]],
    class_names: list[str] | None = None,
) -> list[Path]:
    """Write YOLO labels for multiple frames (orbit / multi-view renders)."""
    if not (len(image_stems) == len(instance_segmaps) == len(instance_attribute_maps)):
        raise ValueError("image_stems, instance_segmaps, and instance_attribute_maps must have the same length")

    labels_dir = output_dir / "labels"
    label_paths: list[Path] = []
    for stem, segmap, attr_map in zip(image_stems, instance_segmaps, instance_attribute_maps):
        lines = instance_segmap_to_yolo_lines(segmap, attr_map)
        label_path = labels_dir / f"{stem}.txt"
        write_yolo_label_file(label_path, lines)
        label_paths.append(label_path)

    write_classes_file(output_dir / "classes.txt", class_names)
    write_data_yaml(output_dir / "data.yaml", class_names, output_dir)
    return label_paths


def colorize_instance_segmap(instance_segmap: np.ndarray) -> np.ndarray:
    """RGB preview of the instance ID map (background black, each instance a distinct color)."""
    height, width = instance_segmap.shape
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    for inst_id in np.unique(instance_segmap):
        inst_id = int(inst_id)
        if inst_id == 0:
            continue
        hue = (inst_id * 97) % 256
        rgb[instance_segmap == inst_id] = (hue, 200, 80)
    return rgb


def overlay_instance_mask(rgb: np.ndarray, instance_segmap: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    """Blend a green mask over RGB — shows the pixels that feed the YOLO bounding box."""
    base = rgb.astype(np.float32)
    mask = instance_segmap != 0
    if not mask.any():
        return rgb.copy()
    highlight = np.array([0.0, 255.0, 0.0], dtype=np.float32)
    base[mask] = base[mask] * (1.0 - alpha) + highlight * alpha
    return np.clip(base, 0, 255).astype(np.uint8)


def append_segmentation_to_hdf5(hdf5_path: Path, instance_segmap: np.ndarray) -> None:
    """Merge the instance segmap into an existing BlenderProc .hdf5 (for blenderproc vis hdf5)."""
    import h5py

    with h5py.File(hdf5_path, "a") as handle:
        for key in ("instance_segmaps", "class_segmaps", "instance_attribute_maps"):
            if key in handle:
                del handle[key]
        handle.create_dataset("instance_segmaps", data=instance_segmap, compression="gzip")


def export_segmentation_previews(
    output_dir: Path,
    image_stem: str,
    rgb: np.ndarray,
    instance_segmap: np.ndarray,
    frame_index: int,
) -> tuple[Path, Path]:
    """Write seg PNG overlays and append seg arrays to the matching frame HDF5."""
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    seg_path = images_dir / f"{image_stem}_seg.png"
    overlay_path = images_dir / f"{image_stem}_seg_overlay.png"
    save_rgb = _save_rgb_image
    save_rgb(colorize_instance_segmap(instance_segmap), seg_path)
    save_rgb(overlay_instance_mask(rgb, instance_segmap), overlay_path)

    hdf5_path = output_dir / f"{frame_index}.hdf5"
    if hdf5_path.exists():
        append_segmentation_to_hdf5(hdf5_path, instance_segmap)

    return seg_path, overlay_path


def _save_rgb_image(rgb: np.ndarray, path: Path) -> None:
    try:
        import imageio.v3 as iio

        iio.imwrite(path, rgb)
    except ImportError:
        from PIL import Image

        Image.fromarray(rgb).save(path)
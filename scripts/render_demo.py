import blenderproc as bproc

# Hands-on demo: render one image of a tank object inside a .blend environment.
# Run from project root:  blenderproc run scripts/render_demo.py
# Tank-only preview:      blenderproc run scripts/render_demo.py -- --tank-only

import argparse
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from yolo_writer import DEFAULT_CLASS_NAMES, write_yolo_dataset

PROJECT_ROOT = SCRIPT_DIR.parent
ENVIRONMENT_DIR = PROJECT_ROOT / "assets" / "environment"

DEFAULT_ENVIRONMENT = ENVIRONMENT_DIR / "Scene_Morning.blend"
DEFAULT_HDR = ENVIRONMENT_DIR / "HDRs" / "spruit_sunrise_4k.hdr"
DEFAULT_TANK = PROJECT_ROOT / "assets" / "objects" / "tank" / "cn_ztz_99a" / "ztz_99a_0.obj"
DEFAULT_OUTPUT = PROJECT_ROOT / "output"

# Tank on the open ground near the scene origin (Blender Z-up)
DEFAULT_TANK_LOCATION = [0.0, 3.0, 0.2]

# Match the authored framing in Scene_Morning.blend (1920x1080, 50 mm lens)
DEFAULT_RESOLUTION = [1920, 1080]
DEFAULT_SCENE_CAMERA = "Camera"
DEFAULT_SAMPLES = 128

# Demo camera: offset from tank center of interest (same as tank-only preview — more top-down)
DEFAULT_CAMERA_OFFSET = [10.0, -10.0, 4.0]

# Rotate environment (deg Z) so authored scene framing faces the demo camera
DEFAULT_ENVIRONMENT_ROTATION_Z = 45.9

# YOLO: BlenderProc category_id on tank -> class 0 in labels/classes.txt
TANK_CATEGORY_ID = 1

TEXTURE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dds", ".hdr", ".exr"}

# Tree/leaf textures not bundled in the repo — map to closest available PBR sets
TEXTURE_FALLBACKS = {
    "tree_bark_03_ao_2k.jpg": "brown_planks_03_AO_2k.jpg",
    "tree_bark_03_diff_2k.jpg": "brown_planks_03_diff_2k.jpg",
    "tree_bark_03_nor_2k.jpg": "brown_planks_03_Nor_2k.jpg",
    "tree_bark_03_rough_2k.jpg": "brown_planks_03_rough_2k.jpg",
    "leaf 2 front 1k_alb.jpg": "186-1868550_grass-blade-texture-png-grass.png",
    "leaf 2 front 1k_dif.jpg": "186-1868550_grass-blade-texture-png-grass.png",
    "leaf 2 front 1k_nor.jpg": "aerial_grass_rock_nor_2k.jpg",
    "dry-tree-branch-isolated-white-background-png-file-transparent-also-available-wooden-fallen-to-ground-high-quality-160380970.jpg": "brown_planks_03_diff_2k.jpg",
    "dry-tree-branch-isolated-white-background-png-file-transparent-": "brown_planks_03_diff_2k.jpg",
}


def load_mesh_asset(path: Path):
    """Load a mesh from .blend, .obj, or .ply."""
    suffix = path.suffix.lower()
    if suffix == ".blend":
        return bproc.loader.load_blend(str(path))
    if suffix in (".obj", ".ply"):
        return bproc.loader.load_obj(str(path))
    raise ValueError(f"Unsupported mesh format: {path}")


def _build_texture_index(env_dir: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in env_dir.rglob("*"):
        if path.suffix.lower() in TEXTURE_EXTENSIONS:
            index[path.name.lower()] = path
    return index


def relink_environment_textures(env_dir: Path) -> tuple[int, int]:
    """Point blend image datablocks at files under assets/environment/."""
    import bpy

    index = _build_texture_index(env_dir)
    fixed = 0
    still_missing = 0

    for image in bpy.data.images:
        if image.packed_file:
            continue

        keys = []
        if image.filepath:
            keys.append(Path(bpy.path.abspath(image.filepath)).name.lower())
        keys.append(image.name.lower())

        resolved = None
        for key in keys:
            if not key:
                continue
            if key in index:
                resolved = index[key]
                break
            fallback = TEXTURE_FALLBACKS.get(key)
            if fallback and fallback.lower() in index:
                resolved = index[fallback.lower()]
                break

        if resolved is None:
            if image.filepath:
                still_missing += 1
            continue

        image.filepath = str(resolved)
        image.reload()
        fixed += 1

    return fixed, still_missing


def configure_renderer(samples: int = DEFAULT_SAMPLES) -> None:
    """Apply BlenderProc Cycles settings for clean, reasonably fast demo renders."""
    import bpy
    from blenderproc.python.renderer import RendererUtility

    bpy.context.scene.render.engine = "CYCLES"
    RendererUtility.set_render_devices()
    RendererUtility.render_init()
    RendererUtility.set_max_amount_of_samples(samples)
    RendererUtility.set_noise_threshold(0.01)
    RendererUtility.set_denoiser("OPTIX")


def snapshot_environment_objects() -> set[str]:
    """Record object names present after opening the environment (before tank import)."""
    import bpy

    return {obj.name for obj in bpy.data.objects if obj.type in {"MESH", "EMPTY", "LIGHT"}}


def rotate_environment_objects(
    object_names: set[str],
    angle_deg: float,
    pivot: list[float],
) -> None:
    """Rotate environment content around the tank pivot on the Z axis."""
    import bpy
    import mathutils

    if abs(angle_deg) < 1e-6:
        return

    pivot_vec = mathutils.Vector(pivot)
    angle_rad = np.radians(angle_deg)
    rot = mathutils.Euler((0.0, 0.0, angle_rad), "XYZ").to_matrix().to_4x4()
    to_pivot = mathutils.Matrix.Translation(-pivot_vec)
    from_pivot = mathutils.Matrix.Translation(pivot_vec)
    transform = from_pivot @ rot @ to_pivot

    rotated = 0
    for name in object_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        obj.matrix_world = transform @ obj.matrix_world
        rotated += 1

    print(f"Rotated {rotated} environment object(s) by {angle_deg:.1f}° around {pivot}")


def open_environment_blend(path: Path) -> None:
    """Open the full .blend scene so world/materials/camera are preserved."""
    import bpy
    from blenderproc.python.utility.Utility import reset_keyframes

    bpy.ops.wm.open_mainfile(filepath=str(path))
    # init() ran first; reopening the .blend resets engine/settings.
    configure_renderer()

    # Scene file carries a long timeline — demo only needs one still frame.
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 1
    bpy.context.scene.frame_set(1)
    reset_keyframes()


def apply_sky_lighting(hdr_path: Path, strength: float = 1.2) -> None:
    """Scene has no lamps — drive lighting from the bundled morning HDR."""
    if not hdr_path.exists():
        raise FileNotFoundError(f"HDR not found: {hdr_path}")
    bproc.world.set_world_background_hdr_img(str(hdr_path), strength=strength)
    print(f"Sky lighting: {hdr_path.name} (strength={strength})")


def setup_studio_scene():
    """Minimal ground + lighting when no environment .blend is available."""
    ground = bproc.object.create_primitive("PLANE", size=40.0)
    ground.set_location([0.0, 0.0, 0.0])

    sun = bproc.types.Light()
    sun.set_type("SUN")
    sun.set_location([12.0, -8.0, 18.0])
    sun.set_energy(4.0)

    fill = bproc.types.Light()
    fill.set_type("POINT")
    fill.set_location([-6.0, 6.0, 8.0])
    fill.set_energy(600.0)


def save_png(path: Path, rgb: np.ndarray) -> None:
    """Write an RGB uint8 array to PNG."""
    try:
        import imageio.v3 as iio

        iio.imwrite(path, rgb)
    except ImportError:
        from PIL import Image

        Image.fromarray(rgb).save(path)


def register_scene_camera(resolution, camera_name: str = DEFAULT_SCENE_CAMERA):
    """Register the scene camera while preserving its authored lens and framing."""
    import bpy
    from blenderproc.python.camera import CameraUtility

    cam_obj = bpy.data.objects.get(camera_name)
    if cam_obj is None or cam_obj.type != "CAMERA":
        cam_obj = bpy.context.scene.camera
    if cam_obj is None:
        raise RuntimeError("No camera found in the loaded environment.")

    bpy.context.scene.camera = cam_obj
    cam_data = cam_obj.data
    width, height = resolution

    lens_value = cam_data.lens if cam_data.lens_unit == "MILLIMETERS" else cam_data.angle
    CameraUtility.set_intrinsics_from_blender_params(
        lens=lens_value,
        image_width=width,
        image_height=height,
        clip_start=cam_data.clip_start,
        clip_end=cam_data.clip_end,
        shift_x=cam_data.shift_x,
        shift_y=cam_data.shift_y,
        lens_unit=cam_data.lens_unit,
    )

    bproc.camera.add_camera_pose(cam_obj.matrix_world)
    print(f"Using scene camera: {cam_obj.name} ({width}x{height}, {cam_data.lens} mm)")


def label_tank_objects(tank_objs) -> None:
    """Tag tank mesh(es) for instance segmentation / YOLO export."""
    for obj in tank_objs:
        obj.set_cp("category_id", TANK_CATEGORY_ID)


def render_segmentation_maps():
    """Fast 1-sample pass producing per-instance masks and class attributes."""
    return bproc.renderer.render_segmap(
        map_by=["instance", "class"],
        default_values={"class": 0},
    )


def add_camera_for_tank(tank_objs, resolution, offset=None):
    """Frame the tank from above — auto-aim at its center (hides ground-gap better)."""
    width, height = resolution
    bproc.camera.set_resolution(width, height)

    if offset is None:
        offset = DEFAULT_CAMERA_OFFSET

    poi = bproc.object.compute_poi(tank_objs)
    cam_location = poi + np.array(offset, dtype=float)
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - cam_location)
    cam_pose = bproc.math.build_transformation_mat(cam_location, rotation_matrix)
    bproc.camera.add_camera_pose(cam_pose)
    print(f"Using demo camera at [{cam_location[0]:.1f}, {cam_location[1]:.1f}, {cam_location[2]:.1f}] (offset {offset})")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render one synthetic RGB image of a tank in a Blender environment."
    )
    parser.add_argument(
        "--environment",
        type=Path,
        default=DEFAULT_ENVIRONMENT,
        help=f"Path to environment .blend (default: {DEFAULT_ENVIRONMENT})",
    )
    parser.add_argument(
        "--hdr",
        type=Path,
        default=DEFAULT_HDR,
        help=f"HDR sky for environment lighting (default: {DEFAULT_HDR})",
    )
    parser.add_argument(
        "--hdr-strength",
        type=float,
        default=1.2,
        help="Brightness of the HDR sky (default: 1.2)",
    )
    parser.add_argument(
        "--tank",
        type=Path,
        default=DEFAULT_TANK,
        help=f"Path to tank asset (default: {DEFAULT_TANK})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--tank-only",
        action="store_true",
        help="Skip environment; render tank on a simple studio ground plane",
    )
    parser.add_argument(
        "--tank-location",
        type=float,
        nargs=3,
        metavar=("X", "Y", "Z"),
        default=DEFAULT_TANK_LOCATION,
        help="Tank placement in world coordinates",
    )
    parser.add_argument(
        "--camera-offset",
        type=float,
        nargs=3,
        metavar=("X", "Y", "Z"),
        default=None,
        help=f"Camera offset from tank center (default: {DEFAULT_CAMERA_OFFSET})",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        default=DEFAULT_RESOLUTION,
        help=f"Render resolution (default: {DEFAULT_RESOLUTION[0]}x{DEFAULT_RESOLUTION[1]})",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=DEFAULT_SAMPLES,
        help=f"Cycles samples — higher = cleaner, slower (default: {DEFAULT_SAMPLES})",
    )
    parser.add_argument(
        "--use-scene-camera",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Use the camera baked into the environment .blend (default: demo top-down framing)",
    )
    parser.add_argument(
        "--yolo",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Export YOLO detection labels (default: on)",
    )
    parser.add_argument(
        "--env-rotation",
        type=float,
        default=DEFAULT_ENVIRONMENT_ROTATION_Z,
        help=f"Rotate environment on Z (degrees) around tank pivot (default: {DEFAULT_ENVIRONMENT_ROTATION_Z})",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.tank.exists():
        raise FileNotFoundError(
            f"Tank asset not found: {args.tank}\n"
            "Expected bundled asset at assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj"
        )

    use_environment = not args.tank_only
    if use_environment and not args.environment.exists():
        raise FileNotFoundError(
            f"Environment not found: {args.environment}\n"
            "Expected bundled scene at assets/environment/Scene_Morning.blend, "
            "or run with --tank-only to preview the tank without an environment."
        )

    bproc.init()
    configure_renderer(samples=args.samples)

    if use_environment:
        print(f"Opening environment: {args.environment}")
        open_environment_blend(args.environment)
        configure_renderer(samples=args.samples)

        fixed, missing = relink_environment_textures(ENVIRONMENT_DIR)
        print(f"Relinked {fixed} environment texture(s); {missing} still missing (tree/leaf fallbacks applied where possible)")

        apply_sky_lighting(args.hdr, strength=args.hdr_strength)
        env_objects = snapshot_environment_objects()
    else:
        print("No environment — using studio ground plane (--tank-only)")
        setup_studio_scene()
        env_objects = set()

    print(f"Loading tank: {args.tank}")
    tank_objs = load_mesh_asset(args.tank)
    for obj in tank_objs:
        obj.set_location(list(args.tank_location))
    label_tank_objects(tank_objs)
    print(f"Placed {len(tank_objs)} tank object(s) at {args.tank_location}")

    if use_environment and env_objects:
        rotate_environment_objects(
            env_objects,
            angle_deg=args.env_rotation,
            pivot=list(args.tank_location),
        )

    if args.use_scene_camera:
        register_scene_camera(resolution=args.resolution)
    else:
        add_camera_for_tank(
            tank_objs,
            args.resolution,
            offset=args.camera_offset,
        )

    width, height = args.resolution
    print(f"Rendering {width}x{height} ...")
    data = bproc.renderer.render()

    args.output.mkdir(parents=True, exist_ok=True)
    bproc.writer.write_hdf5(str(args.output), data)

    rgb = data["colors"][0]
    png_path = args.output / "render.png"
    save_png(png_path, rgb)

    images_dir = args.output / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    yolo_image_path = images_dir / "render.png"
    save_png(yolo_image_path, rgb)

    label_path = None
    if args.yolo:
        print("Rendering instance segmentation for YOLO labels ...")
        seg_data = render_segmentation_maps()
        inst_segmap = seg_data["instance_segmaps"]
        inst_attrs = seg_data["instance_attribute_maps"]
        if isinstance(inst_segmap, list):
            inst_segmap = inst_segmap[0]
            inst_attrs = inst_attrs[0]

        label_path = write_yolo_dataset(
            args.output,
            image_stem="render",
            instance_segmap=inst_segmap,
            instance_attribute_map=inst_attrs,
            class_names=DEFAULT_CLASS_NAMES,
        )
        box_count = len(label_path.read_text(encoding="utf-8").splitlines()) if label_path.exists() else 0
        print(f"YOLO: {box_count} box(es) -> {label_path}")

    print("Done.")
    print(f"  PNG:  {png_path}")
    print(f"  HDF5: {args.output / '0.hdf5'}")
    if label_path is not None:
        print(f"  YOLO: {args.output / 'data.yaml'}")
    print(f"        python scripts/visualize_yolo.py")


if __name__ == "__main__":
    main()
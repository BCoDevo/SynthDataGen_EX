import blenderproc as bproc

# Hands-on demo: render one image of a tank object inside a .blend environment.
# Run from project root:  blenderproc run scripts/render_demo.py
# Tank-only preview:      blenderproc run scripts/render_demo.py -- --tank-only

import argparse
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ENVIRONMENT = PROJECT_ROOT / "assets" / "environment" / "Scene_Morning.blend"
DEFAULT_TANK = PROJECT_ROOT / "assets" / "objects" / "tank" / "cn_ztz_99a" / "ztz_99a_0.obj"
DEFAULT_OUTPUT = PROJECT_ROOT / "output"

# Tank on the open ground near the scene origin (Blender Z-up)
DEFAULT_TANK_LOCATION = [0.0, 3.0, 0.2]

# Fallback camera when not using the scene's built-in camera
DEFAULT_CAMERA_POSITION = [0.0, -13.0, 1.5]
DEFAULT_CAMERA_ROTATION = [1.35, 0.0, 0.0]


def load_mesh_asset(path: Path):
    """Load a mesh from .blend, .obj, or .ply."""
    suffix = path.suffix.lower()
    if suffix == ".blend":
        return bproc.loader.load_blend(str(path))
    if suffix in (".obj", ".ply"):
        return bproc.loader.load_obj(str(path))
    raise ValueError(f"Unsupported mesh format: {path}")


def load_environment(path: Path):
    """Load a full .blend environment (meshes, lights, cameras, collections)."""
    return bproc.loader.load_blend(
        str(path),
        data_blocks=["objects", "collections"],
        obj_types=["mesh", "empty", "light", "camera"],
    )


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


def register_scene_camera(resolution):
    """Register the active Blender camera (from the loaded .blend) for rendering."""
    import bpy

    width, height = resolution
    bproc.camera.set_resolution(width, height)

    cam_obj = bpy.context.scene.camera
    if cam_obj is None:
        raise RuntimeError("No active camera in the loaded environment.")

    bproc.camera.add_camera_pose(cam_obj.matrix_world)
    print(f"Using scene camera: {cam_obj.name}")


def add_camera_for_tank(tank_objs, resolution, position=None, rotation=None):
    """Frame the tank — auto-aim at its center when position/rotation not given."""
    width, height = resolution
    bproc.camera.set_resolution(width, height)

    if position is not None and rotation is not None:
        cam_pose = bproc.math.build_transformation_mat(list(position), list(rotation))
        bproc.camera.add_camera_pose(cam_pose)
        return

    poi = bproc.object.compute_poi(tank_objs)
    cam_location = poi + np.array([10.0, -10.0, 4.0])
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - cam_location)
    cam_pose = bproc.math.build_transformation_mat(cam_location, rotation_matrix)
    bproc.camera.add_camera_pose(cam_pose)


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
        "--camera-position",
        type=float,
        nargs=3,
        metavar=("X", "Y", "Z"),
        default=None,
        help="Camera world position (default: auto-frame tank in --tank-only mode)",
    )
    parser.add_argument(
        "--camera-rotation",
        type=float,
        nargs=3,
        metavar=("RX", "RY", "RZ"),
        default=None,
        help="Camera euler rotation in radians (default: auto-frame tank in --tank-only mode)",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        default=[1280, 720],
        help="Render resolution",
    )
    parser.add_argument(
        "--use-scene-camera",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Use the camera baked into the environment .blend (default: on for full scene)",
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

    if use_environment:
        print(f"Loading environment: {args.environment}")
        load_environment(args.environment)
    else:
        print("No environment — using studio ground plane (--tank-only)")
        setup_studio_scene()

    print(f"Loading tank: {args.tank}")
    tank_objs = load_mesh_asset(args.tank)
    for obj in tank_objs:
        obj.set_location(list(args.tank_location))
    print(f"Placed {len(tank_objs)} tank object(s) at {args.tank_location}")

    from_scene = args.use_scene_camera
    if from_scene is None:
        from_scene = use_environment

    if from_scene:
        register_scene_camera(resolution=args.resolution)
    else:
        add_camera_for_tank(
            tank_objs,
            args.resolution,
            position=args.camera_position or DEFAULT_CAMERA_POSITION,
            rotation=args.camera_rotation or DEFAULT_CAMERA_ROTATION,
        )

    width, height = args.resolution
    print(f"Rendering {width}x{height} ...")
    data = bproc.renderer.render()

    args.output.mkdir(parents=True, exist_ok=True)
    bproc.writer.write_hdf5(str(args.output), data)

    png_path = args.output / "render.png"
    save_png(png_path, data["colors"][0])

    print("Done.")
    print(f"  PNG:  {png_path}")
    print(f"  HDF5: {args.output / '0.hdf5'}")


if __name__ == "__main__":
    main()
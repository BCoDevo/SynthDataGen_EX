"""
Hands-on demo: render one image of a tank object inside a .blend environment.

Run from the project root:
    blenderproc run scripts/render_demo.py

Optional overrides:
    blenderproc run scripts/render_demo.py -- --output output/my_run
"""

import argparse
from pathlib import Path

import blenderproc as bproc
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ENVIRONMENT = PROJECT_ROOT / "assets" / "environment" / "scene.blend"
DEFAULT_TANK = PROJECT_ROOT / "assets" / "objects" / "tank" / "tank.blend"
DEFAULT_OUTPUT = PROJECT_ROOT / "output"

# Camera pose: position [x, y, z], euler rotation [rx, ry, rz] in radians
DEFAULT_CAMERA_POSITION = [8.0, -8.0, 4.0]
DEFAULT_CAMERA_ROTATION = [1.1, 0.0, 0.85]

# Where to place the tank in the environment (meters, Blender Z-up)
DEFAULT_TANK_LOCATION = [0.0, 0.0, 0.0]


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


def save_png(path: Path, rgb: np.ndarray) -> None:
    """Write an RGB uint8 array to PNG without extra dependencies."""
    try:
        import imageio.v3 as iio
    except ImportError:
        from PIL import Image

        Image.fromarray(rgb).save(path)
        return

    iio.imwrite(path, rgb)


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
        help=f"Path to tank asset .blend/.obj/.ply (default: {DEFAULT_TANK})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT})",
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
        default=DEFAULT_CAMERA_POSITION,
        help="Camera world position",
    )
    parser.add_argument(
        "--camera-rotation",
        type=float,
        nargs=3,
        metavar=("RX", "RY", "RZ"),
        default=DEFAULT_CAMERA_ROTATION,
        help="Camera euler rotation in radians",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        default=[1280, 720],
        help="Render resolution",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.environment.exists():
        raise FileNotFoundError(
            f"Environment not found: {args.environment}\n"
            "Place your scene .blend at assets/environment/scene.blend"
        )
    if not args.tank.exists():
        raise FileNotFoundError(
            f"Tank asset not found: {args.tank}\n"
            "Place your tank model at assets/objects/tank/tank.blend (or .obj/.ply)"
        )

    bproc.init()

    print(f"Loading environment: {args.environment}")
    load_environment(args.environment)

    print(f"Loading tank: {args.tank}")
    tank_objs = load_mesh_asset(args.tank)
    for obj in tank_objs:
        obj.set_location(list(args.tank_location))
    print(f"Placed {len(tank_objs)} tank object(s) at {args.tank_location}")

    # Supplemental light — skip if your environment already has adequate lighting
    light = bproc.types.Light()
    light.set_type("SUN")
    light.set_location([10.0, -10.0, 15.0])
    light.set_energy(3.0)

    width, height = args.resolution
    bproc.camera.set_resolution(width, height)

    cam_pose = bproc.math.build_transformation_mat(
        list(args.camera_position),
        list(args.camera_rotation),
    )
    bproc.camera.add_camera_pose(cam_pose)

    print(f"Rendering {width}x{height} ...")
    data = bproc.renderer.render()

    args.output.mkdir(parents=True, exist_ok=True)
    bproc.writer.write_hdf5(str(args.output), data)

    png_path = args.output / "render.png"
    save_png(png_path, data["colors"][0])

    print(f"Done.")
    print(f"  PNG:  {png_path}")
    print(f"  HDF5: {args.output / '0.hdf5'}")


if __name__ == "__main__":
    main()
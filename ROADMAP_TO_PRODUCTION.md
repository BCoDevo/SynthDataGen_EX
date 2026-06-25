# Roadmap to Production

This repo’s **`scripts/render_demo.py`** is a **teaching pipeline**: one tank, one environment, one predictable frame, with YOLO labels and an optional live Blender demo so students can see how CLI flags map to the 3D scene.

A **production baseline** needs the same core ideas — load assets, light a scene, pose cameras, render, annotate — scaled to **many assets, many views, many variations**, with stable output layout and reproducible runs.

This document maps that gap: what the demo already does, what a wider dataset pipeline would add, and a practical order to get there. A related reference implementation is a general-purpose batch script (e.g. a standalone `render.py` with DMF import, COCO export, and multi-view randomization).

---

## Where the demo stands today

| Capability | Teaching demo | Typical production need |
|------------|---------------|-------------------------|
| Assets | Fixed tank OBJ + bundled textures | Any OBJ/DMF under `inputs/`, auto-discover |
| Environment | Full-scene `open_mainfile` + texture relink | Append blend layers, optional background-only shots |
| Camera | Fixed offset or scene camera; **optional orbit multi-view** | Randomized orbit + ranges per view |
| Lighting | HDR sky or studio (`--tank-only`) | Preview lights vs HDR tiers; material brightness |
| Output | 1 frame (or N orbit frames); YOLO via isolated segmap pass | Thousands of frames; COCO/depth; train/val splits |
| Debug | `blenderproc debug` inspect-only | Import smoke tests, config files, job queues |

**Already in the demo (production stepping stone):**

- `--views`, `--seed`, `--camera-distance`, `--camera-elevation`, `--camera-azimuth-jitter` for orbit multi-view
- Per-frame `images/frame_NNN.png` + matching YOLO labels
- Environment texture relink and segmap crash workaround for large scenes

---

## Phased roadmap

Work through these in order unless a project has a hard requirement (e.g. DMF-only assets).

### Phase 1 — Multi-view and camera diversity

**Goal:** Turn one scene setup into a *small* dataset without changing assets or environments.

| Step | Status | Description |
|------|--------|-------------|
| Orbit multi-view (`--views`) | Done | N camera poses on a ring around the tank |
| Seeded azimuth jitter (`--seed`, `--camera-azimuth-jitter`) | Done | Reproducible per-view variation |
| Distance / elevation **ranges** | Todo | e.g. `--camera-distance-range 2.5 4.0` per view |
| Shift ranges | Todo | Horizontal/vertical frame shift randomization |
| Standard frame naming | Partial | Demo uses `frame_000`; production often uses `000000` |

**Extra credit (try now):**

```bash
blenderproc run scripts/render_demo.py -- --tank-only --views 8 --seed 42 --camera-distance 3 --camera-elevation 0.35 --camera-azimuth-jitter 15 --resolution 640 360 --samples 32 --output output/extra_multiview
```

**Why it matters:** Object detectors need viewpoint diversity; a single hero frame teaches the pipeline but not generalization.

---

### Phase 2 — Batch output and dataset layout

**Goal:** Output that drops into training tools (Ultralytics, COCO tools) without hand-renaming.

| Step | Description |
|------|-------------|
| Zero-padded stems | `000000.png` / `000000.txt` for sortable large runs |
| Train/val split in `data.yaml` | Or separate `images/train` and `images/val` |
| Preview export | Batch HDF5 → PNG via `export_hdf5_image.py` or `hdf5_to_images` |
| `--preview-dir` | Decouple HDF5 archive from flat image folder |
| Run manifest | JSON/CSV: seed, CLI args, frame count, git hash, timestamp |

**Why it matters:** At 10k+ images, naming and manifests prevent silent mismatches between images and labels.

---

### Phase 3 — Asset pipeline generalization

**Goal:** Not tied to one tank path; new vehicles drop in under a convention.

| Step | Description |
|------|-------------|
| `--asset-dir` + auto-discover | OBJ or DMF + `textures/` subdirectory |
| Explicit `--obj` / `--dmf` | Override discovery |
| **DMF importer** | War Thunder native format via `io_scene_daet`; transform fixes for scale/rotation |
| `--asset-brightness` | Lift dark PBR materials before render |
| Placement API | Bottom-center of bbox → `--asset-location` (stable ground contact) |

**Why it matters:** Production SDG is asset-agnostic; the teaching repo hardcodes paths so the lesson stays linear.

---

### Phase 4 — Environment and scene composition

**Goal:** Mix and match backgrounds; support negative (no-object) training images.

| Step | Description |
|------|-------------|
| `load_blend` append | Meshes/collections instead of replacing the whole file with `open_mainfile` |
| `--load-environment-collections` | Collection-instanced scenes |
| `--use-blend-world` | Use authored world from blend vs generated gray preview |
| `--background-only` | Environment renders with **empty** YOLO labels (hard negatives) |
| Multiple environment library | Rotate HDRs, blends, or procedural skies per batch |

**Why it matters:** Real detectors see clutter and absence; negatives and env variety reduce false positives.

---

### Phase 5 — Annotations beyond YOLO boxes

**Goal:** Support segmentation, depth, and formats teams already use.

| Step | Description |
|------|-------------|
| **COCO** | `write_coco_annotations` with RLE or polygon masks |
| **Depth + normals** | `--depth-normals` for multi-task or geometry-aware models |
| Configurable categories | `--annotation-category-id`, `--annotation-category-name` |
| Segmap strategy | Main-pass segmentation (fast, all views) vs isolated segmap + env displacement (large scenes) |

**Why it matters:** Detection-only YOLO is enough to teach; production often needs instance masks or auxiliary channels.

---

### Phase 6 — Quality tiers and performance

**Goal:** Fast iteration vs final-quality renders without one-size-fits-all settings.

| Tier | Typical settings | Use case |
|------|------------------|----------|
| Preview | 512², 32 samples, procedural lights, noise 0.05 | Layout and label sanity checks |
| Demo (current default) | 1920×1080, 128 samples, OPTIX denoise, HDR | Teaching and sign-off frames |
| Production | Config-driven resolution/samples; denoise on | Dataset generation runs |

| Step | Description |
|------|-------------|
| CLI presets | `--quality preview|demo|production` |
| OPTIX / CUDA device selection | Documented for farm machines |
| Windows depth/normals caveats | Temp EXR locks (known BlenderProc issue) |

---

### Phase 7 — Operations and scale

**Goal:** Repeatable, debuggable runs at volume (thousands–millions of frames).

| Step | Description |
|------|-------------|
| `--import-only` | Load asset and exit (importer smoke test) |
| Config file | YAML/JSON reproduces a full run (seed, ranges, paths) |
| Structured logging | Per-frame timing, bbox counts, failures |
| Parallel workers | Multiple BlenderProc processes, disjoint output shards |
| Orchestration | Job queue / cloud GPUs outside this repo |

**Why it matters:** Single-process BlenderProc is fine for lessons; production is a scheduling problem once views × assets × environments explodes.

---

## Teaching script vs production baseline (summary)

```
render_demo.py (today)          Production baseline (target)
──────────────────────          ────────────────────────────
Fixed tank + Scene_Morning  →   Any asset dir (OBJ/DMF)
1 hero frame (+ orbit opt) →  N views × M assets × K envs
YOLO only                 →   YOLO + optional COCO/depth
Isolated segmap pass      →   Pass choice by scene size
Inspect-first debug       →   Import-only + config-driven batch
Bundled assets/           →   inputs/ + outputs/ conventions
```

---

## Suggested port order

If you extend this repo toward production, this order balances effort and dataset value:

1. **Camera ranges** — builds on existing `--views` / `--seed`
2. **Batch naming + manifest** — cheap, prevents pain later
3. **COCO export** — if moving past bbox-only training
4. **Background-only negatives** — high value for detector robustness
5. **DMF + asset-dir generalization** — if War Thunder exports are the source of truth
6. **load_blend composition** — when one monolithic `.blend` is too rigid
7. **Job orchestration** — when single-machine batch time exceeds patience

---

## Related files

| File | Role |
|------|------|
| `scripts/render_demo.py` | Teaching pipeline (start here) |
| `LESSON.md` | Student exercises (single-frame focus) |
| `lesson/INSTRUCTOR.md` | Commands, extra credit multi-view |
| `scripts/yolo_writer.py` | Instance seg → YOLO labels |
| `scripts/export_hdf5_image.py` | HDF5 → image without Blender |

---

## After the roadmap

Completing every phase turns this repo into a small SDG framework. That is intentional scope creep for a class demo. The point of this document is to show **which knobs exist in a real pipeline** and **why the teaching script deliberately stops where it does** — so graduates can grow the same pattern into production data, not assume one PNG is the whole story.
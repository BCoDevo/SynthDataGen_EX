# Instructor notes — Synthetic data hands-on lesson

**Audience:** Students new to BlenderProc / synthetic data  
**Duration:** 60–90 min (Exercises 1–6 core; 7–8 extension)  
**Student doc:** `LESSON.md`  
**Worksheet:** students create `lesson/worksheet.md` from template (gitignored)

---

## Learning objectives

By the end, students should be able to:

1. Locate bundled 3D assets and explain why relative paths matter
2. Assemble a `blenderproc run` command with explicit `--tank`, `--environment`, and `--hdr`
3. Interpret a YOLO label line and relate it to pixels
4. Predict the effect of `--tank-location` and `--camera-offset`
5. Describe RGB + label + `data.yaml` as a minimal detection dataset

---

## Suggested pacing

| Block | Exercises | Minutes |
|-------|-----------|---------|
| Setup + asset map | 0–1 | 15 |
| First render + labels | 2–3 | 20 |
| Spatial reasoning | 4–5 | 20 |
| Full scene | 6 | 15–25 |
| Extension | 7–8 | 15 |
| Discussion | Wrap-up | 10 |

Use **low resolution** (`640×360`, `16` samples) until Exercise 6 to keep GPUs cool in a classroom.

---

## Answer key (representative)

### Exercise 1 paths

| Field | Answer |
|-------|--------|
| Tank | `assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj` |
| Environment | `assets/environment/Scene_Morning.blend` |
| HDR | `assets/environment/HDRs/spruit_sunrise_4k.hdr` |
| Script | `scripts/render_demo.py` |

**Discussion:** MTL references `textures/*.dds` relative to the OBJ folder — moving the OBJ without textures breaks materials.

### Exercise 2

- `--tank-only` skips the `.blend` environment; script builds a studio ground + lights.
- Low res/samples = faster iteration while learning the pipeline.
- Background: **gray ground plane**, not grass.

### Exercise 3

Example line at 640×360:

```
0 0.557813 0.577778 0.853125 0.844444
```

- Class `0` = `tank` (from `category_id` 1 → YOLO 0 via `yolo_writer.py`)
- Decoded box roughly: wide box centered on tank (most of frame in tank-only view)

Code trail: `render_demo.py` → `TANK_CATEGORY_ID = 1` → `label_tank_objects()` → `yolo_writer.DEFAULT_CATEGORY_TO_YOLO = {1: 0}`

### Exercise 4

- **Higher Z:** tank floats above ground plane (tank-only) or may hover over terrain (full scene)
- **Lower Z:** tracks clip into ground / z-fighting
- **Change X/Y:** tank shifts in world space → bbox center moves in label file

### Exercise 5

- Larger Z in offset → more top-down; larger horizontal components → more side angle
- Bbox width/height changes with perspective — good lead-in to domain shift

### Exercise 6

Log talking points:

- **Texture relink:** blend was authored on another machine (`Pictures\Blender Textures\`); script remaps by filename to `assets/environment/Textures/`
- **HDR sky:** scene has no lamps; world background provides lighting

### Exercise 7

Accept any well-documented experiment. Common good choices: `--hdr-strength 2.0`, `--env-rotation 0`, `--use-scene-camera`.

### Wrap-up (model answers)

1. **Synthetic:** geometry, materials, and camera are simulated; labels come from perfect segmentation, not human annotation.
2. **Z too low:** mesh intersects terrain; bbox may shrink or look wrong; unrealistic training data.
3. **Domain shift:** studio vs outdoor — detector may fail; need variety in environment, lighting, camera, poses.
4. **Randomize:** camera offset, tank position/yaw, HDR choice/strength, time of day, resolution, clutter.

---

## Common student issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Tank asset not found` | Wrong path or not in repo root | `python scripts/lesson_check.py paths ...` |
| Forgot `--` before flags | BlenderProc argparse | Must be `blenderproc run scripts/render_demo.py -- --tank-only` |
| Old annotated image | visualize picks newest PNG by mtime | Point to explicit path: `python scripts/visualize_yolo.py output/lesson_06/images/render.png` |
| Exercise 6 slow | Full env + HD res | Cap at 1280×720 / 32 samples for class |
| Empty label file | `--no-yolo` or segmap failure | Re-run without `--no-yolo`; ensure updated `render_demo.py` |

---

## Assessment rubric (simple)

| Criterion | Meets |
|-----------|--------|
| Paths | All four correct in worksheet; `lesson_check paths` passes |
| Commands | Uses explicit `--tank` / `--environment` / `--hdr` in Ex 6 |
| YOLO math | Manual pixel box within ~5 px of `lesson_check yolo` |
| Experiments | At least 3 distinct outputs in `output/lesson_*` |
| Reflection | Wrap-up shows cause/effect, not just “it worked” |

---

## Optional extensions

- **Damaged tank:** `--tank assets/objects/tank/cn_ztz_99a/ztz_99a_dmg_0.obj`
- **Batch script:** loop over random `--camera-offset` values (students write the loop)
- **GUI:** `blenderproc debug scripts/render_demo.py` — find tank empty in outliner
- **Train:** `yolo detect train data=output/lesson_06/data.yaml model=yolov8n.pt epochs=10 imgsz=640` (needs `ultralytics`)
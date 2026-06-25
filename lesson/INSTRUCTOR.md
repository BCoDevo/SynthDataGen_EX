# Instructor notes — Synthetic data hands-on lesson

**Audience:** College graduates / technical professionals new to BlenderProc  
**Duration:** 60–90 min (Exercises 1–5 core; 6–8 extension)  
**Student doc:** `LESSON.md`

---

## Learning objectives

1. Locate bundled assets and explain relative path dependencies (MTL → textures)
2. Run `blenderproc` with explicit asset paths and interpret logs
3. Predict effects of `--tank-location` and `--camera-offset`
4. Understand YOLO export as an automated segmentation sidecar (not a manual labeling exercise)
5. Connect CLI parameters to objects visible in Blender's outliner/viewport

---

## Suggested pacing

| Block | Exercises | Minutes |
|-------|-----------|---------|
| Setup + asset map | 0–1 | 10 |
| First render + YOLO ref | 2 | 15 |
| Spatial parameters | 3–4 | 20 |
| Full scene | 5 | 15–25 |
| Extension | 6–7 | 10 |
| Blender capstone | 8 | 15–20 |
| Discussion | Wrap-up | 10 |

Keep `640×360` / `16` samples until Exercise 5.

---

## Answer key

### Exercise 1

| Field | Answer |
|-------|--------|
| Tank | `assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj` |
| Environment | `assets/environment/Scene_Morning.blend` |
| HDR | `assets/environment/HDRs/spruit_sunrise_4k.hdr` |
| Script | `scripts/render_demo.py` |

### Exercise 2

- `--tank-only` → studio ground + lamps; no `.blend` environment
- Background: gray plane, not grass
- YOLO: class `0` = tank; labels auto-generated — no student math required

### Exercise 3–4

- Z too low → clipping; Z high → floating
- X/Y shift → tank moves in frame; label bbox follows
- Higher camera Z → more top-down; perspective changes bbox extent

### Exercise 5

- Texture relink fixes author-machine paths
- HDR provides sole lighting

### Exercise 8 (capstone talking points)

**8a — debug:** Students see the script populate the scene; transform panel validates `--tank-location`. Demo camera is a computed pose, not necessarily the blend's `Camera` object.

**8b — Scene_Morning.blend:** Baked camera faces south-side framing; demo camera + `env-rotation` exist to match that look from a different viewpoint. Ground near `(0, 3, 0)` is the placement reference.

**8c — Tank OBJ:** War Thunder scale; DDS materials; single mesh object = one instance ID in segmentation.

**Common friction:** `blenderproc debug` requires the same `--` flag passthrough as `run`. Opening `.blend` via raw `blender.exe` path — have students copy from their log line.

---

## Assessment rubric

| Criterion | Meets |
|-----------|--------|
| Paths | `lesson_check paths` passes |
| Renders | At least `lesson_02`, `lesson_05`, and one experiment folder |
| Parameters | Can explain tank-location vs camera-offset |
| Blender | Completed 8a or 8b; worksheet note on GUI observation |
| Wrap-up | Mentions domain shift / randomization, not just "synthetic = fake" |

---

## Common issues

| Symptom | Fix |
|---------|-----|
| Forgot `--` before flags | `blenderproc run scripts/render_demo.py -- --tank-only` |
| Debug opens empty scene | Must click Run BlenderProc in Scripting tab |
| Wrong annotated image | `python scripts/visualize_yolo.py output/lesson_05/images/render.png` |
| Empty labels | Re-run without `--no-yolo` |

---

## Optional extensions

- Damaged tank: `--tank assets/objects/tank/cn_ztz_99a/ztz_99a_dmg_0.obj`
- Batch camera offsets (student-written loop)
- Ultralytics train on `output/lesson_05/data.yaml`
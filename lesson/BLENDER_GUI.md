# Exercise 8 — Live Blender demo (instructor)

Use during the live class demo in `LESSON.md` Exercise 8. **Not** a student Blender tutorial — you show the scene; they connect CLI flags to what appears on screen. Deeper Blender UI is better covered elsewhere (e.g. YouTube).

**Student takeaway:** The render pipeline builds a real 3D scene; `--tank-location`, `--camera-offset`, and asset paths correspond to objects and transforms in Blender.

**Prerequisite:** Exercise 5 (`blenderproc run` full environment) so students have a render to reference conceptually.

---

## Command (inspect-only)

Default in `blenderproc debug` — scene setup runs, no Cycles render, Blender stays open until you close it.

```bash
blenderproc debug scripts/render_demo.py -- --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --camera-offset 10 -10 4
```

Run from the **repo root**. Use forward slashes on all platforms.

### Demo flow

1. Blender opens on **Scripting** (empty viewport until the script runs — expected).
2. Click **Run BlenderProc**.
3. Log prints environment load, tank placement, then `Inspect-only`.
4. Layout workspace shows the built scene. Walk through the talking points below, then close Blender.

The terminal stays attached until Blender exits — that is normal.

---

## Talking points (keep it short)

| Point | Tie to CLI / pipeline |
|-------|------------------------|
| Tank mesh in the **Outliner** (`ztz_99a_0`) | `--tank` path — this is what YOLO labels |
| **Transform → Location** ≈ `(0, 3, 0.2)` | `--tank-location` |
| Environment objects around the tank | `Scene_Morning.blend` + texture relink in the script |
| **Demo camera** vs baked scene `Camera` | `--camera-offset` vs `--use-scene-camera` |
| Tank **materials** show textures (not flat gray) | DDS relink under `textures/` |

Do not drill navigation shortcuts or workspaces — one pass, ~5–10 minutes.

---

## Optional: render from debug

If you want Cycles inside debug (still not for student lab time):

```bash
blenderproc debug scripts/render_demo.py -- --force-render --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --output output/lesson_08_debug
```

YOLO labels still require `blenderproc run`, not debug.

---

## Optional extras (only if time)

- Open `Scene_Morning.blend` directly in Blender to show the authored environment without the tank.
- Open `ztz_99a_0.obj` alone to show scale and DDS materials.

These are illustrative — not required for the lesson outcome.
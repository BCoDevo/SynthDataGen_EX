# Exercise 8 — Blender GUI walkthrough

Use with `LESSON.md` Exercise 8. **Goal:** see the same scene the CLI builds — orbit the viewport, read the Outliner — then close Blender yourself. No render runs; Blender does not auto-exit when the script finishes.

**Prerequisite:** Exercise 5 (`blenderproc run` full environment).

---

## Path A — Live scene from the pipeline (`blenderproc debug`)

`blenderproc debug` opens Blender with `render_demo.py` loaded. **Inspect-only is the default in debug** — the script sets up the environment, tank, and camera, then stops. Blender stays open.

```bash
blenderproc debug scripts/render_demo.py -- --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --tank-location 0 3 0.2 --camera-offset 10 -10 4
```

Use forward slashes on all platforms. Run from the **repo root**.

### What happens

1. Blender opens on the **Scripting** workspace (scene is empty at first — expected).
2. Click **Run BlenderProc** (toolbar above the text editor).
3. Log prints: environment open, tank load, `Inspect-only — scene ready in Layout`.
4. Blender switches to **Layout** and frames the tank. Orbit the viewport.

The terminal stays attached until you **close Blender** — that is normal.

### What to inspect

| Area | Look for |
|------|----------|
| **Outliner** | Tank mesh (`ztz_99a_0`); ~64 environment objects |
| **3D Viewport** | Tank on terrain; HDR-lit scene |
| **Properties → Object → Transform** | Location ≈ `(0, 3, 0.2)` per `--tank-location` |
| **View → Cameras → Active Camera** / **Numpad 0** | Demo camera framing vs. Exercise 5 PNG |

**Navigate:** MMB orbit · Shift+MMB pan · scroll zoom · **Numpad .** frame selection

### Optional: render from debug

To run Cycles inside debug (Blender still closes when you quit the app afterward):

```bash
blenderproc debug scripts/render_demo.py -- --force-render --environment assets/environment/Scene_Morning.blend --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj --output output/lesson_08_debug
```

YOLO labels still require `blenderproc run`, not debug.

---

## Path B — Environment `.blend` alone

Copy the Blender path from any `blenderproc run` log:

```
Using blender in /home/<you>/blender/blender-4.2.1-linux-x64/...
```

```bash
# Linux / macOS
/path/to/blender assets/environment/Scene_Morning.blend
```

```powershell
# Windows
& "C:\path\to\blender.exe" assets/environment/Scene_Morning.blend
```

| Target | Note |
|--------|------|
| Outliner → `Camera` | Baked scene camera; differs from demo camera |
| Ground near `(0, 3, 0)` | Tank pivot from the script |
| Shading on terrain | Texture nodes → `assets/environment/Textures/` |

---

## Path C — Tank OBJ alone

**File → Import → Wavefront (.obj)** from a blank file, or:

```bash
/path/to/blender --factory-startup assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj
```

| Check | Expected |
|-------|----------|
| Materials | DDS textures in Shading (not flat gray) |
| Scale | Large game export (tens of meters) |
| Mesh | Single object — this is what segmentation labels |

---

## Instructor screenshot checklist (optional)

1. Scripting tab — **Run BlenderProc** button
2. Layout — Outliner with tank + environment
3. Transform panel vs. `--tank-location`
4. Camera view (Numpad 0) vs. `output/lesson_05/images/render.png`
5. Shading — tank DDS nodes
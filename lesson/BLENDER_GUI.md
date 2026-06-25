# Exercise 8 — Blender GUI walkthrough

Use this alongside `LESSON.md` Exercise 8. Screenshots are optional for instructors; each step describes what you should see.

**Prerequisite:** Complete Exercise 5 so you have a mental model of the full scene.

---

## Path A — Inspect the live pipeline (`blenderproc debug` + pause)

This opens Blender with `render_demo.py` loaded and **holds before the Cycles render** so you can orbit the scene.

```bash
blenderproc debug scripts/render_demo.py -- \
  --environment assets/environment/Scene_Morning.blend \
  --hdr assets/environment/HDRs/spruit_sunrise_4k.hdr \
  --tank assets/objects/tank/cn_ztz_99a/ztz_99a_0.obj \
  --tank-location 0 3 0.2 \
  --camera-offset 10 -10 4 \
  --resolution 640 360 \
  --samples 4 \
  --pause-before-render \
  --output output/lesson_08
```

### Step 1 — Scripting workspace

| Area | What to look for |
|------|------------------|
| Text editor (top) | `render_demo.py` source |
| BlenderProc panel | **Run BlenderProc** button |
| System console | Log lines (`Opening environment`, `Loading tank`, `Pause before render`) |

Run the script once. When the console prints **Pause before render**, do **not** press Enter yet.

### Step 2 — Layout workspace (scene paused)

| Area | What to look for |
|------|------------------|
| **Outliner** (top-right) | `ztz_99a_0` or similar tank mesh; dozens of environment meshes if not `--tank-only` |
| **3D Viewport** | Tank on terrain; demo camera framing |
| **Properties → Object → Transform** | Location ≈ `(0, 3, 0.2)` when tank-location matches |

**Navigate:** Middle-mouse orbit, Shift+middle-mouse pan, scroll zoom. Press **Numpad .** to frame the selected object.

**Compare:** Transform location vs. your `--tank-location` from Exercises 3–4.

### Step 3 — Camera

| Action | What to look for |
|--------|------------------|
| Select camera in Outliner (or View → Cameras → Active Camera) | Orange pyramid icon |
| **Numpad 0** | Camera view — should match your rendered PNG framing |
| Adjust `--camera-offset` in a later run | Camera moves relative to tank center |

### Step 4 — Resume render

Focus the system console / terminal and press **Enter**. The script finishes the RGB + YOLO passes and writes `output/lesson_08/`.

---

## Path B — Environment `.blend` alone

Copy the Blender path from any `blenderproc run` log:

```
Using blender in C:\Users\<you>\blender\blender-4.2.1-windows-x64\...
```

```bash
# Windows — quote the path from your log
& "<path-to-blender>\blender.exe" assets\environment\Scene_Morning.blend
```

### What to inspect

| Target | Where | Note |
|--------|-------|------|
| Baked scene camera | Outliner → `Camera` | Authored framing; differs from demo camera |
| Ground placement | 3D cursor near `(0, 3, 0)` | Tank pivot used by the script |
| World shader | Shading workspace → World | May be empty/overridden at render time by HDR |
| Terrain materials | Shading → mesh selected | Image Texture nodes → filenames under `assets/environment/Textures/` |

---

## Path C — Tank OBJ alone

```bash
& "<path-to-blender>\blender.exe" --factory-startup assets\objects\tank\cn_ztz_99a\ztz_99a_0.obj
```

Or **File → Import → Wavefront (.obj)** from a blank file.

| Check | Expected |
|-------|----------|
| Materials | DDS textures visible in Shading (not flat gray) |
| Scale | Real-world sized mesh (tens of meters — game export) |
| Outliner | Single primary mesh object |

This mesh is what instance segmentation colorizes for YOLO — the bounding box wraps its projected silhouette.

---

## Instructor screenshot checklist (optional)

Capture these for slide decks:

1. Scripting tab with Run BlenderProc highlighted
2. Outliner with tank + environment expanded
3. Object Properties Transform next to a render with same `--tank-location`
4. Camera view (Numpad 0) beside `output/lesson_05/images/render.png`
5. Shading workspace on tank with DDS texture nodes

Save under `lesson/screenshots/` if you add them to the repo (not required for students).
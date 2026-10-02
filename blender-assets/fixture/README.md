# Shared GLB fixture (T1 gate)

Local validation UI pinned to **Three.js r160**, npm `three@0.160.0`. This directory contains no production video, later-task asset, server deployment, or asset-store acceptance operation.

## Run

Node.js 20+ and npm are required. From this directory:

```sh
npm ci --ignore-scripts
npm test
npm run validate -- ../T1-device-mockups/out --strict
npm run check:t1
npm run serve
```

Open `http://127.0.0.1:4173/` and choose a self-contained local `.glb`, or open:

- `http://127.0.0.1:4173/?model=/assets/T1-device-mockups/out/phone.glb`
- `http://127.0.0.1:4173/?model=/assets/T1-device-mockups/out/laptop.glb`

The file picker calls r160 `GLTFLoader.parseAsync` on the selected bytes. It does not upload the GLB. The local server serves this fixture and `../` beneath `/assets/`, binds loopback by default, rejects paths/symlinks outside those roots, and does not contact a remote CDN. Any self-contained, uncompressed GLB supported by the r160 loader can be inspected. Draco, KTX2, and Meshopt decoder setup is not bundled; external resources are outside this fixture's self-contained contract.

`HOST` and `PORT` customize the local server only if your environment permits it. Do not weaken browser security or network isolation to bypass a blocked execution environment.

## Controls and contracts

- **Themes:** `themes.json` contains neutral, warm and cool palettes. Materials are recolored by `material.extras.role`, then material `material_role`, node `role`, and finally material-name fallback. The actual T1 roles `hf_surface`, `hf_muted`, and `hf_screen` are included. Materials are cloned per mesh so node-specific changes do not leak to unrelated meshes.
- **Screen:** standalone mesh named `screen`, or a mesh with `screen_aspect`/screen-role metadata. The test canvas labels the red, green, blue and yellow quadrants **左上 / 右上 / 左下 / 右下**. It uses sRGB and `flipY=false`, matching glTF's top-left image origin. Front-of-screen framing uses the physical device axes, independent of UVs, so mirrored/flipped UVs cannot silently pass by rotating the camera to match them.
- **Lid:** object named `lid`, with `lid_angle_range` in its extras. Reversed endpoints such as `[0, -2.268928]` are sorted for the slider. T1 stores radians; negative X rotation opens the closed horizontal lid toward +Y. The fixture applies the slider directly to `lid.rotation.x`. Missing range metadata disables the slider instead of inventing limits.
- **Animation:** select an exported clip and seek to absolute time. Every seek resets/re-arms the chosen action then calls `mixer.setTime(t)`. There is no frame-delta accumulator and no animation loop. Resetting before a seek is important when seeking backward after the clip has finished.
- **Characters:** individual visibility switches appear for nodes with `character_index`/`characterIndex`, or numeric `char`/`character`/`glyph` names. Nested character children are not shown twice.
- **Icons:** files/nodes marked as icons expose exactly 2,000 seeded `MeshSurfaceSampler` points. The world-space triangle collection makes selection proportional to surface area across all component meshes. Equal seeds reproduce the same points; meshes are not changed.
- **Save PNG:** captures a still preview. No video export path exists.

## Checks

### Khronos Validator

```sh
npm run validate -- ../T1-device-mockups/out --strict
npm run validate -- path/to/a.glb path/to/b.glb --out reports/custom
```

Uses the official `gltf-validator@2.0.0-dev.3.10` npm build. Writes a complete report per content hash plus `summary.json`. Errors produce a nonzero exit; `--strict` also rejects warnings. Embedded resources are allowed; external resources are rejected. Informational messages are retained, not suppressed.

### T1 contract inspection

```sh
npm run check:t1
npm run check:t1 -- ../T1-device-mockups/out/laptop.glb
```

Loads the **actual GLBs** through Three r160 in Node. Checks device names, meter units, root transforms, screen geometry/aspect, full UV coverage, top-left UV orientation in physical coordinates, role extras, zero-area triangles, lid hierarchy, hinge origin, angle range, 105° default and hinge stability/opening direction at six angles. Writes `reports/t1-contract.json`. This is not a substitute for the separate Blender topology and 131-angle collision test in T1.

### Browser screenshots and exact pixel repeat

Use an installed Chromium that the environment permits. The script uses Playwright's normal launch configuration and adds no custom security flags.

```sh
CHROMIUM_EXECUTABLE=/usr/bin/chromium npm run check:browser
# Or, with the Playwright-managed browser already installed:
npm run check:browser
# Custom local GLB:
CHROMIUM_EXECUTABLE=/path/to/chromium npm run check:browser -- path/to/asset.glb
```

This starts a temporary loopback server and exercises the real local file input. It records overview/screenshots, samples all four screen quadrant colors in the physical frame, compares decoded pixel arrays after `[t3, 0, t1, t3]`, tests lid angles, compares themes, and checks character/sampling controls when present. PNGs and reports go in `reports/browser/` and are intentionally trackable.

Exit codes: `0` passed, `1` failed, `2` blocked at browser launch. A static GLB's repeat test only verifies deterministic rendering; it does **not** demonstrate animation motion. T1 exports no animation clips. The mathematical absolute-time animation behavior is separately unit-tested using a synthetic keyframe track.

## Verified results on 2026-10-02

- `npm test`: **8/8 passed**, including exact dependency version, negative range parsing, role palettes, seeded 2,000-point output, character detection and backward/end-of-clip absolute seek
- Khronos strict validation: **0 errors and 0 warnings** for both final T1 GLBs; raw informational messages retained
- T1 contract inspection: **both passed** against the final GLB hashes recorded in the reports
- Browser rendering/pixel checks: **blocked, not passed**. Normal Chromium launch failed at `process_singleton_posix.cc` with `socket() failed: Operation not permitted`. One approved command-escalation retry had the same failure. The provided cloud browser also rejected the running fixture URL with `net::ERR_BLOCKED_BY_CLIENT`
- No browser screenshot was captured. CPU Blender renders elsewhere in T1 are separate evidence and do not prove the fixture's WebGL output

The checked-in `reports/browser/report.json` records the observed blocker and unverified checks. The complete browser suite must be rerun in a permitted environment before claiming browser pixel acceptance.

## Sources

- [Three r160 GLTFLoader](https://github.com/mrdoob/three.js/blob/r160/examples/jsm/loaders/GLTFLoader.js)
- [Three r160 AnimationMixer](https://github.com/mrdoob/three.js/blob/r160/src/animation/AnimationMixer.js)
- [Three r160 MeshSurfaceSampler](https://github.com/mrdoob/three.js/blob/r160/examples/jsm/math/MeshSurfaceSampler.js)
- [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator)

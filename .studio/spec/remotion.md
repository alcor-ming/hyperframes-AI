# Optional Remotion Scene Pilot

Status: development pilot, not a qualified Windows production renderer.
The base HyperFrames runtime does not install or load React or Remotion.

## Ownership

HyperFrames owns the composition clock, playback, scrubbing, narration, BGM and
mixing. `remotion/preview.jsx` mounts a paused, muted Remotion Player and maps
HF global seconds to local integer frames through `runtime/scene-binding.js`.
It has no autonomous playback clock and no MP4 preview fallback. Dispose removes
listeners and the React root. Keep media audio in HF, not native audio elements
inside a Remotion component.

The caller supplies a component, frame rate, positive canvas dimensions and frame
count, plus a `ready` promise that preloads every required image/font/media asset.
The bridge waits for that promise and document fonts before seeking. Rejected
readiness and render errors are failures, not successful black frames. This pilot
does not yet guarantee readiness for arbitrary dynamically mounted video assets;
those compositions are not production-qualified.

## Studio Initialization

Mount only after the document contains the target element. Studio 0.8.27 bundles
local external scripts at the first script position, so a body script may execute
in the head. Use `DOMContentLoaded` when `document.readyState === 'loading'`, not
a timeout or retry. The container must be a connected HTML element in this
document. Native DOM membership validates the node across realms; neither the
current nor owner-document `HTMLElement` constructor reliably describes all
Studio-created wrappers. No constructors or node prototypes are replaced.

Invalid containers, components and dimensions have separate errors. Resource and
render failures reject readiness/seeks and use the existing Studio player error
overlay, with an inline alert for standalone pages. Load/ready cannot erase an
active failure. Disposal removes reporting/listeners and the React root, including
on document navigation; late failures from disposed instances are ignored. After
a replacement scene is ready and rendered, an already-ready host may clear the
previous error. HyperFrames remains the sole clock.

`node tests/remotion-init.mjs` runs isolated A (standalone scene), B (real Studio
DOM without React/Remotion), and C (real Studio integration) checks. Set
`HF_PACKAGE` to locked HyperFrames 0.8.27, `CHROME_PATH` to local Chromium,
`GSAP_FILE` to local gsap.min.js beside MotionPathPlugin.min.js, and `FONT_FILE`
to a local font. The fixture tests actual font/image readiness, screenshot pixels,
play/pause, direct/reverse/repeated seeks, disposal/remount/navigation, invalid
inputs, missing images and component exceptions, including visible failure and
same-document recovery. Results record the platform and each layer separately.
It is silent: WSL Studio integration is not Windows-native or audio acceptance.
The existing Windows-only `tests/remotion-studio.mjs` retains its native boundary.

## Local Verification

Install the optional locked toolchain with `npm ci --prefix .studio/remotion`.
Bundle `preview.jsx` with the composition using the pinned esbuild. Set local
`HF_RUNTIME`, `GSAP_FILE` (beside MotionPathPlugin.min.js) and `CHROME_PATH`, then
run `node tests/remotion-preview.mjs`. This creates only a synthetic temporary
HTML project, WAV tone, screenshots and a JSON report. It never exports video.
This WSL check is explicitly visual-only. It retains the observed audio element
state but does not certify audio synchronization. The earlier time-zero audio
probe failure remains unresolved and is handed to native Windows verification.

On native Windows, set `HF_PACKAGE` to the pinned HyperFrames package directory
instead of `HF_RUNTIME`, and run `node tests/remotion-studio.mjs`. This exercises
the actual Studio iframe and controls; it intentionally rejects WSL execution.
Physical audible synchronization still requires a separately recorded native
listening check. Automated clock checks alone cannot certify that result.
If the audio-element probe stays at zero while the picture advances, inspect
HF's actual audio owner (including the Studio parent/player) before changing
the probe. Do not disable the native assertion to report a successful audio check.

The WSL pilot covers readiness delay, forward/backward seeks, semantic text
reveals, repeated seek equality, playback/pause, disposal and screenshot pixels.
It is not evidence for Windows Studio, native sound, rendering parity, dependency
cache reuse, existing Scene conversion or production acceptance.

## Delivery Boundary

Do not enable this optional adapter in production until native Studio seek,
ready, playback/audio and accepted-production Final parity are verified. Do not
render Draft or test-purpose video. Production Finalize remains the only video
export path. The Windows runtime lock remains unchanged; no optional dependency
has been silently added to deployed runtime packages.

API references: [Player](https://www.remotion.dev/docs/player/player),
[buffer state](https://www.remotion.dev/docs/player/buffer-state).

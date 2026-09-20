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

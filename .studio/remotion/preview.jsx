import React, {createRef} from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {Player} from '@remotion/player';

// Bundle only for projects that opt into Remotion. HF remains the only clock.
export function mountRemotion({container, component, inputProps = {}, start = 0,
  fps, durationInFrames, width, height, ready = Promise.resolve()}) {
  if (!(container instanceof HTMLElement) || typeof component !== 'function' ||
      !Number.isFinite(start) || start < 0 || !Number.isFinite(fps) || fps <= 0 ||
      ![durationInFrames, width, height].every(n => Number.isSafeInteger(n) && n > 0)) {
    throw new TypeError('Remotion needs a container, component and positive frame/canvas dimensions');
  }
  if (!window.HarnessScene) throw new Error('Load scene-binding.js before mounting Remotion');
  const root = createRoot(container), ref = createRef();
  let failure, disposed = false;
  flushSync(() => root.render(<Player ref={ref} component={component} inputProps={inputProps}
    fps={fps} durationInFrames={durationInFrames} compositionWidth={width} compositionHeight={height}
    controls={false} autoPlay={false} loop={false} initiallyMuted numberOfSharedAudioTags={0}
    clickToPlay={false} doubleClickToFullscreen={false} spaceKeyToPlayOrPause={false}
    style={{width: '100%', height: '100%'}}
    errorFallback={({error}) => { failure = error; return <pre role="alert">{error.message}</pre>; }}
  />));
  const player = ref.current;
  if (!player) { root.unmount(); throw new Error('Remotion Player did not mount'); }
  const pause = () => { if (player.isPlaying()) player.pause(); };
  const mute = () => { if (!player.isMuted()) player.mute(); };
  const error = event => { failure = event.detail.error; };
  player.addEventListener('play', pause);
  player.addEventListener('mutechange', mute);
  player.addEventListener('error', error);
  // Content preloads assets through ready. No black-frame timeout fallback.
  const assetsReady = Promise.all([ready, document.fonts.ready]);
  const binding = window.HarnessScene.bindScene({start, duration: durationInFrames / fps,
    ready: assetsReady,
    renderAt(time) {
      if (disposed) return;
      if (failure) throw failure;
      const frame = Math.min(durationInFrames - 1, Math.max(0, Math.floor(time * fps + 1e-7)));
      flushSync(() => { pause(); mute(); player.seekTo(frame); });
      if (failure) throw failure;
      container.dataset.remotionFrame = String(frame);
    },
    dispose() {
      disposed = true;
      player.removeEventListener('play', pause);
      player.removeEventListener('mutechange', mute);
      player.removeEventListener('error', error);
      root.unmount();
    },
  });
  return binding;
}

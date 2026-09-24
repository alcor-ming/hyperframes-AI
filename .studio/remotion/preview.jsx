import React, {createRef} from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {Player} from '@remotion/player';

const initializationErrors = new Map();
let recoverPreview;
const activeErrors = new Set();

function showError(error) {
  const doc = document, iframe = window.frameElement;
  const host = iframe?.getRootNode().host;
  const alert = doc.createElement('pre');
  alert.setAttribute('role', 'alert');
  alert.textContent = error.message;
  (doc.body || doc.documentElement).appendChild(alert);
  let active = true;
  const report = () => {
    if (!active || !iframe?.isConnected || iframe.contentDocument !== doc ||
        host?.localName !== 'hyperframes-player' || iframe.getRootNode().host !== host) return;
    host.pause();
    host.dispatchEvent(new host.ownerDocument.defaultView.CustomEvent('error', {detail: {message: error.message}}));
  };
  activeErrors.add(report);
  // Studio clears errors at load/ready. Preserve only this document's failure.
  host?.addEventListener('ready', report);
  iframe?.addEventListener('load', report);
  const clear = () => {
    if (!active) return;
    active = false;
    activeErrors.delete(report);
    alert.remove();
    host?.removeEventListener('ready', report);
    iframe?.removeEventListener('load', report);
    window.removeEventListener('pagehide', clear);
    recoverPreview = () => {
      if (activeErrors.size || !host?.ready || iframe.contentDocument !== doc || !iframe.isConnected) return;
      // Re-announce an already-ready host only after the replacement scene rendered.
      host.dispatchEvent(new host.ownerDocument.defaultView.CustomEvent('ready', {detail: {duration: host.duration}}));
      recoverPreview = undefined;
    };
  };
  window.addEventListener('pagehide', clear, {once: true});
  report();
  return clear;
}

// Bundle only for projects that opt into Remotion. HF remains the only clock.
export function mountRemotion({container, component, inputProps = {}, start = 0,
  fps, durationInFrames, width, height, ready = Promise.resolve()}) {
  initializationErrors.get(container)?.();
  initializationErrors.delete(container);
  const invalid = message => {
    const error = new TypeError(message);
    initializationErrors.set(container, showError(error));
    throw error;
  };
  let validContainer = false;
  try {
    // Native DOM brand + document membership, not a realm-specific prototype.
    validContainer = Node.prototype.contains.call(document, container) && container.nodeType === 1 &&
      container.namespaceURI === 'http://www.w3.org/1999/xhtml' && container.ownerDocument === document;
  } catch { /* Non-DOM objects must not pass structural lookalike checks. */ }
  if (!validContainer) invalid('Remotion container must be a connected HTML element in this document');
  if (typeof component !== 'function') invalid('Remotion component must be a function');
  if (!Number.isFinite(start) || start < 0 || !Number.isFinite(fps) || fps <= 0 ||
      !Number.isFinite(durationInFrames / fps) ||
      ![durationInFrames, width, height].every(n => Number.isSafeInteger(n) && n > 0)) {
    invalid('Remotion requires nonnegative start, positive fps and positive integer frame/canvas dimensions');
  }
  if (!window.HarnessScene) invalid('Load scene-binding.js before mounting Remotion');
  const root = createRoot(container), ref = createRef();
  let failure, clearError, rejectFailure, disposed = false;
  const failed = new Promise((_, reject) => { rejectFailure = reject; });
  failed.catch(() => {});
  const fail = error => {
    if (disposed || failure) return;
    failure = error instanceof Error ? error : new Error(String(error));
    clearError = showError(failure);
    rejectFailure(failure);
  };
  try { flushSync(() => root.render(<Player ref={ref} component={component} inputProps={inputProps}
    fps={fps} durationInFrames={durationInFrames} compositionWidth={width} compositionHeight={height}
    controls={false} autoPlay={false} loop={false} initiallyMuted numberOfSharedAudioTags={0}
    clickToPlay={false} doubleClickToFullscreen={false} spaceKeyToPlayOrPause={false}
    style={{width: '100%', height: '100%'}}
    errorFallback={({error}) => { fail(error); return <pre role="alert">{error.message}</pre>; }}
  />)); } catch (error) {
    disposed = true;
    clearError?.();
    root.unmount();
    initializationErrors.set(container, showError(error));
    throw error;
  }
  const player = ref.current;
  if (!player) { root.unmount(); clearError?.(); invalid(failure?.message || 'Remotion Player did not mount'); }
  const pause = () => { if (player.isPlaying()) player.pause(); };
  const mute = () => { if (!player.isMuted()) player.mute(); };
  const error = event => { fail(event.detail.error); };
  player.addEventListener('play', pause);
  player.addEventListener('mutechange', mute);
  player.addEventListener('error', error);
  // Content preloads assets through ready. No black-frame timeout fallback.
  const assetsReady = Promise.race([Promise.all([ready, document.fonts.ready]), failed]).catch(error => {
    fail(error);
    throw error;
  });
  assetsReady.catch(() => {});
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
      clearError?.();
      window.removeEventListener('pagehide', binding.dispose);
      player.removeEventListener('play', pause);
      player.removeEventListener('mutechange', mute);
      player.removeEventListener('error', error);
      root.unmount();
    },
  });
  window.addEventListener('pagehide', binding.dispose, {once: true});
  assetsReady.then(async () => {
    if (disposed) return;
    await binding.seek(window.frameElement?.getRootNode().host?.currentTime ?? 0);
    if (!disposed && !failure) recoverPreview?.();
  }).catch(fail);
  return binding;
}

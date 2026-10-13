/* stage-light · 可编辑示例编排（16s 无声）
 *
 * 引用 stage-full 卡的 stage-rig 资产折叠机制（stage-full/stage-rig），但只开两页
 * 面板、少一层道具、没有焦点光与吊灯；转折靠一个持续存在的关键纸卡与它自身的
 * 空间位移，而不是整台淡出或一张张翻页的幻灯片。
 *
 * 一条 paused GSAP 主时间线注册到 window.__timelines["stage-light-example"]，
 * 同一条时间线交给 HarnessScene.bindScene 接收宿主 hf-seek。renderAt(t) 直接按
 * 时间求完整状态，不依赖回调、RAF、Date 或 Math.random。
 */
(function (global) {
  "use strict";

  var DURATION = 16;
  var root = document.getElementById("stage-light-example");
  var byId = function (id) { return document.getElementById(id); };

  // 共享折叠装置：只有内板一对（两页式），一层地面桥，一个道具脚。
  var rig = global.HarnessStageRig.createPaperStage({
    mount: byId("rig"), name: "light", panels: 2, floor: true, props: true
  });

  // 128px 纸卡左上角坐标（transform 之前）。
  var OBSERVE = [[476, 800], [644, 800], [812, 800], [980, 800], [1148, 800], [1316, 800]];
  var GROUPED = [[600, 800], [1120, 800], [740, 800], [1260, 800], [880, 800], [1400, 800]];
  var KEY = 2; // 圆形薄荷卡：贯穿重建的关键对象
  var HAND = 1; // 方形钢蓝卡：由角色交接、再由学习者放进方形托盘的关键对象

  var tokens = [byId("tok-0"), byId("tok-1"), byId("tok-2"), byId("tok-3"), byId("tok-4"), byId("tok-5")];
  var leaders = [byId("lead-0"), byId("lead-1"), byId("lead-2"), byId("lead-3"), byId("lead-4"), byId("lead-5")];
  var stepEl = byId("step");
  var calloutEl = byId("callout");
  var readbar = byId("readbar");

  var MOVE0 = 6.70, MOVE_STEP = 0.42, MOVE_DUR = 0.80;

  var fold = { inner: 0, outer: 0, floor: 0, prop: 0 };

  var CALLOUTS = [
    { a: 1.45, b: 1.85, c: 6.05, d: 6.35, text: "观察：先看清每一张纸卡" },
    { a: 6.60, b: 7.00, c: 10.95, d: 11.20, text: "分组：按形状找共同点" },
    { a: 13.45, b: 13.85, c: 14.05, d: 14.30, text: "解释：外形不同，规则相同" }
  ];

  function ramp(t, a, b, c, d) {
    if (t <= a || t >= d) return 0;
    if (t < b) return (t - a) / (b - a);
    if (t > c) return 1 - (t - c) / (d - c);
    return 1;
  }

  var T = gsap.timeline({ paused: true, defaults: { ease: "power2.out", duration: 0.5 } });

  // ---------- 0s 初始帧（立即写入；paused 时间线在 0s 的渲染是 no-op） ----------
  gsap.set("#cover-sheet", { y: 0 });
  gsap.set(".header", { autoAlpha: 0, y: -16 });
  gsap.set("#tray-round", { autoAlpha: 0, y: 32 });
  gsap.set("#tray-block", { autoAlpha: 0, y: 32 });
  gsap.set("#leaf-card-a", { autoAlpha: 0 });
  gsap.set("#leaf-card-b", { autoAlpha: 0 });
  gsap.set("#rule-tag", { autoAlpha: 0, y: 14 });
  gsap.set("#recap .chip", { y: 0, scale: 1 });
  gsap.set("#recap", { autoAlpha: 0, y: -12 });
  gsap.set("#readbar", { autoAlpha: 0, x: 540, y: 944, scaleX: 0.6 });
  gsap.set("#rig", { y: 0, scale: 1 });
  tokens.forEach(function (node, i) {
    gsap.set(node, { x: OBSERVE[i][0], y: OBSERVE[i][1], autoAlpha: 0, scale: 0.92 });
  });
  leaders.forEach(function (path) { gsap.set(path, { opacity: 0 }); });

  // 角色 0s 初始状态：明确写入，配合 fromTo/immediateRender:false 保证重复与倒放 seek 一致
  gsap.set(".layer-stage", { scale: 1, x: 0, y: 0 });
  gsap.set(".fig-mouth-smile", { autoAlpha: 1 });
  gsap.set("#figures", { autoAlpha: 1 });
  gsap.set("#fig-host", { autoAlpha: 0, y: 70 });
  gsap.set("#fig-learner", { autoAlpha: 0, y: 70 });
  gsap.set("#fig-host .fig-root", { rotation: 0, y: 0, svgOrigin: "130 496" });
  gsap.set("#fig-learner .fig-root", { rotation: 0, y: 0, svgOrigin: "120 456" });
  gsap.set("#fig-host .fig-head", { rotation: 0, svgOrigin: "130 190" });
  gsap.set("#fig-learner .fig-head", { rotation: 0, svgOrigin: "120 150" });
  gsap.set("#fig-host .fig-gaze", { x: 0, y: 0 });
  gsap.set("#fig-learner .fig-gaze", { x: 0, y: 0 });
  gsap.set("#fig-host .fig-arm-near", { rotation: 0, svgOrigin: "160 204" });
  gsap.set("#fig-host .fig-arm-far", { rotation: 0, svgOrigin: "108 204" });
  gsap.set("#fig-learner .fig-arm-near", { rotation: 0, svgOrigin: "80 190" });
  gsap.set("#fig-learner .fig-arm-far", { rotation: 0, svgOrigin: "162 190" });
  gsap.set("#fig-host .fig-mouth-open", { autoAlpha: 0 });
  gsap.set("#fig-learner .fig-mouth-open", { autoAlpha: 0 });

  // ---------- 开场：纸封面升起，两页布景展开 ----------
  T.fromTo(".header", { autoAlpha: 0, y: -16 }, { autoAlpha: 1, y: 0, duration: 0.4, immediateRender: false }, 1.00)
    .to("#cover-sheet", { y: -1080, duration: 0.60, ease: "power3.inOut" }, 0.85)
    .to(fold, { floor: 1, duration: 0.50 }, 1.20)
    .to(fold, { inner: 1, duration: 0.55 }, 1.15)
    .to(fold, { prop: 1, duration: 0.40 }, 1.70)
    .fromTo("#leaf-card-a", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.40, immediateRender: false }, 1.85);

  tokens.forEach(function (node, i) {
    T.fromTo(node,
      { y: OBSERVE[i][1] + 40, autoAlpha: 0, scale: 0.90 },
      { y: OBSERVE[i][1], autoAlpha: 1, scale: 1, duration: 0.28, ease: "power3.out", immediateRender: false },
      1.42 + i * 0.05);
  });

  // ---------- ① 观察：读行扫过一排纸卡，逐个点名 ----------
  T.fromTo(readbar, { autoAlpha: 0, x: 540, scaleX: 0.6 }, { autoAlpha: 0.9, scaleX: 1, duration: 0.40, immediateRender: false }, 2.30)
    .to(readbar, { x: 1380, duration: 2.00, ease: "sine.inOut" }, 3.20)
    .to(readbar, { autoAlpha: 0, duration: 0.40 }, 5.30);
  tokens.forEach(function (node, i) {
    T.to(node, { y: OBSERVE[i][1] - 14, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.inOut" }, 3.35 + i * 0.30);
  });

  // ---------- ② 分组：两格托盘进入，纸卡按形状归位 ----------
  T.fromTo("#tray-round", { autoAlpha: 0, y: 32 }, { autoAlpha: 1, y: 0, duration: 0.45, immediateRender: false }, 6.15)
    .fromTo("#tray-block", { autoAlpha: 0, y: 32 }, { autoAlpha: 1, y: 0, duration: 0.45, immediateRender: false }, 6.25)
    .to(readbar, { autoAlpha: 0.85, x: 804, scaleX: 0.55, duration: 0.50 }, 6.40)
    .to(readbar, { x: 1324, duration: 0.70 }, 8.60);
  tokens.forEach(function (node, i) {
    if (i === HAND) return; // 该纸卡由角色交接，不再走机械移动
    T.to(node, { x: GROUPED[i][0], y: GROUPED[i][1], duration: MOVE_DUR, ease: "power3.inOut" }, MOVE0 + i * MOVE_STEP);
  });
  T.to("#tray-round", { scale: 1.03, duration: 0.14, yoyo: true, repeat: 1 }, 9.55)
    .to("#tray-block", { scale: 1.03, duration: 0.14, yoyo: true, repeat: 1 }, 9.62)
    .to(readbar, { autoAlpha: 0.6, duration: 0.30 }, 9.60);

  // ---------- 角色 · ① 观察：讲解者举起纸卡，学习者先看再指（更少的同时动作） ----------
  T.fromTo("#fig-host", { autoAlpha: 0, y: 70 }, { autoAlpha: 1, y: 0, duration: 0.50, ease: "back.out(1.3)", immediateRender: false }, 1.55)
    .fromTo("#fig-learner", { autoAlpha: 0, y: 70 }, { autoAlpha: 1, y: 0, duration: 0.50, ease: "back.out(1.3)", immediateRender: false }, 1.72)
    .to("#fig-host .fig-head", { rotation: 10, duration: 0.45, ease: "power2.out" }, 2.60)
    .to("#fig-host .fig-gaze", { x: 7, duration: 0.45 }, 2.60)
    .to("#fig-host .fig-arm-near", { rotation: -70, duration: 0.60, ease: "back.out(1.5)" }, 2.85)
    .to(tokens[HAND], { x: OBSERVE[HAND][0] + 14, y: OBSERVE[HAND][1] + 12, duration: 0.22, ease: "power1.in" }, 3.45)
    .fromTo(tokens[HAND], { x: OBSERVE[HAND][0] + 14, y: OBSERVE[HAND][1] + 12 }, { x: 402, y: 624, duration: 0.72, ease: "power3.out", immediateRender: false }, 3.68)
    .to("#fig-learner .fig-head", { rotation: -12, duration: 0.45 }, 4.10)
    .to("#fig-learner .fig-gaze", { x: -7, duration: 0.45 }, 4.10)
    .to("#fig-learner .fig-arm-near", { rotation: 66, duration: 0.55, ease: "back.out(1.6)" }, 4.25)
    .to("#fig-learner .fig-mouth-open", { autoAlpha: 1, duration: 0.14 }, 4.40);

  // ---------- 角色 · ② 分组：同一纸卡从讲解者交到学习者，再放进方形托盘 ----------
  T.to(tokens[HAND], { x: 896, y: 466, duration: 0.85, ease: "power1.inOut" }, 6.50)
    .to(tokens[HAND], { x: 1456, y: 653, duration: 0.85, ease: "power2.out" }, 7.35)
    .to("#fig-host .fig-arm-near", { rotation: 0, duration: 0.75, ease: "power2.out" }, 7.35)
    .to("#fig-host .fig-head", { rotation: 15, duration: 0.80 }, 6.55)
    .to("#fig-learner .fig-arm-near", { rotation: 72, duration: 0.60, ease: "power2.out" }, 6.95)
    .to("#fig-learner .fig-head", { rotation: -14, duration: 0.70 }, 6.60)
    .to(tokens[HAND], { x: 1250, y: 812, duration: 0.55, ease: "power2.in" }, 8.15)
    .to(tokens[HAND], { x: 1120, y: 800, duration: 0.55, ease: "power2.out" }, 8.72)
    .to("#fig-learner .fig-arm-near", { rotation: 86, duration: 0.55 }, 8.15)
    .to("#fig-learner .fig-head", { rotation: -18, duration: 0.55 }, 8.20)
    .to("#fig-learner .fig-gaze", { x: -4, y: 5, duration: 0.55 }, 8.20)
    .to("#fig-learner .fig-arm-near", { rotation: 0, duration: 0.65, ease: "power2.out" }, 9.55)
    .to("#fig-learner .fig-head", { rotation: 0, duration: 0.55 }, 9.45)
    .to("#fig-learner .fig-gaze", { x: 0, y: 0, duration: 0.55 }, 9.45)
    .to("#fig-learner .fig-mouth-open", { autoAlpha: 0, duration: 0.20 }, 9.50);

  // 克制的相机强调：只作用于既有场景组 .layer-stage，幅度小于 full
  T.fromTo("#stage-light-example .layer-stage", { scale: 1, y: 0 }, { scale: 1.03, y: -6, duration: 1.20, ease: "sine.inOut", immediateRender: false }, 8.30)
    .to("#stage-light-example .layer-stage", { scale: 1, y: 0, duration: 1.00, ease: "sine.inOut" }, 10.40);

  // 二者对分组结果的简单反应
  T.to("#fig-host .fig-head", { rotation: -4, duration: 0.35 }, 9.90)
    .to("#fig-host .fig-arm-near", { rotation: -46, duration: 0.50, ease: "back.out(1.4)" }, 10.00)
    .to("#fig-host .fig-arm-near", { rotation: 0, duration: 0.60, ease: "power2.out" }, 10.60)
    .to("#fig-host .fig-mouth-open", { autoAlpha: 1, duration: 0.15 }, 10.00)
    .to("#fig-host .fig-mouth-open", { autoAlpha: 0, duration: 0.20 }, 10.70)
    .to("#fig-learner .fig-head", { rotation: 7, duration: 0.35 }, 10.10)
    .to("#fig-learner .fig-mouth-open", { autoAlpha: 1, duration: 0.15 }, 10.10)
    .to("#fig-learner .fig-mouth-open", { autoAlpha: 0, duration: 0.20 }, 10.78);

  // ---------- 角色 · 随真实折叠退场，解释景再回到两侧 ----------
  T.fromTo("#figures", { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.40, ease: "power2.in", immediateRender: false }, 11.20)
    .to("#fig-host .fig-root", { y: -26, duration: 0.45, ease: "power2.in" }, 11.15)
    .to("#fig-learner .fig-root", { y: -26, duration: 0.45, ease: "power2.in" }, 11.15)
    .fromTo("#figures", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.50, ease: "power2.out", immediateRender: false }, 13.45)
    .to("#fig-host .fig-root", { y: 0, duration: 0.60, ease: "power2.out" }, 13.45)
    .to("#fig-learner .fig-root", { y: 0, duration: 0.60, ease: "power2.out" }, 13.45)
    .to("#fig-host .fig-head", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-learner .fig-head", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-host .fig-gaze", { x: 0, y: 0, duration: 0.60 }, 13.45)
    .to("#fig-learner .fig-gaze", { x: 0, y: 0, duration: 0.60 }, 13.45)
    .to("#fig-host .fig-arm-near", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-learner .fig-arm-near", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-host .fig-mouth-open", { autoAlpha: 0, duration: 0.30 }, 13.45)
    .to("#fig-learner .fig-mouth-open", { autoAlpha: 0, duration: 0.30 }, 13.45)
    .to("#fig-host .fig-head", { rotation: 7, duration: 0.28, yoyo: true, repeat: 1, ease: "sine.inOut" }, 14.30)
    .to("#fig-learner .fig-head", { rotation: 7, duration: 0.28, yoyo: true, repeat: 1, ease: "sine.inOut" }, 14.42)
    .to("#figures", { autoAlpha: 0, duration: 0.35, ease: "power2.in" }, 15.42);

  // ---------- ③ 重建：道具先塌、两页合拢、整台后退 ----------
  T.to("#tray-round", { autoAlpha: 0, y: -18, duration: 0.35 }, 11.20)
    .to("#tray-block", { autoAlpha: 0, y: -18, duration: 0.35 }, 11.22)
    .to("#leaf-card-a", { autoAlpha: 0, duration: 0.35 }, 11.22)
    .to(fold, { prop: 0, duration: 0.32, ease: "power2.in" }, 11.20);
  tokens.forEach(function (node, i) {
    if (i === KEY) return;
    T.to(node, { autoAlpha: 0, scale: 0.90, duration: 0.35 }, 11.25 + i * 0.03);
  });
  T.to(readbar, { x: 960, y: 940, scaleX: 0.7, autoAlpha: 0.75, duration: 0.55, ease: "sine.inOut" }, 11.35)
    .to(fold, { inner: 0, duration: 0.55, ease: "power2.in" }, 11.55)
    .to(tokens[KEY], { x: 900, y: 690, scale: 1.08, duration: 0.55, ease: "power3.out" }, 11.60)
    .to(fold, { floor: 0, duration: 0.45, ease: "power2.in" }, 11.70)
    .to("#rig", { y: 38, scale: 0.94, duration: 0.35, ease: "power2.inOut" }, 12.20);

  // ---------- 新地点在视野里重新展开，关键纸卡留在台上 ----------
  T.fromTo("#leaf-card-b", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.50, immediateRender: false }, 12.60)
    .to(fold, { floor: 1, duration: 0.50 }, 12.70)
    .to(fold, { inner: 1, duration: 0.55 }, 12.85)
    .to("#rig", { y: 0, scale: 1, duration: 0.55 }, 12.95)
    .to(fold, { prop: 1, duration: 0.40 }, 13.15)
    .to(readbar, { x: 964, y: 940, scaleX: 0.5, autoAlpha: 0.85, duration: 0.50, ease: "sine.inOut" }, 13.20)
    .to(tokens[KEY], { x: 900, y: 800, scale: 1, duration: 0.45, ease: "power2.inOut" }, 13.25)
    .fromTo("#rule-tag", { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.40, immediateRender: false }, 13.45);

  // ---------- 收尾：三步回顾，纸封面落下 ----------
  T.fromTo("#recap", { autoAlpha: 0, y: -12 }, { autoAlpha: 1, y: 0, duration: 0.45, immediateRender: false }, 14.30)
    .to("#readbar", { autoAlpha: 0.4, scaleX: 0.9, duration: 0.50 }, 14.35)
    .to("#recap .chip", { y: -8, scale: 1.04, duration: 0.16, yoyo: true, repeat: 1, stagger: 0.10, ease: "power2.inOut" }, 14.90)
    .to("#rule-tag", { autoAlpha: 0, duration: 0.25 }, 15.25)
    .to("#recap", { autoAlpha: 0, duration: 0.30 }, 15.25)
    .to("#readbar", { autoAlpha: 0, duration: 0.30 }, 15.40)
    .to("#cover-sheet", { y: 0, duration: 0.60, ease: "power3.inOut" }, 15.35);

  // ---------- 直接求值 ----------
  function renderAt(t) {
    rig.apply(fold);

    var step = t < 6.35 ? "① 观察" : t < 11.20 ? "② 分组" : t < 12.90 ? "③ 解释" : "观察 → 分组 → 解释";
    if (stepEl.textContent !== step) stepEl.textContent = step;

    var active = null, opacity = 0;
    for (var i = 0; i < CALLOUTS.length; i += 1) {
      var value = ramp(t, CALLOUTS[i].a, CALLOUTS[i].b, CALLOUTS[i].c, CALLOUTS[i].d);
      if (value > opacity) { opacity = value; active = CALLOUTS[i]; }
    }
    var calloutText = active ? active.text : "";
    if (calloutEl.textContent !== calloutText) calloutEl.textContent = calloutText;
    calloutEl.style.opacity = opacity.toFixed(3);

    var rebuilt = t >= 12.50;
    if (root.classList.contains("is-rebuilt") !== rebuilt) root.classList.toggle("is-rebuilt", rebuilt);

    for (var j = 0; j < tokens.length; j += 1) {
      var ox = OBSERVE[j][0] + 64, oy = OBSERVE[j][1] + 64;
      var cx = Number(gsap.getProperty(tokens[j], "x")) + 64;
      var cy = Number(gsap.getProperty(tokens[j], "y")) + 64;
      leaders[j].setAttribute("d", "M" + ox + " " + oy + "L" + cx + " " + cy);
      var start = MOVE0 + j * MOVE_STEP;
      var lineOpacity = (j === KEY || j === HAND) ? 0 : ramp(t, start - 0.10, start + 0.15, start + MOVE_DUR - 0.05, start + MOVE_DUR + 0.25) * 0.55;
      leaders[j].style.opacity = lineOpacity.toFixed(3);
    }
  }

  // ---------- 宿主接线 ----------
  global.__timelines = global.__timelines || {};
  global.__timelines["stage-light-example"] = T;

  var binding = global.HarnessScene.bindScene({
    start: 0,
    duration: DURATION,
    timeline: T,
    ready: document.fonts.ready,
    renderAt: renderAt
  });

  T.totalTime(0, true);
  renderAt(0);

  global.__example = {
    duration: DURATION,
    seek: function (time) { return binding.seek(time); },
    dispose: function () { binding.dispose(); rig.root.remove(); delete global.__timelines["stage-light-example"]; },
    ready: binding.ready
  };
})(window);

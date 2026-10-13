/* stage-full · 可编辑示例编排（16s 无声）
 *
 * 一条 paused GSAP 主时间线，注册到 window.__timelines["stage-full-example"]，
 * 同一条时间线交给 HarnessScene.bindScene 接收宿主 hf-seek。renderAt(t) 直接按
 * 时间求完整状态：铰链角度来自 GSAP 的 fold 状态，文字与指示线由 t 直接计算。
 * 不依赖事件回调、RAF、Date 或 Math.random，正放、倒放、随机 seek 结果一致。
 *
 * 折叠机制来自本卡内资产 assets/stage-rig/stage-rig.js（已授权提取）。
 */
(function (global) {
  "use strict";

  var DURATION = 16;
  var root = document.getElementById("stage-full-example");
  var byId = function (id) { return document.getElementById(id); };

  // 共享折叠装置：四块 480px 面板 + 地面桥 + 道具脚铰链。
  var rig = global.HarnessStageRig.createPaperStage({
    mount: byId("rig"), name: "full", panels: 4, floor: true, props: true
  });

  // 120px 盒子左上角坐标（transform 之前）。
  var OBSERVE = [[500, 790], [660, 790], [820, 790], [980, 790], [1140, 790], [1300, 790]];
  var GROUPED = [[610, 800], [1090, 800], [730, 800], [1210, 800], [850, 800], [1330, 800]];
  var KEY = 2; // amber：贯穿重建的关键物件
  var HAND = 1; // teal：由角色交接、再由学习者放进冷色托盘的关键物件

  var objects = [
    byId("obj-coral"), byId("obj-teal"), byId("obj-amber"),
    byId("obj-sky"), byId("obj-yellow"), byId("obj-violet")
  ];
  var leaders = [
    byId("leader-0"), byId("leader-1"), byId("leader-2"),
    byId("leader-3"), byId("leader-4"), byId("leader-5")
  ];
  var stepEl = byId("step");
  var calloutEl = byId("callout");

  var MOVE0 = 6.70, MOVE_STEP = 0.42, MOVE_DUR = 0.80;

  // GSAP 只做插值；rig.apply 把数值写成铰链角度。
  var fold = { inner: 0, outer: 0, floor: 0, prop: 0 };

  var CALLOUTS = [
    { a: 1.50, b: 1.95, c: 6.05, d: 6.35, text: "观察：先看清每一件" },
    { a: 6.60, b: 7.00, c: 10.95, d: 11.20, text: "分组：按颜色找共同点" },
    { a: 13.55, b: 13.95, c: 14.05, d: 14.30, text: "解释：去掉颜色，留下同一个道理" }
  ];

  function ramp(t, a, b, c, d) {
    if (t <= a || t >= d) return 0;
    if (t < b) return (t - a) / (b - a);
    if (t > c) return 1 - (t - c) / (d - c);
    return 1;
  }

  var T = gsap.timeline({ paused: true, defaults: { ease: "power2.out", duration: 0.5 } });

  // ---------- 0s 初始帧（立即写入；paused 时间线在 0s 的渲染是 no-op） ----------
  gsap.set(".frame-top", { y: -60 });
  gsap.set(".frame-bottom", { y: 60 });
  gsap.set("#curtain-left", { x: 0 });
  gsap.set("#curtain-right", { x: 0 });
  gsap.set("#title-card", { xPercent: -50, yPercent: -50, x: 0, autoAlpha: 0, y: 26, scale: 0.96 });
  gsap.set(".header", { autoAlpha: 0, y: -18 });
  gsap.set("#tray-warm", { autoAlpha: 0, y: 34 });
  gsap.set("#tray-cool", { autoAlpha: 0, y: 34 });
  gsap.set("#wall-card-a", { autoAlpha: 0 });
  gsap.set("#wall-card-b", { autoAlpha: 0 });
  gsap.set("#explain-tag", { autoAlpha: 0, y: 14 });
  gsap.set("#recap .chip", { y: 0, scale: 1 });
  gsap.set("#recap", { autoAlpha: 0, y: -12 });
  gsap.set("#spot-a", { autoAlpha: 0, x: 960, y: 880, scale: 1 });
  gsap.set("#spot-b", { autoAlpha: 0, x: 1210, y: 880, scale: 0.62 });
  gsap.set(".lamp-a", { rotation: 0 });
  gsap.set(".lamp-b", { rotation: 0 });
  gsap.set("#rig", { y: 0, scale: 1 });
  objects.forEach(function (node, i) {
    gsap.set(node, { x: OBSERVE[i][0], y: OBSERVE[i][1], autoAlpha: 0, scale: 0.92 });
  });
  leaders.forEach(function (path) { gsap.set(path, { opacity: 0 }); });

  // 角色 0s 初始状态：明确写入，配合 fromTo/immediateRender:false 保证重复与倒放 seek 一致
  gsap.set(".layer-stage", { force3D: false, scale: 1, x: 0, y: 0 });
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

  // ---------- 开场：台口进、标题卡、短幕开 ----------
  T.fromTo(".frame-top", { y: -60 }, { y: 0, duration: 0.45, immediateRender: false }, 0.05)
    .fromTo(".frame-bottom", { y: 60 }, { y: 0, duration: 0.45, immediateRender: false }, 0.05)
    .fromTo("#title-card", { autoAlpha: 0, y: 26, scale: 0.96 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.5, immediateRender: false }, 0.12)
    .fromTo("#curtain-left", { x: 0 }, { x: -960, duration: 0.80, ease: "power3.inOut", immediateRender: false }, 0.80)
    .fromTo("#curtain-right", { x: 0 }, { x: 960, duration: 0.80, ease: "power3.inOut", immediateRender: false }, 0.80)
    .to("#title-card", { autoAlpha: 0, y: -22, duration: 0.40 }, 0.95)
    .fromTo(".header", { autoAlpha: 0, y: -18 }, { autoAlpha: 1, y: 0, duration: 0.40, immediateRender: false }, 1.10);

  // ---------- 分层搭景：内板先开、外板随后、地面再落、道具最后立起 ----------
  T.to(fold, { inner: 1, duration: 0.50 }, 1.30)
    .to(fold, { floor: 1, duration: 0.45 }, 1.35)
    .to(fold, { outer: 1, duration: 0.50 }, 1.45)
    .to(fold, { prop: 1, duration: 0.40 }, 1.70)
    .fromTo("#wall-card-a", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.40, immediateRender: false }, 1.95);

  objects.forEach(function (node, i) {
    T.fromTo(node,
      { y: OBSERVE[i][1] + 40, autoAlpha: 0, scale: 0.90 },
      { y: OBSERVE[i][1], autoAlpha: 1, scale: 1, duration: 0.28, ease: "power3.out", immediateRender: false },
      1.45 + i * 0.05);
  });

  // ---------- ① 观察：焦点光扫过一排物件，逐个点名 ----------
  T.fromTo("#spot-a", { autoAlpha: 0, scale: 0.90 }, { autoAlpha: 0.90, scale: 1, duration: 0.50, immediateRender: false }, 2.30)
    .set(".lamp-a", { rotation: 10 }, 2.30)
    .set(".lamp-b", { rotation: -10 }, 2.30)
    .to("#spot-a", { x: 560, duration: 0.70, ease: "sine.inOut" }, 3.20)
    .to("#spot-a", { x: 1360, duration: 1.90, ease: "sine.inOut" }, 3.95)
    .to("#spot-a", { autoAlpha: 0.55, scale: 0.92, duration: 0.40 }, 5.20);
  objects.forEach(function (node, i) {
    T.to(node, { scale: 1.07, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.inOut" }, 3.35 + i * 0.30);
  });

  // ---------- ② 分组：托盘进入、焦点光成两池、物件按颜色归位 ----------
  T.fromTo("#tray-warm", { autoAlpha: 0, y: 34 }, { autoAlpha: 1, y: 0, duration: 0.45, immediateRender: false }, 6.15)
    .fromTo("#tray-cool", { autoAlpha: 0, y: 34 }, { autoAlpha: 1, y: 0, duration: 0.45, immediateRender: false }, 6.25)
    .to("#spot-a", { x: 760, y: 880, scale: 0.62, autoAlpha: 0.82, duration: 0.55, ease: "sine.inOut" }, 6.30)
    .fromTo("#spot-b", { autoAlpha: 0 }, { autoAlpha: 0.82, duration: 0.55, immediateRender: false }, 6.40)
    .to(".lamp-a", { rotation: 14, duration: 0.50 }, 6.30)
    .to(".lamp-b", { rotation: -14, duration: 0.50 }, 6.30);
  objects.forEach(function (node, i) {
    if (i === HAND) return; // 该物件由角色交接，不再走机械移动
    T.to(node, { x: GROUPED[i][0], y: GROUPED[i][1], duration: MOVE_DUR, ease: "power3.inOut" }, MOVE0 + i * MOVE_STEP);
  });
  T.to("#tray-warm", { scale: 1.03, duration: 0.14, yoyo: true, repeat: 1 }, 9.55)
    .to("#tray-cool", { scale: 1.03, duration: 0.14, yoyo: true, repeat: 1 }, 9.62)
    .to("#spot-a", { autoAlpha: 0.70, duration: 0.30 }, 9.60)
    .to("#spot-b", { autoAlpha: 0.70, duration: 0.30 }, 9.60);

  // ---------- 角色 · ① 观察：讲解者举起纸盒 token，学习者先看再指 ----------
  T.fromTo("#fig-host", { autoAlpha: 0, y: 70 }, { autoAlpha: 1, y: 0, duration: 0.50, ease: "back.out(1.3)", immediateRender: false }, 1.55)
    .fromTo("#fig-learner", { autoAlpha: 0, y: 70 }, { autoAlpha: 1, y: 0, duration: 0.50, ease: "back.out(1.3)", immediateRender: false }, 1.72)
    .to("#fig-host .fig-head", { rotation: 10, duration: 0.45, ease: "power2.out" }, 2.55)
    .to("#fig-host .fig-gaze", { x: 7, y: 1, duration: 0.45 }, 2.55)
    .to("#fig-host .fig-root", { rotation: 2.5, duration: 0.50 }, 2.60)
    .to("#fig-host .fig-arm-near", { rotation: -70, duration: 0.60, ease: "back.out(1.5)" }, 2.80)
    .to("#fig-host .fig-arm-far", { rotation: 10, duration: 0.45 }, 2.85)
    .to(objects[HAND], { x: OBSERVE[HAND][0] + 16, y: OBSERVE[HAND][1] + 14, duration: 0.22, ease: "power1.in" }, 3.42)
    .fromTo(objects[HAND], { x: OBSERVE[HAND][0] + 16, y: OBSERVE[HAND][1] + 14 }, { x: 406, y: 628, duration: 0.72, ease: "power3.out", immediateRender: false }, 3.66)
    .to("#fig-learner .fig-head", { rotation: -12, duration: 0.45 }, 4.05)
    .to("#fig-learner .fig-gaze", { x: -7, y: 1, duration: 0.45 }, 4.05)
    .to("#fig-learner .fig-root", { rotation: -2, duration: 0.50 }, 4.05)
    .to("#fig-learner .fig-arm-near", { rotation: 66, duration: 0.55, ease: "back.out(1.6)" }, 4.20)
    .to("#fig-learner .fig-arm-far", { rotation: -10, duration: 0.45 }, 4.25)
    .to("#fig-learner .fig-mouth-open", { autoAlpha: 1, duration: 0.14 }, 4.35)
    .to("#fig-learner .fig-mouth-smile", { autoAlpha: 0, duration: 0.14 }, 4.35);

  // ---------- 角色 · ② 分组：连续同一物件的交接，再放进冷色托盘 ----------
  T.to(objects[HAND], { x: 424, y: 646, duration: 0.30, ease: "power2.inOut" }, 5.55)
    .to("#fig-host .fig-arm-near", { rotation: -78, duration: 0.30 }, 5.55)
    .to("#fig-learner .fig-arm-near", { rotation: 52, duration: 0.30 }, 5.55)
    .to(objects[HAND], { x: 900, y: 470, duration: 0.75, ease: "power1.inOut" }, 6.45)
    .to(objects[HAND], { x: 1460, y: 657, duration: 0.80, ease: "power2.out" }, 7.20)
    .to("#fig-host .fig-arm-near", { rotation: -34, duration: 0.60, ease: "power2.inOut" }, 6.55)
    .to("#fig-host .fig-arm-near", { rotation: 0, duration: 0.70, ease: "power2.out" }, 7.25)
    .to("#fig-host .fig-head", { rotation: 16, duration: 0.70 }, 6.55)
    .to("#fig-host .fig-gaze", { x: 11, duration: 0.70 }, 6.55)
    .to("#fig-learner .fig-arm-near", { rotation: 72, duration: 0.55, ease: "power2.out" }, 6.85)
    .to("#fig-learner .fig-head", { rotation: -15, duration: 0.60 }, 6.45)
    .to("#fig-learner .fig-gaze", { x: -10, duration: 0.60 }, 6.45)
    .to(objects[HAND], { x: 1220, y: 812, duration: 0.55, ease: "power2.in" }, 8.05)
    .to(objects[HAND], { x: 1076, y: 796, duration: 0.45, ease: "power2.out" }, 8.62)
    .to(objects[HAND], { x: 1090, y: 800, duration: 0.30, ease: "power2.inOut" }, 9.07)
    .to("#fig-learner .fig-arm-near", { rotation: 86, duration: 0.55 }, 8.05)
    .to("#fig-learner .fig-root", { rotation: -4, duration: 0.55 }, 8.05)
    .to("#fig-learner .fig-head", { rotation: -19, duration: 0.55 }, 8.10)
    .to("#fig-learner .fig-gaze", { x: -4, y: 6, duration: 0.55 }, 8.10)
    .to("#fig-learner .fig-arm-near", { rotation: 26, duration: 0.60, ease: "power2.out" }, 8.75)
    .to("#fig-learner .fig-root", { rotation: 0, duration: 0.60 }, 8.75)
    .to("#fig-learner .fig-arm-near", { rotation: 0, duration: 0.65, ease: "power2.out" }, 9.50)
    .to("#fig-learner .fig-head", { rotation: 0, duration: 0.55 }, 9.40)
    .to("#fig-learner .fig-gaze", { x: 0, y: 0, duration: 0.55 }, 9.40)
    .to("#fig-learner .fig-mouth-open", { autoAlpha: 0, duration: 0.20 }, 9.45)
    .to("#fig-learner .fig-mouth-smile", { autoAlpha: 1, duration: 0.20 }, 9.45);

  // 一次成组强调：合成相机只推到既有场景组 .layer-stage，不缩放整篇文档
  T.fromTo("#stage-full-example .layer-stage", { scale: 1, x: 0, y: 0 }, { force3D: false, scale: 1.055, x: -24, y: -10, duration: 1.10, ease: "sine.inOut", immediateRender: false }, 8.20)
    .to("#stage-full-example .layer-stage", { force3D: false, scale: 1, x: 0, y: 0, duration: 0.90, ease: "sine.inOut" }, 10.35);

  // 二者对分组结果的共同反应
  T.to("#fig-host .fig-head", { rotation: -4, duration: 0.35 }, 9.80)
    .to("#fig-host .fig-gaze", { x: 4, duration: 0.40 }, 9.85)
    .to("#fig-host .fig-arm-near", { rotation: -48, duration: 0.50, ease: "back.out(1.5)" }, 9.95)
    .to("#fig-host .fig-mouth-open", { autoAlpha: 1, duration: 0.15 }, 9.95)
    .to("#fig-host .fig-mouth-smile", { autoAlpha: 0, duration: 0.15 }, 9.95)
    .to("#fig-host .fig-arm-near", { rotation: -18, duration: 0.55, ease: "power2.out" }, 10.55)
    .to("#fig-host .fig-mouth-open", { autoAlpha: 0, duration: 0.20 }, 10.75)
    .to("#fig-host .fig-mouth-smile", { autoAlpha: 1, duration: 0.20 }, 10.75)
    .to("#fig-learner .fig-head", { rotation: 7, duration: 0.35 }, 10.00)
    .to("#fig-learner .fig-arm-far", { rotation: -44, duration: 0.50, ease: "back.out(1.4)" }, 10.10)
    .to("#fig-learner .fig-arm-far", { rotation: 0, duration: 0.50, ease: "power2.out" }, 10.70)
    .to("#fig-host .fig-root", { y: -6, duration: 0.16, yoyo: true, repeat: 1 }, 10.25)
    .to("#fig-learner .fig-root", { y: -6, duration: 0.16, yoyo: true, repeat: 1 }, 10.25);

  // ---------- 角色 · 随真实折叠退场，解释景再回到两侧 ----------
  T.fromTo("#figures", { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.40, ease: "power2.in", immediateRender: false }, 11.20)
    .to("#fig-host .fig-root", { y: -26, duration: 0.45, ease: "power2.in" }, 11.15)
    .to("#fig-learner .fig-root", { y: -26, duration: 0.45, ease: "power2.in" }, 11.15)
    .fromTo("#figures", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.50, ease: "power2.out", immediateRender: false }, 13.45)
    .to("#fig-host .fig-root", { y: 0, rotation: 0, duration: 0.60, ease: "power2.out" }, 13.45)
    .to("#fig-learner .fig-root", { y: 0, rotation: 0, duration: 0.60, ease: "power2.out" }, 13.45)
    .to("#fig-host .fig-head", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-learner .fig-head", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-host .fig-gaze", { x: 0, y: 0, duration: 0.60 }, 13.45)
    .to("#fig-learner .fig-gaze", { x: 0, y: 0, duration: 0.60 }, 13.45)
    .to("#fig-host .fig-arm-near", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-host .fig-arm-far", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-learner .fig-arm-near", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-learner .fig-arm-far", { rotation: 0, duration: 0.60 }, 13.45)
    .to("#fig-host .fig-mouth-open", { autoAlpha: 0, duration: 0.30 }, 13.45)
    .to("#fig-learner .fig-mouth-open", { autoAlpha: 0, duration: 0.30 }, 13.45)
    .to("#fig-host .fig-mouth-smile", { autoAlpha: 1, duration: 0.30 }, 13.45)
    .to("#fig-learner .fig-mouth-smile", { autoAlpha: 1, duration: 0.30 }, 13.45)
    .to("#fig-host .fig-head", { rotation: 7, duration: 0.28, yoyo: true, repeat: 1, ease: "sine.inOut" }, 14.30)
    .to("#fig-learner .fig-head", { rotation: 7, duration: 0.28, yoyo: true, repeat: 1, ease: "sine.inOut" }, 14.42)
    .to("#figures", { autoAlpha: 0, duration: 0.35, ease: "power2.in" }, 15.42);

  // ---------- ③ 重建：道具先塌、面板再折、整台后退 ----------
  T.to("#tray-warm", { autoAlpha: 0, y: -20, duration: 0.35 }, 11.20)
    .to("#tray-cool", { autoAlpha: 0, y: -20, duration: 0.35 }, 11.22)
    .to("#wall-card-a", { autoAlpha: 0, duration: 0.35 }, 11.22)
    .to("#spot-b", { autoAlpha: 0, duration: 0.30 }, 11.15)
    .to(fold, { prop: 0, duration: 0.32, ease: "power2.in" }, 11.20);
  objects.forEach(function (node, i) {
    if (i === KEY) return;
    T.to(node, { autoAlpha: 0, scale: 0.90, duration: 0.35 }, 11.25 + i * 0.03);
  });
  T.to("#spot-a", { x: 960, y: 900, scale: 0.50, autoAlpha: 0.85, duration: 0.55, ease: "sine.inOut" }, 11.35)
    .to(fold, { outer: 0, duration: 0.55, ease: "power2.in" }, 11.45)
    .to(objects[KEY], { x: 900, y: 690, scale: 1.06, duration: 0.60, ease: "power3.out" }, 11.55)
    .to(fold, { inner: 0, duration: 0.50, ease: "power2.in" }, 11.90)
    .to(fold, { floor: 0, duration: 0.45, ease: "power2.in" }, 11.95)
    .to("#rig", { y: 40, scale: 0.94, duration: 0.35, ease: "power2.inOut" }, 12.45);

  // ---------- 新地点在视野里搭起，关键物件留在台上 ----------
  T.fromTo("#wall-card-b", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.50, immediateRender: false }, 12.65)
    .to(fold, { floor: 1, duration: 0.50 }, 12.75)
    .to(fold, { inner: 1, duration: 0.55 }, 12.85)
    .to("#rig", { y: 0, scale: 1, duration: 0.60 }, 13.00)
    .to(fold, { outer: 1, duration: 0.50 }, 13.05)
    .to("#spot-a", { x: 960, y: 880, scale: 0.72, autoAlpha: 0.90, duration: 0.50, ease: "sine.inOut" }, 13.05)
    .to(".lamp-a", { rotation: 4, duration: 0.50 }, 13.20)
    .to(".lamp-b", { rotation: -4, duration: 0.50 }, 13.20)
    .to(fold, { prop: 1, duration: 0.40 }, 13.20)
    .to(objects[KEY], { x: 900, y: 800, scale: 1, duration: 0.45, ease: "power2.inOut" }, 13.30)
    .fromTo("#explain-tag", { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.40, immediateRender: false }, 13.55);

  // ---------- 收尾：三步回顾、幕布合拢 ----------
  T.fromTo("#recap", { autoAlpha: 0, y: -12 }, { autoAlpha: 1, y: 0, duration: 0.45, immediateRender: false }, 14.35)
    .to("#spot-a", { autoAlpha: 0.50, scale: 1, duration: 0.50 }, 14.40)
    .to("#recap .chip", { y: -8, scale: 1.04, duration: 0.16, yoyo: true, repeat: 1, stagger: 0.10, ease: "power2.inOut" }, 14.95)
    .to("#explain-tag", { autoAlpha: 0, duration: 0.25 }, 15.35)
    .to("#recap", { autoAlpha: 0, duration: 0.30 }, 15.30)
    .to("#spot-a", { autoAlpha: 0, duration: 0.30 }, 15.45)
    .fromTo("#curtain-left", { x: -960 }, { x: 0, duration: 0.55, ease: "power3.inOut", immediateRender: false }, 15.40)
    .fromTo("#curtain-right", { x: 960 }, { x: 0, duration: 0.55, ease: "power3.inOut", immediateRender: false }, 15.40)
    .fromTo("#title-card", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.40, immediateRender: false }, 15.55);

  // ---------- 直接求值：每个 t 输出完整、可重建的状态 ----------
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

    // 折叠态里切换布景色，展开后就是新地点；不是整台淡出。
    var cool = t >= 12.60;
    if (root.classList.contains("is-cool") !== cool) root.classList.toggle("is-cool", cool);

    // 因果指示线：从原位连到物件当前位置。
    for (var j = 0; j < objects.length; j += 1) {
      var ox = OBSERVE[j][0] + 60, oy = OBSERVE[j][1] + 60;
      var cx = Number(gsap.getProperty(objects[j], "x")) + 60;
      var cy = Number(gsap.getProperty(objects[j], "y")) + 60;
      leaders[j].setAttribute("d", "M" + ox + " " + oy + "L" + cx + " " + cy);
      var start = MOVE0 + j * MOVE_STEP;
      var lineOpacity = (j === KEY || j === HAND) ? 0 : ramp(t, start - 0.10, start + 0.15, start + MOVE_DUR - 0.05, start + MOVE_DUR + 0.25) * 0.5;
      leaders[j].style.opacity = lineOpacity.toFixed(3);
    }
  }

  // ---------- 宿主接线 ----------
  global.__timelines = global.__timelines || {};
  global.__timelines["stage-full-example"] = T;

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
    dispose: function () { binding.dispose(); rig.root.remove(); delete global.__timelines["stage-full-example"]; },
    ready: binding.ready
  };
})(window);

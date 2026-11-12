/*
 * Evil Santa — Christmas Spirit engine
 * -------------------------------------
 * Works out how much Christmas spirit the current account (team in team mode,
 * player in user mode) has restored, and drives the meter, the wreath, the
 * "Ignite the Spirit!" ceremony and the story scenes.
 *
 * Optional admin settings (Admin > Config > Theme > Theme Settings, JSON):
 *   {
 *     "spirit_total": 45,        // fixed challenge count to divide by
 *     "spirit_season": "2026",   // change to reset everyone's saved progress
 *     "spirit_scene_ext": "webp", // file type of the scene images
 *     "spirit_ui_ext": "webp",    // file type of navbar/meter/coal/wrap images
 *     "spirit_snow": true         // set false to turn the falling snow off
 *   }
 */
(function () {
  "use strict";

  // ---- Story -------------------------------------------------------------
  // One entry per stage. `at` is the minimum % needed to earn it.
  const STAGES = [
    { at: 0,   chapter: "Prologue",   title: "A Coal-Black Christmas",
      text: "Evil Santa has stolen the colour of Christmas. No lights, no presents, just coal in every stocking. His castle looms on the hill." },
    { at: 10,  chapter: "Chapter 1",  title: "This Way to Santa's Castle",
      text: "Five kids grab a candy cane, candy corn, gingerbread stars, a gingerbread bazooka and a string of Christmas lights, and march toward the castle. The sign says: enter at your own risk." },
    { at: 20,  chapter: "Chapter 2",  title: "Candy Bomb Away!",
      text: "Evil elves keep watch on the castle walls. Leo shoulders the gingerbread bazooka and fires. A giant candy bomb sails toward the gate..." },
    { at: 30,  chapter: "Chapter 3",  title: "Cookies at the Gate",
      text: "KA-BLOOP! The gate is gone. A gingerbread star lands in one elf's mouth, a lights lasso loops another, and both turn good." },
    { at: 40,  chapter: "Chapter 4",  title: "The Hall of Antlers",
      text: "Inside the castle, evil reindeer charge down the long corridor. The kids and their new elf friends stand their ground." },
    { at: 50,  chapter: "Chapter 5",  title: "The Standoff",
      text: "The throne room. Evil Santa sits on a mountain of coal with Evil Rudolph and Evil Mrs. Claus at his side. Nobody moves... yet." },
    { at: 60,  chapter: "Chapter 6",  title: "Mayhem!",
      text: "Coal flies. Burnt cookies fly. Candy flies. Rudolph rams into two good reindeer. It's total chaos." },
    { at: 70,  chapter: "Chapter 7",  title: "The Spirit Wins",
      text: "The lights lasso catches Rudolph, a good cookie finds Mrs. Claus, and Santa sits up with a real HO HO HO." },
    { at: 80,  chapter: "Chapter 8",  title: "The Midnight Ride",
      text: "Santa's sleigh sweeps over the town while the kids throw down lights and stars. House by house, Christmas comes back." },
    { at: 90,  chapter: "Finale",     title: "Christmas Is Saved!",
      text: "In the town square, Santa, Mrs. Claus and the kids hand out real presents. Everyone is happy again." },
    { at: 100, chapter: "Secret Ending", title: "Krampus Is Not Amused",
      text: "High on the mountain, Krampus watches the whole town light up. His Naughty Fog is gone and his plan has failed, all thanks to you. You found every last flag. Legendary." },
  ];

  const SETTINGS = (window.init && window.init.themeSettings) || {};
  // Scene file type: the admin setting if given, otherwise detected from the
  // files in static/spirit/scenes/ (first of webp, png, jpg, svg that exists).
  let SCENE_EXT = SETTINGS.spirit_scene_ext || null;
  const SEASON = String(SETTINGS.spirit_season || "default");
  const URL_ROOT = (window.init && window.init.urlRoot) || "";
  const SCENE_BASE = URL_ROOT + "/themes/evil-santa/static/spirit/scenes/";
  const UI_BASE = URL_ROOT + "/themes/evil-santa/static/spirit/ui/";
  const SNOW_ON = SETTINGS.spirit_snow !== false && SETTINGS.spirit_snow !== "false";
  const WRAP_COUNT = 8;
  const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
    document.documentElement.dataset.prefMotion === "off";
  const POLL_MS = 60 * 1000;

  // ---- Account & persistence ----------------------------------------------
  function accountKey() {
    const i = window.init || {};
    const isTeams = i.userMode === "teams";
    const id = isTeams ? i.teamId : i.userId;
    if (!id) return null;
    return `evilsanta:${SEASON}:${isTeams ? "team" : "user"}:${id}`;
  }

  function loadState() {
    const fallback = { best: 0, shown: 0 };
    const key = accountKey();
    if (!key) return fallback;
    try {
      const raw = window.localStorage.getItem(key);
      return raw ? Object.assign(fallback, JSON.parse(raw)) : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function saveState(state) {
    const key = accountKey();
    if (!key) return;
    try {
      window.localStorage.setItem(key, JSON.stringify(state));
    } catch (e) {
      /* storage unavailable: progress simply isn't remembered */
    }
  }

  // ---- Maths ---------------------------------------------------------------
  // Percent is always rounded DOWN, so 40 of 45 solves = 88% (not yet 90).
  function percentOf(solved, total) {
    if (!total) return 0;
    return Math.min(100, Math.floor((solved * 100) / total));
  }

  function stageIndexFor(pct) {
    let idx = 0;
    STAGES.forEach((s, i) => { if (pct >= s.at) idx = i; });
    return idx;
  }

  // ---- Data ----------------------------------------------------------------
  async function fetchProgress() {
    const res = await fetch(URL_ROOT + "/api/v1/challenges", {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    });
    if (!res.ok) return null; // not logged in, CTF not started, etc.
    const body = await res.json();
    if (!body.success) return null;
    const list = body.data || [];
    // solved_by_me is already team-wide in team mode (CTFd uses account_id)
    const ids = list.filter((c) => c.solved_by_me).map((c) => c.id);
    const solved = ids.length;
    const configured = parseInt(SETTINGS.spirit_total, 10);
    // Challenges locked behind prerequisites may be missing from the list,
    // so an admin-set total is more reliable when it's available.
    const total = configured > 0 ? Math.max(configured, solved) : list.length;
    return { solved, total, ids, pct: percentOf(solved, total) };
  }

  // ---- DOM helpers -----------------------------------------------------------
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  function sceneUrl(idx) {
    return SCENE_BASE + "stage-" + String(STAGES[idx].at).padStart(3, "0") + "." + SCENE_EXT;
  }

  function preload(idx) {
    if (idx < STAGES.length) { const img = new Image(); img.src = sceneUrl(idx); }
  }

  // ---- Lights ----------------------------------------------------------------
  // Light the first round(n * fraction) bulbs; new ones switch on one by one.
  function lightBulbs(bulbs, fraction, animate, stepMs) {
    const lit = Math.round(bulbs.length * fraction);
    let k = 0;
    bulbs.forEach((b, i) => {
      const on = i < lit;
      const turningOn = on && !b.classList.contains("on");
      b.style.transitionDelay = turningOn && animate ? (k++ * stepMs) + "ms" : "0ms";
      b.classList.toggle("on", on);
    });
  }

  // ---- Garland along the bottom of the navbar --------------------------------
  const GARLAND_COLOURS = ["#ff3b3b", "#ffd447", "#3ddc6b", "#4cc3ff", "#ff8ad8", "#ff9d2e"];
  const SVG_NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs, parent) {
    const n = document.createElementNS(SVG_NS, tag);
    Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
    if (parent) parent.appendChild(n);
    return n;
  }

  // Bulbs light up in a scattered (but stable) order, not left to right
  function garlandBulbsInOrder() {
    return $$(".spirit-garland .bulb").sort((a, b) => a.dataset.order - b.dataset.order);
  }

  function buildGarland() {
    const host = $(".spirit-garland");
    if (!host) return;
    const width = host.clientWidth || window.innerWidth;
    const swagW = width < 600 ? 90 : 120;
    const swags = Math.max(3, Math.round(width / swagW));
    const w = width / swags;
    const sag = 16;
    host.innerHTML = "";
    const svg = el("svg", { viewBox: `0 0 ${width} 34`, preserveAspectRatio: "none" }, host);
    let d = "M0 4";
    for (let i = 0; i < swags; i++) d += ` Q${i * w + w / 2} ${4 + sag * 2} ${(i + 1) * w} 4`;
    el("path", { class: "rope", d }, svg);
    // point on swag i at t (quadratic bezier)
    const at = (i, t) => {
      const x0 = i * w, x1 = x0 + w / 2, x2 = x0 + w;
      const y0 = 4, y1 = 4 + sag * 2, y2 = 4;
      const u = 1 - t;
      return [u * u * x0 + 2 * u * t * x1 + t * t * x2, u * u * y0 + 2 * u * t * y1 + t * t * y2];
    };
    let n = 0;
    for (let i = 0; i < swags; i++) {
      for (let t = 0.04; t < 1; t += 0.085) {
        const [x, y] = at(i, t);
        const rot = (n * 47) % 180;
        el("ellipse", { class: n % 2 ? "leaf alt" : "leaf", cx: x.toFixed(1), cy: y.toFixed(1), rx: 7, ry: 3.2,
          transform: `rotate(${rot} ${x.toFixed(1)} ${y.toFixed(1)})` }, svg);
        n++;
      }
    }
    let b = 0;
    for (let i = 0; i < swags; i++) {
      [0.28, 0.5, 0.72].forEach((t) => {
        const [x, y] = at(i, t);
        const g = el("g", {}, svg);
        el("rect", { class: "cap", x: (x - 1.8).toFixed(1), y: (y + 1).toFixed(1), width: 3.6, height: 3 }, g);
        const bulb = el("ellipse", { class: "bulb", cx: x.toFixed(1), cy: (y + 8).toFixed(1), rx: 3.2, ry: 4.6 }, g);
        bulb.style.setProperty("--c", GARLAND_COLOURS[b % GARLAND_COLOURS.length]);
        bulb.style.setProperty("--d", ((b * 0.53) % 2.4).toFixed(2) + "s");
        bulb.dataset.order = String((b * 37) % 1009); // scattered, stable order
        b++;
      });
    }
    lightBulbs(garlandBulbsInOrder(), currentSpirit, false, 0);
  }

  // ---- Snow -------------------------------------------------------------------
  // 0%: slow grey ash. 90%+: bright snow with the odd coloured sparkle.
  function startSnow() {
    if (!SNOW_ON || REDUCED_MOTION) return;
    const c = document.createElement("canvas");
    c.className = "spirit-snow";
    document.body.prepend(c);
    const g = c.getContext("2d");
    let flakes = [];
    let shownSpirit = currentSpirit;
    const resize = () => {
      c.width = innerWidth * devicePixelRatio;
      c.height = innerHeight * devicePixelRatio;
      g.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    };
    resize();
    addEventListener("resize", resize);
    const make = (top) => ({
      x: Math.random() * innerWidth,
      y: top ? -10 : Math.random() * innerHeight,
      r: 1 + Math.random() * 2.8,
      vy: 0.3 + Math.random() * 0.9,
      sway: Math.random() * Math.PI * 2,
      sparkle: Math.random() < 0.06,
      hue: (Math.random() * 360) | 0,
    });
    let last = performance.now();
    function frame(now) {
      const dt = Math.min(3, (now - last) / 16.7);
      last = now;
      shownSpirit += (currentSpirit - shownSpirit) * 0.02 * dt; // ease between stages
      const target = Math.round((innerWidth / 1440) * (55 + 110 * shownSpirit));
      while (flakes.length < target) flakes.push(make(flakes.length > 0));
      if (flakes.length > target) flakes.length = target;
      g.clearRect(0, 0, innerWidth, innerHeight);
      if (document.documentElement.dataset.prefSnow === "off") { requestAnimationFrame(frame); return; }
      const speed = 0.55 + 0.7 * shownSpirit;
      const grey = Math.round(110 + 145 * shownSpirit);
      for (const f of flakes) {
        f.sway += 0.01 * dt;
        f.y += f.vy * speed * dt;
        f.x += Math.sin(f.sway) * 0.35 * dt;
        if (f.y > innerHeight + 10) Object.assign(f, make(true));
        if (f.sparkle && shownSpirit > 0.5) {
          g.fillStyle = `hsla(${f.hue}, 90%, 70%, ${0.5 + 0.4 * Math.sin(now / 300 + f.sway)})`;
        } else {
          g.fillStyle = `rgba(${grey}, ${grey}, ${Math.min(255, grey + 6)}, ${0.35 + 0.45 * shownSpirit})`;
        }
        g.beginPath();
        g.arc(f.x, f.y, f.r, 0, Math.PI * 2);
        g.fill();
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  // ---- Images (navbar, meter, coal, wrapping papers) -------------------------
  // Each UI image is looked up on its own (webp, png, jpg, then the svg
  // placeholder), so you can replace them one at a time. Results are cached
  // for the browser session to avoid repeated lookups.
  async function findAsset(name) {
    const pref = SETTINGS.spirit_ui_ext || "";
    const key = "evilsanta-asset2:" + pref + ":" + name;
    try { const hit = sessionStorage.getItem(key); if (hit) return hit; } catch (e) { /* ignore */ }
    const order = [pref, "webp", "png", "jpg", "svg"].filter((x, i, a) => x && a.indexOf(x) === i);
    let found = "none";
    for (const ext of order) {
      if (await probe(UI_BASE + name + "." + ext)) { found = ext; break; }
    }
    try { sessionStorage.setItem(key, found); } catch (e) { /* ignore */ }
    return found;
  }

  async function applyImageSettings() {
    const root = document.documentElement.style;
    const names = ["navbar", "meter", "coal"];
    for (let i = 0; i < WRAP_COUNT; i++) names.push(`wrap-${i}`);
    const exts = await Promise.all(names.map(findAsset));
    // Optional lump-0..4 images (coal, charcoal, twigs...) on transparent backgrounds
    const lumpNames = [0, 1, 2, 3, 4].map((i) => `lump-${i}`);
    const lumpExts = await Promise.all(lumpNames.map(findAsset));
    const lumps = lumpNames.filter((_, i) => lumpExts[i] !== "none").map((n) => `${UI_BASE}${n}.${lumpExts[lumpNames.indexOf(n)]}`);
    if (lumps.length) {
      document.documentElement.dataset.lumps = "on";
      // Fewer than five? Reuse the ones that exist.
      lumpNames.forEach((n, i) => root.setProperty(`--img-${n}`, `url("${lumps[i % lumps.length]}")`));
    }
    names.forEach((name, i) => {
      const ext = exts[i];
      if (ext === "none") return;
      root.setProperty(`--img-${name}`, `url("${UI_BASE}${name}.${ext}")`);
      // Your own art is stretched over the whole card; the svg placeholders tile.
      if (ext !== "svg" && (name === "coal" || name.startsWith("wrap-"))) {
        root.setProperty(`--fit-${name}`, "cover");
      }
    });
  }

  // ---- Player preferences (Settings > Christmas effects) -----------------------
  const PREF_KEY = "evilsanta-prefs";
  const PREF_DEFAULTS = { snow: true, columns: true, garland: true, motion: true, dim: false,
    blur: 0, panel: 0, outline: false, adminStage: "100" };
  function loadPrefs() {
    try { return Object.assign({}, PREF_DEFAULTS, JSON.parse(localStorage.getItem(PREF_KEY) || "{}")); }
    catch (e) { return Object.assign({}, PREF_DEFAULTS); }
  }
  function applyPrefs(p) {
    const d = document.documentElement.dataset;
    p.snow ? delete d.prefSnow : (d.prefSnow = "off");
    p.columns ? delete d.prefColumns : (d.prefColumns = "simple");
    p.garland ? delete d.prefGarland : (d.prefGarland = "off");
    p.motion ? delete d.prefMotion : (d.prefMotion = "off");
    p.dim ? (d.prefDim = "on") : delete d.prefDim;
    p.outline ? (d.prefOutline = "on") : delete d.prefOutline;
    const st = document.documentElement.style;
    p.blur > 0 ? st.setProperty("--pref-blur", p.blur + "px") : st.removeProperty("--pref-blur");
    if (p.panel > 0) { d.prefPanel = "on"; st.setProperty("--pref-panel", p.panel); }
    else { delete d.prefPanel; st.removeProperty("--pref-panel"); }
  }
  function prefLabel(el) {
    const out = document.querySelector(`.spirit-pref-val[data-for="${el.id}"]`);
    if (!out) return;
    out.textContent = el.dataset.pref === "blur" ? (el.value > 0 ? el.value + " px" : "off") : (el.value > 0 ? el.value + "%" : "off");
  }
  function bindPrefsForm() {
    const form = document.getElementById("spirit-prefs");
    if (!form) return;
    const saved = document.getElementById("pref-saved");
    const sync = (p) => form.querySelectorAll("[data-pref]").forEach((el) => {
      if (el.type === "checkbox") el.checked = !!p[el.dataset.pref];
      else { el.value = String(p[el.dataset.pref]); prefLabel(el); }
    });
    const save = (p) => {
      try { localStorage.setItem(PREF_KEY, JSON.stringify(p)); } catch (e) { /* ignore */ }
      applyPrefs(p);
      if (saved) { saved.hidden = false; clearTimeout(saved._t); saved._t = setTimeout(() => { saved.hidden = true; }, 1500); }
    };
    sync(loadPrefs());
    const onChange = (e) => {
      const el = e.target.closest("[data-pref]");
      if (!el) return;
      const p = loadPrefs();
      if (el.type === "checkbox") p[el.dataset.pref] = el.checked;
      else if (el.type === "range") { p[el.dataset.pref] = Number(el.value); prefLabel(el); }
      else p[el.dataset.pref] = el.value;
      save(p);
      if (el.dataset.pref === "adminStage") applyAdminView();
    };
    form.addEventListener("input", onChange);
    form.addEventListener("change", onChange);
    document.getElementById("pref-reset").addEventListener("click", () => {
      const p = Object.assign({}, PREF_DEFAULTS);
      sync(p);
      save(p);
      applyAdminView();
    });
  }

  // Admins don't play, so they can view the site at any stage (default: 100%).
  function adminStageIndex() {
    if (!window.spiritIsAdmin) return null;
    const v = loadPrefs().adminStage;
    if (v === "progress") return null;
    return stageIndexFor(parseInt(v, 10) || 0);
  }
  function applyAdminView() {
    const idx = adminStageIndex();
    if (idx === null || !$("#spirit-meter")) return false;
    state = { best: idx, shown: idx };
    progress = { solved: 0, total: 0, pct: STAGES[idx].at };
    applyStage(idx, { animate: false });
    renderMeter();
    const detail = $("#spirit-meter-detail");
    if (detail) detail.textContent = "Admin view";
    return true;
  }

  // ---- Coal -> present celebration ----------------------------------------------
  function celebrateNewSolves(newIds) {
    let tries = 0;
    const attempt = () => {
      const pending = newIds.filter((id) => {
        const btn = document.querySelector(`.challenge-button[value="${id}"]`);
        if (!btn || !btn.classList.contains("challenge-solved")) return true;
        btn.classList.remove("just-wrapped");
        void btn.offsetWidth;
        btn.classList.add("just-wrapped");
        if (!REDUCED_MOTION) burst(btn.getBoundingClientRect(), 70);
        return false;
      });
      if (pending.length && ++tries < 10) { newIds = pending; setTimeout(attempt, 300); }
    };
    attempt();
  }

  // ---- Rendering -------------------------------------------------------------
  let currentSpirit = 0;
  let knownSolved = null;
  let state = loadState();
  let progress = { solved: 0, total: 0, pct: 0 };
  let busy = false;

  function applyStage(idx, opts) {
    const stage = STAGES[idx];
    const root = document.documentElement;
    // --spirit runs 0 → 1, reaching 1 at "Christmas Is Saved!" (90%)
    const spirit = Math.min(1, stage.at / 90);
    root.style.setProperty("--spirit", spirit.toFixed(3));
    root.dataset.spiritStage = String(stage.at);

    currentSpirit = spirit;
    const animate = !!(opts && opts.animate) && !REDUCED_MOTION;
    lightBulbs($$(".spirit-wreath .bulb"), spirit, animate, 90);
    lightBulbs(garlandBulbsInOrder(), spirit, animate, 35);
    const multiverse = stage.at >= 100;
    $$(".spirit-wreath, .spirit-garland").forEach((w) => w.classList.toggle("multiverse", multiverse));

    // Story panel + scene (challenge page only)
    const chapter = $("#spirit-chapter");
    if (chapter) {
      chapter.textContent = stage.chapter;
      $("#spirit-title").textContent = stage.title;
      $("#spirit-text").textContent = stage.text;
    }
    const scene = $("#spirit-scene");
    if (scene) setScene(scene, idx, opts && opts.animate);
  }

  function ensureSceneLayer(layer) {
    if (layer.querySelector(".spirit-scene-frame")) return;
    const fill = document.createElement("div");
    fill.className = "spirit-scene-fill";
    const frame = document.createElement("div");
    frame.className = "spirit-scene-frame";
    layer.append(fill, frame);
  }

  function measureNavbar() {
    const nav = document.querySelector(".navbar.fixed-top");
    if (nav) document.documentElement.style.setProperty("--nav-h", nav.offsetHeight + "px");
  }

  function setScene(scene, idx, animate) {
    const url = sceneUrl(idx);
    const layers = scene.querySelectorAll(".spirit-scene-layer");
    const current = scene.querySelector(".spirit-scene-layer.active");
    if (current && current.dataset.src === url) return;
    const next = current === layers[0] ? layers[1] : layers[0];
    ensureSceneLayer(next);
    next.style.setProperty("--scene", `url("${url}")`);
    document.documentElement.style.setProperty("--scene-current", `url("${url}")`);
    next.dataset.src = url;
    if (!animate) next.style.transition = "none";
    next.classList.add("active");
    if (current) current.classList.remove("active");
    if (!animate) { void next.offsetWidth; next.style.transition = ""; }
    preload(idx + 1);
  }

  function renderMeter() {
    const fill = $("#spirit-meter-fill");
    if (!fill) return;
    fill.style.width = progress.pct + "%";
    $("#spirit-meter-pct").textContent = progress.pct + "%";
    $("#spirit-meter").setAttribute("aria-valuenow", String(progress.pct));
    const detail = $("#spirit-meter-detail");
    if (detail) detail.textContent = progress.total ? `${progress.solved} / ${progress.total} flags` : "";

    $$(".spirit-tick").forEach((t) => {
      t.classList.toggle("reached", progress.pct >= parseInt(t.dataset.at, 10));
    });

    const waiting = state.best - state.shown;
    const btn = $("#spirit-ignite");
    btn.hidden = waiting <= 0;
    $("#spirit-ignite-count").textContent = waiting > 1 ? `×${waiting}` : "";
  }

  // ---- Ceremony ------------------------------------------------------------
  async function ignite() {
    if (busy || state.shown >= state.best) return;
    busy = true;
    const btn = $("#spirit-ignite");
    btn.disabled = true;
    const from = btn.getBoundingClientRect();
    const wreath = $(".spirit-wreath");
    const to = wreath ? wreath.getBoundingClientRect() : { left: innerWidth / 2, top: 0, width: 0, height: 0 };

    const nextIdx = state.shown + 1;
    if (!REDUCED_MOTION) {
      await sparkTrail(from, to);
      flash();
    }
    state.shown = nextIdx;
    saveState(state);
    applyStage(nextIdx, { animate: true });
    if (!REDUCED_MOTION) burst(to);
    announce(STAGES[nextIdx]);
    renderMeter();
    btn.disabled = false;
    busy = false;
  }

  function announce(stage) {
    const el = $("#spirit-toast");
    if (!el) return;
    el.innerHTML = "";
    const small = document.createElement("small");
    small.textContent = stage.chapter + " unlocked";
    const strong = document.createElement("strong");
    strong.textContent = stage.title;
    el.append(small, strong);
    el.classList.remove("show");
    void el.offsetWidth;
    el.classList.add("show");
  }

  function flash() {
    const f = document.createElement("div");
    f.className = "spirit-flash";
    document.body.appendChild(f);
    setTimeout(() => f.remove(), 900);
  }

  // Particle canvas shared by trail + burst
  let canvas, ctx, particles = [], raf = null;
  function ensureCanvas() {
    if (canvas) return;
    canvas = document.createElement("canvas");
    canvas.className = "spirit-canvas";
    document.body.appendChild(canvas);
    ctx = canvas.getContext("2d");
    const resize = () => {
      canvas.width = innerWidth * devicePixelRatio;
      canvas.height = innerHeight * devicePixelRatio;
      ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    };
    resize();
    addEventListener("resize", resize);
  }

  const SPARK_COLOURS = ["#ff3b3b", "#ffd447", "#3ddc6b", "#ffffff", "#4cc3ff", "#ff8ad8"];

  function loop() {
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    particles = particles.filter((p) => p.life > 0);
    particles.forEach((p) => {
      p.x += p.vx; p.y += p.vy; p.vy += p.g; p.vx *= 0.985; p.life -= 1;
      ctx.globalAlpha = Math.max(0, p.life / p.max);
      ctx.fillStyle = p.c;
      if (p.star) drawStar(p.x, p.y, p.r);
      else { ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill(); }
    });
    ctx.globalAlpha = 1;
    raf = particles.length ? requestAnimationFrame(loop) : null;
  }
  function kick() { if (!raf) raf = requestAnimationFrame(loop); }

  function drawStar(x, y, r) {
    ctx.beginPath();
    for (let i = 0; i < 10; i++) {
      const a = (Math.PI / 5) * i - Math.PI / 2;
      const rr = i % 2 ? r * 0.45 : r;
      ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr);
    }
    ctx.closePath(); ctx.fill();
  }

  function sparkTrail(from, to) {
    ensureCanvas();
    return new Promise((resolve) => {
      const sx = from.left + from.width / 2, sy = from.top + from.height / 2;
      const tx = to.left + to.width / 2, ty = to.top + to.height / 2;
      const dur = 900, t0 = performance.now();
      function step(now) {
        const t = Math.min(1, (now - t0) / dur);
        const e = 1 - Math.pow(1 - t, 3);
        // arc upward on the way to the wreath
        const x = sx + (tx - sx) * e;
        const y = sy + (ty - sy) * e - Math.sin(Math.PI * e) * 120;
        for (let i = 0; i < 4; i++) {
          particles.push({
            x, y, vx: (Math.random() - 0.5) * 2, vy: (Math.random() - 0.5) * 2, g: 0.04,
            r: 1.5 + Math.random() * 2.5, life: 40, max: 40,
            c: SPARK_COLOURS[(Math.random() * SPARK_COLOURS.length) | 0], star: Math.random() < 0.2,
          });
        }
        kick();
        if (t < 1) requestAnimationFrame(step); else resolve();
      }
      requestAnimationFrame(step);
    });
  }

  function burst(rect, count) {
    ensureCanvas();
    const cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2;
    for (let i = 0; i < (count || 140); i++) {
      const a = Math.random() * Math.PI * 2, s = 2 + Math.random() * 6;
      particles.push({
        x: cx, y: cy, vx: Math.cos(a) * s, vy: Math.sin(a) * s - 1, g: 0.09,
        r: 2 + Math.random() * 3, life: 70 + Math.random() * 40, max: 110,
        c: SPARK_COLOURS[(Math.random() * SPARK_COLOURS.length) | 0], star: Math.random() < 0.35,
      });
    }
    kick();
  }

  // ---- Refresh loop ----------------------------------------------------------
  async function refresh() {
    let p = null;
    try { p = await fetchProgress(); } catch (e) { p = null; }
    if (!p) return;
    progress = p;
    if (knownSolved) {
      const fresh = p.ids.filter((id) => !knownSolved.has(id));
      if (fresh.length) celebrateNewSolves(fresh);
    }
    knownSolved = new Set(p.ids);
    const earned = stageIndexFor(p.pct);
    // Never go backwards (e.g. when a new wave of challenges is released)
    if (earned > state.best) { state.best = earned; saveState(state); }
    renderMeter();
  }

  function probe(url) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      img.src = url;
    });
  }

  async function detectSceneExt() {
    const order = [SCENE_EXT, "webp", "png", "jpg", "svg"].filter((x, i, a) => x && a.indexOf(x) === i);
    SCENE_EXT = null;
    for (const ext of order) {
      if (await probe(SCENE_BASE + "stage-000." + ext)) { SCENE_EXT = ext; return; }
    }
    SCENE_EXT = "svg";
  }

  async function init() {
    // Logged-out visitors have no meter: they see everything as a team at 0%.
    const authed = !!$("#spirit-meter");
    if (!authed) state = { best: 0, shown: 0 };
    await detectSceneExt();
    if (state.shown > STAGES.length - 1) state.shown = STAGES.length - 1;
    document.documentElement.dataset.sceneFit = SETTINGS.spirit_scene_fit === "cover" ? "cover" : "columns";
    if (SETTINGS.spirit_scene_fit === "cover") document.documentElement.style.setProperty("--col-w", "0px");
    measureNavbar();
    applyImageSettings();
    buildGarland();
    applyStage(state.shown, { animate: false });
    // Only animate colour changes after the first paint
    setTimeout(() => document.documentElement.classList.add("spirit-animate"), 60);
    startSnow();
    bindPrefsForm();
    let resizeTimer = null;
    addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => { buildGarland(); measureNavbar(); }, 150); });
    if (!authed) return;
    $("#spirit-ignite").addEventListener("click", ignite);
    if (applyAdminView()) return;
    refresh();
    // CTFd fires this after a correct flag submission on the challenge board
    window.addEventListener("load-challenges", () => setTimeout(refresh, 400));
    setInterval(() => { if (!document.hidden) refresh(); }, POLL_MS);
    document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(); });
  }

  // Small debug hook for testing in the browser console:
  //   EvilSanta.preview(5)  -> show stage index 5 without saving
  //   EvilSanta.reset()     -> forget local progress for this account
  window.EvilSanta = {
    stages: STAGES,
    preview: (i) => applyStage(Math.max(0, Math.min(STAGES.length - 1, i)), { animate: true }),
    reset: () => { state = { best: 0, shown: 0 }; saveState(state); location.reload(); },
    refresh,
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

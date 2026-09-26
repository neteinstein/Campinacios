// Interactive link graph for docs/Grafo.md. Self-contained: a small force
// layout drawn on a canvas, fed by assets/graph.json (written by
// scripts/mediawiki_to_markdown.py).
(function () {
  "use strict";

  var PALETTE = ["#3f51b5", "#e91e63", "#009688", "#ff9800", "#9c27b0",
                 "#795548", "#607d8b", "#4caf50"];

  function init(el) {
    if (el.dataset.ready) return;
    el.dataset.ready = "1";
    var dataUrl = new URL(el.dataset.src, window.location.href);
    var siteRoot = new URL("../", dataUrl);
    fetch(dataUrl)
      .then(function (r) { return r.json(); })
      .then(function (data) { render(el, data, siteRoot); })
      .catch(function (e) {
        el.textContent = "Não foi possível carregar o grafo (" + e + ").";
      });
  }

  function render(el, data, siteRoot) {
    var canvas = document.createElement("canvas");
    el.appendChild(canvas);
    var ctx = canvas.getContext("2d");

    var nodes = data.nodes.map(function (n, i) {
      var a = i * 2.399963, r = 12 * Math.sqrt(i + 1);  // sunflower start
      return { id: n.id, title: n.title, group: n.group, x: r * Math.cos(a),
               y: r * Math.sin(a), vx: 0, vy: 0, deg: 0, nb: [] };
    });
    var links = data.links.map(function (l) {
      var s = nodes[l[0]], t = nodes[l[1]];
      s.deg++; t.deg++; s.nb.push(t); t.nb.push(s);
      return { s: s, t: t };
    });
    nodes.forEach(function (n) { n.r = 2.5 + Math.sqrt(n.deg) * 1.2; });

    var groups = [];
    nodes.forEach(function (n) {
      if (groups.indexOf(n.group) < 0) groups.push(n.group);
    });
    groups.sort();
    var color = {}, hidden = {};
    groups.forEach(function (g, i) { color[g] = PALETTE[i % PALETTE.length]; });

    // ---- controls ---------------------------------------------------------
    var controls = document.createElement("div");
    controls.className = "wiki-graph-controls";
    var search = document.createElement("input");
    search.type = "search";
    search.placeholder = "Procurar…";
    controls.appendChild(search);
    groups.forEach(function (g) {
      var item = document.createElement("span");
      item.className = "legend-item";
      item.innerHTML = '<span class="legend-dot"></span>';
      item.firstChild.style.background = color[g];
      item.appendChild(document.createTextNode(g));
      item.title = "Mostrar/esconder";
      item.addEventListener("click", function () {
        hidden[g] = !hidden[g];
        item.classList.toggle("off", !!hidden[g]);
        draw();
      });
      controls.appendChild(item);
    });
    el.appendChild(controls);

    // ---- view -------------------------------------------------------------
    var view = { k: 1, x: 0, y: 0 }, width = 0, height = 0, dpr = 1;
    function resize() {
      dpr = window.devicePixelRatio || 1;
      width = el.clientWidth;
      height = el.clientHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      draw();
    }
    function toWorld(px, py) {
      return { x: (px - width / 2 - view.x) / view.k,
               y: (py - height / 2 - view.y) / view.k };
    }
    function visible(n) { return !hidden[n.group]; }

    // ---- simulation -------------------------------------------------------
    var alpha = 1;
    function tick() {
      var i, j, a, b, dx, dy, d2, f;
      for (i = 0; i < nodes.length; i++) {
        a = nodes[i];
        for (j = i + 1; j < nodes.length; j++) {
          b = nodes[j];
          dx = a.x - b.x; dy = a.y - b.y;
          d2 = dx * dx + dy * dy + 0.01;
          if (d2 > 90000) continue;
          f = 60 * alpha / d2;
          a.vx += dx * f; a.vy += dy * f;
          b.vx -= dx * f; b.vy -= dy * f;
        }
        a.vx -= a.x * 0.004 * alpha;
        a.vy -= a.y * 0.004 * alpha;
      }
      // Springs are weakened on the busier end, as in d3-force: hubs such as
      // "Director" have hundreds of links and would otherwise overshoot.
      links.forEach(function (l) {
        dx = l.t.x - l.s.x; dy = l.t.y - l.s.y;
        var d = Math.sqrt(dx * dx + dy * dy) || 1;
        f = (d - 40) / d * 0.3 * alpha / Math.min(l.s.deg, l.t.deg);
        var bs = l.t.deg / (l.s.deg + l.t.deg);
        l.s.vx += dx * f * bs; l.s.vy += dy * f * bs;
        l.t.vx -= dx * f * (1 - bs); l.t.vy -= dy * f * (1 - bs);
      });
      nodes.forEach(function (n) {
        if (n === dragged) { n.vx = n.vy = 0; return; }
        var v = Math.sqrt(n.vx * n.vx + n.vy * n.vy);
        if (v > 20) { n.vx *= 20 / v; n.vy *= 20 / v; }
        n.x += n.vx; n.y += n.vy;
        n.vx *= 0.6; n.vy *= 0.6;
      });
      alpha *= 0.985;
    }

    // ---- drawing ----------------------------------------------------------
    var hover = null, matches = [];
    function draw() {
      var style = getComputedStyle(el);
      var fg = style.getPropertyValue("--md-default-fg-color").trim() || "#000";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      ctx.translate(width / 2 + view.x, height / 2 + view.y);
      ctx.scale(view.k, view.k);

      var focus = hover ? [hover].concat(hover.nb) : null;
      ctx.lineWidth = 0.6 / view.k;
      links.forEach(function (l) {
        if (!visible(l.s) || !visible(l.t)) return;
        var on = hover && (l.s === hover || l.t === hover);
        ctx.strokeStyle = on ? color[hover.group] : fg;
        ctx.globalAlpha = on ? 0.9 : (hover ? 0.03 : 0.08);
        ctx.beginPath();
        ctx.moveTo(l.s.x, l.s.y);
        ctx.lineTo(l.t.x, l.t.y);
        ctx.stroke();
      });
      nodes.forEach(function (n) {
        if (!visible(n)) return;
        var dim = (focus && focus.indexOf(n) < 0) ||
                  (matches.length && matches.indexOf(n) < 0);
        ctx.globalAlpha = dim ? 0.15 : 1;
        ctx.fillStyle = color[n.group];
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, 2 * Math.PI);
        ctx.fill();
      });
      ctx.globalAlpha = 1;
      ctx.fillStyle = fg;
      ctx.font = 12 / view.k + "px sans-serif";
      nodes.forEach(function (n) {
        if (!visible(n)) return;
        var show = (focus ? focus.indexOf(n) >= 0 : n.r * view.k > 9) ||
                   matches.indexOf(n) >= 0;
        if (show) ctx.fillText(n.title, n.x + n.r + 2 / view.k, n.y + 4 / view.k);
      });
    }

    function loop() {
      if (alpha > 0.02) {
        tick(); tick();
        draw();
      }
      requestAnimationFrame(loop);
    }

    // ---- interaction ------------------------------------------------------
    function nodeAt(px, py) {
      var p = toWorld(px, py), best = null, bestD = Infinity;
      nodes.forEach(function (n) {
        if (!visible(n)) return;
        var d = Math.hypot(n.x - p.x, n.y - p.y);
        if (d < Math.max(n.r, 6 / view.k) && d < bestD) { best = n; bestD = d; }
      });
      return best;
    }
    function pos(e) {
      var r = canvas.getBoundingClientRect();
      return { x: e.clientX - r.left, y: e.clientY - r.top };
    }

    var dragged = null, panning = null, moved = false;
    canvas.addEventListener("pointerdown", function (e) {
      var p = pos(e);
      moved = false;
      dragged = nodeAt(p.x, p.y);
      if (!dragged) panning = { x: p.x - view.x, y: p.y - view.y };
      canvas.classList.add("dragging");
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener("pointermove", function (e) {
      var p = pos(e);
      if (dragged) {
        var w = toWorld(p.x, p.y);
        dragged.x = w.x; dragged.y = w.y;
        moved = true;
        alpha = Math.max(alpha, 0.1);
        draw();
      } else if (panning) {
        view.x = p.x - panning.x; view.y = p.y - panning.y;
        moved = true;
        draw();
      } else {
        var n = nodeAt(p.x, p.y);
        if (n !== hover) {
          hover = n;
          canvas.title = n ? n.title : "";
          canvas.style.cursor = n ? "pointer" : "";
          draw();
        }
      }
    });
    canvas.addEventListener("pointerup", function (e) {
      var p = pos(e);
      var n = !moved && nodeAt(p.x, p.y);
      dragged = panning = null;
      canvas.classList.remove("dragging");
      if (n) window.location.href = new URL(n.id, siteRoot).href;
    });
    canvas.addEventListener("wheel", function (e) {
      e.preventDefault();
      var p = pos(e), before = toWorld(p.x, p.y);
      view.k = Math.min(8, Math.max(0.1, view.k * Math.exp(-e.deltaY * 0.0015)));
      view.x = p.x - width / 2 - before.x * view.k;
      view.y = p.y - height / 2 - before.y * view.k;
      draw();
    }, { passive: false });

    function normalize(s) {
      return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
    }
    search.addEventListener("input", function () {
      var q = normalize(search.value.trim());
      matches = q ? nodes.filter(function (n) {
        return normalize(n.title).indexOf(q) >= 0;
      }) : [];
      draw();
    });
    search.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" || !matches.length) return;
      var n = matches[0];
      view.k = 2;
      view.x = -n.x * view.k;
      view.y = -n.y * view.k;
      draw();
    });

    window.addEventListener("resize", resize);
    for (var i = 0; i < 120; i++) tick();  // settle before the first frame
    view.k = 0.45;
    resize();
    loop();
  }

  function start() {
    document.querySelectorAll(".wiki-graph").forEach(init);
  }
  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(start);  // Material's instant navigation
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();

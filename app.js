/* ==========================================================
   APEX PORTFOLIO — app.js
   Narendranath Edara | narendranathe.github.io
   Combines: D3 force graph, canvas particles, scroll reveals,
   nav glassmorphism, arch toggles, reading progress, mobile menu
   ========================================================== */

(function () {
  "use strict";

  /* -------- READING PROGRESS -------- */
  var progressBar = document.getElementById("progress");
  function updateProgress() {
    var scrollTop = window.scrollY;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    if (progressBar) progressBar.style.height = pct + "%";
  }

  /* -------- NAV GLASSMORPHISM -------- */
  var navWrap = document.getElementById("nav");
  function updateNav() {
    if (!navWrap) return;
    if (window.scrollY > 40) {
      navWrap.classList.add("scrolled");
    } else {
      navWrap.classList.remove("scrolled");
    }
  }

  window.addEventListener("scroll", function () {
    updateProgress();
    updateNav();
  }, { passive: true });

  updateNav();

  /* -------- MOBILE MENU -------- */
  var burger = document.getElementById("burger");
  var drawer = document.getElementById("drawer");
  if (burger && drawer) {
    burger.addEventListener("click", function () {
      var open = drawer.classList.toggle("open");
      burger.setAttribute("aria-expanded", String(open));
      drawer.setAttribute("aria-hidden", String(!open));
    });
    drawer.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        drawer.classList.remove("open");
        burger.setAttribute("aria-expanded", "false");
        drawer.setAttribute("aria-hidden", "true");
      });
    });
  }

  /* -------- YEAR -------- */
  var yr = document.getElementById("yr");
  if (yr) yr.textContent = new Date().getFullYear();

  /* -------- SCROLL REVEAL -------- */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var revealObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          revealObs.unobserve(e.target);
        }
      });
    }, { threshold: 0.08 });
    revealEls.forEach(function (el) { revealObs.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  /* -------- ARCHITECTURE TRACE TOGGLES -------- */
  document.querySelectorAll(".arch-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = document.getElementById(btn.dataset.target);
      if (!target) return;
      var isHidden = target.hidden;
      target.hidden = !isHidden;
      btn.textContent = isHidden
        ? btn.textContent.replace("[ + ]", "[ - ]")
        : btn.textContent.replace("[ - ]", "[ + ]");
      btn.setAttribute("aria-expanded", String(isHidden));
    });
  });

  /* -------- CANVAS PARTICLE FIELD -------- */
  (function initParticles() {
    var canvas = document.getElementById("particles");
    if (!canvas) return;
    var ctx = canvas.getContext("2d");

    var W, H, particles;
    var GREEN = "rgba(0,255,135,";
    var mouse = { x: -9999, y: -9999 };

    function resize() {
      W = canvas.width  = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
    }

    function makeParticle() {
      return {
        x:  Math.random() * W,
        y:  Math.random() * H,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r:  Math.random() * 1.5 + 0.5,
        alpha: Math.random() * 0.5 + 0.1
      };
    }

    function init() {
      resize();
      var count = Math.floor((W * H) / 14000);
      particles = Array.from({ length: count }, makeParticle);
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);

      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];

        /* gentle mouse attraction */
        var dx = mouse.x - p.x;
        var dy = mouse.y - p.y;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 200) {
          p.vx += dx / dist * 0.008;
          p.vy += dy / dist * 0.008;
        }

        /* friction + update */
        p.vx *= 0.98;
        p.vy *= 0.98;
        p.x += p.vx;
        p.y += p.vy;

        /* wrap */
        if (p.x < 0) p.x = W;
        if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H;
        if (p.y > H) p.y = 0;

        /* draw dot */
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = GREEN + p.alpha + ")";
        ctx.fill();

        /* draw connections */
        for (var j = i + 1; j < particles.length; j++) {
          var q = particles[j];
          var ex = p.x - q.x;
          var ey = p.y - q.y;
          var ed = Math.sqrt(ex * ex + ey * ey);
          if (ed < 120) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = GREEN + (0.12 * (1 - ed / 120)) + ")";
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }

      requestAnimationFrame(draw);
    }

    canvas.addEventListener("mousemove", function (e) {
      var rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });
    canvas.addEventListener("mouseleave", function () {
      mouse.x = -9999;
      mouse.y = -9999;
    });

    window.addEventListener("resize", function () {
      init();
    }, { passive: true });

    init();
    draw();
  })();

  /* -------- D3 KNOWLEDGE GRAPH -------- */
  (function initGraph() {
    if (typeof d3 === "undefined") return;

    var NODES = [
      { id: "autoapply",  label: "AutoApply AI",          kind: "system",  section: "autoapply",
        detail: "Agentic discover → tailor → apply → track pipeline. Chrome MV3 extension + FastAPI backend. Multi-provider LLM cascade: Claude → OpenAI → Gemini → Groq → Kimi → Ollama → keyword fallback. 40+ endpoints, 11 ATS adapters, 9-page dashboard, 190 automated tests. Deployed on Fly.io with Supabase + Upstash Redis. 4 distribution surfaces." },
      { id: "tailor",     label: "tailor-resume",         kind: "system",  section: "tailor-resume",
        detail: "MCP server + CLI + PyPI package + Streamlit UI. pip install tailor-resume — production-grade tailoring in minutes. Any MCP-aware agent calls it directly with zero integration work. 355 backend tests, 40+ endpoints." },
      { id: "jobscout",   label: "JobScout",              kind: "system",  section: "jobscout",
        detail: "Discovery layer feeding AutoApply AI's discover phase. Monitors 130+ company career pages across 6 ATS platforms continuously. Normalized diff-based event stream." },
      { id: "mcp",        label: "MCP Server",            kind: "system",  section: "tailor-resume",
        detail: "Model Context Protocol server exposing tailor-resume to any MCP-aware agent runtime. 97M monthly SDK downloads ecosystem-wide. Adopted by OpenAI, Google, Microsoft in 2025." },

      { id: "fastapi",    label: "FastAPI",    kind: "tool" },
      { id: "chromemv3",  label: "Chrome MV3", kind: "tool" },
      { id: "pypi",       label: "PyPI",       kind: "tool" },
      { id: "streamlit",  label: "Streamlit",  kind: "tool" },
      { id: "postgres",   label: "PostgreSQL", kind: "tool" },
      { id: "redis",      label: "Redis",      kind: "tool" },
      { id: "flyio",      label: "Fly.io",     kind: "tool" },
      { id: "claude",     label: "Claude",     kind: "tool" },
      { id: "openai",     label: "OpenAI",     kind: "tool" },
      { id: "gemini",     label: "Gemini",     kind: "tool" },
      { id: "groq",       label: "Groq",       kind: "tool" },

      { id: "cascade",    label: "Multi-provider cascade", kind: "concept" },
      { id: "agentwf",    label: "Agent workflow",         kind: "concept" },
      { id: "mcpproto",   label: "MCP Protocol",           kind: "concept" },
      { id: "rag",        label: "RAG / retrieval",        kind: "concept" },

      { id: "m-tests",    label: "190 tests",       kind: "impact" },
      { id: "m-sources",  label: "130+ sources",    kind: "impact" },
      { id: "m-providers",label: "6 LLM providers", kind: "impact" },
      { id: "m-endpoints",label: "40+ endpoints",   kind: "impact" },
      { id: "m-ats",      label: "11 ATS adapters", kind: "impact" }
    ];

    var LINKS = [
      ["autoapply","fastapi"],["autoapply","chromemv3"],["autoapply","flyio"],["autoapply","postgres"],
      ["autoapply","redis"],["autoapply","agentwf"],["autoapply","cascade"],["autoapply","rag"],
      ["autoapply","claude"],["autoapply","openai"],["autoapply","gemini"],["autoapply","groq"],
      ["autoapply","tailor"],["autoapply","jobscout"],
      ["autoapply","m-tests"],["autoapply","m-providers"],["autoapply","m-endpoints"],["autoapply","m-ats"],

      ["tailor","mcp"],["tailor","pypi"],["tailor","streamlit"],["tailor","fastapi"],
      ["tailor","cascade"],["tailor","claude"],["tailor","m-endpoints"],

      ["mcp","mcpproto"],["mcp","agentwf"],

      ["jobscout","fastapi"],["jobscout","postgres"],["jobscout","m-sources"],["jobscout","m-ats"],

      ["cascade","claude"],["cascade","openai"],["cascade","gemini"],["cascade","groq"],
      ["agentwf","rag"],["agentwf","mcpproto"],["rag","postgres"]
    ].map(function (p) { return { source: p[0], target: p[1] }; });

    function colorFor(k) {
      if (k === "system")  return "#4ade80";
      if (k === "impact")  return "#f59e0b";
      if (k === "concept") return "#a78bfa";
      return "#60a5fa";
    }
    function radiusFor(k) {
      return k === "system" ? 14 : k === "impact" ? 8 : 7;
    }

    /* Adjacency for highlight */
    var adj = new Map();
    LINKS.forEach(function (l) {
      [l.source, l.target].forEach(function (id) {
        if (!adj.has(id)) adj.set(id, new Set());
      });
      adj.get(l.source).add(l.target);
      adj.get(l.target).add(l.source);
    });

    function buildGraph(container, opts) {
      opts = opts || {};
      var mini = !!opts.mini;
      var onClick = opts.onClick || function () {};

      var nodes = NODES.map(function (n) { return Object.assign({}, n); });
      var links = LINKS.map(function (l) { return Object.assign({}, l); });

      container.innerHTML = "";
      var svg = d3.select(container).append("svg")
        .attr("role", "img")
        .attr("aria-label", mini ? "Mini knowledge graph" : "Interactive knowledge graph");

      function size() {
        var r = container.getBoundingClientRect();
        return { w: Math.max(300, r.width), h: Math.max(180, r.height) };
      }
      var s = size(), W = s.w, H = s.h;
      svg.attr("viewBox", "0 0 " + W + " " + H);

      var root = svg.append("g");
      var zoom = d3.zoom().scaleExtent([0.35, 4]).on("zoom", function (e) {
        root.attr("transform", e.transform);
      });
      if (!mini) svg.call(zoom);

      var mobile = W < 600;
      var rScale = mini ? 0.45 : mobile ? 0.8 : 1;

      var sim = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(function (d) { return d.id; })
          .distance(mini ? 36 : mobile ? 65 : 90).strength(0.5))
        .force("charge", d3.forceManyBody().strength(mini ? -80 : mobile ? -170 : -300))
        .force("center", d3.forceCenter(W / 2, H / 2))
        .force("collide", d3.forceCollide().radius(function (d) {
          return radiusFor(d.kind) * rScale + 6;
        }));

      var linkSel = root.append("g")
        .selectAll("line").data(links).join("line")
        .attr("class", "edge-base lit");

      var nodeG = root.append("g")
        .selectAll("g").data(nodes).join("g")
        .attr("class", "lit")
        .style("cursor", "pointer");

      nodeG.append("circle")
        .attr("r", function (d) { return radiusFor(d.kind) * rScale; })
        .attr("fill", function (d) { return colorFor(d.kind); })
        .attr("stroke", "#050810")
        .attr("stroke-width", 1.5)
        .attr("class", function (d) { return d.kind === "system" ? "node-pulse" : ""; });

      if (!mini) {
        nodeG.append("text")
          .text(function (d) { return d.label; })
          .attr("x", function (d) { return radiusFor(d.kind) * rScale + 7; })
          .attr("y", 4)
          .attr("fill", "#f5f5f7")
          .attr("font-family", "JetBrains Mono, monospace")
          .attr("font-size", function (d) { return d.kind === "system" ? 11.5 : 10; })
          .attr("font-weight", function (d) { return d.kind === "system" ? 500 : 400; })
          .attr("opacity", 0.82)
          .attr("pointer-events", "none");
      }

      var drag = d3.drag()
        .on("start", function (e, d) {
          if (!e.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on("drag", function (e, d) { d.fx = e.x; d.fy = e.y; })
        .on("end",  function (e, d) {
          if (!e.active) sim.alphaTarget(0);
          d.fx = null; d.fy = null;
        });
      nodeG.call(drag);

      function highlight(id) {
        if (!id) {
          nodeG.classed("dim", false).classed("lit", true);
          linkSel.attr("class", "edge-base lit");
          return;
        }
        var neigh = adj.get(id) || new Set();
        nodeG
          .classed("dim", function (d) { return d.id !== id && !neigh.has(d.id); })
          .classed("lit", function (d) { return d.id === id || neigh.has(d.id); });
        linkSel.each(function (l) {
          var s = l.source.id || l.source;
          var t = l.target.id || l.target;
          var active = s === id || t === id;
          d3.select(this).attr("class", (active ? "edge-active" : "edge-base") + (active ? " lit" : " dim"));
        });
      }

      nodeG
        .on("mouseenter", function (_e, d) { highlight(d.id); })
        .on("mouseleave", function () { highlight(null); })
        .on("click", function (_e, d) {
          if (mini) {
            var el = document.getElementById(d.section || d.id);
            if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
          } else {
            onClick(d);
          }
        })
        .on("dblclick", function (_e, d) {
          if (mini || d.kind !== "system") return;
          var keep = new Set([d.id].concat(Array.from(adj.get(d.id) || [])));
          nodeG.style("display", function (n) { return keep.has(n.id) ? null : "none"; });
          linkSel.style("display", function (l) {
            var src = l.source.id || l.source;
            var tgt = l.target.id || l.target;
            return keep.has(src) && keep.has(tgt) ? null : "none";
          });
          svg.on("dblclick.reset", function (ev) {
            if (ev.target === svg.node()) {
              nodeG.style("display", null);
              linkSel.style("display", null);
              svg.on("dblclick.reset", null);
            }
          });
        });

      sim.on("tick", function () {
        linkSel
          .attr("x1", function (d) { return d.source.x; })
          .attr("y1", function (d) { return d.source.y; })
          .attr("x2", function (d) { return d.target.x; })
          .attr("y2", function (d) { return d.target.y; });
        nodeG.attr("transform", function (d) {
          return "translate(" + d.x + "," + d.y + ")";
        });
      });

      new ResizeObserver(function () {
        var s = size(); W = s.w; H = s.h;
        svg.attr("viewBox", "0 0 " + W + " " + H);
        sim.force("center", d3.forceCenter(W / 2, H / 2)).alpha(0.4).restart();
      }).observe(container);
    }

    /* --- Node detail panel --- */
    var panel = document.getElementById("node-panel");
    var scrim = document.getElementById("panel-scrim");
    var panelBody = document.getElementById("panel-body");

    function openPanel(node) {
      var kindLabel = { system: "Deployed system", impact: "Impact metric", concept: "Concept" }[node.kind] || "Tool / technology";
      var color = colorFor(node.kind);
      panelBody.innerHTML =
        '<span class="kind" style="color:' + color + '">' + kindLabel + '</span>' +
        '<h3>' + node.label + '</h3>' +
        '<p>' + (node.detail || "A node in the knowledge graph, connected to the systems above.") + '</p>' +
        (node.section
          ? '<a class="jump" href="#' + node.section + '" onclick="closePanel()">Jump to section &#8595;</a>'
          : "");
      panel.classList.add("open");
      panel.setAttribute("aria-hidden", "false");
      scrim.classList.add("open");
      scrim.setAttribute("aria-hidden", "false");
    }

    window.closePanel = function () {
      panel.classList.remove("open");
      panel.setAttribute("aria-hidden", "true");
      scrim.classList.remove("open");
      scrim.setAttribute("aria-hidden", "true");
    };

    document.getElementById("panel-close").addEventListener("click", window.closePanel);
    scrim.addEventListener("click", window.closePanel);

    /* --- Build main graph --- */
    var graphCanvas = document.getElementById("graph-canvas");
    if (graphCanvas) {
      buildGraph(graphCanvas, { onClick: openPanel });
    }

    /* --- Build minimap --- */
    var minigraph = document.getElementById("minigraph");
    if (minigraph) {
      buildGraph(minigraph, { mini: true });
    }

    /* --- Minimap show/hide based on graph visibility --- */
    var graphSection = document.getElementById("graph-section");
    var minimapEl = document.getElementById("minimap");
    if (graphSection && minimapEl && "IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        var visible = entries[0].isIntersecting;
        minimapEl.classList.toggle("show", !visible);
        minimapEl.setAttribute("aria-hidden", visible ? "true" : "false");
      }, { threshold: 0.05 }).observe(graphSection);
    }
  })();

})();

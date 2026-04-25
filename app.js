/* ============================================================
   NARENDRANATH EDARA — portfolio app.js
   D3 knowledge graph (silky orbs, scroll-trap fixed)
   + minimap + node detail panel + nav scroll effect
   ============================================================ */
(function () {
  'use strict';

  // ---- NODE DATA ----
  var NODES = [
    // Systems
    { id: 'exponenthr', label: 'ExponentHR Platform', kind: 'system', section: 'systems',
      detail: 'Catalog-driven NL-to-SQL analytics engine on Microsoft Fabric. FAISS classifies intent across 6K+ HR columns, Claude Sonnet generates RLS/CLS-governed T-SQL, NetworkX auto-resolves cross-domain joins. 400 enterprise clients · 12s→4s latency · −67% ETL compute cost · 3mo→14 day deployment cycles.' },
    { id: 'autoapply', label: 'AutoApply AI', kind: 'system', section: 'systems',
      detail: 'End-to-end workflow platform: discover → tailor → apply → track. Chrome MV3 + FastAPI + React dashboard with multi-provider LLM routing (Claude, OpenAI, Gemini, Groq, Kimi, Ollama), pgvector RAG, 11 ATS adapters, live on Fly.io. 40+ endpoints · 9-page dashboard · 190 tests.' },
    { id: 'tailor', label: 'tailor-resume', kind: 'system', section: 'systems',
      detail: 'Extracted tailoring engine from AutoApply AI. Ships as CLI, Streamlit app, typed MCP server, and PyPI package. 190 automated tests, hosted on Fly.io. Any MCP-aware agent calls it with zero integration work. 4 distribution surfaces from one shared engine.' },
    { id: 'jobscout', label: 'JobScout', kind: 'system', section: 'systems',
      detail: 'Discovery layer feeding AutoApply AI. Monitors 130+ company career pages across 6 ATS platforms. Sponsorship-aware ranking keeps discovery signal clean so the apply workflow doesn’t inherit noise.' },
    { id: 'mcp', label: 'MCP Server', kind: 'system', section: 'systems',
      detail: 'Model Context Protocol server exposing tailor-resume to any MCP-aware agent. 97M monthly MCP SDK downloads, 10K+ public servers, 1B+ tool calls/month — this is the agent interoperability standard. Naren was building for it before most teams knew it existed.' },

    // Tools
    { id: 'fastapi',   label: 'FastAPI',           kind: 'tool' },
    { id: 'chromemv3', label: 'Chrome MV3',         kind: 'tool' },
    { id: 'fabric',    label: 'Microsoft Fabric',   kind: 'tool' },
    { id: 'pypi',      label: 'PyPI',               kind: 'tool' },
    { id: 'streamlit', label: 'Streamlit',          kind: 'tool' },
    { id: 'postgres',  label: 'PostgreSQL',         kind: 'tool' },
    { id: 'redis',     label: 'Redis',              kind: 'tool' },
    { id: 'fly',       label: 'Fly.io',             kind: 'tool' },
    { id: 'claude',    label: 'Claude',             kind: 'tool' },
    { id: 'openai',    label: 'OpenAI',             kind: 'tool' },
    { id: 'gemini',    label: 'Gemini',             kind: 'tool' },

    // Concepts
    { id: 'faiss',    label: 'FAISS retrieval',          kind: 'concept' },
    { id: 'networkx', label: 'NetworkX semantic graph',  kind: 'concept' },
    { id: 'rag',      label: 'RAG / pgvector',           kind: 'concept' },
    { id: 'cascade',  label: 'Multi-provider cascade',   kind: 'concept' },
    { id: 'agentwf',  label: 'Agent workflow',           kind: 'concept' },
    { id: 'mcpproto', label: 'MCP Protocol',             kind: 'concept' },
    { id: 'nlsql',    label: 'NL-to-SQL',               kind: 'concept' },

    // Impact
    { id: 'm-clients',  label: '400 clients',       kind: 'impact' },
    { id: 'm-tests',    label: '190 tests',         kind: 'impact' },
    { id: 'm-sources',  label: '130+ sources',      kind: 'impact' },
    { id: 'm-latency',  label: '12s→4s latency', kind: 'impact' },
    { id: 'm-surfaces', label: '4 surfaces',        kind: 'impact' }
  ];

  var LINKS = [
    ['exponenthr','fastapi'],['exponenthr','fabric'],['exponenthr','faiss'],
    ['exponenthr','networkx'],['exponenthr','nlsql'],['exponenthr','claude'],
    ['exponenthr','m-clients'],['exponenthr','m-latency'],

    ['autoapply','fastapi'],['autoapply','chromemv3'],['autoapply','fly'],
    ['autoapply','postgres'],['autoapply','redis'],['autoapply','rag'],
    ['autoapply','cascade'],['autoapply','agentwf'],
    ['autoapply','tailor'],['autoapply','jobscout'],
    ['autoapply','claude'],['autoapply','openai'],['autoapply','gemini'],
    ['autoapply','m-tests'],

    ['tailor','mcp'],['tailor','pypi'],['tailor','streamlit'],['tailor','fastapi'],
    ['tailor','cascade'],['tailor','m-tests'],['tailor','m-surfaces'],

    ['mcp','mcpproto'],['mcp','agentwf'],

    ['jobscout','fastapi'],['jobscout','postgres'],['jobscout','m-sources'],

    ['cascade','claude'],['cascade','openai'],['cascade','gemini'],
    ['agentwf','rag'],['agentwf','mcpproto'],
    ['rag','postgres'],['faiss','fabric'],['networkx','nlsql']
  ].map(function (p) { return { source: p[0], target: p[1] }; });

  // ---- COLOUR / SIZE HELPERS ----
  function colorFor(kind) {
    if (kind === 'system')  return '#176b52';
    if (kind === 'impact')  return '#b5752a';
    if (kind === 'concept') return '#7a5a9e';
    return '#2e5d9e';
  }
  function haloFor(kind) {
    if (kind === 'system')  return 'rgba(23,107,82,0.16)';
    if (kind === 'impact')  return 'rgba(181,117,42,0.16)';
    if (kind === 'concept') return 'rgba(122,90,158,0.16)';
    return 'rgba(46,93,158,0.16)';
  }
  function radiusFor(kind) {
    if (kind === 'system') return 16;
    if (kind === 'impact') return 9;
    return 8;
  }

  // ---- GRAPH BUILDER ----
  function buildGraph(container, opts) {
    opts = opts || {};
    var mini    = !!opts.mini;
    var onClick = opts.onClick || function () {};

    var data     = NODES.map(function (n) { return Object.assign({}, n); });
    var linkData = LINKS.map(function (l) { return Object.assign({}, l); });

    // adjacency map for highlight
    var adj = new Map();
    LINKS.forEach(function (l) {
      [l.source, l.target].forEach(function (id) {
        if (!adj.has(id)) adj.set(id, new Set());
      });
      adj.get(l.source).add(l.target);
      adj.get(l.target).add(l.source);
    });

    container.innerHTML = '';
    var svg = d3.select(container).append('svg')
      .attr('role', 'img').attr('aria-label', 'Knowledge graph');

    function size() {
      var r = container.getBoundingClientRect();
      return { w: Math.max(300, r.width), h: Math.max(180, r.height) };
    }
    var s = size(), W = s.w, H = s.h;
    svg.attr('viewBox', '0 0 ' + W + ' ' + H);

    // Milky-mist background gradient
    var defs = svg.append('defs');
    var gradId = mini ? 'gBgMini' : 'gBgMain';
    var grad = defs.append('radialGradient')
      .attr('id', gradId).attr('cx', '35%').attr('cy', '40%').attr('r', '65%');
    grad.append('stop').attr('offset', '0%').attr('stop-color', '#ece9e2');
    grad.append('stop').attr('offset', '100%').attr('stop-color', '#f4f2ee');

    svg.append('rect').attr('width', W).attr('height', H)
      .attr('fill', 'url(#' + gradId + ')');

    var root = svg.append('g');

    // Zoom — KEY FIX: filter so regular wheel-scroll passes through the page
    // Only ctrl+wheel or non-wheel events (drag, pinch) trigger zoom
    if (!mini) {
      var zoom = d3.zoom().scaleExtent([0.4, 4])
        .filter(function (event) {
          if (event.type === 'wheel') return event.ctrlKey;
          return !event.button;
        })
        .on('zoom', function (e) { root.attr('transform', e.transform); });
      svg.call(zoom);

      // Transient ctrl-scroll hint
      svg.on('wheel.hint', function (event) {
        if (!event.ctrlKey) {
          var hint = svg.select('.ctrl-hint');
          if (hint.empty()) {
            hint = svg.append('text').attr('class', 'ctrl-hint')
              .attr('x', W / 2).attr('y', H - 16)
              .attr('text-anchor', 'middle')
              .attr('font-size', '11px')
              .attr('fill', '#9b9490')
              .attr('pointer-events', 'none')
              .attr('font-family', 'Inter,sans-serif');
          }
          hint.text('Hold Ctrl + scroll to zoom').attr('opacity', 1)
            .transition().duration(1600).attr('opacity', 0);
        }
      }, { passive: true });
    }

    var isMobile = W < 640;
    var rScale   = mini ? 0.42 : isMobile ? 0.75 : 1;

    var sim = d3.forceSimulation(data)
      .force('link', d3.forceLink(linkData).id(function (d) { return d.id; })
        .distance(mini ? 34 : isMobile ? 65 : 88).strength(0.4))
      .force('charge', d3.forceManyBody().strength(mini ? -80 : isMobile ? -170 : -260))
      .force('center', d3.forceCenter(W / 2, H / 2))
      .force('collide', d3.forceCollide().radius(function (d) {
        return radiusFor(d.kind) * rScale + 8;
      }));

    var linkSel = root.append('g').attr('class', 'links')
      .selectAll('line').data(linkData).join('line')
      .attr('stroke', 'rgba(60,50,40,0.1)')
      .attr('stroke-width', mini ? 0.8 : 1.1);

    var nodeG = root.append('g').attr('class', 'nodes')
      .selectAll('g').data(data).join('g')
      .style('cursor', 'pointer');

    // Silky orb: outer halo + inner filled circle + white ring
    nodeG.append('circle')
      .attr('r', function (d) { return (radiusFor(d.kind) + 8) * rScale; })
      .attr('fill', function (d) { return haloFor(d.kind); })
      .attr('pointer-events', 'none');

    nodeG.append('circle')
      .attr('r', function (d) { return radiusFor(d.kind) * rScale; })
      .attr('fill', function (d) { return colorFor(d.kind); })
      .attr('stroke', 'rgba(255,255,255,0.72)')
      .attr('stroke-width', mini ? 1 : 1.5);

    // Pulsing ring on system nodes
    nodeG.filter(function (d) { return d.kind === 'system'; })
      .append('circle')
      .attr('class', 'pulse-ring')
      .attr('r', function (d) { return radiusFor(d.kind) * rScale; })
      .attr('fill', 'none')
      .attr('stroke', function (d) { return colorFor(d.kind); })
      .attr('stroke-width', 1)
      .attr('opacity', 0)
      .attr('pointer-events', 'none');

    if (!mini) {
      nodeG.append('text')
        .text(function (d) { return d.label; })
        .attr('x', function (d) { return radiusFor(d.kind) + 9; })
        .attr('y', 4)
        .attr('fill', '#2a2520')
        .attr('font-family', 'Inter, sans-serif')
        .attr('font-size', function (d) { return d.kind === 'system' ? 12 : 10; })
        .attr('font-weight', function (d) { return d.kind === 'system' ? '600' : '400'; })
        .attr('opacity', 0.82)
        .attr('pointer-events', 'none');
    }

    // Drag
    var drag = d3.drag()
      .on('start', function (e, d) { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag',  function (e, d) { d.fx = e.x; d.fy = e.y; })
      .on('end',   function (e, d) { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; });
    nodeG.call(drag);

    // Highlight neighbours
    function highlight(id) {
      if (!id) {
        nodeG.attr('opacity', 1);
        linkSel.attr('stroke', 'rgba(60,50,40,0.1)').attr('stroke-width', mini ? 0.8 : 1.1);
        return;
      }
      var neigh = adj.get(id) || new Set();
      nodeG.attr('opacity', function (d) {
        return (d.id === id || neigh.has(d.id)) ? 1 : 0.22;
      });
      linkSel.each(function (l) {
        var s = l.source.id || l.source, t = l.target.id || l.target;
        var active = s === id || t === id;
        d3.select(this)
          .attr('stroke', active ? 'rgba(23,107,82,0.55)' : 'rgba(60,50,40,0.04)')
          .attr('stroke-width', active ? (mini ? 1.5 : 2) : (mini ? 0.4 : 0.7));
      });
    }

    nodeG
      .on('mouseenter', function (_e, d) { highlight(d.id); })
      .on('mouseleave', function () { highlight(null); })
      .on('click', function (_e, d) {
        if (mini) {
          var target = document.getElementById(d.section || 'systems');
          if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
          onClick(d);
        }
      })
      .on('dblclick', function (_e, d) {
        if (mini || d.kind !== 'system') return;
        var keep = new Set([d.id].concat(Array.from(adj.get(d.id) || [])));
        nodeG.style('display', function (n) { return keep.has(n.id) ? null : 'none'; });
        linkSel.style('display', function (l) {
          return (keep.has(l.source.id) && keep.has(l.target.id)) ? null : 'none';
        });
        svg.on('dblclick.reset', function (ev) {
          if (ev.target === svg.node()) {
            nodeG.style('display', null);
            linkSel.style('display', null);
            svg.on('dblclick.reset', null);
          }
        });
      });

    sim.on('tick', function () {
      linkSel
        .attr('x1', function (d) { return d.source.x; }).attr('y1', function (d) { return d.source.y; })
        .attr('x2', function (d) { return d.target.x; }).attr('y2', function (d) { return d.target.y; });
      nodeG.attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });
    });

    // Responsive resize
    new ResizeObserver(function () {
      var ns = size(); W = ns.w; H = ns.h;
      svg.attr('viewBox', '0 0 ' + W + ' ' + H);
      svg.select('rect').attr('width', W).attr('height', H);
      sim.force('center', d3.forceCenter(W / 2, H / 2)).alpha(0.3).restart();
    }).observe(container);

    // Gentle pulse animation for system nodes (CSS keyframe approach via JS interval)
    var pulseRings = nodeG.selectAll('.pulse-ring');
    if (!mini && !pulseRings.empty()) {
      (function pulse() {
        pulseRings
          .attr('r', function () { return this.parentNode.__data__ ? radiusFor(this.parentNode.__data__.kind) * rScale : 16; })
          .attr('opacity', 0.7)
          .transition().duration(1600)
          .attr('r', function () { return this.parentNode.__data__ ? (radiusFor(this.parentNode.__data__.kind) + 14) * rScale : 30; })
          .attr('opacity', 0)
          .on('end', function () { setTimeout(pulse, 800); });
      })();
    }
  }

  // ---- NODE DETAIL PANEL ----
  var panel     = document.getElementById('panel');
  var scrim     = document.getElementById('panel-scrim');
  var panelBody = document.getElementById('panel-body');

  function openPanel(node) {
    var col = colorFor(node.kind);
    var kindLabel = { system: 'Production system', impact: 'Impact metric', concept: 'Concept' }[node.kind] || 'Tool / technology';
    panelBody.innerHTML =
      '<div style="display:flex;align-items:center;gap:0.45rem;margin-bottom:0.6rem">' +
        '<span style="width:9px;height:9px;border-radius:50%;background:' + col + ';display:inline-block"></span>' +
        '<span style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:' + col + ';font-weight:600">' + kindLabel + '</span>' +
      '</div>' +
      '<h3 style="font-family:Playfair Display,serif;font-size:1.45rem;margin:0 0 1rem;color:#1a1818;font-weight:500">' + node.label + '</h3>' +
      '<p style="font-size:0.93rem;line-height:1.72;color:#5c5a55">' + (node.detail || 'A component in the system graph.') + '</p>' +
      (node.section
        ? '<a href="#' + node.section + '" style="display:inline-block;margin-top:1.5rem;color:#176b52;font-size:0.88rem;font-weight:500;text-decoration:none;border-bottom:1px solid #176b52" onclick="document.getElementById(\'panel\').classList.remove(\'open\');document.getElementById(\'panel-scrim\').classList.remove(\'open\');document.getElementById(\'panel\').setAttribute(\'aria-hidden\',\'true\')">Jump to section ↓</a>'
        : '');
    panel.classList.add('open');
    scrim.classList.add('open');
    panel.setAttribute('aria-hidden', 'false');
  }

  function closePanel() {
    panel.classList.remove('open');
    scrim.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
  }

  if (panel && scrim) {
    document.getElementById('panel-close').addEventListener('click', closePanel);
    scrim.addEventListener('click', closePanel);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closePanel();
    });
  }

  // ---- INIT ----
  var graphEl    = document.getElementById('graph');
  var minigraphEl = document.getElementById('minigraph');

  if (graphEl)    buildGraph(graphEl,     { onClick: openPanel });
  if (minigraphEl) buildGraph(minigraphEl, { mini: true });

  // Minimap: show when graph section scrolls out of view
  var graphContainer = document.getElementById('graph-container');
  var minimap        = document.getElementById('minimap');
  if (graphContainer && minimap) {
    new IntersectionObserver(function (entries) {
      var visible = entries[0].isIntersecting;
      minimap.classList.toggle('show', !visible);
      minimap.setAttribute('aria-hidden', visible ? 'true' : 'false');
    }, { threshold: 0.1 }).observe(graphContainer);
  }

  // Nav glassmorphism on scroll
  var siteHeader = document.getElementById('site-header');
  if (siteHeader) {
    window.addEventListener('scroll', function () {
      siteHeader.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }

})();

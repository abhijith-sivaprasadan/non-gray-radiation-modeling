"""The interactive single-page app served by scripts/dashboard_server.py.

Kept as one plain string (no build step, no external JS/CSS dependencies) so the
whole app is a single HTTP response and works with nothing but the stdlib server.
"""

PAGE_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Non-Gray Thermal Radiation Portfolio - Live Dashboard</title>
<style>
:root {
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e; --ink-muted: #898781;
  --grid: #e1e0d9; --border: rgba(11,11,11,0.10);
  --blue: #2a78d6; --aqua: #1baf7a; --yellow: #eda100; --violet: #4a3aa7; --red: #e34948; --magenta: #e87ba4;
  --good: #0ca30c; --warning: #fab219; --critical: #d03b3b;
}
@media (prefers-color-scheme: dark) {
  :root {
    --page: #0d0d0d; --surface: #1a1a19; --ink: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
    --grid: #2c2c2a; --border: rgba(255,255,255,0.10);
    --blue: #3987e5; --aqua: #199e70; --yellow: #c98500; --violet: #9085e9; --red: #e66767; --magenta: #d55181;
    --good: #0ca30c; --warning: #fab219; --critical: #d03b3b;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink); font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
.layout { display: flex; min-height: 100vh; }
nav { width: 260px; flex: 0 0 260px; background: var(--surface); border-right: 1px solid var(--border);
  padding: 16px 0; position: sticky; top: 0; height: 100vh; overflow-y: auto; }
nav .brand { padding: 0 20px 12px; font-weight: 650; font-size: 15px; border-bottom: 1px solid var(--border); margin-bottom: 10px; }
nav .runbar { padding: 0 16px 14px; display: flex; flex-direction: column; gap: 6px; border-bottom: 1px solid var(--border); margin-bottom: 10px; }
nav a { display: block; padding: 9px 20px; color: var(--ink-2); text-decoration: none; font-size: 13.5px; border-left: 3px solid transparent; }
nav a:hover { color: var(--ink); background: var(--page); }
nav a.active { color: var(--blue); border-left-color: var(--blue); font-weight: 600; }
main { flex: 1; padding: 28px 40px 100px; max-width: 1080px; }
section { margin-bottom: 56px; scroll-margin-top: 20px; }
h1 { font-size: 24px; font-weight: 650; margin: 0 0 6px; }
h2 { font-size: 19px; font-weight: 650; margin: 0 0 4px; }
h3 { font-size: 14px; font-weight: 650; margin: 20px 0 8px; color: var(--ink-2); }
.subtitle { color: var(--ink-2); font-size: 13.5px; margin: 0 0 20px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; margin-bottom: 16px; }
.tiles { display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0 20px; }
.tile { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 18px; min-width: 150px; flex: 1 1 150px; }
.tile .label { font-size: 11.5px; color: var(--ink-muted); text-transform: uppercase; letter-spacing: .03em; }
.tile .value { font-size: 23px; font-weight: 650; margin-top: 4px; font-variant-numeric: tabular-nums; }
.tile .sub { font-size: 11.5px; color: var(--ink-2); margin-top: 2px; }
figure { margin: 14px 0; }
figure img { max-width: 100%; border-radius: 8px; border: 1px solid var(--border); display: block; }
figcaption { font-size: 12px; color: var(--ink-muted); margin-top: 6px; }
.figrow { display: flex; flex-wrap: wrap; gap: 16px; }
.figrow figure { flex: 1 1 320px; margin: 0; }
table { border-collapse: collapse; width: 100%; font-size: 12.5px; margin: 6px 0; }
th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--grid); font-variant-numeric: tabular-nums; white-space: nowrap; }
th { color: var(--ink-2); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: .02em; cursor: pointer; user-select: none; }
th:hover { color: var(--ink); }
.note { font-size: 12px; color: var(--ink-muted); margin-top: 6px; }
code { background: var(--page); padding: 1px 6px; border-radius: 4px; font-size: 12px; }
.status { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; padding: 2px 0; }
.status .dot { width: 8px; height: 8px; border-radius: 50%; }
.status.ok .dot { background: var(--good); } .status.ok { color: var(--ink-2); }
.status.missing .dot { background: var(--critical); } .status.missing { color: var(--critical); }
.eqn { background: var(--page); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; font-family: Consolas, monospace; font-size: 13px; }
button { font: inherit; cursor: pointer; border-radius: 7px; border: 1px solid var(--border); background: var(--surface); color: var(--ink); padding: 7px 12px; font-size: 13px; }
button:hover:not(:disabled) { background: var(--page); }
button:disabled { opacity: .55; cursor: default; }
button.primary { background: var(--blue); border-color: var(--blue); color: #fff; }
button.primary:hover:not(:disabled) { filter: brightness(1.08); }
#statusbar { position: fixed; left: 260px; right: 0; bottom: 0; padding: 9px 20px; background: var(--surface);
  border-top: 1px solid var(--border); font-size: 12.5px; color: var(--ink-2); z-index: 5; }
.table-toolbar { display: flex; align-items: center; gap: 10px; margin: 10px 0 6px; }
.table-toolbar input { font: inherit; padding: 6px 10px; border-radius: 7px; border: 1px solid var(--border); background: var(--page); color: var(--ink); font-size: 12.5px; width: 220px; }
.table-count { font-size: 12px; color: var(--ink-muted); }
.pager { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
.pager span { font-size: 12px; color: var(--ink-2); }
.table-wrap { overflow-x: auto; }
.chart-wrap { position: relative; margin: 10px 0; }
.chart-svg { width: 100%; height: auto; display: block; }
.grid-line { stroke: var(--grid); stroke-width: 1; }
.axis-line { stroke: var(--ink-muted); stroke-width: 1; }
.axis-label { fill: var(--ink-muted); font-size: 10px; }
.legend { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 6px; font-size: 12px; color: var(--ink-2); }
.legend .item { display: inline-flex; align-items: center; gap: 6px; }
.legend .swatch { width: 10px; height: 10px; border-radius: 2px; }
.tooltip { position: absolute; pointer-events: none; background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 8px 10px; font-size: 11.5px; box-shadow: 0 4px 14px rgba(0,0,0,.18); white-space: nowrap; }
.tooltip .row { display: flex; align-items: center; gap: 6px; }
.tooltip .row .swatch { width: 8px; height: 8px; border-radius: 50%; }
.field-select { display: flex; align-items: center; gap: 8px; margin: 6px 0 14px; }
.field-select select { font: inherit; padding: 5px 8px; border-radius: 7px; border: 1px solid var(--border); background: var(--page); color: var(--ink); }
</style>
</head>
<body>
<div class="layout">
<nav>
  <div class="brand">Radiation Portfolio</div>
  <div class="runbar">
    <button class="primary" id="run-all-btn">Run all</button>
    <button id="refresh-btn">Refresh</button>
  </div>
  <a href="#overview" data-section="overview">Overview</a>
  <a href="#project1" data-section="project1">Project 1: Hydrogen / H2O</a>
  <a href="#project2" data-section="project2">Project 2: Particle correlations</a>
  <a href="#project3" data-section="project3">Project 3: DOM profiles</a>
  <a href="#project4" data-section="project4">Project 4: ML surrogate</a>
  <a href="#project5" data-section="project5">Project 5: RADCAL smoke test</a>
</nav>
<main>
  <section id="overview"></section>
  <section id="project1"></section>
  <section id="project2"></section>
  <section id="project3"></section>
  <section id="project4"></section>
  <section id="project5"></section>
</main>
</div>
<div id="statusbar">Loading...</div>

<script>
const PALETTE = ['#2a78d6', '#1baf7a', '#eda100', '#4a3aa7', '#e34948', '#e87ba4', '#eb6834'];
let DATA = null;

function setStatus(text) { document.getElementById('statusbar').textContent = text; }

function el(tag, attrs, children) {
  const node = document.createElement(tag);
  for (const k in (attrs || {})) {
    if (k === 'class') node.className = attrs[k];
    else if (k === 'text') node.textContent = attrs[k];
    else node.setAttribute(k, attrs[k]);
  }
  (children || []).forEach(c => node.appendChild(c));
  return node;
}

function fmtNum(v) {
  if (v === null || v === undefined) return '';
  if (typeof v !== 'number') return String(v);
  if (v === 0) return '0';
  const abs = Math.abs(v);
  if (abs >= 1e5 || abs < 1e-3) return v.toExponential(3);
  return Number(v.toPrecision(5)).toString();
}

// ---------------------------------------------------------------- tables ---

function dataTable(container, columns, rows, opts) {
  opts = Object.assign({ pageSize: 15, filterable: true }, opts || {});
  let sortCol = null, sortDir = 1, filterText = '', page = 0;

  function render() {
    let filtered = rows;
    if (filterText) {
      const q = filterText.toLowerCase();
      filtered = rows.filter(r => columns.some(c => String(r[c] ?? '').toLowerCase().includes(q)));
    }
    if (sortCol) {
      filtered = [...filtered].sort((a, b) => {
        const av = a[sortCol], bv = b[sortCol];
        const bothNumeric = typeof av === 'number' && typeof bv === 'number';
        const cmp = bothNumeric ? (av - bv) : String(av).localeCompare(String(bv));
        return cmp * sortDir;
      });
    }
    const totalPages = Math.max(1, Math.ceil(filtered.length / opts.pageSize));
    page = Math.min(page, totalPages - 1);
    const pageRows = filtered.slice(page * opts.pageSize, (page + 1) * opts.pageSize);

    container.innerHTML = '';
    if (opts.filterable) {
      const input = el('input', { placeholder: 'Filter rows...' });
      input.value = filterText;
      input.addEventListener('input', e => { filterText = e.target.value; page = 0; render(); });
      const count = el('span', { class: 'table-count', text: filtered.length + ' rows' });
      container.appendChild(el('div', { class: 'table-toolbar' }, [input, count]));
    }

    const headRow = el('tr', {}, columns.map(c => {
      const label = c + (sortCol === c ? (sortDir === 1 ? ' ▲' : ' ▼') : '');
      const th = el('th', { text: label });
      th.addEventListener('click', () => { sortDir = (sortCol === c) ? -sortDir : 1; sortCol = c; render(); });
      return th;
    }));
    const tbody = el('tbody', {}, pageRows.map(r => el('tr', {}, columns.map(c => el('td', { text: fmtNum(r[c]) })))));
    const table = el('table', {}, [el('thead', {}, [headRow]), tbody]);
    container.appendChild(el('div', { class: 'table-wrap' }, [table]));

    if (totalPages > 1) {
      const prev = el('button', { text: 'Prev' }); prev.disabled = page === 0;
      prev.addEventListener('click', () => { page--; render(); });
      const next = el('button', { text: 'Next' }); next.disabled = page >= totalPages - 1;
      next.addEventListener('click', () => { page++; render(); });
      const info = el('span', { text: `Page ${page + 1} / ${totalPages}` });
      container.appendChild(el('div', { class: 'pager' }, [prev, info, next]));
    }
  }
  render();
}

// ---------------------------------------------------------------- charts ---

function svgEl(tag, attrs) {
  const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const k in attrs) node.setAttribute(k, attrs[k]);
  return node;
}

function chart(container, series, opts) {
  opts = Object.assign({
    width: 620, height: 300, padding: { top: 14, right: 18, bottom: 34, left: 58 },
    xLabel: '', yLabel: '', logX: false, logY: false, mode: 'line', refLineYEqualsX: false,
  }, opts || {});
  container.innerHTML = '';

  const wrap = el('div', { class: 'chart-wrap' });
  const { width, height, padding } = opts;
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;
  const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, class: 'chart-svg' });

  const tx = opts.logX ? (v => Math.log10(v)) : (v => v);
  const ty = opts.logY ? (v => Math.log10(v)) : (v => v);
  const itx = opts.logX ? (v => Math.pow(10, v)) : (v => v);

  let allX = [], allY = [];
  series.forEach(s => s.points.forEach(p => { allX.push(tx(p.x)); allY.push(ty(p.y)); }));
  if (opts.refLineYEqualsX) { allX.forEach(v => allY.push(v)); allY.forEach(v => allX.push(v)); }
  let xMin = Math.min(...allX), xMax = Math.max(...allX);
  let yMin = Math.min(...allY), yMax = Math.max(...allY);
  if (xMin === xMax) { xMin -= 1; xMax += 1; }
  if (yMin === yMax) { yMin -= 1; yMax += 1; }
  const xPad = (xMax - xMin) * 0.04, yPad = (yMax - yMin) * 0.06;
  xMin -= xPad; xMax += xPad; yMin -= yPad; yMax += yPad;

  const xScale = v => padding.left + (tx(v) - xMin) / (xMax - xMin) * plotW;
  const yScale = v => padding.top + plotH - (ty(v) - yMin) / (yMax - yMin) * plotH;

  for (let i = 0; i <= 4; i++) {
    const y = padding.top + plotH * i / 4;
    svg.appendChild(svgEl('line', { x1: padding.left, x2: width - padding.right, y1: y, y2: y, class: 'grid-line' }));
    const dataVal = itx === undefined ? null : null;
    const label = fmtNum(opts.logY ? Math.pow(10, yMax - (yMax - yMin) * i / 4) : (yMax - (yMax - yMin) * i / 4));
    svg.appendChild(svgEl('text', { x: padding.left - 8, y: y + 3, class: 'axis-label', 'text-anchor': 'end' })).textContent = label;
  }
  for (let i = 0; i <= 4; i++) {
    const x = padding.left + plotW * i / 4;
    const rawX = xMin + (xMax - xMin) * i / 4;
    const label = fmtNum(opts.logX ? Math.pow(10, rawX) : rawX);
    const t = svgEl('text', { x: x, y: height - padding.bottom + 16, class: 'axis-label', 'text-anchor': 'middle' });
    t.textContent = label;
    svg.appendChild(t);
  }
  svg.appendChild(svgEl('line', { x1: padding.left, x2: padding.left, y1: padding.top, y2: padding.top + plotH, class: 'axis-line' }));
  svg.appendChild(svgEl('line', { x1: padding.left, x2: width - padding.right, y1: padding.top + plotH, y2: padding.top + plotH, class: 'axis-line' }));

  if (opts.refLineYEqualsX) {
    const p1x = padding.left, p1y = yScale(itx(xMin));
    const p2x = width - padding.right, p2y = yScale(itx(xMax));
    svg.appendChild(svgEl('line', { x1: p1x, x2: p2x, y1: p1y, y2: p2y, stroke: 'var(--ink-muted)', 'stroke-width': 1, 'stroke-dasharray': '4 4' }));
  }

  series.forEach((s, i) => {
    const color = s.color || PALETTE[i % PALETTE.length];
    if (opts.mode === 'scatter') {
      s.points.forEach(p => {
        svg.appendChild(svgEl('circle', { cx: xScale(p.x), cy: yScale(p.y), r: 3, fill: color, 'fill-opacity': 0.75 }));
      });
    } else {
      const sorted = [...s.points].sort((a, b) => a.x - b.x);
      const d = sorted.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${xScale(p.x).toFixed(2)} ${yScale(p.y).toFixed(2)}`).join(' ');
      svg.appendChild(svgEl('path', { d, fill: 'none', stroke: color, 'stroke-width': 2 }));
    }
  });

  const hoverLine = svgEl('line', { x1: 0, x2: 0, y1: padding.top, y2: padding.top + plotH, stroke: 'var(--ink-muted)', 'stroke-width': 1, opacity: 0 });
  svg.appendChild(hoverLine);
  const hoverDots = series.map((s, i) => svgEl('circle', { r: 4, fill: s.color || PALETTE[i % PALETTE.length], opacity: 0 }));
  hoverDots.forEach(d => svg.appendChild(d));

  const tooltip = el('div', { class: 'tooltip' });
  tooltip.style.display = 'none';
  wrap.appendChild(svg);
  wrap.appendChild(tooltip);

  const catcher = svgEl('rect', { x: padding.left, y: padding.top, width: plotW, height: plotH, fill: 'transparent' });
  svg.appendChild(catcher);

  catcher.addEventListener('mousemove', evt => {
    const rect = svg.getBoundingClientRect();
    const scaleX = width / rect.width;
    const mouseX = (evt.clientX - rect.left) * scaleX;
    const dataXlog = xMin + (mouseX - padding.left) / plotW * (xMax - xMin);
    const dataX = itx(dataXlog);

    const rows = [];
    series.forEach((s, i) => {
      let nearest = s.points[0], bestDist = Infinity;
      s.points.forEach(p => { const dist = Math.abs(p.x - dataX); if (dist < bestDist) { bestDist = dist; nearest = p; } });
      if (!nearest) return;
      hoverDots[i].setAttribute('cx', xScale(nearest.x));
      hoverDots[i].setAttribute('cy', yScale(nearest.y));
      hoverDots[i].setAttribute('opacity', 1);
      rows.push({ name: s.name, color: s.color || PALETTE[i % PALETTE.length], x: nearest.x, y: nearest.y });
    });
    hoverLine.setAttribute('x1', xScale(dataX));
    hoverLine.setAttribute('x2', xScale(dataX));
    hoverLine.setAttribute('opacity', 1);

    tooltip.innerHTML = '';
    if (rows.length) {
      tooltip.appendChild(el('div', { text: (opts.xLabel || 'x') + ': ' + fmtNum(rows[0].x) }));
      rows.forEach(r => {
        const sw = el('span', { class: 'swatch' }); sw.style.background = r.color;
        tooltip.appendChild(el('div', { class: 'row' }, [sw, el('span', { text: r.name + ': ' + fmtNum(r.y) })]));
      });
    }
    tooltip.style.display = rows.length ? 'block' : 'none';
    tooltip.style.left = Math.min(evt.offsetX + 14, rect.width - 170) + 'px';
    tooltip.style.top = Math.max(evt.offsetY - 10, 0) + 'px';
  });
  catcher.addEventListener('mouseleave', () => {
    tooltip.style.display = 'none';
    hoverLine.setAttribute('opacity', 0);
    hoverDots.forEach(d => d.setAttribute('opacity', 0));
  });

  if (series.length > 1) {
    const legend = el('div', { class: 'legend' }, series.map((s, i) => {
      const sw = el('span', { class: 'swatch' }); sw.style.background = s.color || PALETTE[i % PALETTE.length];
      return el('span', { class: 'item' }, [sw, el('span', { text: s.name })]);
    }));
    wrap.appendChild(legend);
  }
  container.appendChild(wrap);
}

// ------------------------------------------------------------- sections ---

function renderOverview(data) {
  const root = document.getElementById('overview');
  root.innerHTML = '';
  root.appendChild(el('h1', { text: 'Non-Gray Thermal Radiation Portfolio' }));
  root.appendChild(el('p', {
    class: 'subtitle',
    text: 'Real data extracted from published papers (Singh & Hostikka 2026, Rashidzadeh et al. 2026, ' +
      'Johansson 2017) - live, interactive view of the generated equations, benchmark tables, and DOM/ML pipeline.',
  }));
  root.appendChild(el('div', { class: 'tiles' }, data.tiles.map(t => el('div', { class: 'tile' }, [
    el('div', { class: 'label', text: t.label }),
    el('div', { class: 'value', text: t.value }),
    ...(t.sub ? [el('div', { class: 'sub', text: t.sub })] : []),
  ]))));
  const card = el('div', { class: 'card' }, [el('h3', { text: 'Artifact status' })]);
  data.artifacts.forEach(a => {
    card.appendChild(el('div', { class: 'status ' + (a.ok ? 'ok' : 'missing') }, [
      el('span', { class: 'dot' }), el('span', { text: a.label + (a.ok ? ' report generated' : ' not generated yet') }),
    ]));
  });
  root.appendChild(card);
}

function figureUrl(project, name) { return '/outputs/' + project + '/figures/' + name; }

function renderProject1(data) {
  const root = document.getElementById('project1');
  root.innerHTML = '';
  root.appendChild(el('h2', { text: 'Project 1: Published Hydrogen / H2O Radiation Data' }));
  root.appendChild(el('p', { class: 'subtitle', text: 'Singh & Hostikka 2026 - HITEMP-derived H2O Planck-mean fit and validation fields.' }));
  root.appendChild(el('div', { class: 'eqn', text: data.equation }));
  const figrow = el('div', { class: 'figrow' });
  data.figures.forEach(f => {
    if (!f.exists) { figrow.appendChild(el('p', { class: 'note', text: 'Missing figure: ' + f.name })); return; }
    const img = el('img', { src: figureUrl('project1_real_hydrogen', f.name), alt: f.name });
    figrow.appendChild(el('figure', {}, [img, el('figcaption', { text: f.name })]));
  });
  root.appendChild(figrow);
  root.appendChild(el('h3', { text: 'Published model-error summary' }));
  const tableDiv = el('div', {});
  root.appendChild(tableDiv);
  if (data.error_summary) dataTable(tableDiv, data.error_summary.columns, data.error_summary.rows, { filterable: false, pageSize: 20 });
}

function renderProject2(data) {
  const root = document.getElementById('project2');
  root.innerHTML = '';
  root.appendChild(el('h2', { text: 'Project 2: Johansson Particle Correlations' }));
  root.appendChild(el('p', { class: 'subtitle', text: 'Gray coal/char and ash absorption/scattering efficiencies fitted to Mie data (Johansson 2017, Eq. 8).' }));

  if (!data.efficiencies) { root.appendChild(el('p', { class: 'note', text: 'Not generated yet.' })); return; }

  const temps = [...new Set(data.efficiencies.rows.map(r => r.temperature_k))].sort((a, b) => a - b);
  const select = el('select', {});
  temps.forEach(t => select.appendChild(el('option', { value: t, text: t + ' K' })));
  select.value = temps.includes(1500) ? 1500 : temps[Math.floor(temps.length / 2)];
  root.appendChild(el('div', { class: 'field-select' }, [el('span', { text: 'Temperature:' }), select]));

  const absChart = el('div', {});
  const scatChart = el('div', {});
  root.appendChild(el('h3', { text: 'Absorption efficiency vs. particle radius' }));
  root.appendChild(absChart);
  root.appendChild(el('h3', { text: 'Scattering efficiency vs. particle radius' }));
  root.appendChild(scatChart);

  function draw() {
    const t = Number(select.value);
    const rows = data.efficiencies.rows.filter(r => r.temperature_k === t).sort((a, b) => a.radius_um - b.radius_um);
    const seriesFor = (absKey) => [
      { name: 'coal/char', points: rows.map(r => ({ x: r.radius_um, y: r['coal_char_' + absKey] })) },
      { name: 'ash1', points: rows.map(r => ({ x: r.radius_um, y: r['ash1_' + absKey] })) },
      { name: 'ash2', points: rows.map(r => ({ x: r.radius_um, y: r['ash2_' + absKey] })) },
    ];
    chart(absChart, seriesFor('q_abs'), { logX: true, logY: true, xLabel: 'radius [um]', yLabel: 'Q_abs' });
    chart(scatChart, seriesFor('q_scat'), { logX: true, logY: true, xLabel: 'radius [um]', yLabel: 'Q_scat' });
  }
  select.addEventListener('change', draw);
  draw();

  root.appendChild(el('h3', { text: 'Correlation parameters' }));
  const paramsDiv = el('div', {});
  root.appendChild(paramsDiv);
  if (data.params) dataTable(paramsDiv, data.params.columns, data.params.rows, { filterable: false, pageSize: 20 });
}

function renderDomProfile(root, title, profile) {
  root.appendChild(el('h3', { text: title }));
  if (!profile) { root.appendChild(el('p', { class: 'note', text: 'Not generated yet.' })); return; }
  const fluxDiv = el('div', {}), sourceDiv = el('div', {});
  root.appendChild(el('div', { class: 'figrow' }, [
    el('div', { style: 'flex:1 1 320px' }, [el('h3', { text: 'Heat flux [W/m2]' }), fluxDiv]),
    el('div', { style: 'flex:1 1 320px' }, [el('h3', { text: 'Source term [W/m3]' }), sourceDiv]),
  ]));
  const points = profile.rows.map(r => ({ x: r.coordinate_m, y: r.heat_flux_w_m2 }));
  const sourcePoints = profile.rows.map(r => ({ x: r.coordinate_m, y: r.source_term_w_m3 }));
  chart(fluxDiv, [{ name: 'heat flux', points }], { xLabel: 'coordinate [m]', yLabel: 'W/m2' });
  chart(sourceDiv, [{ name: 'source term', points: sourcePoints }], { xLabel: 'coordinate [m]', yLabel: 'W/m3' });
  const tableDiv = el('div', {});
  root.appendChild(tableDiv);
  dataTable(tableDiv, profile.columns, profile.rows, { pageSize: 10 });
}

function renderProject3(data) {
  const root = document.getElementById('project3');
  root.innerHTML = '';
  root.appendChild(el('h2', { text: 'Project 3: DOM on Published Fields' }));
  root.appendChild(el('p', {
    class: 'subtitle',
    text: '1-D discrete-ordinates sweep through the radial and axial Singh & Hostikka fields. ' +
      "Not a reproduction of the paper's 2-D LBL/RCFSK benchmark.",
  }));
  renderDomProfile(root, 'Radial midline', data.radial);
  renderDomProfile(root, 'Axial centerline', data.axial);
}

function renderProject4(data) {
  const root = document.getElementById('project4');
  root.innerHTML = '';
  root.appendChild(el('h2', { text: 'Project 4: ML Surrogate for the Published H2O Correlation' }));
  root.appendChild(el('p', { class: 'subtitle', text: 'A small MLP trained to reproduce log10(kappa_planck) from the Singh & Hostikka correlation.' }));

  if (data.metrics) {
    const m = data.metrics;
    root.appendChild(el('div', { class: 'tiles' }, [
      el('div', { class: 'tile' }, [el('div', { class: 'label', text: 'R2 (log space)' }), el('div', { class: 'value', text: fmtNum(m.r2_log_space) })]),
      el('div', { class: 'tile' }, [el('div', { class: 'label', text: 'RMSE log10(kappa)' }), el('div', { class: 'value', text: fmtNum(m.rmse_log10) })]),
      el('div', { class: 'tile' }, [el('div', { class: 'label', text: 'MAPE(kappa)' }), el('div', { class: 'value', text: (100 * m.mean_absolute_percentage_error_kappa).toFixed(2) + '%' })]),
      el('div', { class: 'tile' }, [el('div', { class: 'label', text: 'Train / test samples' }), el('div', { class: 'value', text: m.train_samples + ' / ' + m.test_samples })]),
    ]));
  }

  root.appendChild(el('h3', { text: 'Parity: predicted vs. reference kappa' }));
  const chartDiv = el('div', {});
  root.appendChild(chartDiv);
  if (data.predictions) {
    const points = data.predictions.rows.map(r => ({ x: r['reference_kappa_m-1'], y: r['predicted_kappa_m-1'] }));
    chart(chartDiv, [{ name: 'prediction', points, color: PALETTE[0] }], {
      mode: 'scatter', logX: true, logY: true, refLineYEqualsX: true,
      xLabel: 'reference kappa [m^-1]', yLabel: 'predicted kappa [m^-1]',
    });
    const tableDiv = el('div', {});
    root.appendChild(el('h3', { text: 'Test-set predictions' }));
    root.appendChild(tableDiv);
    dataTable(tableDiv, data.predictions.columns, data.predictions.rows, { pageSize: 15 });
  }
}

function renderProject5(data) {
  const root = document.getElementById('project5');
  root.innerHTML = '';
  root.appendChild(el('h2', { text: 'Project 5: RADCAL Asset Smoke Test' }));
  root.appendChild(el('p', {
    class: 'subtitle',
    text: 'Launches the downloaded Firemodels RADCAL executable and parses its output. A launch/parsing smoke test, not a validation claim.',
  }));
  root.appendChild(el('h3', { text: 'Parsed summary' }));
  const tableDiv = el('div', {});
  root.appendChild(tableDiv);
  if (data.summary) dataTable(tableDiv, data.summary.columns, data.summary.rows, { filterable: false, pageSize: 20 });
  else root.appendChild(el('p', { class: 'note', text: 'Not generated yet.' }));
}

function renderAll() {
  renderOverview(DATA.overview);
  renderProject1(DATA.project1);
  renderProject2(DATA.project2);
  renderDomSafe();
  renderProject4(DATA.project4);
  renderProject5(DATA.project5);
}
function renderDomSafe() { renderProject3(DATA.project3); }

async function loadData() {
  const res = await fetch('/api/data');
  DATA = await res.json();
  renderAll();
}

async function runTarget(target, button) {
  const original = button.textContent;
  button.disabled = true;
  button.textContent = 'Running...';
  setStatus('Running ' + target + ' ... this can take a few seconds.');
  try {
    const res = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ target }) });
    const json = await res.json();
    if (json.ok) setStatus('Completed ' + target + '.');
    else setStatus(target + ' failed: ' + (json.log_tail || []).slice(-2).join(' | '));
    await loadData();
  } catch (e) {
    setStatus('Request failed: ' + e);
  } finally {
    button.disabled = false;
    button.textContent = original;
  }
}

document.getElementById('run-all-btn').addEventListener('click', e => runTarget('all', e.target));
document.getElementById('refresh-btn').addEventListener('click', async e => {
  e.target.disabled = true;
  setStatus('Refreshing...');
  await loadData();
  setStatus('Refreshed.');
  e.target.disabled = false;
});

const navLinks = [...document.querySelectorAll('nav a[data-section]')];
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinks.forEach(a => a.classList.toggle('active', a.dataset.section === entry.target.id));
    }
  });
}, { rootMargin: '-20% 0px -70% 0px' });
document.querySelectorAll('main section').forEach(s => observer.observe(s));

loadData().then(() => setStatus('Ready.')).catch(e => setStatus('Failed to load data: ' + e));
</script>
</body></html>
"""

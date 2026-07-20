(function () {
  "use strict";

  const DATA = window.DASHBOARD_DATA;
  const SVG_NS = "http://www.w3.org/2000/svg";

  // ---------- small helpers ----------

  function el(tag, attrs, children) {
    const node = document.createElementNS(SVG_NS, tag);
    if (attrs) {
      for (const k in attrs) node.setAttribute(k, attrs[k]);
    }
    if (children) {
      children.forEach((c) => c && node.appendChild(c));
    }
    return node;
  }

  function fmtNum(n, digits) {
    return Number(n).toLocaleString("en-US", {
      minimumFractionDigits: digits || 0,
      maximumFractionDigits: digits || 0,
    });
  }

  // linear RGB lerp between two hex colors
  function hexToRgb(hex) {
    const v = hex.replace("#", "");
    return [
      parseInt(v.substring(0, 2), 16),
      parseInt(v.substring(2, 4), 16),
      parseInt(v.substring(4, 6), 16),
    ];
  }

  function lerpColor(hexA, hexB, t) {
    const a = hexToRgb(hexA);
    const b = hexToRgb(hexB);
    const rgb = a.map((v, i) => Math.round(v + (b[i] - v) * t));
    return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
  }

  // sequential blue ramp, anchor flipped for dark surface:
  // low value -> dark step (recedes toward the dark surface), high value -> light step (pops)
  const SEQ_DARK_LOW = "#184f95";
  const SEQ_LIGHT_HIGH = "#cde2fb";

  function riskFill(t) {
    return lerpColor(SEQ_DARK_LOW, SEQ_LIGHT_HIGH, t);
  }

  function riskTextColor(t) {
    // once the fill gets light (t > ~0.55) switch to dark text for contrast
    return t > 0.55 ? "#0b0b0b" : "#ffffff";
  }

  // ---------- tooltip ----------

  const tooltipEl = document.getElementById("tooltip");

  function showTooltip(evt, title, rows) {
    tooltipEl.innerHTML =
      `<div class="tt-title">${title}</div>` +
      rows
        .map(
          (r) => `<div class="tt-row"><span>${r[0]}</span><b>${r[1]}</b></div>`
        )
        .join("");
    tooltipEl.classList.add("visible");
    moveTooltip(evt);
  }

  function moveTooltip(evt) {
    const pad = 16;
    let x = evt.clientX + pad;
    let y = evt.clientY + pad;
    const rect = tooltipEl.getBoundingClientRect();
    if (x + rect.width > window.innerWidth - 8) x = evt.clientX - rect.width - pad;
    if (y + rect.height > window.innerHeight - 8) y = evt.clientY - rect.height - pad;
    tooltipEl.style.left = x + "px";
    tooltipEl.style.top = y + "px";
  }

  function hideTooltip() {
    tooltipEl.classList.remove("visible");
  }

  function bindTooltip(node, title, rows) {
    node.addEventListener("mouseenter", (e) => showTooltip(e, title, rows));
    node.addEventListener("mousemove", moveTooltip);
    node.addEventListener("mouseleave", hideTooltip);
  }

  // ---------- header meta + KPI tiles ----------

  function renderHeroMeta() {
    const o = DATA.overall;
    document.getElementById("hero-meta").innerHTML = `
      <span><b>${fmtNum(o.totalOrders)}</b> orders analyzed</span>
      <span><b>${DATA.warehouses.length}</b> warehouses</span>
      <span><b>${DATA.workflows.length}</b> workflow stages</span>
      <span>Generated <b>${DATA.generatedAt}</b></span>
    `;
  }

  function renderKpis() {
    const o = DATA.overall;
    const risk = DATA.insights.riskiestCombo;
    const tiles = [
      {
        label: "Avg. preparation time",
        value: `${fmtNum(o.avgPrepTimeMin, 1)} min`,
        caption: "Target: under 20 min",
        cls: o.avgPrepTimeMin <= 20 ? "good" : "critical",
      },
      {
        label: "Packing accuracy",
        value: `${fmtNum(o.avgPackingAccuracyPct, 1)}%`,
        caption: "Target: 98%+",
        cls: o.avgPackingAccuracyPct >= 95 ? "good" : "critical",
      },
      {
        label: "Complaint rate",
        value: `${fmtNum(o.complaintRatePerOrder, 2)} / order`,
        caption: "Target: under 0.5",
        cls: o.complaintRatePerOrder <= 0.5 ? "good" : "critical",
      },
      {
        label: "Highest-risk combination",
        value: `${risk.warehouse} · ${risk.workflow}`,
        caption: `${fmtNum(risk.failureRiskPct, 1)}% failure risk`,
        cls: "critical",
      },
    ];

    document.getElementById("kpi-grid").innerHTML = tiles
      .map(
        (t) => `
      <div class="kpi-tile">
        <div class="kpi-label">${t.label}</div>
        <div class="kpi-value">${t.value}</div>
        <div class="kpi-caption ${t.cls || ""}">${t.caption}</div>
      </div>`
      )
      .join("");
  }

  function renderInsights() {
    const r = DATA.insights.riskiestCombo;
    const s = DATA.insights.safestCombo;
    document.getElementById("insight-grid").innerHTML = `
      <div class="insight-card risk">
        <div class="insight-tag risk"><span class="insight-dot risk"></span>Highest failure risk</div>
        <div class="insight-combo">${r.warehouse} &middot; ${r.workflow}</div>
        <div class="insight-stats">
          <span><b>${fmtNum(r.failureRiskPct, 1)}%</b> failure risk</span>
          <span><b>${fmtNum(r.avgPackingAccuracyPct, 1)}%</b> accuracy</span>
          <span><b>${fmtNum(r.complaintRatePerOrder, 2)}</b> complaints/order</span>
          <span><b>${fmtNum(r.avgPrepTimeMin, 1)}</b> min prep</span>
        </div>
      </div>
      <div class="insight-card safe">
        <div class="insight-tag safe"><span class="insight-dot safe"></span>Best-practice benchmark</div>
        <div class="insight-combo">${s.warehouse} &middot; ${s.workflow}</div>
        <div class="insight-stats">
          <span><b>${fmtNum(s.failureRiskPct, 1)}%</b> failure risk</span>
          <span><b>${fmtNum(s.avgPackingAccuracyPct, 1)}%</b> accuracy</span>
          <span><b>${fmtNum(s.complaintRatePerOrder, 2)}</b> complaints/order</span>
          <span><b>${fmtNum(s.avgPrepTimeMin, 1)}</b> min prep</span>
        </div>
      </div>
    `;
  }

  // ---------- generic small-multiple bar chart (by workflow) ----------

  function renderWorkflowBar(containerId, valueKey, opts) {
    const data = DATA.byWorkflow.slice().sort((a, b) => b[valueKey] - a[valueKey]);
    const W = 420, H = 240;
    const marginL = 40, marginR = 12, marginT = 14, marginB = 40;
    const plotW = W - marginL - marginR;
    const plotH = H - marginT - marginB;
    const dataMax = Math.max(...data.map((d) => d[valueKey]), opts.target || 0);
    const maxVal = dataMax * 1.2;
    const barSlot = plotW / data.length;
    const barW = Math.min(56, barSlot * 0.5);

    const svg = el("svg", { class: "chart", viewBox: `0 0 ${W} ${H}` });

    svg.appendChild(
      el("line", { x1: marginL, x2: W - marginR, y1: marginT + plotH, y2: marginT + plotH, class: "baseline" })
    );

    if (opts.target != null) {
      const ty = marginT + plotH - (opts.target / maxVal) * plotH;
      svg.appendChild(el("line", { x1: marginL, x2: W - marginR, y1: ty, y2: ty, class: "target-line" }));
    }

    data.forEach((d, i) => {
      const val = d[valueKey];
      const x = marginL + i * barSlot + (barSlot - barW) / 2;
      const barH = Math.max(2, (val / maxVal) * plotH);
      const y = marginT + plotH - barH;

      const bar = el("rect", { x, y, width: barW, height: barH, rx: 5, fill: "var(--series-blue)" });
      bindTooltip(bar, d.workflow_type, [
        [opts.label, fmtNum(val, opts.digits)],
        ["Orders", fmtNum(d.orders)],
        ["Health score", fmtNum(d.avgWarehouseHealthScore, 1)],
      ]);
      svg.appendChild(bar);

      const label = document.createElementNS(SVG_NS, "text");
      label.setAttribute("x", x + barW / 2);
      label.setAttribute("y", H - marginB + 18);
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("class", "axis-label");
      label.textContent = d.workflow_type;
      svg.appendChild(label);

      const valueLabel = document.createElementNS(SVG_NS, "text");
      valueLabel.setAttribute("x", x + barW / 2);
      valueLabel.setAttribute("y", y - 8);
      valueLabel.setAttribute("text-anchor", "middle");
      valueLabel.setAttribute("class", "axis-label");
      valueLabel.setAttribute("fill", "var(--text-secondary)");
      valueLabel.textContent = fmtNum(val, opts.digits);
      svg.appendChild(valueLabel);
    });

    document.getElementById(containerId).appendChild(svg);
  }

  // rank-based status color: worst = critical, middle = warning, best = good
  function rankColor(index, total) {
    const t = total <= 1 ? 0 : index / (total - 1);
    if (t < 0.34) return "var(--critical)";
    if (t < 0.67) return "var(--warning)";
    return "var(--good)";
  }

  // ---------- horizontal ranking bar (risk ranking) ----------

  function renderRankingBar(containerId, data, opts) {
    const rows = data.slice().sort((a, b) => b[opts.valueKey] - a[opts.valueKey]);
    const W = 460;
    const rowH = 34;
    const marginL = 8, marginR = 54, marginT = 4, marginB = 4;
    const labelW = 110;
    const H = marginT + marginB + rowH * rows.length;
    const plotW = W - marginL - marginR - labelW;
    const maxVal = Math.max(...rows.map((r) => r[opts.valueKey])) * 1.08;

    const svg = el("svg", { class: "chart", viewBox: `0 0 ${W} ${H}` });

    rows.forEach((r, i) => {
      const y = marginT + i * rowH;
      const barH = 16;
      const barY = y + (rowH - barH) / 2;
      const barW = Math.max(2, (r[opts.valueKey] / maxVal) * plotW);
      const color = rankColor(i, rows.length);

      const label = document.createElementNS(SVG_NS, "text");
      label.setAttribute("x", marginL + labelW - 8);
      label.setAttribute("y", y + rowH / 2 + 4);
      label.setAttribute("text-anchor", "end");
      label.setAttribute("class", "axis-label");
      label.textContent = opts.labelFn(r);
      svg.appendChild(label);

      const track = el("rect", {
        x: marginL + labelW, y: barY, width: plotW, height: barH, rx: 4,
        fill: "var(--gridline)",
      });
      svg.appendChild(track);

      const bar = el("rect", {
        x: marginL + labelW, y: barY, width: barW, height: barH, rx: 4, fill: color,
      });
      bindTooltip(bar, opts.labelFn(r), opts.tooltipFn(r));
      svg.appendChild(bar);

      const valueLabel = document.createElementNS(SVG_NS, "text");
      valueLabel.setAttribute("x", marginL + labelW + barW + 8);
      valueLabel.setAttribute("y", y + rowH / 2 + 4);
      valueLabel.setAttribute("class", "axis-label");
      valueLabel.setAttribute("fill", "var(--text-secondary)");
      valueLabel.textContent = opts.valueFn(r);
      svg.appendChild(valueLabel);
    });

    document.getElementById(containerId).appendChild(svg);
  }

  // ---------- donut chart (complaint share) ----------

  function renderDonut(containerId, data, opts) {
    const rows = data.slice().sort((a, b) => b[opts.valueKey] - a[opts.valueKey]);
    const total = rows.reduce((s, r) => s + r[opts.valueKey], 0);
    const colors = ["var(--series-blue)", "var(--series-violet)", "var(--series-magenta)", "var(--series-yellow)", "var(--series-green)"];

    const size = 200, cx = 100, cy = 100, rOuter = 88, rInner = 52;
    const svg = el("svg", { class: "chart", viewBox: `0 0 ${size} ${size}` });

    let angle = -Math.PI / 2;
    const legendItems = [];

    rows.forEach((r, i) => {
      const value = r[opts.valueKey];
      const frac = total > 0 ? value / total : 0;
      const sweep = frac * 2 * Math.PI;
      const nextAngle = angle + sweep;
      const color = colors[i % colors.length];

      const x1 = cx + rOuter * Math.cos(angle);
      const y1 = cy + rOuter * Math.sin(angle);
      const x2 = cx + rOuter * Math.cos(nextAngle);
      const y2 = cy + rOuter * Math.sin(nextAngle);
      const ix1 = cx + rInner * Math.cos(nextAngle);
      const iy1 = cy + rInner * Math.sin(nextAngle);
      const ix2 = cx + rInner * Math.cos(angle);
      const iy2 = cy + rInner * Math.sin(angle);
      const largeArc = sweep > Math.PI ? 1 : 0;

      const d = [
        `M ${x1} ${y1}`,
        `A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2} ${y2}`,
        `L ${ix1} ${iy1}`,
        `A ${rInner} ${rInner} 0 ${largeArc} 0 ${ix2} ${iy2}`,
        "Z",
      ].join(" ");

      const slice = el("path", { d, fill: color, stroke: "var(--surface-1)", "stroke-width": 2 });
      bindTooltip(slice, opts.labelFn(r), [
        [opts.valueLabel || "Value", fmtNum(value, opts.digits || 0)],
        ["Share", fmtNum(frac * 100, 1) + "%"],
      ]);
      svg.appendChild(slice);

      legendItems.push({ color, label: opts.labelFn(r), pct: fmtNum(frac * 100, 1) + "%" });
      angle = nextAngle;
    });

    document.getElementById(containerId).appendChild(svg);

    if (opts.legendId) {
      document.getElementById(opts.legendId).innerHTML = legendItems
        .map(
          (li) =>
            `<span class="legend-item"><span class="legend-swatch" style="background:${li.color}"></span>${li.label} — ${li.pct}</span>`
        )
        .join("");
    }
  }

  // ---------- failure risk heatmap ----------

  function renderMatrixHeatmap() {
    const warehouses = DATA.warehouses;
    const workflows = DATA.workflows;
    const byKey = {};
    DATA.matrix.forEach((m) => {
      byKey[m.warehouse_id + "|" + m.workflow_type] = m;
    });

    const W = 900;
    const marginL = 64, marginR = 16, marginT = 34, marginB = 10;
    const rowH = 56;
    const H = marginT + marginB + rowH * warehouses.length;
    const plotW = W - marginL - marginR;
    const colW = plotW / workflows.length;

    const riskValues = DATA.matrix.map((m) => m.failureRiskPct);
    const riskMin = Math.min(...riskValues);
    const riskMax = Math.max(...riskValues);
    const riskSpan = riskMax - riskMin || 1;
    const scaleT = (risk) => (risk - riskMin) / riskSpan;

    const svg = el("svg", { class: "chart", viewBox: `0 0 ${W} ${H}` });

    workflows.forEach((wf, c) => {
      const label = document.createElementNS(SVG_NS, "text");
      label.setAttribute("x", marginL + c * colW + colW / 2);
      label.setAttribute("y", marginT - 12);
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("class", "axis-label");
      label.textContent = wf;
      svg.appendChild(label);
    });

    warehouses.forEach((wh, r) => {
      const label = document.createElementNS(SVG_NS, "text");
      label.setAttribute("x", marginL - 12);
      label.setAttribute("y", marginT + r * rowH + rowH / 2 + 4);
      label.setAttribute("text-anchor", "end");
      label.setAttribute("class", "axis-label");
      label.textContent = wh;
      svg.appendChild(label);

      workflows.forEach((wf, c) => {
        const cellData = byKey[wh + "|" + wf];
        const risk = cellData.failureRiskPct;
        const t = scaleT(risk);
        const x = marginL + c * colW;
        const y = marginT + r * rowH;

        const rect = el("rect", {
          x: x + 3, y: y + 3, width: colW - 6, height: rowH - 6,
          class: "heat-cell", fill: riskFill(t),
        });
        bindTooltip(rect, `${wh} · ${wf}`, [
          ["Failure risk", fmtNum(risk, 1) + "%"],
          ["Health score", fmtNum(cellData.avgWarehouseHealthScore, 1)],
          ["Orders", fmtNum(cellData.orders)],
          ["Avg prep time", fmtNum(cellData.avgPrepTimeMin, 1) + " min"],
          ["Accuracy", fmtNum(cellData.avgPackingAccuracyPct, 1) + "%"],
          ["Complaints/order", fmtNum(cellData.complaintRatePerOrder, 2)],
        ]);
        svg.appendChild(rect);

        const label = document.createElementNS(SVG_NS, "text");
        label.setAttribute("x", x + colW / 2);
        label.setAttribute("y", y + rowH / 2);
        label.setAttribute("class", "heat-label");
        label.setAttribute("fill", riskTextColor(t));
        label.textContent = fmtNum(risk, 0) + "%";
        svg.appendChild(label);
      });
    });

    document.getElementById("chart-matrix").appendChild(svg);

    // gradient legend
    const legendWrap = document.getElementById("legend-matrix");
    const steps = 24;
    let gradientHtml = "";
    for (let i = 0; i < steps; i++) {
      gradientHtml += riskFill(i / (steps - 1)) + (i < steps - 1 ? "," : "");
    }
    legendWrap.innerHTML = `
      <span class="legend-item">Lower risk (${fmtNum(riskMin, 1)}%)</span>
      <span style="width:160px;height:10px;border-radius:4px;background:linear-gradient(90deg, ${gradientHtml});display:inline-block;"></span>
      <span class="legend-item">Higher risk (${fmtNum(riskMax, 1)}%)</span>
    `;

    // table view
    const tbody = document.querySelector("#table-matrix tbody");
    tbody.innerHTML = DATA.matrix
      .slice()
      .sort((a, b) => b.failureRiskPct - a.failureRiskPct)
      .map(
        (m) => `<tr>
          <td>${m.warehouse_id}</td>
          <td>${m.workflow_type}</td>
          <td>${fmtNum(m.orders)}</td>
          <td>${fmtNum(m.avgPrepTimeMin, 1)}</td>
          <td>${fmtNum(m.avgPackingAccuracyPct, 1)}</td>
          <td>${fmtNum(m.complaintRatePerOrder, 2)}</td>
          <td>${fmtNum(m.failureRiskPct, 1)}</td>
        </tr>`
      )
      .join("");

    document.getElementById("toggle-matrix-table").addEventListener("click", (e) => {
      const chart = document.getElementById("chart-matrix");
      const table = document.getElementById("table-matrix");
      const showingTable = !table.classList.contains("hidden");
      table.classList.toggle("hidden", showingTable);
      chart.classList.toggle("hidden", !showingTable);
      e.target.textContent = showingTable ? "View as table" : "View as chart";
    });
  }

  // ---------- warehouse detail page ----------

  function getQueryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  function renderWarehouseDetail() {
    const current = DATA.warehouses.includes(getQueryParam("id"))
      ? getQueryParam("id")
      : DATA.warehouses[0];

    document.getElementById("warehouse-tabs").innerHTML = DATA.warehouses
      .map(
        (w) =>
          `<a href="warehouse.html?id=${w}" class="wh-tab${w === current ? " active" : ""}">${w}</a>`
      )
      .join("");

    const wh = DATA.byWarehouse.find((w) => w.warehouse_id === current);
    const rows = DATA.matrix
      .filter((m) => m.warehouse_id === current)
      .sort((a, b) => b.failureRiskPct - a.failureRiskPct);

    document.getElementById("warehouse-heading").textContent = `${current} — Warehouse Detail`;

    const tiles = [
      { label: "Orders", value: fmtNum(wh.orders) },
      { label: "Avg prep time", value: `${fmtNum(wh.avgPrepTimeMin, 1)} min` },
      { label: "Packing accuracy", value: `${fmtNum(wh.avgPackingAccuracyPct, 1)}%` },
      { label: "Complaint rate", value: `${fmtNum(wh.complaintRatePerOrder, 2)}/order` },
      { label: "Health score", value: fmtNum(wh.avgWarehouseHealthScore, 1) },
    ];
    document.getElementById("warehouse-kpis").innerHTML = tiles
      .map(
        (t) => `
      <div class="kpi-tile">
        <div class="kpi-label">${t.label}</div>
        <div class="kpi-value">${t.value}</div>
      </div>`
      )
      .join("");

    const tbody = document.querySelector("#warehouse-workflow-table tbody");
    tbody.innerHTML = rows
      .map(
        (r) => `<tr>
          <td>${r.workflow_type}</td>
          <td>${fmtNum(r.orders)}</td>
          <td>${fmtNum(r.avgPrepTimeMin, 1)}</td>
          <td>${fmtNum(r.avgPackingAccuracyPct, 1)}</td>
          <td>${fmtNum(r.complaintRatePerOrder, 2)}</td>
          <td>${fmtNum(r.failureRiskPct, 1)}</td>
        </tr>`
      )
      .join("");

    const o = DATA.overall;
    const diff = wh.avgWarehouseHealthScore - o.avgWarehouseHealthScore;
    document.getElementById("warehouse-comparison").innerHTML =
      `<b>${current}</b>'s health score is <b>${fmtNum(Math.abs(diff), 1)}</b> points ` +
      `${diff >= 0 ? "above" : "below"} the fleet average of <b>${fmtNum(o.avgWarehouseHealthScore, 1)}</b>. ` +
      `Its riskiest workflow here is <b>${rows[0].workflow_type}</b> at ${fmtNum(rows[0].failureRiskPct, 1)}% failure risk.`;
  }

  // ---------- workflow comparison page ----------

  function renderWorkflowComparison() {
    const rows = DATA.byWorkflow
      .map((w) => ({ ...w, failureRiskPct: Math.round((100 - w.avgWarehouseHealthScore) * 10) / 10 }))
      .sort((a, b) => b.failureRiskPct - a.failureRiskPct);

    const tbody = document.querySelector("#workflow-comparison-table tbody");
    tbody.innerHTML = rows
      .map((r, i) => {
        const badgeClass = i === 0 ? "critical" : i === rows.length - 1 ? "good" : "warning";
        return `<tr>
          <td><a href="workflow.html?wf=${encodeURIComponent(r.workflow_type)}">${r.workflow_type}</a></td>
          <td>${fmtNum(r.orders)}</td>
          <td>${fmtNum(r.avgPrepTimeMin, 1)}</td>
          <td>${fmtNum(r.avgPackingAccuracyPct, 1)}</td>
          <td>${fmtNum(r.complaintRatePerOrder, 2)}</td>
          <td><span class="risk-badge ${badgeClass}">${fmtNum(r.failureRiskPct, 1)}%</span></td>
        </tr>`;
      })
      .join("");

    renderRankingBar("chart-workflow-ranking", rows, {
      valueKey: "failureRiskPct",
      labelFn: (r) => r.workflow_type,
      valueFn: (r) => fmtNum(r.failureRiskPct, 1) + "%",
      tooltipFn: (r) => [
        ["Failure risk", fmtNum(r.failureRiskPct, 1) + "%"],
        ["Accuracy", fmtNum(r.avgPackingAccuracyPct, 1) + "%"],
        ["Complaints/order", fmtNum(r.complaintRatePerOrder, 2)],
      ],
    });
  }

  // ---------- workflow detail page ----------

  function renderWorkflowDetail() {
    const current = DATA.workflows.includes(getQueryParam("wf"))
      ? getQueryParam("wf")
      : DATA.workflows[0];

    document.getElementById("workflow-tabs").innerHTML = DATA.workflows
      .map(
        (w) =>
          `<a href="workflow.html?wf=${encodeURIComponent(w)}" class="wh-tab${w === current ? " active" : ""}">${w}</a>`
      )
      .join("");

    const wf = DATA.byWorkflow.find((w) => w.workflow_type === current);
    const failureRisk = Math.round((100 - wf.avgWarehouseHealthScore) * 10) / 10;
    const rows = DATA.matrix
      .filter((m) => m.workflow_type === current)
      .sort((a, b) => b.failureRiskPct - a.failureRiskPct);

    document.getElementById("workflow-heading").textContent = `${current} — Workflow Detail`;

    const riskLabel = failureRisk >= 40 ? "High Risk" : failureRisk >= 33 ? "Medium Risk" : "Low Risk";
    const riskClass = failureRisk >= 40 ? "critical" : failureRisk >= 33 ? "warning" : "good";
    document.getElementById("workflow-risk-badge").innerHTML =
      `<span class="risk-badge ${riskClass}">${riskLabel}</span>`;

    const tiles = [
      { label: "Orders", value: fmtNum(wf.orders) },
      { label: "Avg prep time", value: `${fmtNum(wf.avgPrepTimeMin, 1)} min` },
      { label: "Packing accuracy", value: `${fmtNum(wf.avgPackingAccuracyPct, 1)}%` },
      { label: "Complaint rate", value: `${fmtNum(wf.complaintRatePerOrder, 2)}/order` },
      { label: "Failure risk", value: `${fmtNum(failureRisk, 1)}%` },
    ];
    document.getElementById("workflow-kpis").innerHTML = tiles
      .map(
        (t) => `
      <div class="kpi-tile">
        <div class="kpi-label">${t.label}</div>
        <div class="kpi-value">${t.value}</div>
      </div>`
      )
      .join("");

    const tbody = document.querySelector("#workflow-warehouse-table tbody");
    tbody.innerHTML = rows
      .map(
        (r) => `<tr>
          <td>${r.warehouse_id}</td>
          <td>${fmtNum(r.orders)}</td>
          <td>${fmtNum(r.avgPrepTimeMin, 1)}</td>
          <td>${fmtNum(r.avgPackingAccuracyPct, 1)}</td>
          <td>${fmtNum(r.complaintRatePerOrder, 2)}</td>
          <td>${fmtNum(r.failureRiskPct, 1)}</td>
        </tr>`
      )
      .join("");

    document.getElementById("workflow-comparison-note").innerHTML =
      `Across warehouses, <b>${current}</b> is riskiest at <b>${rows[0].warehouse_id}</b> ` +
      `(${fmtNum(rows[0].failureRiskPct, 1)}%) and safest at <b>${rows[rows.length - 1].warehouse_id}</b> ` +
      `(${fmtNum(rows[rows.length - 1].failureRiskPct, 1)}%).`;
  }

  // ---------- insights & actions page ----------

  function renderInsightsActions() {
    const risk = DATA.insights.riskiestCombo;
    const safe = DATA.insights.safestCombo;
    const worstWorkflow = DATA.byWorkflow
      .map((w) => ({ ...w, failureRiskPct: 100 - w.avgWarehouseHealthScore }))
      .sort((a, b) => b.failureRiskPct - a.failureRiskPct)[0];
    const worstWarehouse = DATA.byWarehouse.slice().sort((a, b) => a.avgWarehouseHealthScore - b.avgWarehouseHealthScore)[0];

    const actions = [
      {
        icon: "warning",
        title: `Investigate ${risk.warehouse} · ${risk.workflow} first`,
        detail: `Highest failure risk in the whole matrix at ${fmtNum(risk.failureRiskPct, 1)}% — ${fmtNum(risk.complaintRatePerOrder, 2)} complaints/order and ${fmtNum(risk.avgPrepTimeMin, 1)} min average prep time.`,
        link: "failure-risk.html",
        linkLabel: "View heatmap",
      },
      {
        icon: "warning",
        title: `Review the ${worstWorkflow.workflow_type} workflow itself`,
        detail: `${worstWorkflow.workflow_type} has the highest failure risk averaged across all five warehouses (${fmtNum(worstWorkflow.failureRiskPct, 1)}%) — this points at the process, not one site.`,
        link: `workflow.html?wf=${encodeURIComponent(worstWorkflow.workflow_type)}`,
        linkLabel: "View workflow detail",
      },
      {
        icon: "critical",
        title: `Schedule a quality audit at ${worstWarehouse.warehouse_id}`,
        detail: `Lowest warehouse health score in the fleet (${fmtNum(worstWarehouse.avgWarehouseHealthScore, 1)}) — below the ${fmtNum(DATA.overall.avgWarehouseHealthScore, 1)} fleet average.`,
        link: `warehouse.html?id=${worstWarehouse.warehouse_id}`,
        linkLabel: "View warehouse detail",
      },
      {
        icon: "good",
        title: `Roll out ${safe.warehouse} · ${safe.workflow}'s process`,
        detail: `Best-practice benchmark at ${fmtNum(safe.failureRiskPct, 1)}% failure risk and ${fmtNum(safe.avgPackingAccuracyPct, 1)}% accuracy — the internal standard to copy elsewhere.`,
        link: "failure-risk.html",
        linkLabel: "View heatmap",
      },
    ];

    const iconSvg = {
      warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4"/><path d="M12 17h.01"/><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>',
      critical: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>',
      good: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>',
    };

    document.getElementById("actions-list").innerHTML = actions
      .map(
        (a) => `
      <div class="action-card">
        <div class="action-icon ${a.icon}">${iconSvg[a.icon]}</div>
        <div class="action-body">
          <div class="action-title">${a.title}</div>
          <div class="action-detail">${a.detail}</div>
        </div>
        <a class="action-link" href="${a.link}">${a.linkLabel} →</a>
      </div>`
      )
      .join("");
  }

  // ---------- overview dashboard: failure rate by warehouse (vertical, rank-colored) ----------

  function renderWarehouseRiskBars(containerId) {
    const rows = DATA.byWarehouse
      .map((w) => ({ ...w, failureRiskPct: Math.round((100 - w.avgWarehouseHealthScore) * 10) / 10 }))
      .sort((a, b) => b.failureRiskPct - a.failureRiskPct);

    const W = 460, H = 220;
    const marginL = 34, marginR = 8, marginT = 14, marginB = 34;
    const plotW = W - marginL - marginR;
    const plotH = H - marginT - marginB;
    const maxVal = Math.max(...rows.map((r) => r.failureRiskPct)) * 1.15;
    const barSlot = plotW / rows.length;
    const barW = Math.min(52, barSlot * 0.55);

    const svg = el("svg", { class: "chart", viewBox: `0 0 ${W} ${H}` });
    svg.appendChild(el("line", { x1: marginL, x2: W - marginR, y1: marginT + plotH, y2: marginT + plotH, class: "baseline" }));

    rows.forEach((r, i) => {
      const x = marginL + i * barSlot + (barSlot - barW) / 2;
      const barH = Math.max(2, (r.failureRiskPct / maxVal) * plotH);
      const y = marginT + plotH - barH;
      const color = rankColor(i, rows.length);

      const bar = el("rect", { x, y, width: barW, height: barH, rx: 5, fill: color });
      bindTooltip(bar, r.warehouse_id, [
        ["Failure risk", fmtNum(r.failureRiskPct, 1) + "%"],
        ["Health score", fmtNum(r.avgWarehouseHealthScore, 1)],
        ["Orders", fmtNum(r.orders)],
      ]);
      svg.appendChild(bar);

      const label = document.createElementNS(SVG_NS, "text");
      label.setAttribute("x", x + barW / 2);
      label.setAttribute("y", H - marginB + 18);
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("class", "axis-label");
      label.textContent = r.warehouse_id;
      svg.appendChild(label);

      const valueLabel = document.createElementNS(SVG_NS, "text");
      valueLabel.setAttribute("x", x + barW / 2);
      valueLabel.setAttribute("y", y - 8);
      valueLabel.setAttribute("text-anchor", "middle");
      valueLabel.setAttribute("class", "axis-label");
      valueLabel.setAttribute("fill", "var(--text-secondary)");
      valueLabel.textContent = fmtNum(r.failureRiskPct, 1) + "%";
      svg.appendChild(valueLabel);
    });

    document.getElementById(containerId).appendChild(svg);
  }

  // ---------- shared nav ----------

  function highlightActiveNav() {
    const path = window.location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".sidebar-nav a").forEach((a) => {
      const href = a.getAttribute("href").split("?")[0];
      if (href === path) a.classList.add("active");
    });
  }

  // ---------- boot ----------

  function init() {
    if (document.getElementById("hero-meta")) renderHeroMeta();
    if (document.getElementById("kpi-grid")) renderKpis();
    if (document.getElementById("insight-grid")) renderInsights();
    if (document.getElementById("chart-matrix")) renderMatrixHeatmap();
    if (document.getElementById("chart-prep-time"))
      renderWorkflowBar("chart-prep-time", "avgPrepTimeMin", { target: 20, label: "Avg prep time", digits: 1 });
    if (document.getElementById("chart-accuracy"))
      renderWorkflowBar("chart-accuracy", "avgPackingAccuracyPct", { target: 95, label: "Accuracy", digits: 1 });
    if (document.getElementById("chart-complaint-rate"))
      renderWorkflowBar("chart-complaint-rate", "complaintRatePerOrder", { target: 0.5, label: "Complaints/order", digits: 2 });
    if (document.getElementById("warehouse-tabs")) renderWarehouseDetail();
    if (document.getElementById("workflow-tabs")) renderWorkflowDetail();
    if (document.getElementById("workflow-comparison-table")) renderWorkflowComparison();
    if (document.getElementById("actions-list")) renderInsightsActions();
    if (document.getElementById("chart-risk-ranking"))
      renderRankingBar(
        "chart-risk-ranking",
        DATA.byWorkflow.map((w) => ({ ...w, failureRiskPct: Math.round((100 - w.avgWarehouseHealthScore) * 10) / 10 })),
        {
          valueKey: "failureRiskPct",
          labelFn: (r) => r.workflow_type,
          valueFn: (r) => fmtNum(r.failureRiskPct, 1) + "%",
          tooltipFn: (r) => [
            ["Failure risk", fmtNum(r.failureRiskPct, 1) + "%"],
            ["Accuracy", fmtNum(r.avgPackingAccuracyPct, 1) + "%"],
          ],
        }
      );
    if (document.getElementById("chart-warehouse-risk")) renderWarehouseRiskBars("chart-warehouse-risk");
    if (document.getElementById("chart-complaint-share"))
      renderDonut(
        "chart-complaint-share",
        DATA.byWorkflow.map((w) => ({ ...w, complaints: Math.round(w.complaintRatePerOrder * w.orders) })),
        { valueKey: "complaints", labelFn: (r) => r.workflow_type, valueLabel: "Complaints", legendId: "legend-complaint-share" }
      );
    if (document.getElementById("footer-date")) document.getElementById("footer-date").textContent = DATA.generatedAt;
    highlightActiveNav();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

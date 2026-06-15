from __future__ import annotations

from fastapi.responses import HTMLResponse


def render_dashboard() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lab Observability Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #667085;
      --line: #d8dee9;
      --blue: #2563eb;
      --green: #059669;
      --red: #dc2626;
      --amber: #d97706;
      --violet: #7c3aed;
      --teal: #0f766e;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 20px 24px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }

    h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.2;
      font-weight: 700;
    }

    .status {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: var(--green);
    }

    main {
      width: min(1360px, 100%);
      margin: 0 auto;
      padding: 24px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }

    .panel {
      min-height: 235px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }

    .panel-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }

    h2 {
      margin: 0;
      font-size: 15px;
      line-height: 1.35;
    }

    .unit {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }

    .metric-row {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .metric {
      min-width: 0;
      padding: 10px;
      border-radius: 6px;
      background: #f8fafc;
      border: 1px solid #e7ecf3;
    }

    .label {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
    }

    .value {
      margin-top: 6px;
      font-size: clamp(18px, 2vw, 28px);
      line-height: 1.05;
      font-weight: 750;
      overflow-wrap: anywhere;
    }

    .chart {
      width: 100%;
      height: 96px;
      display: block;
      border: 1px solid #eef2f7;
      border-radius: 6px;
      background: linear-gradient(#ffffff, #fbfcfe);
    }

    .bars {
      display: grid;
      gap: 10px;
    }

    .bar-row {
      display: grid;
      grid-template-columns: 82px minmax(0, 1fr) 64px;
      align-items: center;
      gap: 10px;
      font-size: 13px;
    }

    .track {
      height: 10px;
      border-radius: 999px;
      background: #edf2f7;
      overflow: hidden;
    }

    .fill {
      height: 100%;
      width: 0;
      border-radius: inherit;
      background: var(--blue);
      transition: width 180ms ease;
    }

    .wide {
      grid-column: span 2;
    }

    @media (max-width: 980px) {
      .grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .wide {
        grid-column: span 1;
      }
    }

    @media (max-width: 680px) {
      header {
        align-items: flex-start;
        flex-direction: column;
      }

      main {
        padding: 14px;
      }

      .grid {
        grid-template-columns: 1fr;
      }

      .metric-row {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>Lab Observability Dashboard</h1>
    <div class="status"><span class="dot" id="status-dot"></span><span id="updated-at">Waiting for metrics</span></div>
  </header>

  <main>
    <section class="grid" aria-label="Observability metrics">
      <article class="panel wide">
        <div class="panel-head">
          <h2>Latency P50 / P95 / P99</h2>
          <span class="unit">ms</span>
        </div>
        <div class="metric-row">
          <div class="metric"><div class="label">P50</div><div class="value" id="latency-p50">0</div></div>
          <div class="metric"><div class="label">P95</div><div class="value" id="latency-p95">0</div></div>
          <div class="metric"><div class="label">P99</div><div class="value" id="latency-p99">0</div></div>
        </div>
        <canvas class="chart" id="latency-chart" width="760" height="120"></canvas>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h2>Traffic</h2>
          <span class="unit">requests</span>
        </div>
        <div class="metric"><div class="label">Total</div><div class="value" id="traffic">0</div></div>
        <canvas class="chart" id="traffic-chart" width="360" height="120"></canvas>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h2>Error Rate</h2>
          <span class="unit">breakdown</span>
        </div>
        <div class="metric"><div class="label">Errors</div><div class="value" id="errors-total">0</div></div>
        <div class="bars" id="error-breakdown"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h2>Cost</h2>
          <span class="unit">USD</span>
        </div>
        <div class="metric-row">
          <div class="metric"><div class="label">Total</div><div class="value" id="total-cost">$0</div></div>
          <div class="metric"><div class="label">Average</div><div class="value" id="avg-cost">$0</div></div>
          <div class="metric"><div class="label">Budget</div><div class="value">$2.50</div></div>
        </div>
        <canvas class="chart" id="cost-chart" width="360" height="120"></canvas>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h2>Tokens In / Out</h2>
          <span class="unit">tokens</span>
        </div>
        <div class="bars">
          <div class="bar-row"><span>Input</span><div class="track"><div class="fill" id="tokens-in-bar"></div></div><strong id="tokens-in">0</strong></div>
          <div class="bar-row"><span>Output</span><div class="track"><div class="fill" id="tokens-out-bar"></div></div><strong id="tokens-out">0</strong></div>
        </div>
        <canvas class="chart" id="tokens-chart" width="360" height="120"></canvas>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h2>Quality Proxy</h2>
          <span class="unit">0-1 score</span>
        </div>
        <div class="metric"><div class="label">Average</div><div class="value" id="quality">0</div></div>
        <div class="bars">
          <div class="bar-row"><span>SLO</span><div class="track"><div class="fill" id="quality-bar"></div></div><strong>0.75</strong></div>
        </div>
      </article>
    </section>
  </main>

  <script>
    const history = [];
    const maxPoints = 24;

    const colors = {
      blue: "#2563eb",
      green: "#059669",
      red: "#dc2626",
      amber: "#d97706",
      violet: "#7c3aed",
      teal: "#0f766e",
      grid: "#e7ecf3"
    };

    function setText(id, value) {
      document.getElementById(id).textContent = value;
    }

    function money(value) {
      return `$${Number(value || 0).toFixed(4)}`;
    }

    function compact(value) {
      return Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(Number(value || 0));
    }

    function drawLine(canvasId, series, color, maxOverride) {
      const canvas = document.getElementById(canvasId);
      const ctx = canvas.getContext("2d");
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.strokeStyle = colors.grid;
      ctx.lineWidth = 1;
      for (let y = 24; y < h; y += 24) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }
      const values = series.map(Number);
      const max = Math.max(maxOverride || 0, ...values, 1);
      const step = values.length > 1 ? w / (values.length - 1) : w;
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.beginPath();
      values.forEach((value, index) => {
        const x = index * step;
        const y = h - (value / max) * (h - 14) - 7;
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    function drawDualLine(canvasId, first, second) {
      drawLine(canvasId, first, colors.teal);
      const canvas = document.getElementById(canvasId);
      const ctx = canvas.getContext("2d");
      const w = canvas.width;
      const h = canvas.height;
      const max = Math.max(...first, ...second, 1);
      const step = second.length > 1 ? w / (second.length - 1) : w;
      ctx.strokeStyle = colors.violet;
      ctx.lineWidth = 3;
      ctx.beginPath();
      second.forEach((value, index) => {
        const x = index * step;
        const y = h - (value / max) * (h - 14) - 7;
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    function renderErrors(errorBreakdown) {
      const target = document.getElementById("error-breakdown");
      const entries = Object.entries(errorBreakdown || {});
      const total = entries.reduce((sum, [, value]) => sum + Number(value || 0), 0);
      setText("errors-total", compact(total));
      if (!entries.length) {
        target.innerHTML = '<div class="bar-row"><span>None</span><div class="track"><div class="fill" style="width:0;background:var(--green)"></div></div><strong>0</strong></div>';
        return;
      }
      target.innerHTML = entries.map(([name, value]) => {
        const width = total ? Math.max(8, (Number(value) / total) * 100) : 0;
        return `<div class="bar-row"><span>${name}</span><div class="track"><div class="fill" style="width:${width}%;background:var(--red)"></div></div><strong>${value}</strong></div>`;
      }).join("");
    }

    function render(metrics) {
      history.push(metrics);
      if (history.length > maxPoints) history.shift();

      setText("latency-p50", Math.round(metrics.latency_p50 || 0));
      setText("latency-p95", Math.round(metrics.latency_p95 || 0));
      setText("latency-p99", Math.round(metrics.latency_p99 || 0));
      setText("traffic", compact(metrics.traffic));
      setText("total-cost", money(metrics.total_cost_usd));
      setText("avg-cost", money(metrics.avg_cost_usd));
      setText("tokens-in", compact(metrics.tokens_in_total));
      setText("tokens-out", compact(metrics.tokens_out_total));
      setText("quality", Number(metrics.quality_avg || 0).toFixed(2));

      const tokensMax = Math.max(metrics.tokens_in_total || 0, metrics.tokens_out_total || 0, 1);
      document.getElementById("tokens-in-bar").style.width = `${((metrics.tokens_in_total || 0) / tokensMax) * 100}%`;
      document.getElementById("tokens-out-bar").style.width = `${((metrics.tokens_out_total || 0) / tokensMax) * 100}%`;
      document.getElementById("tokens-out-bar").style.background = "var(--violet)";
      document.getElementById("quality-bar").style.width = `${Math.min(100, (metrics.quality_avg || 0) * 100)}%`;
      document.getElementById("quality-bar").style.background = (metrics.quality_avg || 0) >= 0.75 ? "var(--green)" : "var(--amber)";

      renderErrors(metrics.error_breakdown);
      drawLine("latency-chart", history.map(item => item.latency_p95 || 0), colors.blue, 3000);
      drawLine("traffic-chart", history.map(item => item.traffic || 0), colors.green);
      drawLine("cost-chart", history.map(item => item.total_cost_usd || 0), colors.amber, 2.5);
      drawDualLine("tokens-chart", history.map(item => item.tokens_in_total || 0), history.map(item => item.tokens_out_total || 0));
    }

    async function refresh() {
      try {
        const response = await fetch("/metrics", { cache: "no-store" });
        const metrics = await response.json();
        render(metrics);
        document.getElementById("status-dot").style.background = "var(--green)";
        setText("updated-at", `Updated ${new Date().toLocaleTimeString()}`);
      } catch (error) {
        document.getElementById("status-dot").style.background = "var(--red)";
        setText("updated-at", "Metrics unavailable");
      }
    }

    refresh();
    setInterval(refresh, 15000);
  </script>
</body>
</html>
        """
    )

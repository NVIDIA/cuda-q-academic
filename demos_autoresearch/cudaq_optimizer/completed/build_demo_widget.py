"""Build a polished, dependency-free NVIDIA-style interactive 3D widget."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from summarize_results import winner

ROOT = Path(__file__).resolve().parent
CASE = "qaoa_depth15"
CASE_DIR = ROOT / "research" / CASE
OUTPUT = ROOT / "energy_trajectories_3d.html"


def read_rows() -> list[dict[str, str]]:
    with (CASE_DIR / "results.tsv").open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_trace(round_number: int) -> dict:
    path = CASE_DIR / "traces" / f"round_{round_number:03d}.json"
    return json.loads(path.read_text())


def build_dataset() -> dict:
    rows = read_rows()
    reference = json.loads((ROOT / "reference.json").read_text())
    exact_energy = float(reference["cases"][CASE]["exact_energy"])
    rounds = []
    prefix = []
    for row in rows:
        prefix.append(row)
        round_number = int(row["round"])
        result = read_trace(round_number)
        valid = row["valid"] == "yes" and bool(row.get("best_energy"))
        energy = float(row["best_energy"]) if valid else None
        improved = bool(valid and winner(prefix) is row)
        points = [
            {
                "call": int(entry["call"]),
                "elapsed": float(entry["elapsed_s"]),
                "energy": float(entry["energy"]),
                "bestEnergy": float(entry["best_energy"]),
            }
            for entry in result.get("trace", [])
        ]
        rounds.append(
            {
                "round": round_number,
                "optimizer": row["optimizer_label"],
                "status": row["status"],
                "valid": valid,
                "converged": row["converged"] == "yes",
                "timeCap": row["time_cap_reached"] == "yes",
                "observeCap": row["status"] == "call_cap",
                "improved": improved,
                "calls": int(row["calls_used"]) if row["calls_used"] else 0,
                "elapsed": (
                    float(row["evaluator_elapsed_s"])
                    if row["evaluator_elapsed_s"]
                    else None
                ),
                "bestEnergy": energy,
                "acceptedIterations": (
                    int(row["accepted_iterations"])
                    if row["accepted_iterations"]
                    else 0
                ),
                "points": points,
            }
        )

    valid_rounds = [item for item in rounds if item["valid"]]
    winner_row = winner(rows)
    winning_item = next(
        item
        for item in valid_rounds
        if item["round"] == int(winner_row["round"])
    )
    winning_item["winner"] = True
    initial_energy = float(rows[0]["initial_energy"])
    energies = [item["bestEnergy"] for item in valid_rounds]
    return {
        "case": CASE,
        "callBudget": 300,
        "timeGuard": 120,
        "parameterCount": 30,
        "layerCount": 15,
        "target": reference["target"],
        "targetOption": reference.get("target_option"),
        "energyTieTolerance": 1.0e-6,
        "winnerRound": winning_item["round"],
        "winnerEnergy": winning_item["bestEnergy"],
        "exactEnergy": exact_energy,
        "winnerExactGap": winning_item["bestEnergy"] - exact_energy,
        "initialEnergy": initial_energy,
        "energyMin": min([exact_energy, *energies]),
        "energyMax": max([initial_energy, *energies]),
        "rounds": rounds,
    }


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CUDA-Q Depth-15 Optimizer Autoresearch</title>
  <style>
    :root {
      color-scheme: dark;
      --nv-green: #76b900;
      --nv-lime: #b4e61d;
      --black: #050505;
      --panel: #101114;
      --panel-2: #17191d;
      --line: #2b2e34;
      --text: #f7f7f7;
      --muted: #a3a7ae;
      --gray: #747982;
      --warn: #ffb000;
      --nv-purple: #a855f7;
      --bad: #ef5350;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; }
    body {
      background:
        radial-gradient(circle at 15% -15%, rgba(118,185,0,.18), transparent 38%),
        linear-gradient(135deg, #070807 0%, #0c0d10 55%, #050505 100%);
      color: var(--text);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, sans-serif;
    }
    .app { display: grid; grid-template-columns: minmax(0, 1fr) 390px; height: 100%; }
    .stage { position: relative; min-width: 0; overflow: hidden; }
    .stage::before {
      content: ""; position: absolute; inset: 0; pointer-events: none;
      background-image:
        linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
      background-size: 28px 28px;
    }
    canvas {
      display: block; width: 100%; height: 100%; cursor: grab;
      touch-action: none; outline: none;
    }
    canvas:focus-visible { box-shadow: inset 0 0 0 2px var(--nv-green); }
    canvas.dragging { cursor: grabbing; }
    .brand {
      position: absolute; left: 24px; top: 20px; pointer-events: none;
      display: flex; align-items: flex-start; gap: 13px;
    }
    .mark {
      width: 10px; height: 47px; border-radius: 2px; background: var(--nv-green);
      box-shadow: 0 0 22px rgba(118,185,0,.42);
    }
    .brand h1 { margin: 0; font-size: 21px; letter-spacing: .015em; }
    .brand p { margin: 3px 0 0; color: var(--muted); font-size: 12.5px; }
    .badge {
      display: inline-block; margin-top: 7px; padding: 3px 7px;
      border: 1px solid rgba(118,185,0,.55); border-radius: 999px;
      color: var(--nv-lime); background: rgba(118,185,0,.08);
      font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    }
    .controls {
      position: absolute; left: 22px; bottom: 20px; display: flex; gap: 8px;
      flex-wrap: wrap; max-width: calc(100% - 44px);
      padding: 9px; border: 1px solid var(--line); border-radius: 12px;
      background: rgba(12,13,16,.91); box-shadow: 0 12px 38px rgba(0,0,0,.38);
    }
    .control-label {
      align-self: center; color: var(--muted); padding: 0 2px 0 4px;
      font-size: 10px; letter-spacing: .08em; text-transform: uppercase;
    }
    button, select {
      border: 1px solid #34383f; border-radius: 8px; background: #17191d;
      color: var(--text); min-height: 36px; padding: 7px 11px; font: inherit;
      cursor: pointer;
    }
    button:hover, select:hover { border-color: var(--nv-green); }
    button.active { border-color: var(--nv-green); color: var(--nv-lime); }
    .orbit-panel {
      position: absolute; left: 24px; top: 100px; width: 270px;
      padding: 11px 13px; border: 1px solid var(--line); border-radius: 12px;
      background: rgba(12,13,16,.9); box-shadow: 0 12px 38px rgba(0,0,0,.3);
    }
    .orbit-row {
      display: grid; grid-template-columns: 42px 1fr 42px;
      align-items: center; gap: 8px; margin: 5px 0; color: var(--muted);
      font-size: 11px;
    }
    .orbit-row output { color: #dfe2e6; text-align: right; font-variant-numeric: tabular-nums; }
    .orbit-note {
      margin: 7px 1px 0; padding-top: 7px; border-top: 1px solid #292c31;
      color: #8f949c; font-size: 10.5px;
    }
    input[type="range"] { width: 100%; accent-color: var(--nv-green); cursor: pointer; }
    .pivot {
      position: absolute; left: 50%; top: 53%; width: 16px; height: 16px;
      transform: translate(-50%, -50%); border: 1px solid rgba(180,230,29,.45);
      border-radius: 50%; opacity: .24; pointer-events: none;
      transition: opacity .14s, transform .14s, box-shadow .14s;
    }
    .pivot::before, .pivot::after {
      content: ""; position: absolute; left: 50%; top: 50%;
      background: rgba(180,230,29,.8); transform: translate(-50%, -50%);
    }
    .pivot::before { width: 24px; height: 1px; }
    .pivot::after { width: 1px; height: 24px; }
    .stage.orbiting .pivot {
      opacity: 1; transform: translate(-50%, -50%) scale(1.14);
      box-shadow: 0 0 18px rgba(118,185,0,.48);
    }
    .hint {
      position: absolute; right: 18px; bottom: 18px; pointer-events: none;
      color: #81858c; text-align: right; font-size: 11.5px;
    }
    .tooltip {
      display: none; position: absolute; z-index: 10; width: 305px;
      padding: 11px 13px; border: 1px solid #3d424a; border-radius: 10px;
      background: rgba(10,11,13,.97); box-shadow: 0 14px 40px rgba(0,0,0,.55);
      pointer-events: none;
    }
    .tooltip strong { color: #fff; }
    .tooltip .green { color: var(--nv-lime); }
    .tooltip .muted { color: var(--muted); }
    aside {
      overflow: auto; padding: 20px; border-left: 1px solid var(--line);
      background: rgba(12,13,16,.97);
    }
    aside h2 { margin: 0 0 5px; font-size: 19px; }
    aside h3 {
      margin: 21px 0 9px; color: #dfe2e6; font-size: 11px;
      letter-spacing: .11em; text-transform: uppercase;
    }
    aside p { margin: 8px 0; color: #c8cbd0; }
    .callout {
      margin-top: 12px; padding: 11px 12px; border-left: 3px solid var(--nv-green);
      border-radius: 0 8px 8px 0; background: #171a15; color: #dfe7d4;
    }
    .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
    .metric {
      min-height: 69px; padding: 10px; border: 1px solid var(--line);
      border-radius: 9px; background: var(--panel-2);
    }
    .metric span { display: block; color: var(--muted); font-size: 10.5px; }
    .metric b { display: block; margin-top: 5px; font-size: 15px; }
    .legend { display: grid; gap: 7px; color: #c9ccd1; }
    .legend div { display: flex; align-items: center; gap: 9px; }
    .swatch { width: 24px; height: 3px; border-radius: 3px; }
    .shape-o, .shape-x {
      display: inline-flex; width: 18px; height: 18px; align-items: center;
      justify-content: center; color: var(--nv-green); font-weight: 800;
    }
    table { width: 100%; border-collapse: collapse; font-size: 11.5px; }
    th, td { padding: 6px 5px; border-bottom: 1px solid #25282d; text-align: right; }
    th:nth-child(2), td:nth-child(2) { text-align: left; }
    th {
      position: sticky; top: -20px; color: var(--muted); background: #0c0d10;
      z-index: 2;
    }
    tr { cursor: pointer; }
    tr:hover { background: #181b20; }
    tr.selected { background: rgba(118,185,0,.12); outline: 1px solid rgba(118,185,0,.35); }
    tr.new-best { color: var(--nv-lime); }
    tr.winner { color: var(--nv-green); font-weight: 700; }
    tr.invalid { color: var(--bad); }
    .status { font-size: 10px; text-transform: uppercase; letter-spacing: .05em; }
    @media (max-width: 920px) {
      .app { grid-template-columns: 1fr; grid-template-rows: 63vh 37vh; }
      aside { border-left: 0; border-top: 1px solid var(--line); }
      .hint { display: none; }
      .orbit-panel { width: 235px; top: 92px; }
      .controls { bottom: 10px; left: 10px; max-width: calc(100% - 20px); }
    }
  </style>
</head>
<body>
  <div class="app">
    <main class="stage" id="stage">
      <canvas id="plot" tabindex="0" aria-label="Interactive 3D energy trajectory plot"></canvas>
      <div class="pivot" aria-hidden="true"></div>
      <div class="brand">
        <div class="mark"></div>
        <div>
          <h1>CUDA-Q Depth-15 Optimizer Autoresearch</h1>
          <p>Round × counted observes × lowest observed energy</p>
          <span class="badge">CUDA-Q observe · NVIDIA FP64</span>
        </div>
      </div>
      <div class="orbit-panel" aria-label="Camera controls">
        <div class="orbit-row">
          <span>Yaw</span><input id="yaw" type="range" min="-180" max="180" value="-47">
          <output id="yawOut">-47°</output>
        </div>
        <div class="orbit-row">
          <span>Tilt</span><input id="pitch" type="range" min="-80" max="80" value="-24">
          <output id="pitchOut">-24°</output>
        </div>
        <div class="orbit-row">
          <span>Zoom</span><input id="zoom" type="range" min="55" max="210" value="100">
          <output id="zoomOut">100%</output>
        </div>
        <div class="orbit-note">Drag anywhere on the plot as a virtual trackball. The center cross is the fixed orbit pivot.</div>
      </div>
      <div class="controls">
        <span class="control-label">View</span>
        <button data-view="iso">Isometric</button>
        <button data-view="front">Front</button>
        <button data-view="top">Top</button>
        <button data-view="energy">Energy side</button>
        <button id="perspective">Perspective</button>
        <button id="reset">Reset view</button>
        <button id="rotate">Auto-rotate</button>
        <select id="filter" aria-label="Filter trajectories">
          <option value="all">All rounds</option>
          <option value="best">New-best rounds</option>
          <option value="converged">Converged</option>
          <option value="capped">Budget exhausted</option>
        </select>
        <select id="isolate" aria-label="Isolate one round">
          <option value="all">All rounds</option>
        </select>
      </div>
      <div class="hint">Drag like a trackball around the center cross · wheel to zoom<br>
        Arrow keys orbit · +/- zoom · double-click resets</div>
      <div class="tooltip" id="tooltip"></div>
    </main>
    <aside>
      <h2>Energy-first research</h2>
      <p>Each optimizer gets the same seeded 30-parameter start and exactly 300 counted-observe opportunities.</p>
      <div class="callout">
        Call 1 is the fixed initial point. The evaluator stops before call 301
        and preserves the best completed observation. Energies within 1e-6 use
        convergence or early completion, then elapsed time, as tie-breakers.
        The purple plane is the exact ground energy from brute-force enumeration
        of all 64 computational-basis assignments.
      </div>
      <h3>Study result</h3>
      <div class="metrics" id="metrics"></div>
      <p id="comparison"></p>
      <h3>Visual encoding</h3>
      <div class="legend">
        <div><span class="swatch" style="height:8px;background:rgba(168,85,247,.48);border:1px solid var(--nv-purple)"></span>Exact Hamiltonian ground-energy plane</div>
        <div><span class="swatch" style="background:var(--nv-green)"></span>Set a new study-best energy</div>
        <div><span class="swatch" style="background:var(--gray)"></span>Did not improve the study best</div>
        <div><span class="shape-o">●</span>Accepted-energy converged</div>
        <div><span class="shape-x">✕</span>Not converged / observe cap</div>
      </div>
      <h3>Round outcomes</h3>
      <table>
        <thead><tr><th>Round</th><th>Optimizer</th><th>Energy</th><th>Calls</th><th>Conv.</th></tr></thead>
        <tbody id="roundTable"></tbody>
      </table>
    </aside>
  </div>
  <script>
    "use strict";
    const study = __DATA__;
    const canvas = document.getElementById("plot");
    const stage = document.getElementById("stage");
    const tooltip = document.getElementById("tooltip");
    const ctx = canvas.getContext("2d");
    const state = {
      yaw: -.82, pitch: -.42, zoom: 1, perspective: false, dragging: false,
      orientation: null, dragStart: null, dragOrientation: null,
      auto: false, filter: "all", isolate: "all",
      width: 0, height: 0, projected: []
    };
    const color = {
      green: "#76b900", lime: "#b4e61d", gray: "#747982",
      grid: "rgba(132,138,146,.20)", axis: "#8d9299", text: "#c8cbd0",
      invalid: "#ef5350", exact: "#a855f7"
    };
    const energySpan = Math.max(.02, study.energyMax - study.energyMin);
    const energyLow = study.energyMin - energySpan * .05;
    const energyHigh = study.energyMax + energySpan * .08;
    const maxRound = Math.max(1, ...study.rounds.map(item => item.round));
    const fmtEnergy = value => value == null ? "—" : Number(value).toFixed(9);
    const escapeHtml = value => String(value)
      .replaceAll("&", "&amp;").replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;").replaceAll('"', "&quot;");

    function world(round, call, energy) {
      return {
        x: maxRound === 1 ? 0 : -2 + 4 * (round - 1) / (maxRound - 1),
        y: -1.55 + 3.1 * Math.min(study.callBudget, call) / study.callBudget,
        z: -1.55 + 3.1 * (energy - energyLow) / (energyHigh - energyLow)
      };
    }
    function multiplyQuaternion(a, b) {
      return [
        a[3]*b[0] + a[0]*b[3] + a[1]*b[2] - a[2]*b[1],
        a[3]*b[1] - a[0]*b[2] + a[1]*b[3] + a[2]*b[0],
        a[3]*b[2] + a[0]*b[1] - a[1]*b[0] + a[2]*b[3],
        a[3]*b[3] - a[0]*b[0] - a[1]*b[1] - a[2]*b[2]
      ];
    }
    function normalizeQuaternion(q) {
      const length = Math.hypot(q[0], q[1], q[2], q[3]) || 1;
      return q.map(value => value / length);
    }
    function axisAngle(x, y, z, angle) {
      const half = angle * .5, sine = Math.sin(half);
      return [x*sine, y*sine, z*sine, Math.cos(half)];
    }
    function quaternionFromEuler(yaw, pitch) {
      return normalizeQuaternion(multiplyQuaternion(
        axisAngle(1, 0, 0, pitch),
        axisAngle(0, 1, 0, yaw)
      ));
    }
    function rotateVector(p, q) {
      const tx = 2 * (q[1]*p.z - q[2]*p.y);
      const ty = 2 * (q[2]*p.x - q[0]*p.z);
      const tz = 2 * (q[0]*p.y - q[1]*p.x);
      return {
        x: p.x + q[3]*tx + (q[1]*tz - q[2]*ty),
        y: p.y + q[3]*ty + (q[2]*tx - q[0]*tz),
        z: p.z + q[3]*tz + (q[0]*ty - q[1]*tx)
      };
    }
    function quaternionBetween(a, b) {
      const cross = {
        x: a.y*b.z - a.z*b.y,
        y: a.z*b.x - a.x*b.z,
        z: a.x*b.y - a.y*b.x
      };
      const dot = a.x*b.x + a.y*b.y + a.z*b.z;
      if (dot < -.9999) {
        const axis = Math.abs(a.x) < .8
          ? {x: 0, y: -a.z, z: a.y}
          : {x: -a.y, y: a.x, z: 0};
        const length = Math.hypot(axis.x, axis.y, axis.z) || 1;
        return [axis.x/length, axis.y/length, axis.z/length, 0];
      }
      return normalizeQuaternion([cross.x, cross.y, cross.z, 1 + dot]);
    }
    function plotCenter() {
      return {x: state.width * .5, y: state.height * .53};
    }
    function arcballPoint(event) {
      const rect = canvas.getBoundingClientRect();
      const center = plotCenter();
      const radius = Math.max(80, Math.min(state.width, state.height) * .43);
      let x = (event.clientX - rect.left - center.x) / radius;
      let y = (center.y - (event.clientY - rect.top)) / radius;
      const squared = x*x + y*y;
      if (squared <= 1) return {x, y, z: Math.sqrt(1 - squared)};
      const length = Math.sqrt(squared);
      return {x: x/length, y: y/length, z: 0};
    }
    function updateAnglesFromOrientation() {
      const [x,y,z,w] = state.orientation;
      const r00 = 1 - 2*(y*y + z*z);
      const r02 = 2*(x*z + y*w);
      const r11 = 1 - 2*(x*x + z*z);
      const r21 = 2*(y*z + x*w);
      state.yaw = Math.atan2(r02, r00);
      state.pitch = Math.max(-1.396, Math.min(1.396, Math.atan2(r21, r11)));
    }
    state.orientation = quaternionFromEuler(state.yaw, state.pitch);
    function project(p) {
      const rotated = rotateVector(p, state.orientation);
      const perspective = state.perspective
        ? 7 / Math.max(2, 7 + rotated.z)
        : 1;
      const unit = Math.min(state.width / 5.7, state.height / 4.65);
      const center = plotCenter();
      return {
        x: center.x + rotated.x * unit * perspective * state.zoom,
        y: center.y - rotated.y * unit * perspective * state.zoom,
        depth: rotated.z
      };
    }
    function line3(a, b, stroke, width = 1) {
      const pa = project(a), pb = project(b);
      ctx.beginPath(); ctx.moveTo(pa.x, pa.y); ctx.lineTo(pb.x, pb.y);
      ctx.strokeStyle = stroke; ctx.lineWidth = width; ctx.stroke();
    }
    function label3(p, text, dx = 0, dy = 0, fill = color.axis) {
      const q = project(p);
      ctx.font = "11px ui-sans-serif, system-ui"; ctx.fillStyle = fill;
      ctx.fillText(text, q.x + dx, q.y + dy);
    }
    function drawExactPlane() {
      if (!Number.isFinite(study.exactEnergy)) return;
      const corners = [
        world(1, 0, study.exactEnergy),
        world(maxRound, 0, study.exactEnergy),
        world(maxRound, study.callBudget, study.exactEnergy),
        world(1, study.callBudget, study.exactEnergy)
      ];
      const projected = corners.map(project);
      ctx.beginPath();
      ctx.moveTo(projected[0].x, projected[0].y);
      projected.slice(1).forEach(point => ctx.lineTo(point.x, point.y));
      ctx.closePath();
      ctx.fillStyle = "rgba(168,85,247,.34)";
      ctx.fill();
      ctx.strokeStyle = "rgba(192,132,252,1)";
      ctx.lineWidth = 2.4;
      ctx.stroke();
      for (const fraction of [.25, .5, .75]) {
        const round = 1 + fraction * (maxRound - 1);
        const call = fraction * study.callBudget;
        line3(
          world(round, 0, study.exactEnergy),
          world(round, study.callBudget, study.exactEnergy),
          "rgba(216,180,254,.52)",
          1
        );
        line3(
          world(1, call, study.exactEnergy),
          world(maxRound, call, study.exactEnergy),
          "rgba(216,180,254,.52)",
          1
        );
      }
      label3(
        world(maxRound, study.callBudget, study.exactEnergy),
        `EXACT ${fmtEnergy(study.exactEnergy)}`,
        8,
        -8,
        color.exact
      );
    }
    function drawAxes() {
      const corners = [];
      for (const x of [-2,2]) for (const y of [-1.55,1.55]) for (const z of [-1.55,1.55]) {
        corners.push({x,y,z});
      }
      for (let i=0;i<corners.length;i++) for (let j=i+1;j<corners.length;j++) {
        const a=corners[i], b=corners[j];
        if ((a.x!==b.x)+(a.y!==b.y)+(a.z!==b.z)===1) line3(a,b,color.grid,.8);
      }
      const roundTicks = [...new Set([0,.25,.5,.75,1].map(
        fraction => Math.max(1, Math.round(1 + fraction * (maxRound - 1)))
      ))];
      for (const r of roundTicks) label3(world(r,0,energyLow), String(r), -4, 15);
      for (const call of [0,75,150,225,300]) {
        label3(world(1,call,energyLow), String(call), -34, 4);
      }
      for (let i=0;i<5;i++) {
        const e=energyLow+(energyHigh-energyLow)*i/4;
        label3(world(1,0,e), e.toFixed(3), -65, 4);
      }
      label3(world((maxRound+1)/2,0,energyLow), "AUTORESEARCH ROUND", -58, 34, "#e2e4e7");
      label3(world(1,160,energyLow), "OBSERVE CALL", -58, -9, "#e2e4e7");
      label3(world(1,0,(energyLow+energyHigh)/2), "BEST ENERGY", -67, -8, "#e2e4e7");
    }
    function visible(r) {
      if (state.isolate !== "all" && String(r.round) !== state.isolate) return false;
      if (state.filter==="best") return r.improved;
      if (state.filter==="converged") return r.converged;
      if (state.filter==="capped") return r.observeCap || r.timeCap;
      return true;
    }
    function traceColor(r) {
      if (!r.valid) return color.invalid;
      if (r.winner) return color.green;
      return r.improved ? color.lime : color.gray;
    }
    function endpoint(p, r, stroke) {
      ctx.strokeStyle = stroke; ctx.fillStyle = stroke; ctx.lineWidth = r.winner ? 3 : 2;
      if (r.converged) {
        ctx.beginPath(); ctx.arc(p.x,p.y,r.winner?6:4,0,Math.PI*2); ctx.fill();
      } else {
        const size=r.winner?7:5;
        ctx.beginPath(); ctx.moveTo(p.x-size,p.y-size); ctx.lineTo(p.x+size,p.y+size);
        ctx.moveTo(p.x+size,p.y-size); ctx.lineTo(p.x-size,p.y+size); ctx.stroke();
      }
    }
    function drawTrace(r) {
      if (!visible(r) || !r.points.length) return;
      const stroke=traceColor(r);
      ctx.beginPath(); const projected=[];
      r.points.forEach((point,i)=>{
        const p=project(world(r.round,point.call,point.bestEnergy));
        projected.push({...p,point,round:r});
        if(i===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);
      });
      ctx.strokeStyle=stroke;
      ctx.globalAlpha=r.winner?1:r.improved?.88:.48;
      ctx.lineWidth=r.winner?3.5:r.improved?2:1.15; ctx.stroke(); ctx.globalAlpha=1;
      endpoint(projected.at(-1),r,stroke);
      const finalPoint=projected.at(-1);
      ctx.fillStyle=stroke;ctx.font=r.winner?"700 12px ui-sans-serif":"11px ui-sans-serif";
      ctx.fillText(`R${r.round}`,finalPoint.x+8,finalPoint.y-7);
      state.projected.push(...projected);
    }
    function render() {
      ctx.clearRect(0,0,state.width,state.height); state.projected=[];
      drawAxes();
      drawExactPlane();
      const ordered=[...study.rounds].sort((a,b)=>
        Number(a.winner)-Number(b.winner)||Number(a.improved)-Number(b.improved));
      ordered.forEach(drawTrace);
    }
    function resize() {
      const rect=canvas.getBoundingClientRect(), dpr=Math.min(devicePixelRatio||1,2);
      canvas.width=Math.round(rect.width*dpr); canvas.height=Math.round(rect.height*dpr);
      ctx.setTransform(dpr,0,0,dpr,0,0); state.width=rect.width; state.height=rect.height; render();
    }
    canvas.addEventListener("pointerdown",e=>{
      state.dragging=true;
      state.dragStart=arcballPoint(e);
      state.dragOrientation=[...state.orientation];
      canvas.classList.add("dragging");canvas.setPointerCapture(e.pointerId);
      stage.classList.add("orbiting");canvas.focus();
      tooltip.style.display="none";
    });
    canvas.addEventListener("pointermove",e=>{
      if(state.dragging){
        const delta=quaternionBetween(state.dragStart,arcballPoint(e));
        state.orientation=normalizeQuaternion(
          multiplyQuaternion(delta,state.dragOrientation)
        );
        updateAnglesFromOrientation();syncCamera();render();return;
      }
      const rect=canvas.getBoundingClientRect(),mx=e.clientX-rect.left,my=e.clientY-rect.top;
      let nearest=null,distance=13;
      for(const p of state.projected){const d=Math.hypot(p.x-mx,p.y-my);if(d<distance){distance=d;nearest=p;}}
      if(!nearest){tooltip.style.display="none";return;}
      const r=nearest.round,p=nearest.point;
      tooltip.innerHTML=`<strong>Round ${r.round}: ${escapeHtml(r.optimizer)}</strong><br>
        <span class="muted">Observe call</span> ${p.call} / ${study.callBudget} ·
        <span class="muted">elapsed</span> ${p.elapsed.toFixed(3)}s<br>
        <span class="muted">Energy at call</span> ${fmtEnergy(p.energy)}<br>
        <span class="green">Lowest so far ${fmtEnergy(p.bestEnergy)}</span><br>
        <span class="muted">Outcome</span> ${r.converged?"converged":r.observeCap?"observe cap":"not converged"} ·
        ${r.improved?"became study leader":"did not become leader"}`;
      tooltip.style.display="block";
      tooltip.style.left=`${Math.min(state.width-320,Math.max(8,mx+14))}px`;
      tooltip.style.top=`${Math.min(state.height-120,Math.max(8,my+14))}px`;
    });
    canvas.addEventListener("pointerup",e=>{
      state.dragging=false;canvas.classList.remove("dragging");
      stage.classList.remove("orbiting");canvas.releasePointerCapture(e.pointerId);
    });
    canvas.addEventListener("pointercancel",()=>{
      state.dragging=false;canvas.classList.remove("dragging");
      stage.classList.remove("orbiting");
    });
    canvas.addEventListener("wheel",e=>{
      e.preventDefault();state.zoom=Math.max(.55,Math.min(2.1,state.zoom*Math.exp(-e.deltaY*.001)));
      syncCamera();render();
    },{passive:false});
    function syncCamera(){
      const degrees=180/Math.PI;
      document.getElementById("yaw").value=Math.round(state.yaw*degrees);
      document.getElementById("pitch").value=Math.round(state.pitch*degrees);
      document.getElementById("zoom").value=Math.round(state.zoom*100);
      document.getElementById("yawOut").value=`${Math.round(state.yaw*degrees)}°`;
      document.getElementById("pitchOut").value=`${Math.round(state.pitch*degrees)}°`;
      document.getElementById("zoomOut").value=`${Math.round(state.zoom*100)}%`;
      document.getElementById("perspective").classList.toggle("active",state.perspective);
    }
    function setView(view){
      const views={
        iso:[-.82,-.42,1],
        front:[0,0,1],
        top:[0,-1.35,1],
        energy:[-Math.PI/2,0,1]
      };
      [state.yaw,state.pitch,state.zoom]=views[view]||views.iso;
      state.orientation=quaternionFromEuler(state.yaw,state.pitch);
      syncCamera();render();
    }
    function reset(){state.perspective=false;setView("iso");}
    canvas.addEventListener("dblclick",reset);
    document.getElementById("reset").addEventListener("click",reset);
    document.getElementById("filter").addEventListener("change",e=>{state.filter=e.target.value;render();});
    document.getElementById("isolate").addEventListener("change",e=>{
      state.isolate=e.target.value;populateTable();render();
    });
    document.querySelectorAll("[data-view]").forEach(button=>{
      button.addEventListener("click",()=>setView(button.dataset.view));
    });
    document.getElementById("perspective").addEventListener("click",()=>{
      state.perspective=!state.perspective;syncCamera();render();
    });
    for(const [id,property,scale] of [["yaw","yaw",Math.PI/180],["pitch","pitch",Math.PI/180],["zoom","zoom",.01]]){
      document.getElementById(id).addEventListener("input",event=>{
        state[property]=Number(event.target.value)*scale;
        if(property!=="zoom"){
          state.orientation=quaternionFromEuler(state.yaw,state.pitch);
        }
        syncCamera();render();
      });
    }
    canvas.addEventListener("keydown",event=>{
      const handled=["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","+","=","-","0"].includes(event.key);
      if(!handled)return;event.preventDefault();
      let orbit=null;
      if(event.key==="ArrowLeft")orbit=axisAngle(0,1,0,-.08);
      if(event.key==="ArrowRight")orbit=axisAngle(0,1,0,.08);
      if(event.key==="ArrowUp")orbit=axisAngle(1,0,0,-.08);
      if(event.key==="ArrowDown")orbit=axisAngle(1,0,0,.08);
      if(orbit){
        state.orientation=normalizeQuaternion(
          multiplyQuaternion(orbit,state.orientation)
        );
        updateAnglesFromOrientation();
      }
      if(event.key==="+"||event.key==="=")state.zoom=Math.min(2.1,state.zoom*1.08);
      if(event.key==="-")state.zoom=Math.max(.55,state.zoom/1.08);
      if(event.key==="0"){reset();return;}
      syncCamera();render();
    });
    document.getElementById("rotate").addEventListener("click",e=>{
      state.auto=!state.auto;e.target.textContent=state.auto?"Stop rotation":"Auto-rotate";
    });
    function animate(){
      if(state.auto&&!state.dragging){
        state.orientation=normalizeQuaternion(multiplyQuaternion(
          axisAngle(0,1,0,.003),state.orientation
        ));
        updateAnglesFromOrientation();syncCamera();render();
      }
      requestAnimationFrame(animate);
    }
    function populateTable(){
      document.getElementById("roundTable").innerHTML=study.rounds.map(r=>{
        const cls=[r.winner?"winner":r.improved?"new-best":!r.valid?"invalid":"",
          state.isolate===String(r.round)?"selected":""].filter(Boolean).join(" ");
        const name=escapeHtml(r.optimizer);
        return `<tr class="${cls}" data-round="${r.round}"><td>${r.round}</td><td title="${name}">${name}</td>
          <td>${fmtEnergy(r.bestEnergy)}</td><td>${r.calls}/${study.callBudget}</td>
          <td class="status">${r.converged?"yes":"no"}</td></tr>`;
      }).join("");
      document.querySelectorAll("#roundTable tr").forEach(row=>{
        row.addEventListener("click",()=>{
          state.isolate=state.isolate===row.dataset.round?"all":row.dataset.round;
          document.getElementById("isolate").value=state.isolate;
          populateTable();render();
        });
      });
    }
    function populate() {
      const winner=study.rounds.find(r=>r.winner), baseline=study.rounds[0];
      const converged=study.rounds.filter(r=>r.converged).length;
      document.getElementById("metrics").innerHTML=`
        <div class="metric"><span>Winning round</span><b>${winner.round}</b></div>
        <div class="metric"><span>Lowest energy</span><b>${fmtEnergy(winner.bestEnergy)}</b></div>
        <div class="metric"><span>Exact ground energy</span><b style="color:var(--nv-purple)">${fmtEnergy(study.exactEnergy)}</b></div>
        <div class="metric"><span>Winner exact gap</span><b>${fmtEnergy(study.winnerExactGap)}</b></div>
        <div class="metric"><span>Observe calls</span><b>${winner.calls} / ${study.callBudget}</b></div>
        <div class="metric"><span>Converged rounds</span><b>${converged} / ${study.rounds.length}</b></div>
        <div class="metric"><span>CUDA-Q target</span><b>${escapeHtml(study.target)} ${escapeHtml(study.targetOption||"")}</b></div>
        <div class="metric"><span>Recorded rounds</span><b>${study.rounds.length}</b></div>`;
      document.getElementById("comparison").innerHTML=
        `The winner improved on round 1 by <strong style="color:var(--nv-lime)">${(baseline.bestEnergy-winner.bestEnergy).toFixed(6)}</strong> energy units. `+
        `It remained <strong style="color:var(--nv-purple)">${fmtEnergy(study.winnerExactGap)}</strong> above the exact ground energy. `+
        `${winner.converged?"It converged before the observe cap.":"It set the best energy without converging."}`;
      const isolate=document.getElementById("isolate");
      isolate.innerHTML=`<option value="all">All rounds</option>`+
        study.rounds.map(r=>`<option value="${r.round}">Round ${r.round}</option>`).join("");
      populateTable();
    }
    populate();syncCamera();new ResizeObserver(resize).observe(stage);resize();animate();
  </script>
</body>
</html>
"""


def build_widget() -> Path:
    dataset = build_dataset()
    payload = json.dumps(dataset, separators=(",", ":"))
    OUTPUT.write_text(HTML.replace("__DATA__", payload))
    print(f"Wrote {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    build_widget()

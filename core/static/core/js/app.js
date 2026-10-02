function refreshResults() {
  Object.keys(GAMES).forEach(k => {
    if (!results[k]) results[k] = generateResult(GAMES[k]);
  });
  renderResults();
  showToast("Results refreshed");
}

function predict() {
  if (busy) return;
  busy = true;
  const g = GAMES[currentGame];
  const btn = document.getElementById("predictBtn");
  btn.disabled = true;
  btn.innerHTML = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" stroke-dasharray="60" stroke-dashoffset="30"/></svg> Tumbling drum';

  document.getElementById("lines").innerHTML = "";

  const machine = document.getElementById("machine");
  document.getElementById("machineIdle").style.display = "none";

  const gameChain = [currentGame, ...g.companions];
  const allSets = {};
  gameChain.forEach(k => {
    const used = [];
    allSets[k] = Array.from({ length: lineCount }, () => {
      try {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", "/predictor/api/generate/?game=" + encodeURIComponent(k) +
                        "&avoid=" + encodeURIComponent(used.join(",")), false);
        xhr.send();
        const data = JSON.parse(xhr.responseText);
        used.push(...data.mains);
        return { mains: data.mains, bonus: data.bonus };
      } catch (e) {
        return genSet(GAMES[k], true);
      }
    });
  });

  const ballCount = g.pick + (g.bonus ? 1 : 0);
  const tumblers = [];
  for (let i = 0; i < ballCount; i++) {
    const t = document.createElement("div");
    t.className = "tumbler";
    t.style.left = (16 + Math.random() * 66) + "%";
    t.style.top = (16 + Math.random() * 58) + "%";
    const isB = g.bonus && i === ballCount - 1;
    const b = document.createElement("div");
    b.className = "tball" + (isB ? " bonus" : "");
    b.textContent = 1 + Math.floor(Math.random() * (isB ? g.bonusMax : g.max));
    b.style.setProperty("--tx", (Math.random() * 70 - 35) + "px");
    b.style.setProperty("--ty", (Math.random() * 52 - 42) + "px");
    b.style.setProperty("--td", (0.28 + Math.random() * 0.22) + "s");
    t.appendChild(b);
    machine.appendChild(t);
    tumblers.push(t);
  }

  const status = document.createElement("div");
  status.className = "machine-status";
  machine.appendChild(status);

  const phases = [
    "Scanning 90 draw matrix",
    "Weighting hot pool",
    "Balancing odd and even",
    "Optimising spread",
    "Generating companion lines",
    "Locking in set"
  ];
  let pi = 0;
  status.textContent = phases[0];
  const phaseIv = setInterval(() => {
    pi = Math.min(pi + 1, phases.length - 1);
    status.textContent = phases[pi];
  }, 460);

  const numIv = setInterval(() => {
    tumblers.forEach((t, i) => {
      const isB = g.bonus && i === ballCount - 1;
      t.firstChild.textContent = 1 + Math.floor(Math.random() * (isB ? g.bonusMax : g.max));
    });
  }, 70);

  setTimeout(() => {
    clearInterval(numIv);
    clearInterval(phaseIv);
    tumblers.forEach(t => t.remove());
    status.remove();
    document.getElementById("machineIdle").style.display = "";
    revealAllLines(gameChain, allSets, true);
    btn.disabled = false;
    btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M13 2L4 14h6l-1 8 9-12h-6z"/></svg> Predict Numbers';
    busy = false;
  }, 2600 + lineCount * 200);
}

function quickPick() {
  if (busy) return;
  const g = GAMES[currentGame];
  const gameChain = [currentGame, ...g.companions];
  const allSets = {};
  gameChain.forEach(k => {
    const used = [];
    allSets[k] = Array.from({ length: lineCount }, () => {
      try {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", "/predictor/api/generate/?game=" + encodeURIComponent(k) +
                        "&weighted=0&avoid=" + encodeURIComponent(used.join(",")), false);
        xhr.send();
        const data = JSON.parse(xhr.responseText);
        used.push(...data.mains);
        return { mains: data.mains, bonus: data.bonus };
      } catch (e) {
        return genSet(GAMES[k], false);
      }
    });
  });
  revealAllLines(gameChain, allSets, false);
}

function revealAllLines(gameChain, allSets, weighted) {
  const wrap = document.getElementById("lines");
  wrap.innerHTML = "";

  let baseConf = 0;
  let baseStats = null;
  let totalLines = 0;

  gameChain.forEach((gameKey, chainIndex) => {
    const game = GAMES[gameKey];
    const sets = allSets[gameKey];

    sets.forEach((s, i) => {
      const st = statsFor(game, s);
      totalLines++;

      if (chainIndex === 0 && i === 0) {
        baseStats = st;
        baseConf = parseFloat(st.conf);
      } else if (chainIndex === 0) {
        baseConf = (baseConf + parseFloat(st.conf)) / 2;
      }

      const block = document.createElement("div");
      block.className = "line-block";
      block.style.animationDelay = (totalLines * 0.08) + "s";

      if (chainIndex === 0) {
        block.style.background = "#f5f5f8";
        block.style.borderColor = "var(--line-2)";
      }

      let balls = s.mains.map((n, j) =>
        `<div class="ball" style="animation-delay:${0.12 + j * 0.06}s">${n}</div>`
      ).join("");

      if (s.bonus !== null) {
        balls += `<span class="plus">+</span><div class="ball bonus" style="animation-delay:${0.12 + s.mains.length * 0.06}s">${s.bonus}</div>`;
      }

      const tagLabel = chainIndex === 0 ? "BASE" : "COMPANION";
      block.innerHTML = `
        <div class="line-head">
          <div class="line-title">
            <svg viewBox="0 0 24 24">${chainIndex === 0
              ? '<path d="M13 2L4 14h6l-1 8 9-12h-6z"/>'
              : '<path d="M4 12h16M12 4v16"/>'}</svg>
            <span>${game.name}</span>
            <span class="line-tag">${tagLabel} · LINE ${i + 1}</span>
          </div>
          <div class="line-meta">${st.conf}% · SUM ${st.sum} · SPREAD ${st.spread}</div>
        </div>
        <div class="balls">${balls}</div>`;
      wrap.appendChild(block);

      addHistory(game, s, st);
    });
  });

  updateStats(GAMES[currentGame], baseStats, baseConf, weighted, totalLines);
  showToast(weighted ? `Lines locked in: ${totalLines} total` : `Quick pick ready: ${totalLines} total`);
}

function updateStats(g, st, avgConf, weighted, n) {
  const off = RING_LEN - (RING_LEN * Math.min(avgConf, 100) / 100);
  document.getElementById("ringFg").style.strokeDashoffset = off;
  animateNum("confVal", avgConf, "%", 900);
  animateNum("bigVal", avgConf, "%", 900);
  document.getElementById("confNote").textContent =
    `${weighted ? "Weighted" : "Quick pick"} set for ${g.name} and its companion lines. Confidence weighs hot coverage, spread and balance.`;
  document.getElementById("hotCov").textContent = `${st.hotHits}/${g.pick} hot balls`;
  document.getElementById("sumVal").textContent = st.sum;
  document.getElementById("spreadVal").textContent = st.spread;
  document.getElementById("linesCount2").textContent = n + " lines";

  const oddPct = Math.round(st.odd / st.mains.length * 100);
  const lowPct = Math.round(st.lows / st.mains.length * 100);

  document.getElementById("oeDonut").style.background =
    `conic-gradient(var(--ink) ${oddPct * 3.6}deg, var(--bg-2) ${oddPct * 3.6}deg)`;
  document.getElementById("oePct").textContent = oddPct + "%";
  document.getElementById("oeLegend").innerHTML = `<b>${st.odd}</b> odd · <b>${st.even}</b> even`;

  document.getElementById("lhDonut").style.background =
    `conic-gradient(var(--ink) ${lowPct * 3.6}deg, var(--bg-2) ${lowPct * 3.6}deg)`;
  document.getElementById("lhPct").textContent = lowPct + "%";
  document.getElementById("lhLegend").innerHTML = `<b>${st.lows}</b> low (1 to ${Math.ceil(g.max / 2)}) · <b>${st.highs}</b> high`;
  document.getElementById("hotHits").textContent = `${st.hotHits} / ${g.pick}`;

  drawSpark(g, st);
}

function drawSpark(g, st) {
  const svg = document.getElementById("spark");
  if (!svg) return;
  const pts = [];
  let v = 22;
  for (let i = 0; i <= 24; i++) {
    v += (Math.random() - 0.48) * 8;
    v = Math.max(6, Math.min(38, v));
    pts.push([i * (300 / 24), 44 - v]);
  }
  const line = pts.map(p => p.join(",")).join(" ");
  const area = `0,44 ${line} 300,44`;
  svg.innerHTML = `<polygon class="area" points="${area}"/><polyline points="${line}"/>`;
  document.getElementById("sparkVal").textContent = `SUM ${st.sum} · SPREAD ${st.spread}`;
}

function clearAll() {
  const lines = document.getElementById("lines");
  if (lines) lines.innerHTML = "";
  const idle = document.getElementById("machineIdle");
  if (idle) idle.style.display = "";
  const ring = document.getElementById("ringFg");
  if (ring) ring.style.strokeDashoffset = RING_LEN;
  const cv = document.getElementById("confVal");
  if (cv) cv.innerHTML = "—<small>%</small>";
  const bv = document.getElementById("bigVal");
  if (bv) bv.innerHTML = "—<small>%</small>";
  const cn = document.getElementById("confNote");
  if (cn) cn.textContent = "Run the engine to receive a weighted confidence index based on hot coverage, spread and balance.";

  ["hotCov", "sumVal", "spreadVal", "hotHits", "linesCount2"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = "—";
  });
  ["oePct", "lhPct"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = "—";
  });

  const oel = document.getElementById("oeLegend");
  if (oel) oel.textContent = "Awaiting prediction";
  const lel = document.getElementById("lhLegend");
  if (lel) lel.textContent = "Awaiting prediction";
  const oe = document.getElementById("oeDonut");
  if (oe) oe.style.background = "var(--bg-2)";
  const lh = document.getElementById("lhDonut");
  if (lh) lh.style.background = "var(--bg-2)";
  const sp = document.getElementById("spark");
  if (sp) sp.innerHTML = "";
  const spv = document.getElementById("sparkVal");
  if (spv) spv.textContent = "—";
  showToast("Cleared. Ready for a new run.");
}

function tick() {
  const clock = document.getElementById("clock");
  if (clock) clock.textContent = new Date().toLocaleTimeString("en-GB", { hour12: false });
  const g = GAMES[currentGame];
  const nd = nextDraw(g);
  const cd = nd ? fmtCD(nd - new Date()) : "--:--:--";
  const c = document.getElementById("countdown");
  if (c) c.textContent = cd;
  const cg = document.getElementById("cdGame");
  if (cg) cg.textContent = g.name;
  const mc = document.getElementById("miniCd");
  if (mc) mc.textContent = cd;
  const mcg = document.getElementById("miniCdGame");
  if (mcg) mcg.textContent = g.name;
}

document.addEventListener("DOMContentLoaded", () => {
  const active = document.querySelector("#sbNav .sb-item.active")?.dataset.page;

  const predictBtn = document.getElementById("predictBtn");
  if (predictBtn) predictBtn.addEventListener("click", predict);

  const topBtn = document.getElementById("topPredictBtn");
  if (topBtn) topBtn.addEventListener("click", () => {
    if (active === "predictor") {
      document.getElementById("predictBtn")?.click();
    } else {
      sessionStorage.setItem("autoPredict", "1");
      window.location.href = "/predictor/";
    }
  });

  if (sessionStorage.getItem("autoPredict") === "1" && active === "predictor") {
    sessionStorage.removeItem("autoPredict");
    setTimeout(() => document.getElementById("predictBtn")?.click(), 350);
  }

  document.querySelectorAll("#linesCount button").forEach(b => {
    b.addEventListener("click", () => {
      document.querySelectorAll("#linesCount button").forEach(x => x.classList.remove("on"));
      b.classList.add("on");
      lineCount = parseInt(b.dataset.n);
    });
  });

  const predictorSel = document.getElementById("predictorGameSelector");
  if (predictorSel) {
    predictorSel.querySelectorAll(".game").forEach(btn => {
      btn.addEventListener("click", () => {
        const game = btn.dataset.game;
        window.location.href = "/predictor/?game=" + encodeURIComponent(game);
      });
    });
  }

  if (document.getElementById("schedDash"))           renderScheduleInto("schedDash");
  if (document.getElementById("histPage"))            renderHistoryPage();
  if (document.getElementById("panelTitle"))          refreshPredictorMeta();
  if (document.getElementById("resultsList"))         refreshResults();
  if (document.getElementById("profilePredCount"))    updateProfileCount();

  tick();
  setInterval(tick, 1000);
  setInterval(() => { if (document.getElementById("schedDash")) renderScheduleInto("schedDash"); }, 60000);
  setInterval(() => { if (document.getElementById("resultsList")) refreshResults(); }, 30000);
});
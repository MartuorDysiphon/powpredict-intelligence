const RING_LEN = 276.5;

const PAGE_URLS = {
  dashboard: "/",
  predictor: "/predictor/",
  results:   "/results/",
  analytics: "/analytics/",
  history:   "/history/",
  profile:   "/profile/",
};

function switchPage(pageId) {
  const url = PAGE_URLS[pageId];
  if (url) window.location.href = url;
}

function renderGameSelector(containerId, showAll) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = "";

  const keys = showAll ? Object.keys(GAMES) : BASE_GAMES;

  keys.forEach(key => {
    const g = GAMES[key];
    const b = document.createElement("button");
    b.className = "game" + (key === currentGame ? " active" : "");
    b.innerHTML = `<span class="gd"></span>${g.name}`;
    b.onclick = () => {
      currentGame = key;
      document.querySelectorAll(".games").forEach(sel => {
        sel.querySelectorAll(".game").forEach(x => {
          const label = x.textContent.trim();
          const matchKey = Object.keys(GAMES).find(k => GAMES[k].name === label);
          x.classList.toggle("active", matchKey === key);
        });
      });
      renderHotColdPair("dashHotList", "dashColdList");
      renderHotColdPair("analyticsHotList", "analyticsColdList");
      renderScheduleInto("schedDash");
      refreshPredictorMeta();
      renderAnalyticsFreq();
      renderResults();
    };
    el.appendChild(b);
  });
}

function renderHotColdInto(elId, nums, cls, freqs) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.innerHTML = "";
  nums.forEach((n, i) => {
    const pct = Math.round(freqs[i]);
    const row = document.createElement("div");
    row.className = "hc-row";
    row.innerHTML = `
      <div class="hc-num ${cls}">${n}</div>
      <div class="hc-bar"><div class="hc-fill ${cls}" data-w="${Math.min(pct, 100)}"></div></div>
      <div class="hc-val">${pct}%</div>`;
    el.appendChild(row);
  });
  requestAnimationFrame(() => requestAnimationFrame(() => {
    el.querySelectorAll(".hc-fill").forEach(f => f.style.width = f.dataset.w + "%");
  }));
}

function renderHotColdPair(hotId, coldId) {
  const g = GAMES[currentGame];
  renderHotColdInto(hotId, g.hot, "hot", g.freq);
  renderHotColdInto(coldId, g.cold, "cold", g.freq.map(f => 100 - f));
}

function renderScheduleInto(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.innerHTML = "";
  Object.values(GAMES).forEach(g => {
    const nd = nextDraw(g);
    const row = document.createElement("div");
    row.className = "sched-row";
    row.innerHTML = `
      <div class="sched-name">${g.name}<span class="sd">${g.pick} from 1 to ${g.max}${g.bonus ? " plus 1 from 1 to " + g.bonusMax : ""}</span></div>
      <span class="sched-chip">${g.draw}</span>
      <span class="mono" style="font-size:11px;color:var(--gray-2);font-weight:700;white-space:nowrap">${nd ? fmtCD(nd - new Date()) : "—"}</span>`;
    el.appendChild(row);
  });
}

function renderAnalyticsFreq() {
  const g = GAMES[currentGame];
  const el = document.getElementById("analyticsFreqList");
  if (!el) return;
  el.innerHTML = "";
  g.hot.forEach((n, i) => {
    const pct = Math.round(g.freq[i]);
    const row = document.createElement("div");
    row.className = "hc-row";
    row.innerHTML = `
      <div class="hc-num hot">${n}</div>
      <div class="hc-bar"><div class="hc-fill hot" data-w="${pct}"></div></div>
      <div class="hc-val">${pct}%</div>`;
    el.appendChild(row);
  });
  requestAnimationFrame(() => requestAnimationFrame(() => {
    el.querySelectorAll(".hc-fill").forEach(f => f.style.width = f.dataset.w + "%");
  }));
}

function renderResults() {
  const el = document.getElementById("resultsList");
  if (!el) return;
  Object.keys(GAMES).forEach(k => {
    if (!results[k]) results[k] = generateResult(GAMES[k]);
  });

  el.innerHTML = "";
  Object.entries(GAMES).forEach(([key, g]) => {
    const r = results[key];
    const block = document.createElement("div");
    block.className = "result-block";
    let balls = r.mains.map(n => `<div class="rball">${n}</div>`).join("");
    if (r.bonus !== null) balls += `<span class="plus">+</span><div class="rball bonus">${r.bonus}</div>`;
    block.innerHTML = `
      <div class="result-head">
        <div class="result-title">${g.name}</div>
        <div class="result-time">${r.time}</div>
      </div>
      <div class="result-balls">${balls}</div>`;
    el.appendChild(block);
  });
  const upd = document.getElementById("resultsUpdated");
  if (upd) upd.textContent = "Updated " + new Date().toLocaleTimeString("en-GB", { hour12: false });
}

function renderHistoryPage() {
  const render = (el, limit) => {
    if (!el) return;
    el.innerHTML = history.length ? "" : `<div class="empty">No predictions yet. Run the engine to build your history.</div>`;
    (limit ? history.slice(0, limit) : history).forEach(h => {
      const row = document.createElement("div");
      row.className = "hist-row";
      row.innerHTML = `<span class="hist-game">${h.game}</span><span class="hist-nums">${h.nums}</span><span class="hist-conf">${h.conf}%</span><span class="hist-time">${h.time}</span>`;
      el.appendChild(row);
    });
  };
  render(document.getElementById("histPage"));
  render(document.getElementById("histDash"), 6);
}

function refreshPredictorMeta() {
  const g = GAMES[currentGame];
  const pt = document.getElementById("panelTitle");
  if (!pt) return;
  pt.textContent = `${g.name} Prediction Panel`;
  let hint = `${g.pick} numbers from 1 to ${g.max}`;
  if (g.bonus) hint += ` plus 1 bonus from 1 to ${g.bonusMax}`;
  hint += `. Draws: ${g.draw}.`;
  if (g.companions.length) {
    const compNames = g.companions.map(k => GAMES[k].name).join(" and ");
    hint += ` Companion lines will also be generated for ${compNames}.`;
  }
  document.getElementById("panelHint").textContent = hint;
  const sc = document.getElementById("scGame");
  if (sc) sc.textContent = `${g.name} Confidence Report`;
}

function addHistory(g, s, st) {
  history.unshift({
    game: g.short,
    nums: s.mains.join(" ") + (s.bonus !== null ? " +" + s.bonus : ""),
    conf: st.conf,
    time: new Date().toLocaleTimeString("en-ZA", { hour: "2-digit", minute: "2-digit" })
  });
  if (history.length > 40) history.length = 40;
  localStorage.setItem("powpredict_v7", JSON.stringify(history));
  renderHistoryPage();
  updateProfileCount();
}

function clearHistory() {
  history = [];
  localStorage.removeItem("powpredict_v7");
  renderHistoryPage();
  updateProfileCount();
  showToast("History cleared");
}

function updateProfileCount() {
  const el = document.getElementById("profilePredCount");
  if (el) el.textContent = history.length;
}

function exportHistory() {
  if (!history.length) {
    showToast("Nothing to export");
    return;
  }
  const data = history.map(h => `${h.game} | ${h.nums} | ${h.conf}% | ${h.time}`).join("\n");
  const blob = new Blob(["Powpredict History Export\n\n" + data], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "powpredict-history.txt";
  a.click();
  URL.revokeObjectURL(url);
  showToast("History exported");
}

function toggleSwitch(el) {
  el.classList.toggle("on");
}

function animateNum(id, target, suffix, dur) {
  const el = document.getElementById(id);
  if (!el) return;
  const start = performance.now();
  (function step(t) {
    const p = Math.min((t - start) / dur, 1);
    const e = 1 - Math.pow(1 - p, 3);
    el.innerHTML = (target * e).toFixed(1) + `<small>${suffix}</small>`;
    if (p < 1) requestAnimationFrame(step);
  })(performance.now());
}

let toastT;
function showToast(msg) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove("show"), 2600);
}
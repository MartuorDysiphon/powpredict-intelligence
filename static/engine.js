let currentGame = "lotto";
let lineCount = 1;
let history = JSON.parse(localStorage.getItem("powpredict_v7") || "[]");
let busy = false;
let results = {};

function weightedPick(count, max, hot, cold) {
  const pool = [];
  for (let n = 1; n <= max; n++) {
    const w = 2 + (hot.includes(n) ? 6 : 0) + (cold.includes(n) ? 2 : 0);
    pool.push({ n, w });
  }
  const out = [];
  while (out.length < count) {
    let total = 0;
    for (const p of pool) total += p.w;
    let r = Math.random() * total;
    for (let i = 0; i < pool.length; i++) {
      r -= pool[i].w;
      if (r <= 0) {
        out.push(pool[i].n);
        pool.splice(i, 1);
        break;
      }
    }
  }
  return out.sort((a, b) => a - b);
}

function purePick(count, max) {
  const pool = Array.from({ length: max }, (_, i) => i + 1);
  const out = [];
  for (let i = 0; i < count; i++) {
    out.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
  }
  return out.sort((a, b) => a - b);
}

function genSet(g, weighted) {
  const mains = weighted ? weightedPick(g.pick, g.max, g.hot, g.cold) : purePick(g.pick, g.max);
  let bonus = null;
  if (g.bonus) {
    const pool = [];
    for (let n = 1; n <= g.bonusMax; n++) {
      pool.push({ n, w: weighted && g.hot.includes(n) ? 5 : 2 });
    }
    let total = 0;
    for (const p of pool) total += p.w;
    let r = Math.random() * total;
    for (const p of pool) {
      r -= p.w;
      if (r <= 0) {
        bonus = p.n;
        break;
      }
    }
  }
  return { mains, bonus };
}

function statsFor(g, s) {
  const sum = s.mains.reduce((a, b) => a + b, 0);
  const odd = s.mains.filter(n => n % 2).length;
  const spread = s.mains[s.mains.length - 1] - s.mains[0];
  const hotHits = s.mains.filter(n => g.hot.includes(n)).length;
  const lows = s.mains.filter(n => n <= Math.ceil(g.max / 2)).length;
  const conf = Math.min(96, 71 + hotHits * 3 + (spread > g.max * .45 ? 4 : 0) + (Math.random() * 5)).toFixed(1);
  return { sum, odd, even: s.mains.length - odd, spread, hotHits, lows, highs: s.mains.length - lows, conf };
}

function nextDraw(g) {
  const now = new Date();
  for (let add = 0; add < 8; add++) {
    const d = new Date(now);
    d.setDate(now.getDate() + add);
    if (g.days.includes(d.getDay())) {
      d.setHours(g.hour, g.min, 0, 0);
      if (d > now) return d;
    }
  }
  return null;
}

function fmtCD(ms) {
  if (ms <= 0) return "00:00:00:00";
  const totalSeconds = Math.floor(ms / 1000);
  const d = String(Math.floor(totalSeconds / 86400)).padStart(2, "0");
  const h = String(Math.floor((totalSeconds % 86400) / 3600)).padStart(2, "0");
  const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
  const s = String(totalSeconds % 60).padStart(2, "0");
  return `${d}:${h}:${m}:${s}`;
}

function generateResult(g) {
  const s = genSet(g, true);
  return {
    mains: s.mains,
    bonus: s.bonus,
    time: new Date().toLocaleString("en-ZA", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "short" })
  };
}
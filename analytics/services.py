from collections import Counter
from datetime import date

from results.models import DrawResult


GAME_LABELS = {
    "lotto":          "Lotto",
    "lotto-plus-1":   "Lotto Plus 1",
    "lotto-plus-2":   "Lotto Plus 2",
    "powerball":      "PowerBall",
    "powerball-plus": "PowerBall Plus",
    "daily":          "Daily Lotto",
}

# Number of most recent draws used to compute hot/cold.
# Smaller = more responsive to each new draw.
# Larger  = more stable, requires more data.
WINDOW = 30


def _main_numbers(draw):
    """Return list of non-null main numbers for a DrawResult row."""
    return [n for n in (draw.main_1, draw.main_2, draw.main_3,
                        draw.main_4, draw.main_5, draw.main_6) if n]


def hot_numbers(game_key, limit=8, window=WINDOW):
    """
    Most frequently drawn main numbers over the last `window` draws.
    Returns list of {"number": int, "count": int, "pct": int}
    """
    recent = DrawResult.objects.filter(game=game_key).order_by("-draw_date")[:window]

    counter = Counter()
    total_draws = 0
    for draw in recent:
        mains = _main_numbers(draw)
        if not mains:
            continue
        total_draws += 1
        counter.update(mains)

    if total_draws == 0:
        return []

    result = []
    for number, count in counter.most_common(limit):
        result.append({
            "number": number,
            "count": count,
            "pct": round(count / total_draws * 100),
        })
    return result


def cold_numbers(game_key, limit=8, window=WINDOW):
    """
    Least frequently drawn main numbers over the last `window` draws,
    plus how many days it's been since each was last drawn.
    Returns list of {"number","count","pct","last_seen","days_ago"}
    """
    all_draws = DrawResult.objects.filter(game=game_key)
    if not all_draws.exists():
        return []

    # Determine the maximum number ever drawn for this game
    max_n = 0
    for draw in all_draws.only("main_1", "main_2", "main_3",
                                "main_4", "main_5", "main_6"):
        for n in _main_numbers(draw):
            if n > max_n:
                max_n = n

    all_numbers = set(range(1, max_n + 1))

    recent = list(DrawResult.objects.filter(game=game_key)
                    .order_by("-draw_date")[:window])
    seen_in_window = Counter()

    for draw in recent:
        for n in _main_numbers(draw):
            seen_in_window[n] += 1

    # Last-seen date across full history (not just window)
    last_seen = {}
    for draw in all_draws.order_by("-draw_date"):
        for n in _main_numbers(draw):
            if n not in last_seen:
                last_seen[n] = draw.draw_date

    total_draws = len(recent) or 1
    today = date.today()

    cold_pool = []
    for n in sorted(all_numbers):
        count = seen_in_window.get(n, 0)
        seen_date = last_seen.get(n)
        days_ago = (today - seen_date).days if seen_date else None
        cold_pool.append({
            "number": n,
            "count": count,
            "pct": round(count / total_draws * 100),
            "last_seen": seen_date,
            "days_ago": days_ago,
        })

    # Sort ascending by count, then by longest overdue first
    cold_pool.sort(key=lambda x: (x["count"], -(x["days_ago"] or 0), x["number"]))
    return cold_pool[:limit]


def frequency_distribution(game_key, limit=8, window=WINDOW):
    """
    Bar-chart data: top `limit` numbers by frequency over the last `window` draws.
    """
    recent = DrawResult.objects.filter(game=game_key).order_by("-draw_date")[:window]

    counter = Counter()
    total_draws = 0
    for draw in recent:
        mains = _main_numbers(draw)
        if not mains:
            continue
        total_draws += 1
        counter.update(mains)

    if total_draws == 0:
        return []

    rows = []
    for number, count in counter.most_common(limit):
        rows.append({
            "number": number,
            "count": count,
            "pct": round(count / total_draws * 100),
        })
    return rows
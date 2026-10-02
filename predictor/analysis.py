from collections import Counter, defaultdict
from datetime import date

from results.models import DrawResult


GAMES_FOR_ANALYSIS = {
    "lotto":          "Lotto",
    "lotto-plus-1":   "Lotto Plus 1",
    "lotto-plus-2":   "Lotto Plus 2",
    "powerball":      "PowerBall",
    "powerball-plus": "PowerBall Plus",
    "daily":          "Daily Lotto",
}

HISTORY_WINDOW = 500


def _mains(draw):
    return [n for n in (draw.main_1, draw.main_2, draw.main_3,
                        draw.main_4, draw.main_5, draw.main_6) if n]


def build_profile(game_key, window=HISTORY_WINDOW):
    qs = DrawResult.objects.filter(game=game_key).order_by("-draw_date")
    if not qs.exists():
        return None

    recent = list(qs[:window])
    full = list(qs)

    max_number = 0
    for d in full:
        for n in _mains(d):
            if n > max_number:
                max_number = n

    if max_number == 0:
        return None

    # Frequency of each number across the window 
    freq = Counter()
    for d in recent:
        freq.update(_mains(d))

    total_draws = len(recent) or 1

    recency = Counter()
    decay = 0.99
    for i, d in enumerate(recent):
        w = decay ** i
        for n in _mains(d):
            recency[n] += w

    last_seen_index = {}
    for i, d in enumerate(full):
        for n in _mains(d):
            if n not in last_seen_index:
                last_seen_index[n] = i

    # Pair co-occurrence 
    pairs = Counter()
    for d in recent:
        nums = _mains(d)
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                pairs[(nums[i], nums[j])] += 1

    # Sum distribution
    sums = [sum(_mains(d)) for d in recent if _mains(d)]
    sum_mean = sum(sums) / len(sums) if sums else 0
    sum_std = (
        (sum((s - sum_mean) ** 2 for s in sums) / len(sums)) ** 0.5
        if len(sums) > 1 else 0
    )

    spreads = []
    for d in recent:
        m = _mains(d)
        if len(m) >= 2:
            spreads.append(max(m) - min(m))
    spread_mean = sum(spreads) / len(spreads) if spreads else 0

    # Odd/even distribution 
    odd_counts = Counter()
    for d in recent:
        m = _mains(d)
        if m:
            odd_counts[sum(1 for n in m if n % 2)] += 1
    odd_mode = odd_counts.most_common(1)[0][0] if odd_counts else 3

    half = max_number // 2
    low_counts = Counter()
    for d in recent:
        m = _mains(d)
        if m:
            low_counts[sum(1 for n in m if n <= half)] += 1
    low_mode = low_counts.most_common(1)[0][0] if low_counts else 3

    # Decade distribution
    decade_dist = defaultdict(int)
    for d in recent:
        for n in _mains(d):
            decade_dist[n // 10] += 1
    total_decade = sum(decade_dist.values()) or 1
    decade_pct = {k: v / total_decade for k, v in decade_dist.items()}

    # Consecutive-number frequency
    consecutive_draws = 0
    for d in recent:
        m = sorted(_mains(d))
        if any(m[i + 1] - m[i] == 1 for i in range(len(m) - 1)):
            consecutive_draws += 1
    consecutive_rate = consecutive_draws / total_draws

    # Repeats from previous draw
    repeats = Counter()
    for i in range(len(recent) - 1):
        cur = set(_mains(recent[i]))
        prev = set(_mains(recent[i + 1]))
        repeats[len(cur & prev)] += 1
    repeat_mode = repeats.most_common(1)[0][0] if repeats else 0

    # Ending digit distribution
    ending_dist = Counter()
    for d in recent:
        for n in _mains(d):
            ending_dist[n % 10] += 1

    # Prime/composite ratio
    primes = _sieve(max_number)
    prime_ratios = []
    for d in recent:
        m = _mains(d)
        if m:
            prime_ratios.append(sum(1 for n in m if n in primes) / len(m))
    prime_mean = sum(prime_ratios) / len(prime_ratios) if prime_ratios else 0

    dow_freq = defaultdict(Counter)
    for d in recent:
        dow_freq[d.draw_date.weekday()].update(_mains(d))

    return {
        "game": game_key,
        "max_number": max_number,
        "total_draws": total_draws,
        "freq": dict(freq),
        "recency": dict(recency),
        "last_seen_index": last_seen_index,
        "pairs": dict(pairs),
        "sum_mean": sum_mean,
        "sum_std": sum_std,
        "spread_mean": spread_mean,
        "odd_mode": odd_mode,
        "low_mode": low_mode,
        "half": half,
        "decade_pct": dict(decade_pct),
        "consecutive_rate": consecutive_rate,
        "repeat_mode": repeat_mode,
        "ending_dist": dict(ending_dist),
        "prime_mean": prime_mean,
        "dow_freq": {k: dict(v) for k, v in dow_freq.items()},
    }


def _sieve(n):
    """Return set of primes up to n (inclusive)."""
    if n < 2:
        return set()
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return {i for i, p in enumerate(is_prime) if p}


def score_set(candidate, profile):
    if not profile or not candidate:
        return 0.0

    score = 0.0

    # 1. Frequency contribution (0..25 points)
    max_freq = max(profile["freq"].values()) if profile["freq"] else 1
    freq_score = sum(profile["freq"].get(n, 0) for n in candidate) / (len(candidate) * max_freq)
    score += freq_score * 25

    # 2. Recency contribution (0..20 points)
    max_rec = max(profile["recency"].values()) if profile["recency"] else 1
    rec_score = sum(profile["recency"].get(n, 0) for n in candidate) / (len(candidate) * max_rec)
    score += rec_score * 20

    # 3. Sum proximity (0..15 points)
    total = sum(candidate)
    sd = profile["sum_std"] or 1
    diff = abs(total - profile["sum_mean"])
    sum_score = max(0.0, 1.0 - (diff / (3 * sd)))
    score += sum_score * 15

    # 4. Spread proximity (0..10 points)
    spread = max(candidate) - min(candidate)
    spread_target = profile["spread_mean"] or (profile["max_number"] * 0.7)
    spread_diff = abs(spread - spread_target)
    spread_score = max(0.0, 1.0 - spread_diff / profile["max_number"])
    score += spread_score * 10

    # 5. Odd/even balance (0..10 points)
    odd = sum(1 for n in candidate if n % 2)
    odd_diff = abs(odd - profile["odd_mode"])
    score += max(0.0, 1.0 - odd_diff / len(candidate)) * 10

    # 6. Low/high balance (0..10 points)
    low = sum(1 for n in candidate if n <= profile["half"])
    low_diff = abs(low - profile["low_mode"])
    score += max(0.0, 1.0 - low_diff / len(candidate)) * 10

    # 7. Consecutive-number presence (0..5 points)
    sorted_c = sorted(candidate)
    has_consec = any(sorted_c[i + 1] - sorted_c[i] == 1 for i in range(len(sorted_c) - 1))
    if (has_consec and profile["consecutive_rate"] > 0.5) or \
       (not has_consec and profile["consecutive_rate"] <= 0.5):
        score += 5

    # 8. Prime ratio (0..5 points)
    primes = _sieve(profile["max_number"])
    prime_ratio = sum(1 for n in candidate if n in primes) / len(candidate)
    prime_diff = abs(prime_ratio - profile["prime_mean"])
    score += max(0.0, 1.0 - prime_diff * 2) * 5

    return round(score, 2)


def analyze_pair_strength(candidate, profile):
    if not profile or len(candidate) < 2:
        return 0
    c = sorted(candidate)
    strengths = []
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            strengths.append(profile["pairs"].get((c[i], c[j]), 0))
    return sum(strengths) / len(strengths) if strengths else 0


def gap_score(candidate, profile):
    if not profile:
        return 0
    overdue_threshold = 20
    overdue = sum(
        1 for n in candidate
        if profile["last_seen_index"].get(n, 9999) >= overdue_threshold
    )
    return overdue


def summarize_profile(profile, top_n=8):
    if not profile:
        return {"hot": [], "recency_hot": [], "cold": [], "overdue": []}

    hot = sorted(profile["freq"].items(), key=lambda x: -x[1])[:top_n]
    rec_hot = sorted(profile["recency"].items(), key=lambda x: -x[1])[:top_n]

    # Cold: numbers in range that appeared least often
    all_nums = set(range(1, profile["max_number"] + 1))
    cold_pool = [(n, profile["freq"].get(n, 0)) for n in all_nums]
    cold = sorted(cold_pool, key=lambda x: x[1])[:top_n]

    # Overdue: highest last_seen_index
    overdue = sorted(
        profile["last_seen_index"].items(),
        key=lambda x: -x[1]
    )[:top_n]

    return {
        "hot": [{"number": n, "count": c} for n, c in hot],
        "recency_hot": [{"number": n, "count": round(c, 1)} for n, c in rec_hot],
        "cold": [{"number": n, "count": c} for n, c in cold],
        "overdue": [{"number": n, "draws_ago": i} for n, i in overdue],
    }
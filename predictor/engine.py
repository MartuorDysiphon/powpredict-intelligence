"""
Enhanced prediction engine.

Generates candidate sets, scores them against the DB-derived statistical
profile, and returns the best matches. All numbers come from real analysis.

Reminder: this does not predict randomness. It produces sets whose shape
matches the historical distribution of past draws.
"""
import random

from .analysis import (
    build_profile,
    score_set,
    analyze_pair_strength,
    gap_score,
    summarize_profile,
)


CANDIDATE_COUNT = 5000


def generate_best_set(game_key, weighted=True, avoid=None):
    """
    Generate a scored set for `game_key`.

    weighted=True  → uses the profile scorer (Predict button)
    weighted=False → pure random (Quick Pick)

    `avoid` is an optional list of numbers already used in another line,
    so multiple lines don't duplicate.

    Returns (mains_sorted, bonus, metadata)
    """
    profile = build_profile(game_key)

    if not profile or not weighted:
        return _pure_random(game_key, avoid=avoid)

    max_n = profile["max_number"]

    # Game-specific draw size
    pick_size = _pick_size(game_key)
    has_bonus, bonus_max = _bonus_info(game_key)

    # --- Build candidate pool weighted by frequency + recency ---
    freq = profile["freq"]
    recency = profile["recency"]

    # Base weight: 1 for every number, boosted by freq and recency
    base_weight = {}
    for n in range(1, max_n + 1):
        f = freq.get(n, 0)
        r = recency.get(n, 0)
        base_weight[n] = 1 + f * 0.6 + r * 2.0

    # --- Generate candidates ---
    candidates = []
    for _ in range(CANDIDATE_COUNT):
        pool = list(range(1, max_n + 1))
        weights = [base_weight[n] for n in pool]

        chosen = []
        while len(chosen) < pick_size:
            total = sum(weights)
            r = random.random() * total
            upto = 0
            for i, w in enumerate(weights):
                upto += w
                if r <= upto:
                    chosen.append(pool[i])
                    pool.pop(i)
                    weights.pop(i)
                    break

        chosen.sort()

        # Skip if duplicates vs another line
        if avoid and any(n in avoid for n in chosen):
            continue

        candidates.append(chosen)

    # --- Score every candidate ---
    scored = []
    for c in candidates:
        base = score_set(c, profile)
        pair_bonus = analyze_pair_strength(c, profile) * 0.3
        gap_bonus = gap_score(c, profile) * 0.5
        total = base + pair_bonus + gap_bonus
        scored.append((total, c))

    scored.sort(key=lambda x: -x[0])
    top = scored[:50]

    # Pick randomly among the top 50 so successive runs differ
    chosen_score, chosen = random.choice(top)

    # --- Bonus ball if applicable ---
    bonus = None
    if has_bonus:
        bonus_pool = list(range(1, bonus_max + 1))
        bonus_weights = [
            1 + profile["freq"].get(n, 0) * 0.5 + profile["recency"].get(n, 0) * 1.5
            for n in bonus_pool
        ]
        total = sum(bonus_weights)
        r = random.random() * total
        upto = 0
        for n, w in zip(bonus_pool, bonus_weights):
            upto += w
            if r <= upto:
                bonus = n
                break

    meta = {
        "score": round(chosen_score, 2),
        "profile": summarize_profile(profile),
        "sample_size": profile["total_draws"],
    }
    return chosen, bonus, meta


def _pure_random(game_key, avoid=None):
    """Plain random pick — the Quick Pick path."""
    from games import GAMES  # only used for range info

    g = GAMES.get(game_key)
    if not g:
        return [], None, {}

    pick_size = g["pick"]
    max_n = g["max"]

    pool = list(range(1, max_n + 1))
    if avoid:
        pool = [n for n in pool if n not in avoid]
        if len(pool) < pick_size:
            pool = list(range(1, max_n + 1))

    random.shuffle(pool)
    chosen = sorted(pool[:pick_size])

    bonus = None
    if g.get("bonus"):
        bonus = random.randint(1, g["bonusMax"])

    return chosen, bonus, {"score": 0, "profile": None, "sample_size": 0}


def _pick_size(game_key):
    """Draw size for each game (numbers of main balls)."""
    return {
        "lotto": 6, "lotto-plus-1": 6, "lotto-plus-2": 6,
        "powerball": 5, "powerball-plus": 5, "daily": 5,
    }.get(game_key, 6)


def _bonus_info(game_key):
    """(has_bonus, bonus_max) for each game."""
    return {
        "powerball": (True, 20),
        "powerball-plus": (True, 20),
    }.get(game_key, (False, 0))
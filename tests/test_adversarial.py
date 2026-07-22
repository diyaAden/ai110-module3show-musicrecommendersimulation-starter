"""
Adversarial / edge-case tests for the scoring logic.

These profiles are deliberately designed to try to "trick" score_song:
conflicting preferences, wrong capitalization, out-of-range numbers,
empty profiles, and genres that don't exist in the catalog.
"""

from src.recommender import (
    score_song,
    recommend_songs,
    GENRE_WEIGHT,
    MOOD_WEIGHT,
)

# Minimal song dicts (only the fields score_song reads).
POP_HAPPY = {"genre": "pop", "mood": "happy", "energy": 0.82, "acousticness": 0.18}
METAL = {"genre": "metal", "mood": "aggressive", "energy": 0.96, "acousticness": 0.03}
LOFI = {"genre": "lofi", "mood": "chill", "energy": 0.40, "acousticness": 0.80}
CATALOG = [POP_HAPPY, METAL, LOFI]


def test_case_insensitive_matching():
    """'Pop'/'Happy' must score the same as 'pop'/'happy' (no silent failure)."""
    lower = score_song(
        {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8},
        POP_HAPPY,
    )[0]
    upper = score_song(
        {"favorite_genre": "Pop", "favorite_mood": "Happy", "target_energy": 0.8},
        POP_HAPPY,
    )[0]
    assert lower == upper
    # Both genre and mood should have matched, so at least their combined weight.
    assert upper >= GENRE_WEIGHT + MOOD_WEIGHT


def test_out_of_range_energy_never_negative():
    """A target_energy far outside [0, 1] must not produce negative scores."""
    for song in CATALOG:
        score, _ = score_song({"favorite_genre": "pop", "target_energy": 5.0}, song)
        assert score >= 0.0


def test_out_of_range_energy_is_clamped():
    """target_energy 5.0 is clamped to 1.0, so a high-energy song scores near max."""
    score, _ = score_song({"target_energy": 5.0}, METAL)  # energy 0.96 vs clamped 1.0
    assert 0.9 <= score <= 1.0


def test_negative_energy_is_clamped():
    """target_energy below 0 is clamped to 0.0, so the energy term stays in [0, 1]."""
    score, _ = score_song({"target_energy": -3.0}, LOFI)  # energy 0.40 vs clamped 0.0
    assert 0.0 <= score <= 1.0  # only the energy rule applies, capped by ENERGY_WEIGHT


def test_empty_profile_scores_zero():
    """With no preferences, every song scores 0.0 with no reasons."""
    for song in CATALOG:
        score, reasons = score_song({}, song)
        assert score == 0.0
        assert reasons == []


def test_nonexistent_genre_is_ignored_gracefully():
    """A genre not in the catalog is skipped; other rules still apply."""
    score, reasons = score_song(
        {"favorite_genre": "k-pop", "favorite_mood": "happy", "target_energy": 0.8},
        POP_HAPPY,
    )
    joined = " ".join(reasons)
    assert "genre" not in joined      # genre rule did not fire
    assert "mood" in joined           # mood rule still fired


def test_conflicting_prefs_still_rank_without_crashing():
    """High energy + chill mood is contradictory but must still return a ranking."""
    results = recommend_songs(
        {"favorite_mood": "chill", "target_energy": 0.9}, CATALOG, k=3
    )
    assert len(results) == 3
    # Results are sorted highest-first.
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)

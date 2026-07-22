import csv
from operator import itemgetter
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Scoring weights (the "personality" of the recommender).
# Change these to run experiments — e.g. drop GENRE_WEIGHT to 0.5.
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 1.0


def _clamp01(value: float) -> float:
    """Clamp a number into the [0.0, 1.0] range."""
    return max(0.0, min(1.0, value))


def _same(a: str, b: str) -> bool:
    """Case- and whitespace-insensitive text match."""
    return str(a).strip().lower() == str(b).strip().lower()

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score every song against the profile and return the top k (Ranking Rule)."""
        prefs = self._prefs_from_profile(user)
        scored = [(song, score_song(prefs, self._song_to_dict(song))[0]) for song in self.songs]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language reason string for why this song fits the profile."""
        prefs = self._prefs_from_profile(user)
        score, reasons = score_song(prefs, self._song_to_dict(song))
        if not reasons:
            return f"{song.title} scored {score:.2f} but had no strong matches."
        return f"{song.title} (score {score:.2f}): " + "; ".join(reasons)

    @staticmethod
    def _prefs_from_profile(user: UserProfile) -> Dict:
        """Adapt a UserProfile dataclass into the dict score_song expects."""
        return {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

    @staticmethod
    def _song_to_dict(song: Song) -> Dict:
        """Adapt a Song dataclass into the dict score_song expects."""
        return {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
        }

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV into a list of dicts, converting numeric columns to numbers."""
    float_fields = {"energy", "valence", "danceability", "acousticness"}

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip blank lines that DictReader may yield as empty rows.
            if not row.get("id"):
                continue
            song: Dict = dict(row)
            song["id"] = int(row["id"])
            song["tempo_bpm"] = int(row["tempo_bpm"])
            for field in float_fields:
                song[field] = float(row[field])
            songs.append(song)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences and return (score, reasons)."""
    genre_pref = user_prefs.get("favorite_genre", user_prefs.get("genre"))
    mood_pref = user_prefs.get("favorite_mood", user_prefs.get("mood"))
    energy_pref = user_prefs.get("target_energy", user_prefs.get("energy"))
    likes_acoustic = user_prefs.get("likes_acoustic")  # None = rule skipped

    score = 0.0
    reasons: List[str] = []

    # Rule 1 — genre match (strongest signal, highest weight).
    # Case-insensitive so "Pop" still matches "pop".
    if genre_pref is not None and _same(song["genre"], genre_pref):
        score += GENRE_WEIGHT
        reasons.append(f"matches your favorite genre ({song['genre']})")

    # Rule 2 — mood match (also case-insensitive)
    if mood_pref is not None and _same(song["mood"], mood_pref):
        score += MOOD_WEIGHT
        reasons.append(f"matches your mood ({song['mood']})")

    # Rule 3 — energy proximity (closeness to target, not raw value).
    # Clamp the target to [0, 1] so out-of-range input can't push the score negative.
    if energy_pref is not None:
        target = _clamp01(float(energy_pref))
        closeness = 1 - abs(song["energy"] - target)
        score += ENERGY_WEIGHT * closeness
        reasons.append(
            f"energy {song['energy']:.2f} is close to your target {target:.2f}"
        )

    # Rule 4 — acoustic preference lever
    if likes_acoustic is not None:
        if likes_acoustic:
            score += ACOUSTIC_WEIGHT * song["acousticness"]
            reasons.append(f"acoustic feel ({song['acousticness']:.2f}) matches your taste")
        else:
            score += ACOUSTIC_WEIGHT * (1 - song["acousticness"])
            reasons.append(f"low acousticness ({song['acousticness']:.2f}) matches your taste")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation), highest first."""
    # Use score_song as the "judge" for every song in the catalog.
    # Each item becomes (song, score, reasons).
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Ranking Rule: sort by score (index 1) high -> low, then keep the top k.
    ranked = sorted(scored, key=itemgetter(1), reverse=True)[:k]

    # Turn each reasons list into a readable explanation string (top k only).
    return [
        (song, score, "; ".join(reasons) if reasons else "no strong matches")
        for song, score, reasons in ranked
    ]

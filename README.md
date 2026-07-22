# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version recommends songs from a small catalog by comparing each song against
a user's "taste profile." Every song carries a set of features (genre, mood, and
numeric audio attributes like energy and acousticness), and the user profile stores
the preferences to match against. A scoring rule turns each song into a single number
based on how well it fits the profile, and a ranking rule sorts those scores to pick
the top recommendations — each with a short explanation of why it was chosen.

---

## How The System Works

### What features does each `Song` use?

Each `Song` stores nine fields. Some are identity, the rest are features used for
matching. Some matches are direct (genre and mood), while the numeric audio attributes
are compared on a `0–1` scale to gauge how good a fit they are:

- **Identity (not scored):** `id`, `title`, `artist`
- **Categorical taste features:** `genre`, `mood`
- **Numeric audio features (0–1):** `energy`, `valence`, `danceability`, `acousticness`
- **Numeric (raw scale):** `tempo_bpm`

The current scoring rule uses `genre`, `mood`, `energy`, and `acousticness`. The other
numeric features (`valence`, `danceability`, `tempo_bpm`) stay in the data for future
experiments.

### What information does the `UserProfile` store?

The profile stores only the *preferences* the system scores against — not a full copy
of a song. It has four fields, chosen to cover three different kinds of preference:

| Field | Example | Kind of preference |
|---|---|---|
| `favorite_genre` | `"lofi"` | categorical match |
| `favorite_mood` | `"chill"` | categorical match |
| `target_energy` | `0.4` | numeric proximity target (0–1) |
| `likes_acoustic` | `True` | boolean lever |

### How does the `Recommender` compute a score?

For each song we start at `0.0` and apply four rules (the **Scoring Rule**). Genre is
weighted highest because it is the most reliable taste signal:

| Rule | Points | How |
|---|---|---|
| Genre match | `+2.0` | if `song.genre == favorite_genre` |
| Mood match | `+1.0` | if `song.mood == favorite_mood` |
| Energy proximity | `0 → +1.0` | `1 - abs(song.energy - target_energy)` |
| Acoustic preference | `0 → +1.0` | `acousticness` if `likes_acoustic` else `1 - acousticness` |

The **maximum score is 5.0**. Energy uses *closeness* to the target, not the raw value —
a song exactly at the target scores best, and it falls off whether the song is too
energetic or too calm.

### How do you choose which songs to recommend?

A separate **Ranking Rule** takes the scored songs, sorts them from highest to lowest,
and returns the top `k` (default 5). Keeping scoring (per song) and ranking (across the
list) separate means we can change *how songs are judged* independently from *how many
we show*.

```
songs ──► score each song ──► sort by score (high → low) ──► take top k ──► recommendations
           (Scoring Rule)            (Ranking Rule)
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Running `python -m src.main` with the starter profile (`genre=pop`, `mood=happy`,
`energy=0.8`) produces the following output:

```
============================================================
  🎵  Music Recommender
============================================================
Taste profile:
  • genre         : pop
  • mood          : happy
  • energy        : 0.8

Top 5 recommendations:
------------------------------------------------------------
 1. Sunrise City — Neon Echo
    Score: 3.98   [pop / happy]
    Why:
      • matches your favorite genre (pop)
      • matches your mood (happy)
      • energy 0.82 is close to your target 0.80
------------------------------------------------------------
 2. Gym Hero — Max Pulse
    Score: 2.87   [pop / intense]
    Why:
      • matches your favorite genre (pop)
      • energy 0.93 is close to your target 0.80
------------------------------------------------------------
 3. Rooftop Lights — Indigo Parade
    Score: 1.96   [indie pop / happy]
    Why:
      • matches your mood (happy)
      • energy 0.76 is close to your target 0.80
------------------------------------------------------------
 4. Concrete Kingdom — Ridge Mercer
    Score: 0.98   [hip hop / confident]
    Why:
      • energy 0.78 is close to your target 0.80
------------------------------------------------------------
 5. Night Drive Loop — Neon Echo
    Score: 0.95   [synthwave / moody]
    Why:
      • energy 0.75 is close to your target 0.80
------------------------------------------------------------
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

**General limitations**

- It only works on a tiny catalog (18 songs), so rankings are noisy.
- It does not understand lyrics or language — only the numeric/categorical features.
- Genre is weighted highest (`+2.0`), so it can over-favor one genre.
- Exact-match categoricals can't recognize *adjacent* tastes (ambient is treated as
  no more "lofi-like" than metal is).

**Edge cases found by adversarial testing**

I tried to "trick" the scoring logic with deliberately awkward profiles
(see `tests/test_adversarial.py`). Two exposed real bugs, now fixed:

| Profile | Problem | Status |
|---|---|---|
| `target_energy: 5.0` (out of range) | Energy term went strongly **negative**, poisoning the ranking | ✅ Fixed — target is clamped to `[0, 1]` |
| `genre: "Pop"` (wrong case) | Silently failed to match `"pop"`, so the user's main preference was ignored | ✅ Fixed — matching is now case-insensitive |

Remaining behaviors that are *by design* but worth knowing:

- **Conflicting preferences** (e.g. `mood: chill` + `target_energy: 0.9`) are resolved
  by letting the categorical match win, so a "high-energy" seeker can still be handed
  a calm song.
- **Empty profile** (`{}`) scores every song `0.0` and returns them in catalog order —
  the "recommendations" are then just the first rows of the file.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this




# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**TuneMatch 1.0**

A simple song recommender that matches songs to a user's taste.

---

## 2. Intended Use  

It suggests songs a user might like.

- The user gives a taste profile: a favorite genre, a favorite mood, a target energy
  level, and whether they like acoustic music.
- The model ranks the songs and returns the top few, each with a reason.
- It assumes the user can name one clear genre and mood.
- This is for classroom exploration, not for real users.

---

## 3. How the Model Works  

Every song has a genre, a mood, and some numbers. The numbers describe the sound, like
how much energy it has and how acoustic it is.

The user says what they like. Then the model gives each song points:

- Same genre gets the most points.
- Same mood gets some points.
- Songs close to the user's energy level get points.
- Acoustic songs get points if the user likes acoustic music.

The model adds up the points for each song. Then it sorts the songs from most points to
fewest and shows the top ones.

**Changes from the starter:** I filled in the empty functions. I made genre and mood
matching ignore capital letters. I also stopped a bad energy value from making scores
go negative.

---

## 4. Data  

The catalog has 18 songs.

- Genres include pop, lofi, rock, jazz, ambient, synthwave, indie pop, hip hop,
  classical, reggae, folk, metal, edm, r&b, and country.
- Moods include happy, chill, intense, relaxed, moody, focused, and more.
- I added 8 new songs to make the catalog more varied.
- A lot of musical taste is missing. There are no lyrics, no language, and no culture.
  The model only knows the sound features in the file.

---

## 5. Strengths  

It works well for clear tastes.

- A "chill lofi" user gets chill lofi songs.
- A "gym" user gets loud, high-energy songs.
- Opposite users get opposite songs. That matched what I expected.
- The energy rule works well. Low-energy users get calm songs.
- Every pick comes with a reason, so it is easy to see why a song was chosen.

---

## 6. Limitations and Bias 

The system has some clear weak spots.

- It does not read lyrics or language.
- It only knows 18 songs, so results are noisy.
- Genre gets the most points, so it can over-favor one genre.
- Rare genres cause big score jumps. Jazz has only one song, so that song wins easily
  and then scores drop fast.
- Matching is exact. It cannot tell that ambient is close to lofi, so near-matches get
  no credit.
- Users with an unusual taste (a genre with few songs) get worse results than users
  with a common taste like pop.

---

## 7. Evaluation  

How I checked whether the recommender behaved as expected.

### Profiles I tested

Four "persona" profiles chosen to stress different corners of the feature space,
plus a set of adversarial edge cases (documented in the README and
`tests/test_adversarial.py`).

| Persona | genre | mood | target_energy | likes_acoustic |
|---|---|---|---|---|
| **Studier** | lofi | chill | 0.40 | True |
| **Gym** | pop | intense | 0.95 | False |
| **Acoustic soul** | jazz | relaxed | 0.40 | True |
| **Happy pop** | pop | happy | 0.80 | False |

Top-3 results (E = energy, A = acousticness):

```
Studier        -> Library Rain (lofi, E0.35 A0.86) | Midnight Coding (lofi) | Focus Flow (lofi)
Gym            -> Gym Hero (pop, E0.93 A0.05)      | Sunrise City (pop)     | Storm Runner (rock)
Acoustic soul  -> Coffee Shop Stories (jazz, E0.37 A0.89) | Grandfather's Porch (folk) | Library Rain (lofi)
Happy pop      -> Sunrise City (pop, E0.82 A0.18)  | Gym Hero (pop)         | Rooftop Lights (indie pop)
```

### What I looked for

- Did each persona's top songs actually match its preferences (right energy band,
  right acoustic feel, right genre/mood)?
- Did *different* profiles produce *different* top lists (i.e. does the system
  discriminate), and did any overlap make sense?

### Pairwise comparisons

- **Studier vs Gym** — Near-perfect opposites, zero overlap. Studier gets calm,
  acoustic lofi (E ≈ 0.35–0.42); Gym gets loud, electric pop/rock (E ≈ 0.82–0.93).
  Makes sense: `target_energy` 0.40 vs 0.95 and `likes_acoustic` True vs False push
  in opposite directions on *both* continuous features at once.
- **Studier vs Acoustic soul** — Same *sound* (both low-energy + acoustic), different
  *label*. They share Library Rain, but the `+2.0` genre weight sends Studier to lofi
  and Acoustic soul to jazz for the #1 slot. This shows genre acts as the tiebreaker
  among songs that are sonically similar.
- **Studier vs Happy pop** — Differ on every axis (genre, energy, acoustic), so no
  overlap. Calm lofi vs upbeat pop — exactly the separation you'd expect.
- **Gym vs Acoustic soul** — The strongest contrast in the whole set: opposite on
  energy *and* acousticness. High-energy electric tracks vs quiet acoustic ones, no
  shared songs.
- **Gym vs Happy pop** — The *most similar* pair, and the most interesting. Both are
  pop, non-acoustic, high-ish energy, so Sunrise City and Gym Hero appear in **both**
  top-3s — just reordered. Gym ranks Gym Hero #1 (intense mood + E0.93 ≈ 0.95); Happy
  pop ranks Sunrise City #1 (happy mood + E0.82 ≈ 0.80). Here only the mood match and a
  0.15 difference in `target_energy` decide the order.
- **Acoustic soul vs Happy pop** — Opposites again: quiet jazz/folk vs upbeat pop, no
  overlap.

### What surprised me

- **The Gym vs Happy pop overlap.** Two clearly different users ("workout" vs "feel
  good") share two of three songs. The system's ability to tell "loud pop" users apart
  is subtle — driven only by mood and a small energy-target gap — which shows how coarse
  the features are on a tiny catalog.
- **A scoring cliff for rare genres.** For the Acoustic soul profile, the #1 jazz match
  scores 4.86 but #2 drops all the way to 1.87. There is only *one* jazz song in the
  catalog, so the `+2.0` genre bonus can apply to exactly one track; everything else
  competes on energy + acoustic alone. Sparse genres create big score gaps.
- **Sound can beat label.** Library Rain (lofi) shows up for the Acoustic soul (jazz)
  profile anyway, because a low-energy, high-acoustic song fits the *feel* even without
  the genre match. The numeric features carry real signal on their own.

### Simple tests / comparisons I ran

- `tests/test_recommender.py` — the starter tests (ranking + explanation).
- `tests/test_adversarial.py` — edge cases (case-insensitivity, out-of-range energy,
  empty profile, nonexistent genre, conflicting preferences).

---

## 8. Future Work  

Here is how I would improve the model next.

- Add more songs so results are less noisy.
- Let users pick more than one genre or mood.
- Treat similar genres as related, so lofi and ambient can share credit.
- Use more features, like danceability and how positive a song feels.
- Make sure the top list is not all one genre.

---

## 9. Personal Reflection  

I learned that a recommender is really just points and sorting. The system does not
"understand" music. It only compares numbers and labels.

The surprising part was how much one feature can control the results. Giving genre the
most points made it the biggest factor. I also saw that a small catalog makes the
results noisy and easy to skew.

Now I think differently about music apps. When one recommends a song, it is making
choices about what "similar" means. Those choices can quietly favor some tastes over
others.

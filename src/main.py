"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

LINE_WIDTH = 60


def print_profile(user_prefs: dict) -> None:
    """Print the taste profile the recommendations are based on."""
    print("=" * LINE_WIDTH)
    print("  🎵  Music Recommender")
    print("=" * LINE_WIDTH)
    print("Taste profile:")
    for key, value in user_prefs.items():
        print(f"  • {key:<14}: {value}")
    print()


def print_recommendations(recommendations: list) -> None:
    """Print each recommendation with its title, score, and reasons."""
    print(f"Top {len(recommendations)} recommendations:")
    print("-" * LINE_WIDTH)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank:>2}. {song['title']} — {song['artist']}")
        print(f"    Score: {score:.2f}   [{song['genre']} / {song['mood']}]")
        print("    Why:")
        # The explanation is a "; "-joined string of the scoring reasons.
        for reason in explanation.split("; "):
            print(f"      • {reason}")
        print("-" * LINE_WIDTH)


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print()
    print_profile(user_prefs)
    print_recommendations(recommendations)


if __name__ == "__main__":
    main()

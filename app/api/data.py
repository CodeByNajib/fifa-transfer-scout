import numpy as np
import pandas as pd
from pathlib import Path

from app.api.constants import POSITIONS, MIN_OVERALL_RATING

# New path: looks directly in the folder where the code runs (or in the container root)
DATA_PATH = Path("players_22.csv")


# Loads and cleans the FIFA 22 player dataset from the data directory
def load_data() -> pd.DataFrame:
    """Load and clean FIFA 22 player dataset."""
    # Checks if the file exists to produce a clear error message
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Could not find {DATA_PATH}. Check the path!")

    df = pd.read_csv(DATA_PATH, low_memory=False)
    columns = [
        "short_name",
        "long_name",
        "age",
        "overall",
        "potential",
        "value_eur",
        "wage_eur",
        "player_positions",
        "club_name",
        "nationality_name",
        "league_name",
    ]
    df = df[columns].dropna()
    df["value_eur"] = df["value_eur"].astype(float)
    df["wage_eur"] = df["wage_eur"].astype(float)
    return df


# Returns the best players for a given position, sorted by overall rating
def get_top_players(df: pd.DataFrame, position: str, top_n: int = 10) -> pd.DataFrame:
    """Return the best player for a given position."""
    filtered = df[df["player_positions"].str.contains(position.upper(), na=False)]
    return filtered.nlargest(top_n, "overall")[
        [
            "short_name",
            "age",
            "overall",
            "potential",
            "value_eur",
            "club_name",
            "player_positions",
        ]
    ]


# Finds players with high rating relative to their market value, excludes GK and players below 75
def get_undervalued_players(
    df: pd.DataFrame, max_value: float, top_n: int = 10
) -> pd.DataFrame:
    """Find players with high rating relative to their market value."""
    budget_players = df[
        (df["value_eur"] <= max_value)
        & (df["overall"] >= MIN_OVERALL_RATING)
        & (~df["player_positions"].str.contains("GK", na=False))
    ].copy()
    overall = np.array(budget_players["overall"])
    values = np.array(budget_players["value_eur"])
    budget_players["value_score"] = overall / (values / 1_000_000 + 1)
    return budget_players.nlargest(top_n, "value_score")[
        [
            "short_name",
            "age",
            "overall",
            "value_eur",
            "club_name",
            "player_positions",
            "value_score",
        ]
    ]


# Calculates peak age and average rating per position across all players
def get_peak_age_by_position(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate average peak age per position."""
    positions = POSITIONS
    results = []
    for pos in positions:
        group = df[df["player_positions"].str.contains(pos, na=False)]
        if len(group) > 0:
            peak_age = group.loc[group["overall"].idxmax(), "age"]
            avg_rating = np.mean(group["overall"].values)
            results.append(
                {
                    "position": pos,
                    "peak_age": peak_age,
                    "avg_rating": round(avg_rating, 1),
                    "player_count": len(group),
                }
            )
    return pd.DataFrame(results)


# Count number of players per country and return a dictionary
def get_nationality_counts(df):
    counts = df["nationality_name"].value_counts().reset_index()
    counts.columns = ["country", "player_count"]
    return counts

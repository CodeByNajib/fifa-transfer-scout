import pandas as pd
import numpy as np
from pathlib import Path


# Path to dataset
DATA_PATH = Path(__file__).parent.parent / "data" / "players_22.csv"


# Loads and cleans the FIFA 22 player dataset from the data directory
def load_data() -> pd.DataFrame:
    """Load and clean FIFA 22 player dataset."""
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
    return df


# Returns the best players for a given position, sorted by overall rating
def get_top_players(df: pd.DataFrame, position: str, top_n: int = 10) -> pd.DataFrame:
    """Return the best player for a given position."""
    filtered = df[df["player_positions"].str.contains(position.upper(), na=False)]
    return filtered.nlargest(top_n, "overall")[
        ["short_name", "age", "overall", "potential", "value_eur", "club_name"]
    ]


# Finds players with high rating relative to their market value, excludes GK and players below 75
def get_undervalued_players(
    df: pd.DataFrame, max_value: float, top_n: int = 10
) -> pd.DataFrame:
    """Find players with high rating relative to their market value."""
    budget_players = df[
        (df["value_eur"] <= max_value)
        & (df["overall"] >= 75)
        & (~df["player_positions"].str.contains("GK", na=False))
    ].copy()
    budget_players["value_score"] = budget_players["overall"] / (
        budget_players["value_eur"] / 1_000_000 + 1
    )
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
    positions = ["GK", "CB", "CM", "CAM", "ST", "LW", "RW"]
    results = []
    for pos in positions:
        group = df[df["player_positions"].str.contains(pos, na=False)]
        if len(group) > 0:
            peak_age = group.loc[group["overall"].idxmax(), "age"]
            avg_rating = group["overall"].mean()
            results.append(
                {
                    "position": pos,
                    "peak_age": peak_age,
                    "avg_rating": round(avg_rating, 1),
                    "player_count": len(group),
                }
            )
    return pd.DataFrame(results)

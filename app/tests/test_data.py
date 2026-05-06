import pytest
import pandas as pd
from app.api.data import (
    get_top_players,
    get_undervalued_players,
    get_peak_age_by_position,
)


# Fixture - creates a small tests dataset used across all tests
@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "short_name": [
                "L. Messi",
                "R. Lewandowski",
                "K. Mbappe",
                "Patrick Goltz",
                "Alex Test",
            ],
            "age": [34, 32, 22, 36, 28],
            "overall": [93, 92, 91, 75, 80],
            "potential": [93, 92, 95, 75, 85],
            "value_eur": [78000000.0, 119500000.0, 194000000.0, 800000.0, 5000000.0],
            "wage_eur": [3200000.0, 270000.0, 23000.0, 5000.0, 20000.0],
            "player_positions": ["RW, ST, CF", "ST", "ST, LW", "GK", "CM"],
            "club_name": ["PSG", "Bayern", "PSG", "Schalke", "Ajax"],
            "nationality_name": [
                "Argentina",
                "Poland",
                "France",
                "Germany",
                "Netherlands",
            ],
            "league_name": [
                "Ligue 1",
                "Bundesliga",
                "Ligue 1",
                "Bundesliga",
                "Eredivisie",
            ],
        }
    )


# Tests that get_top_players returns correct number of players for a position
def test_get_top_players_return_correct_count(sample_df):
    result = get_top_players(sample_df, "ST", top_n=2)
    assert len(result) == 2


# Tests that results are sorted by overall rating descending
def test_get_top_players_sorted_by_rating(sample_df):
    result = get_top_players(sample_df, "ST", top_n=3)
    ratings = result["overall"].tolist()
    assert ratings == sorted(ratings, reverse=True)


# Tests that position filtering works case-insensitively
def test_get_top_players_case_insensitive(sample_df):
    result_upper = get_top_players(sample_df, "ST", top_n=5)
    result_lower = get_top_players(sample_df, "st", top_n=5)
    assert len(result_upper) == len(result_lower)


# Tests that undervalued players excludes GKs and respects max value
def test_get_undervalued_excludes_gk(sample_df):
    result = get_undervalued_players(sample_df, max_value=10_000_000, top_n=5)
    assert "GK" not in result["player_positions"].values


# Tests that peak age function returns a DataFrame with expected columns
def test_get_peak_age_returns_correct_columns(sample_df):
    result = get_peak_age_by_position(sample_df)
    assert "position" in result.columns
    assert "peak_age" in result.columns
    assert "avg_rating" in result.columns

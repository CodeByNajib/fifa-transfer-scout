import pytest
from pathlib import Path
from app.api import database
from app.api.database import (
    init_db,
    save_scout_query,
    get_scout_history,
    clear_scout_history,
    add_to_watchlist,
    get_watchlist,
    remove_from_watchlist,
)

# Eksempel på en spiller der bruges i flere tests
SAMPLE_PLAYER = {
    "short_name": "L. Messi",
    "age": 34,
    "overall": 93,
    "potential": 93,
    "player_positions": "RW",
    "nationality_name": "Argentina",
    "value_eur": 78000000.0,
}

SAMPLE_PLAYER_2 = {
    "short_name": "C. Ronaldo",
    "age": 36,
    "overall": 91,
    "potential": 91,
    "player_positions": "ST",
    "nationality_name": "Portugal",
    "value_eur": 45000000.0,
}


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    # Omdirigerer DB_PATH til en midlertidig fil så tests ikke rammer produktionsdatabasen
    temp_db = tmp_path / "test_scout.db"
    monkeypatch.setattr(database, "DB_PATH", temp_db)
    init_db()
    yield


# ─── Scout historik tests ──────────────────────────────────────────────────────


def test_save_and_get_scout_history():
    # Gemmer et spørgsmål og verificerer at det kan hentes igen
    save_scout_query("Is Messi good?", "Yes, he is the best.", "RW")
    history = get_scout_history()

    assert len(history) == 1
    assert history[0]["query"] == "Is Messi good?"
    assert history[0]["response"] == "Yes, he is the best."
    assert history[0]["position"] == "RW"


def test_scout_history_newest_first():
    # Verificerer at nyeste spørgsmål returneres først
    save_scout_query("First question", "First answer", "ST")
    save_scout_query("Second question", "Second answer", "CB")
    history = get_scout_history()

    assert history[0]["query"] == "Second question"
    assert history[1]["query"] == "First question"


def test_scout_history_limit():
    # Verificerer at limit-parameteren virker korrekt
    for i in range(5):
        save_scout_query(f"Question {i}", f"Answer {i}", "CM")

    history = get_scout_history(limit=3)
    assert len(history) == 3


def test_clear_scout_history():
    # Verificerer at al historik slettes korrekt
    save_scout_query("Question", "Answer", "GK")
    clear_scout_history()
    history = get_scout_history()

    assert len(history) == 0


def test_save_scout_query_without_position():
    # Verificerer at position kan være None
    save_scout_query("Generic question", "Generic answer", None)
    history = get_scout_history()

    assert history[0]["position"] is None


# ─── Watchlist tests ───────────────────────────────────────────────────────────


def test_add_to_watchlist():
    # Verificerer at en spiller kan tilføjes til watchlisten
    result = add_to_watchlist(SAMPLE_PLAYER)
    assert result["added"] is True


def test_get_watchlist():
    # Verificerer at spillere i watchlisten kan hentes
    add_to_watchlist(SAMPLE_PLAYER)
    watchlist = get_watchlist()

    assert len(watchlist) == 1
    assert watchlist[0]["short_name"] == "L. Messi"
    assert watchlist[0]["overall"] == 93


def test_watchlist_newest_first():
    # Verificerer at nyeste tilføjede spiller returneres først
    add_to_watchlist(SAMPLE_PLAYER)
    add_to_watchlist(SAMPLE_PLAYER_2)
    watchlist = get_watchlist()

    assert watchlist[0]["short_name"] == "C. Ronaldo"


def test_add_duplicate_player():
    # Verificerer at UNIQUE constraint forhindrer duplikater
    add_to_watchlist(SAMPLE_PLAYER)
    result = add_to_watchlist(SAMPLE_PLAYER)

    assert result["added"] is False
    assert "already in your watchlist" in result["reason"]


def test_remove_from_watchlist():
    # Verificerer at en spiller kan fjernes fra watchlisten via ID
    add_to_watchlist(SAMPLE_PLAYER)
    watchlist = get_watchlist()
    player_id = watchlist[0]["id"]

    result = remove_from_watchlist(player_id)
    assert result["removed"] is True
    assert len(get_watchlist()) == 0


def test_remove_nonexistent_player():
    # Verificerer at sletning af ikke-eksisterende spiller returnerer korrekt besked
    result = remove_from_watchlist(999)

    assert result["removed"] is False
    assert result["reason"] == "Player not found"


def test_multiple_players_in_watchlist():
    # Verificerer at flere spillere kan gemmes samtidigt
    add_to_watchlist(SAMPLE_PLAYER)
    add_to_watchlist(SAMPLE_PLAYER_2)
    watchlist = get_watchlist()

    assert len(watchlist) == 2

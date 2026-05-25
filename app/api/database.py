import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/app/data/scout.db")


def get_connection() -> sqlite3.Connection:
    # Creates a connection to the SQLite database and returns dict-like rows
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    # Creates tables on first startup if they don't already exist
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS scout_history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                query     TEXT    NOT NULL,
                response  TEXT    NOT NULL,
                position  TEXT,
                timestamp TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS watchlist (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                short_name  TEXT    NOT NULL,
                age         INTEGER,
                overall     INTEGER,
                potential   INTEGER,
                position    TEXT,
                nationality TEXT,
                value_eur   REAL,
                added_at    TEXT    NOT NULL,
                UNIQUE(short_name)
            );
        """)


# ─── Scout history ────────────────────────────────────────────────────────────


def save_scout_query(query: str, response: str, position: str | None) -> None:
    # Saves AI scout questions and answers in the database with a timestamp
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO scout_history (query, response, position, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (query, response, position, datetime.now().isoformat(timespec="seconds")),
        )


def get_scout_history(limit: int = 20) -> list[dict]:
    # Fetches the most recent AI scout messages sorted with newest first
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM scout_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def clear_scout_history() -> None:
    # Deletes all scout history from the database
    with get_connection() as conn:
        conn.execute("DELETE FROM scout_history")


# ─── Watchlist ────────────────────────────────────────────────────────────────


def add_to_watchlist(player: dict) -> dict:
    # Adds a player to the watchlist - UNIQUE(short_name) prevents duplicates
    with get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO watchlist
                    (short_name, age, overall, potential, position, nationality, value_eur, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    player.get("short_name"),
                    player.get("age"),
                    player.get("overall"),
                    player.get("potential"),
                    player.get("player_positions"),
                    player.get("nationality_name"),
                    player.get("value_eur"),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            return {"added": True}
        except sqlite3.IntegrityError:
            # Returns an error message if the player already exists in the watchlist
            return {
                "added": False,
                "reason": f"{player.get('short_name')} is already in your watchlist",
            }


def get_watchlist() -> list[dict]:
    # Fetches all players in the watchlist sorted with most recently added first
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM watchlist ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


def remove_from_watchlist(player_id: int) -> dict:
    # Removes a player from the watchlist by ID - rowcount 0 means the player was not found
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM watchlist WHERE id = ?", (player_id,))
    if cursor.rowcount == 0:
        return {"removed": False, "reason": "Player not found"}
    return {"removed": True}

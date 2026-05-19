import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/app/data/scout.db")


def get_connection() -> sqlite3.Connection:
    # Opretter forbindelse til SQLite databasen og returnerer dict-lignende rows
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    # Opretter tabeller ved første opstart hvis de ikke allerede findes
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


# ─── Scout historik ───────────────────────────────────────────────────────────


def save_scout_query(query: str, response: str, position: str | None) -> None:
    # Gemmer AI-scout spørgsmål og svar i databasen med tidsstempel
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO scout_history (query, response, position, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (query, response, position, datetime.now().isoformat(timespec="seconds")),
        )


def get_scout_history(limit: int = 20) -> list[dict]:
    # Henter de seneste AI-scout beskeder sorteret med nyeste først
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM scout_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def clear_scout_history() -> None:
    # Sletter al scout historik fra databasen
    with get_connection() as conn:
        conn.execute("DELETE FROM scout_history")


# ─── Watchlist ────────────────────────────────────────────────────────────────


def add_to_watchlist(player: dict) -> dict:
    # Tilføjer en spiller til watchlisten - UNIQUE(short_name) forhindrer duplikater
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
            # Returnerer fejlbesked hvis spilleren allerede findes i watchlisten
            return {
                "added": False,
                "reason": f"{player.get('short_name')} is already in your watchlist",
            }


def get_watchlist() -> list[dict]:
    # Henter alle spillere i watchlisten sorteret med senest tilføjede først
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM watchlist ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


def remove_from_watchlist(player_id: int) -> dict:
    # Fjerner en spiller fra watchlisten via ID - rowcount 0 betyder spilleren ikke fandtes
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM watchlist WHERE id = ?", (player_id,))
    if cursor.rowcount == 0:
        return {"removed": False, "reason": "Player not found"}
    return {"removed": True}

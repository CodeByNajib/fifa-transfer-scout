import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import os
import httpx
from dotenv import load_dotenv

# SQLite database functions
from app.api.database import (
    init_db,
    save_scout_query,
    get_scout_history,
    clear_scout_history,
)
from app.api.database import add_to_watchlist, get_watchlist, remove_from_watchlist

# Import of project modules
from app.api.constants import DEFAULT_MAX_VALUE
from app.api.data import (
    load_data,
    get_top_players,
    get_undervalued_players,
    get_peak_age_by_position,
    get_nationality_counts,
)
from app.api.scout_ai import ask_scout_assistant

load_dotenv()

app = FastAPI(title="FIFA Transfer Scout API")


# Data validation model for AI queries (ensures correct data transfer from Streamlit)
class ScoutQuery(BaseModel):
    query: str
    context_data: List[dict]  # List of players that serve as context for the AI


@app.on_event("startup")
def startup_event() -> None:
    # Load the dataset and create database tables on startup
    app.state.df = load_data()
    init_db()


# --- PLAYER ENDPOINTS ---


# Root endpoint for quick verification that the server is running
@app.get("/")
def read_root() -> dict:
    return {
        "message": "FIFA Transfer Scout API is running. Visit /docs for Swagger UI."
    }


# Returns a list of the best players for a given position
@app.get("/players/top/{position}")
def top_players(request: Request, position: str, top_n: int = 10) -> list[dict]:
    # Converts position to uppercase to match the dataset (e.g. 'st' -> 'ST')
    result = get_top_players(request.app.state.df, position.upper(), top_n)
    if result.empty:
        raise HTTPException(
            status_code=404, detail=f"No players found for position: {position}"
        )
    return result.to_dict(orient="records")


# Returns undervalued players below a specific market value in EUR
@app.get("/players/undervalued")
def undervalued_players(
    request: Request, max_value: float = DEFAULT_MAX_VALUE, top_n: int = 10
) -> list[dict]:
    result = get_undervalued_players(request.app.state.df, max_value, top_n)
    if result.empty:
        raise HTTPException(status_code=404, detail="No undervalued players found")
    return result.to_dict(orient="records")


# Returns average peak age and rating per position
@app.get("/players/peak-age")
def peak_age(request: Request) -> list[dict]:
    result = get_peak_age_by_position(request.app.state.df)
    return result.to_dict(orient="records")


# AI Scout endpoint: connects filtered data with Mistral AI (RAG-light logic)
@app.post("/players/ask-scout")
def ask_scout(payload: ScoutQuery) -> dict:
    # Validates that player data has been provided with the request
    if not payload.context_data:
        raise HTTPException(
            status_code=400, detail="No player data provided as context."
        )

    # Converts the received JSON data back to a Pandas DataFrame
    context_df = pd.DataFrame(payload.context_data)

    try:
        # Calls the AI assistant with the correct import logic (Mistral client)
        answer = ask_scout_assistant(payload.query, context_df)

        # Saves the question and answer in the SQLite database
        save_scout_query(
            query=payload.query,
            response=answer,
            position=payload.context_data[0].get("player_positions")
            if payload.context_data
            else None,
        )

        return {"answer": answer}
    except Exception as e:
        # Returns a 500 error if problems occur with the API call to Mistral
        raise HTTPException(status_code=500, detail=f"AI Assistant error: {str(e)}")


# Geographic endpoint: allows Streamlit to fetch nationality data
@app.get("/players/nationality")
def player_nationality(request: Request) -> list[dict]:
    result = get_nationality_counts(request.app.state.df)
    return result.to_dict(orient="records")


# Live match data from football-data.org (project requirement)
@app.get("/transfers/news")
async def get_football_news() -> dict:
    # Fetches current football matches and results from an external API
    api_key = os.getenv("FOOTBALL_DATA_API_KEY")
    url = "https://api.football-data.org/v4/matches"
    headers: dict[str, str] = {"X-Auth-Token": api_key} if api_key is not None else {}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": "Could not fetch live data", "details": response.text}
        return response.json()


# --- SCOUT HISTORY ENDPOINTS ---


# Returns the most recent AI scout questions and answers
@app.get("/scout/history")
def scout_history(limit: int = 20) -> list[dict]:
    return get_scout_history(limit=limit)


# Deletes all scout history
@app.delete("/scout/history")
def delete_scout_history() -> dict:
    clear_scout_history()
    return {"message": "History cleared"}


# --- WATCHLIST ENDPOINTS ---


# Adds a player to the watchlist
@app.post("/watchlist")
def watchlist_add(player: dict) -> dict:
    result = add_to_watchlist(player)
    if not result["added"]:
        raise HTTPException(status_code=409, detail=result["reason"])
    return result


# Returns all players in the watchlist
@app.get("/watchlist")
def watchlist_get() -> list[dict]:
    return get_watchlist()


# Removes a player from the watchlist by ID
@app.delete("/watchlist/{player_id}")
def watchlist_remove(player_id: int) -> dict:
    result = remove_from_watchlist(player_id)
    if not result["removed"]:
        raise HTTPException(status_code=404, detail=result["reason"])
    return result

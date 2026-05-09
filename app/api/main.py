import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import httpx
from dotenv import load_dotenv

# SQLite databasefunktioner
from app.api.database import (
    init_db,
    save_scout_query,
    get_scout_history,
    clear_scout_history,
)
from app.api.database import add_to_watchlist, get_watchlist, remove_from_watchlist

# Import af mine egne moduler fra projektstrukturen
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


# Datavalideringsmodel til AI-forespørgsler (sikrer korrekt dataoverførsel fra Streamlit)
class ScoutQuery(BaseModel):
    query: str
    context_data: List[dict]  # Liste af spillere som fungerer som kontekst for AI'en


@app.on_event("startup")
def startup_event():
    # Indlæs datasættet og opret databasetabeller ved opstart
    global df
    df = load_data()
    init_db()


# --- PLAYER ENDPOINTS ---


# Root endpoint til hurtig verificering af at serveren kører
@app.get("/")
def read_root():
    return {
        "message": "FIFA Transfer Scout API is running. Visit /docs for Swagger UI."
    }


# Returnerer en liste over de bedste spillere for en given position
@app.get("/players/top/{position}")
def top_players(position: str, top_n: int = 10):
    # Konverterer position til store bogstaver for at matche datasættet (f.eks. 'st' -> 'ST')
    result = get_top_players(df, position.upper(), top_n)
    if result.empty:
        raise HTTPException(
            status_code=404, detail=f"No players found for position: {position}"
        )
    return result.to_dict(orient="records")


# Returnerer undervurderede spillere under en specifik markedsværdi i EUR
@app.get("/players/undervalued")
def undervalued_players(max_value: float = 10_000_000, top_n: int = 10):
    result = get_undervalued_players(df, max_value, top_n)
    if result.empty:
        raise HTTPException(status_code=404, detail="No undervalued players found")
    return result.to_dict(orient="records")


# Returnerer gennemsnitlig peak-alder og rating per position
@app.get("/players/peak-age")
def peak_age():
    result = get_peak_age_by_position(df)
    return result.to_dict(orient="records")


# AI Scout endpoint: Forbinder filtreret data med Mistral AI (RAG-light logik)
@app.post("/players/ask-scout")
def ask_scout(payload: ScoutQuery):
    # Validerer at der er sendt spillerdata med forespørgslen
    if not payload.context_data:
        raise HTTPException(
            status_code=400, detail="No player data provided as context."
        )

    # Konverterer den modtagne JSON-data tilbage til en Pandas DataFrame
    context_df = pd.DataFrame(payload.context_data)

    try:
        # Kalder AI-assistenten med den korrekte import-logik (Mistral client)
        answer = ask_scout_assistant(payload.query, context_df)

        # Gemmer spørgsmål og svar i SQLite databasen
        save_scout_query(
            query=payload.query,
            response=answer,
            position=payload.context_data[0].get("player_positions")
            if payload.context_data
            else None,
        )

        return {"answer": answer}
    except Exception as e:
        # Returnerer en 500-fejl hvis der opstår problemer med API-kaldet til Mistral
        raise HTTPException(status_code=500, detail=f"AI Assistant error: {str(e)}")


# Geografisk endpoint: Så Streamlit kan hente nationalitetsdata
@app.get("/players/nationality")
def player_nationality():
    result = get_nationality_counts(df)
    return result.to_dict(orient="records")


# Live kampdata fra football-data.org (krav i opgavebeskrivelse)
@app.get("/transfers/news")
async def get_football_news():
    # Henter aktuelle fodboldkampe og resultater fra et eksternt API
    api_key = os.getenv("FOOTBALL_DATA_API_KEY")
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": api_key}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": "Could not fetch live data", "details": response.text}
        return response.json()


# --- SCOUT HISTORY ENDPOINTS ---


# Returnerer de seneste AI-scout spørgsmål og svar
@app.get("/scout/history")
def scout_history(limit: int = 20):
    return get_scout_history(limit=limit)


# Sletter al scout historik
@app.delete("/scout/history")
def delete_scout_history():
    clear_scout_history()
    return {"message": "History cleared"}


# --- WATCHLIST ENDPOINTS ---


# Tilføjer en spiller til watchlisten
@app.post("/watchlist")
def watchlist_add(player: dict):
    result = add_to_watchlist(player)
    if not result["added"]:
        raise HTTPException(status_code=409, detail=result["reason"])
    return result


# Returnerer alle spillere i watchlisten
@app.get("/watchlist")
def watchlist_get():
    return get_watchlist()


# Fjerner en spiller fra watchlisten via ID
@app.delete("/watchlist/{player_id}")
def watchlist_remove(player_id: int):
    result = remove_from_watchlist(player_id)
    if not result["removed"]:
        raise HTTPException(status_code=404, detail=result["reason"])
    return result

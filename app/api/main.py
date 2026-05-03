import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Import af dine egne moduler fra projektstrukturen
from app.api.data import (
    load_data,
    get_top_players,
    get_undervalued_players,
    get_peak_age_by_position,
)
from app.api.scout_ai import ask_scout_assistant

app = FastAPI(title="FIFA Transfer Scout API")

# Indlæs datasættet ved opstart (players_22.csv)
df = load_data()


# Datavalideringsmodel til AI-forespørgsler (sikrer korrekt dataoverførsel fra Streamlit)
class ScoutQuery(BaseModel):
    query: str
    context_data: List[dict]  # Liste af spillere som fungerer som kontekst for AI'en


# --- API ENDPOINTS ---


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
    """
    Modtager et spørgsmål og en liste af spillere.
    Sender forespørgslen videre til AI-assistenten i scout_ai.py.
    """
    if not payload.context_data:
        raise HTTPException(
            status_code=400, detail="No player data provided as context."
        )

    # Konverterer den modtagne JSON-data tilbage til en Pandas DataFrame
    context_df = pd.DataFrame(payload.context_data)

    try:
        # Kalder AI-assistenten med den korrekte import-logik (Mistral client)
        answer = ask_scout_assistant(payload.query, context_df)
        return {"answer": answer}
    except Exception as e:
        # Returnerer en 500-fejl hvis der opstår problemer med API-kaldet til Mistral
        raise HTTPException(status_code=500, detail=f"AI Assistant error: {str(e)}")

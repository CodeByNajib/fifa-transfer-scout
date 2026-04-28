from fastapi import FastAPI, HTTPException
from app.api.data import (
    load_data,
    get_top_players,
    get_undervalued_players,
    get_peak_age_by_position,
)

app = FastAPI(title="FIFA Transfer Scout API")

df = load_data()


# Returns a list of the top players for a given position
@app.get("/players/top/{position}")
def top_players(position: str, top_n: int = 10):
    result = get_top_players(df, position, top_n)
    if result.empty:
        raise HTTPException(
            status_code=404, detail=f"No players found for position: {position}"
        )
    return result.to_dict(orient="records")


# Returns undervalued players below a given market value in EUR
@app.get("/players/undervalued")
def undervalued_players(max_value: float = 10_000_000, top_n: int = 10):
    result = get_undervalued_players(df, max_value, top_n)
    if result.empty:
        raise HTTPException(status_code=404, detail="No undervalued players found")
    return result.to_dict(orient="records")


# Returns peak age and average rating per position
@app.get("/players/peak-age")
def peak_age():
    result = get_peak_age_by_position(df)
    return result.to_dict(orient="records")

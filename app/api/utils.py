import streamlit as st


def format_market_value(value: float) -> str:
    return f"€{value / 1_000_000:.1f}M"


def handle_api_error(res) -> bool:
    """Show feedback for a failed API response. Returns True if an error occurred.

    409 Conflict → st.warning (e.g. duplicate watchlist entry).
    All other 4xx/5xx → st.error with status code.
    Falls back to a generic message if the response body is not valid JSON.
    """
    if res.status_code < 400:
        return False
    try:
        detail = res.json().get("detail", "Unknown error")
    except Exception:
        detail = "Unknown error"
    if res.status_code == 409:
        st.warning(detail)
    else:
        st.error(f"Error {res.status_code}: {detail}")
    return True

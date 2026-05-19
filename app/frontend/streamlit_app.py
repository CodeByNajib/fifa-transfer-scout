import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import plotly.express as px

from app.api.constants import POSITIONS
from app.api.utils import format_market_value, handle_api_error

# Streamlit-kode bruger denne miljøvariabel
API_URL = os.getenv("API_URL", "http://localhost:8000")


def render_watchlist_button(row: dict, prefix: str) -> None:
    if st.button("+ Watchlist", key=f"{prefix}_{row['short_name']}"):
        res = requests.post(f"{API_URL}/watchlist", json=row)
        if res.status_code == 200:
            st.success(f"{row['short_name']} added!")
        else:
            handle_api_error(res)

st.set_page_config(
    page_title="FIFA Transfer Scout",
    page_icon="assets/logo.png" if False else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS - dark scouting aesthetic
st.markdown(
    """
<style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #2d333b; }
    .scout-title { font-size: 2.2rem; font-weight: 700; color: #58a6ff; letter-spacing: -1px; margin-bottom: 0; }
    .scout-sub { font-size: 0.9rem; color: #8b949e; margin-top: 0; margin-bottom: 2rem; }
    .metric-card { background: #161b22; border: 1px solid #2d333b; border-radius: 10px; padding: 1rem 1.5rem; }
    .stat-value { font-size: 1.8rem; font-weight: 700; color: #58a6ff; }
    .stat-label { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="stDataFrame"] { border: 1px solid #2d333b; border-radius: 8px; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<p class="scout-title">FIFA TRANSFER SCOUT</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="scout-sub">FIFA 22 - Data-driven player analysis</p>',
    unsafe_allow_html=True,
)

# Initialisér aktiv side i session state hvis den ikke findes
if "page" not in st.session_state:
    st.session_state.page = "[TOP]  Players"

# Custom CSS til knap-navigation i sidebar
st.markdown(
    """
<style>
    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        text-align: left;
        background: transparent;
        border: 0.5px solid #2d333b;
        border-radius: 6px;
        color: #8b949e;
        font-size: 12px;
        font-family: monospace;
        padding: 6px 10px;
        margin-bottom: 4px;
        transition: all 0.15s;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: #21262d;
        color: #c9d1d9;
        border-color: #444c56;
    }
    [data-testid="stSidebar"] .stButton button:focus {
        background: #1f3a5f;
        color: #58a6ff;
        border-color: #58a6ff;
        box-shadow: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar navigationsknapper
with st.sidebar:
    st.markdown("### Analysis Mode")
    st.markdown("---")

    pages = [
        "[TOP]  Players",
        "[GEM]  Hidden Gems",
        "[PEAK]  Career Peak",
        "[MAP]  World Map",
        "[LIST]  Watchlist",
        "[LOG]  History",
        "[AI]  Scout Assistant",
        "[NEWS]  Live Football",
    ]

    # Vis en knap per side - klik sætter session state
    for p in pages:
        if st.button(p, key=f"nav_{p}"):
            st.session_state.page = p

    st.markdown("---")
    st.markdown(
        '<p style="color:#8b949e; font-size:0.75rem;">Data: FIFA 22 · 19,000+ players</p>',
        unsafe_allow_html=True,
    )

# Hent aktiv side fra session state
page = st.session_state.page


# --- Top Players ---
if page == "[TOP]  Players":
    st.markdown("### [TOP] Best players by position")

    col1, col2 = st.columns([2, 1])
    with col1:
        position = st.selectbox(
            "",
            POSITIONS,
            label_visibility="collapsed",
        )
    with col2:
        top_n = st.slider("Show top", 5, 20, 10)

    response = requests.get(
        f"{API_URL}/players/top/{position}", params={"top_n": top_n}
    )

    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        # Opsummeringsmetrikker øverst
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg. Rating", f"{df['overall'].mean():.1f}")
        c2.metric("Avg. Age", f"{df['age'].mean():.1f} yrs")
        c3.metric("Avg. Value", format_market_value(df["value_eur"].mean()))

        # Vandret søjlediagram
        fig, ax = plt.subplots(figsize=(8, top_n * 0.4 + 1), facecolor="#0e1117")
        ax.set_facecolor("#0e1117")
        colors = [
            "#58a6ff" if r >= 88 else "#388bfd" if r >= 84 else "#1f6feb"
            for r in df["overall"]
        ]
        bars = ax.barh(
            df["short_name"][::-1], df["overall"][::-1], color=colors[::-1], height=0.6
        )
        ax.set_xlabel("Overall Rating", color="#8b949e")
        ax.tick_params(colors="#8b949e")
        ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
        ax.set_xlim(df["overall"].min() - 3, df["overall"].max() + 3)
        for bar, val in zip(bars, df["overall"][::-1]):
            ax.text(
                bar.get_width() + 0.2,
                bar.get_y() + bar.get_height() / 2,
                str(val),
                va="center",
                color="#c9d1d9",
                fontsize=9,
            )
        fig.tight_layout()
        st.pyplot(fig)

        # Tabel med watchlist-knap per spiller
        st.markdown("#### Player List")
        value_fmts = df["value_eur"].apply(format_market_value)
        for row, value_fmt in zip(df.to_dict("records"), value_fmts):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"**{row['short_name']}** &nbsp;|&nbsp; {row['player_positions']} &nbsp;|&nbsp; ⭐ {row['overall']} &nbsp;|&nbsp; {value_fmt}"
                )
            with col2:
                render_watchlist_button(row, "watch_top")
    else:
        handle_api_error(response)


# --- Hidden Gems ---
elif page == "[GEM]  Hidden Gems":
    st.markdown("### [GEM] Undervalued players - high quality, low cost")

    col1, col2 = st.columns([2, 1])
    with col1:
        max_value = st.slider("Max market value (€M)", 1, 50, 10) * 1_000_000
    with col2:
        top_n = st.slider("Show top", 5, 20, 10)

    response = requests.get(
        f"{API_URL}/players/undervalued",
        params={"max_value": max_value, "top_n": top_n},
    )

    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        c1, c2, c3 = st.columns(3)
        c1.metric("Avg. Rating", f"{df['overall'].mean():.1f}")
        c2.metric("Avg. Value", format_market_value(df["value_eur"].mean()))
        c3.metric("Best value score", f"{df['value_score'].max():.1f}")

        # Scatter: rating vs. markedsværdi - hover viser spillernavn interaktivt
        fig = px.scatter(
            df,
            x=df["value_eur"] / 1_000_000,
            y="overall",
            color="value_score",
            hover_name="short_name",
            hover_data={
                "overall": True,
                "value_score": ":.1f",
                "player_positions": True,
                "club_name": True,
            },
            color_continuous_scale="Blues",
            labels={
                "x": "Market Value (€M)",
                "overall": "Overall Rating",
                "value_score": "Value Score",
            },
        )
        fig.update_traces(marker=dict(size=12, line=dict(width=1, color="#58a6ff")))
        fig.update_layout(
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font=dict(color="#c9d1d9"),
            yaxis=dict(range=[70, 85], gridcolor="#2d333b"),
            xaxis=dict(gridcolor="#2d333b"),
            coloraxis_colorbar=dict(title="Score"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabel med watchlist-knap per spiller
        st.markdown("#### Player List")
        value_fmts = df["value_eur"].apply(format_market_value)
        for row, value_fmt in zip(df.to_dict("records"), value_fmts):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"**{row['short_name']}** &nbsp;|&nbsp; {row['player_positions']} &nbsp;|&nbsp; ⭐ {row['overall']} &nbsp;|&nbsp; Score: {row['value_score']:.1f} &nbsp;|&nbsp; {value_fmt}"
                )
            with col2:
                render_watchlist_button(row, "watch_gem")
    else:
        handle_api_error(response)


# --- Career Peak ---
elif page == "[PEAK]  Career Peak":
    st.markdown("### [PEAK] When do players peak - by position?")

    response = requests.get(f"{API_URL}/players/peak-age")

    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        fig, axes = plt.subplots(1, 2, figsize=(10, 4), facecolor="#0e1117")

        # Peak-alder per position
        ax = axes[0]
        ax.set_facecolor("#0e1117")
        colors = [
            "#58a6ff" if a >= 32 else "#388bfd" if a >= 29 else "#1f6feb"
            for a in df["peak_age"]
        ]
        ax.bar(df["position"], df["peak_age"], color=colors, width=0.6)
        ax.set_ylim(20, 40)
        ax.set_title("Peak Age per Position", color="#c9d1d9", pad=12)
        ax.set_ylabel("Age", color="#8b949e")
        ax.tick_params(colors="#8b949e")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#2d333b")
        for i, (pos, age) in enumerate(zip(df["position"], df["peak_age"])):
            ax.text(i, age + 0.3, str(age), ha="center", color="#c9d1d9", fontsize=9)

        # Gennemsnitsrating per position
        ax2 = axes[1]
        ax2.set_facecolor("#0e1117")
        ax2.bar(df["position"], df["avg_rating"], color="#388bfd", width=0.6)
        ax2.set_title("Avg. Rating per Position", color="#c9d1d9", pad=12)
        ax2.set_ylabel("Rating", color="#8b949e")
        ax2.tick_params(colors="#8b949e")
        ax2.spines[["top", "right", "left"]].set_visible(False)
        ax2.spines["bottom"].set_color("#2d333b")
        ax2.set_ylim(60, 70)
        for i, (pos, r) in enumerate(zip(df["position"], df["avg_rating"])):
            ax2.text(i, r + 0.1, str(r), ha="center", color="#c9d1d9", fontsize=9)

        fig.tight_layout()
        st.pyplot(fig)

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        handle_api_error(response)


# --- World Map ---
elif page == "[MAP]  World Map":
    st.markdown("### [MAP] Global Player Distribution")
    st.markdown(
        "This map visualizes the nationality of all players in the dataset using GeoPandas."
    )

    response = requests.get(f"{API_URL}/players/nationality")

    if response.status_code == 200:
        counts_df = pd.DataFrame(response.json())

        # Hent verdenskortet direkte fra Natural Earth data
        world = gpd.read_file(
            "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        )

        # Map navne for at sikre bedre match (FIFA navne vs. kortnavn)
        name_map = {
            "United States": "United States of America",
            "England": "United Kingdom",
            "China PR": "China",
        }
        counts_df["country"] = counts_df["country"].replace(name_map)

        # Merge FIFA-data med verdenskortet
        world = world.merge(counts_df, left_on="ADMIN", right_on="country", how="left")
        world["player_count"] = world["player_count"].fillna(0)

        fig, ax = plt.subplots(1, 1, figsize=(15, 8), facecolor="#0e1117")
        ax.set_facecolor("#0e1117")

        # Tegn kortet med farveintensitet baseret på spillerantal
        world.plot(
            column="player_count",
            ax=ax,
            legend=True,
            legend_kwds={"label": "Number of Players", "orientation": "horizontal"},
            cmap="Blues",
            edgecolor="#2d333b",
            linewidth=0.5,
            missing_kwds={"color": "#161b22"},
        )

        ax.set_axis_off()
        fig.tight_layout()
        st.pyplot(fig)

        # Top 10 lande i tabel under kortet
        st.markdown("#### Distribution Details")
        st.dataframe(counts_df.head(10), use_container_width=True, hide_index=True)
    else:
        handle_api_error(response)


# --- My Watchlist ---
elif page == "[LIST]  Watchlist":
    st.markdown("### [LIST] My Watchlist")

    res = requests.get(f"{API_URL}/watchlist")
    if handle_api_error(res):
        st.stop()
    players = res.json()

    if not players:
        st.info(
            "Your watchlist is empty - add players from Top Players or Hidden Gems."
        )
    else:
        st.markdown(f"**{len(players)} players saved**")
        st.divider()

        # Vis hver spiller med metrics og slet-knap
        for player in players:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                st.markdown(
                    f"**{player['short_name']}**  \n{player['nationality']} · {player['position']}"
                )
            with col2:
                st.metric("Rating", player["overall"])
            with col3:
                st.metric("Potential", player["potential"])
            with col4:
                st.metric("Value", format_market_value(player["value_eur"]))
            with col5:
                st.write("")
                # Fjern spiller fra watchlisten via DELETE-endpoint
                if st.button("Remove", key=f"del_{player['id']}"):
                    del_res = requests.delete(f"{API_URL}/watchlist/{player['id']}")
                    if del_res.status_code == 200:
                        st.rerun()
                    else:
                        handle_api_error(del_res)
            st.divider()


# --- AI Scout Assistant ---
elif page == "[AI]  Scout Assistant":
    st.markdown("### [AI] Scout Assistant")
    st.markdown("Ask the AI scout anything about players for a specific position.")

    position = st.selectbox("Select position", POSITIONS, label_visibility="visible")

    top_response = requests.get(f"{API_URL}/players/top/{position}", params={"top_n": 10})
    if handle_api_error(top_response):
        st.stop()
    context_data = top_response.json()

    query = st.text_area("Your question", placeholder="e.g. Who is the best value-for-money striker?", height=100)

    if st.button("Ask Scout") and query.strip():
        with st.spinner("Thinking..."):
            ask_response = requests.post(
                f"{API_URL}/players/ask-scout",
                json={"query": query, "context_data": context_data},
            )
        if ask_response.status_code == 200:
            st.markdown("#### Scout Answer")
            st.markdown(ask_response.json().get("answer", ""))
        else:
            handle_api_error(ask_response)


# --- Live Football News ---
elif page == "[NEWS]  Live Football":
    st.markdown("### [NEWS] Live Football - Today's Matches")

    response = requests.get(f"{API_URL}/transfers/news")

    if response.status_code == 200:
        data = response.json()

        if "error" in data:
            st.error(f"Could not fetch live data: {data.get('details', '')}")
        else:
            matches = data.get("matches", [])

            if not matches:
                st.info("No matches found for today.")
            else:
                STATUS_COLORS = {
                    "FINISHED": "#3fb950",
                    "IN_PLAY": "#58a6ff",
                    "PAUSED": "#d29922",
                    "SCHEDULED": "#8b949e",
                    "POSTPONED": "#f85149",
                    "CANCELLED": "#f85149",
                    "SUSPENDED": "#d29922",
                }

                c1, c2, c3 = st.columns(3)
                c1.metric("Total Matches", len(matches))
                c2.metric(
                    "Live",
                    sum(1 for m in matches if m.get("status") in ("IN_PLAY", "PAUSED")),
                )
                c3.metric(
                    "Finished",
                    sum(1 for m in matches if m.get("status") == "FINISHED"),
                )

                st.markdown("---")

                for match in matches:
                    home = match.get("homeTeam", {}).get("name", "Unknown")
                    away = match.get("awayTeam", {}).get("name", "Unknown")
                    utc_date = match.get("utcDate", "")
                    status = match.get("status", "SCHEDULED")
                    score = match.get("score", {}).get("fullTime", {})
                    home_score = score.get("home")
                    away_score = score.get("away")

                    try:
                        dt = pd.to_datetime(utc_date).strftime("%d %b %Y  %H:%M UTC")
                    except Exception:
                        dt = utc_date

                    color = STATUS_COLORS.get(status, "#8b949e")
                    score_str = (
                        f"**{home_score} – {away_score}**"
                        if home_score is not None and away_score is not None
                        else "vs"
                    )

                    col1, col2, col3 = st.columns([4, 2, 2])
                    with col1:
                        st.markdown(f"**{home}** &nbsp; {score_str} &nbsp; **{away}**")
                        st.markdown(
                            f'<span style="color:#8b949e; font-size:0.8rem;">{dt}</span>',
                            unsafe_allow_html=True,
                        )
                    with col2:
                        competition = (
                            match.get("competition", {}).get("name", "")
                        )
                        st.markdown(
                            f'<span style="color:#8b949e; font-size:0.8rem;">{competition}</span>',
                            unsafe_allow_html=True,
                        )
                    with col3:
                        st.markdown(
                            f'<span style="color:{color}; font-size:0.8rem; font-weight:600;">{status}</span>',
                            unsafe_allow_html=True,
                        )
                    st.divider()
    else:
        handle_api_error(response)


# --- Scout History ---
elif page == "[LOG]  History":
    st.markdown("### [LOG] Scout History")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("Your previous AI scout questions and answers")
    with col2:
        # Slet al historik via DELETE-endpoint
        if st.button("Clear history"):
            del_res = requests.delete(f"{API_URL}/scout/history")
            if not handle_api_error(del_res):
                st.rerun()

    res = requests.get(f"{API_URL}/scout/history")
    if handle_api_error(res):
        st.stop()
    history = res.json()

    if not history:
        st.info("No history yet - ask the AI scout a question!")
    else:
        # Vis hvert spørgsmål/svar i en collapsible expander
        for entry in history:
            with st.expander(f"{entry['timestamp']}  |  {entry['query'][:60]}..."):
                st.markdown(f"**Question:** {entry['query']}")
                st.markdown(f"**Position:** {entry['position'] or 'Not specified'}")
                st.divider()
                st.markdown(f"**Answer:**  \n{entry['response']}")

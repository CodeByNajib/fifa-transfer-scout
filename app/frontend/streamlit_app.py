import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import httpx

# Streamlit-kode bruger denne miljøvariabel
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Når API'en kaldes:
response = httpx.get(f"{API_URL}/players/top/ST")


st.set_page_config(
    page_title="FIFA Transfer Scout",
    page_icon="assets/logo.png" if False else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS — dark scouting aesthetic
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
    '<p class="scout-sub">FIFA 22 — Data-driven player analysis</p>',
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("### Analysis Mode")
    page = st.radio(
        "",
        ["Top Players", "Hidden Gems", "Career Peak", "World Map"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        '<p style="color:#8b949e; font-size:0.75rem;">Data: FIFA 22 · 19,000+ players</p>',
        unsafe_allow_html=True,
    )


# --- Top Players ---
if page == "Top Players":
    st.markdown("### Best players by position")

    col1, col2 = st.columns([2, 1])
    with col1:
        position = st.selectbox(
            "",
            ["ST", "CM", "CAM", "CB", "GK", "LW", "RW"],
            label_visibility="collapsed",
        )
    with col2:
        top_n = st.slider("Show top", 5, 20, 10)

    response = requests.get(
        f"{API_URL}/players/top/{position}", params={"top_n": top_n}
    )

    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        # Summary metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg. Rating", f"{df['overall'].mean():.1f}")
        c2.metric("Avg. Age", f"{df['age'].mean():.1f} yrs")
        c3.metric("Avg. Value", f"€{df['value_eur'].mean() / 1_000_000:.1f}M")

        # Horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, top_n * 0.5 + 1), facecolor="#0e1117")
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

        # Table
        df_display = df.copy()
        df_display["value_eur"] = df["value_eur"].apply(
            lambda x: f"€{x / 1_000_000:.1f}M"
        )
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# --- Hidden Gems ---
elif page == "Hidden Gems":
    st.markdown("### Undervalued players - high quality, low cost")

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
        c2.metric("Avg. Value", f"€{df['value_eur'].mean() / 1_000_000:.1f}M")
        c3.metric("Best value score", f"{df['value_score'].max():.1f}")

        # Scatter: rating vs value
        fig, ax = plt.subplots(figsize=(10, 5), facecolor="#0e1117")
        ax.set_facecolor("#0e1117")
        scatter = ax.scatter(
            df["value_eur"] / 1_000_000,
            df["overall"],
            c=df["value_score"],
            cmap="Blues",
            s=120,
            edgecolors="#58a6ff",
            linewidths=0.5,
        )
        for _, row in df.iterrows():
            ax.annotate(
                row["short_name"],
                (row["value_eur"] / 1_000_000, row["overall"]),
                textcoords="offset points",
                xytext=(8, 5),
                fontsize=8,
                color="#c9d1d9",
                fontweight="bold",
            )
        ax.set_xlabel("Market Value (€M)", color="#8b949e")
        ax.set_ylabel("Overall Rating", color="#8b949e")
        ax.set_ylim(70, 85)  # Fixed range so the plot doesn't zoom in too much
        ax.tick_params(colors="#8b949e")
        ax.spines[["top", "right", "bottom", "left"]].set_color("#2d333b")
        fig.tight_layout()
        st.pyplot(fig)

        df_display = df.copy()
        df_display["value_eur"] = df["value_eur"].apply(
            lambda x: f"€{x / 1_000_000:.1f}M"
        )
        df_display["value_score"] = df["value_score"].apply(lambda x: f"{x:.1f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# --- Career Peak ---
elif page == "Career Peak":
    st.markdown("### When do players peak - by position?")

    response = requests.get(f"{API_URL}/players/peak-age")

    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor="#0e1117")

        # Peak age bar
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

        # Avg rating bar
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

# --- World Map ---
elif page == "World Map":
    st.markdown("### Global Player Distribution")
    st.markdown(
        "This map visualizes the nationality of all players in the dataset using GeoPandas."
    )

    response = requests.get(f"{API_URL}/players/nationality")

    if response.status_code == 200:
        counts_df = pd.DataFrame(response.json())

        # Hent indbygget verdenskort fra geopandas
        # Hent verdenskortet direkte fra Natural Earth data
        world = gpd.read_file(
            "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        )

        # Map navne for at sikre bedre match (FIFA navne vs Kort navne)
        name_map = {
            "United States": "United States of America",
            "England": "United Kingdom",
            "China PR": "China",
        }
        counts_df["country"] = counts_df["country"].replace(name_map)

        # Merge FIFA data med verdenskort
        world = world.merge(counts_df, left_on="ADMIN", right_on="country", how="left")
        world["player_count"] = world["player_count"].fillna(0)

        # Plotting
        fig, ax = plt.subplots(1, 1, figsize=(15, 10), facecolor="#0e1117")
        ax.set_facecolor("#0e1117")

        # Tegn kortet
        world.plot(
            column="player_count",
            ax=ax,
            legend=True,
            legend_kwds={"label": "Number of Players", "orientation": "horizontal"},
            cmap="Blues",
            edgecolor="#2d333b",
            linewidth=0.5,
            missing_kwds={"color": "#161b22"},  # Lande uden data bliver mørke
        )

        ax.set_axis_off()
        fig.tight_layout()
        st.pyplot(fig)

        # Vis top 10 lande i en tabel nedenunder
        st.markdown("#### Distribution Details")
        st.dataframe(counts_df.head(10), use_container_width=True, hide_index=True)

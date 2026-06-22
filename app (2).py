import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Avenged Sevenfold – Spotify Explorer",
    page_icon="🤘",
    layout="wide",
)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("avenged_songs.csv")
    df["duration_min"] = (df["duration_ms"] / 60000).round(2)
    df["release_year"] = pd.to_datetime(df["release_date"]).dt.year
    return df

df = load_data()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🤘 Avenged Sevenfold – Spotify Explorer")
st.markdown("Eksplorasi data audio features dari **175 lagu** A7X di Spotify.")
st.divider()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("🎛️ Filter")
albums = ["Semua Album"] + sorted(df["album"].unique().tolist())
selected_album = st.sidebar.selectbox("Album", albums)

if selected_album != "Semua Album":
    filtered = df[df["album"] == selected_album]
else:
    filtered = df.copy()

audio_features = ["danceability", "energy", "speechiness", "acousticness",
                  "instrumentalness", "liveness", "valence"]
feature_x = st.sidebar.selectbox("Sumbu X (Scatter)", audio_features, index=1)  # energy
feature_y = st.sidebar.selectbox("Sumbu Y (Scatter)", audio_features, index=6)  # valence

# ── KPI cards ────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("🎵 Total Lagu", len(filtered))
col2.metric("💿 Album", filtered["album"].nunique())
col3.metric("⭐ Avg Popularity", f"{filtered['popularity'].mean():.1f}")
col4.metric("⏱️ Avg Durasi", f"{filtered['duration_min'].mean():.2f} min")

st.divider()

# ── Row 1: Popularity per album & Top songs ───────────────────────────────────
r1c1, r1c2 = st.columns([3, 2])

with r1c1:
    st.subheader("📊 Rata-rata Popularitas per Album")
    pop_album = (
        df.groupby("album")["popularity"]
        .mean()
        .reset_index()
        .sort_values("popularity", ascending=True)
    )
    fig = px.bar(
        pop_album, x="popularity", y="album", orientation="h",
        color="popularity", color_continuous_scale="Reds",
        labels={"popularity": "Popularitas", "album": "Album"},
    )
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    st.subheader("🏆 Top 10 Lagu Terpopuler")
    top10 = (
        filtered[["name", "album", "popularity"]]
        .sort_values("popularity", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    top10.index += 1
    st.dataframe(top10, use_container_width=True, height=370)

st.divider()

# ── Row 2: Scatter & Radar ────────────────────────────────────────────────────
r2c1, r2c2 = st.columns(2)

with r2c1:
    st.subheader(f"🔵 {feature_x.capitalize()} vs {feature_y.capitalize()}")
    fig2 = px.scatter(
        filtered, x=feature_x, y=feature_y,
        color="album", hover_data=["name", "popularity"],
        labels={feature_x: feature_x.capitalize(), feature_y: feature_y.capitalize()},
    )
    fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend=dict(font_size=10))
    st.plotly_chart(fig2, use_container_width=True)

with r2c2:
    st.subheader("🕸️ Audio Features – Rata-rata per Album")
    radar_albums = st.multiselect(
        "Pilih album untuk dibandingkan",
        options=sorted(df["album"].unique().tolist()),
        default=sorted(df["album"].unique().tolist())[:3],
    )
    fig3 = go.Figure()
    for alb in radar_albums:
        vals = df[df["album"] == alb][audio_features].mean().tolist()
        vals += [vals[0]]
        cats = audio_features + [audio_features[0]]
        fig3.add_trace(go.Scatterpolar(r=vals, theta=cats, fill="toself", name=alb))
    fig3.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(font_size=10),
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Row 3: Energy & Tempo distribution ───────────────────────────────────────
r3c1, r3c2 = st.columns(2)

with r3c1:
    st.subheader("⚡ Distribusi Energy")
    fig4 = px.histogram(
        filtered, x="energy", nbins=20, color_discrete_sequence=["#e63946"],
        labels={"energy": "Energy"},
    )
    fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig4, use_container_width=True)

with r3c2:
    st.subheader("🥁 Distribusi Tempo (BPM)")
    fig5 = px.histogram(
        filtered, x="tempo", nbins=20, color_discrete_sequence=["#457b9d"],
        labels={"tempo": "Tempo (BPM)"},
    )
    fig5.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ── Raw data table ────────────────────────────────────────────────────────────
with st.expander("📋 Lihat Data Lengkap"):
    cols_show = ["name", "album", "release_date", "popularity", "duration_min",
                 "energy", "danceability", "valence", "tempo", "acousticness"]
    st.dataframe(filtered[cols_show].reset_index(drop=True), use_container_width=True)

st.caption("Data source: Spotify API via Kaggle · Dataset: avenged_songs.csv")

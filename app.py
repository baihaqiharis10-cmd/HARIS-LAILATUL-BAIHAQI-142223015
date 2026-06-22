import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Avenged Sevenfold – Song Explorer",
    page_icon="🤘",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Metal+Mania&family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] { background-color: #0d0d0d; color: #e8e8e8; }

    h1, h2, h3 {
        font-family: 'Metal Mania', cursive !important;
        letter-spacing: 2px;
    }

    .stMetric {
        background: #1a1a1a;
        border: 1px solid #ff2e2e33;
        border-radius: 10px;
        padding: 12px 16px;
    }

    .stMetric label { color: #ff2e2e !important; font-size: 0.75rem !important; text-transform: uppercase; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #ffffff !important; }

    .stSlider > div { color: #ff2e2e; }
    .stMultiSelect span { background: #ff2e2e !important; }

    section[data-testid="stSidebar"] { background: #111111; border-right: 1px solid #ff2e2e33; }
    section[data-testid="stSidebar"] * { color: #e8e8e8 !important; }

    .block-container { padding-top: 2rem; }

    hr { border-color: #ff2e2e44; }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("avenged_songs.csv")
    df["release_date"] = pd.to_datetime(df["release_date"])
    df["release_year"] = df["release_date"].dt.year
    df["duration_min"] = (df["duration_ms"] / 60000).round(2)
    # Key mapping
    key_map = {0:"C",1:"C#",2:"D",3:"D#",4:"E",5:"F",6:"F#",7:"G",8:"G#",9:"A",10:"A#",11:"B"}
    df["key_name"] = df["key"].map(key_map)
    df["mode_name"] = df["mode"].map({1: "Major", 0: "Minor"})
    return df

df = load_data()

AUDIO_FEATURES = ["danceability","energy","speechiness","acousticness",
                  "instrumentalness","liveness","valence"]

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎚️ Filter")

albums = sorted(df["album"].unique())
sel_albums = st.sidebar.multiselect("Album", albums, default=albums)

pop_range = st.sidebar.slider(
    "Popularity", int(df["popularity"].min()), int(df["popularity"].max()),
    (int(df["popularity"].min()), int(df["popularity"].max()))
)

filtered = df[
    df["album"].isin(sel_albums) &
    df["popularity"].between(*pop_range)
]

st.sidebar.markdown(f"**{len(filtered)} lagu** ditampilkan")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🤘 Avenged Sevenfold")
st.markdown("### Spotify Song Explorer")
st.markdown("---")

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Lagu",        len(filtered))
k2.metric("Album",             filtered["album"].nunique())
k3.metric("Rata² Popularity",  f"{filtered['popularity'].mean():.1f}")
k4.metric("Rata² Energy",      f"{filtered['energy'].mean():.2f}")
k5.metric("Rata² Durasi",      f"{filtered['duration_min'].mean():.1f} min")

st.markdown("---")

# ── Row 1: popularity bar + radar ────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Top 20 Lagu Paling Populer")
    top20 = filtered.nlargest(20, "popularity")[["name","album","popularity"]]
    fig = px.bar(
        top20.sort_values("popularity"),
        x="popularity", y="name", color="album",
        orientation="h", text="popularity",
        color_discrete_sequence=px.colors.sequential.Reds_r,
    )
    fig.update_layout(
        paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d",
        font_color="#e8e8e8", showlegend=True,
        yaxis_title=None, xaxis_title="Popularity",
        legend=dict(bgcolor="#111111", bordercolor="#ff2e2e44"),
        height=460,
    )
    fig.update_traces(textposition="outside", marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Profil Audio Rata-rata")
    avg = filtered[AUDIO_FEATURES].mean()
    fig_r = go.Figure(go.Scatterpolar(
        r=avg.values,
        theta=avg.index.str.capitalize(),
        fill="toself",
        line_color="#ff2e2e",
        fillcolor="rgba(255,46,46,0.2)",
    ))
    fig_r.update_layout(
        polar=dict(
            bgcolor="#1a1a1a",
            radialaxis=dict(visible=True, range=[0,1], color="#555"),
            angularaxis=dict(color="#aaa"),
        ),
        paper_bgcolor="#0d0d0d", font_color="#e8e8e8",
        height=460,
    )
    st.plotly_chart(fig_r, use_container_width=True)

st.markdown("---")

# ── Row 2: scatter + distribution ────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Energy vs Valence")
    fig_s = px.scatter(
        filtered, x="energy", y="valence",
        color="album", size="popularity",
        hover_name="name",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_s.update_layout(
        paper_bgcolor="#0d0d0d", plot_bgcolor="#111111",
        font_color="#e8e8e8", height=380,
        legend=dict(bgcolor="#111111", bordercolor="#ff2e2e44"),
    )
    st.plotly_chart(fig_s, use_container_width=True)

with col4:
    st.subheader("Distribusi Tempo")
    fig_h = px.histogram(
        filtered, x="tempo", nbins=30,
        color_discrete_sequence=["#ff2e2e"],
    )
    fig_h.update_layout(
        paper_bgcolor="#0d0d0d", plot_bgcolor="#111111",
        font_color="#e8e8e8", height=380,
        xaxis_title="BPM", yaxis_title="Jumlah Lagu",
    )
    st.plotly_chart(fig_h, use_container_width=True)

st.markdown("---")

# ── Row 3: per-album stats + timeline ────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("Statistik per Album")
    album_stats = (
        filtered.groupby("album")
        .agg(
            Lagu=("name","count"),
            Popularity=("popularity","mean"),
            Energy=("energy","mean"),
            Danceability=("danceability","mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Popularity", ascending=False)
    )
    st.dataframe(album_stats, use_container_width=True, hide_index=True)

with col6:
    st.subheader("Popularity per Tahun Rilis")
    yearly = (
        filtered.groupby("release_year")["popularity"]
        .mean().reset_index()
        .rename(columns={"popularity":"avg_popularity"})
    )
    fig_l = px.line(
        yearly, x="release_year", y="avg_popularity",
        markers=True, color_discrete_sequence=["#ff2e2e"],
    )
    fig_l.update_layout(
        paper_bgcolor="#0d0d0d", plot_bgcolor="#111111",
        font_color="#e8e8e8", height=320,
        xaxis_title="Tahun", yaxis_title="Avg Popularity",
    )
    st.plotly_chart(fig_l, use_container_width=True)

st.markdown("---")

# ── Feature comparison by album (box plot) ───────────────────────────────────
st.subheader("Perbandingan Audio Feature per Album")
feature_sel = st.selectbox("Pilih fitur:", AUDIO_FEATURES, index=1)
fig_b = px.box(
    filtered, x="album", y=feature_sel, color="album",
    color_discrete_sequence=px.colors.qualitative.Bold,
    points="all", hover_name="name",
)
fig_b.update_layout(
    paper_bgcolor="#0d0d0d", plot_bgcolor="#111111",
    font_color="#e8e8e8", showlegend=False, height=380,
    xaxis_title=None,
)
st.plotly_chart(fig_b, use_container_width=True)

st.markdown("---")

# ── Data table ────────────────────────────────────────────────────────────────
st.subheader("📋 Data Lengkap")
cols_show = ["name","album","release_year","popularity","duration_min",
             "energy","danceability","valence","tempo","key_name","mode_name"]
st.dataframe(
    filtered[cols_show].sort_values("popularity", ascending=False),
    use_container_width=True, hide_index=True,
)

st.caption("Data source: Spotify API · Avenged Sevenfold discography")


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Avenged Sevenfold Data Mining", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("avenged_songs.csv")

df = load_data()

st.title("🎵 Avenged Sevenfold Data Mining Dashboard")

st.subheader("Dataset Preview")
st.dataframe(df.head())

st.subheader("Dataset Information")
st.write("Jumlah data:", len(df))
st.write("Jumlah kolom:", len(df.columns))

numeric_cols = df.select_dtypes(include="number").columns.tolist()

feature = st.selectbox("Pilih fitur numerik", numeric_cols)

fig, ax = plt.subplots()
df[feature].hist(ax=ax)
ax.set_title(f"Distribusi {feature}")
st.pyplot(fig)

st.subheader("Statistik Deskriptif")
st.dataframe(df[numeric_cols].describe())

if "album" in df.columns:
    st.subheader("Jumlah Lagu per Album")
    album_counts = df["album"].value_counts()
    st.bar_chart(album_counts)

st.subheader("Korelasi Fitur")
corr = df[numeric_cols].corr()
st.dataframe(corr)

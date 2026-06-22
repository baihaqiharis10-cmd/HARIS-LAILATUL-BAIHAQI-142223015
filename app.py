
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Data Mining Pelanggan", layout="wide")

st.title("📊 Data Mining Pelanggan")

uploaded_file = st.file_uploader("Upload Dataset CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Preview Dataset")
    st.dataframe(df.head())

    st.subheader("Informasi Dataset")
    st.write(df.describe())

    st.subheader("Visualisasi Pendapatan")

    fig, ax = plt.subplots()
    ax.hist(df["Pendapatan"], bins=10)
    ax.set_xlabel("Pendapatan")
    ax.set_ylabel("Jumlah")
    st.pyplot(fig)

    st.subheader("Jumlah Kategori Pelanggan")
    st.bar_chart(df["Kategori_Pelanggan"].value_counts())

else:
    st.info("Silakan upload dataset CSV terlebih dahulu.")

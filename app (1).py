import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Avenged Sevenfold Data Mining", layout="wide")

st.title("🎵 Avenged Sevenfold Songs Dataset")
st.write("Aplikasi Streamlit untuk eksplorasi dan analisis dataset lagu Avenged Sevenfold.")

uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded_file is not None:
    # ✅ FIX 1: Coba beberapa encoding untuk menghindari error UnicodeDecodeError
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        try:
            df = pd.read_csv(uploaded_file, encoding="latin1")
        except Exception as e:
            st.error(f"Gagal membaca file CSV: {e}")
            st.stop()
    except Exception as e:
        st.error(f"Gagal membaca file CSV: {e}")
        st.stop()

    # ✅ FIX 2: Validasi bahwa dataframe tidak kosong
    if df.empty:
        st.warning("File CSV kosong atau tidak memiliki data.")
        st.stop()

    st.subheader("Preview Data")
    st.dataframe(df.head())

    st.subheader("Informasi Dataset")
    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Baris", df.shape[0])
    col2.metric("Jumlah Kolom", df.shape[1])
    col3.metric("Missing Values", int(df.isna().sum().sum()))

    st.subheader("Filter Data")
    if "album" in df.columns:
        # ✅ FIX 3: Konversi ke string dulu untuk menghindari error tipe data campuran
        df["album"] = df["album"].astype(str)
        album_options = ["Semua"] + sorted(df["album"].dropna().unique().tolist())
        album = st.selectbox("Pilih Album", album_options)
        if album != "Semua":
            df = df[df["album"] == album]

    st.dataframe(df)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:
        st.subheader("Statistik Deskriptif")
        st.dataframe(df[numeric_cols].describe())

        st.subheader("Visualisasi")
        selected_col = st.selectbox("Pilih Kolom Numerik", numeric_cols)

        fig = px.histogram(
            df,
            x=selected_col,
            title=f"Distribusi {selected_col}"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ✅ FIX 4: Hanya hitung korelasi jika ada minimal 2 kolom numerik
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            fig2 = px.imshow(
                corr,
                text_auto=True,
                title="Heatmap Korelasi"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Heatmap korelasi membutuhkan minimal 2 kolom numerik.")

    else:
        st.warning("Tidak ada kolom numerik yang ditemukan dalam dataset.")

    # ✅ FIX 5: Gunakan df yang sudah difilter untuk download
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data Hasil Filter",
        data=csv_data,
        file_name="hasil_filter.csv",
        mime="text/csv"
    )

else:
    st.info("Silakan upload file CSV untuk memulai analisis.")

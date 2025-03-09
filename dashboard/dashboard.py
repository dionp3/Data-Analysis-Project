import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Load dataset
FILE_PATH = 'data/all_data.csv'

@st.cache_data
def load_data():
    """Fungsi untuk memuat dan memproses dataset."""
    df = pd.read_csv(FILE_PATH)
    df['dteday'] = pd.to_datetime(df['dteday'])

    # Mengonversi kolom kategori agar lebih efisien
    category_cols = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday', 'weathersit']
    for col in category_cols:
        df[col] = df[col].astype('category')

    return df

df = load_data()

# Sidebar Navigasi
st.sidebar.header('👤 Dibuat oleh: Dion Prayoga (dionp3)')
st.sidebar.title('🚲 Analisis Penyewaan Sepeda')
option = st.sidebar.selectbox('🔍 Pilih Analisis', 
                              ['Pengaruh Hari Libur', 'Pola Penyewaan Sepanjang Hari', 'Analisis RFM'])

# 1. Analisis Pengaruh Hari Libur terhadap Penyewaan Sepeda
if option == 'Pengaruh Hari Libur':
    st.title('📊 Pengaruh Hari Libur terhadap Peminjaman Sepeda')

    # Menghitung rata-rata penyewaan pada hari biasa dan hari libur
    average_regular_day_rentals = df[df['holiday'] == 0]['cnt'].mean()
    average_holiday_rentals = df[df['holiday'] == 1]['cnt'].mean()

    # Visualisasi dengan barplot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=['Hari Biasa', 'Hari Libur'], 
                y=[average_regular_day_rentals, average_holiday_rentals], 
                palette=['blue', 'yellow'], ax=ax)

    # Menambahkan label nilai di atas bar
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.0f}', 
                    (p.get_x() + p.get_width() / 2, p.get_height()), 
                    ha='center', va='bottom')

    ax.set_xlabel('Hari')
    ax.set_ylabel('Jumlah Peminjaman Sepeda')
    ax.set_title('Pengaruh Hari Libur Terhadap Peminjaman Sepeda')

    st.pyplot(fig)

    # Caption
    st.caption("Grafik ini menunjukkan perbandingan rata-rata jumlah peminjaman sepeda pada hari biasa dan hari libur. "
               "Dapat diamati apakah penyewaan meningkat atau menurun saat hari libur.")

# 2. Pola Penyewaan Sepeda Sepanjang Hari (Berdasarkan Jam)
elif option == 'Pola Penyewaan Sepanjang Hari':
    st.title('⏰ Pola Penyewaan Sepeda Berdasarkan Jam dalam Sehari')

    # Mengelompokkan data berdasarkan jam
    average_hourly_rentals = df.groupby('hr')['cnt'].mean()

    # Visualisasi menggunakan barplot
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=average_hourly_rentals.index, 
                y=average_hourly_rentals.values, 
                palette='viridis', ax=ax)

    # Menambahkan label nilai di atas bar
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.0f}', 
                    (p.get_x() + p.get_width() / 2, p.get_height()), 
                    ha='center', va='bottom')

    ax.set_xlabel('Jam dalam Sehari')
    ax.set_ylabel('Jumlah Peminjaman Sepeda')
    ax.set_title('Pola Penggunaan Sepeda Berdasarkan Jam')

    st.pyplot(fig)

    # Caption
    st.caption("Grafik ini menunjukkan pola peminjaman sepeda berdasarkan jam dalam sehari. "
               "Biasanya terdapat lonjakan jumlah penyewaan pada jam-jam tertentu, misalnya saat jam sibuk kerja atau jam pulang kerja.")

# 3. Analisis RFM (Recency, Frequency, Monetary)
elif option == 'Analisis RFM':
    st.title('📊📈 Analisis RFM (Recency, Frequency, Monetary)')

    # Salin dataframe untuk analisis
    rfm_df = df.copy()
    recent_date = rfm_df["dteday"].max()  # Tanggal terbaru dalam dataset

    # Hitung RFM berdasarkan hari dalam seminggu
    rfm_df = rfm_df.groupby(by="weekday", as_index=False).agg({
        "dteday": "max",   # Tanggal terakhir transaksi (untuk Recency)
        "instant": "count", # Frequency: jumlah transaksi dalam seminggu
        "cnt": "sum"        # Monetary: total sepeda yang disewa dalam seminggu
    })

    # Ubah nama kolom agar lebih mudah dipahami
    rfm_df.columns = ["weekday", "max_order_timestamp", "frequency", "monetary"]

    # Hitung Recency (selisih hari dari transaksi terakhir)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date.date() - x).days)

    # Hapus kolom timestamp setelah dihitung Recency
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    # Menampilkan tabel RFM di Streamlit
    st.write('📋 **Tabel Analisis RFM berdasarkan Hari dalam Seminggu**')
    st.dataframe(rfm_df)

    # --- VISUALISASI RFM ---
    st.subheader("📊 Distribusi RFM berdasarkan Hari")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Histogram Recency
    sns.histplot(rfm_df["recency"], bins=20, kde=True, color="purple", ax=axes[0])
    axes[0].set_title("Distribusi Recency")
    axes[0].set_xlabel("Recency (days)")
    axes[0].set_ylabel("Jumlah")

    # Histogram Frequency
    sns.histplot(rfm_df["frequency"], bins=20, kde=True, color="orange", ax=axes[1])
    axes[1].set_title("Distribusi Frequency")
    axes[1].set_xlabel("Frequency")
    axes[1].set_ylabel("Jumlah")

    # Histogram Monetary
    sns.histplot(rfm_df["monetary"], bins=20, kde=True, color="cyan", ax=axes[2])
    axes[2].set_title("Distribusi Monetary")
    axes[2].set_xlabel("Monetary")
    axes[2].set_ylabel("Jumlah")

    plt.tight_layout()
    st.pyplot(fig)

    # --- PENJELASAN ---
    st.markdown("""
    **📌 Penjelasan Analisis RFM:**  
    - **Recency (R)**: Seberapa baru transaksi terakhir terjadi dalam satu minggu.  
    - **Frequency (F)**: Seberapa sering transaksi terjadi dalam seminggu.  
    - **Monetary (M)**: Total jumlah penyewaan sepeda dalam satu minggu.  

    **📊 Hasil Visualisasi:**  
    - **Distribusi Recency** → Semakin kecil nilainya, berarti pelanggan lebih aktif menyewa sepeda baru-baru ini.  
    - **Distribusi Frequency** → Semakin besar nilainya, berarti ada lebih banyak transaksi dalam seminggu.  
    - **Distribusi Monetary** → Semakin besar nilainya, berarti jumlah penyewaan sepeda dalam seminggu lebih banyak.  
    """)
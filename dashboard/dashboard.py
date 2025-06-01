import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

# Load data
day_data = pd.read_csv("day_data.csv")
hour_data = pd.read_csv("hour_data.csv")

# Convert date column to datetime
day_data['dteday'] = pd.to_datetime(day_data['dteday'])
day_data['month'] = day_data['dteday'].dt.month

# Mapping for season and weather
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}

day_data['season'] = day_data['season'].map(season_mapping)
day_data['weathersit'] = day_data['weathersit']
hour_data['season'] = hour_data['season'].map(season_mapping)
hour_data['weathersit'] = hour_data['weathersit']

# Sidebar Filters
st.sidebar.header("Filter Data")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [day_data['dteday'].min(), day_data['dteday'].max()])
season_filter = st.sidebar.multiselect("Pilih Musim", day_data['season'].unique(), day_data['season'].unique())
weather_filter = st.sidebar.multiselect("Pilih Kondisi Cuaca", day_data['weathersit'].unique(), day_data['weathersit'].unique())

# Filter data
df_filtered = day_data[
    (day_data['dteday'].dt.date >= date_range[0]) & 
    (day_data['dteday'].dt.date <= date_range[1]) &
    (day_data['season'].isin(season_filter)) & 
    (day_data['weathersit'].isin(weather_filter))
]

# Judul dashboard
st.title("Dashboard Penyewaan Sepeda")

# Grafik Tren Penyewaan Sepeda per Bulan
st.subheader("Tren Penyewaan Sepeda per Bulan")
monthly_trend = df_filtered.groupby('month')['cnt'].sum()
fig, ax = plt.subplots()
ax.plot(monthly_trend.index, monthly_trend.values, marker='o', linestyle='-')
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

# Grafik Tren Penyewaan Sepeda per Musim
st.subheader("Tren Penyewaan Sepeda per Musim")
season_trend = df_filtered.groupby('season')['cnt'].sum()
fig, ax = plt.subplots()
ax.bar(season_trend.index, season_trend.values)
ax.set_xlabel("Musim")
ax.set_ylabel("Jumlah Penyewaan")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
st.pyplot(fig)

# Heatmap Pengaruh Cuaca dan Jam terhadap Penyewaan
st.subheader("Heatmap Pengaruh Cuaca dan Jam terhadap Penyewaan")
hour_data_pivot = hour_data.pivot_table(index='hr', columns='weathersit', values='cnt', aggfunc='sum')
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(hour_data_pivot, cmap='coolwarm', annot=True, fmt='.0f', ax=ax, linewidths=0.5)
ax.set_xlabel("Kondisi Cuaca")
ax.set_ylabel("Jam")
st.pyplot(fig)
st.markdown("""
**Keterangan Kondisi Cuaca:**  
1 = Clear, Few clouds, Partly cloudy  
2 = Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist  
3 = Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds  
4 = Heavy Rain + Ice Pellets + Thunderstorm + Mist, Snow + Fog  
""")

# Grafik Kesibukan Pelanggan setiap Jamnya
st.subheader("Kesibukan Pelanggan Setiap Jam")
hourly_trend = hour_data.groupby('hr')['cnt'].sum()
fig, ax = plt.subplots()
ax.bar(hourly_trend.index, hourly_trend.values)
ax.set_xlabel("Jam")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

# Analisis Binning
st.subheader("Analisis Binning")

# Mendefinisikan binning waktu
bins = [0, 6, 12, 18, 24]  # Binning berdasarkan waktu (malam, pagi, siang, sore)
labels = ['Malam (00-06)', 'Pagi (06-12)', 'Siang (12-18)', 'Sore (18-24)']

# Pengelompokkan ke waktu
hour_data['time_bin'] = pd.cut(hour_data['hr'], bins=bins, labels=labels, right=False)

# Menentukan pengelompokkan berdasarkan frekuensi penyewaan (cnt)
cnt_bins = [hour_data["cnt"].min(), hour_data["cnt"].quantile(0.33), 
             hour_data["cnt"].quantile(0.66), hour_data["cnt"].max()]
cnt_labels = ["Rendah", "Sedang", "Tinggi"]

# Pengelompokkan ke jumlah penyewaan
hour_data["rental_bin"] = pd.cut(hour_data["cnt"], bins=cnt_bins, labels=cnt_labels, right=False)

# Mendefinisikan binning temperature
temp_bins = [0, 0.3, 0.6, 1.0]
temp_labels = ["Dingin", "Sedang", "Panas"]

# Pengelompokan temperatur
hour_data["temp_bin"] = pd.cut(hour_data["temp"], bins=temp_bins, labels=temp_labels, right=False)

# Visualisasi Binning dengan Seaborn
st.subheader("Distribusi Penyewaan Berdasarkan Waktu Penggunaan")
time_bin_counts = hour_data['time_bin'].value_counts().sort_index()
fig, ax = plt.subplots()
sns.barplot(x=time_bin_counts.index, y=time_bin_counts.values, palette='Blues', ax=ax)
ax.set_xlabel("Waktu Penggunaan")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

st.subheader("Distribusi Penyewaan Berdasarkan Kategori Frekuensi")
rental_bin_counts = hour_data['rental_bin'].value_counts().sort_index()
fig, ax = plt.subplots()
sns.barplot(x=rental_bin_counts.index, y=rental_bin_counts.values, palette='Greens', ax=ax)
ax.set_xlabel("Kategori Penyewaan")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

st.subheader("Distribusi Penyewaan Berdasarkan Temperatur")
temp_bin_counts = hour_data['temp_bin'].value_counts().sort_index()
fig, ax = plt.subplots()
sns.barplot(x=temp_bin_counts.index, y=temp_bin_counts.values, palette='Oranges', ax=ax)
ax.set_xlabel("Kategori Temperatur")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)
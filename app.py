import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===============================
# 1. KONFIGURASI HALAMAN
# ===============================
st.set_page_config(
    page_title="Matriks Performa Pendidikan Tinggi Nasional",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# 2. PALET WARNA & GAYA
# ===============================
PRIMARY = "#2D4059"   # Navy Blue (Strategis/Kepercayaan)
DANGER = "#EA5455"    # Merah (Peringatan/Berisiko)
SECONDARY = "#F07B3F" # Oranye (Highlight)
ACCENT = "#FFD460"    # Kuning (Fokus)
BACKGROUND = "#F4F4F4"
SUCCESS = "#28C76F"   # Hijau (Positif/Patuh)

# Pengaturan Matplotlib
plt.rcParams["axes.facecolor"] = "#FFFFFF"
plt.rcParams["figure.facecolor"] = "#FFFFFF"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["text.color"] = PRIMARY
plt.rcParams["axes.labelcolor"] = PRIMARY
plt.rcParams["xtick.color"] = PRIMARY
plt.rcParams["ytick.color"] = PRIMARY

# ===============================
# 3. CUSTOM CSS (STYLING)
# ===============================
def local_css():
    st.markdown(
        f"""
        <style>
        /* Impor Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {PRIMARY};
        }}

        /* --- STYLING SIDEBAR --- */
        [data-testid="stSidebar"] {{
            background-color: {PRIMARY};
            border-right: 1px solid {PRIMARY};
        }}
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: white !important;
        }}
        
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
            color: #E0E0E0 !important;
        }}
        
        [data-testid="stSidebar"] div[role="radiogroup"] label p {{
            color: {PRIMARY} !important;
            font-weight: 600;
        }}

        /* Styling Menu Radio Button */
        div[role="radiogroup"] > label > div:first-child {{
            display: none;
        }}
        
        div[role="radiogroup"] > label {{
            background-color: white;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 8px;
            border: 1px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            cursor: pointer;
        }}

        div[role="radiogroup"] > label:hover {{
            background-color: {SECONDARY};
            transform: translateY(-2px);
        }}
        
        div[role="radiogroup"] > label:hover p {{
            color: white !important; 
        }}

        /* Sorot Item Terpilih */
        div[role="radiogroup"] > label[data-baseweb="radio"] {{
            background-color: #f8f9fa;
            border-left: 6px solid {SECONDARY};
        }}

        /* --- KARTU METRIK --- */
        [data-testid="stMetric"] {{
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-top: 3px solid {PRIMARY};
        }}
        
        [data-testid="stMetricLabel"] {{
            color: #888;
            font-size: 14px;
            font-weight: 600;
        }}
        
        [data-testid="stMetricValue"] {{
            color: {PRIMARY};
            font-weight: 700;
        }}

        /* --- HEADERS --- */
        h1, h2, h3 {{
            color: {PRIMARY};
        }}
        
        h4 {{
            color: {SECONDARY};
            font-weight: 600;
        }}
        
        /* --- DATAFRAME --- */
        [data-testid="stDataFrame"] {{
            border: 1px solid #E0E0E0;
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

local_css()

# ===============================
# 4. MEMUAT DATA
# ===============================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Kmeans_assignment_data.csv")
    except FileNotFoundError:
        st.error("⚠️ Sumber Data Tidak Ditemukan. Pastikan file 'Kmeans_assignment_data.csv' berada di direktori utama.")
        return pd.DataFrame()
    
    # Pembersihan & Rekayasa Fitur
    df.rename(columns={df.columns[0]: 'Universitas'}, inplace=True)
    df['Tingkat Penerimaan'] = (df['Accept'] / df['Apps']) * 100
    df['Total Biaya'] = df['Outstate'] + df['Room.Board'] + df['Books'] + df['Personal']
    return df

df = load_data()

# ===============================
# 5. KONTROL SIDEBAR
# ===============================
st.sidebar.markdown(f"<h2 style='color: white;'>🇺🇸 Depdikbud AS</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='color: #CCCCCC; font-size: 13px; margin-top: -15px;'>Kantor Analitik Pendidikan Tinggi</p>", unsafe_allow_html=True)

# --- NAVIGASI ---
st.sidebar.markdown("### 🧭 Area Fokus Kebijakan")
selected_view = st.sidebar.radio(
    "Navigasi",
    options=[
        "📊 Pembandingan Performa Nasional", 
        "💵 Efisiensi Fiskal & Analisis ROI", 
        "🔓 Aksesibilitas & Ekuitas Jalur",
        "🎓 Kapasitas & Kualitas Pengajaran"
    ],
    label_visibility="collapsed"
)
st.sidebar.divider()

# --- FILTER ---
st.sidebar.markdown("### 🎚️ Segmentasi Kohort")

private_filter = st.sidebar.selectbox(
    "Kontrol Sektor",
    ["Semua Sektor", "Swasta (Nirlaba)", "Negeri (Pemerintah)"]
)

grad_range = st.sidebar.slider(
    "Target Tingkat Kelulusan (%)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

# Logika Filter
df_filtered = df.copy()
if not df_filtered.empty:
    if private_filter == "Swasta (Nirlaba)":
        df_filtered = df_filtered[df_filtered["Private"] == "Yes"]
    elif private_filter == "Negeri (Pemerintah)":
        df_filtered = df_filtered[df_filtered["Private"] == "No"]

    df_filtered = df_filtered[
        (df_filtered["Grad.Rate"] >= grad_range[0]) &
        (df_filtered["Grad.Rate"] <= grad_range[1])
    ]

# ===============================
# 6. KONTEN UTAMA
# ===============================

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data institusi yang cocok dengan kriteria ini. Mohon sesuaikan filter.")
else:
    # --- JUDUL HALAMAN ---
    c_title, c_logo = st.columns([5, 1])
    with c_title:
        st.markdown(f"<h1 style='margin-bottom:0;'>🇺🇸 Matriks Performa Pendidikan Tinggi Nasional</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{SECONDARY}; font-weight:600; font-size: 1.1em;'>Ringkasan Intelijen Strategis untuk Menteri Pendidikan</p>", unsafe_allow_html=True)
        st.markdown("*Laporan rahasia mengenai aksesibilitas institusi, efisiensi fiskal, dan hasil pendidikan.*")

    # --- BAGIAN METRIK (KPI) ---
    st.markdown("### 📊 KPI Nasional (Indikator Performa Utama)")
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Entitas yang Dipantau", f"{len(df_filtered)}")
    with m2:
        st.metric("Tingkat Kelulusan Nasional", f"{df_filtered['Grad.Rate'].mean():.1f}%", 
                  delta=f"{df_filtered['Grad.Rate'].mean() - df['Grad.Rate'].mean():.1f}% vs Baseline Nasional")
    with m3:
        st.metric("Rata-rata Biaya Kuliah", f"${df_filtered['Total Biaya'].mean():,.0f}", 
                  help="Estimasi Beban Tahunan (Uang Kuliah + Asrama + Makan)")
    with m4:
        st.metric("Indeks Kualitas Pengajaran", f"{df_filtered['PhD'].mean():.1f}%",
                  help="% Staf Pengajar bergelar Doktor (PhD)")

    st.markdown("---")

    # ==========================
    # VIEW: BENCHMARKS (Ringkasan)
    # ==========================
    FIG_SIZE = (8, 5)
    
    if selected_view == "📊 Pembandingan Performa Nasional":
        st.subheader("📊 Tolok Ukur Strategis & Peringkat")
        st.markdown("**Ringkasan Eksekutif:** Menganalisis kesenjangan antara biaya pendidikan dan tingkat keberhasilan mahasiswa. Fokus kebijakan adalah mengidentifikasi institusi yang memberikan tingkat kelulusan tinggi tanpa hambatan finansial yang berat.")

        tab1, tab2, tab3 = st.tabs(["🎓 Performa Tinggi (Kelulusan)", "💎 Selektivitas Elit", "📉 Pemimpin Afordabilitas"])
        
        with tab1:
            st.markdown("##### 🏆 10 Institusi Teratas berdasarkan Tingkat Kelulusan")
            top_grad = df_filtered[['Universitas', 'Private', 'Grad.Rate', 'Total Biaya']].sort_values('Grad.Rate', ascending=False).head(10)
            st.dataframe(
                top_grad.style.format({"Grad.Rate": "{:.1f}%", "Total Biaya": "${:,.0f}"})
                .background_gradient(subset=['Grad.Rate'], cmap='Blues'),
                use_container_width=True
            )
            
        with tab2:
            st.markdown("##### 🔒 10 Institusi Paling Selektif")
            top_sel = df_filtered[['Universitas', 'Private', 'Tingkat Penerimaan', 'Top10perc']].sort_values('Tingkat Penerimaan', ascending=True).head(10)
            st.dataframe(
                top_sel.style.format({"Tingkat Penerimaan": "{:.2f}%", "Top10perc": "{:.0f}%"})
                .background_gradient(subset=['Tingkat Penerimaan'], cmap='Reds_r'),
                use_container_width=True
            )
            
        with tab3:
            st.markdown("##### 💰 10 Institusi dengan Biaya Terendah")
            top_cheap = df_filtered[['Universitas', 'Private', 'Total Biaya', 'Grad.Rate']].sort_values('Total Biaya', ascending=True).head(10)
            st.dataframe(
                top_cheap.style.format({"Total Biaya": "${:,.0f}", "Grad.Rate": "{:.1f}%"})
                .background_gradient(subset=['Total Biaya'], cmap='Greens_r'),
                use_container_width=True
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
             st.markdown("#### Analisis Sektor: Tingkat Kelulusan")
             st.caption("Membandingkan variabilitas hasil antara sektor Negeri dan Swasta.")
             fig, ax = plt.subplots(figsize=FIG_SIZE)
             sns.violinplot(x="Private", y="Grad.Rate", data=df_filtered, palette=[SECONDARY, PRIMARY], ax=ax)
             ax.set_ylabel("Tingkat Kelulusan (%)")
             ax.set_xlabel("Sektor (Swasta/Negeri)")
             ax.set_xticklabels(["Swasta", "Negeri"])
             ax.grid(axis='y', alpha=0.3)
             st.pyplot(fig, use_container_width=True)
             
        with col2:
             st.markdown("#### Matriks Biaya-Manfaat")
             st.caption("Korelasi antara beban finansial tahunan dan hasil pendidikan.")
             fig, ax = plt.subplots(figsize=FIG_SIZE)
             sns.scatterplot(x="Total Biaya", y="Grad.Rate", hue="Private", data=df_filtered, palette=[SECONDARY, PRIMARY], alpha=0.7, ax=ax)
             ax.set_xlabel("Total Biaya Tahunan ($)")
             ax.set_ylabel("Tingkat Kelulusan (%)")
             ax.grid(True, alpha=0.3)
             st.pyplot(fig, use_container_width=True)

    # ==========================
    # VIEW: EFFICIENCY (Anggaran)
    # ==========================
    elif selected_view == "💵 Efisiensi Fiskal & Analisis ROI":
        st.subheader("💵 Efisiensi Fiskal & ROI Institusional")
        
        st.info("💡 **Arahan Strategis:** Identifikasi institusi 'High-ROI' yang mencapai hasil mahasiswa unggul (Tingkat Kelulusan) dengan pengeluaran instruksional yang dioptimalkan.")

        fig3, ax3 = plt.subplots(figsize=(10, 6))
        
        # Scatter
        scatter = ax3.scatter(
            df_filtered["Expend"],
            df_filtered["Grad.Rate"],
            c=df_filtered["Kampus"].map({"Swasta": PRIMARY, "Negeri": SECONDARY}),
            s=df_filtered["F.Undergrad"] / 30,
            alpha=0.6,
            edgecolors='white',
            linewidth=0.5
        )
        
        # Garis Kuadran
        avg_exp = df_filtered["Expend"].mean()
        avg_grad = df_filtered["Grad.Rate"].mean()
        
        ax3.axvline(avg_exp, color='gray', linestyle='--', alpha=0.5)
        ax3.axhline(avg_grad, color='gray', linestyle='--', alpha=0.5)
        
        # Anotasi
        ax3.text(df_filtered["Expend"].max()*0.8, 10, "⚠️ Berisiko / Tidak Efisien\n(Biaya Tinggi, Hasil Rendah)", ha='center', color=DANGER, fontweight='bold', fontsize=9)
        ax3.text(df_filtered["Expend"].min()+1000, 95, "✅ Model Performa Tinggi\n(Biaya Rendah, Hasil Tinggi)", ha='left', color=SUCCESS, fontweight='bold', fontsize=9)

        ax3.set_xlabel("Pengeluaran Instruksional per Mahasiswa ($)")
        ax3.set_ylabel("Tingkat Kelulusan (%)")
        ax3.set_title("Matriks ROI Institusional")
        
        # Legenda Manual
        from matplotlib.lines import Line2D
        custom_lines = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor=SECONDARY, markersize=12, label='Negeri (Pemerintah)'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=PRIMARY, markersize=12, label='Swasta (Nirlaba)')
        ]
        ax3.legend(handles=custom_lines, title="Sektor")
        ax3.grid(True, linestyle=':', alpha=0.4)
        
        st.pyplot(fig3, use_container_width=True)

    # ==========================
    # VIEW: ADMISSIONS (Akses)
    # ==========================
    elif selected_view == "🔓 Aksesibilitas & Ekuitas Jalur":
        st.subheader("🔓 Audit Aksesibilitas & Ekuitas Jalur Pendidikan")
        st.markdown("**Tujuan:** Menilai kesenjangan selektivitas antar sektor untuk memastikan akses yang setara ke pendidikan elit bagi siswa berbakat tanpa memandang latar belakang.")
        
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            fig4, ax4 = plt.subplots(figsize=(8, 6))
            
            data_pub = df_filtered[df_filtered["Private"] == "No"]["Tingkat Penerimaan"]
            data_priv = df_filtered[df_filtered["Private"] == "Yes"]["Tingkat Penerimaan"]
            
            bp = ax4.boxplot([data_pub, data_priv], patch_artist=True, labels=["Sektor Negeri", "Sektor Swasta"], widths=0.5)
            
            colors = [SECONDARY, PRIMARY]
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.8)
            
            for median in bp['medians']:
                median.set(color=ACCENT, linewidth=2)
                
            ax4.set_ylabel("Tingkat Penerimaan (%)")
            ax4.set_title("Distribusi Selektivitas berdasarkan Sektor")
            ax4.grid(axis='y', linestyle='--', alpha=0.4)
            
            st.pyplot(fig4, use_container_width=True)
            
        with col_b:
            st.markdown("#### 💡 Statistik Sektor")
            st.write(f"**Median Penerimaan Negeri:** {data_pub.median():.1f}%")
            st.write(f"**Median Penerimaan Swasta:** {data_priv.median():.1f}%")
            
            st.markdown("---")
            st.markdown("#### Jalur Bakat (Lulusan SMA Terbaik)")
            st.progress(int(df_filtered['Top10perc'].mean()))
            st.caption(f"Secara nasional, **{int(df_filtered['Top10perc'].mean())}%** mahasiswa terdaftar berasal dari 10% lulusan terbaik di kelas SMA mereka.")

    # ==========================
    # VIEW: FACULTY (Kualitas)
    # ==========================
    elif selected_view == "🎓 Kapasitas & Kualitas Pengajaran":
        st.subheader("🎓 Kapasitas Pengajaran & Penjaminan Kualitas")
        st.markdown("Menyelidiki korelasi antara kualifikasi staf akademik, ukuran kelas, dan kepuasan jangka panjang pemangku kepentingan.")

        # --- Baris 1: Dampak Fakultas ---
        st.markdown("#### 1. Dampak Kualifikasi Dosen terhadap Keberhasilan Mahasiswa")
        fig5, ax5 = plt.subplots(figsize=(10, 4))
        
        # Plot Regresi
        sns.regplot(x="PhD", y="Grad.Rate", data=df_filtered, 
                    scatter_kws={'alpha':0.3, 'color': PRIMARY}, 
                    line_kws={'color': DANGER}, ax=ax5)
        
        ax5.set_xlabel("% Dosen bergelar PhD")
        ax5.set_ylabel("Tingkat Kelulusan (%)")
        ax5.grid(True, alpha=0.2)
        
        col_res1, col_res2 = st.columns([3, 1])
        with col_res1:
            st.pyplot(fig5, use_container_width=True)
        with col_res2:
            st.markdown("**Wawasan Statistik:**")
            corr = df_filtered['PhD'].corr(df_filtered['Grad.Rate'])
            st.metric("Koefisien Korelasi", f"{corr:.2f}")
            if corr > 0.3:
                st.caption("Korelasi positif menunjukkan bahwa kualifikasi staf yang lebih tinggi adalah pendorong utama hasil mahasiswa.")
            else:
                st.caption("Korelasi lemah menunjukkan variabel lain (misal: pendanaan) mungkin lebih kritis.")

        # --- Baris 2: Sumber Daya & Alumni ---
        st.markdown("---")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### 2. Distribusi Rasio Mahasiswa-Dosen")
            st.caption("Rasio yang lebih rendah menunjukkan perhatian personal dan ketersediaan sumber daya yang lebih baik.")
            
            fig6, ax6 = plt.subplots(figsize=FIG_SIZE)
            sns.histplot(data=df_filtered, x="S.F.Ratio", hue="Private", multiple="stack", palette=[SECONDARY, PRIMARY], ax=ax6, binwidth=2)
            ax6.set_xlabel("Rasio Mahasiswa per Dosen")
            ax6.set_ylabel("Jumlah Institusi")
            st.pyplot(fig6, use_container_width=True)

        with c2:
            st.markdown("#### 3. Keterlibatan Alumni (Donasi)")
            st.caption("Indikator kepuasan lulusan jangka panjang dan kesehatan finansial institusi.")
            
            # Bar chart untuk rata-rata donasi alumni
            avg_alumni = df_filtered.groupby("Private")["perc.alumni"].mean().reset_index()
            
            fig7, ax7 = plt.subplots(figsize=FIG_SIZE)
            bars = ax7.bar(avg_alumni["Private"], avg_alumni["perc.alumni"], color=[SECONDARY, PRIMARY], width=0.5)
            
            ax7.set_ylabel("% Alumni yang Berdonasi")
            ax7.set_ylim(0, 50)
            ax7.set_xticklabels(["Negeri", "Swasta"])
            
            # Label
            for bar in bars:
                height = bar.get_height()
                ax7.text(bar.get_x() + bar.get_width()/2, height + 1, f"{height:.1f}%", 
                         ha='center', fontweight='bold', color=PRIMARY)
            
            st.pyplot(fig7, use_container_width=True)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #888; font-size: 12px;'>
        &copy; 2026 Departemen Pendidikan AS | Kantor Wakil Menteri <br>
        <span style='color:{SECONDARY};'>Sumber Data: IPEDS Integrated Postsecondary Education Data System</span>
    </div>
    """, 
    unsafe_allow_html=True
)
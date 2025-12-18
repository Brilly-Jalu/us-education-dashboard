import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===============================
# 1. PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="National Postsecondary Performance Matrix",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# 2. COLOR PALETTE & STYLE
# ===============================
PRIMARY = "#2D4059"   # Navy Blue (Strategic/Trust)
DANGER = "#EA5455"    # Red (Alert/At-Risk)
SECONDARY = "#F07B3F" # Orange (Highlight)
ACCENT = "#FFD460"    # Yellow (Focus)
BACKGROUND = "#F4F4F4"
SUCCESS = "#28C76F"   # Green (Positive/Compliant)

# Matplotlib settings
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
        /* Import Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {PRIMARY};
        }}

        /* --- SIDEBAR STYLING --- */
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

        /* Styling Radio Button Menu */
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
            color: orange !important; /* Changed to white for better contrast on hover */
        }}

        /* Highlight Selected Item */
        div[role="radiogroup"] > label[data-baseweb="radio"] {{
            background-color: #f8f9fa;
            border-left: 6px solid {SECONDARY};
        }}

        /* --- METRIC CARDS --- */
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
# 4. LOAD DATA
# ===============================
@st.cache_data
def load_data():
    try:
        # Standard relative path
        df = pd.read_csv("Kmeans_assignment_data.csv")
    except FileNotFoundError:
        st.error("⚠️ Data Source Missing. Please ensure 'Kmeans_assignment_data.csv' is in the root directory.")
        return pd.DataFrame()
    
    # Cleaning & Feature Engineering
    df.rename(columns={df.columns[0]: 'University'}, inplace=True)
    df['Acceptance Rate'] = (df['Accept'] / df['Apps']) * 100
    # Note: Using Outstate tuition as a proxy for max cost burden
    df['Total Cost'] = df['Outstate'] + df['Room.Board'] + df['Books'] + df['Personal']
    return df

df = load_data()

# ===============================
# 5. SIDEBAR CONTROLS
# ===============================
st.sidebar.markdown(f"<h2 style='color: white;'>🇺🇸 Dept. of Education</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='color: #CCCCCC; font-size: 13px; margin-top: -15px;'>Office of Postsecondary Analytics</p>", unsafe_allow_html=True)

# --- NAVIGATION ---
st.sidebar.markdown("### 🧭 Policy Focus Areas")
selected_view = st.sidebar.radio(
    "Navigation",
    options=[
        "📊 National Performance Benchmarks", 
        "💵 Fiscal Efficiency & ROI Analysis", 
        "🔓 Accessibility & Pipeline Equity",
        "🎓 Instructional Capacity & Quality"
    ],
    label_visibility="collapsed"
)
st.sidebar.divider()

# --- FILTERS ---
st.sidebar.markdown("### 🎚️ Cohort Segmentation")

private_filter = st.sidebar.selectbox(
    "Sector Control",
    ["All Sectors", "Private (Non-Profit)", "Public (State)"]
)

grad_range = st.sidebar.slider(
    "Completion Rate Target (%)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

# Filter Logic
df_filtered = df.copy()
if not df_filtered.empty:
    if private_filter == "Private (Non-Profit)":
        df_filtered = df_filtered[df_filtered["Private"] == "Yes"]
    elif private_filter == "Public (State)":
        df_filtered = df_filtered[df_filtered["Private"] == "No"]

    df_filtered = df_filtered[
        (df_filtered["Grad.Rate"] >= grad_range[0]) &
        (df_filtered["Grad.Rate"] <= grad_range[1])
    ]

# ===============================
# 6. MAIN CONTENT
# ===============================

if df_filtered.empty:
    st.warning("⚠️ No institutional data found matching these criteria. Please adjust filters.")
else:
    # --- TITLE SECTION ---
    c_title, c_logo = st.columns([5, 1])
    with c_title:
        st.markdown(f"<h1 style='margin-bottom:0;'>🇺🇸 National Postsecondary Performance Matrix</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{SECONDARY}; font-weight:600; font-size: 1.1em;'>Strategic Intelligence Briefing for the Secretary of Education</p>", unsafe_allow_html=True)
        st.markdown("*Confidential briefing regarding institutional accessibility, fiscal efficiency, and educational outcomes.*")

    # --- METRICS SECTION (UPDATED) ---
    st.markdown("### 📊 National KPIs (Key Performance Indicators)")
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Monitored Entities", f"{len(df_filtered)}")
    with m2:
        st.metric("National Completion Rate", f"{df_filtered['Grad.Rate'].mean():.1f}%", 
                  delta=f"{df_filtered['Grad.Rate'].mean() - df['Grad.Rate'].mean():.1f}% vs National Baseline")
    with m3:
        st.metric("Avg. Cost of Attendance", f"${df_filtered['Total Cost'].mean():,.0f}", 
                  help="Estimated Annual Burden (Tuition + Room + Board)")
    with m4:
        st.metric("Instructional Quality Index", f"{df_filtered['PhD'].mean():.1f}%",
                  help="% Faculty holding PhDs")

    st.markdown("---")

    # ==========================
    # VIEW: BENCHMARKS (Overview)
    # ==========================
    FIG_SIZE = (8, 5)
    
    if selected_view == "📊 National Performance Benchmarks":
        st.subheader("📊 Strategic Benchmarks & Rankings")
        st.markdown("**Executive Summary:** Analyzing the disparity between cost of attendance and student success rates. Policy focus is on identifying institutions that deliver high graduation rates without imposing prohibitive financial barriers.")

        tab1, tab2, tab3 = st.tabs(["🎓 High Performance (Completion)", "💎 Elite Selectivity", "📉 Affordability Leaders"])
        
        with tab1:
            st.markdown("##### 🏆 Top 10 Institutions by Completion Rate")
            top_grad = df_filtered[['University', 'Private', 'Grad.Rate', 'Total Cost']].sort_values('Grad.Rate', ascending=False).head(10)
            st.dataframe(
                top_grad.style.format({"Grad.Rate": "{:.1f}%", "Total Cost": "${:,.0f}"})
                .background_gradient(subset=['Grad.Rate'], cmap='Blues'),
                use_container_width=True
            )
            
        with tab2:
            st.markdown("##### 🔒 Top 10 Most Selective Institutions")
            top_sel = df_filtered[['University', 'Private', 'Acceptance Rate', 'Top10perc']].sort_values('Acceptance Rate', ascending=True).head(10)
            st.dataframe(
                top_sel.style.format({"Acceptance Rate": "{:.2f}%", "Top10perc": "{:.0f}%"})
                .background_gradient(subset=['Acceptance Rate'], cmap='Reds_r'),
                use_container_width=True
            )
            
        with tab3:
            st.markdown("##### 💰 Top 10 Lowest Cost of Attendance")
            top_cheap = df_filtered[['University', 'Private', 'Total Cost', 'Grad.Rate']].sort_values('Total Cost', ascending=True).head(10)
            st.dataframe(
                top_cheap.style.format({"Total Cost": "${:,.0f}", "Grad.Rate": "{:.1f}%"})
                .background_gradient(subset=['Total Cost'], cmap='Greens_r'),
                use_container_width=True
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
             st.markdown("#### Sector Analysis: Completion Rates")
             st.caption("Comparing outcome variability between Public and Private sectors.")
             fig, ax = plt.subplots(figsize=FIG_SIZE)
             sns.violinplot(x="Private", y="Grad.Rate", data=df_filtered, palette=[SECONDARY, PRIMARY], ax=ax)
             ax.set_ylabel("Graduation Rate (%)")
             ax.set_xlabel("Sector (Private/Public)")
             ax.grid(axis='y', alpha=0.3)
             st.pyplot(fig, use_container_width=True)
             
        with col2:
             st.markdown("#### Cost-Benefit Matrix")
             st.caption("Correlation between annual financial burden and educational outcomes.")
             fig, ax = plt.subplots(figsize=FIG_SIZE)
             sns.scatterplot(x="Total Cost", y="Grad.Rate", hue="Private", data=df_filtered, palette=[SECONDARY, PRIMARY], alpha=0.7, ax=ax)
             ax.set_xlabel("Total Annual Cost ($)")
             ax.set_ylabel("Graduation Rate (%)")
             ax.grid(True, alpha=0.3)
             st.pyplot(fig, use_container_width=True)

    # ==========================
    # VIEW: EFFICIENCY (Budget)
    # ==========================
    elif selected_view == "💵 Fiscal Efficiency & ROI Analysis":
        st.subheader("💵 Fiscal Efficiency & Institutional ROI")
        
        st.info("💡 **Strategic Directive:** Identify 'High-ROI' institutions that achieve superior student outcomes (Graduation Rate) with optimized instructional expenditure.")

        fig3, ax3 = plt.subplots(figsize=(10, 6))
        
        # Scatter
        scatter = ax3.scatter(
            df_filtered["Expend"],
            df_filtered["Grad.Rate"],
            c=df_filtered["Private"].map({"Yes": PRIMARY, "No": SECONDARY}),
            s=df_filtered["F.Undergrad"] / 30,
            alpha=0.6,
            edgecolors='white',
            linewidth=0.5
        )
        
        # Quadrant Lines
        avg_exp = df_filtered["Expend"].mean()
        avg_grad = df_filtered["Grad.Rate"].mean()
        
        ax3.axvline(avg_exp, color='gray', linestyle='--', alpha=0.5)
        ax3.axhline(avg_grad, color='gray', linestyle='--', alpha=0.5)
        
        # Annotations
        ax3.text(df_filtered["Expend"].max()*0.8, 10, "⚠️ At-Risk / Inefficient\n(High Cost, Low Outcomes)", ha='center', color=DANGER, fontweight='bold', fontsize=9)
        ax3.text(df_filtered["Expend"].min()+1000, 95, "✅ High Performance Model\n(Low Cost, High Outcomes)", ha='left', color=SUCCESS, fontweight='bold', fontsize=9)

        ax3.set_xlabel("Instructional Expenditure per Student ($)")
        ax3.set_ylabel("Graduation Rate (%)")
        ax3.set_title("Institutional ROI Matrix")
        
        # Manual Legend
        from matplotlib.lines import Line2D
        custom_lines = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor=SECONDARY, markersize=12, label='Public (State)'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=PRIMARY, markersize=12, label='Private (Non-Profit)')
        ]
        ax3.legend(handles=custom_lines, title="Sector")
        ax3.grid(True, linestyle=':', alpha=0.4)
        
        st.pyplot(fig3, use_container_width=True)

    # ==========================
    # VIEW: ADMISSIONS (Access)
    # ==========================
    elif selected_view == "🔓 Accessibility & Pipeline Equity":
        st.subheader("🔓 Accessibility & Pipeline Equity Audit")
        st.markdown("**Objective:** Assess the selectivity gap between sectors to ensure equitable access to elite education for talented students regardless of background.")
        
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            fig4, ax4 = plt.subplots(figsize=(8, 6))
            
            data_pub = df_filtered[df_filtered["Private"] == "No"]["Acceptance Rate"]
            data_priv = df_filtered[df_filtered["Private"] == "Yes"]["Acceptance Rate"]
            
            bp = ax4.boxplot([data_pub, data_priv], patch_artist=True, labels=["Public Sector", "Private Sector"], widths=0.5)
            
            colors = [SECONDARY, PRIMARY]
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.8)
            
            for median in bp['medians']:
                median.set(color=ACCENT, linewidth=2)
                
            ax4.set_ylabel("Acceptance Rate (%)")
            ax4.set_title("Selectivity Distribution by Sector")
            ax4.grid(axis='y', linestyle='--', alpha=0.4)
            
            st.pyplot(fig4, use_container_width=True)
            
        with col_b:
            st.markdown("#### 💡 Sector Statistics")
            st.write(f"**Public Median Acceptance:** {data_pub.median():.1f}%")
            st.write(f"**Private Median Acceptance:** {data_priv.median():.1f}%")
            
            st.markdown("---")
            st.markdown("#### Talent Pipeline (Top HS Grads)")
            st.progress(int(df_filtered['Top10perc'].mean()))
            st.caption(f"Nationally, **{int(df_filtered['Top10perc'].mean())}%** of enrolled students come from the Top 10% of their High School Class.")

    # ==========================
    # VIEW: FACULTY (Quality)
    # ==========================
    elif selected_view == "🎓 Instructional Capacity & Quality":
        st.subheader("🎓 Instructional Capacity & Quality Assurance")
        st.markdown("Investigating the correlation between academic staff credentials, class sizes, and long-term stakeholder satisfaction.")

        # --- Row 1: Faculty Impact ---
        st.markdown("#### 1. Impact of Faculty Qualifications on Student Success")
        fig5, ax5 = plt.subplots(figsize=(10, 4))
        
        # Regression plot
        sns.regplot(x="PhD", y="Grad.Rate", data=df_filtered, 
                    scatter_kws={'alpha':0.3, 'color': PRIMARY}, 
                    line_kws={'color': DANGER}, ax=ax5)
        
        ax5.set_xlabel("% Faculty holding PhDs")
        ax5.set_ylabel("Graduation Rate (%)")
        ax5.grid(True, alpha=0.2)
        
        col_res1, col_res2 = st.columns([3, 1])
        with col_res1:
            st.pyplot(fig5, use_container_width=True)
        with col_res2:
            st.markdown("**Statistical Insight:**")
            corr = df_filtered['PhD'].corr(df_filtered['Grad.Rate'])
            st.metric("Correlation Coefficient", f"{corr:.2f}")
            if corr > 0.3:
                st.caption("Positive correlation indicates higher qualified staff is a key driver of student outcomes.")
            else:
                st.caption("Weak correlation suggests other variables (e.g., funding) may be more critical.")

        # --- Row 2: Resources & Alumni ---
        st.markdown("---")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### 2. Student-Faculty Ratio Distribution")
            st.caption("Lower ratio implies better personalized attention and resource availability.")
            
            fig6, ax6 = plt.subplots(figsize=FIG_SIZE)
            sns.histplot(data=df_filtered, x="S.F.Ratio", hue="Private", multiple="stack", palette=[SECONDARY, PRIMARY], ax=ax6, binwidth=2)
            ax6.set_xlabel("Student to Faculty Ratio")
            ax6.set_ylabel("Count of Institutions")
            st.pyplot(fig6, use_container_width=True)

        with c2:
            st.markdown("#### 3. Alumni Engagement (Donations)")
            st.caption("Proxy for long-term graduate satisfaction and institutional financial health.")
            
            # Bar chart for average alumni donation
            avg_alumni = df_filtered.groupby("Private")["perc.alumni"].mean().reset_index()
            
            fig7, ax7 = plt.subplots(figsize=FIG_SIZE)
            bars = ax7.bar(avg_alumni["Private"], avg_alumni["perc.alumni"], color=[SECONDARY, PRIMARY], width=0.5)
            
            ax7.set_ylabel("% Alumni Donating")
            ax7.set_ylim(0, 50)
            ax7.set_xticklabels(["Public", "Private"])
            
            # Labels
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
        &copy; 2024 US Department of Education | Office of the Under Secretary <br>
        <span style='color:{SECONDARY};'>Data Source: IPEDS Integrated Postsecondary Education Data System</span>
    </div>
    """, 
    unsafe_allow_html=True
)
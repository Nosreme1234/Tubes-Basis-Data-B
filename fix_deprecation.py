import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error as MySQLError
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
from sqlalchemy import create_engine
import warnings

warnings.filterwarnings('ignore')

# PAGE CONFIG
st.set_page_config(
    page_title="AkademiQ — Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LIGHT BLUE THEME CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ─── Root & Body ─── */
:root {
    --bg-base:    #f4f8ff;
    --bg-card:    #edf3ff;
    --bg-hover:   #dbe6ff;
    --bg-glass:   rgba(237,243,255,0.88);
    --border:     rgba(37,99,235,0.16);
    --border-hi:  rgba(37,99,235,0.28);
    --accent-1:   #2563eb;   /* blue */
    --accent-2:   #0ea5e9;   /* sky */
    --accent-3:   #93c5fd;   /* soft blue */
    --accent-4:   #1d4ed8;   /* deep blue */
    --accent-5:   #bfdbfe;   /* light blue */
    --text-1:     #0f172a;
    --text-2:     #334e68;
    --text-3:     #4a6d8c;
    --radius:     14px;
    --radius-lg:  20px;
    --shadow:     0 10px 30px rgba(15,23,42,0.08);
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--bg-base) !important;
    color: var(--text-1) !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #f8fbff !important;
    border-right: 1px solid var(--border) !important;
}

/* ─── Hide Streamlit Branding ─── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stHeader"] { 
    background-color: transparent !important;
}

/* ─── Paksa tombol toggle sidebar muncul ─── */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999990 !important;
    background: #2563eb !important;
    border-radius: 8px !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stExpandSidebarButton"] svg,
[data-testid="stSidebarCollapseButton"] svg {
    color: #ffffff !important; fill: #ffffff !important;
}
            
/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--text-3); border-radius: 99px; }

/* ─── Typography ─── */
h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: 0;
    color: var(--text-1) !important;
}
.mono { font-family: 'Space Mono', monospace; }

/* ─── Sidebar ─── */
.sidebar-logo {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 22px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-4), var(--accent-1));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
}
.sidebar-sub {
    font-size: 11px;
    color: var(--text-2);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 24px;
}

[data-testid="stRadio"] label {
    color: #1e3a5f !important;
    font-size: 15px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: color 0.2s;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}
[data-testid="stRadio"] label:hover { 
    color: var(--accent-1) !important; 
}

/* Biar emoji keliatan jelas */
[data-testid="stRadio"] label span {
    font-size: 15px !important;
    filter: none !important;
    opacity: 1 !important;
}

/* ─── Page Header ─── */
.page-header {
    padding: 20px 0 4px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
}
.page-header h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 28px;
    font-weight: 800;
    margin: 0;
    color: #1d4ed8 !important;
    -webkit-text-fill-color: #1d4ed8 !important;
}
.page-header p {
    color: var(--text-2);
    font-size: 13px;
    margin: 4px 0 0;
}

/* ─── KPI Cards ─── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.2s;
    box-shadow: var(--shadow);
}
.kpi-card:hover {
    border-color: var(--accent-1);
    transform: translateY(-2px);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-4), var(--accent-1));
}
.kpi-icon {
    font-size: 20px;
    margin-bottom: 10px;
    display: block;
}
.kpi-label {
    font-size: 11px;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 30px;
    font-weight: 700;
    color: var(--text-1);
    line-height: 1;
}
.kpi-sub {
    font-size: 11px;
    color: var(--text-3);
    margin-top: 6px;
}

/* ─── Section Header ─── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 32px 0 16px;
}
.section-header .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent-1);
    flex-shrink: 0;
}
.section-header h3 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 15px;
    font-weight: 700;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-2) !important;
}

/* ─── Data Table ─── */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-hover) !important;
    color: var(--text-2) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stDataFrame"] td {
    color: var(--text-1) !important;
    font-size: 13px !important;
}

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    border: 1px solid rgba(37,99,235,0.25) !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.05em !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border-color: var(--accent-4) !important;
    box-shadow: 0 0 18px rgba(37,99,235,0.18) !important;
    transform: translateY(-1px) !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    color: #ffffff !important;
    border: 1px solid rgba(14,165,233,0.25) !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: var(--accent-2) !important;
    box-shadow: 0 0 18px rgba(14,165,233,0.2) !important;
}

/* ─── Inputs & Selects ─── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #eef4ff !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-1) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 4px rgba(37,99,235,0.08) !important;
}

/* ─── Radio ─── */
[data-testid="stRadio"] > div { gap: 4px !important; }

/* ─── Selectbox ─── */
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label {
    color: var(--text-2) !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ─── Metric override ─── */
[data-testid="stMetric"] {
    background: #eef4ff;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: var(--text-2) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    color: var(--text-1) !important;
    font-size: 24px !important;
}

/* ─── Alerts ─── */
.stAlert {
    border-radius: var(--radius) !important;
    border-left-width: 3px !important;
    background: var(--bg-card) !important;
}
.stSuccess { border-color: var(--accent-2) !important; }
.stWarning { border-color: var(--accent-3) !important; }
.stError   { border-color: var(--accent-4) !important; }
.stInfo    { border-color: var(--accent-1) !important; }

/* ─── Expander ─── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stExpander"] summary {
    color: var(--text-1) !important;
    font-size: 13px !important;
}

/* ─── Divider ─── */
hr { border-color: var(--border) !important; }

/* ─── Tabs (if used) ─── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
    color: var(--text-2) !important;
    border-radius: 6px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent-1) !important;
    background: rgba(99,179,237,0.08) !important;
}

/* ─── Badge ─── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 10px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.badge-A { background: rgba(104,211,145,0.15); color: #68d391; border: 1px solid rgba(104,211,145,0.3); }
.badge-B { background: rgba(99,179,237,0.15);  color: #63b3ed; border: 1px solid rgba(99,179,237,0.3); }
.badge-C { background: rgba(246,173,85,0.15);  color: #f6ad55; border: 1px solid rgba(246,173,85,0.3); }
.badge-D { background: rgba(252,129,129,0.15); color: #fc8181; border: 1px solid rgba(252,129,129,0.3); }
.badge-E { background: rgba(113,128,150,0.15); color: #718096; border: 1px solid rgba(113,128,150,0.3); }

/* ─── Info Panel ─── */
.info-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin: 8px 0;
}

/* ─── Danger zone ─── */
.danger-zone {
    border: 1px solid rgba(37,99,235,0.2);
    background: rgba(37,99,235,0.08);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin-bottom: 16px;
}
.danger-zone p { color: var(--accent-4); font-size: 13px; margin: 0; }

/* ─── Sidebar Status ─── */
.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent-2);
    box-shadow: 0 0 6px var(--accent-2);
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* override: tombol buka-tutup sidebar + header tidak menutup kontrol */
[data-testid="stHeader"] { height: auto !important; }
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebarButton"] {
    display: flex !important; visibility: visible !important; opacity: 1 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label,
[data-testid="stSidebar"] [data-testid="stRadio"] label * {
    color: #1e3a5f !important;
    -webkit-text-fill-color: #1e3a5f !important;
    opacity: 1 !important;
}

/* Navigasi sidebar tampil sebagai tombol timbul (seperti Export CSV) */
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label {
    background: #ffffff !important;
    border: 1px solid #dbe6f7 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px rgba(37,99,235,0.10) !important;
    transition: transform 0.12s, box-shadow 0.12s, background 0.12s !important;
    cursor: pointer !important;
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:hover {
    background: #f0f6ff !important;
    box-shadow: 0 4px 10px rgba(37,99,235,0.18) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
    background: #2563eb !important;
    border-color: #2563eb !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.35) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked),
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stWidgetLabel"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# PLOTLY LIGHT THEME
PLOTLY_LAYOUT = dict(
    paper_bgcolor='#f7fbff',
    plot_bgcolor='#ffffff',
    font=dict(family='Inter, sans-serif', color='#0f172a', size=12),
    title_font=dict(family='Plus Jakarta Sans, sans-serif', color='#1d4ed8', size=15),
    legend=dict(
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='rgba(15,23,42,0.08)',
        borderwidth=1,
        font=dict(color='#475569', size=11)
    ),
    xaxis=dict(
        gridcolor='rgba(15,23,42,0.08)',
        linecolor='rgba(15,23,42,0.15)',
        tickfont=dict(color='#475569', size=11),
        zerolinecolor='rgba(15,23,42,0.08)'
    ),
    yaxis=dict(
        gridcolor='rgba(15,23,42,0.08)',
        linecolor='rgba(15,23,42,0.15)',
        tickfont=dict(color='#475569', size=11),
        zerolinecolor='rgba(15,23,42,0.08)'
    ),
    coloraxis_colorbar=dict(tickfont=dict(color='#475569')),
    margin=dict(l=20, r=20, t=50, b=20)
)

COLOR_SEQ = ['#1d4ed8', '#2563eb', '#3b82f6', '#60a5fa', '#38bdf8', '#7dd3fc', '#93c5fd']
GRADE_COLORS = {
    'A': '#0ea5e9', 'B': '#2563eb', 'C': '#38bdf8', 'D': '#7dd3fc', 'E': '#94a3b8'
}

def apply_dark_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# DATABASE
@st.cache_resource
def get_sqlalchemy_engine():
    try:
        engine = create_engine('mysql+pymysql://root:@localhost/db_akademik')
        return engine
    except Exception:
        return None

@st.cache_resource
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost', user='root', password='',
            database='db_akademik', autocommit=True
        )
        return conn
    except MySQLError as err:
        st.error(f"Koneksi database gagal: {err}")
        return None

def execute_query(query, params=None):
    try:
        engine = get_sqlalchemy_engine()
        if engine:
            return pd.read_sql(query, engine)
        conn = get_db_connection()
        if conn is None:
            return None
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return None

def execute_write(query, params=None):
    try:
        conn = get_db_connection()
        if conn is None:
            return False, "Tidak dapat terhubung ke database"
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        cursor.close()
        return True, "Sukses"
    except MySQLError as e:
        return False, str(e)

def get_letter_grade(score):
    if score >= 80: return 'A'
    elif score >= 70: return 'B'
    elif score >= 60: return 'C'
    elif score >= 50: return 'D'
    else: return 'E'


def hex_to_rgba(hex_color, alpha=0.12):
    hex_color = str(hex_color).lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r},{g},{b},{alpha})'
    return hex_color

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">AkademiQ</div>
    <div class="sidebar-sub">Dashboard Sistem Nilai</div>
    """, unsafe_allow_html=True)

    menu_option = st.radio(
        "Navigasi",
        [
            "Overview",
            "Mahasiswa",
            "Mata Kuliah",
            "Analisis Nilai",
            "Pencarian",
            "Laporan",
            "CRUD"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px; color:#4a5568; line-height:1.8;">
    <span class="status-dot"></span><span style="color:#68d391">Connected</span><br>
    <span style="color:#4a5568;">DB ·</span> db_akademik<br>
    <span style="color:#4a5568;">Engine ·</span> MySQL / MariaDB<br>
    <span style="color:#4a5568;">Schema ·</span> Opsi B<br>
    <span style="color:#4a5568;">Build ·</span> 2026.1
    </div>
    """, unsafe_allow_html=True)

# HELPERS
def kpi_card(icon, label, value, sub="", color_a="#63b3ed", color_b="#b794f4"):
    st.markdown(f"""
    <div class="kpi-card" style="--color-a:{color_a};--color-b:{color_b};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def section_header(title):
    st.markdown(f"""
    <div class="section-header">
        <div class="dot"></div>
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)

# PAGE: OVERVIEW
if menu_option == "Overview":
    st.markdown('<div class="page-header"><h1>📊 Overview Dashboard</h1><p>Ringkasan performa akademik keseluruhan</p></div>', unsafe_allow_html=True)

    # ── KPIs ──
    df_mhs  = execute_query("SELECT COUNT(*) as total FROM mahasiswa")
    df_mk   = execute_query("SELECT COUNT(*) as total FROM mata_kuliah")
    df_nval = execute_query("SELECT COUNT(*) as total FROM nilai")
    df_avg  = execute_query("SELECT ROUND(AVG(0.3*COALESCE(nilai_uts,0)+0.4*COALESCE(nilai_uas,0)+0.3*COALESCE(nilai_tugas,0)),2) as v FROM nilai")
    df_lulus = execute_query("SELECT COUNT(*) as total FROM nilai WHERE (0.3*COALESCE(nilai_uts,0)+0.4*COALESCE(nilai_uas,0)+0.3*COALESCE(nilai_tugas,0)) >= 60")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        total_mhs = int(df_mhs['total'].values[0]) if df_mhs is not None else 0
        kpi_card("", "Total Mahasiswa", f"{total_mhs:,}", "Terdaftar", "#63b3ed", "#b794f4")
    with c2:
        total_mk = int(df_mk['total'].values[0]) if df_mk is not None else 0
        kpi_card("", "Mata Kuliah", f"{total_mk:,}", "Aktif", "#68d391", "#63b3ed")
    with c3:
        total_nilai = int(df_nval['total'].values[0]) if df_nval is not None else 0
        kpi_card("", "Total Nilai", f"{total_nilai:,}", "Record", "#f6ad55", "#fc8181")
    with c4:
        avg_val = float(df_avg['v'].values[0]) if df_avg is not None and df_avg['v'].values[0] is not None else 0
        kpi_card("", "Rata-rata Nilai", f"{avg_val:.1f}", "Keseluruhan", "#b794f4", "#fc8181")
    with c5:
        total_lulus = int(df_lulus['total'].values[0]) if df_lulus is not None else 0
        pct = round(total_lulus / total_nilai * 100, 1) if total_nilai > 0 else 0
        kpi_card("", "Tingkat Lulus", f"{pct}%", f"{total_lulus} dari {total_nilai}", "#68d391", "#f6ad55")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Distribusi Huruf Mutu ──
    section_header("Distribusi Huruf Mutu")

    df_huruf = execute_query("""
        SELECT CASE WHEN na>=80 THEN 'A' WHEN na>=70 THEN 'B'
                    WHEN na>=60 THEN 'C' WHEN na>=50 THEN 'D' ELSE 'E' END AS huruf,
               COUNT(*) AS jumlah
        FROM (SELECT 0.3*COALESCE(nilai_uts,0)+0.4*COALESCE(nilai_uas,0)+0.3*COALESCE(nilai_tugas,0) AS na FROM nilai) t
        GROUP BY huruf ORDER BY huruf
    """)

    if df_huruf is not None:
        c1, c2 = st.columns([1, 1])

        with c1:
            colors = [GRADE_COLORS.get(h, '#718096') for h in df_huruf['huruf']]
            fig = go.Figure(go.Pie(
                labels=df_huruf['huruf'], values=df_huruf['jumlah'],
                hole=0.58,
                marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
                textfont=dict(family='Space Mono', size=13, color='white'),
                hovertemplate='<b>Nilai %{label}</b><br>%{value} mahasiswa<br>%{percent}<extra></extra>'
            ))
            fig.add_annotation(text=f"<b>{total_nilai}</b><br><span style='font-size:11px'>Total</span>",
                               x=0.5, y=0.5, showarrow=False,
                               font=dict(size=18, color='#f0f4f8', family='Plus Jakarta Sans'))
            fig.update_layout(title="Proporsi Huruf Mutu", **PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = go.Figure(go.Bar(
                x=df_huruf['huruf'], y=df_huruf['jumlah'],
                marker=dict(
                    color=colors,
                    line=dict(color='rgba(0,0,0,0)', width=0)
                ),
                text=df_huruf['jumlah'],
                textposition='outside',
                textfont=dict(family='Space Mono', size=12, color='#f0f4f8'),
                hovertemplate='<b>Nilai %{x}</b><br>%{y} mahasiswa<extra></extra>'
            ))
            fig2.update_layout(title="Jumlah per Huruf Mutu",
                               bargap=0.35, **PLOTLY_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)

    # ── Performa per Prodi ──
    section_header("Performa per Program Studi")

    df_prodi = execute_query("""
        SELECT m.prodi,
               COUNT(DISTINCT m.nim) AS jml_mhs,
               COUNT(n.id_nilai) AS jml_nilai,
               ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir,
               ROUND(AVG(n.nilai_uts),2) AS rata_uts,
               ROUND(AVG(n.nilai_uas),2) AS rata_uas,
               ROUND(AVG(n.nilai_tugas),2) AS rata_tugas
        FROM nilai n JOIN mahasiswa m ON n.nim=m.nim
        GROUP BY m.prodi ORDER BY rata_akhir DESC
    """)

    if df_prodi is not None:
        c1, c2 = st.columns([3, 2])

        with c1:
            # Grouped bar
            fig3 = go.Figure()
            labels = ['UTS', 'UAS', 'Tugas', 'Final']
            cols_map = {'UTS': 'rata_uts', 'UAS': 'rata_uas', 'Tugas': 'rata_tugas', 'Final': 'rata_akhir'}
            bar_colors = ['#63b3ed', '#b794f4', '#f6ad55', '#68d391']
            for lbl, col, bc in zip(labels, cols_map.values(), bar_colors):
                fig3.add_trace(go.Bar(
                    name=lbl, x=df_prodi['prodi'], y=df_prodi[col],
                    marker_color=bc,
                    hovertemplate=f'<b>%{{x}}</b><br>{lbl}: %{{y}}<extra></extra>'
                ))
            fig3.update_layout(title="Komponen Nilai per Prodi", barmode='group',
                               bargap=0.2, bargroupgap=0.06, **PLOTLY_LAYOUT)
            st.plotly_chart(fig3, use_container_width=True)

        with c2:
            # Radar chart
            categories = ['Rata UTS', 'Rata UAS', 'Rata Tugas', 'Nilai Akhir']
            fig4 = go.Figure()
            for i, row in df_prodi.iterrows():
                vals = [row['rata_uts'], row['rata_uas'], row['rata_tugas'], row['rata_akhir']]
                vals += [vals[0]]
                cats = categories + [categories[0]]
                fig4.add_trace(go.Scatterpolar(
                    r=vals, theta=cats, fill='toself',
                    name=row['prodi'],
                    line=dict(color=COLOR_SEQ[i % len(COLOR_SEQ)], width=2),
                    fillcolor=hex_to_rgba(COLOR_SEQ[i % len(COLOR_SEQ)], 0.12)
                ))
            fig4.update_layout(
                title="Radar Komponen Nilai",
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0,100], gridcolor='rgba(255,255,255,0.07)',
                                   tickfont=dict(color='#4a5568', size=9)),
                    angularaxis=dict(tickfont=dict(color='#8a9ab5', size=11),
                                    gridcolor='rgba(255,255,255,0.07)')
                ),
                **PLOTLY_LAYOUT
            )
            st.plotly_chart(fig4, use_container_width=True)

    # ── Tren Nilai per Semester ──
    section_header("Tren Nilai per Semester")

    df_sem = execute_query("""
        SELECT n.semester_ambil,
               COUNT(*) AS jml,
               ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata,
               ROUND(AVG(n.nilai_uts),2) AS rata_uts,
               ROUND(AVG(n.nilai_uas),2) AS rata_uas,
               ROUND(AVG(n.nilai_tugas),2) AS rata_tugas
        FROM nilai n GROUP BY n.semester_ambil ORDER BY n.semester_ambil
    """)

    if df_sem is not None:
        fig5 = go.Figure()
        traces = [
            ('Nilai Akhir', 'rata', '#63b3ed', True),
            ('UTS', 'rata_uts', '#b794f4', False),
            ('UAS', 'rata_uas', '#f6ad55', False),
            ('Tugas', 'rata_tugas', '#68d391', False)
        ]
        for name, col, color, visible in traces:
            fig5.add_trace(go.Scatter(
                x=df_sem['semester_ambil'], y=df_sem[col],
                name=name, mode='lines+markers',
                line=dict(color=color, width=2.5),
                marker=dict(size=7, color=color, line=dict(color='#ffffff', width=2)),
                visible=True if visible else 'legendonly',
                hovertemplate=f'Semester %{{x}}<br>{name}: %{{y:.1f}}<extra></extra>'
            ))
        fig5.update_layout(title="Tren Nilai per Semester Pengambilan",
                           xaxis_title="Semester", yaxis_title="Rata-rata Nilai",
                           yaxis_range=[0, 105], **PLOTLY_LAYOUT)
        st.plotly_chart(fig5, use_container_width=True)

    # ── Top 5 & Bottom 5 MK ──
    section_header("Perbandingan Mata Kuliah")

    df_mk_perf = execute_query("""
        SELECT mk.nama_mk,
               ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata,
               COUNT(DISTINCT n.nim) AS jml_mhs
        FROM mata_kuliah mk LEFT JOIN nilai n ON mk.kode_mk=n.kode_mk
        GROUP BY mk.nama_mk ORDER BY rata DESC
    """)

    if df_mk_perf is not None:
        c1, c2 = st.columns(2)
        with c1:
            top5 = df_mk_perf.head(5)
            fig6 = go.Figure(go.Bar(
                x=top5['rata'], y=top5['nama_mk'], orientation='h',
                marker=dict(color='#68d391', opacity=0.85,
                            line=dict(color='rgba(0,0,0,0)', width=0)),
                text=[f"{v:.1f}" for v in top5['rata']],
                textposition='inside', textfont=dict(color='white', family='Space Mono', size=11),
                hovertemplate='<b>%{y}</b><br>Rata-rata: %{x:.1f}<extra></extra>'
            ))
            fig6.update_layout(title="5 MK Nilai Tertinggi",
                               xaxis_range=[0, 105], **PLOTLY_LAYOUT)
            st.plotly_chart(fig6, use_container_width=True)

        with c2:
            bot5 = df_mk_perf.tail(5)
            fig7 = go.Figure(go.Bar(
                x=bot5['rata'], y=bot5['nama_mk'], orientation='h',
                marker=dict(color='#fc8181', opacity=0.85,
                            line=dict(color='rgba(0,0,0,0)', width=0)),
                text=[f"{v:.1f}" for v in bot5['rata']],
                textposition='inside', textfont=dict(color='white', family='Space Mono', size=11),
                hovertemplate='<b>%{y}</b><br>Rata-rata: %{x:.1f}<extra></extra>'
            ))
            fig7.update_layout(title="5 MK Nilai Terendah",
                               xaxis_range=[0, 105], **PLOTLY_LAYOUT)
            st.plotly_chart(fig7, use_container_width=True)

        # ── Rata-rata nilai per MK (matkul bisa dipilih) ──
        section_header("Rata-rata Nilai per Mata Kuliah")

        semua_mk = df_mk_perf['nama_mk'].tolist()
        pilihan_mk = st.multiselect(
            "Pilih mata kuliah (kosongkan untuk menampilkan semua)",
            options=semua_mk,
            default=[],
            key="mk_chart_filter",
            placeholder="Ketik atau pilih mata kuliah..."
        )

        if pilihan_mk:
            df_pilih = df_mk_perf[df_mk_perf['nama_mk'].isin(pilihan_mk)].sort_values('rata', ascending=False)
        else:
            df_pilih = df_mk_perf.sort_values('rata', ascending=False)

        if len(df_pilih) > 0:
            show_text = len(df_pilih) <= 15
            fig8 = go.Figure(go.Bar(
                x=df_pilih['nama_mk'], y=df_pilih['rata'],
                marker=dict(color=df_pilih['rata'], colorscale='Blues', opacity=0.9, showscale=False),
                text=[f"{v:.1f}" for v in df_pilih['rata']] if show_text else None,
                textposition='outside', textfont=dict(color='#1d4ed8', family='Space Mono', size=10),
                hovertemplate='<b>%{x}</b><br>Rata-rata: %{y:.1f}<extra></extra>'
            ))
            fig8.update_layout(
                title=f"Rata-rata Nilai Akhir ({len(df_pilih)} mata kuliah)",
                yaxis_range=[0, 105], **PLOTLY_LAYOUT
            )
            fig8.update_xaxes(tickangle=-40)
            st.plotly_chart(fig8, use_container_width=True)
        else:
            st.info("Pilih minimal satu mata kuliah untuk menampilkan grafik.")

# PAGE: MAHASISWA
elif menu_option == "Mahasiswa":
    st.markdown('<div class="page-header"><h1>👥 Data Mahasiswa</h1><p>Direktori mahasiswa terdaftar</p></div>', unsafe_allow_html=True)

    # Filters
    c1, c2, c3 = st.columns(3)
    with c1:
        df_prodi_opt = execute_query("SELECT DISTINCT prodi FROM mahasiswa ORDER BY prodi")
        prodi_filter = st.multiselect("Program Studi",
            df_prodi_opt['prodi'].tolist() if df_prodi_opt is not None else [])
    with c2:
        df_ang_opt = execute_query("SELECT DISTINCT angkatan FROM mahasiswa ORDER BY angkatan DESC")
        angkatan_filter = st.multiselect("Angkatan",
            df_ang_opt['angkatan'].tolist() if df_ang_opt is not None else [])
    with c3:
        gender_filter = st.multiselect("Jenis Kelamin",
            ['L – Laki-laki', 'P – Perempuan'])

    query = "SELECT nim, nama, angkatan, jenis_kelamin, prodi FROM mahasiswa WHERE 1=1"
    if prodi_filter:
        query += f" AND prodi IN ({','.join([repr(p) for p in prodi_filter])})"
    if angkatan_filter:
        query += f" AND angkatan IN ({','.join(map(str, angkatan_filter))})"
    if gender_filter:
        genders = [g[0] for g in gender_filter]
        query += f" AND jenis_kelamin IN ({','.join([repr(g) for g in genders])})"
    query += " ORDER BY prodi, angkatan DESC, nama"

    df_mhs = execute_query(query)

    if df_mhs is not None:
        c1, c2, c3 = st.columns(3)
        with c1: kpi_card("", "Mahasiswa Ditemukan", f"{len(df_mhs):,}", "", "#63b3ed", "#b794f4")
        with c2:
            l_count = len(df_mhs[df_mhs['jenis_kelamin'] == 'L'])
            kpi_card("", "Laki-laki", f"{l_count:,}", f"{round(l_count/len(df_mhs)*100,1) if len(df_mhs)>0 else 0}%", "#63b3ed", "#b794f4")
        with c3:
            p_count = len(df_mhs[df_mhs['jenis_kelamin'] == 'P'])
            kpi_card("", "Perempuan", f"{p_count:,}", f"{round(p_count/len(df_mhs)*100,1) if len(df_mhs)>0 else 0}%", "#fc8181", "#f6ad55")

        st.markdown("<br>", unsafe_allow_html=True)

        section_header("Daftar Mahasiswa")
        st.dataframe(df_mhs, use_container_width=True, hide_index=True)

        csv = df_mhs.to_csv(index=False)
        st.download_button("Export CSV", csv,
            f"mahasiswa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")

    # Visualisasi
    section_header("Statistik Demografik")

    df_all_mhs = execute_query("""
        SELECT prodi, jenis_kelamin, angkatan, COUNT(*) AS jml
        FROM mahasiswa GROUP BY prodi, jenis_kelamin, angkatan
    """)

    if df_all_mhs is not None:
        c1, c2 = st.columns(2)

        with c1:
            df_prodi_gender = df_all_mhs.groupby(['prodi', 'jenis_kelamin'])['jml'].sum().reset_index()
            df_prodi_gender['gender_label'] = df_prodi_gender['jenis_kelamin'].map({'L': 'Laki-laki', 'P': 'Perempuan'})
            fig = px.bar(df_prodi_gender, x='prodi', y='jml', color='gender_label',
                         barmode='group', title="Distribusi Gender per Prodi",
                         labels={'prodi': 'Prodi', 'jml': 'Jumlah', 'gender_label': 'Gender'},
                         color_discrete_map={'Laki-laki': '#63b3ed', 'Perempuan': '#fc8181'})
            fig.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df_angkatan = df_all_mhs.groupby('angkatan')['jml'].sum().reset_index()
            fig2 = go.Figure(go.Bar(
                x=df_angkatan['angkatan'].astype(str), y=df_angkatan['jml'],
                marker=dict(color='#b794f4', opacity=0.85),
                text=df_angkatan['jml'], textposition='outside',
                textfont=dict(color='#f0f4f8', family='Space Mono', size=11)
            ))
            fig2.update_layout(title="Jumlah Mahasiswa per Angkatan",
                               xaxis_title="Angkatan", yaxis_title="Jumlah", **PLOTLY_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)

# PAGE: MATA KULIAH
elif menu_option == "Mata Kuliah":
    st.markdown('<div class="page-header"><h1>📚 Mata Kuliah</h1><p>Katalog dan performa setiap mata kuliah</p></div>', unsafe_allow_html=True)

    df_mk = execute_query("SELECT kode_mk, nama_mk, sks FROM mata_kuliah ORDER BY kode_mk")

    if df_mk is not None:
        c1, c2, c3 = st.columns(3)
        with c1: kpi_card("", "Total MK", f"{len(df_mk):,}", "Terdaftar", "#63b3ed", "#68d391")
        with c2: kpi_card("", "Total SKS", f"{int(df_mk['sks'].sum()):,}", "Semua MK", "#f6ad55", "#fc8181")
        with c3: kpi_card("", "Rata SKS", f"{df_mk['sks'].mean():.1f}", "Per MK", "#b794f4", "#63b3ed")

        st.markdown("<br>", unsafe_allow_html=True)

        section_header("Daftar Mata Kuliah")
        st.dataframe(df_mk, use_container_width=True, hide_index=True)

    section_header("Statistik Nilai per Mata Kuliah")

    df_mk_stats = execute_query("""
        SELECT mk.kode_mk, mk.nama_mk, mk.sks,
               COUNT(DISTINCT n.nim) AS jml_mhs,
               ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir,
               ROUND(AVG(n.nilai_uts),2) AS rata_uts,
               ROUND(AVG(n.nilai_uas),2) AS rata_uas,
               ROUND(AVG(n.nilai_tugas),2) AS rata_tugas,
               ROUND(STDDEV(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS std_dev,
               ROUND(MIN(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS min_nilai,
               ROUND(MAX(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS max_nilai
        FROM mata_kuliah mk LEFT JOIN nilai n ON mk.kode_mk=n.kode_mk
        GROUP BY mk.kode_mk, mk.nama_mk, mk.sks ORDER BY rata_akhir DESC
    """)

    if df_mk_stats is not None:
        st.dataframe(df_mk_stats, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)

        with c1:
            fig = go.Figure()
            for col, color, name in [
                ('rata_uts','#63b3ed','UTS'),
                ('rata_uas','#b794f4','UAS'),
                ('rata_tugas','#f6ad55','Tugas'),
                ('rata_akhir','#68d391','Final')
            ]:
                fig.add_trace(go.Bar(
                    name=name, x=df_mk_stats['nama_mk'], y=df_mk_stats[col],
                    marker_color=color, opacity=0.85
                ))
            fig.update_layout(title="Komponen Nilai per Mata Kuliah",
                              barmode='group', xaxis_tickangle=-35, **PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            opsi_mk_dist = df_mk_stats['nama_mk'].tolist()
            pilih_mk_dist = st.multiselect(
                "Pilih mata kuliah (kosongkan untuk menampilkan semua)",
                options=opsi_mk_dist, default=[], key="dist_mk_filter",
                placeholder="Ketik atau pilih mata kuliah..."
            )
            df_dist = df_mk_stats[df_mk_stats['nama_mk'].isin(pilih_mk_dist)] if pilih_mk_dist else df_mk_stats

            jm = df_dist['jml_mhs']
            if len(jm) > 0 and jm.max() > jm.min():
                size_norm = 10 + (jm - jm.min()) / (jm.max() - jm.min()) * 35
            else:
                size_norm = pd.Series([22] * len(jm), index=jm.index)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_dist['nama_mk'],
                y=df_dist['rata_akhir'],
                mode='markers',
                marker=dict(
                    size=size_norm,
                    color=df_dist['rata_akhir'],
                    colorscale=[[0,'#fc8181'],[0.5,'#f6ad55'],[1,'#68d391']],
                    showscale=True,
                    colorbar=dict(title='Nilai', tickfont=dict(color='#8a9ab5'))
                ),
                error_y=dict(
                    type='data', array=df_dist['std_dev'],
                    color='rgba(100,116,139,0.45)', thickness=2, width=6
                ),
                text=df_dist['nama_mk'],
                hovertemplate='<b>%{text}</b><br>Rata-rata: %{y:.1f}<br>Std Dev: ±%{error_y.array:.1f}<extra></extra>'
            ))
            fig2.update_layout(title="Distribusi Nilai (ukuran = jml mahasiswa)",
                               xaxis_showticklabels=False, yaxis_range=[0,105], **PLOTLY_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)

# PAGE: ANALISIS NILAI
elif menu_option == "Analisis Nilai":
    st.markdown('<div class="page-header"><h1>📈 Analisis Nilai</h1><p>Wawasan mendalam performa akademik</p></div>', unsafe_allow_html=True)

    tabs = st.tabs(["Top & Bottom", "Gender", "Retake", "Terbaik per Prodi", "Distribusi"])

    # ── Tab 1: Top & Bottom ──
    with tabs[0]:
        c1, c2 = st.columns(2)

        df_top = execute_query("""
            SELECT m.nama, m.nim, m.prodi, mk.nama_mk,
                   n.nilai_uts, n.nilai_uas, n.nilai_tugas,
                   ROUND(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0),2) AS nilai_akhir
            FROM nilai n JOIN mahasiswa m ON n.nim=m.nim JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk
            ORDER BY nilai_akhir DESC LIMIT 10
        """)
        df_bot = execute_query("""
            SELECT m.nama, m.nim, m.prodi, mk.nama_mk,
                   n.nilai_uts, n.nilai_uas, n.nilai_tugas,
                   ROUND(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0),2) AS nilai_akhir
            FROM nilai n JOIN mahasiswa m ON n.nim=m.nim JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk
            ORDER BY nilai_akhir ASC LIMIT 10
        """)

        with c1:
            section_header("10 Nilai Tertinggi")
            if df_top is not None:
                st.dataframe(df_top, use_container_width=True, hide_index=True)
                fig = go.Figure(go.Bar(
                    y=df_top['nama'][::-1], x=df_top['nilai_akhir'][::-1], orientation='h',
                    marker=dict(color='#68d391', opacity=0.85),
                    text=[f"{v:.1f}" for v in df_top['nilai_akhir'][::-1]],
                    textposition='inside', textfont=dict(color='white', family='Space Mono')
                ))
                fig.update_layout(title="Top 10 Nilai Tertinggi", xaxis_range=[0,105], **PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            section_header("10 Nilai Terendah")
            if df_bot is not None:
                st.dataframe(df_bot, use_container_width=True, hide_index=True)
                fig2 = go.Figure(go.Bar(
                    y=df_bot['nama'][::-1], x=df_bot['nilai_akhir'][::-1], orientation='h',
                    marker=dict(color='#fc8181', opacity=0.85),
                    text=[f"{v:.1f}" for v in df_bot['nilai_akhir'][::-1]],
                    textposition='inside', textfont=dict(color='white', family='Space Mono')
                ))
                fig2.update_layout(title="10 Nilai Terendah", xaxis_range=[0,105], **PLOTLY_LAYOUT)
                st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 2: Gender ──
    with tabs[1]:
        df_gender = execute_query("""
            SELECT m.jenis_kelamin,
                   CASE WHEN m.jenis_kelamin='L' THEN 'Laki-laki' ELSE 'Perempuan' END AS gender,
                   COUNT(DISTINCT m.nim) AS jml_mhs,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir,
                   ROUND(AVG(n.nilai_uts),2) AS rata_uts,
                   ROUND(AVG(n.nilai_uas),2) AS rata_uas,
                   ROUND(AVG(n.nilai_tugas),2) AS rata_tugas
            FROM mahasiswa m LEFT JOIN nilai n ON m.nim=n.nim GROUP BY m.jenis_kelamin
        """)

        if df_gender is not None:
            c1, c2 = st.columns(2)

            with c1:
                fig = go.Figure()
                cats = ['rata_uts', 'rata_uas', 'rata_tugas', 'rata_akhir']
                labels = ['UTS', 'UAS', 'Tugas', 'Final']
                colors = ['#63b3ed', '#fc8181']
                for i, row in df_gender.iterrows():
                    fig.add_trace(go.Bar(
                        name=row['gender'], x=labels,
                        y=[row[c] for c in cats],
                        marker_color=colors[i % len(colors)],
                        text=[f"{row[c]:.1f}" for c in cats],
                        textposition='outside',
                        textfont=dict(color='#f0f4f8', family='Space Mono', size=11)
                    ))
                fig.update_layout(title="Perbandingan Nilai per Gender",
                                  barmode='group', **PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.dataframe(df_gender, use_container_width=True, hide_index=True)

                # Donut gender count
                fig2 = go.Figure(go.Pie(
                    labels=df_gender['gender'], values=df_gender['jml_mhs'],
                    hole=0.55, marker=dict(colors=['#63b3ed', '#fc8181'],
                                          line=dict(color='#ffffff', width=2))
                ))
                fig2.update_layout(title="Proporsi Gender", **PLOTLY_LAYOUT)
                st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 3: Retake ──
    with tabs[2]:
        section_header("Analisis Retake (Pengulangan Mata Kuliah)")

        df_retake = execute_query("""
            SELECT m.nim, m.nama, m.prodi, mk.nama_mk,
                   COUNT(*) AS jumlah_retake,
                   ROUND(MIN(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS nilai_min,
                   ROUND(MAX(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS nilai_max
            FROM nilai n JOIN mahasiswa m ON n.nim=m.nim JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk
            GROUP BY n.nim, n.kode_mk, m.nama, m.prodi, mk.nama_mk
            HAVING COUNT(*) > 1 ORDER BY jumlah_retake DESC, m.nama
        """)

        if df_retake is not None and len(df_retake) > 0:
            kpi_card("", "Total Retake", f"{len(df_retake):,}", "Pengambilan Ulang", "#f6ad55", "#fc8181")
            st.markdown("<br>", unsafe_allow_html=True)
            df_retake['peningkatan'] = df_retake['nilai_max'] - df_retake['nilai_min']
            st.dataframe(df_retake, use_container_width=True, hide_index=True)

            fig = px.scatter(df_retake, x='nilai_min', y='nilai_max',
                             color='prodi', size='jumlah_retake',
                             hover_data=['nama', 'nama_mk'],
                             title="Nilai Awal vs Nilai Akhir Setelah Retake",
                             labels={'nilai_min': 'Nilai Pertama', 'nilai_max': 'Nilai Terakhir'},
                             color_discrete_sequence=COLOR_SEQ)
            # Reference line y=x
            fig.add_shape(type='line', x0=0, y0=0, x1=100, y1=100,
                          line=dict(color='rgba(255,255,255,0.15)', dash='dash', width=1))
            fig.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹTidak ditemukan data retake")

    # ── Tab 4: Terbaik per Prodi ──
    with tabs[3]:
        section_header("Mahasiswa Terbaik per Program Studi")

        df_terbaik = execute_query("""
            SELECT m.prodi, m.nim, m.nama,
                   COUNT(n.id_nilai) AS jml_mk,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir
            FROM nilai n JOIN mahasiswa m ON n.nim=m.nim
            GROUP BY m.prodi, m.nim, m.nama ORDER BY m.prodi, rata_akhir DESC
        """)

        if df_terbaik is not None:
            # Get #1 per prodi
            top_per_prodi = df_terbaik.groupby('prodi').first().reset_index()

            cols = st.columns(len(top_per_prodi))
            for i, (col, row) in enumerate(zip(cols, top_per_prodi.itertuples())):
                with col:
                    grade = get_letter_grade(row.rata_akhir)
                    color = GRADE_COLORS.get(grade, '#718096')
                    st.markdown(f"""
                    <div class="kpi-card" style="--color-a:{color};--color-b:{color}; text-align:center;">
                        <div style="font-size:32px; margin-bottom:8px;"></div>
                        <div style="font-family:'Plus Jakarta Sans'; font-size:13px; font-weight:700; color:#8a9ab5; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">{row.prodi}</div>
                        <div style="font-size:15px; font-weight:600; color:#f0f4f8; margin-bottom:2px;">{row.nama}</div>
                        <div style="font-family:Space Mono; font-size:11px; color:#4a5568;">{row.nim}</div>
                        <div style="font-family:Space Mono; font-size:28px; font-weight:700; color:{color}; margin:8px 0;">{row.rata_akhir:.1f}</div>
                        <div class="badge badge-{grade}">{grade}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(df_terbaik, use_container_width=True, hide_index=True)

    # ── Tab 5: Distribusi ──
    with tabs[4]:
        section_header("Distribusi Nilai Keseluruhan")

        df_all_vals = execute_query("""
            SELECT m.prodi,
                   ROUND(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0),2) AS nilai_akhir,
                   n.nilai_uts, n.nilai_uas, n.nilai_tugas
            FROM nilai n JOIN mahasiswa m ON n.nim=m.nim
        """)

        if df_all_vals is not None:
            c1, c2 = st.columns(2)

            with c1:
                fig = go.Figure()
                for prodi in df_all_vals['prodi'].unique():
                    d = df_all_vals[df_all_vals['prodi'] == prodi]
                    fig.add_trace(go.Histogram(
                        x=d['nilai_akhir'], name=prodi, opacity=0.7,
                        nbinsx=20, histnorm='probability density'
                    ))
                fig.update_layout(title="Distribusi Densitas Nilai per Prodi",
                                  barmode='overlay', xaxis_title="Nilai Akhir", **PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                fig2 = go.Figure()
                for prodi, color in zip(df_all_vals['prodi'].unique(), COLOR_SEQ):
                    d = df_all_vals[df_all_vals['prodi'] == prodi]
                    fig2.add_trace(go.Box(
                        y=d['nilai_akhir'], name=prodi,
                        marker=dict(color=color),
                        boxpoints='suspectedoutliers',
                        line=dict(color=color, width=2),
                        fillcolor=hex_to_rgba(color, 0.12)
                    ))
                fig2.update_layout(title="Box Plot Nilai Akhir per Prodi",
                                   yaxis_title="Nilai", **PLOTLY_LAYOUT)
                st.plotly_chart(fig2, use_container_width=True)

            # Heatmap komponen per prodi
            df_heat = df_all_vals.groupby('prodi')[['nilai_uts','nilai_uas','nilai_tugas','nilai_akhir']].mean().round(2)
            fig3 = go.Figure(go.Heatmap(
                z=df_heat.values,
                x=['UTS', 'UAS', 'Tugas', 'Final'],
                y=df_heat.index,
                colorscale=[[0,'#fc8181'],[0.5,'#f6ad55'],[1,'#68d391']],
                text=df_heat.values.round(1),
                texttemplate='%{text}',
                textfont=dict(color='white', family='Space Mono', size=14),
                zmin=0, zmax=100
            ))
            fig3.update_layout(title="Heatmap Rata-rata Komponen Nilai per Prodi", **PLOTLY_LAYOUT)
            st.plotly_chart(fig3, use_container_width=True)

# PAGE: PENCARIAN
elif menu_option == "Pencarian":
    st.markdown('<div class="page-header"><h1>🔍 Pencarian & Filter</h1><p>Cari data mahasiswa, mata kuliah, atau nilai tertentu</p></div>', unsafe_allow_html=True)

    search_type = st.selectbox("Tipe Pencarian",
        ["Cari Mahasiswa", "Cari Mata Kuliah", "Nilai per Mahasiswa"])

    if search_type == "Cari Mahasiswa":
        keyword = st.text_input("Ketik NIM atau nama mahasiswa…", placeholder="contoh: Budi / 2023001")
        if keyword:
            df = execute_query(f"""
                SELECT nim, nama, angkatan, jenis_kelamin, prodi FROM mahasiswa
                WHERE nim LIKE '%{keyword}%' OR nama LIKE '%{keyword}%' ORDER BY nama
            """)
            if df is not None and len(df) > 0:
                st.success(f"{len(df)} hasil ditemukan")
                st.dataframe(df, use_container_width=True, hide_index=True)
                for _, row in df.iterrows():
                    with st.expander(f"Nilai — {row['nama']} ({row['nim']})"):
                        df_n = execute_query(f"""
                            SELECT mk.nama_mk, n.semester_ambil, n.nilai_uts, n.nilai_uas, n.nilai_tugas,
                                   ROUND(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0),2) AS nilai_akhir
                            FROM nilai n JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk
                            WHERE n.nim='{row['nim']}' ORDER BY n.semester_ambil, mk.nama_mk
                        """)
                        if df_n is not None and len(df_n) > 0:
                            df_n['Grade'] = df_n['nilai_akhir'].apply(get_letter_grade)
                            st.dataframe(df_n, use_container_width=True, hide_index=True)
                            c1, c2, c3 = st.columns(3)
                            with c1: st.metric("Rata UTS", f"{df_n['nilai_uts'].mean():.1f}")
                            with c2: st.metric("Rata UAS", f"{df_n['nilai_uas'].mean():.1f}")
                            with c3: st.metric("Rata Final", f"{df_n['nilai_akhir'].mean():.1f}")
            else:
                st.warning("Tidak ada hasil")

    elif search_type == "Cari Mata Kuliah":
        keyword = st.text_input("Ketik kode atau nama mata kuliah…", placeholder="contoh: Kalkulus / MAT101")
        if keyword:
            df = execute_query(f"""
                SELECT kode_mk, nama_mk, sks FROM mata_kuliah
                WHERE kode_mk LIKE '%{keyword}%' OR nama_mk LIKE '%{keyword}%' ORDER BY kode_mk
            """)
            if df is not None and len(df) > 0:
                st.success(f"{len(df)} hasil ditemukan")
                st.dataframe(df, use_container_width=True, hide_index=True)
                for _, row in df.iterrows():
                    with st.expander(f"Statistik — {row['nama_mk']} ({row['kode_mk']})"):
                        df_s = execute_query(f"""
                            SELECT COUNT(DISTINCT n.nim) AS jml_mhs,
                                   ROUND(AVG(n.nilai_uts),2) AS rata_uts,
                                   ROUND(AVG(n.nilai_uas),2) AS rata_uas,
                                   ROUND(AVG(n.nilai_tugas),2) AS rata_tugas,
                                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir
                            FROM nilai n WHERE n.kode_mk='{row['kode_mk']}'
                        """)
                        if df_s is not None:
                            st.dataframe(df_s, use_container_width=True, hide_index=True)
            else:
                st.warning("Tidak ada hasil")

    else:  # Nilai per Mahasiswa
        df_list = execute_query("SELECT nim, nama FROM mahasiswa ORDER BY nama")
        if df_list is not None:
            nim_sel = st.selectbox("Pilih Mahasiswa",
                df_list['nim'].tolist(),
                format_func=lambda x: f"{x} — {df_list[df_list['nim']==x]['nama'].values[0]}")

            df_n = execute_query(f"""
                SELECT m.nama, m.prodi, mk.kode_mk, mk.nama_mk, mk.sks,
                       n.semester_ambil, n.nilai_uts, n.nilai_uas, n.nilai_tugas,
                       ROUND(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0),2) AS nilai_akhir
                FROM nilai n JOIN mahasiswa m ON n.nim=m.nim JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk
                WHERE m.nim='{nim_sel}' ORDER BY n.semester_ambil, mk.nama_mk
            """)

            if df_n is not None and len(df_n) > 0:
                df_n['Grade'] = df_n['nilai_akhir'].apply(get_letter_grade)

                c1, c2, c3, c4 = st.columns(4)
                with c1: kpi_card("", "Nama", df_n['nama'].values[0], df_n['prodi'].values[0], "#63b3ed", "#b794f4")
                with c2: kpi_card("", "Total MK", str(len(df_n)), "Ditempuh", "#68d391", "#63b3ed")
                with c3: kpi_card("", "Rata Final", f"{df_n['nilai_akhir'].mean():.1f}", get_letter_grade(df_n['nilai_akhir'].mean()), "#f6ad55", "#fc8181")
                with c4: kpi_card("", "Total SKS", str(int(df_n['sks'].sum())), "Diambil", "#b794f4", "#63b3ed")

                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df_n, use_container_width=True, hide_index=True)

                # Per-semester chart
                df_sem = df_n.groupby('semester_ambil')['nilai_akhir'].mean().reset_index()
                fig = go.Figure(go.Scatter(
                    x=df_sem['semester_ambil'], y=df_sem['nilai_akhir'],
                    mode='lines+markers',
                    line=dict(color='#63b3ed', width=2.5),
                    marker=dict(size=9, color='#63b3ed', line=dict(color='#ffffff', width=2)),
                    fill='tozeroy', fillcolor='rgba(99,179,237,0.08)'
                ))
                fig.update_layout(title=f"Tren Nilai Akhir per Semester — {df_n['nama'].values[0]}",
                                  xaxis_title="Semester", yaxis_title="Rata-rata Nilai",
                                  yaxis_range=[0,105], **PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹMahasiswa ini belum memiliki nilai")

# PAGE: LAPORAN
elif menu_option == "Laporan":
    st.markdown('<div class="page-header"><h1>📋 Laporan Lengkap</h1><p>Laporan komprehensif untuk program studi</p></div>', unsafe_allow_html=True)

    report_type = st.selectbox("Pilih Laporan", [
        "Ringkasan per Mahasiswa",
        "Ringkasan per Mata Kuliah",
        "Data Tidak Lengkap",
        "Mata Kuliah Tersulit",
        "Risiko Akademik"
    ])

    if report_type == "Ringkasan per Mahasiswa":
        df = execute_query("""
            SELECT m.nim, m.nama, m.prodi, m.angkatan,
                   CASE WHEN m.jenis_kelamin='L' THEN 'Laki-laki' ELSE 'Perempuan' END AS gender,
                   COUNT(n.id_nilai) AS total_mk,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir,
                   ROUND(AVG(n.nilai_uts),2) AS rata_uts,
                   ROUND(AVG(n.nilai_uas),2) AS rata_uas,
                   ROUND(AVG(n.nilai_tugas),2) AS rata_tugas
            FROM mahasiswa m LEFT JOIN nilai n ON m.nim=n.nim
            GROUP BY m.nim, m.nama, m.prodi, m.angkatan, m.jenis_kelamin
            ORDER BY m.prodi, rata_akhir DESC
        """)
        if df is not None:
            df['Grade'] = df['rata_akhir'].apply(lambda x: get_letter_grade(x) if x else '-')
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False)
            st.download_button("Export CSV", csv,
                f"laporan_mahasiswa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")

    elif report_type == "Ringkasan per Mata Kuliah":
        df = execute_query("""
            SELECT mk.kode_mk, mk.nama_mk, mk.sks,
                   COUNT(DISTINCT n.nim) AS jml_mhs,
                   ROUND(AVG(n.nilai_uts),2) AS rata_uts,
                   ROUND(AVG(n.nilai_uas),2) AS rata_uas,
                   ROUND(AVG(n.nilai_tugas),2) AS rata_tugas,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir,
                   ROUND(STDDEV(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS std_dev
            FROM mata_kuliah mk LEFT JOIN nilai n ON mk.kode_mk=n.kode_mk
            GROUP BY mk.kode_mk, mk.nama_mk, mk.sks ORDER BY rata_akhir DESC
        """)
        if df is not None:
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif report_type == "Data Tidak Lengkap":
        df = execute_query("""
            SELECT m.nim, m.nama, mk.nama_mk,
                   n.nilai_uts, n.nilai_uas, n.nilai_tugas,
                   CASE WHEN n.nilai_uts IS NULL AND n.nilai_uas IS NULL AND n.nilai_tugas IS NULL THEN 'SEMUA'
                        WHEN n.nilai_uts IS NULL THEN 'UTS'
                        WHEN n.nilai_uas IS NULL THEN 'UAS'
                        WHEN n.nilai_tugas IS NULL THEN 'TUGAS'
                        ELSE 'LENGKAP' END AS komponen_kosong
            FROM nilai n JOIN mahasiswa m ON n.nim=m.nim JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk
            WHERE n.nilai_uts IS NULL OR n.nilai_uas IS NULL OR n.nilai_tugas IS NULL
            ORDER BY m.nama
        """)
        if df is not None and len(df) > 0:
            st.warning(f"{len(df)} record memiliki nilai tidak lengkap")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("Semua data nilai sudah lengkap!")

    elif report_type == "Mata Kuliah Tersulit":
        df = execute_query("""
            SELECT mk.kode_mk, mk.nama_mk, mk.sks,
                   COUNT(n.id_nilai) AS jml_pengambil,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir,
                   ROUND(STDDEV(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS std_dev,
                   SUM(CASE WHEN (0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)) < 60 THEN 1 ELSE 0 END) AS jml_gagal
            FROM mata_kuliah mk LEFT JOIN nilai n ON mk.kode_mk=n.kode_mk
            GROUP BY mk.kode_mk, mk.nama_mk, mk.sks ORDER BY rata_akhir ASC LIMIT 10
        """)
        if df is not None:
            df['pct_gagal'] = (df['jml_gagal'] / df['jml_pengambil'] * 100).round(1)
            st.dataframe(df, use_container_width=True, hide_index=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['nama_mk'], y=df['rata_akhir'], name='Rata-rata',
                marker_color='#fc8181', opacity=0.8
            ))
            fig.add_trace(go.Scatter(
                x=df['nama_mk'], y=df['pct_gagal'], name='% Gagal',
                mode='lines+markers', yaxis='y2',
                line=dict(color='#f6ad55', width=2.5, dash='dot'),
                marker=dict(size=8, color='#f6ad55')
            ))
            fig.update_layout(
                title="10 Mata Kuliah Tersulit — Nilai & Tingkat Kegagalan",
                xaxis_tickangle=-30,
                yaxis=dict(title="Rata-rata Nilai", range=[0,100],
                           gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#8a9ab5')),
                yaxis2=dict(title="% Gagal", overlaying='y', side='right',
                            range=[0,100], tickfont=dict(color='#f6ad55'),
                            gridcolor='rgba(0,0,0,0)'),
                **PLOTLY_LAYOUT
            )
            st.plotly_chart(fig, use_container_width=True)

    elif report_type == "Risiko Akademik":
        section_header("Identifikasi Mahasiswa Risiko Akademik")

        df = execute_query("""
            SELECT m.nim, m.nama, m.prodi, m.angkatan,
                   COUNT(n.id_nilai) AS total_mk,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)),2) AS rata_akhir,
                   SUM(CASE WHEN (0.3*COALESCE(n.nilai_uts,0)+0.4*COALESCE(n.nilai_uas,0)+0.3*COALESCE(n.nilai_tugas,0)) < 60 THEN 1 ELSE 0 END) AS mk_gagal
            FROM mahasiswa m LEFT JOIN nilai n ON m.nim=n.nim
            GROUP BY m.nim, m.nama, m.prodi, m.angkatan
            HAVING mk_gagal > 0 OR rata_akhir < 65
            ORDER BY rata_akhir ASC
        """)

        if df is not None and len(df) > 0:
            df['risiko'] = df.apply(lambda r:
                'Tinggi' if r['rata_akhir'] < 55 or r['mk_gagal'] >= 3 else
                'Sedang' if r['rata_akhir'] < 65 or r['mk_gagal'] >= 1 else
                'Rendah', axis=1)

            st.warning(f"Ditemukan {len(df)} mahasiswa dengan potensi risiko akademik")
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Risk distribution
            risk_count = df['risiko'].value_counts().reset_index()
            risk_count.columns = ['risiko', 'jumlah']
            colors_risk = {'Tinggi': '#fc8181', 'Sedang': '#f6ad55', 'Rendah': '#68d391'}
            fig = go.Figure(go.Bar(
                x=risk_count['risiko'], y=risk_count['jumlah'],
                marker_color=[colors_risk.get(r, '#63b3ed') for r in risk_count['risiko']],
                text=risk_count['jumlah'], textposition='outside',
                textfont=dict(color='#f0f4f8', family='Space Mono')
            ))
            fig.update_layout(title="Distribusi Level Risiko Akademik", **PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

            csv = df.to_csv(index=False)
            st.download_button("Export Laporan Risiko", csv,
                f"risiko_akademik_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")
        else:
            st.success("Tidak ada mahasiswa dengan risiko akademik terdeteksi")

# PAGE: CRUD
elif menu_option == "CRUD":
    st.markdown('<div class="page-header"><h1>⚡ Operasi Database</h1><p>Create · Read · Update · Delete</p></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="danger-zone">
    <p>Halaman ini memungkinkan modifikasi langsung ke database. Gunakan dengan hati-hati!</p>
    </div>
    """, unsafe_allow_html=True)

    crud_type = st.tabs(["Create", "Read", "Update", "Delete"])

    # ── CREATE ──
    with crud_type[0]:
        create_choice = st.radio("Tipe Data", ["Mahasiswa Baru", "Mata Kuliah Baru", "Nilai Baru"], horizontal=True)

        if create_choice == "Mahasiswa Baru":
            c1, c2 = st.columns(2)
            with c1:
                nim = st.text_input("NIM")
                nama = st.text_input("Nama Lengkap")
                angkatan = st.number_input("Angkatan", 2000, 2050, 2024)
            with c2:
                jk = st.radio("Jenis Kelamin", ["L", "P"], horizontal=True)
                prodi = st.selectbox("Program Studi", ["Statistika", "Matematika", "Informatika"])

            if st.button("Simpan Mahasiswa"):
                if nim and nama:
                    ok, msg = execute_write(
                        "INSERT INTO mahasiswa (nim,nama,angkatan,jenis_kelamin,prodi) VALUES (%s,%s,%s,%s,%s)",
                        (nim, nama, angkatan, jk, prodi)
                    )
                    if ok: st.success("Mahasiswa berhasil ditambahkan!")
                    elif "Duplicate" in msg: st.error(f"NIM '{nim}' sudah terdaftar!")
                    else: st.error(f"{msg}")
                else:
                    st.warning("NIM dan Nama harus diisi!")

        elif create_choice == "Mata Kuliah Baru":
            c1, c2 = st.columns(2)
            with c1:
                kode_mk = st.text_input("Kode MK")
                nama_mk = st.text_input("Nama Mata Kuliah")
            with c2:
                sks = st.number_input("SKS", 1, 6, 3)

            if st.button("Simpan Mata Kuliah"):
                if kode_mk and nama_mk:
                    ok, msg = execute_write(
                        "INSERT INTO mata_kuliah (kode_mk,nama_mk,sks) VALUES (%s,%s,%s)",
                        (kode_mk, nama_mk, sks)
                    )
                    if ok: st.success("Mata Kuliah berhasil ditambahkan!")
                    elif "Duplicate" in msg: st.error(f"Kode '{kode_mk}' sudah ada!")
                    else: st.error(f"{msg}")
                else:
                    st.warning("Kode dan Nama harus diisi!")

        else:  # Nilai Baru
            df_mhs = execute_query("SELECT nim, nama FROM mahasiswa ORDER BY nama")
            df_mk_list = execute_query("SELECT kode_mk, nama_mk FROM mata_kuliah ORDER BY nama_mk")
            if df_mhs is not None and df_mk_list is not None:
                c1, c2 = st.columns(2)
                with c1:
                    nim_sel = st.selectbox("Mahasiswa", df_mhs['nim'].tolist(),
                        format_func=lambda x: f"{x} — {df_mhs[df_mhs['nim']==x]['nama'].values[0]}")
                    kode_sel = st.selectbox("Mata Kuliah", df_mk_list['kode_mk'].tolist(),
                        format_func=lambda x: f"{x} — {df_mk_list[df_mk_list['kode_mk']==x]['nama_mk'].values[0]}")
                    sem = st.number_input("Semester", 1, 14, 1)
                with c2:
                    uts = st.number_input("Nilai UTS", 0.0, 100.0, 0.0)
                    uas = st.number_input("Nilai UAS", 0.0, 100.0, 0.0)
                    tugas = st.number_input("Nilai Tugas", 0.0, 100.0, 0.0)
                    final = round(0.3*uts + 0.4*uas + 0.3*tugas, 2)
                    st.info(f"Preview Nilai Akhir: **{final:.2f}** ({get_letter_grade(final)})")

                if st.button("Simpan Nilai"):
                    ok, msg = execute_write(
                        "INSERT INTO nilai (nim,kode_mk,semester_ambil,nilai_uts,nilai_uas,nilai_tugas) VALUES (%s,%s,%s,%s,%s,%s)",
                        (nim_sel, kode_sel, sem, uts, uas, tugas)
                    )
                    if ok: st.success("Nilai berhasil ditambahkan!")
                    elif "Duplicate" in msg: st.error("Nilai sudah ada untuk kombinasi ini!")
                    else: st.error(f"{msg}")

    # ── READ ──
    with crud_type[1]:
        tbl = st.selectbox("Pilih Tabel", ["mahasiswa", "mata_kuliah", "nilai"])
        queries = {
            "mahasiswa": "SELECT * FROM mahasiswa ORDER BY prodi, nama",
            "mata_kuliah": "SELECT * FROM mata_kuliah ORDER BY kode_mk",
            "nilai": """SELECT n.*, m.nama AS nama_mhs, mk.nama_mk
                        FROM nilai n JOIN mahasiswa m ON n.nim=m.nim
                        JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk ORDER BY m.nama"""
        }
        df = execute_query(queries[tbl])
        if df is not None:
            kpi_card("", "Total Record", f"{len(df):,}", tbl, "#63b3ed", "#b794f4")
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── UPDATE ──
    with crud_type[2]:
        df_nilai_list = execute_query("""
            SELECT n.id_nilai, m.nama, mk.nama_mk, n.semester_ambil,
                   n.nilai_uts, n.nilai_uas, n.nilai_tugas
            FROM nilai n JOIN mahasiswa m ON n.nim=m.nim JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk
            ORDER BY m.nama
        """)

        if df_nilai_list is not None and len(df_nilai_list) > 0:
            id_sel = st.selectbox("Pilih Record Nilai",
                df_nilai_list['id_nilai'].tolist(),
                format_func=lambda x: f"ID {x} — {df_nilai_list[df_nilai_list['id_nilai']==x].iloc[0]['nama']} · {df_nilai_list[df_nilai_list['id_nilai']==x].iloc[0]['nama_mk']}")

            row = df_nilai_list[df_nilai_list['id_nilai'] == id_sel].iloc[0]
            c1, c2, c3 = st.columns(3)
            with c1: new_uts = st.number_input("UTS", 0.0, 100.0, float(row['nilai_uts'] or 0))
            with c2: new_uas = st.number_input("UAS", 0.0, 100.0, float(row['nilai_uas'] or 0))
            with c3: new_tugas = st.number_input("Tugas", 0.0, 100.0, float(row['nilai_tugas'] or 0))

            preview = round(0.3*new_uts + 0.4*new_uas + 0.3*new_tugas, 2)
            st.info(f"Preview Nilai Akhir Baru: **{preview:.2f}** ({get_letter_grade(preview)})")

            if st.button("Update Nilai"):
                ok, msg = execute_write(
                    "UPDATE nilai SET nilai_uts=%s, nilai_uas=%s, nilai_tugas=%s WHERE id_nilai=%s",
                    (new_uts, new_uas, new_tugas, id_sel)
                )
                if ok: st.success("Nilai berhasil diupdate!")
                else: st.error(f"{msg}")

    # ── DELETE ──
    with crud_type[3]:
        del_type = st.radio("Hapus", ["Mahasiswa", "Nilai"], horizontal=True)

        if del_type == "Mahasiswa":
            df_mhs = execute_query("SELECT nim, nama FROM mahasiswa ORDER BY nama")
            if df_mhs is not None:
                nim_del = st.selectbox("Pilih Mahasiswa",
                    df_mhs['nim'].tolist(),
                    format_func=lambda x: f"{x} — {df_mhs[df_mhs['nim']==x]['nama'].values[0]}")
                confirm = st.checkbox("Saya memahami data ini akan dihapus permanen (termasuk semua nilai)")
                if st.button("Hapus Mahasiswa"):
                    if confirm:
                        ok, msg = execute_write("DELETE FROM mahasiswa WHERE nim=%s", (nim_del,))
                        if ok: st.success("Mahasiswa berhasil dihapus!")
                        else: st.error(f"{msg}")
                    else:
                        st.warning("Centang konfirmasi terlebih dahulu")

        else:  # Nilai
            df_n = execute_query("""
                SELECT n.id_nilai, m.nama, mk.nama_mk, n.semester_ambil
                FROM nilai n JOIN mahasiswa m ON n.nim=m.nim JOIN mata_kuliah mk ON n.kode_mk=mk.kode_mk
                ORDER BY m.nama
            """)
            if df_n is not None:
                id_del = st.selectbox("Pilih Nilai",
                    df_n['id_nilai'].tolist(),
                    format_func=lambda x: f"ID {x} — {df_n[df_n['id_nilai']==x].iloc[0]['nama']} · {df_n[df_n['id_nilai']==x].iloc[0]['nama_mk']}")
                confirm = st.checkbox("Saya yakin ingin menghapus nilai ini")
                if st.button("Hapus Nilai"):
                    if confirm:
                        ok, msg = execute_write("DELETE FROM nilai WHERE id_nilai=%s", (id_del,))
                        if ok: st.success("Nilai berhasil dihapus!")
                        else: st.error(f"{msg}")
                    else:
                        st.warning("Centang konfirmasi terlebih dahulu")

# FOOTER
st.markdown("""
<div style="margin-top:60px; padding:24px 0; border-top:1px solid rgba(255,255,255,0.05); text-align:center;">
    <span style="font-family:'Space Mono',monospace; font-size:11px; color:#2d3748; letter-spacing:0.1em;">
    AKADEMIQ · DASHBOARD NILAI MAHASISWA · AHMAD FAUZAN · ALESANDRIA AZZAHRA · NAUFAL RAHMAN · 2026
    </span>
</div>
""", unsafe_allow_html=True)

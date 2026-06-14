import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error as MySQLError
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from sqlalchemy import create_engine
import warnings
import re

warnings.filterwarnings('ignore')

# Quick fix untuk deprecated parameters
def fix_deprecated_params():
    pass

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Dashboard Akademik",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== DATABASE CONNECTION =====
@st.cache_resource
def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',  # Sesuaikan dengan username MySQL Anda
            password='',  # Sesuaikan dengan password MySQL Anda (kosong jika tidak ada)
            database='db_akademik',
            autocommit=True
        )
        return conn
    except MySQLError as err:
        st.error(f"❌ Error koneksi database: {err}")
        return None

@st.cache_resource
def get_sqlalchemy_engine():
    """Membuat SQLAlchemy engine untuk pandas read_sql"""
    try:
        engine = create_engine('mysql+pymysql://root:@localhost/db_akademik')
        return engine
    except Exception as err:
        return None

# ===== HELPER FUNCTIONS =====
def execute_query(query):
    """Menjalankan query dan mengembalikan DataFrame"""
    try:
        engine = get_sqlalchemy_engine()
        if engine is None:
            conn = get_db_connection()
            if conn is None:
                st.error("❌ Tidak dapat terhubung ke database")
                return None
            df = pd.read_sql(query, conn)
            conn.close()
        else:
            df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"❌ Error executing query: {str(e)}")
        return None

def calculate_final_grade(row):
    """Menghitung nilai akhir dari komponen nilai"""
    uts = row.get('nilai_uts', 0) or 0
    uas = row.get('nilai_uas', 0) or 0
    tugas = row.get('nilai_tugas', 0) or 0
    return 0.3 * uts + 0.4 * uas + 0.3 * tugas

def get_letter_grade(score):
    """Konversi nilai numerik ke huruf mutu"""
    if score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'E'

# ===== SIDEBAR CONFIGURATION =====
st.sidebar.title("⚙️ Pengaturan Dashboard")
st.sidebar.divider()

menu_option = st.sidebar.radio(
    "Pilih Halaman:",
    [
        "📈 Dashboard Utama",
        "👥 Data Mahasiswa",
        "📚 Data Mata Kuliah",
        "📊 Analisis Nilai",
        "🔍 Pencarian & Filter",
        "📋 Laporan Lengkap",
        "⚡ CRUD Operations"
    ]
)

st.sidebar.divider()
st.sidebar.info(
    "📌 Sistem Nilai Mahasiswa\n\n"
    "Database: db_akademik\n"
    "DBMS: MySQL 8 / MariaDB\n"
    "Skema: Opsi B (semester_ambil di nilai)"
)

# ===== MAIN DASHBOARD =====
if menu_option == "📈 Dashboard Utama":
    st.title("📊 Dashboard Sistem Nilai Mahasiswa")
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Mahasiswa
    with col1:
        df_mhs = execute_query("SELECT COUNT(*) as total FROM mahasiswa")
        if df_mhs is not None:
            total_mhs = df_mhs['total'].values[0]
            st.metric("👥 Total Mahasiswa", total_mhs, delta=None)
    
    # Total Mata Kuliah
    with col2:
        df_mk = execute_query("SELECT COUNT(*) as total FROM mata_kuliah")
        if df_mk is not None:
            total_mk = df_mk['total'].values[0]
            st.metric("📚 Total Mata Kuliah", total_mk, delta=None)
    
    # Total Nilai Tercatat
    with col3:
        df_nilai = execute_query("SELECT COUNT(*) as total FROM nilai")
        if df_nilai is not None:
            total_nilai = df_nilai['total'].values[0]
            st.metric("📊 Total Nilai Tercatat", total_nilai, delta=None)
    
    # Rata-rata Nilai Keseluruhan
    with col4:
        df_avg = execute_query(
            """SELECT ROUND(AVG(0.3*COALESCE(nilai_uts,0) 
               + 0.4*COALESCE(nilai_uas,0) 
               + 0.3*COALESCE(nilai_tugas,0)), 2) as rata_nilai 
               FROM nilai"""
        )
        if df_avg is not None:
            avg_nilai = df_avg['rata_nilai'].values[0]
            st.metric("📈 Rata-rata Nilai", f"{avg_nilai:.2f}", delta=None)
    
    st.markdown("---")
    
    # Distribusi Huruf Mutu
    st.subheader("📊 Distribusi Huruf Mutu")
    
    df_huruf = execute_query("""
        SELECT CASE WHEN na >= 80 THEN 'A'
                    WHEN na >= 70 THEN 'B'
                    WHEN na >= 60 THEN 'C'
                    WHEN na >= 50 THEN 'D'
                    ELSE 'E' END AS huruf_mutu,
               COUNT(*) AS jumlah
        FROM (
            SELECT 0.3*COALESCE(nilai_uts,0)
                   + 0.4*COALESCE(nilai_uas,0)
                   + 0.3*COALESCE(nilai_tugas,0) AS na
            FROM nilai
        ) t
        GROUP BY huruf_mutu
        ORDER BY huruf_mutu
    """)
    
    if df_huruf is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                df_huruf,
                values='jumlah',
                names='huruf_mutu',
                title='Distribusi Huruf Mutu',
                color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6']
            )
            st.plotly_chart(fig_pie, width='stretch')
        
        with col2:
            fig_bar = px.bar(
                df_huruf,
                x='huruf_mutu',
                y='jumlah',
                title='Jumlah Mahasiswa per Huruf Mutu',
                labels={'huruf_mutu': 'Huruf Mutu', 'jumlah': 'Jumlah Mahasiswa'},
                color='huruf_mutu',
                color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6']
            )
            st.plotly_chart(fig_bar, width='stretch')
    
    st.markdown("---")
    
    # Rata-rata Nilai per Prodi
    st.subheader("📚 Performa per Program Studi")
    
    df_prodi = execute_query("""
        SELECT m.prodi,
               COUNT(*) AS jml_nilai,
               ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                       + 0.4*COALESCE(n.nilai_uas,0)
                       + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir,
               ROUND(AVG(n.nilai_uts), 2) as rata_uts,
               ROUND(AVG(n.nilai_uas), 2) as rata_uas,
               ROUND(AVG(n.nilai_tugas), 2) as rata_tugas
        FROM nilai n
        JOIN mahasiswa m ON n.nim = m.nim
        GROUP BY m.prodi
        ORDER BY rata_nilai_akhir DESC
    """)
    
    if df_prodi is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_prodi_bar = px.bar(
                df_prodi,
                x='prodi',
                y='rata_nilai_akhir',
                title='Rata-rata Nilai Akhir per Prodi',
                labels={'prodi': 'Program Studi', 'rata_nilai_akhir': 'Rata-rata Nilai'},
                color='rata_nilai_akhir',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_prodi_bar, width='stretch')
        
        with col2:
            st.dataframe(df_prodi, width='stretch', hide_index=True)

elif menu_option == "👥 Data Mahasiswa":
    st.title("👥 Data Mahasiswa")
    st.markdown("---")
    
    # Filter opsi
    col1, col2, col3 = st.columns(3)
    
    with col1:
        prodi_filter = st.multiselect(
            "Filter Program Studi:",
            execute_query("SELECT DISTINCT prodi FROM mahasiswa ORDER BY prodi")['prodi'].tolist() if execute_query("SELECT DISTINCT prodi FROM mahasiswa ORDER BY prodi") is not None else [],
            default=None
        )
    
    with col2:
        angkatan_filter = st.multiselect(
            "Filter Angkatan:",
            sorted(execute_query("SELECT DISTINCT angkatan FROM mahasiswa ORDER BY angkatan DESC")['angkatan'].tolist()) if execute_query("SELECT DISTINCT angkatan FROM mahasiswa ORDER BY angkatan DESC") is not None else [],
            default=None
        )
    
    with col3:
        gender_filter = st.multiselect(
            "Filter Jenis Kelamin:",
            [('L', 'Laki-laki'), ('P', 'Perempuan')],
            default=None,
            format_func=lambda x: x[1]
        )
    
    # Query with filters
    query = "SELECT nim, nama, angkatan, jenis_kelamin, prodi FROM mahasiswa WHERE 1=1"
    
    if prodi_filter:
        prodi_list = "', '".join(prodi_filter)
        query += f" AND prodi IN ('{prodi_list}')"
    
    if angkatan_filter:
        angkatan_list = ", ".join(map(str, angkatan_filter))
        query += f" AND angkatan IN ({angkatan_list})"
    
    if gender_filter:
        gender_list = "', '".join([g[0] for g in gender_filter])
        query += f" AND jenis_kelamin IN ('{gender_list}')"
    
    query += " ORDER BY prodi, angkatan DESC, nama"
    
    df_mahasiswa = execute_query(query)
    
    if df_mahasiswa is not None:
        st.metric("Total Mahasiswa (Filtered)", len(df_mahasiswa))
        
        st.subheader("Daftar Mahasiswa")
        st.dataframe(df_mahasiswa, width='stretch', hide_index=True)
        
        # Download button
        csv = df_mahasiswa.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"mahasiswa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    
    # Statistik Gender
    st.subheader("📊 Statistik Gender")
    
    df_gender = execute_query("""
        SELECT jenis_kelamin,
               CASE WHEN jenis_kelamin = 'L' THEN 'Laki-laki' ELSE 'Perempuan' END AS gender,
               COUNT(*) AS jumlah
        FROM mahasiswa
        GROUP BY jenis_kelamin
    """)
    
    if df_gender is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(df_gender, values='jumlah', names='gender', title='Distribusi Gender')
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.dataframe(df_gender[['gender', 'jumlah']], width='stretch', hide_index=True)

elif menu_option == "📚 Data Mata Kuliah":
    st.title("📚 Data Mata Kuliah")
    st.markdown("---")
    
    df_mk_list = execute_query("SELECT kode_mk, nama_mk, sks FROM mata_kuliah ORDER BY kode_mk")
    
    if df_mk_list is not None:
        st.metric("Total Mata Kuliah", len(df_mk_list))
        st.metric("Total SKS", df_mk_list['sks'].sum())
        
        st.subheader("Daftar Mata Kuliah")
        st.dataframe(df_mk_list, width='stretch', hide_index=True)
    
    st.markdown("---")
    
    # Statistik Mata Kuliah
    st.subheader("📊 Statistik per Mata Kuliah")
    
    df_mk_stats = execute_query("""
        SELECT mk.kode_mk,
               mk.nama_mk,
               mk.sks,
               COUNT(DISTINCT n.nim) AS jml_mahasiswa,
               ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                       + 0.4*COALESCE(n.nilai_uas,0)
                       + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir,
               ROUND(AVG(n.nilai_uts), 2) AS rata_uts,
               ROUND(AVG(n.nilai_uas), 2) AS rata_uas,
               ROUND(AVG(n.nilai_tugas), 2) AS rata_tugas
        FROM mata_kuliah mk
        LEFT JOIN nilai n ON mk.kode_mk = n.kode_mk
        GROUP BY mk.kode_mk, mk.nama_mk, mk.sks
        ORDER BY rata_nilai_akhir DESC
    """)
    
    if df_mk_stats is not None:
        st.dataframe(df_mk_stats, width='stretch', hide_index=True)
        
        # Visualisasi
        fig = px.bar(
            df_mk_stats,
            x='nama_mk',
            y='rata_nilai_akhir',
            title='Rata-rata Nilai Akhir per Mata Kuliah',
            labels={'nama_mk': 'Mata Kuliah', 'rata_nilai_akhir': 'Rata-rata Nilai'},
            color='rata_nilai_akhir',
            color_continuous_scale='Viridis'
        )
        fig.update_xaxis(tickangle=-45)
        st.plotly_chart(fig, width='stretch')

elif menu_option == "📊 Analisis Nilai":
    st.title("📊 Analisis Nilai")
    st.markdown("---")
    
    # Submenu
    analysis_type = st.selectbox(
        "Pilih Tipe Analisis:",
        [
            "5 Nilai Tertinggi",
            "5 Nilai Terendah",
            "Perbandingan Gender",
            "Retake Analysis",
            "Semester Performance",
            "Mahasiswa Terbaik per Prodi"
        ]
    )
    
    if analysis_type == "5 Nilai Tertinggi":
        st.subheader("🏆 5 Nilai Akhir Tertinggi")
        
        df_top = execute_query("""
            SELECT m.nama AS nama_mahasiswa,
                   m.nim,
                   m.prodi,
                   mk.nama_mk,
                   n.nilai_uts, n.nilai_uas, n.nilai_tugas,
                   ROUND(0.3*COALESCE(n.nilai_uts,0)
                           + 0.4*COALESCE(n.nilai_uas,0)
                           + 0.3*COALESCE(n.nilai_tugas,0), 2) AS nilai_akhir
            FROM nilai n
            JOIN mahasiswa m ON n.nim = m.nim
            JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
            ORDER BY nilai_akhir DESC
            LIMIT 5
        """)
        
        if df_top is not None:
            st.dataframe(df_top, width='stretch', hide_index=True)
            
            fig = px.bar(
                df_top,
                x='nama_mahasiswa',
                y='nilai_akhir',
                title='5 Nilai Tertinggi',
                labels={'nama_mahasiswa': 'Mahasiswa', 'nilai_akhir': 'Nilai Akhir'},
                color='nilai_akhir',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, width='stretch')
    
    elif analysis_type == "5 Nilai Terendah":
        st.subheader("📉 5 Nilai Akhir Terendah")
        
        df_bottom = execute_query("""
            SELECT m.nama AS nama_mahasiswa,
                   m.nim,
                   m.prodi,
                   mk.nama_mk,
                   n.nilai_uts, n.nilai_uas, n.nilai_tugas,
                   ROUND(0.3*COALESCE(n.nilai_uts,0)
                           + 0.4*COALESCE(n.nilai_uas,0)
                           + 0.3*COALESCE(n.nilai_tugas,0), 2) AS nilai_akhir
            FROM nilai n
            JOIN mahasiswa m ON n.nim = m.nim
            JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
            ORDER BY nilai_akhir ASC
            LIMIT 5
        """)
        
        if df_bottom is not None:
            st.dataframe(df_bottom, width='stretch', hide_index=True)
            
            fig = px.bar(
                df_bottom,
                x='nama_mahasiswa',
                y='nilai_akhir',
                title='5 Nilai Terendah',
                labels={'nama_mahasiswa': 'Mahasiswa', 'nilai_akhir': 'Nilai Akhir'},
                color='nilai_akhir',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, width='stretch')
    
    elif analysis_type == "Perbandingan Gender":
        st.subheader("👥 Perbandingan Performa Gender")
        
        df_gender_stats = execute_query("""
            SELECT m.jenis_kelamin,
                   CASE WHEN m.jenis_kelamin = 'L' THEN 'Laki-laki' ELSE 'Perempuan' END AS gender,
                   COUNT(DISTINCT m.nim) AS jml_mahasiswa,
                   COUNT(n.id_nilai) AS jml_nilai,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                           + 0.4*COALESCE(n.nilai_uas,0)
                           + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir,
                   ROUND(AVG(n.nilai_uts), 2) AS rata_uts,
                   ROUND(AVG(n.nilai_uas), 2) AS rata_uas,
                   ROUND(AVG(n.nilai_tugas), 2) AS rata_tugas
            FROM mahasiswa m
            LEFT JOIN nilai n ON m.nim = n.nim
            GROUP BY m.jenis_kelamin
        """)
        
        if df_gender_stats is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(df_gender_stats, width='stretch', hide_index=True)
            
            with col2:
                fig = px.bar(
                    df_gender_stats,
                    x='gender',
                    y='rata_nilai_akhir',
                    title='Rata-rata Nilai per Gender',
                    labels={'gender': 'Jenis Kelamin', 'rata_nilai_akhir': 'Rata-rata Nilai'},
                    color='gender',
                    color_discrete_sequence=['#3498db', '#e74c3c']
                )
                st.plotly_chart(fig, width='stretch')
    
    elif analysis_type == "Retake Analysis":
        st.subheader("🔄 Analisis Retake (Pengambilan Ulang)")
        
        df_retake = execute_query("""
            SELECT m.nim,
                   m.nama,
                   mk.nama_mk,
                   COUNT(*) AS jumlah_retake,
                   GROUP_CONCAT(CONCAT('Sem ', n.semester_ambil, ': ', 
                       ROUND(0.3*COALESCE(n.nilai_uts,0) + 0.4*COALESCE(n.nilai_uas,0) + 0.3*COALESCE(n.nilai_tugas,0), 2)) 
                       SEPARATOR ' | ') AS detail_nilai
            FROM nilai n
            JOIN mahasiswa m ON n.nim = m.nim
            JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
            GROUP BY n.nim, n.kode_mk, m.nama, mk.nama_mk
            HAVING COUNT(*) > 1
            ORDER BY m.nama, mk.nama_mk
        """)
        
        if df_retake is not None and len(df_retake) > 0:
            st.dataframe(df_retake, width='stretch', hide_index=True)
            st.success(f"✅ Ditemukan {len(df_retake)} record retake")
        else:
            st.info("ℹ️ Tidak ada mahasiswa yang retake")
    
    elif analysis_type == "Semester Performance":
        st.subheader("📅 Performa per Semester Pengambilan")
        
        df_semester = execute_query("""
            SELECT n.semester_ambil,
                   COUNT(*) AS jml_nilai,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                           + 0.4*COALESCE(n.nilai_uas,0)
                           + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir,
                   ROUND(AVG(n.nilai_uts), 2) AS rata_uts,
                   ROUND(AVG(n.nilai_uas), 2) AS rata_uas,
                   ROUND(AVG(n.nilai_tugas), 2) AS rata_tugas
            FROM nilai n
            GROUP BY n.semester_ambil
            ORDER BY n.semester_ambil
        """)
        
        if df_semester is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(df_semester, width='stretch', hide_index=True)
            
            with col2:
                fig = px.line(
                    df_semester,
                    x='semester_ambil',
                    y='rata_nilai_akhir',
                    title='Tren Nilai per Semester',
                    labels={'semester_ambil': 'Semester', 'rata_nilai_akhir': 'Rata-rata Nilai'},
                    markers=True
                )
                st.plotly_chart(fig, width='stretch')
    
    elif analysis_type == "Mahasiswa Terbaik per Prodi":
        st.subheader("🏅 Mahasiswa Terbaik per Program Studi")
        
        df_terbaik = execute_query("""
            SELECT m.prodi,
                   m.nim,
                   m.nama,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                           + 0.4*COALESCE(n.nilai_uas,0)
                           + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir
            FROM nilai n
            JOIN mahasiswa m ON n.nim = m.nim
            GROUP BY m.prodi, m.nim, m.nama
            ORDER BY m.prodi, rata_nilai_akhir DESC
        """)
        
        if df_terbaik is not None:
            st.dataframe(df_terbaik, width='stretch', hide_index=True)

elif menu_option == "🔍 Pencarian & Filter":
    st.title("🔍 Pencarian & Filter Data")
    st.markdown("---")
    
    search_type = st.selectbox(
        "Pilih Tipe Pencarian:",
        ["Cari Mahasiswa", "Cari Mata Kuliah", "Cari Nilai Mahasiswa"]
    )
    
    if search_type == "Cari Mahasiswa":
        st.subheader("👥 Pencarian Mahasiswa")
        
        keyword = st.text_input("Masukkan NIM atau nama mahasiswa:")
        
        if keyword:
            query = f"""
                SELECT nim, nama, angkatan, jenis_kelamin, prodi
                FROM mahasiswa
                WHERE nim LIKE '%{keyword}%' OR nama LIKE '%{keyword}%'
                ORDER BY nama
            """
            
            df = execute_query(query)
            
            if df is not None and len(df) > 0:
                st.success(f"✅ Ditemukan {len(df)} hasil")
                st.dataframe(df, width='stretch', hide_index=True)
                
                # Tampilkan detail nilai untuk setiap mahasiswa
                for idx, row in df.iterrows():
                    with st.expander(f"📊 Lihat Nilai {row['nama']} ({row['nim']})"):
                        df_nilai = execute_query(f"""
                            SELECT mk.nama_mk,
                                   n.semester_ambil,
                                   n.nilai_uts,
                                   n.nilai_uas,
                                   n.nilai_tugas,
                                   ROUND(0.3*COALESCE(n.nilai_uts,0)
                                           + 0.4*COALESCE(n.nilai_uas,0)
                                           + 0.3*COALESCE(n.nilai_tugas,0), 2) AS nilai_akhir
                            FROM nilai n
                            JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
                            WHERE n.nim = '{row['nim']}'
                            ORDER BY n.semester_ambil, mk.nama_mk
                        """)
                        
                        if df_nilai is not None:
                            st.dataframe(df_nilai, width='stretch', hide_index=True)
                            
                            # Ringkasan
                            avg_nilai = df_nilai['nilai_akhir'].mean()
                            st.metric("Rata-rata Nilai", f"{avg_nilai:.2f}")
            else:
                st.warning("⚠️ Tidak ada hasil pencarian")
    
    elif search_type == "Cari Mata Kuliah":
        st.subheader("📚 Pencarian Mata Kuliah")
        
        keyword = st.text_input("Masukkan kode atau nama mata kuliah:")
        
        if keyword:
            query = f"""
                SELECT kode_mk, nama_mk, sks
                FROM mata_kuliah
                WHERE kode_mk LIKE '%{keyword}%' OR nama_mk LIKE '%{keyword}%'
                ORDER BY kode_mk
            """
            
            df = execute_query(query)
            
            if df is not None and len(df) > 0:
                st.success(f"✅ Ditemukan {len(df)} hasil")
                st.dataframe(df, width='stretch', hide_index=True)
                
                # Tampilkan statistik nilai per mata kuliah
                for idx, row in df.iterrows():
                    with st.expander(f"📊 Statistik {row['nama_mk']} ({row['kode_mk']})"):
                        df_stats = execute_query(f"""
                            SELECT COUNT(DISTINCT n.nim) AS jml_mahasiswa,
                                   ROUND(AVG(n.nilai_uts), 2) AS rata_uts,
                                   ROUND(AVG(n.nilai_uas), 2) AS rata_uas,
                                   ROUND(AVG(n.nilai_tugas), 2) AS rata_tugas,
                                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                                           + 0.4*COALESCE(n.nilai_uas,0)
                                           + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir
                            FROM nilai n
                            WHERE n.kode_mk = '{row['kode_mk']}'
                        """)
                        
                        if df_stats is not None:
                            st.dataframe(df_stats, width='stretch', hide_index=True)
            else:
                st.warning("⚠️ Tidak ada hasil pencarian")
    
    elif search_type == "Cari Nilai Mahasiswa":
        st.subheader("📊 Pencarian Nilai Mahasiswa")
        
        # List mahasiswa
        df_list = execute_query("SELECT nim, nama FROM mahasiswa ORDER BY nama")
        
        if df_list is not None:
            nim_selected = st.selectbox(
                "Pilih Mahasiswa:",
                df_list['nim'].tolist(),
                format_func=lambda x: f"{x} - {df_list[df_list['nim']==x]['nama'].values[0]}"
            )
            
            df_nilai = execute_query(f"""
                SELECT m.nama,
                       m.nim,
                       m.prodi,
                       mk.kode_mk,
                       mk.nama_mk,
                       mk.sks,
                       n.semester_ambil,
                       n.nilai_uts,
                       n.nilai_uas,
                       n.nilai_tugas,
                       ROUND(0.3*COALESCE(n.nilai_uts,0)
                               + 0.4*COALESCE(n.nilai_uas,0)
                               + 0.3*COALESCE(n.nilai_tugas,0), 2) AS nilai_akhir
                FROM nilai n
                JOIN mahasiswa m ON n.nim = m.nim
                JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
                WHERE m.nim = '{nim_selected}'
                ORDER BY n.semester_ambil, mk.nama_mk
            """)
            
            if df_nilai is not None and len(df_nilai) > 0:
                st.success(f"✅ Ditemukan {len(df_nilai)} record nilai")
                
                # Detail mahasiswa
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nama", df_nilai['nama'].values[0])
                with col2:
                    st.metric("Program Studi", df_nilai['prodi'].values[0])
                with col3:
                    st.metric("Total MK", len(df_nilai))
                
                st.dataframe(df_nilai, width='stretch', hide_index=True)
                
                # Ringkasan
                col1, col2, col3 = st.columns(3)
                with col1:
                    rata_uts = df_nilai['nilai_uts'].mean()
                    st.metric("Rata-rata UTS", f"{rata_uts:.2f}")
                with col2:
                    rata_uas = df_nilai['nilai_uas'].mean()
                    st.metric("Rata-rata UAS", f"{rata_uas:.2f}")
                with col3:
                    rata_tugas = df_nilai['nilai_tugas'].mean()
                    st.metric("Rata-rata Tugas", f"{rata_tugas:.2f}")
                
                rata_akhir = df_nilai['nilai_akhir'].mean()
                st.metric("Rata-rata Nilai Akhir", f"{rata_akhir:.2f}")
            else:
                st.info("ℹ️ Mahasiswa ini belum memiliki nilai")

elif menu_option == "📋 Laporan Lengkap":
    st.title("📋 Laporan Lengkap")
    st.markdown("---")
    
    report_type = st.selectbox(
        "Pilih Tipe Laporan:",
        [
            "Ringkasan per Mahasiswa",
            "Ringkasan per Mata Kuliah",
            "Data Tidak Lengkap",
            "Mata Kuliah Tersulit"
        ]
    )
    
    if report_type == "Ringkasan per Mahasiswa":
        st.subheader("📊 Ringkasan Akademik per Mahasiswa")
        
        df_summary = execute_query("""
            SELECT m.nim,
                   m.nama,
                   m.prodi,
                   m.angkatan,
                   CASE WHEN m.jenis_kelamin = 'L' THEN 'Laki-laki' ELSE 'Perempuan' END AS gender,
                   COUNT(n.id_nilai) AS total_mk,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                           + 0.4*COALESCE(n.nilai_uas,0)
                           + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir,
                   ROUND(AVG(n.nilai_uts), 2) AS rata_uts,
                   ROUND(AVG(n.nilai_uas), 2) AS rata_uas,
                   ROUND(AVG(n.nilai_tugas), 2) AS rata_tugas,
                   MAX(n.semester_ambil) AS semester_tertinggi
            FROM mahasiswa m
            LEFT JOIN nilai n ON m.nim = n.nim
            GROUP BY m.nim, m.nama, m.prodi, m.angkatan, m.jenis_kelamin
            ORDER BY m.prodi, m.angkatan DESC, rata_nilai_akhir DESC
        """)
        
        if df_summary is not None:
            st.dataframe(df_summary, width='stretch', hide_index=True)
            
            # Download button
            csv = df_summary.to_csv(index=False)
            st.download_button(
                label="📥 Download Laporan CSV",
                data=csv,
                file_name=f"laporan_mahasiswa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    elif report_type == "Ringkasan per Mata Kuliah":
        st.subheader("📚 Ringkasan per Mata Kuliah")
        
        df_mk_summary = execute_query("""
            SELECT mk.kode_mk,
                   mk.nama_mk,
                   mk.sks,
                   COUNT(DISTINCT n.nim) AS jml_mahasiswa,
                   ROUND(AVG(n.nilai_uts), 2) AS rata_uts,
                   ROUND(AVG(n.nilai_uas), 2) AS rata_uas,
                   ROUND(AVG(n.nilai_tugas), 2) AS rata_tugas,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                           + 0.4*COALESCE(n.nilai_uas,0)
                           + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir
            FROM mata_kuliah mk
            LEFT JOIN nilai n ON mk.kode_mk = n.kode_mk
            GROUP BY mk.kode_mk, mk.nama_mk, mk.sks
            ORDER BY rata_nilai_akhir DESC
        """)
        
        if df_mk_summary is not None:
            st.dataframe(df_mk_summary, width='stretch', hide_index=True)
    
    elif report_type == "Data Tidak Lengkap":
        st.subheader("⚠️ Data Nilai yang Tidak Lengkap (NULL)")
        
        df_incomplete = execute_query("""
            SELECT m.nim,
                   m.nama,
                   mk.nama_mk,
                   n.nilai_uts,
                   n.nilai_uas,
                   n.nilai_tugas,
                   CASE WHEN n.nilai_uts IS NULL THEN 'UTS' 
                        WHEN n.nilai_uas IS NULL THEN 'UAS'
                        WHEN n.nilai_tugas IS NULL THEN 'TUGAS'
                        ELSE 'LENGKAP' END AS komponen_kosong
            FROM nilai n
            JOIN mahasiswa m ON n.nim = m.nim
            JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
            WHERE n.nilai_uts IS NULL OR n.nilai_uas IS NULL OR n.nilai_tugas IS NULL
            ORDER BY m.nama, mk.nama_mk
        """)
        
        if df_incomplete is not None and len(df_incomplete) > 0:
            st.warning(f"⚠️ Ditemukan {len(df_incomplete)} record dengan data tidak lengkap")
            st.dataframe(df_incomplete, width='stretch', hide_index=True)
        else:
            st.success("✅ Semua data nilai sudah lengkap!")
    
    elif report_type == "Mata Kuliah Tersulit":
        st.subheader("📉 5 Mata Kuliah Tersulit (Rata-rata Terendah)")
        
        df_hardest = execute_query("""
            SELECT mk.kode_mk,
                   mk.nama_mk,
                   mk.sks,
                   COUNT(n.id_nilai) AS jml_pengambil,
                   ROUND(AVG(n.nilai_uts), 2) AS rata_uts,
                   ROUND(AVG(n.nilai_uas), 2) AS rata_uas,
                   ROUND(AVG(n.nilai_tugas), 2) AS rata_tugas,
                   ROUND(AVG(0.3*COALESCE(n.nilai_uts,0)
                           + 0.4*COALESCE(n.nilai_uas,0)
                           + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS rata_nilai_akhir,
                   ROUND(STDDEV(0.3*COALESCE(n.nilai_uts,0)
                              + 0.4*COALESCE(n.nilai_uas,0)
                              + 0.3*COALESCE(n.nilai_tugas,0)), 2) AS std_dev
            FROM mata_kuliah mk
            LEFT JOIN nilai n ON mk.kode_mk = n.kode_mk
            GROUP BY mk.kode_mk, mk.nama_mk, mk.sks
            ORDER BY rata_nilai_akhir ASC
            LIMIT 5
        """)
        
        if df_hardest is not None:
            st.dataframe(df_hardest, width='stretch', hide_index=True)
            
            fig = px.bar(
                df_hardest,
                x='nama_mk',
                y='rata_nilai_akhir',
                title='5 Mata Kuliah Tersulit',
                labels={'nama_mk': 'Mata Kuliah', 'rata_nilai_akhir': 'Rata-rata Nilai'},
                color='rata_nilai_akhir',
                color_continuous_scale='Reds'
            )
            fig.update_xaxis(tickangle=-45)
            st.plotly_chart(fig, width='stretch')

elif menu_option == "⚡ CRUD Operations":
    st.title("⚡ Operasi Database (CRUD)")
    st.markdown("---")
    
    st.warning("⚠️ Halaman ini memungkinkan modifikasi data. Gunakan dengan hati-hati!")
    
    crud_type = st.selectbox(
        "Pilih Operasi:",
        ["CREATE", "READ", "UPDATE", "DELETE"]
    )
    
    if crud_type == "CREATE":
        st.subheader("➕ Tambah Data Baru")
        
        create_choice = st.radio("Pilih tipe data:", ["Mahasiswa Baru", "Mata Kuliah Baru", "Nilai Baru"])
        
        if create_choice == "Mahasiswa Baru":
            st.info("Formulir Tambah Mahasiswa")
            
            nim = st.text_input("NIM:")
            nama = st.text_input("Nama:")
            angkatan = st.number_input("Angkatan:", min_value=2000, max_value=2050, value=2024)
            jenis_kelamin = st.radio("Jenis Kelamin:", ["L", "P"], horizontal=True)
            prodi = st.selectbox("Program Studi:", ["Statistika", "Matematika", "Informatika"])
            
            if st.button("💾 Simpan Mahasiswa"):
                if nim and nama:
                    try:
                        conn = get_db_connection()
                        if conn is None:
                            st.error("❌ Tidak dapat terhubung ke database")
                            st.stop()
                        
                        cursor = conn.cursor()
                        
                        query = """INSERT INTO mahasiswa (nim, nama, angkatan, jenis_kelamin, prodi)
                                  VALUES (%s, %s, %s, %s, %s)"""
                        
                        cursor.execute(query, (nim, nama, angkatan, jenis_kelamin, prodi))
                        conn.commit()
                        
                        st.success("✅ Mahasiswa berhasil ditambahkan!")
                        
                        cursor.close()
                        conn.close()
                    except MySQLError as e:
                        if "Duplicate entry" in str(e):
                            st.error(f"❌ NIM '{nim}' sudah terdaftar!")
                        else:
                            st.error(f"❌ Database Error: {e}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ NIM dan Nama harus diisi!")
        
        elif create_choice == "Mata Kuliah Baru":
            st.info("Formulir Tambah Mata Kuliah")
            
            kode_mk = st.text_input("Kode MK:")
            nama_mk = st.text_input("Nama Mata Kuliah:")
            sks = st.number_input("SKS:", min_value=1, max_value=6, value=3)
            
            if st.button("💾 Simpan Mata Kuliah"):
                if kode_mk and nama_mk:
                    try:
                        conn = get_db_connection()
                        if conn is None:
                            st.error("❌ Tidak dapat terhubung ke database")
                            st.stop()
                        
                        cursor = conn.cursor()
                        
                        query = """INSERT INTO mata_kuliah (kode_mk, nama_mk, sks)
                                  VALUES (%s, %s, %s)"""
                        
                        cursor.execute(query, (kode_mk, nama_mk, sks))
                        conn.commit()
                        
                        st.success("✅ Mata Kuliah berhasil ditambahkan!")
                        
                        cursor.close()
                        conn.close()
                    except MySQLError as e:
                        if "Duplicate entry" in str(e):
                            st.error(f"❌ Kode MK '{kode_mk}' sudah terdaftar!")
                        else:
                            st.error(f"❌ Database Error: {e}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Kode MK dan Nama harus diisi!")
        
        elif create_choice == "Nilai Baru":
            st.info("Formulir Tambah Nilai")
            
            # Get list mahasiswa
            df_mhs = execute_query("SELECT nim, nama FROM mahasiswa ORDER BY nama")
            if df_mhs is not None:
                nim = st.selectbox(
                    "Pilih Mahasiswa:",
                    df_mhs['nim'].tolist(),
                    format_func=lambda x: f"{x} - {df_mhs[df_mhs['nim']==x]['nama'].values[0]}"
                )
            
            # Get list mata kuliah
            df_mk = execute_query("SELECT kode_mk, nama_mk FROM mata_kuliah ORDER BY nama_mk")
            if df_mk is not None:
                kode_mk = st.selectbox(
                    "Pilih Mata Kuliah:",
                    df_mk['kode_mk'].tolist(),
                    format_func=lambda x: f"{x} - {df_mk[df_mk['kode_mk']==x]['nama_mk'].values[0]}"
                )
            
            semester_ambil = st.number_input("Semester Ambil:", min_value=1, max_value=14, value=1)
            nilai_uts = st.number_input("Nilai UTS:", min_value=0.0, max_value=100.0, value=0.0)
            nilai_uas = st.number_input("Nilai UAS:", min_value=0.0, max_value=100.0, value=0.0)
            nilai_tugas = st.number_input("Nilai Tugas:", min_value=0.0, max_value=100.0, value=0.0)
            
            if st.button("💾 Simpan Nilai"):
                try:
                    conn = get_db_connection()
                    if conn is None:
                        st.error("❌ Tidak dapat terhubung ke database")
                        st.stop()
                    
                    cursor = conn.cursor()
                    
                    query = """INSERT INTO nilai (nim, kode_mk, semester_ambil, nilai_uts, nilai_uas, nilai_tugas)
                              VALUES (%s, %s, %s, %s, %s, %s)"""
                    
                    cursor.execute(query, (nim, kode_mk, semester_ambil, nilai_uts, nilai_uas, nilai_tugas))
                    conn.commit()
                    
                    st.success("✅ Nilai berhasil ditambahkan!")
                    
                    cursor.close()
                    conn.close()
                except MySQLError as e:
                    if "Duplicate entry" in str(e):
                        st.error(f"❌ Nilai untuk mahasiswa ini di semester {semester_ambil} sudah ada!")
                    else:
                        st.error(f"❌ Database Error: {e}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    elif crud_type == "READ":
        st.subheader("📖 Lihat Data")
        
        read_table = st.selectbox("Pilih Tabel:", ["mahasiswa", "mata_kuliah", "nilai"])
        
        if read_table == "mahasiswa":
            df = execute_query("SELECT * FROM mahasiswa ORDER BY prodi, nama")
        elif read_table == "mata_kuliah":
            df = execute_query("SELECT * FROM mata_kuliah ORDER BY kode_mk")
        else:  # nilai
            df = execute_query("""
                SELECT n.*, m.nama as nama_mahasiswa, mk.nama_mk
                FROM nilai n
                JOIN mahasiswa m ON n.nim = m.nim
                JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
                ORDER BY m.nama, mk.nama_mk
            """)
        
        if df is not None:
            st.metric("Total Record", len(df))
            st.dataframe(df, width='stretch', hide_index=True)
    
    elif crud_type == "UPDATE":
        st.subheader("✏️ Update Data")
        
        st.info("Fitur update untuk nilai mahasiswa")
        
        # Get list nilai
        df_nilai_list = execute_query("""
            SELECT n.id_nilai, m.nama, mk.nama_mk, n.semester_ambil
            FROM nilai n
            JOIN mahasiswa m ON n.nim = m.nim
            JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
            ORDER BY m.nama
        """)
        
        if df_nilai_list is not None and len(df_nilai_list) > 0:
            id_nilai_selected = st.selectbox(
                "Pilih Nilai yang akan diupdate:",
                df_nilai_list['id_nilai'].tolist(),
                format_func=lambda x: f"ID: {x} - {df_nilai_list[df_nilai_list['id_nilai']==x].iloc[0][['nama', 'nama_mk']].values}"
            )
            
            # Get current values
            df_current = execute_query(f"""
                SELECT nilai_uts, nilai_uas, nilai_tugas
                FROM nilai
                WHERE id_nilai = {id_nilai_selected}
            """)
            
            if df_current is not None and len(df_current) > 0:
                current_uts = df_current['nilai_uts'].values[0]
                current_uas = df_current['nilai_uas'].values[0]
                current_tugas = df_current['nilai_tugas'].values[0]
                
                new_uts = st.number_input("Nilai UTS Baru:", min_value=0.0, max_value=100.0, value=float(current_uts) if current_uts else 0.0)
                new_uas = st.number_input("Nilai UAS Baru:", min_value=0.0, max_value=100.0, value=float(current_uas) if current_uas else 0.0)
                new_tugas = st.number_input("Nilai Tugas Baru:", min_value=0.0, max_value=100.0, value=float(current_tugas) if current_tugas else 0.0)
                
                if st.button("🔄 Update Nilai"):
                    try:
                        conn = get_db_connection()
                        if conn is None:
                            st.error("❌ Tidak dapat terhubung ke database")
                            st.stop()
                        
                        cursor = conn.cursor()
                        query = """UPDATE nilai 
                                  SET nilai_uts = %s, nilai_uas = %s, nilai_tugas = %s
                                  WHERE id_nilai = %s"""
                        
                        cursor.execute(query, (new_uts, new_uas, new_tugas, id_nilai_selected))
                        conn.commit()
                        
                        st.success("✅ Nilai berhasil diupdate!")
                        
                        cursor.close()
                        conn.close()
                    except MySQLError as e:
                        st.error(f"❌ Database Error: {e}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ Tidak ada data nilai")
    
    elif crud_type == "DELETE":
        st.subheader("🗑️ Hapus Data")
        
        st.danger("⚠️ Operasi DELETE akan menghapus data secara permanen!")
        
        delete_choice = st.radio("Pilih tipe penghapusan:", ["Hapus Mahasiswa", "Hapus Nilai"])
        
        if delete_choice == "Hapus Mahasiswa":
            df_mhs = execute_query("SELECT nim, nama FROM mahasiswa ORDER BY nama")
            if df_mhs is not None:
                nim = st.selectbox(
                    "Pilih Mahasiswa yang akan dihapus:",
                    df_mhs['nim'].tolist(),
                    format_func=lambda x: f"{x} - {df_mhs[df_mhs['nim']==x]['nama'].values[0]}"
                )
                
                confirm = st.checkbox("Saya yakin ingin menghapus data ini")
                
                if st.button("🗑️ Hapus Mahasiswa"):
                    if confirm:
                        try:
                            conn = get_db_connection()
                            if conn is None:
                                st.error("❌ Tidak dapat terhubung ke database")
                                st.stop()
                            
                            cursor = conn.cursor()
                            
                            cursor.execute("DELETE FROM mahasiswa WHERE nim = %s", (nim,))
                            conn.commit()
                            
                            st.success("✅ Mahasiswa berhasil dihapus! (Data nilai juga terhapus karena CASCADE)")
                            
                            cursor.close()
                            conn.close()
                        except MySQLError as e:
                            st.error(f"❌ Database Error: {e}")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Centang konfirmasi terlebih dahulu!")
        
        elif delete_choice == "Hapus Nilai":
            df_nilai = execute_query("""
                SELECT n.id_nilai, m.nama, mk.nama_mk, n.semester_ambil
                FROM nilai n
                JOIN mahasiswa m ON n.nim = m.nim
                JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
                ORDER BY m.nama
            """)
            
            if df_nilai is not None:
                id_nilai = st.selectbox(
                    "Pilih Nilai yang akan dihapus:",
                    df_nilai['id_nilai'].tolist(),
                    format_func=lambda x: f"ID: {x} - {df_nilai[df_nilai['id_nilai']==x].iloc[0][['nama', 'nama_mk']].values}"
                )
                
                confirm = st.checkbox("Saya yakin ingin menghapus nilai ini")
                
                if st.button("🗑️ Hapus Nilai"):
                    if confirm:
                        try:
                            conn = get_db_connection()
                            if conn is None:
                                st.error("❌ Tidak dapat terhubung ke database")
                                st.stop()
                            
                            cursor = conn.cursor()
                            
                            cursor.execute("DELETE FROM nilai WHERE id_nilai = %s", (id_nilai,))
                            conn.commit()
                            
                            st.success("✅ Nilai berhasil dihapus!")
                            
                            cursor.close()
                            conn.close()
                        except MySQLError as e:
                            st.error(f"❌ Database Error: {e}")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Centang konfirmasi terlebih dahulu!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d; font-size: 12px;'>
    <p>Dashboard Sistem Nilai Mahasiswa © 2026 | Database: db_akademik | DBMS: MySQL/MariaDB</p>
    </div>
    """,
    unsafe_allow_html=True
)

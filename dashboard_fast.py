import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error as MySQLError
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine
import warnings

warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Dashboard Akademik",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== DATABASE CONNECTION =====
@st.cache_resource
def get_db_connection():
    """Cache koneksi database"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='db_akademik',
            autocommit=True
        )
        return conn
    except MySQLError as err:
        st.error(f"❌ Error koneksi: {err}")
        return None

@st.cache_data(ttl=3600)
def get_mahasiswa_data():
    """Cache data mahasiswa selama 1 jam"""
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        df = pd.read_sql("SELECT * FROM mahasiswa ORDER BY prodi, nama", conn)
        conn.close()
        return df
    except:
        return None

@st.cache_data(ttl=3600)
def get_mata_kuliah_data():
    """Cache data mata kuliah"""
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        df = pd.read_sql("SELECT * FROM mata_kuliah ORDER BY kode_mk", conn)
        conn.close()
        return df
    except:
        return None

@st.cache_data(ttl=3600)
def get_nilai_data():
    """Cache data nilai dengan aggregates"""
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        query = """
            SELECT n.*, 
                   m.nama as nama_mahasiswa, m.prodi,
                   mk.nama_mk,
                   ROUND(0.3*COALESCE(n.nilai_uts,0) + 0.4*COALESCE(n.nilai_uas,0) + 0.3*COALESCE(n.nilai_tugas,0), 2) AS nilai_akhir
            FROM nilai n
            JOIN mahasiswa m ON n.nim = m.nim
            JOIN mata_kuliah mk ON n.kode_mk = mk.kode_mk
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except:
        return None

def get_huruf_mutu(score):
    """Convert skor ke huruf"""
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

# ===== SIDEBAR =====
st.sidebar.title("📊 Dashboard Akademik")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Menu:",
    ["📈 Dashboard", "👥 Mahasiswa", "📚 Mata Kuliah", "📊 Analisis", "⚡ CRUD"]
)

st.sidebar.divider()
st.sidebar.info("Database: db_akademik\nDBMS: MySQL 8")

# ===== LOAD DATA =====
df_nilai = get_nilai_data()
df_mhs = get_mahasiswa_data()
df_mk = get_mata_kuliah_data()

if df_nilai is None or len(df_nilai) == 0:
    st.error("❌ Data tidak ditemukan. Pastikan database sudah diisi.")
    st.stop()

# ===== PAGE: DASHBOARD =====
if menu == "📈 Dashboard":
    st.title("📊 Dashboard Sistem Nilai Mahasiswa")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Mahasiswa", len(df_mhs))
    
    with col2:
        st.metric("📚 Mata Kuliah", len(df_mk))
    
    with col3:
        st.metric("📊 Total Nilai", len(df_nilai))
    
    with col4:
        avg_nilai = df_nilai['nilai_akhir'].mean()
        st.metric("📈 Rata-rata", f"{avg_nilai:.2f}")
    
    st.divider()
    
    # Distribusi Huruf Mutu
    st.subheader("Distribusi Huruf Mutu")
    df_nilai['huruf'] = df_nilai['nilai_akhir'].apply(get_huruf_mutu)
    huruf_counts = df_nilai['huruf'].value_counts().sort_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(
            values=huruf_counts.values,
            names=huruf_counts.index,
            title='Distribusi Huruf Mutu',
            color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6']
        )
        st.plotly_chart(fig_pie, width='stretch')
    
    with col2:
        fig_bar = px.bar(
            x=huruf_counts.index,
            y=huruf_counts.values,
            title='Jumlah Mahasiswa per Huruf',
            labels={'x': 'Huruf Mutu', 'y': 'Jumlah'},
            color=huruf_counts.index,
            color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6']
        )
        st.plotly_chart(fig_bar, width='stretch')
    
    st.divider()
    
    # Top 5 Tertinggi
    st.subheader("🏆 5 Nilai Tertinggi")
    top5 = df_nilai.nlargest(5, 'nilai_akhir')[['nama_mahasiswa', 'nama_mk', 'nilai_uts', 'nilai_uas', 'nilai_tugas', 'nilai_akhir']]
    st.dataframe(top5, width='stretch', hide_index=True)
    
    # Top 5 Terendah
    st.subheader("📉 5 Nilai Terendah")
    bottom5 = df_nilai.nsmallest(5, 'nilai_akhir')[['nama_mahasiswa', 'nama_mk', 'nilai_uts', 'nilai_uas', 'nilai_tugas', 'nilai_akhir']]
    st.dataframe(bottom5, width='stretch', hide_index=True)

# ===== PAGE: MAHASISWA =====
elif menu == "👥 Mahasiswa":
    st.title("👥 Data Mahasiswa")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Cari NIM atau Nama:")
    with col2:
        st.write("")
    
    # Filter
    if search:
        filtered = df_mhs[
            (df_mhs['nim'].str.contains(search, case=False)) |
            (df_mhs['nama'].str.contains(search, case=False))
        ]
    else:
        filtered = df_mhs
    
    st.metric("Total Mahasiswa (Filtered)", len(filtered))
    st.dataframe(filtered[['nim', 'nama', 'angkatan', 'jenis_kelamin', 'prodi']], width='stretch', hide_index=True)
    
    # Download CSV
    csv = filtered.to_csv(index=False)
    st.download_button(
        "📥 Download CSV",
        csv,
        f"mahasiswa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv"
    )

# ===== PAGE: MATA KULIAH =====
elif menu == "📚 Mata Kuliah":
    st.title("📚 Data Mata Kuliah")
    
    st.metric("Total MK", len(df_mk))
    st.metric("Total SKS", int(df_mk['sks'].sum()))
    
    st.divider()
    
    # Statistik per MK
    st.subheader("Statistik Mata Kuliah")
    mk_stats = []
    for _, mk in df_mk.iterrows():
        nilai_mk = df_nilai[df_nilai['kode_mk'] == mk['kode_mk']]
        if len(nilai_mk) > 0:
            mk_stats.append({
                'kode_mk': mk['kode_mk'],
                'nama_mk': mk['nama_mk'],
                'sks': mk['sks'],
                'jml_pengambil': len(nilai_mk['nim'].unique()),
                'rata_nilai': nilai_mk['nilai_akhir'].mean()
            })
    
    df_stats = pd.DataFrame(mk_stats)
    st.dataframe(df_stats, width='stretch', hide_index=True)
    
    # Chart
    fig = px.bar(
        df_stats,
        x='nama_mk',
        y='rata_nilai',
        title='Rata-rata Nilai per Mata Kuliah',
        labels={'nama_mk': 'Mata Kuliah', 'rata_nilai': 'Rata-rata Nilai'},
        color='rata_nilai',
        color_continuous_scale='Viridis'
    )
    fig.update_xaxis(tickangle=-45)
    st.plotly_chart(fig, width='stretch')

# ===== PAGE: ANALISIS =====
elif menu == "📊 Analisis":
    st.title("📊 Analisis Nilai")
    
    analysis = st.selectbox(
        "Pilih Analisis:",
        ["Performa per Prodi", "Perbandingan Gender", "Semester Trends", "Retake Analysis"]
    )
    
    if analysis == "Performa per Prodi":
        st.subheader("Rata-rata Nilai per Program Studi")
        prodi_stats = df_nilai.groupby('prodi').agg({
            'nilai_akhir': ['count', 'mean'],
            'nilai_uts': 'mean',
            'nilai_uas': 'mean',
            'nilai_tugas': 'mean'
        }).round(2)
        
        prodi_stats.columns = ['Jumlah Nilai', 'Rata-rata Akhir', 'Rata UTS', 'Rata UAS', 'Rata Tugas']
        st.dataframe(prodi_stats, width='stretch')
        
        fig = px.bar(
            x=prodi_stats.index,
            y=prodi_stats['Rata-rata Akhir'],
            title='Performa per Prodi',
            labels={'x': 'Program Studi', 'y': 'Rata-rata Nilai'},
            color=prodi_stats['Rata-rata Akhir'],
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, width='stretch')
    
    elif analysis == "Perbandingan Gender":
        st.subheader("Perbandingan Performa Gender")
        gender_stats = df_nilai.groupby(lambda x: df_nilai.loc[x, 'nim'].map(
            lambda nim: 'Laki-laki' if df_mhs[df_mhs['nim']==nim]['jenis_kelamin'].values[0]=='L' else 'Perempuan'
        )).agg({
            'nilai_akhir': ['count', 'mean'],
            'nilai_uts': 'mean',
            'nilai_uas': 'mean',
            'nilai_tugas': 'mean'
        }).round(2)
        
        gender_stats.columns = ['Jumlah', 'Rata-rata Akhir', 'Rata UTS', 'Rata UAS', 'Rata Tugas']
        st.dataframe(gender_stats, width='stretch')
    
    elif analysis == "Semester Trends":
        st.subheader("Tren Nilai per Semester")
        sem_stats = df_nilai.groupby('semester_ambil').agg({
            'nilai_akhir': ['count', 'mean']
        }).round(2)
        
        sem_stats.columns = ['Jumlah Nilai', 'Rata-rata']
        
        fig = px.line(
            x=sem_stats.index,
            y=sem_stats['Rata-rata'],
            title='Tren Rata-rata Nilai per Semester',
            labels={'x': 'Semester', 'y': 'Rata-rata Nilai'},
            markers=True
        )
        st.plotly_chart(fig, width='stretch')
    
    elif analysis == "Retake Analysis":
        st.subheader("Analisis Retake")
        retake = df_nilai.groupby(['nim', 'kode_mk']).size()
        retake = retake[retake > 1]
        
        if len(retake) > 0:
            st.warning(f"⚠️ Ditemukan {len(retake)} record retake")
            retake_df = retake.reset_index(name='jumlah_retake')
            st.dataframe(retake_df, width='stretch', hide_index=True)
        else:
            st.success("✅ Tidak ada mahasiswa yang retake")

# ===== PAGE: CRUD =====
elif menu == "⚡ CRUD":
    st.title("⚡ Operasi CRUD")
    
    crud_op = st.selectbox("Pilih Operasi:", ["CREATE", "READ", "UPDATE", "DELETE"])
    
    if crud_op == "CREATE":
        st.subheader("➕ Tambah Data")
        
        create_type = st.radio("Tipe Data:", ["Mahasiswa", "Mata Kuliah", "Nilai"])
        
        if create_type == "Mahasiswa":
            nim = st.text_input("NIM:")
            nama = st.text_input("Nama:")
            angkatan = st.number_input("Angkatan:", 2000, 2050, 2024)
            gender = st.radio("Jenis Kelamin:", ["L", "P"])
            prodi = st.selectbox("Prodi:", ["Statistika", "Matematika", "Informatika"])
            
            if st.button("Simpan"):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO mahasiswa (nim, nama, angkatan, jenis_kelamin, prodi) VALUES (%s, %s, %s, %s, %s)",
                        (nim, nama, angkatan, gender, prodi)
                    )
                    conn.commit()
                    st.success("✅ Mahasiswa berhasil ditambah!")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        elif create_type == "Mata Kuliah":
            kode = st.text_input("Kode MK:")
            nama = st.text_input("Nama MK:")
            sks = st.number_input("SKS:", 1, 6, 3)
            
            if st.button("Simpan"):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO mata_kuliah (kode_mk, nama_mk, sks) VALUES (%s, %s, %s)",
                        (kode, nama, sks)
                    )
                    conn.commit()
                    st.success("✅ Mata Kuliah berhasil ditambah!")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        elif create_type == "Nilai":
            nim = st.selectbox("NIM Mahasiswa:", df_mhs['nim'].tolist())
            kode = st.selectbox("Kode MK:", df_mk['kode_mk'].tolist())
            sem = st.number_input("Semester:", 1, 14, 1)
            uts = st.number_input("Nilai UTS:", 0.0, 100.0)
            uas = st.number_input("Nilai UAS:", 0.0, 100.0)
            tugas = st.number_input("Nilai Tugas:", 0.0, 100.0)
            
            if st.button("Simpan"):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO nilai (nim, kode_mk, semester_ambil, nilai_uts, nilai_uas, nilai_tugas) VALUES (%s, %s, %s, %s, %s, %s)",
                        (nim, kode, sem, uts, uas, tugas)
                    )
                    conn.commit()
                    st.success("✅ Nilai berhasil ditambah!")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    elif crud_op == "READ":
        table = st.selectbox("Tabel:", ["mahasiswa", "mata_kuliah", "nilai"])
        
        if table == "mahasiswa":
            st.dataframe(df_mhs, width='stretch', hide_index=True)
        elif table == "mata_kuliah":
            st.dataframe(df_mk, width='stretch', hide_index=True)
        else:
            st.dataframe(df_nilai[['nim', 'nama_mahasiswa', 'kode_mk', 'nama_mk', 'semester_ambil', 'nilai_uts', 'nilai_uas', 'nilai_tugas', 'nilai_akhir']], 
                        width='stretch', hide_index=True)
    
    elif crud_op == "UPDATE":
        st.info("Update Nilai")
        id_nilai = st.number_input("ID Nilai:", 1)
        new_uts = st.number_input("UTS Baru:", 0.0, 100.0)
        new_uas = st.number_input("UAS Baru:", 0.0, 100.0)
        new_tugas = st.number_input("Tugas Baru:", 0.0, 100.0)
        
        if st.button("Update"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE nilai SET nilai_uts=%s, nilai_uas=%s, nilai_tugas=%s WHERE id_nilai=%s",
                    (new_uts, new_uas, new_tugas, id_nilai)
                )
                conn.commit()
                st.success("✅ Nilai berhasil diupdate!")
                cursor.close()
                conn.close()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    elif crud_op == "DELETE":
        st.danger("⚠️ Hati-hati dengan operasi DELETE!")
        
        del_type = st.radio("Hapus:", ["Mahasiswa", "Nilai"])
        
        if del_type == "Mahasiswa":
            nim = st.selectbox("Pilih Mahasiswa:", df_mhs['nim'].tolist())
            confirm = st.checkbox("Saya yakin")
            
            if st.button("Hapus") and confirm:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM mahasiswa WHERE nim=%s", (nim,))
                    conn.commit()
                    st.success("✅ Mahasiswa berhasil dihapus!")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            id_nilai = st.number_input("ID Nilai:", 1)
            confirm = st.checkbox("Saya yakin")
            
            if st.button("Hapus") and confirm:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM nilai WHERE id_nilai=%s", (id_nilai,))
                    conn.commit()
                    st.success("✅ Nilai berhasil dihapus!")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: #7f8c8d; font-size: 12px;'>"
    "<p>Dashboard Sistem Nilai Mahasiswa © 2026 | Database: db_akademik</p>"
    "</div>",
    unsafe_allow_html=True
)

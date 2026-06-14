# 📊 Dashboard Sistem Nilai Mahasiswa (Opsi B)

Sistem informasi akademik untuk mengelola dan menganalisis nilai mahasiswa dengan database MySQL/MariaDB.

## 📋 File yang Tersedia

1. **db_akademik.sql** - Script SQL lengkap untuk database
   - Pembuatan database dan tabel
   - Insert data dummy
   - Query CRUD dan analisis

2. **dashboard.py** - Dashboard interaktif menggunakan Streamlit
   - Visualisasi data real-time
   - Fitur CRUD operations
   - Analisis mendalam

3. **requirements.txt** - Package Python yang diperlukan

---

## 🚀 Panduan Setup

### Step 1: Setup Database MySQL

#### Pilihan A: Menggunakan MySQL Command Line
```bash
# Masuk ke MySQL
mysql -u root -p

# Copy-paste seluruh isi db_akademik.sql atau jalankan:
source C:\Users\aliff\Downloads\Tugas Besar Basis Data B\db_akademik.sql
```

#### Pilihan B: Menggunakan MySQL Workbench
1. Buka MySQL Workbench
2. Klik File → Open SQL Script
3. Pilih file `db_akademik.sql`
4. Klik Execute (atau Ctrl+Shift+Enter)
5. Tunggu hingga selesai

#### Pilihan C: Menggunakan PHP MyAdmin (jika tersedia)
1. Buka http://localhost/phpmyadmin
2. Klik Import
3. Pilih file `db_akademik.sql`
4. Klik Go

---

### Step 2: Install Python Dependencies

Pastikan Python 3.8+ sudah terinstall. Kemudian jalankan:

```bash
# Buka Command Prompt/PowerShell
cd C:\Users\aliff\Downloads\Tugas Besar Basis Data B

# Install package
pip install -r requirements.txt
```

Atau install manual:
```bash
pip install streamlit pandas mysql-connector-python plotly matplotlib numpy
```

---

### Step 3: Konfigurasi Koneksi Database

Edit file `dashboard.py` dan sesuaikan konfigurasi database (jika berbeda):

```python
@st.cache_resource
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',        # IP/hostname MySQL server
        user='root',             # Username MySQL (sesuaikan jika berbeda)
        password='',             # Password MySQL (kosong jika tidak ada)
        database='db_akademik'   # Nama database
    )
    return conn
```

---

### Step 4: Jalankan Dashboard

```bash
cd C:\Users\aliff\Downloads\Tugas Besar Basis Data B

streamlit run dashboard.py
```

Atau:
```bash
python -m streamlit run dashboard.py
```

Dashboard akan terbuka di browser: http://localhost:8501

---

## 📊 Fitur Dashboard

### 1. 📈 Dashboard Utama
- KPI Cards (Total Mahasiswa, MK, Nilai, Rata-rata)
- Distribusi Huruf Mutu (Pie Chart & Bar Chart)
- Performa per Program Studi

### 2. 👥 Data Mahasiswa
- List semua mahasiswa dengan filter
- Filter berdasarkan Prodi, Angkatan, Gender
- Statistik distribusi gender
- Download CSV

### 3. 📚 Data Mata Kuliah
- List semua mata kuliah
- Statistik per mata kuliah (rata-rata nilai, jumlah mahasiswa)
- Visualisasi performa mata kuliah

### 4. 📊 Analisis Nilai
- **5 Nilai Tertinggi** - Peringkat top performers
- **5 Nilai Terendah** - Identifikasi mahasiswa yang butuh bantuan
- **Perbandingan Gender** - Analisis perbedaan performa laki-laki vs perempuan
- **Retake Analysis** - Identifikasi mahasiswa yang mengulang mata kuliah
- **Semester Performance** - Tren nilai per semester pengambilan
- **Mahasiswa Terbaik per Prodi** - Peringkat 1 setiap prodi

### 5. 🔍 Pencarian & Filter
- **Cari Mahasiswa** - Cari berdasarkan NIM/nama dengan detail nilai
- **Cari Mata Kuliah** - Cari MK dengan statistik
- **Cari Nilai Mahasiswa** - Detail lengkap nilai per mahasiswa

### 6. 📋 Laporan Lengkap
- **Ringkasan per Mahasiswa** - Summary akademik setiap mahasiswa
- **Ringkasan per Mata Kuliah** - Summary performa MK
- **Data Tidak Lengkap** - Identifikasi nilai NULL
- **Mata Kuliah Tersulit** - 5 MK dengan rata-rata terendah

### 7. ⚡ CRUD Operations
- **CREATE** - Tambah Mahasiswa, MK, atau Nilai
- **READ** - Lihat semua data dari tabel
- **UPDATE** - Ubah data dengan query SQL
- **DELETE** - Hapus data (dengan konfirmasi)

---

## 🔢 Skema Database

### Tabel: mahasiswa
```
nim (PK)        - VARCHAR(20)
nama            - VARCHAR(100)
angkatan        - YEAR
jenis_kelamin   - ENUM('L','P')
prodi           - VARCHAR(50)
created_at      - DATETIME
```

### Tabel: mata_kuliah
```
kode_mk (PK)    - VARCHAR(15)
nama_mk         - VARCHAR(100)
sks             - TINYINT (1-6)
created_at      - DATETIME
```

### Tabel: nilai (Bridge Table)
```
id_nilai (PK)       - INT AUTO_INCREMENT
nim (FK)            - VARCHAR(20)
kode_mk (FK)        - VARCHAR(15)
semester_ambil      - TINYINT (1-14)
nilai_uts           - DECIMAL(5,2) [0-100]
nilai_uas           - DECIMAL(5,2) [0-100]
nilai_tugas         - DECIMAL(5,2) [0-100]
created_at          - DATETIME
```

**Unique Key:** (nim, kode_mk, semester_ambil) - Memungkinkan retake

---

## 📐 Rumus Nilai Akhir

```
Nilai Akhir = (0.3 × UTS) + (0.4 × UAS) + (0.3 × Tugas)
```

**Konversi ke Huruf Mutu:**
- A: Nilai ≥ 80
- B: Nilai ≥ 70
- C: Nilai ≥ 60
- D: Nilai ≥ 50
- E: Nilai < 50

---

## 💾 Data Dummy

Database sudah berisi data sampel:
- **15 Mahasiswa** dari 3 prodi (Statistika, Matematika, Informatika)
- **10 Mata Kuliah** dengan berbagai SKS
- **48 Record Nilai** dengan distribusi semester 1-5

---

## ⚠️ Troubleshooting

### Error: "Connection refused" atau "Can't connect to MySQL server"
**Solusi:**
1. Pastikan MySQL server sudah berjalan
2. Periksa username dan password di `dashboard.py`
3. Pastikan database `db_akademik` sudah dibuat

### Error: "No module named 'streamlit'"
**Solusi:**
```bash
pip install -r requirements.txt
```

### Error: "Unknown database 'db_akademik'"
**Solusi:**
1. Jalankan ulang script `db_akademik.sql`
2. Pastikan query berhasil (cek di MySQL Workbench)

### Dashboard tidak buka di browser
**Solusi:**
1. Tunggu 5-10 detik saat first run
2. Manual buka: http://localhost:8501
3. Check terminal untuk error messages

---

## 📝 Query Utama di Database

Database sudah dilengkapi dengan 12 query analysis:

1. **Q1** - Track record akademik per mahasiswa
2. **Q2** - Mahasiswa dengan nilai tertinggi per MK
3. **Q3** - Statistik lengkap per mata kuliah
4. **Q4** - Deteksi retake
5. **Q5** - Nilai terendah per angkatan
6. **Q6** - Perbandingan performa gender
7. **Q7** - Identifikasi data incomplete (NULL)
8. **Q8** - Semester terbaik/terburuk
9. **Q9** - Mahasiswa di atas rata-rata prodi
10. **Q10** - Total SKS per mahasiswa
11. **Q11** - 5 Mata kuliah tersulit
12. **Q12** - Summary lengkap per mahasiswa

---

## 🎯 Use Cases

### 1. Monitoring Performa Akademik
- Lihat trending nilai per semester
- Identifikasi mahasiswa dengan performa menurun

### 2. Analisis Program Studi
- Bandingkan performa antar prodi
- Deteksi mata kuliah yang sulit di setiap prodi

### 3. Pelaporan dan Evaluasi
- Generate laporan untuk presentasi
- Download data untuk analisis lebih lanjut

### 4. Identifikasi Mahasiswa Potensial
- Cari top performers untuk penghargaan
- Identifikasi mahasiswa yang butuh bantuan akademik

### 5. Riset dan Pengembangan Kurikulum
- Analisis efektivitas mata kuliah
- Evaluasi kesuksesan program studi

---

## 📞 Support

Untuk bantuan lebih lanjut, hubungi tim IT atau Academic Affairs.

---

**Versi:** 1.0  
**Tahun:** 2026  
**DBMS:** MySQL 8 / MariaDB  
**Framework:** Streamlit  
**Python:** 3.8+

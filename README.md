# Pemograman-Jaringan
Tugas Bikin WEB
Menggunakan web socket dan API

## Cara Menjalankan

Cara tercepat — jalankan satu perintah:

```bash
./run.sh
```

`run.sh` akan:
1. Cek apakah dependency sudah terinstall
2. Install ke user site jika belum (menggunakan `requirements.txt`)
3. Jalankan server di `http://0.0.0.0:5000`

Buka browser:
- Local: `http://localhost:5000`
- Dev Container / Codespaces: forward port `5000` di VS Code, lalu akses URL yang diberikan

## Alternatif: Jalankan Manual

Jika lebih suka menjalankan manual tanpa skrip:

```bash
# Install dependency ke user site
pip install --user -r requirements.txt

# Jalankan server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Atau gunakan virtualenv (opsional):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Fitur

- **Real-time Weather**: Menampilkan cuaca Pontianak via WebSocket (`/ws`) dengan update setiap 10 detik
- **Interactive Map**: Klik peta untuk melihat cuaca di lokasi lain (request ke `/weather?lat=...&lon=...`)
- **API Call Logging**: Dashboard menampilkan log semua API calls dengan timestamp dan counter
- **Frontend**: `templates/index.html` dengan Leaflet.js + OpenWeather API

## API Endpoints

- `GET /` — Halaman utama dengan peta dan log dashboard
- `WebSocket /ws` — Streaming data cuaca real-time Pontianak (interval 10s)
- `GET /weather?lat=X&lon=Y` — Ambil data cuaca berdasarkan koordinat (logged)
- `GET /api/logs` — Ambil semua log API calls dengan timestamp

## Proses Menjalankan Step-by-Step

### Step 1: Siapkan Environment

Pastikan Python 3.8+ terinstall:
```bash
python3 --version
```

### Step 2: Jalankan Server

Opsi A (paling simpel — recommended):
```bash
./run.sh
```

Opsi B (manual):
```bash
pip install --user -r requirements.txt
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Opsi C (dengan virtualenv):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### Step 3: Buka Browser

- **Local**: `http://localhost:5000`
- **Dev Container/Codespaces**: Forward port 5000 di VS Code, akses URL yang diberikan

### Step 4: Gunakan Aplikasi

1. **Dashboard utama** menampilkan:
   - Kota & suhu terkini (Pontianak default via WebSocket)
   - Status koneksi WebSocket
   - Feels like, humidity, updated time

2. **Peta interaktif**:
   - Scroll/zoom untuk melihat seluruh dunia
   - Klik lokasi manapun untuk lihat cuaca di sana
   - Marker merah menandai lokasi klik terakhir

3. **Log Dashboard** (di bawah peta):
   - Menampilkan setiap API call dengan timestamp `[HH:MM:SS]`
   - Total counter menghitung semua calls
   - Auto-refresh setiap 5 detik

### Contoh Alur:

```
1. Server start → menampilkan "Application startup complete"
2. Buka browser → melihat suhu Pontianak via WebSocket
3. Klik peta (mis: Jakarta) → API call tercatat di log
4. Log dashboard update → menampilkan "[14:23:45] /weather?lat=-6.17&lon=106.83"
5. Total calls counter naik → "Total Calls: 1"
```

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| WebSocket error 404 | Pastikan port forwarding aktif dan akses dari `localhost:5000` (bukan port lain) |
| Port 5000 sudah terpakai | Ubah port di `run.sh` baris terakhir atau gunakan port berbeda: `python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000` |
| Module not found error | Install dependencies: `pip install --user -r requirements.txt` |
| Log tidak muncul | Refresh browser (F5) atau klik peta lagi untuk trigger API call |
| Suhu tidak update | WebSocket mungkin disconnect — lihat console browser (F12) untuk error detail |

## Struktur Project

```
.
├── main.py              → Backend FastAPI (WebSocket, API endpoints, logging)
├── templates/
│   └── index.html       → Frontend (peta, dashboard, log display)
├── requirements.txt     → Python dependencies
├── run.sh               → Script jalankan otomatis
└── README.md            → File ini
```

---

Repo sudah dibersihkan: hanya file penting (`main.py`, `templates/`, `requirements.txt`, `run.sh`)

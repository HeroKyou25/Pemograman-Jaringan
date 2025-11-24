# Setup untuk Deployment ke Vercel

## Langkah-Langkah Deployment

### 1. Buat `.env` file untuk lokal development (jangan di-commit)
```bash
cp .env.example .env
```

Edit `.env` dan masukkan API key Anda:
```
OPENWEATHER_API_KEY=your_actual_api_key
```

File `.env` sudah di-ignore via `.gitignore`, jadi aman tidak akan ter-upload.

### 2. Set Environment Variables di Vercel Dashboard
1. Masuk ke [Vercel Dashboard](https://vercel.com/dashboard)
2. Pilih project `Pemograman-Jaringan`
3. Buka **Settings** → **Environment Variables**
4. Tambahkan variabel:
   - **Name:** `OPENWEATHER_API_KEY`
   - **Value:** `your_actual_api_key` (ganti dengan API key asli)
   - **Environment:** Production, Preview, Development

Atau gunakan CLI:
```bash
vercel env add OPENWEATHER_API_KEY production
vercel env add OPENWEATHER_API_KEY preview
vercel env add OPENWEATHER_API_KEY development
```

### 3. Jika menggunakan Database (PostgreSQL di Vercel)
Tambahkan environment variable:
- **Name:** `DATABASE_URL`
- **Value:** `postgresql://user:password@host/dbname`

Jika tidak diset, aplikasi akan default menggunakan SQLite lokal.

### 4. Deploy ke Vercel
```bash
vercel deploy
```

Atau jika branch sudah terhubung ke Vercel, cukup push ke GitHub:
```bash
git add .
git commit -m "Fix Vercel deployment"
git push origin main
```

## Mengapa `.env` tidak disertakan?

- **Keamanan:** File `.env` berisi secret (API key). Jika di-commit ke repo publik, siapa pun bisa lihat dan menyalahgunakan.
- **Best Practice:** Environment variables disimpan di Vercel Dashboard (enkripsi), bukan di repo.
- **Development:** File `.env` hanya untuk lokal development; Vercel menggunakan variables dari Dashboard.

## Troubleshooting

### Error: "Read-only file system: 'static'"
✅ **FIXED** - Aplikasi sekarang skip `os.makedirs("static")` saat di Vercel.

### Error: "OPENWEATHER_API_KEY not found"
Pastikan Anda sudah set environment variable di Vercel Dashboard:
- Settings → Environment Variables → tambahkan `OPENWEATHER_API_KEY`
- Deploy ulang setelah menambahkan

### WebSocket timeout / tidak terhubung
WebSocket di Vercel Serverless Functions terbatas. Untuk production yang robust, pertimbangkan:
- Menggunakan managed service (seperti Vercel Edge Functions untuk WebSocket)
- Atau hosting alternatif seperti Railway, Fly.io yang lebih cocok untuk long-running connections

## File Penting

| File | Deskripsi |
|------|-----------|
| `.env.example` | Template environment variables (commit ke repo) |
| `.env` | Actual environment variables (tidak di-commit, hanya lokal) |
| `vercel.json` | Konfigurasi Vercel deployment |
| `api/index.py` | Entry point untuk Vercel Serverless Functions |
| `requirements.txt` | Python dependencies (Vercel auto-install) |

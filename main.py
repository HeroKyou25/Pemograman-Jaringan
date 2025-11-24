from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import asyncio
from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables dari .env file (hanya untuk development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI()

# pastikan folder static ada supaya tidak crash saat mounting (skip di Vercel karena read-only FS)
if os.environ.get("VERCEL") != "1":
    os.makedirs("static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

# folder templates
templates = Jinja2Templates(directory="templates")

# ==== DATABASE SETUP ====
# Gunakan DATABASE_URL dari environment, atau default ke SQLite lokal
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./weather.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WeatherLog(Base):
    """Model untuk menyimpan data cuaca"""
    __tablename__ = "weather_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    temp = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Integer)
    description = Column(String)
    logged_at = Column(DateTime, default=datetime.utcnow)

# Buat tabel jika belum ada
Base.metadata.create_all(bind=engine)

# ==== KONFIGURASI CUACA ====
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "ca21257afebb7702df3c0497ccffa219")  # API key
CITY = "Pontianak"    # kota default untuk mode WebSocket
COUNTRY_CODE = "ID"   # kode negara
UPDATE_INTERVAL = 10  # detik (interval update WebSocket)
# =============================

# ==== API CALL TRACKING ====
api_call_count = 0
api_call_logs = []

def log_api_call(endpoint: str, method: str = "GET", status: str = "success"):
    """Log API call dengan timestamp"""
    global api_call_count, api_call_logs
    api_call_count += 1
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "id": api_call_count,
        "timestamp": timestamp,
        "endpoint": endpoint,
        "method": method,
        "status": status
    }
    api_call_logs.append(log_entry)
    # simpan hanya 50 log terakhir
    if len(api_call_logs) > 50:
        api_call_logs.pop(0)
    print(f"[{timestamp}] API Call #{api_call_count}: {method} {endpoint} - {status}")
    return log_entry

def save_weather_to_db(city: str, temp: float, feels_like: float, humidity: int, description: str):
    """Simpan data cuaca ke database"""
    try:
        db = SessionLocal()
        weather_log = WeatherLog(
            city=city,
            temp=temp,
            feels_like=feels_like,
            humidity=humidity,
            description=description
        )
        db.add(weather_log)
        db.commit()
        db.refresh(weather_log)
        db.close()
        return weather_log
    except Exception as e:
        print(f"Error saving to DB: {e}")
        return None

# =============================


def format_weather(data: dict) -> dict:
    """Format JSON dari OpenWeather ke bentuk sederhana untuk frontend."""
    try:
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        city = data.get("name")
        
        # Save ke database
        save_weather_to_db(city, temp, feels_like, humidity, description)
        
        return {
            "city": city,
            "temp": temp,
            "feels_like": feels_like,
            "description": description,
            "humidity": humidity,
            "updated_at": datetime.now().strftime("%H:%M:%S"),
        }
    except Exception as e:
        print("Error format_weather:", e)
        return {
            "city": data.get("name") if data else CITY,
            "temp": None,
            "feels_like": None,
            "description": "Tidak bisa ambil data",
            "humidity": None,
            "updated_at": datetime.now().strftime("%H:%M:%S"),
        }


def get_weather_default() -> dict:
    """Cuaca default berbasis nama kota (untuk WebSocket)."""
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={CITY},{COUNTRY_CODE}&appid={WEATHER_API_KEY}&units=metric&lang=id"
    )
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        print("DATA CUACA (DEFAULT):", data)
        return format_weather(data)
    except Exception as e:
        print("Error get_weather_default:", e)
        return format_weather({})


def get_weather_by_coords(lat: float, lon: float) -> dict:
    """Cuaca berdasarkan koordinat lat/lon (untuk klik peta)."""
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=id"
    )
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        print("DATA CUACA (KOORDINAT):", data)
        return format_weather(data)
    except Exception as e:
        print("Error get_weather_by_coords:", e)
        return format_weather({})
    

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Halaman utama: render templates/index.html."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    """WebSocket: kirim data cuaca default berkala ke client."""
    await websocket.accept()
    try:
        while True:
            weather = get_weather_default()
            await websocket.send_json(weather)
            await asyncio.sleep(UPDATE_INTERVAL)
    except Exception as e:
        print("WebSocket closed:", e)
        await websocket.close()


@app.get("/weather", response_class=JSONResponse)
async def weather_endpoint(lat: float, lon: float):
    """
    Endpoint HTTP biasa:
    /weather?lat=...&lon=...
    Dipanggil saat user klik peta.
    """
    log_api_call(f"/weather?lat={lat:.2f}&lon={lon:.2f}", "GET")
    weather = get_weather_by_coords(lat, lon)
    return JSONResponse(content=weather)


@app.get("/api/logs", response_class=JSONResponse)
async def get_logs():
    """Endpoint untuk ambil semua log API calls"""
    return JSONResponse(content={
        "total_calls": api_call_count,
        "logs": api_call_logs
    })


@app.get("/api/weather-history", response_class=JSONResponse)
async def get_weather_history(limit: int = 100):
    """
    Endpoint untuk ambil riwayat data cuaca dari database.
    Query params: limit (jumlah data terbaru, default 100)
    """
    try:
        db = SessionLocal()
        # Query data terbaru dengan limit
        weather_history = db.query(WeatherLog).order_by(WeatherLog.logged_at.desc()).limit(limit).all()
        db.close()
        
        # Format ke JSON
        result = []
        for log in weather_history:
            result.append({
                "id": log.id,
                "city": log.city,
                "temp": log.temp,
                "feels_like": log.feels_like,
                "humidity": log.humidity,
                "description": log.description,
                "logged_at": log.logged_at.strftime("%Y-%m-%d %H:%M:%S") if log.logged_at else None
            })
        
        return JSONResponse(content={
            "total": len(result),
            "data": result
        })
    except Exception as e:
        print(f"Error fetching weather history: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)



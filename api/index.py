import sys
import os

# Tambahkan parent directory ke path agar bisa import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export untuk Vercel Serverless Functions
export = app

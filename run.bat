@echo off
cd /d "%~dp0"

:: (Opsiyonel) virtual‑env aktivasyonu
call venv\Scripts\activate

:: Streamlit'i 8501 portunda başlat (headless false)
start "" streamlit run financial_dashboard.py --server.headless false

:: 3 saniye bekle, ardından Chrome'da adresi aç
timeout /t 3 >nul
start "" "chrome" "http://localhost:8501"

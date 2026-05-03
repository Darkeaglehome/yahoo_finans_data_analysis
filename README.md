# 📈 Financial Analysis Terminal (Streamlit)

A high-performance, professional trading terminal interface built with Streamlit and Plotly for market analysis. Supports both English and Turkish.

[English](#english) | [Türkçe](#türkçe)

---

## English

### 🚀 Features
- **Real-time Data:** Fetches live and historical market data using Yahoo Finance API.
- **Advanced Charting:**
    - Multiple chart modes: Candlestick, Line, B/W Bars (Hollow), and Heikin-Ashi.
    - Interactive tools: Zoom, Pan, and unified hover tooltips.
    - Technical Indicators: SMA (20, 50, 200) and RSI (14) with custom thresholds.
- **Comprehensive Metrics:**
    - **Performance:** Total Return, Annualized Return, Avg Daily Return.
    - **Risk Analysis:** Annual Volatility, Max Drawdown, Value at Risk (VaR 95%).
    - **Ratios:** Sharpe, Sortino, and Calmar ratios.
- **Smart Trend Detection:** Automatic Bull/Bear/Sideways market labeling based on SMA200.
- **Export Capabilities:** One-click Excel download for all processed data and indicators.
- **User Experience:** Clean, professional "Soft-Blue" theme with a compact sidebar.

### 🛠 Tech Stack
- **Frontend:** [Streamlit](https://streamlit.io/)
- **Visualizations:** [Plotly](https://plotly.com/python/)
- **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **API:** [yfinance](https://github.com/ranaroussi/yfinance)

### 📥 Installation
1. Install the required dependencies:
   ```bash
   pip install streamlit yfinance plotly pandas numpy scipy openpyxl
   ```

### 🏃 Usage
Run the application using Streamlit:
```bash
streamlit run financial_dashboard.py
```

---

## Türkçe

### 🚀 Özellikler
- **Gerçek Zamanlı Veri:** Yahoo Finance API kullanarak canlı ve geçmiş piyasa verilerini çeker.
- **Gelişmiş Grafikleme:**
    - Çoklu grafik modları: Mum (Candlestick), Çizgi, Siyah-Beyaz Çubuklar ve Heikin-Ashi.
    - Etkileşimli araçlar: Yakınlaştırma, kaydırma ve birleşik ipucu kutuları.
    - Teknik Göstergeler: Özel eşiklere sahip SMA (20, 50, 200) ve RSI (14).
- **Kapsamlı Metrikler:**
    - **Performans:** Toplam Getiri, Yıllıklandırılmış Getiri, Ortalama Günlük Getiri.
    - **Risk Analizi:** Yıllık Volatilite, Maksimum Kayıp (Max Drawdown), Riske Maruz Değer (VaR %95).
    - **Oranlar:** Sharpe, Sortino ve Calmar oranları.
- **Akıllı Trend Tespiti:** SMA200'e dayalı otomatik Boğa/Ayı/Yatay piyasa etiketleme.
- **Dışa Aktarma:** İşlenmiş tüm veriler ve göstergeler için tek tıkla Excel indirme.
- **Kullanıcı Deneyimi:** Kompakt kenar çubuğu ile temiz, profesyonel "Soft-Blue" teması.

### 🛠 Teknoloji Yığını
- **Arayüz:** [Streamlit](https://streamlit.io/)
- **Görselleştirme:** [Plotly](https://plotly.com/python/)
- **Veri İşleme:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **API:** [yfinance](https://github.com/ranaroussi/yfinance)

### 📥 Kurulum
1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install streamlit yfinance plotly pandas numpy scipy openpyxl
   ```

### 🏃 Kullanım
Uygulamayı Streamlit ile çalıştırın:
```bash
streamlit run financial_dashboard.py
```

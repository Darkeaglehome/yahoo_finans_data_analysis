import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Financial Analysis Terminal", layout="wide")

# ─── Kompakt CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Üst boşluğu azalt */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; }
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    /* Küçük başlık */
    .small-title { font-size: 1rem; font-weight: 600; color: #0a3d62; margin: 0 0 0.3rem 0; }
    /* Metrik kartları */
    .metric-card { background: #e8f0fe; border-radius: 8px; padding: 2px 4px; text-align: center; margin-bottom: 4px; }
    .metric-card .label { font-size: 0.65rem; color: #555; margin: 0; }
    .metric-card .value { font-size: 0.95rem; font-weight: 700; color: #0a3d62; margin: 0; }
    .metric-card .value.green { color: #16a34a; }
    .metric-card .value.red { color: #dc2626; }
    .metric-card .value.purple { color: #8b5cf6; }
    /* Açılış/kapanış satırı */
    .info-row { font-size: 0.85rem; color: #333; margin-bottom: 6px; }
    .info-row span { font-weight: 600; }
    /* Sidebar */
    section[data-testid="stSidebar"] { width: 130px !important; }
    section[data-testid="stSidebar"] .block-container { padding-top: 0.5rem; }
    /* Divider */
    .section-divider { border-top: 1px solid #ccd5e0; margin: 8px 0 4px 0; }
    /* Plotly modebar'ı sağ alta taşı */
    .modebar-container {
        top: auto !important;
        bottom: 40px !important;
        right: 15px !important;
    }
    .modebar {
        flex-direction: row !important;
    }
    /* Radio butonlarını küçült */
    div[data-testid="stRadio"] > div { transform: scale(0.85); transform-origin: center; }
</style>
""", unsafe_allow_html=True)

# ─── Veri çekme ─────────────────────────────────────────────────────

def fetch_yahoo_chart(ticker: str, start_date, end_date):
    """Yahoo Finance v8 chart API ile veri çek."""
    period1 = int(datetime.combine(start_date, datetime.min.time()).timestamp())
    period2 = int(datetime.combine(end_date, datetime.max.time()).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?period1={period1}&period2={period2}&interval=1d"
        f"&includePrePost=false&events=div%7Csplit"
    )
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    body = resp.json()
    result = body["chart"]["result"]
    if not result:
        return pd.DataFrame()
    meta = result[0]
    timestamps = meta.get("timestamp")
    if not timestamps:
        return pd.DataFrame()
    quote = meta["indicators"]["quote"][0]
    df = pd.DataFrame({
        "Open":   quote["open"],
        "High":   quote["high"],
        "Low":    quote["low"],
        "Close":  quote["close"],
        "Volume": quote["volume"],
    }, index=pd.to_datetime(timestamps, unit="s", utc=True))
    df.index.name = "Date"
    df.index = df.index.tz_convert(None)
    df.dropna(subset=["Close"], inplace=True)
    return df


def get_data(ticker, start_date, end_date):
    try:
        df = fetch_yahoo_chart(ticker, start_date, end_date)
        if not df.empty:
            return df
    except Exception:
        pass
    # Yedek: yfinance
    try:
        import yfinance as yf
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(c).strip() for c in data.columns.values]
            data.rename(columns={c: c.split('_')[0] for c in data.columns}, inplace=True)
        return data
    except Exception:
        return pd.DataFrame()


# ─── Sidebar ────────────────────────────────────────────────────────

if 'lang' not in st.session_state:
    st.session_state.lang = "Türkçe"

# ─── Sidebar Üst Kısım: Başlık ve Dil ───────────────────────────────
st.sidebar.markdown('<p class="small-title" style="text-align:center;">📈 Financial Analysis Terminal</p>', unsafe_allow_html=True)

lang_col1, lang_col2 = st.sidebar.columns(2)
with lang_col1:
    if st.button("TR", use_container_width=True, key="tr_btn_sidebar"):
        st.session_state.lang = "Türkçe"
        st.rerun()
with lang_col2:
    if st.button("EN", use_container_width=True, key="en_btn_sidebar"):
        st.session_state.lang = "English"
        st.rerun()

st.sidebar.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)

lang = st.session_state.lang

texts = {
    "Türkçe": {
        "params": "⚙ Parametreler",
        "ticker": "Sembol",
        "start": "Başlangıç",
        "end": "Bitiş",
        "analyze": "📊 Analiz Et",
        "fetching": "Veri çekiliyor…",
        "no_data": "**{ticker}** için veri bulunamadı. Sembolü ve internet bağlantınızı kontrol edin.",
        "excel": "📥 Excel İndir",
        "open": "Açılış",
        "close": "Kapanış",
        "high": "En Yüksek",
        "low": "En Düşük",
        "volume": "Hacim",
        "change": "Değişim",
        "total_ret": "Toplam Getiri",
        "volatility": "Yıllık Volatilite",
        "sharpe": "Sharpe Oranı",
        "sortino": "Sortino Oranı",
        "max_dd": "Max Drawdown",
        "calmar": "Calmar Oranı",
        "win_rate": "Kazanma Oranı",
        "profit_factor": "Kâr Faktörü",
        "avg_daily": "Ort. Günlük Getiri",
        "daily_range": "Gün Aralığı",
        "annualized_ret": "Yıllık Getiri",
        "var_95": "VaR (%95)",
        "kelly": "RSI (14)",
        "chart_type": "Grafik Tipi",
    },
    "English": {
        "params": "⚙ Parameters",
        "ticker": "Ticker Symbol",
        "start": "Start Date",
        "end": "End Date",
        "analyze": "📊 Analyze",
        "fetching": "Fetching data…",
        "no_data": "No data found for **{ticker}**. Please check the ticker symbol and your connection.",
        "excel": "📥 Download Excel",
        "open": "Open",
        "close": "Close",
        "high": "High",
        "low": "Low",
        "volume": "Volume",
        "change": "Change",
        "total_ret": "Total Return",
        "volatility": "Annual Volatility",
        "sharpe": "Sharpe Ratio",
        "sortino": "Sortino Ratio",
        "max_dd": "Max Drawdown",
        "calmar": "Calmar Ratio",
        "win_rate": "Win Rate",
        "profit_factor": "Profit Factor",
        "avg_daily": "Avg. Daily Return",
        "daily_range": "Daily Range",
        "annualized_ret": "Annualized Return",
        "var_95": "VaR (95%)",
        "kelly": "RSI (14)",
        "chart_type": "Chart Type",
    }
}
t = texts[lang]

if "chart_type" not in st.session_state:
    st.session_state.chart_type = "Candlestick"
chart_type = st.session_state.chart_type

st.sidebar.header(t["params"])
ticker = st.sidebar.text_input(t["ticker"], value="AAPL")
start_date = st.sidebar.date_input(t["start"], value=pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input(t["end"], value=pd.to_datetime("today"))
run_analysis = st.sidebar.button(t["analyze"])

# ─── Analiz ─────────────────────────────────────────────────────────

# ─── Analiz ─────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

if run_analysis or st.session_state.data.empty:
    with st.spinner(t["fetching"]):
        fetched_data = get_data(ticker, start_date, end_date)
        if fetched_data.empty:
            st.error(t["no_data"].format(ticker=ticker))
            st.session_state.data = pd.DataFrame()
        else:
            st.session_state.data = fetched_data
            st.session_state.ticker = ticker

if "data" in st.session_state and not st.session_state.data.empty:
    data = st.session_state.data
    current_ticker = st.session_state.ticker

    # ── Hesaplamalar ────────────────────────────────────────
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['SMA200'] = data['Close'].rolling(window=200).mean()

    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    daily_returns = data['Close'].pct_change().dropna()
    total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
    volatility = daily_returns.std() * np.sqrt(252)
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() != 0 else 0
    cum_returns = (1 + daily_returns).cumprod()
    max_dd = ((cum_returns - cum_returns.cummax()) / cum_returns.cummax()).min()

    # Ek metrikler
    avg_daily_return = daily_returns.mean()
    sortino_neg = daily_returns[daily_returns < 0]
    downside_std = sortino_neg.std() * np.sqrt(252) if len(sortino_neg) > 0 else 0.0001
    sortino = (avg_daily_return * 252) / downside_std if downside_std != 0 else 0
    beta_approx = volatility
    calmar = (total_return / abs(max_dd)) if max_dd != 0 else 0
    win_rate = (daily_returns > 0).sum() / len(daily_returns) if len(daily_returns) > 0 else 0
    avg_gain = daily_returns[daily_returns > 0].mean() if (daily_returns > 0).any() else 0
    avg_loss = daily_returns[daily_returns < 0].mean() if (daily_returns < 0).any() else 0
    profit_factor = abs(avg_gain / avg_loss) if avg_loss != 0 else 0
    
    annualized_return = (1 + total_return) ** (252 / len(daily_returns)) - 1 if len(daily_returns) > 0 else 0
    var_95 = np.percentile(daily_returns, 5) if len(daily_returns) > 0 else 0
    last_rsi = data['RSI'].iloc[-1]
    
    # Trend Hesaplama
    last_sma200 = data['SMA200'].iloc[-1]
    last_close = data['Close'].iloc[-1]
    if pd.isna(last_sma200):
        trend_label = "YETERSİZ VERİ" if lang == "Türkçe" else "NO DATA"
        trend_color = "black"
    else:
        if last_close > last_sma200 * 1.02:
            trend_label = "BOĞA 🐂" if lang == "Türkçe" else "BULL 🐂"
            trend_color = "#16a34a"
        elif last_close < last_sma200 * 0.98:
            trend_label = "AYI 🐻" if lang == "Türkçe" else "BEAR 🐻"
            trend_color = "#dc2626"
        else:
            trend_label = "YATAY ➖" if lang == "Türkçe" else "SIDEWAYS ➖"
            trend_color = "#f59e0b"

    # Son gün verileri
    last_open = data['Open'].iloc[-1]
    last_high = data['High'].iloc[-1]
    last_low = data['Low'].iloc[-1]
    last_vol = data['Volume'].iloc[-1]
    price_range = last_high - last_low
    daily_change = last_close - last_open
    daily_change_pct = (daily_change / last_open) * 100

    # ── Excel indirme ───────────────────────────────────────────
    export_df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    for col in ['SMA20', 'SMA50', 'SMA200', 'RSI']:
        if col in data.columns: export_df[col] = data[col]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_df.to_excel(writer, sheet_name=current_ticker, index=True)
    excel_bytes = output.getvalue()

    st.sidebar.markdown('<div style="margin-top: -10px;"></div>', unsafe_allow_html=True)
    st.sidebar.download_button(
        label=t["excel"],
        data=excel_bytes,
        file_name=f'{current_ticker}_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        use_container_width=True
    )

    # ── Açılış / Kapanış tek satırda ────────────────────────
    change_color = "green" if daily_change >= 0 else "red"
    change_arrow = "▲" if daily_change >= 0 else "▼"
    st.markdown(
        f'<div class="info-row">'
        f'<span>{current_ticker}</span> &nbsp;|&nbsp; '
        f'{t["open"]}: <span>{last_open:.2f}</span> &nbsp;|&nbsp; '
        f'{t["close"]}: <span>{last_close:.2f}</span> &nbsp;|&nbsp; '
        f'{t["high"]}: <span>{last_high:.2f}</span> &nbsp;|&nbsp; '
        f'{t["low"]}: <span>{last_low:.2f}</span> &nbsp;|&nbsp; '
        f'{t["volume"]}: <span>{last_vol:,.0f}</span> &nbsp;|&nbsp; '
        f'{t["change"]}: <span style="color:{change_color}">{change_arrow} {daily_change:+.2f} ({daily_change_pct:+.2f}%)</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Layout: Grafik (sol) + Metrikler (sağ) ──────────────
    chart_col, metric_col = st.columns([15, 1])

    with chart_col:
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.06,
            subplot_titles=(f'{current_ticker}', ''),
            row_width=[0.15, 0.85],
            specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
        )

        # Hacim (Arka planda soluk/şeffaf + Renkli)
        vol_colors = ['rgba(22, 163, 74, 0.6)' if c >= o else 'rgba(220, 38, 38, 0.6)' 
                      for c, o in zip(data['Close'], data['Open'])]
        fig.add_trace(go.Bar(
            x=data.index, y=data['Volume'],
            name='Volume',
            marker_color=vol_colors,
            showlegend=False
        ), row=1, col=1, secondary_y=True)
        
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name='Candlestick',
            ), row=1, col=1, secondary_y=False)
        elif chart_type == "Line":
            fig.add_trace(go.Scatter(
                x=data.index, y=data['Close'], 
                line=dict(color='#0a3d62', width=2), name='Line'
            ), row=1, col=1, secondary_y=False)
        elif chart_type == "Bars (B/W)":
            # Siyah-Beyaz Mum Stili (Hollow Up, Solid Down)
            fig.add_trace(go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name='Bars (B/W)',
                increasing=dict(line=dict(color='black', width=1), fillcolor='white'),
                decreasing=dict(line=dict(color='black', width=1), fillcolor='black')
            ), row=1, col=1, secondary_y=False)
        elif chart_type == "Heikin-Ashi":
            ha_df = data.copy()
            ha_df['Close'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
            ha_df['Open'] = (data['Open'].iloc[0] + data['Close'].iloc[0]) / 2
            for i in range(1, len(data)):
                ha_df.iloc[i, ha_df.columns.get_loc('Open')] = (ha_df.iloc[i-1]['Open'] + ha_df.iloc[i-1]['Close']) / 2
            ha_df['High'] = ha_df[['High', 'Open', 'Close']].max(axis=1)
            ha_df['Low'] = ha_df[['Low', 'Open', 'Close']].min(axis=1)
            fig.add_trace(go.Candlestick(
                x=ha_df.index, open=ha_df['Open'], high=ha_df['High'],
                low=ha_df['Low'], close=ha_df['Close'], name='Heikin-Ashi'
            ), row=1, col=1, secondary_y=False)

        fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'],
                                 line=dict(color='#3b82f6', width=1), name='SMA 20'), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'],
                                 line=dict(color='#f59e0b', width=1), name='SMA 50'), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'],
                                 line=dict(color='#ef4444', width=1), name='SMA 200'), row=1, col=1, secondary_y=False)
        
        fig.add_annotation(
            text=f"<b>{trend_label}</b>",
            xref="x domain", yref="y domain",
            x=0.02, y=0.96,
            showarrow=False,
            font=dict(size=14, color=trend_color),
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor=trend_color,
            borderwidth=2,
            borderpad=4,
            row=1, col=1
        )
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'],
                                 line=dict(color='#8b5cf6', width=2), name='RSI'), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.update_layout(
            height=600, margin=dict(l=0, r=0, t=35, b=0),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=0.24, xanchor="left", x=0.02, bgcolor="rgba(255,255,255,0.5)", font=dict(size=9)),
            hovermode="x unified",
            hoverdistance=100,
            spikedistance=1000,
            font=dict(color="black"),
            dragmode="pan"
        )
        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            showline=True, showgrid=True, spikedash="solid", spikecolor="#555555", spikethickness=1,
            tickfont=dict(size=12, color="black", family="Arial, sans-serif"),
            rangebreaks=[dict(bounds=["sat", "mon"])] # Hafta sonu boşluklarını kaldır
        )
        fig.update_yaxes(
            side='left',
            mirror=True,
            showspikes=True, spikemode="across", spikesnap="cursor",
            showline=True, showgrid=True, spikedash="solid", spikecolor="#555555", spikethickness=1,
            tickfont=dict(size=12, color="black", family="Arial, sans-serif")
        )
        # Hacim eksenini gizle ve ölçeklendir (altta kalması için)
        fig.update_yaxes(showticklabels=False, showgrid=False, range=[0, data['Volume'].max() * 2.5], row=1, col=1, secondary_y=True, fixedrange=True)
        
        # Başlık düzenlemeleri bitti
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        
        # Seçim Butonları (Grafik ve RSI altına taşındı ve küçültüldü)
        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            chart_type = st.radio(
                "Seçim", 
                ["Candlestick", "Line", "Bars (B/W)", "Heikin-Ashi"], 
                horizontal=True, 
                label_visibility="collapsed", 
                key="chart_type"
            )

    with metric_col:
        # ── Getiri Metrikleri ───────────────────────────────
        ret_color = "green" if total_return >= 0 else "red"
        dd_color = "red"
        cards = [
            (t["total_ret"], f"{total_return:.2%}", ret_color),
            (t["volatility"], f"{volatility:.2%}", ""),
            (t["sharpe"], f"{sharpe:.2f}", "green" if sharpe > 1 else ("red" if sharpe < 0 else "")),
            (t["sortino"], f"{sortino:.2f}", "green" if sortino > 1 else ""),
            (t["max_dd"], f"{max_dd:.2%}", dd_color),
            (t["calmar"], f"{calmar:.2f}", ""),
        ]

        for label, val, color in cards:
            cls = f' {color}' if color else ''
            st.markdown(
                f'<div class="metric-card">'
                f'<p class="label">{label}</p>'
                f'<p class="value{cls}">{val}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # ── İşlem İstatistikleri ────────────────────────────
        cards2 = [
            (t["avg_daily"], f"{avg_daily_return:.3%}", "green" if avg_daily_return > 0 else "red"),
            (t["annualized_ret"], f"{annualized_return:.2%}", "green" if annualized_return > 0 else "red"),
            (t["var_95"], f"{var_95:.2%}", "red"),
            (t["kelly"], f"{last_rsi:.2f}", "purple"),
        ]
        for label, val, color in cards2:
            cls = f' {color}' if color else ''
            st.markdown(
                f'<div class="metric-card">'
                f'<p class="label">{label}</p>'
                f'<p class="value{cls}">{val}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="SPX Market Intelligence", layout="wide")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- ROBUST DATA MINING FUNCTIONS ---
def get_safe_data(ticker):
    try:
        d = yf.download(ticker, period="5d", progress=False)
        if not d.empty:
            return d['Close'].dropna().iloc[-1].item()
        return 0.0
    except:
        return 0.0

def calculate_rsi(ticker, period="1d", window=14):
    try:
        hist_period = "60d" if period == "1d" else "2y"
        interval = "1d" if period == "1d" else "1wk"
        df = yf.download(ticker, period=hist_period, interval=interval, progress=False)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1].item()
    except:
        return 0.0

def get_sma(ticker, window):
    try:
        d = yf.download(ticker, period="2y", progress=False)
        return d['Close'].rolling(window=window).mean().iloc[-1].item()
    except:
        return 0.0

def get_sector_leaderboard():
    sectors = {
        "XLC": "Comm Services", "XLY": "Consumer Disc", "XLP": "Consumer Staples",
        "XLE": "Energy", "XLF": "Financials", "XLV": "Health Care",
        "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real Estate",
        "XLK": "Technology", "XLU": "Utilities"
    }
    tickers = list(sectors.keys())
    try:
        data = yf.download(tickers, period="2mo", progress=False)['Close']
        daily = ((data.iloc[-1] / data.iloc[-2]) - 1) * 100
        weekly = ((data.iloc[-1] / data.iloc[-6]) - 1) * 100
        monthly = ((data.iloc[-1] / data.iloc[-21]) - 1) * 100
        
        def format_top5(series):
            top5 = series.sort_values(ascending=False).head(5)
            return [f"{sectors[t]}: {v:+.1f}%" for t, v in top5.items()]

        return format_top5(daily), format_top5(weekly), format_top5(monthly)
    except:
        return ["Data Pending"]*5, ["Data Pending"]*5, ["Data Pending"]*5

# Fetch Core Data
spx_now = get_safe_data("^GSPC")
qqq_now = get_safe_data("QQQ")
vix_now = get_safe_data("^VIX")
tnx_now = get_safe_data("^TNX")
short_rate = get_safe_data("^IRX")
btc_now = get_safe_data("BTC-USD")
gold_now = get_safe_data("GC=F")

# SPX & QQQ Indicators
sma_200d = get_sma("^GSPC", 200)
spx_rsi_d = calculate_rsi("^GSPC", "1d")
spx_rsi_w = calculate_rsi("^GSPC", "1wk")
qqq_200d = get_sma("QQQ", 200)
qqq_rsi_d = calculate_rsi("QQQ", "1d")
qqq_rsi_w = calculate_rsi("QQQ", "1wk")

# Leaderboard Data
top_d, top_w, top_m = get_sector_leaderboard()

# --- THE 6 PILLARS OVERLAY ---
cols = st.columns(6)
mom_val = ((spx_now/sma_200d)-1)*100 if sma_200d > 0 else 0
mom_color = "🟢" if mom_val > 0 else "🔴"

def show_pillar(col, label, status_

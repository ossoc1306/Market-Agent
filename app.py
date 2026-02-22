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
btc_now = get

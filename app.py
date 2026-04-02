import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

# --- 2. PORTFOLIO DEFINITIONS ---
PORTFOLIOS = {
    "All-Weather (Dalio)": {"VTI": 0.30, "TLT": 0.40, "IEF": 0.15, "GLD": 0.075, "DBC": 0.075},
    "60/40 Portfolio": {"VTI": 0.60, "BND": 0.40},
    "Fugger Portfolio": {"VTI": 0.25, "VNQ": 0.25, "BND": 0.25, "GLD": 0.25},
    "Permanent Portfolio": {"VTI": 0.25, "TLT": 0.25, "BIL": 0.25, "GLD": 0.25},
    "Golden Butterfly": {"VTI": 0.20, "IJS": 0.20, "TLT": 0.20, "SHV": 0.20, "GLD": 0.20},
    "Three-Fund": {"VTI": 0.34, "VXUS": 0.33, "BND": 0.33},
    "Coffeehouse": {"VOO": 0.10, "IJS": 0.10, "IJV": 0.10, "VEA": 0.10, "VNQ": 0.10, "VIG": 0.10, "AGG": 0.40},
    "Ivy League (Swensen)": {"VTI": 0.30, "VEA": 0.15, "VWO": 0.05, "VNQ": 0.20, "IEF": 0.15, "TIP": 0.15},
    "Warren Buffett": {"VOO": 0.90, "BIL": 0.10},
    "Global Asset Allocation": {"VTI": 0.18, "VEA": 0.135, "VWO": 0.045, "LQD": 0.18, "TLT": 0.18, "GLD": 0.10, "DBC": 0.10, "VNQ": 0.08}
}

# --- 3. DATA MINING FUNCTIONS ---
@st.cache_data(ttl=600) 
def get_safe_data(ticker):
    try:
        d = yf.download(ticker, period="5d", progress=False)
        return d['Close'].dropna().iloc[-1].item() if not d.empty else 0.0
    except: return 0.0

@st.cache_data(ttl=600)
def calculate_rsi(ticker, period="1d", window=14):
    try:
        hp = "60d" if period == "1d" else "2y"
        iv = "1d" if period == "1d" else "1wk"
        df = yf.download(ticker, period=hp, interval=iv, progress=False)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return (100 - (100 / (1 + rs))).iloc[-1].item()
    except: return 50.0

@st.cache_data(ttl=600)
def get_sma(ticker, window):
    try:
        d = yf.download(ticker, period="2y", progress=False)
        return d['Close'].rolling(window=window).mean().iloc[-1].item()
    except: return 0.0

@st.cache_data(ttl=300)
def get_news_feed(url, limit=5):
    try:
        feed = feedparser.parse(url)
        return [{"title": e.title, "link": e.link} for e in feed.entries[:limit]]
    except: return []

@st.cache_data(ttl=600)
def get_sector_leaderboard():
    sectors = {"XLC":"Comm Services","XLY":"Consumer Disc","XLP":"Consumer Staples","XLE":"Energy","XLF":"Financials","XLV":"Health Care","XLI":"Industrials","XLB":"Materials","XLRE":"Real Estate","XLK":"Technology","XLU":"Utilities"}
    tickers = list(sectors.keys())
    try:
        data = yf.download(tickers, period="max", progress=False)['Close']
        s_rsis = {t: calculate_rsi(t, "1d") for t in tickers}
        daily = ((data.iloc[-1] / data.iloc[-2]) - 1) * 100
        weekly = ((data.iloc[-1] / data.iloc[-6]) - 1) * 100
        monthly = ((data.iloc[-1] / data.iloc[-21]) - 1) * 100
        ytd_start = data[data.index >= f"{datetime.now().year}-01-01"].iloc[0]
        ytd = ((data.iloc[-1] / ytd_start) - 1) * 100
        def get_ranks(series):
            top = series.sort_values(ascending=False).head(5)
            bot = series.sort_values(ascending=True).head(5)
            return [f"{sectors[t]}: {v:+.1f}%" for t, v in top.items()], [f"{sectors[t]}: {v:+.1f}%" for t, v in bot.items()]
        return get_ranks(daily), get_ranks(weekly), get_ranks(monthly), get_ranks(ytd), s_rsis, sectors
    except: return ([],[]),([],[]),([],[]),([],[]), {}, {}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Terminal Controls")
    if st.button("🔄 Refresh Market Data"):
        st.cache_data.clear()
        st.rerun()

# --- 5. TABS ---
tab_terminal, tab_alpha, tab_lab = st.tabs(["🛡️ Terminal", "🕵️ Alpha", "📈 Lab"])

with tab_terminal:
    st.title("🛡️ Multi-Asset Terminal")
    
    # Fetch Core Data
    spx_now = get_safe_data("^GSPC")
    sma_200d = get_sma("^GSPC", 200)
    vix_now = get_safe_data("^VIX")
    tnx_now = get_safe_data("^TNX")
    short_rate = get_safe_data("^IRX")
    gold_now = get_safe_data("GC=F")
    dbc_now = get_safe_data("DBC")
    xlb_now = get_safe_data("XLB")
    btc_now = get_safe_data("BTC-USD")
    dxy_now = get_safe_data("DX-Y.NYB")

    # PILLARS
    cols = st.columns(6)
    cols[0].metric("Momentum", f"{'🟢 BULLISH' if spx_now > sma_200d else '🔴 BEARISH'}", f"{((spx_now/sma_200d)-1)*100:+.1f}% vs 200D")
    cols[1].metric("Inflation", f"{'🔴 HIGH' if (gold_now/dbc_now if dbc_now > 0 else 0) > 1.1 else '🟢 STABLE'}", "Gold/DBC Ratio")
    cols[2].metric("Growth", f"{'🟢 EXPAND' if (xlb_now/gold_now if gold_now > 0 else 0) > 0.015 else '🟡 SLOWING'}", "Materials vs Gold")
    cols[3].metric("Positioning", f"{'🔴 HEAVY' if vix_now > 30 else '🟡 NEUTRAL' if vix_now > 20 else '🟢 LITE'}", f"VIX {vix_now:.1f}")
    cols[4].metric("Monetary", f"{'🔴 TIGHT' if (tnx_now - short_rate) < 0 else '🟢 EASING'}", f"Spread: {tnx_now-short_rate:.2f}%")
    cols[5].metric("Fiscal", f"{'🔴 STRESS' if tnx_now > get_sma('^TNX', 200)*1.1 else '🟢 STABLE'}", "Yield vs 200D MA")

    st.divider()

    # SCORECARD
    st.subheader("🎯 Asset Class Scorecard")
    sc = st.columns(5)
    rsi_avg = (calculate_rsi("^GSPC") + calculate_rsi("QQQ") + calculate_rsi("VXUS")) / 3
    sc[0].metric("Stocks", "🟢 BULLISH" if spx_now > sma_200d and rsi_avg < 65 else "🔴 BEARISH")
    sc[1].metric("Bonds", "🟢 BULLISH" if tnx_now > short_rate else "🔴 BEARISH")
    sc[2].metric("Gold", "🟢 BULLISH" if gold_now/spx_now > 0.7 else "🔴 BEARISH")
    sc[3].metric("Crypto", "🟢 BULLISH" if btc_now > get_sma("BTC-USD", 200) else "🔴 BEARISH")
    sc[4].metric("Real Estate", "🟢 BULLISH" if calculate_rsi("XLRE") < 40 else "🔴 BEARISH")

    st.divider()

    # SECTORS
    daily, weekly, monthly, ytd, s_rsis, s_names = get_sector_leaderboard()
    if s_rsis:
        st.subheader("📊 Sector RSI Heatmap")
        h = st.columns(11)
        for i, (t, r) in enumerate(s_rsis.items()):
            h[i].metric(s_names[t], f"{r:.0f}", "🔴" if r > 70 else "🔵" if r < 30 else "⚪")
        
        st.write("---")
        l = st.columns(4)
        for i, (n, d) in enumerate([("Daily", daily), ("Weekly", weekly), ("Monthly", monthly), ("YTD", ytd)]):
            with l[i]:
                st.write(f"**{n} Leaders**")
                for item in d[0]: st.write(f"🟢 {item}")
                st.write(f"**{n} Laggards**")
                for item in d[1]: st.write(f"🔴 {item}")

# --- TAB 2: ALPHA ---
with tab_alpha:
    st.header("🕵️ Unusual Congressional Alpha")
    api_key = "6sG3kEmPzwx6pzFxdyarM7weg4jvSEFw"
    try:
        data = requests.get(f"https://financialmodelingprep.com/api/v3/house-disclosure?apikey={api_key}").json()
        df = pd.DataFrame([{"Politician": f"{t.get('firstName')} {t.get('lastName')}", "Ticker": t.get('symbol'), "Date": t.get('transactionDate'), "Amount": t.get('amount')} for t in data[:15]])
        st.dataframe(df, use_container_width=True, hide_index=True)
    except: st.warning("API limit reached or key invalid.")

# --- TAB 3: LAB ---
with tab_lab:
    st.header("📈 Portfolio Performance Lab")
    all_t = list(set([t for p in PORTFOLIOS.values() for t in p.keys()]))
    ytd_start = f"{datetime.now().year}-01-01"
    try:
        px = {t: {"c": yf.download(t, period="5d")['Close'].iloc[-1].item(), "s": yf.download(t, start=ytd_start)['Close'].iloc[0].item()} for t in all_t}
        res = []
        for name, weights in PORTFOLIOS.items():
            perf = sum(((px[t]["c"]/px[t]["s"])-1) * w for t, w in weights.items() if t in px)
            res.append({"Portfolio": name, "YTD %": round(perf*100, 2)})
        st.dataframe(pd.DataFrame(res).sort_values("YTD %", ascending=False), use_container_width=True, hide_index=True)
    except: st.error("Data retrieval error for YTD stats.")

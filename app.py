import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

# --- PORTFOLIO DEFINITIONS ---
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

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Terminal Controls")
    if st.button("🔄 Refresh Market Data"):
        st.cache_data.clear()
        st.rerun()
    st.info("Manual refresh clears the cache and pulls the latest data.")

# --- DATA MINING FUNCTIONS ---
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
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1].item()
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

# --- 1. TABS NAVIGATION ---
tab_terminal, tab_alpha, tab_lab = st.tabs(["🛡️ Multi-Asset Terminal", "🕵️ Unusual Congressional Alpha", "📈 Portfolio Lab"])

# --- TAB 1: TERMINAL ---
with tab_terminal:
    st.title("🛡️ Multi-Asset Terminal")
    st.subheader("Global Asset Intel | Automated Macro Overlay")

    # Fetch Core Data
    spx_now = get_safe_data("^GSPC")
    sma_200d = get_sma("^GSPC", 200)
    vix_now = get_safe_data("^VIX")
    tnx_now = get_safe_data("^TNX")
    tnx_200ma = get_sma("^TNX", 200)
    short_rate = get_safe_data("^IRX")
    gold_now = get_safe_data("GC=F")
    dbc_now = get_safe_data("DBC")
    xlb_now = get_safe_data("XLB")
    btc_now = get_safe_data("BTC-USD")
    btc_200ma = get_sma("BTC-USD", 200)
    dxy_now = get_safe_data("DX-Y.NYB")

    # --- 6 PILLARS OVERLAY (FULLY AUTOMATED) ---
    cols = st.columns(6)
    
    # Momentum
    mom_status = "BULLISH" if spx_now > sma_200d else "BEARISH"
    mom_color = "🟢" if mom_status == "BULLISH" else "🔴"
    cols[0].metric("Momentum", f"{mom_color} {mom_status}", f"{((spx_now/sma_200d)-1)*100:+.1f}% vs 200D")

    # Inflation (Gold/Commodity pressure)
    inf_ratio = gold_now / dbc_now if dbc_now > 0 else 0
    inf_status = "🔴 HIGH" if inf_ratio > 1.1 else "🟢 STABLE"
    cols[1].metric("Inflation", inf_status, "Gold/DBC Pressure")

    # Growth (Materials vs Gold)
    growth_ratio = xlb_now / gold_now if gold_now > 0 else 0
    growth_status = "🟢 EXPAND" if growth_ratio > 0.015 else "🟡 SLOWING"
    cols[2].metric("Growth", growth_status, "Materials vs Gold")
    
    # Positioning (VIX)
    pos_status = "🔴 HEAVY" if vix_now > 30 else "🟡 NEUTRAL" if vix_now > 20 else "🟢 LITE"
    cols[3].metric("Positioning", pos_status, f"VIX {vix_now:.1f}")

    # Monetary (10Y-3M Spread)
    spread = tnx_now - short_rate
    mon_status = "🔴 TIGHT" if spread < 0 else "🟢 EASING"
    cols[4].metric("Monetary", mon_status, f"Spread: {spread:.2f}%")

    # Fiscal (Yield Momentum)
    fisc_status = "🔴 STRESS" if tnx_now > tnx_200ma * 1.1 else "🟢 STABLE"
    cols[5].metric("Fiscal", fisc_status, "Yield vs 200D MA")

    st.divider()

    # --- SCORECARD ---
    st.subheader("🎯 Asset Class Scorecard")
    s_cols = st.columns(5)
    avg_rsi = (calculate_rsi("^GSPC") + calculate_rsi("QQQ") + calculate_rsi("VXUS")) / 3
    
    def get_rating(green_cond, red_cond):
        if green_cond: return "🟢 BULLISH"
        if red_cond: return "🔴 BEARISH"
        return "🟡 NEUTRAL"

    s_cols[0].metric("Stocks", get_rating(spx_now > sma_200d and avg_rsi < 65, spx_now < sma_200d or avg_rsi > 75))
    s_cols[1].metric("Bonds", get_rating(tnx_now > short_rate, tnx_now < short_rate))
    s_cols[2].metric("Gold", get_rating(gold_now/spx_now > 0.7 or avg_rsi < 45, dxy_now > 108))
    s_cols[3].metric("Crypto", get_rating(btc_now > btc_200ma and dxy_now < 105, btc_now < btc_200ma or dxy_now > 107))
    s_cols[4].metric("Real Estate", get_rating(calculate_rsi("XLRE") < 40, calculate_rsi("XLRE") > 70))

    st.divider()

    # --- GEOPOLITICAL FEEDS ---
    g_left, g_right = st.columns(2)
    with g_left:
        st.write("**🌍 Global Headlines (BBC)**")
        for e in get_news_feed("https://feeds.bbci.co.uk/news/world/rss.xml") or []:
            st.markdown(f"- [{e['title']}]({e['link']})")
    with g_right:
        st.write("**💰 Finance Headlines (CNBC)**")
        for e in get_news_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114") or []:
            st.markdown(f"- [{e['title']}]({e['link']})")

# --- TAB 2: CONGRESSIONAL ALPHA ---
with tab_alpha:
    st.header("🕵️ Unusual Congressional Alpha Agent (Live)")
    st.markdown("*Target: Top 10 Niche/Small-Cap trades from live filings.*")

    @st.cache_data(ttl=3600)
    def get_hybrid_trades(api_key):
        persistent_memory = [
            {"Politician": "Tim Moore (R)", "Ticker": "GNPX", "Company": "Genprex, Inc.", "Date": "2026-02-05", "Amount": "$1k-$15k", "Rationale": "🔴 Micro-cap Biotech"},
            {"Politician": "Jonathan Jackson (D)", "Ticker": "GEV", "Company": "GE Vernova Inc.", "Date": "2026-01-30", "Amount": "$15k-$50k", "Rationale": "🟠 Infrastructure"},
            {"Politician": "Michael Guest (R)", "Ticker": "CHRD", "Company": "Chord Energy", "Date": "2026-01-09", "Amount": "$1k-$15k", "Rationale": "⚪ Energy Play"}
        ]
        try:
            h_url = f"https://financialmodelingprep.com/api/v3/house-disclosure?apikey={api_key}"
            live_data = requests.get(h_url).json()
            live_unusual = [{"Politician": f"{t.get('firstName')} {t.get('lastName')}", "Ticker": t.get('symbol'), "Company": t.get('assetDescription')[:35], "Date": t.get('transactionDate'), "Amount": t.get('amount'), "Rationale": "🟠 Live Filing"} for t in live_data[:20] if len(t.get('symbol', '')) < 6]
            return pd.DataFrame(live_unusual + persistent_memory).drop_duplicates(subset=['Politician', 'Ticker']).head(10)
        except: return pd.DataFrame(persistent_memory)

    df_alpha = get_hybrid_trades("6sG3kEmPzwx6pzFxdyarM7weg4jvSEFw")
    st.dataframe(df_alpha, use_container_width=True, hide_index=True)

# --- TAB 3: PORTFOLIO LAB ---
with tab_lab:
    st.header("📈 Lazy Portfolio Performance Lab")
    all_p_tickers = list(set([t for p in PORTFOLIOS.values() for t in p.keys()]))
    
    @st.cache_data(ttl=3600)
    def get_ytd_portfolio_data(tickers):
        prices = {}
        ytd_start = f"{datetime.now().year}-01-01"
        for ticker in tickers:
            try:
                df = yf.download(ticker, start=ytd_start, progress=False)
                if not df.empty: prices[ticker] = {"current": df['Close'].iloc[-1].item(), "ytd_start": df['Close'].iloc[0].item()}
            except: continue
        return prices

    p_prices = get_ytd_portfolio_data(all_p_tickers)
    perf_list = []
    for name, weights in PORTFOLIOS.items():
        ytd_perf = sum(((p_prices[t]["current"]/p_prices[t]["ytd_start"])-1) * w for t, w in weights.items() if t in p_prices)
        perf_list.append({"Portfolio Design": name, "Tickers": ", ".join(weights.keys()), "YTD %": round(ytd_perf * 100, 2)})
    
    st.dataframe(pd.DataFrame(perf_list).sort_values(by="YTD %", ascending=False), use_container_width=True, hide_index=True)

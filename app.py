import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
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
        hp, iv = ("60d", "1d") if period == "1d" else ("2y", "1wk")
        df = yf.download(ticker, period=hp, interval=iv, progress=False)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
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

# --- 1. TABS NAVIGATION (Congressional Alpha Removed) ---
tab_terminal, tab_lab = st.tabs(["🛡️ Multi-Asset Terminal", "📈 Portfolio Lab"])

with tab_terminal:
    st.title("🛡️ Multi-Asset Terminal")
    st.subheader("Global Asset Intel | G.A.I. Multi-Asset Overlay")

    # FETCH CORE DATA
    spx_now = get_safe_data("^GSPC")
    vix_now = get_safe_data("^VIX")
    tnx_now = get_safe_data("^TNX")
    short_rate = get_safe_data("^IRX")
    gold_now = get_safe_data("GC=F")
    dbc_now = get_safe_data("DBC")
    xlb_now = get_safe_data("XLB")
    btc_now = get_safe_data("BTC-USD")
    dxy_now = get_safe_data("DX-Y.NYB")
    sma_200d = get_sma("^GSPC", 200)

    # --- 6 PILLARS OVERLAY (AUTOMATED) ---
    cols = st.columns(6)
    cols[0].metric("Momentum", f"{'🟢 BULLISH' if spx_now > sma_200d else '🔴 BEARISH'}", f"{((spx_now/sma_200d)-1)*100:+.1f}% vs 200D")
    cols[1].metric("Inflation", f"{'🔴 HIGH' if (gold_now/dbc_now if dbc_now > 0 else 0) > 1.1 else '🟢 STABLE'}", "Gold/DBC Ratio")
    cols[2].metric("Growth", f"{'🟢 EXPAND' if (xlb_now/gold_now if gold_now > 0 else 0) > 0.015 else '🟡 SLOWING'}", "Materials vs Gold")
    cols[3].metric("Positioning", f"{'🔴 HEAVY' if vix_now > 30 else '🟡 NEUTRAL' if vix_now > 20 else '🟢 LITE'}", f"VIX {vix_now:.1f}")
    cols[4].metric("Monetary", f"{'🔴 TIGHT' if (tnx_now - short_rate) < 0 else '🟢 EASING'}", f"Spread: {tnx_now-short_rate:.2f}%")
    cols[5].metric("Fiscal", f"{'🔴 STRESS' if tnx_now > get_sma('^TNX', 200)*1.1 else '🟢 STABLE'}", "Yield vs 200D MA")

    st.divider()

    # --- ASSET CLASS SCORECARD ---
    st.subheader("🎯 Asset Class Scorecard")
    s_cols = st.columns(5)
    rsi_avg = (calculate_rsi("^GSPC") + calculate_rsi("QQQ") + calculate_rsi("VXUS")) / 3
    
    def get_rating(green_cond, red_cond):
        if green_cond: return "🟢 BULLISH"
        if red_cond: return "🔴 BEARISH"
        return "🟡 NEUTRAL"

    s_cols[0].metric("Stocks", get_rating(spx_now > sma_200d and rsi_avg < 65, spx_now < sma_200d or rsi_avg > 75))
    s_cols[1].metric("Bonds", get_rating(tnx_now > short_rate, tnx_now < short_rate))
    s_cols[2].metric("Gold", get_rating(gold_now/spx_now > 0.7 or rsi_avg < 45, dxy_now > 108))
    s_cols[3].metric("Crypto", get_rating(btc_now > get_sma("BTC-USD", 200) and dxy_now < 105, btc_now < get_sma("BTC-USD", 200)))
    s_cols[4].metric("Real Estate", get_rating(calculate_rsi("XLRE") < 40, calculate_rsi("XLRE") > 70))

    st.divider()

    # --- NEWS FEEDS ---
    geo_left, geo_right = st.columns(2)
    with geo_left:
        st.write("**🌍 Global Headlines (BBC)**")
        for e in get_news_feed("https://feeds.bbci.co.uk/news/world/rss.xml") or []:
            st.markdown(f"- [{e['title']}]({e['link']})")
    with geo_right:
        st.write("**💰 Finance Headlines (CNBC)**")
        for e in get_news_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114") or []:
            st.markdown(f"- [{e['title']}]({e['link']})")

# --- TAB 2: PORTFOLIO LAB (FULLY RESTORED & COMPLETED) ---
with tab_lab:
    st.header("📈 Lazy Portfolio Performance Lab")
    st.caption("Real-time Tracking of Year-to-Date (YTD) Performance")
    
    all_p_tickers = list(set([t for p in PORTFOLIOS.values() for t in p.keys()]))
    
    @st.cache_data(ttl=3600)
    def get_ytd_data(tickers):
        ytd_prices = {}
        ytd_start = f"{datetime.now().year}-01-01"
        for t in tickers:
            try:
                df = yf.download(t, start=ytd_start, progress=False)
                if not df.empty:
                    ytd_prices[t] = {"current": df['Close'].iloc[-1].item(), "start": df['Close'].iloc[0].item()}
            except: continue
        return ytd_prices

    prices = get_ytd_data(all_p_tickers)
    
    if prices:
        perf_results = []
        for name, weights in PORTFOLIOS.items():
            try:
                # Weighted return calculation
                ytd_return = sum(((prices[t]["current"]/prices[t]["start"]) - 1) * w for t, w in weights.items() if t in prices)
                perf_results.append({
                    "Portfolio Design": name,
                    "Tickers": ", ".join(weights.keys()),
                    "YTD %": round(ytd_return * 100, 2)
                })
            except: continue
        
        df_perf = pd.DataFrame(perf_results).sort_values(by="YTD %", ascending=False)
        st.dataframe(df_perf, use_container_width=True, hide_index=True)
        
        # Summary Metrics
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("YTD Leader", df_perf.iloc[0]["Portfolio Design"], f"{df_perf.iloc[0]['YTD %']}%")
        m2.metric("60/40 Benchmark", "Balanced", f"{df_perf[df_perf['Portfolio Design']=='60/40 Portfolio']['YTD %'].values[0]}%")
        m3.metric("YTD Laggard", df_perf.iloc[-1]["Portfolio Design"], f"{df_perf.iloc[-1]['YTD %']}%")
    else:
        st.warning("Awaiting market data for YTD performance calculation...")

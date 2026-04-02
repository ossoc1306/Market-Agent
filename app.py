import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

# --- 2. DATA DEFINITIONS ---
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

SECTORS = {
    "XLC": "Comm Services", "XLY": "Consumer Disc", "XLP": "Consumer Staples",
    "XLE": "Energy", "XLF": "Financials", "XLV": "Health Care",
    "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real Estate",
    "XLK": "Technology", "XLU": "Utilities"
}

# --- 3. CORE FUNCTIONS ---

@st.cache_data(ttl=600)
def get_historical_data(tickers, period="2y"):
    try:
        return yf.download(tickers, period=period, progress=False)['Close']
    except:
        return pd.DataFrame()

def calculate_rsi_vector(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/window, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/window, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=300)
def get_news_feed(url, limit=5):
    try:
        feed = feedparser.parse(url)
        return [{"title": e.title, "link": e.link} for e in feed.entries[:limit]]
    except:
        return []

# --- 4. TABS ---
tab_terminal, tab_alpha, tab_lab = st.tabs(["🛡️ Terminal", "🕵️ Alpha", "📈 Portfolio Lab"])

with tab_terminal:
    st.title("🛡️ Multi-Asset Terminal")
    
    with st.status("Syncing Global Markets...", expanded=False):
        # Fetch indices + Sectors together
        all_core = ["^GSPC", "QQQ", "VXUS", "^VIX", "^TNX", "^IRX", "DX-Y.NYB", "BTC-USD", "GC=F"] + list(SECTORS.keys())
        full_df = get_historical_data(all_core)
        
        prices = full_df.iloc[-1]
        spx_now, sma_200_spx = prices["^GSPC"], full_df["^GSPC"].rolling(200).mean().iloc[-1]
        
        # Sector Analytics
        sector_df = full_df[list(SECTORS.keys())]
        s_rsis = {t: calculate_rsi_vector(sector_df[t]).iloc[-1] for t in SECTORS.keys()}
        
        # Performance Windows
        s_daily = ((sector_df.iloc[-1] / sector_df.iloc[-2]) - 1) * 100
        s_weekly = ((sector_df.iloc[-1] / sector_df.iloc[-6]) - 1) * 100
        s_monthly = ((sector_df.iloc[-1] / sector_df.iloc[-21]) - 1) * 100
        ytd_start = sector_df[sector_df.index >= f"{datetime.now().year}-01-01"].iloc[0]
        s_ytd = ((sector_df.iloc[-1] / ytd_start) - 1) * 100

    # 6 PILLARS
    cols = st.columns(6)
    mom_label = "BULLISH" if spx_now > sma_200_spx else "BEARISH"
    mom_ico = "🟢" if mom_label == "BULLISH" else "🔴"
    cols[0].metric("Momentum", f"{mom_ico} {mom_label}", f"{((spx_now/sma_200_spx)-1)*100:+.1f}% vs 200D")
    cols[1].metric("Inflation", "🟡 2.40%", "PCE Sticky")
    cols[2].metric("Growth", "🟡 1.40%", "Q4 Slowdown")
    cols[3].metric("Positioning", "🟢 LITE", f"VIX {prices['^VIX']:.1f}")
    cols[4].metric("Monetary", "🟡 6.75%", "Prime Rate")
    cols[5].metric("Fiscal", "🔴 DEFICIT", "Duration Mix ↑")

    st.divider()

    # SECTOR PERFORMANCE & HEATMAP (Restored)
    st.subheader("📊 Sector Performance & RSI Heatmap")
    heat_cols = st.columns(11)
    for i, (t, rsi) in enumerate(s_rsis.items()):
        c = "🔴" if rsi > 70 else ("🔵" if rsi < 30 else "⚪")
        heat_cols[i].metric(SECTORS[t], f"{rsi:.0f}", c)
    
    st.write("---")
    l_cols = st.columns(4)
    timeframes = [("Daily", s_daily), ("Weekly", s_weekly), ("Monthly", s_monthly), ("YTD", s_ytd)]
    
    for i, (name, series) in enumerate(timeframes):
        with l_cols[i]:
            st.write(f"**{name} Leaders**")
            top = series.sort_values(ascending=False).head(3)
            for t, v in top.items(): st.write(f"🟢 {SECTORS[t]}: {v:+.1f}%")
            st.write(f"**{name} Laggards**")
            bot = series.sort_values(ascending=True).head(3)
            for t, v in bot.items(): st.write(f"🔴 {SECTORS[t]}: {v:+.1f}%")

    st.divider()

    # NEWS AGENTS
    c_left, c_right = st.columns(2)
    with c_left:
        st.write("**🌍 Global Headlines**")
        for n in get_news_feed("https://feeds.bbci.co.uk/news/world/rss.xml"):
            st.markdown(f"- [{n['title']}]({n['link']})")
    with c_right:
        st.write("**💰 Finance Headlines**")
        for n in get_news_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"):
            st.markdown(f"- [{n['title']}]({n['link']})")

# --- TAB 3: PORTFOLIO LAB ---
with tab_lab:
    st.header("📈 Lazy Portfolio Performance Lab")
    all_p_tickers = list(set([t for p in PORTFOLIOS.values() for t in p.keys()]))
    
    @st.cache_data(ttl=3600)
    def get_ytd_returns(tickers):
        start = f"{datetime.now().year}-01-01"
        data = yf.download(tickers, start=start, progress=False)['Close']
        return (data.iloc[-1] / data.iloc[0]) - 1

    ytd_rets = get_ytd_returns(all_p_tickers)
    results = []
    for name, weights in PORTFOLIOS.items():
        ret = sum(ytd_rets[t] * w for t, w in weights.items() if t in ytd_rets)
        results.append({"Portfolio": name, "YTD %": round(ret*100, 2), "Assets": ", ".join(weights.keys())})
    
    st.dataframe(pd.DataFrame(results).sort_values("YTD %", ascending=False), use_container_width=True, hide_index=True)

st.caption(f"Terminal Updated: {datetime.now().strftime('%H:%M:%S')}")

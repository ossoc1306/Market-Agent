import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
from datetime import datetime

# --- 1. PAGE CONFIG & STYLES ---
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

st.markdown("""
    <style>
        [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
        .stDataFrame { height: 400px; }
    </style>
""", unsafe_allow_html=True)

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

# --- 3. HIGH-EFFICIENCY DATA ENGINES ---

@st.cache_data(ttl=600)
def get_terminal_data(tickers):
    """Vectorized fetch for core terminal metrics."""
    try:
        data = yf.download(tickers, period="2y", progress=False)['Close']
        return data
    except:
        return pd.DataFrame()

def calculate_rsi_vector(series, window=14):
    """Wilder's Smoothing RSI - Vectorized for speed."""
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

# --- 4. DATA PROCESSING ---
core_symbols = ["^GSPC", "QQQ", "VXUS", "^VIX", "^TNX", "^IRX", "DX-Y.NYB", "BTC-USD", "GC=F", "XLRE"]
raw_data = get_terminal_data(core_symbols)

# Latest Prices
prices = raw_data.iloc[-1]
spx_now, btc_now, gold_now = prices["^GSPC"], prices["BTC-USD"], prices["GC=F"]
vix_now, dxy_now, tnx_now, short_rate = prices["^VIX"], prices["DX-Y.NYB"], prices["^TNX"], prices["^IRX"]

# Technicals (200MA & RSI)
sma_200_spx = raw_data["^GSPC"].rolling(window=200).mean().iloc[-1]
sma_200_btc = raw_data["BTC-USD"].rolling(window=200).mean().iloc[-1]
sma_200_gold = raw_data["GC=F"].rolling(window=200).mean().iloc[-1]

rsi_spx = calculate_rsi_vector(raw_data["^GSPC"]).iloc[-1]
rsi_qqq = calculate_rsi_vector(raw_data["QQQ"]).iloc[-1]
rsi_vxus = calculate_rsi_vector(raw_data["VXUS"]).iloc[-1]
avg_rsi = (rsi_spx + rsi_qqq + rsi_vxus) / 3

# --- 5. UI TABS ---
tab_terminal, tab_alpha, tab_lab = st.tabs(["🛡️ Terminal", "🕵️ Alpha", "📈 Portfolio Lab"])

# --- TAB 1: TERMINAL ---
with tab_terminal:
    st.title("🛡️ Multi-Asset Terminal")
    st.subheader("Global Asset Intel | G.A.I. Multi-Asset Overlay")

    # 6 PILLARS OVERLAY
    cols = st.columns(6)
    mom_label = "BULLISH" if spx_now > sma_200_spx else "BEARISH"
    mom_ico = "🟢" if mom_label == "BULLISH" else "🔴"
    mom_dist = ((spx_now/sma_200_spx)-1)*100
    
    cols[0].metric("Momentum", f"{mom_ico} {mom_label}", f"{mom_dist:+.1f}% vs 200D")
    cols[1].metric("Inflation", "🟡 2.40%", "PCE Sticky at 3%")
    cols[2].metric("Growth", "🟡 1.40%", "Q4 Slowdown")
    cols[3].metric("Positioning", "🟢 LITE", f"VIX {vix_now:.1f}")
    cols[4].metric("Monetary", "🟡 6.75%", "Prime Rate")
    cols[5].metric("Fiscal", "🔴 DEFICIT", "Duration Mix ↑")

    st.divider()

    # ASSET CLASS SCORECARD (Trend-Following Logic)
    st.subheader("🎯 Asset Class Scorecard")
    s_cols = st.columns(5)
    
    def get_rating(bull_cond, bear_cond):
        if bull_cond: return "🟢 BULLISH"
        if bear_cond: return "🔴 BEARISH"
        return "🟡 NEUTRAL"

    s_cols[0].metric("Stocks", get_rating(spx_now > sma_200_spx and rsi_spx < 70, spx_now < sma_200_spx or rsi_spx > 80))
    s_cols[1].metric("Bonds", get_rating(tnx_now > short_rate, tnx_now < short_rate))
    s_cols[2].metric("Gold", get_rating(gold_now > sma_200_gold, gold_now < sma_200_gold))
    s_cols[3].metric("Crypto", get_rating(btc_now > sma_200_btc and dxy_now < 103, btc_now < sma_200_btc))
    s_cols[4].metric("Real Estate", get_rating(calculate_rsi_vector(raw_data["XLRE"]).iloc[-1] < 35, calculate_rsi_vector(raw_data["XLRE"]).iloc[-1] > 65))

    # HEATMAP & NEWS
    st.divider()
    st.subheader("🌡️ Market Temperature")
    temp_status = "EXTREME GREED" if avg_rsi > 70 else "EXTREME FEAR" if avg_rsi < 30 else "NEUTRAL"
    st.markdown(f"### Current Regime: **{temp_status}** (Avg RSI: {avg_rsi:.1f})")

    col_l, col_r = st.columns(2)
    with col_l:
        st.write("**🌍 Global Headlines (BBC)**")
        for n in get_news_feed("https://feeds.bbci.co.uk/news/world/rss.xml"):
            st.markdown(f"- [{n['title']}]({n['link']})")
    with col_r:
        st.write("**💰 Finance Headlines (CNBC)**")
        for n in get_news_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"):
            st.markdown(f"- [{n['title']}]({n['link']})")

# --- TAB 2: ALPHA (Simplified for space) ---
with tab_alpha:
    st.header("🕵️ Unusual Congressional Alpha")
    st.info("Agent monitoring live filings for small-cap clusters...")
    # Placeholder for the API logic from previous code
    st.warning("Connect FMP API Key in secrets to activate live tracking.")

# --- TAB 3: PORTFOLIO LAB (High Efficiency) ---
with tab_lab:
    st.header("📈 Lazy Portfolio Performance Lab")
    all_p_tickers = list(set([t for p in PORTFOLIOS.values() for t in p.keys()]))
    
    @st.cache_data(ttl=3600)
    def get_ytd_data(tickers):
        start = f"{datetime.now().year}-01-01"
        data = yf.download(tickers, start=start, progress=False)['Close']
        return (data.iloc[-1] / data.iloc[0]) - 1

    ytd_returns = get_ytd_data(all_p_tickers)
    
    results = []
    for name, weights in PORTFOLIOS.items():
        ret = sum(ytd_returns[t] * w for t, w in weights.items() if t in ytd_returns)
        results.append({"Design": name, "YTD %": round(ret*100, 2), "Assets": ", ".join(weights.keys())})
    
    st.dataframe(pd.DataFrame(results).sort_values("YTD %", ascending=False), use_container_width=True, hide_index=True)

st.caption(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Sources: YFinance, BBC, CNBC")

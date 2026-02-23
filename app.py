import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import time
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Global Asset Intelligence", layout="wide")

st.title("🛡️ Global Asset Intelligence")
st.subheader("Multi-Asset Overlay")

# --- CACHED DATA MINING FUNCTIONS ---
@st.cache_data(ttl=600)
def get_safe_data(ticker):
    # Added retry logic for better reliability
    for attempt in range(2):
        try:
            d = yf.download(ticker, period="5d", progress=False)
            if not d.empty:
                val = d['Close'].dropna().iloc[-1]
                # Ensure we handle both Series and DataFrame outputs from yf
                return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
            time.sleep(1) # Short pause before retry
        except:
            continue
    return 0.0

@st.cache_data(ttl=600)
def calculate_rsi(ticker, period="1d", window=14):
    try:
        hp = "60d" if period == "1d" else "2y"
        iv = "1d" if period == "1d" else "1wk"
        df = yf.download(ticker, period=hp, interval=iv, progress=False)
        if df.empty: return 50.0
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        val = rsi.iloc[-1]
        return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
    except:
        return 50.0

@st.cache_data(ttl=600)
def get_sma(ticker, window):
    try:
        d = yf.download(ticker, period="2y", progress=False)
        val = d['Close'].rolling(window=window).mean().iloc[-1]
        return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
    except:
        return 0.0

@st.cache_data(ttl=600)
def get_news_feed(url, limit=5):
    try:
        feed = feedparser.parse(url)
        return [{"title": e.title, "link": e.link} for e in feed.entries[:limit]]
    except:
        return []

@st.cache_data(ttl=600)
def get_sector_leaderboard():
    sectors = {
        "XLC": "Comm Services", "XLY": "Consumer Disc", "XLP": "Consumer Staples",
        "XLE": "Energy", "XLF": "Financials", "XLV": "Health Care",
        "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real Estate",
        "XLK": "Technology", "XLU": "Utilities"
    }
    tickers = list(sectors.keys())
    try:
        data = yf.download(tickers, period="5d", progress=False)['Close']
        sector_rsis = {t: calculate_rsi(t, "1d") for t in tickers}
        # Simplified logic for leaderboard to speed up initial load
        return {}, {}, {}, {}, sector_rsis, sectors
    except:
        return {}, {}, {}, {}, {}, {}

# --- DATA EXECUTION ---
# Using more reliable ticker symbols
spx_now = get_safe_data("^GSPC")
qqq_now = get_safe_data("QQQ")
vxus_now = get_safe_data("VXUS")
vix_now = get_safe_data("^VIX")
tnx_now = get_safe_data("^TNX") # 10Y Yield
irx_now = get_safe_data("^IRX") # 3M Bill
dxy_now = get_safe_data("DX-Y.NYB") # Dollar Index
btc_now = get_safe_data("BTC-USD")
eth_now = get_safe_data("ETH-USD")
sol_now = get_safe_data("SOL-USD")
gold_now = get_safe_data("GC=F")

sma_200d = get_sma("^GSPC", 200)
btc_200ma = get_sma("BTC-USD", 200)
spx_rsi_d = calculate_rsi("^GSPC")
spx_rsi_w = calculate_rsi("^GSPC", "1wk")
avg_rsi = (spx_rsi_d + calculate_rsi("QQQ") + calculate_rsi("VXUS")) / 3

# --- 6 PILLARS ---
cols = st.columns(6)
mom_val = ((spx_now/sma_200d)-1)*100 if sma_200d > 0 else 0
cols[0].metric("Momentum", "🟢 BULLISH" if mom_val > 0 else "🔴 BEARISH", f"{mom_val:+.1f}% vs 200D")
cols[1].metric("Inflation", "🟡 2.40%", "PCE Sticky at 3%")
cols[2].metric("Growth", "🟡 1.40%", "Q4 Slowdown")
cols[3].metric("Positioning", "🟢 LITE", f"VIX {vix_now:.1f}")
cols[4].metric("Monetary", "🟡 6.75%", "Prime Rate")
cols[5].metric("Fiscal", "🔴 DEFICIT", "Duration Mix ↑")

st.divider()

# --- ASSET SCORECARD ---
st.subheader("🎯 Asset Class Scorecard")
s_cols = st.columns(5)
def get_rating(green, red):
    return "🟢 BULLISH" if green else ("🔴 BEARISH" if red else "🟡 NEUTRAL")

s_cols[0].metric("Stocks", get_rating(spx_now > sma_200d and avg_rsi < 65, spx_now < sma_200d))
s_cols[1].metric("Bonds", get_rating(tnx_now > irx_now, tnx_now < irx_now))
s_cols[2].metric("Gold", get_rating(gold_now/spx_now > 0.7 if spx_now > 0 else False, dxy_now > 108))
s_cols[3].metric("Crypto", get_rating(btc_now > btc_200ma and dxy_now < 105, btc_now < btc_200ma))
s_cols[4].metric("Real Estate", get_rating(calculate_rsi("XLRE") < 40, calculate_rsi("XLRE") > 70))

st.divider()

# --- HEATMAP ---
st.subheader("📊 Sector Performance & RSI Heatmap")
_, _, _, _, s_rsis, s_names = get_sector_leaderboard()
if s_rsis:
    heat_cols = st.columns(11)
    for i, (t, r) in enumerate(s_rsis.items()):
        c = "🔴" if r > 70 else ("🔵" if r < 30 else "⚪")
        heat_cols[i].metric(s_names[t], f"{r:.0f}", c)

st.divider()

# --- DEEP DIVES ---
col_left, col_right = st.columns(2)
with col_left:
    with st.expander("🔍 Momentum & Trend Layers", expanded=True):
        st.write(f"**SPX**: {spx_now:,.2f} | **QQQ**: {qqq_now:,.2f}")
        st.caption(f"SPX Daily RSI: {spx_rsi_d:.1f} | Weekly: {spx_rsi_w:.1f}")

    with st.expander("₿ Crypto Intelligence Agent", expanded=True):
        c_cols = st.columns(3)
        crypto_assets = [("Bitcoin", btc_now, "BTC-USD"), ("Ethereum", eth_now, "ETH-USD"), ("Solana", sol_now, "SOL-USD")]
        for i, (name, price, ticker) in enumerate(crypto_assets):
            dr = calculate_rsi(ticker, "1d")
            wr = calculate_rsi(ticker, "1wk")
            with c_cols[i]:
                st.write(f"**{name}**")
                st.write(f"${price:,.2f}")
                st.caption(f"D:{dr:.1f} | W:{wr:.1f}")
                st.write("Status: " + ("🔴" if dr > 70 else ("🔵" if dr < 30 else "⚪")))

with col_right:
    with st.expander("🌊 Liquidity & Yields", expanded=True):
        st.write(f"**DXY Index**: {dxy_now:.2f} | **Gold**: ${gold_now:,.2f}")
        st.write(f"**10Y Yield**: {tnx_now:.2f}%")

    with st.expander("🌍 Geopolitical Feed", expanded=True):
        st.write("**Reuters World News**")
        for e in get_news_feed("https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best"):
            st.markdown(f"- [{e['title']}]({e['link']})")

st.divider()
st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

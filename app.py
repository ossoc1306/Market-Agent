import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

# --- PORTFOLIO DEFINITIONS (Updated with Rationale & Precise Weights) ---
PORTFOLIOS = {
    "All-Weather (Dalio)": {
        "weights": {"VTI": 0.30, "TLT": 0.40, "IEF": 0.15, "GLD": 0.075, "DBC": 0.075},
        "rationale": "Balanced for all economic 'seasons' (inflation, deflation, growth, recession)."
    },
    "60/40 Portfolio": {
        "weights": {"VTI": 0.60, "BND": 0.40},
        "rationale": "The classic benchmark for moderate risk and steady growth."
    },
    "Three-Fund (Bogleheads)": {
        "weights": {"VTI": 0.34, "VXUS": 0.33, "BND": 0.33},
        "rationale": "Maximum diversification with minimum complexity and ultra-low fees."
    },
    "Core-Four (Rick Ferri)": {
        "weights": {"VTI": 0.48, "VXUS": 0.24, "BND": 0.20, "VNQ": 0.08},
        "rationale": "Enhances the Three-Fund model with a dedicated Real Estate (REIT) tilt."
    },
    "No-Brainer (Bernstein)": {
        "weights": {"VOO": 0.25, "IJR": 0.25, "VEA": 0.25, "BND": 0.25},
        "rationale": "Equal split across US Large, US Small, Intl, and Bonds to avoid over-concentration."
    },
    "Permanent Portfolio": {
        "weights": {"VTI": 0.25, "TLT": 0.25, "BIL": 0.25, "GLD": 0.25},
        "rationale": "Built for extreme safety by holding non-correlated assets."
    },
    "Golden Butterfly": {
        "weights": {"VTI": 0.20, "IJS": 0.20, "TLT": 0.20, "SHV": 0.20, "GLD": 0.20},
        "rationale": "High-velocity version of the Permanent Portfolio with a Small-Cap Value tilt."
    },
    "Ivy League (Swensen)": {
        "weights": {"VTI": 0.30, "VEA": 0.15, "VWO": 0.05, "VNQ": 0.20, "IEF": 0.15, "TIP": 0.15},
        "rationale": "Mimics institutional endowment strategies with heavy Real Estate/TIPS exposure."
    },
    "Global Asset Allocation": {
        "weights": {"VTI": 0.18, "VEA": 0.135, "VWO": 0.045, "LQD": 0.18, "TLT": 0.18, "GLD": 0.10, "DBC": 0.10, "VNQ": 0.08},
        "rationale": "A 'buy-the-world' strategy covering almost every liquid asset class."
    },
    "Warren Buffett": {
        "weights": {"VOO": 0.90, "BIL": 0.10},
        "rationale": "Aggressive US-centric bet on S&P 500 compounding with a tiny cash reserve."
    },
    "Coffeehouse": {
        "weights": {"VOO": 0.10, "IJS": 0.10, "IJV": 0.10, "VEA": 0.10, "VNQ": 0.10, "VIG": 0.10, "AGG": 0.40},
        "rationale": "Diversified equity slices with a heavy bond floor for income and stability."
    },
    "Fugger Portfolio": {
        "weights": {"VTI": 0.25, "VNQ": 0.25, "BND": 0.25, "GLD": 0.25},
        "rationale": "Historical wealth preservation model split equally across primary assets."
    }
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Terminal Controls")
    if st.button("🔄 Refresh Market Data"):
        st.cache_data.clear()
        st.rerun()

# --- DATA FUNCTIONS ---
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
        rs = gain / loss
        return (100 - (100 / (1 + rs))).iloc[-1].item()
    except: return 50.0

@st.cache_data(ttl=600)
def get_sma(ticker, window):
    try:
        d = yf.download(ticker, period="2y", progress=False)
        return d['Close'].rolling(window=window).mean().iloc[-1].item()
    except: return 0.0

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

# --- TABS ---
tab_terminal, tab_lab = st.tabs(["🛡️ Multi-Asset Terminal", "📈 Portfolio Lab"])

with tab_terminal:
    st.title("🛡️ Multi-Asset Terminal")
    st.subheader("Global Asset Intel | G.A.I. Multi-Asset Overlay")

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

    # 6 PILLARS
    cols = st.columns(6)
    cols[0].metric("Momentum", f"{'🟢 BULLISH' if spx_now > sma_200d else '🔴 BEARISH'}", f"{((spx_now/sma_200d)-1)*100:+.1f}% vs 200D")
    cols[1].metric("Inflation", f"{'🔴 HIGH' if (gold_now/dbc_now if dbc_now > 0 else 0) > 1.1 else '🟢 STABLE'}", "Gold/DBC Ratio")
    cols[2].metric("Growth", f"{'🟢 EXPAND' if (xlb_now/gold_now if gold_now > 0 else 0) > 0.015 else '🟡 SLOWING'}", "Materials vs Gold")
    cols[3].metric("Positioning", f"{'🔴 HEAVY' if vix_now > 30 else '🟡 NEUTRAL' if vix_now > 20 else '🟢 LITE'}", f"VIX {vix_now:.1f}")
    cols[4].metric("Monetary", f"{'🔴 TIGHT' if (tnx_now - short_rate) < 0 else '🟢 EASING'}", f"Spread: {tnx_now-short_rate:.2f}%")
    cols[5].metric("Fiscal", f"{'🔴 STRESS' if tnx_now > get_sma('^TNX', 200)*1.1 else '🟢 STABLE'}", "Yield vs 200D MA")

    st.divider()

    # Asset Class Scorecard
    sc = st.columns(5)
    rsi_avg = (calculate_rsi("^GSPC") + calculate_rsi("QQQ") + calculate_rsi("VXUS")) / 3
    def get_rating(green_cond, red_cond):
        if green_cond: return "🟢 BULLISH"
        if red_cond: return "🔴 BEARISH"
        return "🟡 NEUTRAL"

    sc[0].metric("Stocks", get_rating(spx_now > sma_200d and rsi_avg < 65, spx_now < sma_200d or rsi_avg > 75))
    sc[1].metric("Bonds", get_rating(tnx_now > short_rate, tnx_now < short_rate))
    sc[2].metric("Gold", get_rating(gold_now/spx_now > 0.7 or rsi_avg < 45, dxy_now > 108))
    sc[3].metric("Crypto", get_rating(btc_now > get_sma("BTC-USD", 200) and dxy_now < 105, btc_now < get_sma("BTC-USD", 200)))
    sc[4].metric("Real Estate", get_rating(calculate_rsi("XLRE") < 40, calculate_rsi("XLRE") > 70))

    st.divider()

    # Sector Analytics
    daily, weekly, monthly, ytd, s_rsis, s_names = get_sector_leaderboard()
    if s_rsis:
        st.subheader("📊 Sector Performance & RSI Heatmap")
        heat_cols = st.columns(11)
        for i, (t, r) in enumerate(s_rsis.items()):
            heat_cols[i].metric(s_names[t], f"{r:.0f}", "🔴" if r > 70 else "🔵" if r < 30 else "⚪")
        
        st.write("---")
        l_cols = st.columns(4)
        for i, (n, d) in enumerate([("Daily", daily), ("Weekly", weekly), ("Monthly", monthly), ("Year-to-Date", ytd)]):
            with l_cols[i]:
                st.write(f"**{n} Leaders**")
                for item in d[0]: st.write(f"🟢 {item}")
                st.write(f"**{n} Laggards**")
                for item in d[1]: st.write(f"🔴 {item}")

    st.divider()

    # --- DEEP DIVES (BITCOIN, ETH, SOL, DXY, GOLD RESTORED) ---
    col_l, col_r = st.columns(2)
    with col_l:
        with st.expander("🔍 Momentum & Trend Layers (SPX, QQQ, VXUS)", expanded=True):
            st.write(f"**S&P 500 (SPX):** {spx_now:,.2f} | **Nasdaq (QQQ):** {get_safe_data('QQQ'):,.2f}")
            st.write(f"**Bitcoin:** ${btc_now:,.2f} | **200-MA:** ${get_sma('BTC-USD', 200):,.2f}")

        with st.expander("₿ Crypto Intelligence Agent (BTC, ETH, SOL)", expanded=True):
            cryptos = {"Bitcoin (BTC)": "BTC-USD", "Ethereum (ETH)": "ETH-USD", "Solana (SOL)": "SOL-USD"}
            c_cols = st.columns(3)
            for i, (name, ticker) in enumerate(cryptos.items()):
                p, dr, wr = get_safe_data(ticker), calculate_rsi(ticker, "1d"), calculate_rsi(ticker, "1wk")
                with c_cols[i]:
                    st.write(f"**{name}**")
                    st.write(f"Price: ${p:,.2f}")
                    st.write(f"Daily RSI: {dr:.1f} | Weekly: {wr:.1f}")

    with col_r:
        with st.expander("🌊 Liquidity & Yields", expanded=True):
            st.write(f"**Dollar Index (DXY):** {dxy_now:.2f} | **10Y/3M Spread:** {tnx_now-short_rate:.2f}%")
            st.write(f"**Gold Price:** ${gold_now:,.2f} | **Gold/SPX Ratio:** {gold_now/spx_now:.4f}")

        with st.expander("🌍 Global Headlines (BBC)", expanded=True):
            feed = feedparser.parse("https://feeds.bbci.co.uk/news/world/rss.xml")
            for entry in feed.entries[:5]: st.markdown(f"- [{entry.title}]({entry.link})")

    st.divider()
    st.write("**💰 Finance Headlines (CNBC)**")
    f_feed = feedparser.parse("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114")
    for entry in f_feed.entries[:5]: st.markdown(f"- [{entry.title}]({entry.link})")

# --- TAB 2: PORTFOLIO LAB (Full Weights + Rationale) ---
with tab_lab:
    st.header("📈 Lazy Portfolio Performance Lab")
    all_t = list(set([t for p in PORTFOLIOS.values() for t in p["weights"].keys()]))
    ytd_start = f"{datetime.now().year}-01-01"
    
    @st.cache_data(ttl=3600)
    def get_ytd_data(tickers):
        px = {}
        for t in tickers:
            try:
                df = yf.download(t, start=ytd_start, progress=False)
                if not df.empty: px[t] = {"c": df['Close'].iloc[-1].item(), "s": df['Close'].iloc[0].item()}
            except: continue
        return px

    px_data = get_ytd_data(all_t)
    if px_data:
        results = []
        for name, data in PORTFOLIOS.items():
            w_display = [f"{t} ({int(w*100)}%)" for t, w in data["weights"].items()]
            ret = sum(((px_data[t]["c"]/px_data[t]["s"])-1) * w for t, w in data["weights"].items() if t in px_data)
            results.append({
                "Portfolio": name, 
                "YTD %": round(ret*100, 2), 
                "Rationale": data["rationale"], 
                "Tickers & Weights": ", ".join(w_display)
            })
        st.dataframe(pd.DataFrame(results).sort_values("YTD %", ascending=False), use_container_width=True, hide_index=True)

import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

# --- PORTFOLIO DEFINITIONS (Updated with Historical & Regime Data) ---
PORTFOLIOS = {
    "All-Weather (Dalio)": {
        "weights": {"VTI": 0.30, "TLT": 0.40, "IEF": 0.15, "GLD": 0.075, "DBC": 0.075},
        "hist_ret": "6.0%", "stag_pot": "High"
    },
    "60/40 Portfolio": {
        "weights": {"VTI": 0.60, "BND": 0.40},
        "hist_ret": "8.4%", "stag_pot": "Low"
    },
    "Fugger Portfolio": {
        "weights": {"VTI": 0.25, "VNQ": 0.25, "BND": 0.25, "GLD": 0.25},
        "hist_ret": "6.1%", "stag_pot": "High"
    },
    "Permanent Portfolio": {
        "weights": {"VTI": 0.25, "TLT": 0.25, "BIL": 0.25, "GLD": 0.25},
        "hist_ret": "5.9%", "stag_pot": "High"
    },
    "Golden Butterfly": {
        "weights": {"VTI": 0.20, "IJS": 0.20, "TLT": 0.20, "SHV": 0.20, "GLD": 0.20},
        "hist_ret": "7.2%", "stag_pot": "High"
    },
    "Three-Fund": {
        "weights": {"VTI": 0.34, "VXUS": 0.33, "BND": 0.33},
        "hist_ret": "8.9%", "stag_pot": "Low"
    },
    "Coffeehouse": {
        "weights": {"VOO": 0.10, "IJS": 0.10, "IJV": 0.10, "VEA": 0.10, "VNQ": 0.10, "VIG": 0.10, "AGG": 0.40},
        "hist_ret": "8.2%", "stag_pot": "Low-Mod"
    },
    "Ivy League (Swensen)": {
        "weights": {"VTI": 0.30, "VEA": 0.15, "VWO": 0.05, "VNQ": 0.20, "IEF": 0.15, "TIP": 0.15},
        "hist_ret": "7.5%", "stag_pot": "Moderate"
    },
    "Warren Buffett": {
        "weights": {"VOO": 0.90, "BIL": 0.10},
        "hist_ret": "11.2%", "stag_pot": "Low"
    },
    "Global Asset Allocation": {
        "weights": {"VTI": 0.18, "VEA": 0.135, "VWO": 0.045, "LQD": 0.18, "TLT": 0.18, "GLD": 0.10, "DBC": 0.10, "VNQ": 0.08},
        "hist_ret": "7.8%", "stag_pot": "Moderate"
    }
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Terminal Controls")
    if st.button("🔄 Refresh Market Data"):
        st.cache_data.clear()
        st.rerun()
    st.info("Manual refresh clears the cache and pulls the latest data.")

# --- 1. TABS NAVIGATION ---
tab_terminal, tab_lab = st.tabs(["🛡️ Multi-Asset Terminal", "📈 Portfolio Lab"])

with tab_terminal:
    st.title("🛡️ Multi-Asset Terminal")
    st.subheader("Global Asset Intel | G.A.I. Multi-Asset Overlay")

    # --- DATA MINING FUNCTIONS ---
    @st.cache_data(ttl=600) 
    def get_safe_data(ticker):
        try:
            d = yf.download(ticker, period="5d", progress=False)
            if not d.empty:
                return d['Close'].dropna().iloc[-1].item()
            return 0.0
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

    @st.cache_data(ttl=600)
    def get_sector_leaderboard():
        sectors = {"XLC": "Comm Services", "XLY": "Consumer Disc", "XLP": "Consumer Staples", "XLE": "Energy", "XLF": "Financials", "XLV": "Health Care", "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real Estate", "XLK": "Technology", "XLU": "Utilities"}
        tickers = list(sectors.keys())
        try:
            data = yf.download(tickers, period="max", progress=False)['Close']
            sector_rsis = {t: calculate_rsi(t, "1d") for t in tickers}
            daily = ((data.iloc[-1] / data.iloc[-2]) - 1) * 100
            weekly = ((data.iloc[-1] / data.iloc[-6]) - 1) * 100
            monthly = ((data.iloc[-1] / data.iloc[-21]) - 1) * 100
            ytd_start = data[data.index >= f"{datetime.now().year}-01-01"].iloc[0]
            ytd = ((data.iloc[-1] / ytd_start) - 1) * 100
            def get_ranks(series):
                top = series.sort_values(ascending=False).head(5)
                bot = series.sort_values(ascending=True).head(5)
                return [f"{sectors[t]}: {v:+.1f}% (RSI: {sector_rsis[t]:.1f})" for t, v in top.items()], [f"{sectors[t]}: {v:+.1f}% (RSI: {sector_rsis[t]:.1f})" for t, v in bot.items()]
            return get_ranks(daily), get_ranks(weekly), get_ranks(monthly), get_ranks(ytd), sector_rsis, sectors
        except: return ([],[]),([],[]),([],[]),([],[]), {}, {}

    # --- FETCH CORE DATA ---
    spx_now = get_safe_data("^GSPC")
    qqq_now = get_safe_data("QQQ")
    vxus_now = get_safe_data("VXUS")
    vix_now = get_safe_data("^VIX")
    tnx_now = get_safe_data("^TNX")
    short_rate = get_safe_data("^IRX")
    dxy_now = get_safe_data("DX-Y.NYB")
    btc_now = get_safe_data("BTC-USD")
    gold_now = get_safe_data("GC=F")
    dbc_now = get_safe_data("DBC")
    xlb_now = get_safe_data("XLB")

    # INDICATORS
    sma_200d = get_sma("^GSPC", 200)
    tnx_200ma = get_sma("^TNX", 200)
    btc_200ma = get_sma("BTC-USD", 200)
    avg_rsi = (calculate_rsi("^GSPC") + calculate_rsi("QQQ") + calculate_rsi("VXUS")) / 3

    # --- 6 PILLARS OVERLAY (AUTOMATED) ---
    cols = st.columns(6)
    cols[0].metric("Momentum", f"{'🟢 BULLISH' if spx_now > sma_200d else '🔴 BEARISH'}", f"{((spx_now/sma_200d)-1)*100:+.1f}% vs 200D")
    cols[1].metric("Inflation", f"{'🔴 HIGH' if (gold_now/dbc_now if dbc_now > 0 else 0) > 1.1 else '🟢 STABLE'}", "Gold/DBC Ratio")
    cols[2].metric("Growth", f"{'🟢 EXPAND' if (xlb_now/gold_now if gold_now > 0 else 0) > 0.015 else '🟡 SLOWING'}", "Materials vs Gold")
    cols[3].metric("Positioning", f"{'🔴 HEAVY' if vix_now > 30 else '🟡 NEUTRAL' if vix_now > 20 else '🟢 LITE'}", f"VIX {vix_now:.1f}")
    cols[4].metric("Monetary", f"{'🔴 TIGHT' if (tnx_now - short_rate) < 0 else '🟢 EASING'}", f"Spread: {tnx_now-short_rate:.2f}%")
    cols[5].metric("Fiscal", f"{'🔴 STRESS' if tnx_now > tnx_200ma * 1.1 else '🟢 STABLE'}", "Yield vs 200D MA")

    st.divider()

    # --- SCORECARD ---
    st.subheader("🎯 Asset Class Scorecard")
    sc = st.columns(5)
    def get_rating(green_cond, red_cond):
        if green_cond: return "🟢 BULLISH"
        if red_cond: return "🔴 BEARISH"
        return "🟡 NEUTRAL"

    sc[0].metric("Stocks", get_rating(spx_now > sma_200d and avg_rsi < 65, spx_now < sma_200d or avg_rsi > 75))
    sc[1].metric("Bonds", get_rating(tnx_now > short_rate, tnx_now < short_rate))
    sc[2].metric("Gold", get_rating(gold_now/spx_now > 0.7 or avg_rsi < 45, dxy_now > 108))
    sc[3].metric("Crypto", get_rating(btc_now > btc_200ma and dxy_now < 105, btc_now < btc_200ma or dxy_now > 107))
    sc[4].metric("Real Estate", get_rating(calculate_rsi("XLRE") < 40, calculate_rsi("XLRE") > 70))

    st.divider()

    # --- SECTOR PERFORMANCE & HEATMAP ---
    daily, weekly, monthly, ytd, s_rsis, s_names = get_sector_leaderboard()
    if s_rsis:
        st.subheader("📊 Sector Performance & RSI Heatmap")
        heat_cols = st.columns(11)
        for i, (t, r) in enumerate(s_rsis.items()):
            heat_cols[i].metric(s_names[t], f"{r:.0f}", "🔴" if r > 70 else "🔵" if r < 30 else "⚪")
        
        st.write("---")
        l_cols = st.columns(4)
        for i, (name, data) in enumerate([("Daily", daily), ("Weekly", weekly), ("Monthly", monthly), ("Year-to-Date", ytd)]):
            with l_cols[i]:
                st.write(f"**{name} Leaders**")
                for item in data[0]: st.write(f"🟢 {item}")
                st.write(f"**{name} Laggards**")
                for item in data[1]: st.write(f"🔴 {item}")

    st.divider()

    # --- DEEP DIVES ---
    col_left, col_right = st.columns(2)
    with col_left:
        with st.expander("🔍 Momentum & Trend Layers (SPX, QQQ, VXUS)", expanded=True):
            st.write(f"**S&P 500 (SPX):** {spx_now:,.2f} (200-MA: {sma_200d:,.2f})")
            st.write(f"**Nasdaq (QQQ):** {qqq_now:,.2f} | **Intl (VXUS):** {vxus_now:,.2f}")

        with st.expander("₿ Crypto Intelligence Agent (BTC, ETH, SOL)", expanded=True):
            cryptos = {"Bitcoin (BTC)": "BTC-USD", "Ethereum (ETH)": "ETH-USD", "Solana (SOL)": "SOL-USD"}
            c_cols = st.columns(3)
            for i, (name, ticker) in enumerate(cryptos.items()):
                p = get_safe_data(ticker)
                dr = calculate_rsi(ticker, "1d")
                with c_cols[i]:
                    st.write(f"**{name}**")
                    st.write(f"Price: ${p:,.2f} | RSI: {dr:.1f}")

    with col_right:
        with st.expander("🌊 Liquidity & Yields", expanded=True):
            st.write(f"**Dollar Index (DXY):** {dxy_now:.2f}")
            st.write(f"**10Y/3M Spread:** {tnx_now - short_rate:.2f}%")

        with st.expander("✨ Gold Intelligence Agent", expanded=True):
            st.write(f"**Gold Price:** ${gold_now:,.2f}")
            st.write(f"**Gold/SPX Ratio:** {gold_now/spx_now if spx_now > 0 else 0:.4f}")

    st.divider()
    
    # NEWS FEEDS
    geo_left, geo_right = st.columns(2)
    with geo_left:
        st.write("**🌍 Global Headlines (BBC)**")
        for e in get_news_feed("https://feeds.bbci.co.uk/news/world/rss.xml") or []:
            st.markdown(f"- [{e['title']}]({e['link']})")
    with geo_right:
        st.write("**💰 Finance Headlines (CNBC)**")
        for e in get_news_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114") or []:
            st.markdown(f"- [{e['title']}]({e['link']})")

# --- TAB 2: PORTFOLIO LAB (Updated with New Columns) ---
with tab_lab:
    st.header("📈 Lazy Portfolio Performance Lab")
    
    # Get flat list of tickers for live YTD calculation
    all_p_tickers = list(set([t for p in PORTFOLIOS.values() for t in p["weights"].keys()]))
    
    @st.cache_data(ttl=3600)
    def get_ytd_portfolio_data(tickers):
        prices = {}
        ytd_start_date = f"{datetime.now().year}-01-01"
        for ticker in tickers:
            try:
                df = yf.download(ticker, start=ytd_start_date, progress=False)
                if not df.empty:
                    prices[ticker] = {"current": df['Close'].iloc[-1].item(), "ytd_start": df['Close'].iloc[0].item()}
            except: continue
        return prices

    p_prices = get_ytd_portfolio_data(all_p_tickers)
    if p_prices:
        res = []
        for name, data in PORTFOLIOS.items():
            weights = data["weights"]
            # Build string for weights display
            weight_strings = [f"{t}: {int(w*100)}%" for t, w in weights.items()]
            ytd_perf = sum(((p_prices[t]["current"]/p_prices[t]["ytd_start"])-1) * w for t, w in weights.items() if t in p_prices)
            
            res.append({
                "Portfolio Design": name, 
                "Allocation Weighting": ", ".join(weight_strings),
                "YTD %": round(ytd_perf * 100, 2),
                "Ann. Return (Since 2008)": data["hist_ret"],
                "Stagflation Potential": data["stag_pot"]
            })
        
        st.dataframe(pd.DataFrame(res).sort_values(by="YTD %", ascending=False), use_container_width=True, hide_index=True)

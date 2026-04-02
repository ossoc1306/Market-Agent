import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

# --- PORTFOLIO DEFINITIONS (Restored to Full Detail) ---
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
    st.info("Manual refresh clears the cache and pulls the latest prices.")

# --- 1. TABS NAVIGATION ---
tab_terminal, tab_alpha, tab_lab = st.tabs(["🛡️ Multi-Asset Terminal", "🕵️ Unusual Congressional Alpha", "📈 Portfolio Lab"])

with tab_terminal:
    st.title("🛡️ Multi-Asset Terminal")
    st.subheader("Global Asset Intel | G.A.I. Multi-Asset Overlay")

    # --- DATA MINING FUNCTIONS (Restored Original Logic) ---
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
            data = yf.download(tickers, period="max", progress=False)['Close']
            sector_rsis = {t: calculate_rsi(t, "1d") for t in tickers}
            daily = ((data.iloc[-1] / data.iloc[-2]) - 1) * 100
            weekly = ((data.iloc[-1] / data.iloc[-6]) - 1) * 100
            monthly = ((data.iloc[-1] / data.iloc[-21]) - 1) * 100
            current_year = datetime.now().year
            ytd_start = data[data.index >= f"{current_year}-01-01"].iloc[0]
            ytd = ((data.iloc[-1] / ytd_start) - 1) * 100
            
            def get_ranks(series):
                sorted_s = series.sort_values(ascending=False)
                top5 = sorted_s.head(5)
                bot5 = sorted_s.tail(5).sort_values(ascending=True)
                t_list = [f"{sectors[t]}: {v:+.1f}% (RSI: {sector_rsis[t]:.1f})" for t, v in top5.items()]
                b_list = [f"{sectors[t]}: {v:+.1f}% (RSI: {sector_rsis[t]:.1f})" for t, v in bot5.items()]
                return t_list, b_list

            return get_ranks(daily), get_ranks(weekly), get_ranks(monthly), get_ranks(ytd), sector_rsis, sectors
        except:
            err = ["Data Pending"]*5
            return (err, err), (err, err), (err, err), (err, err), {}, {}

    # --- FETCH CORE DATA ---
    spx_now = get_safe_data("^GSPC")
    vix_now = get_safe_data("^VIX")
    tnx_now = get_safe_data("^TNX")
    short_rate = get_safe_data("^IRX")
    gold_now = get_safe_data("GC=F")
    dbc_now = get_safe_data("DBC")
    xlb_now = get_safe_data("XLB")
    btc_now = get_safe_data("BTC-USD")
    dxy_now = get_safe_data("DX-Y.NYB")

    # --- INDICATORS ---
    sma_200d = get_sma("^GSPC", 200)
    tnx_200ma = get_sma("^TNX", 200)
    btc_200ma = get_sma("BTC-USD", 200)
    avg_rsi = (calculate_rsi("^GSPC") + calculate_rsi("QQQ") + calculate_rsi("VXUS")) / 3

    # --- 6 PILLARS OVERLAY (FULLY AUTOMATED) ---
    cols = st.columns(6)
    
    # 1. Momentum
    m_stat = "🟢 BULLISH" if spx_now > sma_200d else "🔴 BEARISH"
    cols[0].metric("Momentum", m_stat, f"{((spx_now/sma_200d)-1)*100:+.1f}% vs 200D")

    # 2. Inflation
    inf_val = gold_now / dbc_now if dbc_now > 0 else 0
    cols[1].metric("Inflation", "🔴 HIGH" if inf_val > 1.1 else "🟢 STABLE", "Gold/DBC Ratio")

    # 3. Growth
    gro_val = xlb_now / gold_now if gold_now > 0 else 0
    cols[2].metric("Growth", "🟢 EXPAND" if gro_val > 0.015 else "🟡 SLOWING", "Materials vs Gold")
    
    # 4. Positioning
    p_stat = "🔴 HEAVY" if vix_now > 30 else "🟡 NEUTRAL" if vix_now > 20 else "🟢 LITE"
    cols[3].metric("Positioning", p_stat, f"VIX {vix_now:.1f}")

    # 5. Monetary
    cols[4].metric("Monetary", "🔴 TIGHT" if (tnx_now - short_rate) < 0 else "🟢 EASING", f"Spread: {tnx_now-short_rate:.2f}%")

    # 6. Fiscal
    cols[5].metric("Fiscal", "🔴 STRESS" if tnx_now > tnx_200ma * 1.1 else "🟢 STABLE", "Yield vs 200D MA")

    st.divider()

    # --- ASSET CLASS SCORECARD ---
    st.subheader("🎯 Asset Class Scorecard")
    s_cols = st.columns(5)
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

    # --- SECTOR PERFORMANCE & RSI HEATMAP ---
    daily_data, weekly_data, monthly_data, ytd_data, s_rsis, s_names = get_sector_leaderboard()
    if s_rsis:
        st.subheader("📊 Sector Performance & RSI Heatmap")
        heat_cols = st.columns(11)
        for i, (t, r) in enumerate(s_rsis.items()):
            c = "🔴" if r > 70 else ("🔵" if r < 30 else "⚪")
            heat_cols[i].metric(s_names[t], f"{r:.0f}", c)
        
        st.write("---")
        l_cols = st.columns(4)
        timeframes = [("Daily", daily_data), ("Weekly", weekly_data), ("Monthly", monthly_data), ("Year-to-Date", ytd_data)]
        for i, (name, data) in enumerate(timeframes):
            with l_cols[i]:
                st.write(f"**{name} Leaders**")
                for item in data[0]: st.write(f"🟢 {item}")
                st.write(f"**{name} Laggards**")
                for item in data[1]: st.write(f"🔴 {item}")

    st.divider()

    # --- DEEP DIVES ---
    col_left, col_right = st.columns(2)
    with col_left:
        with st.expander("🔍 Momentum & Trend Layers", expanded=True):
            st.write(f"**S&P 500:** {spx_now:,.2f} | **200-MA:** {sma_200d:,.2f}")
            st.write(f"**Bitcoin:** ${btc_now:,.2f} | **200-MA:** ${btc_200ma:,.2f}")

        with st.expander("🌍 Geopolitical Intelligence Agent", expanded=True):
            world_news = get_news_feed("https://feeds.bbci.co.uk/news/world/rss.xml")
            for entry in world_news or []: st.markdown(f"- [{entry['title']}]({entry['link']})")

    with col_right:
        with st.expander("🌊 Liquidity & Yields", expanded=True):
            st.write(f"**Dollar Index:** {dxy_now:.2f}")
            st.write(f"**10Y/3M Spread:** {tnx_now - short_rate:.2f}%")

        with st.expander("💰 Finance Headlines", expanded=True):
            cnbc_news = get_news_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114")
            for entry in cnbc_news or []: st.markdown(f"- [{entry['title']}]({entry['link']})")

# --- 2. HYBRID AUTOMATED ALPHA TAB ---
with tab_alpha:
    st.header("🕵️ Unusual Congressional Alpha Agent (Live)")
    FMP_API_KEY = "6sG3kEmPzwx6pzFxdyarM7weg4jvSEFw"
    
    @st.cache_data(ttl=3600)
    def get_hybrid_trades(api_key):
        persistent_memory = [
            {"Politician": "Tim Moore (R)", "Ticker": "GNPX", "Company": "Genprex, Inc.", "Date": "2026-02-05", "Amount": "$1k-$15k", "Rationale": "🔴 Micro-cap Biotech"},
            {"Politician": "Jonathan Jackson (D)", "Ticker": "GEV", "Company": "GE Vernova Inc.", "Date": "2026-01-30", "Amount": "$15k-$50k", "Rationale": "🟠 Infrastructure"}
        ]
        try:
            h_url = f"https://financialmodelingprep.com/api/v3/house-disclosure?apikey={api_key}"
            live_data = requests.get(h_url).json()
            live_unusual = []
            for t in live_data[:20]:
                sym = t.get('symbol', 'N/A')
                if len(sym) < 6:
                    live_unusual.append({"Politician": f"{t.get('firstName')} {t.get('lastName')}", "Ticker": sym, "Company": t.get('assetDescription', 'N/A')[:35], "Date": t.get('transactionDate'), "Amount": t.get('amount'), "Rationale": "🟠 Live Filing"})
            combined = pd.DataFrame(live_unusual + persistent_memory)
            return combined.drop_duplicates(subset=['Politician', 'Ticker']).head(10)
        except: return pd.DataFrame(persistent_memory)

    df_alpha = get_hybrid_trades(FMP_API_KEY)
    st.dataframe(df_alpha, use_container_width=True, hide_index=True)

# --- 3. PORTFOLIO LAB ---
with tab_lab:
    st.header("📈 Lazy Portfolio Performance Lab")
    all_p_tickers = list(set([t for p in PORTFOLIOS.values() for t in p.keys()]))
    
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
    perf_list = []
    if p_prices:
        for name, weights in PORTFOLIOS.items():
            ytd_perf = sum(((p_prices[t]["current"] / p_prices[t]["ytd_start"]) - 1) * w for t, w in weights.items() if t in p_prices)
            perf_list.append({"Portfolio Design": name, "Tickers": ", ".join(weights.keys()), "YTD %": round(ytd_perf * 100, 2)})
        st.dataframe(pd.DataFrame(perf_list).sort_values(by="YTD %", ascending=False), use_container_width=True, hide_index=True)

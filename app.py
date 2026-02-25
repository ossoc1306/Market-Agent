import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

# --- 1. TABS: WRAPPING THE ENTIRE APP ---
tab_terminal, tab_alpha = st.tabs(["🛡️ Multi-Asset Terminal", "🕵️ Unusual Congressional Alpha"])

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
        except:
            return 0.0

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
        except:
            return 50.0

    @st.cache_data(ttl=600)
    def get_sma(ticker, window):
        try:
            d = yf.download(ticker, period="2y", progress=False)
            return d['Close'].rolling(window=window).mean().iloc[-1].item()
        except:
            return 0.0

    @st.cache_data(ttl=300)
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

    # Fetch Core Data
    spx_now = get_safe_data("^GSPC")
    qqq_now = get_safe_data("QQQ")
    vxus_now = get_safe_data("VXUS")
    vix_now = get_safe_data("^VIX")
    tnx_now = get_safe_data("^TNX")
    short_rate = get_safe_data("^IRX")
    dxy_now = get_safe_data("DX-Y.NYB")
    btc_now = get_safe_data("BTC-USD")
    gold_now = get_safe_data("GC=F")

    # Indicators
    sma_200d = get_sma("^GSPC", 200)
    btc_200ma = get_sma("BTC-USD", 200)
    spx_rsi_d = calculate_rsi("^GSPC")
    spx_rsi_w = calculate_rsi("^GSPC", "1wk")
    qqq_rsi_d = calculate_rsi("QQQ")
    vxus_rsi_d = calculate_rsi("VXUS")
    avg_rsi = (spx_rsi_d + qqq_rsi_d + vxus_rsi_d) / 3

    # --- 6 PILLARS OVERLAY ---
    cols = st.columns(6)
    mom_val = ((spx_now/sma_200d)-1)*100 if sma_200d > 0 else 0
    mom_color = "🟢" if mom_val > 0 else "🔴"
    cols[0].metric("Momentum", f"{mom_color} BULLISH", f"{mom_val:+.1f}% vs 200D")
    cols[1].metric("Inflation", "🟡 2.40%", "PCE Sticky at 3%")
    cols[2].metric("Growth", "🟡 1.40%", "Q4 Slowdown")
    cols[3].metric("Positioning", "🟢 LITE", f"VIX {vix_now:.1f}")
    cols[4].metric("Monetary", "🟡 6.75%", "Prime Rate")
    cols[5].metric("Fiscal", "🔴 DEFICIT", "Duration Mix ↑")

    st.divider()

    # --- ASSET CLASS SCORECARD ---
    st.subheader("🎯 Asset Class Scorecard")
    s_cols = st.columns(5)
    def get_rating(green_cond, red_cond):
        if green_cond: return "🟢 BULLISH"
        if red_cond: return "🔴 BEARISH"
        return "🟡 NEUTRAL"

    stocks_rating = get_rating(spx_now > sma_200d and avg_rsi < 65, spx_now < sma_200d or avg_rsi > 75)
    crypto_rating = get_rating(btc_now > btc_200ma and dxy_now < 105, btc_now < btc_200ma or dxy_now > 107)
    gold_rating = get_rating(gold_now/spx_now > 0.7 or avg_rsi < 45, dxy_now > 108)
    bonds_rating = get_rating(tnx_now > short_rate, tnx_now < short_rate)
    re_rating = get_rating(calculate_rsi("XLRE") < 40, calculate_rsi("XLRE") > 70)

    s_cols[0].metric("Stocks", stocks_rating)
    s_cols[1].metric("Bonds", bonds_rating)
    s_cols[2].metric("Gold", gold_rating)
    s_cols[3].metric("Crypto", crypto_rating)
    s_cols[4].metric("Real Estate", re_rating)

    st.divider()

    # --- MARKET TEMPERATURE ---
    st.subheader("🌡️ Market Temperature & Sentiment Gauge")
    if avg_rsi > 70: status, color = "EXTREME GREED / OVERBOUGHT", "🔴"
    elif avg_rsi > 60: status, color = "GREED", "🟠"
    elif avg_rsi < 30: status, color = "EXTREME FEAR / OVERSOLD", "🔵"
    elif avg_rsi < 40: status, color = "FEAR", "🟡"
    else: status, color = "NEUTRAL", "🟢"
    st.markdown(f"### {color} Current Regime: **{status}** (Avg RSI: {avg_rsi:.1f})")

    st.divider()

    # --- SECTOR PERFORMANCE ---
    st.subheader("📊 Sector Performance & RSI Heatmap")
    daily_data, weekly_data, monthly_data, ytd_data, s_rsis, s_names = get_sector_leaderboard()
    if s_rsis:
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
            st.write(f"**S&P 500 (SPX)**: {spx_now:,.2f}")
            st.write(f"**Nasdaq (QQQ)**: {qqq_now:,.2f}")
        with st.expander("📊 Inflation & Growth", expanded=True):
            st.write("**Core PCE:** 3.0% YoY")
            st.write("**GDP Growth:** 1.4%")
        with st.expander("₿ Crypto Agent", expanded=True):
            st.write(f"**BTC Price:** ${btc_now:,.2f}")

    with col_right:
        with st.expander("🌊 Liquidity Agent", expanded=True):
            st.write(f"**Dollar Index (DXY):** {dxy_now:.2f}")
        with st.expander("✨ Gold Agent", expanded=True):
            st.write(f"**Gold Price:** ${gold_now:,.2f}")
        with st.expander("🏦 Yield Curve", expanded=True):
            st.write(f"**10-Year Yield:** {tnx_now:.2f}%")

    st.divider()

    # --- GEOPOLITICAL AGENT ---
    st.subheader("🌍 Geopolitical Intelligence Agent (Live Feed)")
    geo_left, geo_right = st.columns(2)
    with geo_left:
        st.write("**🌍 Global Headlines (BBC World News)**")
        world_news = get_news_feed("https://feeds.bbci.co.uk/news/world/rss.xml")
        for entry in world_news or []: st.markdown(f"- [{entry['title']}]({entry['link']})")
    with geo_right:
        st.write("**💰 Market & Finance Headlines (CNBC)**")
        cnbc_news = get_news_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114")
        for entry in cnbc_news or []: st.markdown(f"- [{entry['title']}]({entry['link']})")

    st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: Yahoo Finance, BBC, CNBC")


# --- 2. HYBRID AUTOMATED ALPHA TAB ---
with tab_alpha:
    st.header("🕵️ Unusual Congressional Alpha Agent (Live)")
    st.markdown("""
    *Target: Top 10 Niche/Small-Cap trades. Older trades are filtered out as new filings are detected.*
    """)

    # --- HYBRID API + CACHE AGENT LOGIC ---
    @st.cache_data(ttl=3600) # Hourly refresh
    def get_hybrid_trades(api_key):
        # 1. Base "Persistent Memory" for when API has no new niche results
        persistent_memory = [
            {"Politician": "Tim Moore (R)", "Ticker": "GNPX", "Company": "Genprex, Inc.", "Date": "2026-02-05", "Amount": "$1,001 - $15,000", "Insight": "🔴 Micro-cap Biotech (<$10M cap)."},
            {"Politician": "Jonathan Jackson (D)", "Ticker": "GEV", "Company": "GE Vernova Inc.", "Date": "2026-01-30", "Amount": "$15,001 - $50,000", "Insight": "🟠 Infrastructure Spin-off. Non-index."},
            {"Politician": "Tim Moore (R)", "Ticker": "SMPL", "Company": "Simply Good Foods", "Date": "2026-02-11", "Amount": "$15,001 - $50,000", "Insight": "⚪ Specialized nutritional brands."},
            {"Politician": "Michael Guest (R)", "Ticker": "CHRD", "Company": "Chord Energy", "Date": "2026-01-09", "Amount": "$1,001 - $15,000", "Insight": "⚪ Localized shale oil producer."},
            {"Politician": "Tim Moore (R)", "Ticker": "DNUT", "Company": "Krispy Kreme Inc.", "Date": "2026-02-12", "Amount": "$1,001 - $15,000", "Insight": "⚪ Specific brand-heavy consumer pick."}
        ]
        
        try:
            # 2. Fetch Latest Filings
            h_url = f"https://financialmodelingprep.com/api/v3/house-disclosure?apikey={api_key}"
            s_url = f"https://financialmodelingprep.com/api/v3/senate-disclosure?apikey={api_key}"
            
            h_data = requests.get(h_url).json()
            s_data = requests.get(senate_url).json()
            all_raw = (h_data if isinstance(h_data, list) else []) + (s_data if isinstance(s_data, list) else [])
            
            # Filter Logic: Exclude Mega-Caps & Broad S&P 500 names
            mega_caps = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B", "V", "JPM", "WMT"]
            
            live_unusual = []
            for t in all_raw[:60]: # Scan recent 60
                sym = t.get('symbol', 'N/A')
                if sym not in mega_caps and sym != 'N/A' and len(sym) < 6:
                    live_unusual.append({
                        "Politician": f"{t.get('firstName', '')} {t.get('lastName', '')}",
                        "Ticker": sym,
                        "Company": t.get('assetDescription', 'N/A')[:35] + "...",
                        "Date": t.get('transactionDate', 'N/A'),
                        "Amount": t.get('amount', 'N/A'),
                        "Insight": "🟠 Live Niche Filing Detected"
                    })
            
            # 3. Merge, Clean, and Truncate to Top 10
            combined_df = pd.DataFrame(live_unusual + persistent_memory)
            # Drop duplicates based on Politician + Ticker
            combined_df = combined_df.drop_duplicates(subset=['Politician', 'Ticker'], keep='first')
            # Sort by Date descending
            combined_df = combined_df.sort_values(by="Date", ascending=False)
            return combined_df.head(10)
            
        except:
            return pd.DataFrame(persistent_memory)

    # --- API KEY INTEGRATED ---
    FMP_API_KEY = "6sG3kEmPzwx6pzFxdyarM7weg4jvSEFw"
    
    final_trades = get_hybrid_trades(FMP_API_KEY)
    
    if not final_trades.empty:
        st.dataframe(
            final_trades, 
            use_container_width=True, 
            hide_index=True,
            column_config={"Insight": st.column_config.TextColumn("Agent Rationale", width="large")}
        )
    else:
        st.info("Agent is scanning for new unusual niche filings...")

    st.divider()
    st.subheader("🚨 Significant Macro Exit Alerts")
    st.warning("**Agent Update:** Monitoring for liquidations over $1M (e.g., [Dave McCormick/GS](https://market-agent-vinovkctutaoxrxbkk3lrp.streamlit.app/)) in primary sector leaders to identify institutional distribution.")

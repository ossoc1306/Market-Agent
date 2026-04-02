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

# --- 1. TABS NAVIGATION ---
tab_terminal, tab_alpha, tab_lab = st.tabs(["🛡️ Multi-Asset Terminal", "🕵️ Unusual Congressional Alpha", "📈 Portfolio Lab"])

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

    # --- INDICATORS ---
    sma_200d = get_sma("^GSPC", 200)
    btc_200ma = get_sma("BTC-USD", 200)
    spx_rsi_d = calculate_rsi("^GSPC")
    spx_rsi_w = calculate_rsi("^GSPC", "1wk")
    qqq_rsi_d = calculate_rsi("QQQ")
    vxus_rsi_d = calculate_rsi("VXUS")
    avg_rsi = (spx_rsi_d + qqq_rsi_d + vxus_rsi_d) / 3

    # --- 6 PILLARS OVERLAY ---
    cols = st.columns(6)
    
    # MOMENTUM UPDATE: Bullish if Price > 200D MA, Bearish otherwise
    if sma_200d > 0:
        mom_status = "BULLISH" if spx_now > sma_200d else "BEARISH"
        mom_color = "🟢" if spx_now > sma_200d else "🔴"
        mom_val = ((spx_now/sma_200d)-1)*100
    else:
        mom_status = "DATA PENDING"
        mom_color = "⚪"
        mom_val = 0.0

    cols[0].metric("Momentum", f"{mom_color} {mom_status}", f"{mom_val:+.1f}% vs 200D")
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
        st.caption("RSI Heatmap Key: 🔴 Overbought (>70) | 🔵 Oversold (<30) | ⚪ Neutral")

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
        with st.expander("🔍 Momentum & Trend Layers (SPX, QQQ, VXUS)", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write("**S&P 500 (SPX)**")
                st.write(f"Price: {spx_now:,.2f}")
                st.write(f"Daily RSI: {spx_rsi_d:.1f} | Weekly: {spx_rsi_w:.1f}")
                st.write(f"200-MA: {sma_200d:,.2f}")
            with c2:
                st.write("**Nasdaq (QQQ)**")
                st.write(f"Price: {qqq_now:,.2f}")
                st.write(f"Daily RSI: {qqq_rsi_d:.1f} | Weekly: {calculate_rsi('QQQ', '1wk'):.1f}")
            with c3:
                st.write("**International (VXUS)**")
                st.write(f"Price: {vxus_now:,.2f}")
                st.write(f"Daily RSI: {vxus_rsi_d:.1f} | Weekly: {calculate_rsi('VXUS', '1wk'):.1f}")

        with st.expander("₿ Crypto Intelligence Agent (BTC, ETH, SOL)", expanded=True):
            cryptos = {"Bitcoin (BTC)": "BTC-USD", "Ethereum (ETH)": "ETH-USD", "Solana (SOL)": "SOL-USD"}
            c_cols = st.columns(3)
            for i, (name, ticker) in enumerate(cryptos.items()):
                price = get_safe_data(ticker)
                dr = calculate_rsi(ticker, "1d")
                wr = calculate_rsi(ticker, "1wk")
                with c_cols[i]:
                    st.write(f"**{name}**")
                    st.write(f"Price: ${price:,.2f}")
                    st.write(f"Daily RSI: {dr:.1f} | Weekly: {wr:.1f}")

    with col_right:
        with st.expander("🌊 Liquidity Watch Agent", expanded=True):
            st.write(f"**Dollar Index (DXY):** {dxy_now:.2f}")

        with st.expander("✨ Gold Intelligence Agent", expanded=True):
            st.write(f"**Current Gold Price:** ${gold_now:,.2f}")
            st.write(f"**Gold/SPX Ratio:** {gold_now/spx_now if spx_now > 0 else 0:.4f}")

        with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
            st.write(f"**10-Year Benchmark:** {tnx_now:.2f}%")
            st.write(f"**10Y/3M Spread:** {tnx_now - short_rate:.2f}%")

    st.divider()

    # --- GEOPOLITICAL AGENT ---
    st.subheader("🌍 Geopolitical Intelligence Agent (Live Feed)")
    geo_left, geo_right = st.columns(2)
    with geo_left:
        st.write("**🌍 Global Headlines (BBC)**")
        world_news = get_news_feed("https://feeds.bbci.co.uk/news/world/rss.xml")
        for entry in world_news or []: st.markdown(f"- [{entry['title']}]({entry['link']})")
    with geo_right:
        st.write("**💰 Finance Headlines (CNBC)**")
        cnbc_news = get_news_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114")
        for entry in cnbc_news or []: st.markdown(f"- [{entry['title']}]({entry['link']})")

# --- 2. HYBRID ALPHA TAB ---
with tab_alpha:
    st.header("🕵️ Unusual Congressional Alpha Agent (Live)")
    # (Original Alpha code follows here...)

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
    # (Original Performance Lab calculation and table follow here...)

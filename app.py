import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import requests
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Multi-Asset Terminal", layout="wide")

# --- PORTFOLIO DEFINITIONS (Updated with Historical, Regime & Yield Data) ---
PORTFOLIOS = {
    "All-Weather (Dalio)": {
        "weights": {"VTI": 0.30, "TLT": 0.40, "IEF": 0.15, "GLD": 0.075, "DBC": 0.075},
        "hist_ret": "6.0%", "stag_pot": "High", "est_yield": 2.1
    },
    "60/40 Portfolio": {
        "weights": {"VTI": 0.60, "BND": 0.40},
        "hist_ret": "8.4%", "stag_pot": "Low", "est_yield": 2.8
    },
    "Fugger Portfolio": {
        "weights": {"VTI": 0.25, "VNQ": 0.25, "BND": 0.25, "GLD": 0.25},
        "hist_ret": "6.1%", "stag_pot": "High", "est_yield": 2.4
    },
    "Permanent Portfolio": {
        "weights": {"VTI": 0.25, "TLT": 0.25, "BIL": 0.25, "GLD": 0.25},
        "hist_ret": "5.9%", "stag_pot": "High", "est_yield": 2.2
    },
    "Golden Butterfly": {
        "weights": {"VTI": 0.20, "IJS": 0.20, "TLT": 0.20, "SHV": 0.20, "GLD": 0.20},
        "hist_ret": "7.2%", "stag_pot": "High", "est_yield": 2.3
    },
    "Three-Fund": {
        "weights": {"VTI": 0.34, "VXUS": 0.33, "BND": 0.33},
        "hist_ret": "8.9%", "stag_pot": "Low", "est_yield": 2.6
    },
    "Coffeehouse": {
        "weights": {"VOO": 0.10, "IJS": 0.10, "IJV": 0.10, "VEA": 0.10, "VNQ": 0.10, "VIG": 0.10, "AGG": 0.40},
        "hist_ret": "8.2%", "stag_pot": "Low-Mod", "est_yield": 2.9
    },
    "Ivy League (Swensen)": {
        "weights": {"VTI": 0.30, "VEA": 0.15, "VWO": 0.05, "VNQ": 0.20, "IEF": 0.15, "TIP": 0.15},
        "hist_ret": "7.5%", "stag_pot": "Moderate", "est_yield": 3.1
    },
    "Warren Buffett": {
        "weights": {"VOO": 0.90, "BIL": 0.10},
        "hist_ret": "11.2%", "stag_pot": "Low", "est_yield": 1.7
    },
    "Global Asset Allocation": {
        "weights": {"VTI": 0.18, "VEA": 0.135, "VWO": 0.045, "LQD": 0.18, "TLT": 0.18, "GLD": 0.10, "DBC": 0.10, "VNQ": 0.08},
        "hist_ret": "7.8%", "stag_pot": "Moderate", "est_yield": 2.5
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
tab_terminal, tab_lab, tab_rebalance, tab_architect, tab_rotation = st.tabs([
    "🛡️ Multi-Asset Terminal", 
    "📈 Portfolio Lab", 
    "⚖️ Rebalance & Income",
    "🔬 Strategy Architect",
    "🔄 Rotation Radar"
])

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

    # --- INDICATORS & NEW FAST AVERAGES ---
    sma_200d = get_sma("^GSPC", 200)
    sma_20d = get_sma("^GSPC", 20)  # Fast trend for breakdown confirmation
    tnx_200ma = get_sma("^TNX", 200)
    btc_200ma = get_sma("BTC-USD", 200)
    avg_rsi = (calculate_rsi("^GSPC") + calculate_rsi("QQQ") + calculate_rsi("VXUS")) / 3
    
    # --- NEW BOND & REAL ESTATE PRICING ---
    tlt_now = get_safe_data("TLT")
    tlt_200ma = get_sma("TLT", 200)
    xlre_now = get_safe_data("XLRE")
    xlre_200ma = get_sma("XLRE", 200)
    xlre_20ma = get_sma("XLRE", 20)
    xlre_rsi = calculate_rsi("XLRE")
    
    # --- NEW GOLD DYNAMIC AVERAGES ---
    gold_50ma = get_sma("GC=F", 50)
    gold_200ma = get_sma("GC=F", 200)

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
    
    # Updated to prioritize risk: If a red condition triggers, it overrides the green.
    def get_rating(green_cond, red_cond):
        if red_cond: return "🔴 BEARISH"
        if green_cond: return "🟢 BULLISH"
        return "🟡 NEUTRAL"

    # Stocks: Bearish only if below 200MA OR (RSI is wildly overbought AND price breaks the 20-day MA).
    sc[0].metric("Stocks", get_rating(
        green_cond=spx_now > sma_200d, 
        red_cond=spx_now < sma_200d or (avg_rsi > 80 and spx_now < sma_20d)
    ))

    # Bonds: Tracks actual TLT price vs 200MA. Small 2% buffer on the downside to prevent fake-outs.
    sc[1].metric("Bonds", get_rating(
        green_cond=tlt_now > tlt_200ma, 
        red_cond=tlt_now < tlt_200ma * 0.98
    ))

    # Gold: Dynamic guardrails using 50MA and 200MA instead of static ratios.
    sc[2].metric("Gold", get_rating(
        green_cond=gold_now > gold_50ma, 
        red_cond=gold_now < gold_200ma
    ))

    # Crypto: Requires a 5% crash through the 200MA to flash red, accommodating for high volatility.
    sc[3].metric("Crypto", get_rating(
        green_cond=btc_now > btc_200ma, 
        red_cond=btc_now < btc_200ma * 0.95
    ))

    # Real Estate: Price vs 200MA, with a breakdown trigger similar to stocks.
    sc[4].metric("Real Estate", get_rating(
        green_cond=xlre_now > xlre_200ma, 
        red_cond=xlre_now < xlre_200ma or (xlre_rsi > 80 and xlre_now < xlre_20ma)
    ))

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

# --- TAB 2: PORTFOLIO LAB ---
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

# --- TAB 3: REBALANCE & INCOME SECTION ---
with tab_rebalance:
    st.header("⚖️ Rebalance & Income Projection")
    st.write("Define your target portfolio size to automatically see the suggested construction.")
    
    col_input, col_stats = st.columns([2, 1])
    
    with col_input:
        target_strategy = st.selectbox("Select Strategy to Analyze", list(PORTFOLIOS.keys()))
        target_weights = PORTFOLIOS[target_strategy]["weights"]
        
        st.subheader("Portfolio Configuration")
        total_portfolio_value = st.number_input(
            "Target Total Portfolio Value ($)", 
            min_value=0.0, 
            value=25000.0, 
            step=1000.0,
            help="The total amount you want invested across this strategy."
        )
        
        st.write("---")
        st.subheader("Actual Holdings")
        st.info("The fields below are auto-populated with the ideal amounts for a balanced portfolio. Overwrite them with your actual balances to see required trades.")
        
        current_vals = {}
        input_cols = st.columns(3)
        
        for i, (ticker, weight) in enumerate(target_weights.items()):
            suggested_amount = total_portfolio_value * weight
            current_vals[ticker] = input_cols[i % 3].number_input(
                f"Actual {ticker} ($)", 
                min_value=0.0, 
                value=float(suggested_amount), 
                step=100.0
            )
    
    portfolio_yield_pct = PORTFOLIOS[target_strategy]["est_yield"]
    annual_income = total_portfolio_value * (portfolio_yield_pct / 100)

    with col_stats:
        st.subheader("💰 Income Projection")
        st.metric("Target Portfolio Value", f"${total_portfolio_value:,.2f}")
        st.metric("Est. Annual Income", f"${annual_income:,.2f}", f"{portfolio_yield_pct}% Yield")
        st.write(f"**Monthly Average:** ${annual_income/12:,.2f}")
        st.caption("Note: Yields are based on trailing twelve-month (TTM) averages.")

    st.divider()
    
    st.subheader("🛠️ Rebalancing & Construction Plan")
    rebalance_data = []
    for ticker, weight in target_weights.items():
        target_val = total_portfolio_value * weight
        actual_val = current_vals[ticker]
        diff = target_val - actual_val
        
        if abs(diff) < 1.0:
            action = "✅ Balanced"
        elif diff > 0:
            action = f"🟢 BUY ${diff:,.2f}"
        else:
            action = f"🔴 SELL ${abs(diff):,.2f}"
            
        rebalance_data.append({
            "Asset": ticker,
            "Target Allocation": f"{weight*100:.1f}%",
            "Current Allocation": f"{(actual_val/total_portfolio_value)*100:.1f}%" if total_portfolio_value > 0 else "0%",
            "Current Value": f"${actual_val:,.2f}",
            "Target Value (Ideal)": f"${target_val:,.2f}",
            "Required Action": action
        })
    
    st.table(pd.DataFrame(rebalance_data))

# --- TAB 4: STRATEGY ARCHITECT (Final Version with Correlation Matrix) ---
with tab_architect:
    st.header("🔬 Custom Strategy & Stress Test")
    
    REGIMES = {
        "2008 Housing Crisis": {
            "dates": ("2007-10-01", "2009-03-09"),
            "summary": "The Great Recession triggered by the housing collapse. S&P 500 fell ~50%."
        },
        "2020 COVID Crash": {
            "dates": ("2020-02-19", "2020-03-23"),
            "summary": "Swift bear market due to global lockdowns. Market bottomed after Fed intervention."
        },
        "2022 Rate Hike Shock": {
            "dates": ("2022-01-01", "2022-12-31"),
            "summary": "Stocks and bonds crashed as the Fed fought 40-year high inflation."
        },
        "Bull Market Run (Recent)": {
            "dates": ("2023-01-01", datetime.now().strftime("%Y-%m-%d")),
            "summary": "Defined by the AI Revolution. Tech led most of the gains."
        }
    }

    col_build, col_dates = st.columns([2, 1])

    with col_build:
        st.subheader("🛠️ Build Your Tickers")
        custom_tickers_raw = st.text_input("Enter Tickers (comma separated)", value="XLE, QQQ, GLD, BND")
        custom_tickers = [t.strip().upper() for t in custom_tickers_raw.split(",") if t.strip()]
        
        st.write("Assign Weights (Must sum to 100%)")
        c_weight_cols = st.columns(len(custom_tickers) if custom_tickers else 1)
        custom_weights = {}
        for i, ticker in enumerate(custom_tickers):
            custom_weights[ticker] = c_weight_cols[i].number_input(f"{ticker} %", min_value=0, max_value=100, value=100//len(custom_tickers))
        
        total_w = sum(custom_weights.values())
        
        benchmark_choice = st.selectbox(
            "Compare against Benchmark:", 
            ["S&P 500 (SPY)", "Nasdaq 100 (QQQ)", "Bitcoin (BTC-USD)", "None"]
        )
        benchmark_map = {"S&P 500 (SPY)": "SPY", "Nasdaq 100 (QQQ)": "QQQ", "Bitcoin (BTC-USD)": "BTC-USD"}

    with col_dates:
        st.subheader("📅 Select Timeframe")
        # Streamlit date_input returns a tuple for ranges. 
        date_range = st.date_input("Select Start and End Dates", value=(datetime(2020, 1, 1), datetime.now()))
        
        st.write("---")
        st.caption("Quick Select Historical Regimes:")
        quick_regime = st.selectbox("Apply Preset Range:", ["Custom"] + list(REGIMES.keys()))
        
        # Initialize variables
        start_date = None
        end_date = None

        if quick_regime != "Custom":
            start_date, end_date = REGIMES[quick_regime]["dates"]
            st.info(f"**Market Context:** {REGIMES[quick_regime]['summary']}")
        # Check if selection is complete (tuple length 2)
        elif isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            # Selection is in progress
            start_date = None
            end_date = None

    if st.button("🚀 Run Stress Test"):
        if total_w != 100:
            st.error(f"⚠️ Total weight must be exactly 100%. Your current total is **{total_w}%**.")
        elif not custom_tickers:
            st.error("⚠️ Please enter at least one ticker symbol.")
        elif start_date is None or end_date is None:
            st.warning("⚠️ Please select a full date range (click both start and end dates on the calendar).")
        else:
            with st.spinner(f"Analyzing strategy performance..."):
                try:
                    tickers_to_fetch = list(set(custom_tickers + ([benchmark_map[benchmark_choice]] if benchmark_choice != "None" else [])))
                    raw_data = yf.download(tickers_to_fetch, start=start_date, end=end_date, progress=False)
                    data = raw_data['Close'] if 'Close' in raw_data.columns else raw_data

                    if data.empty:
                        st.error("No historical data found for these tickers.")
                    else:
                        # 1. Calculations
                        returns = data[custom_tickers].pct_change().dropna()
                        weights_arr = [custom_weights[t]/100 for t in custom_tickers]
                        port_returns = (returns * weights_arr).sum(axis=1)
                        cumulative_growth = (1 + port_returns).cumprod() * 100
                        
                        # 2. Metrics
                        port_vol = port_returns.std() * (252**0.5) * 100
                        port_perf = (cumulative_growth.iloc[-1] - 100)
                        max_dd = ((cumulative_growth / cumulative_growth.cummax()) - 1).min() * 100
                        rf_daily = 0.02 / 252
                        sharpe_ratio = ((port_returns - rf_daily).mean() / port_returns.std()) * (252**0.5) if port_returns.std() != 0 else 0
                        
                        # 3. Display Metrics
                        m1, m2, m3, m4, m5 = st.columns(5)
                        m1.metric("Strategy Return", f"{port_perf:+.2f}%")
                        m2.metric("Max Drawdown", f"{max_dd:.2f}%", delta_color="inverse")
                        m3.metric("Volatility Score", f"{port_vol:.1f}%", help="Avg S&P Vol is 15-18%.")
                        m4.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}", help="Risk-adjusted return.")

                        plot_df = pd.DataFrame({"Your Strategy": cumulative_growth}, index=cumulative_growth.index)
                        if benchmark_choice != "None":
                            bench_ticker = benchmark_map[benchmark_choice]
                            bench_growth = (1 + data[bench_ticker].pct_change().dropna()).cumprod() * 100
                            plot_df[f"Benchmark ({bench_ticker})"] = bench_growth
                            m5.metric(f"vs {benchmark_choice.split(' ')[0]}", f"{(port_perf - (bench_growth.iloc[-1]-100)):+.2f}%")

                        with st.expander("🎓 What is the Sharpe Ratio? (Novice Guide)"):
                            st.write("The Sharpe Ratio measures if your returns are worth the risk. Scores above 1.0 are good; 2.0+ is excellent.")

                        st.line_chart(plot_df)
                        
                        st.subheader("📊 Individual Asset Performance")
                        asset_perf = {t: ((data[t].iloc[-1] / data[t].iloc[0]) - 1) * 100 for t in custom_tickers}
                        st.bar_chart(pd.DataFrame.from_dict(asset_perf, orient='index', columns=['Return %']))

                        # --- NEW: CORRELATION MATRIX SECTION ---
                        st.divider()
                        st.subheader("🔗 Diversification Check: Correlation Matrix")
                        
                        corr_matrix = returns.corr()
                        st.write("This table shows how closely your assets move together (1.0 is a perfect match).")
                        
                        # Apply a heatmap style for easy reading
                        st.dataframe(corr_matrix.style.format("{:.2f}"))

                        with st.expander("🎓 What is Correlation? (Novice Guide)"):
                            st.write("""
                            **Correlation** measures how much two assets move in the same direction at the same time:
                            * **1.0 (Red):** Perfect Correlation. If one crashes, the other likely will too.
                            * **0.0 (Yellow):** No Correlation. These assets move independently. 
                            * **Negative (Green):** Inverse Correlation. When one goes down, the other goes up.
                            
                            **Strategy Tip:** To build a safer portfolio, look for assets with **Low (0.0 to 0.4)** or **Negative** correlation.
                            """)
                        
                except Exception as e:
                    st.error(f"Calculation Error: {str(e)}")

# --- TAB 5: SECTOR ROTATION RADAR (Exhaustion & Multi-Month Seasonality) ---
with tab_rotation:
    st.header("🔄 Sector Rotation Radar")
    st.write("Measure technical exhaustion and forward-looking historical seasonality to anticipate capital rotation.")
    
    # --- ROTATION DATA FUNCTIONS ---
    @st.cache_data(ttl=3600)
    def get_technical_exhaustion(ticker):
        try:
            df = yf.download(ticker, period="1y", progress=False)['Close']
            if df.empty: return None
            
            # Calculate 50-day Moving Average and Standard Deviation
            sma_50 = df.rolling(window=50).mean()
            std_50 = df.rolling(window=50).std()
            
            current_price = float(df.iloc[-1].squeeze())
            current_sma = float(sma_50.iloc[-1].squeeze())
            current_std = float(std_50.iloc[-1].squeeze())
            
            if current_std == 0: return None
            
            # Z-Score Calculation (Rubber Band Stretch)
            z_score = (current_price - current_sma) / current_std
            return current_price, current_sma, z_score
        except: return None

    @st.cache_data(ttl=3600)
    def get_seasonality(ticker):
        try:
            # Pull 10 years of data for deep historical context
            df = yf.download(ticker, period="10y", progress=False)['Close']
            if df.empty: return None
            
            # Resample to monthly and calculate month-over-month returns
            monthly_data = df.resample('ME').last()
            monthly_returns = monthly_data.pct_change() * 100
            
            now = datetime.now()
            curr_m = now.month
            curr_name = now.strftime('%B')
            
            next_m = 1 if curr_m == 12 else curr_m + 1
            next_name = datetime.strptime(str(next_m), "%m").strftime('%B')
            
            # Isolate historical data for current and next month
            curr_returns = monthly_returns[monthly_returns.index.month == curr_m].dropna()
            next_returns = monthly_returns[monthly_returns.index.month == next_m].dropna()
            
            if curr_returns.empty or next_returns.empty: return None
            
            curr_win = float((curr_returns > 0).mean().squeeze()) * 100
            curr_avg = float(curr_returns.mean().squeeze())
            
            next_win = float((next_returns > 0).mean().squeeze()) * 100
            next_avg = float(next_returns.mean().squeeze())
            
            return {
                "curr_name": curr_name, "curr_win": curr_win, "curr_avg": curr_avg,
                "next_name": next_name, "next_win": next_win, "next_avg": next_avg
            }
        except: return None

    # --- UI & ANALYSIS ENGINE ---
    col_input, col_info = st.columns([1, 2])
    with col_input:
        target_ticker = st.text_input("Enter Target Sector/Asset (e.g., SMH, XLK, XLE)", "SMH").upper()
        run_radar = st.button("🚀 Analyze Rotation Probabilities")
        
    with col_info:
        st.info("💡 **How to read this:** The engine looks 30-60 days ahead. It detects if smart money is likely distributing (taking profits before a weak month) or accumulating (front-running a historically strong month).")

    if run_radar and target_ticker:
        with st.spinner(f"Running Exhaustion and Forward Seasonality models for {target_ticker}..."):
            exhaustion_data = get_technical_exhaustion(target_ticker)
            season_data = get_seasonality(target_ticker)
            
            if exhaustion_data and season_data:
                price, sma, z_score = exhaustion_data
                
                st.divider()
                st.subheader(f"📊 {target_ticker} | Statistical Profile")
                
                # Setup Display Columns for 6 metrics
                m1, m2, m3, m4, m5, m6 = st.columns(6)
                
                # Z-Score Metric Logic
                if z_score > 2:
                    z_status, z_color = "🔴 Overbought", "inverse"
                elif z_score < -2:
                    z_status, z_color = "🟢 Oversold", "normal"
                else:
                    z_status, z_color = "🟡 Neutral", "off"

                m1.metric("Current Price", f"${price:,.2f}", f"50-SMA: ${sma:,.2f}")
                m2.metric("Technical Z-Score", f"{z_score:+.2f}", z_status, delta_color=z_color)
                
                # Current Month Metrics
                c_win, c_name = season_data['curr_win'], season_data['curr_name']
                m3.metric(f"Current: {c_name} Win %", f"{c_win:.0f}%", "Edge" if c_win > 55 else "Weak" if c_win < 45 else "")
                m4.metric(f"{c_name} Avg Return", f"{season_data['curr_avg']:+.2f}%")
                
                # Next Month Metrics
                n_win, n_name = season_data['next_win'], season_data['next_name']
                m5.metric(f"Forward: {n_name} Win %", f"{n_win:.0f}%", "Edge" if n_win > 55 else "Weak" if n_win < 45 else "")
                m6.metric(f"{n_name} Avg Return", f"{season_data['next_avg']:+.2f}%")
                
                # --- SYNTHESIS REPORT (Multi-Month Logic) ---
                st.write("---")
                st.write("### 🧠 AI Synthesis & Forward Rotation Probability")
                
                if z_score > 2.0:
                    if c_win < 50 and n_win < 50:
                        st.error(f"**High Fade Probability:** {target_ticker} is highly overextended (Z > 2.0) with sustained seasonal headwinds through {n_name}. Capital is highly likely to rotate out.")
                    elif c_win >= 50 and n_win < 50:
                        st.warning(f"**Distribution Warning:** {target_ticker} is overextended and entering a historically weak {n_name}. Smart money is likely taking profits now. Prepare for a rotation out.")
                    elif c_win < 50 and n_win >= 50:
                        st.warning(f"**Conflicting Signals:** Overextended and fighting current seasonal weakness, but historical tailwinds arrive in {n_name}. Expect choppy consolidation.")
                    else:
                        st.success(f"**Overbought but Supported:** Stretched, but strong seasonal tailwinds persist through {n_name}. Momentum might carry, but downside risk is elevated due to the stretched rubber band.")
                
                elif z_score < -2.0:
                    if c_win >= 50 and n_win >= 50:
                        st.success(f"**Prime Accumulation Zone:** Heavily oversold (Z < -2.0) with sustained historical tailwinds through {n_name}. High probability of capital rotation INTO this asset.")
                    elif c_win < 50 and n_win >= 50:
                        st.success(f"**Front-Running the Rotation:** Oversold and currently weak, but {n_name} historically brings strong inflows. Smart money may begin accumulating now.")
                    elif c_win >= 50 and n_win < 50:
                        st.warning(f"**Dead Cat Bounce Risk:** Oversold and currently supported, but severe seasonal headwinds hit in {n_name}. Keep a tight leash on any long trades.")
                    else:
                        st.error(f"**Falling Knife:** Oversold, but historical seasonality remains terrible through {n_name}. Wait for technical confirmation before trying to catch this.")
                
                else: # Neutral Z-Score (-2 to 2)
                    if c_win >= 55 and n_win >= 55:
                        st.success(f"**Sustained Tailwind:** Normal technical ranges, backed by strong seasonal inflows through {n_name}. Path of least resistance is up.")
                    elif c_win < 45 and n_win < 45:
                        st.error(f"**Sustained Headwind:** Normal technical ranges, but facing a multi-month seasonal slump through {n_name}. Capital is likely deploying elsewhere.")
                    elif n_win > c_win + 10:
                        st.info(f"**Forward-Looking Upgrade:** Currently neutral, but historical seasonality significantly improves next month ({n_name}). Watch for early capital inflows.")
                    elif n_win < c_win - 10:
                        st.warning(f"**Forward-Looking Downgrade:** Currently neutral, but historical seasonality drops off sharply in {n_name}. Upside may be capped soon.")
                    else:
                        st.info(f"**Holding Pattern:** {target_ticker} is trading within normal technical ranges with mixed historical seasonality. No clear rotation edge detected.")
                    
            else:
                st.error("Could not fetch data. Please check the ticker symbol and try again.")

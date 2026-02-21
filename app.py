import streamlit as st
    import yfinance as yf
    from datetime import datetime
    
    # PAGE CONFIG
    st.set_page_config(page_title="Global Macro Intelligence", layout="wide")
    
    st.title("🛡️ Global Macro & Crypto Intelligence")
    st.subheader("Cross-Asset Regime Overlay")
    
    # --- ROBUST DATA MINING FUNCTION ---
    def get_safe_data(ticker, label):
        try:
            d = yf.download(ticker, period="1mo", progress=False)
            if not d.empty:
                return d['Close'].iloc[-1].item()
            return 0.0
        except:
            return 0.0import streamlit as st
    import yfinance as yf
    from datetime import datetime
    
    # PAGE CONFIG
    st.set_page_config(page_title="SPX Market Intelligence", layout="wide")
    
    st.title("🛡️ SPX Market Intelligence")
    st.subheader("Multi-Agent Regime Overlay")
    
    # --- DATA MINING ---
    # Fetching SPX, 10yr Yield, 3mo Bill, and VIX
    data = yf.download(["^GSPC", "^TNX", "^IRX", "^VIX"], period="2y", progress=False)
    
    # Calculations
    spx_close = data['Close']['^GSPC'].iloc[-1]
    sma_200d = data['Close']['^GSPC'].rolling(window=200).mean().iloc[-1]
    ten_year = data['Close']['^TNX'].iloc[-1]
    short_rate = data['Close']['^IRX'].iloc[-1]
    
    # --- THE SIMPLIFIED OVERLAY ---
    cols = st.columns(6)
    indicators = [
        ("Momentum", "🟢 BULLISH", "Above 200D"),
        ("Inflation", "🟡 2.4%", "Sticky PCE"),
        ("Growth", "🟡 1.4%", "GDP Slowing"),
        ("Positioning", "🟢 LITE", f"VIX {data['Close']['^VIX'].iloc[-1]:.1f}"),
        ("Monetary", "🟡 NEUTRAL", "Prime 6.75%"),
        ("Fiscal", "🔴 DEFICIT", "Duration ↑")
    ]
    
    for i, col in enumerate(cols):
        col.metric(indicators[i][0], indicators[i][1], indicators[i][2])
    
    st.divider()
    
    # --- THE SUBSTANCE (DEEP DIVES) ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        with st.expander("🔍 Momentum & Trend Layers", expanded=True):
            st.write(f"**Current S&P 500:** {spx_close:,.2f}")
            st.write(f"**Daily 200-MA:** {sma_200d:,.2f}")
            st.info("Analysis: Primary trend remains structurally intact above the 200-day moving average.")
    
        with st.expander("📊 Inflation & Growth Dynamics", expanded=True):
            st.write("**Headline CPI:** 2.4%")
            st.write("**Core PCE:** 3.0% (Sticky)")
            st.write("**GDP Growth:** 1.4% (Q4)")
            st.warning("Substance: Growth is cooling while core inflation remains above target, creating a complex 'soft landing' environment.")
    
    with col_right:
        with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
            st.write(f"**US Prime Rate:** 6.75%")
            st.write(f"**10-Year Benchmark:** {ten_year:.2f}%")
            st.write(f"**3-Month T-Bill:** {short_rate:.2f}%")
            st.error("Risk: Inverted yield curve and restrictive prime rate continue to act as headwinds for credit-sensitive sectors.")
    
        with st.expander("📜 Fiscal Policy & Treasury Issuance", expanded=True):
            st.write("**Issuance Mix:** Shifting toward Coupons (Long-term).")
            st.write("**Liquidity Summary:** Increased long-dated supply drains market liquidity and adds upward pressure to yields.")
    
    st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    
    # Fetching individually
    spx_now = get_safe_data("^GSPC", "S&P 500")
    btc_now = get_safe_data("BTC-USD", "Bitcoin")
    gold_now = get_safe_data("GC=F", "Gold")
    dxy_now = get_safe_data("UUP", "Dollar")
    qqq_now = get_safe_data("QQQ", "Nasdaq")
    intl_now = get_safe_data("VXUS", "Intl")
    vix_now = get_safe_data("^VIX", "VIX")
    tnx_now = get_safe_data("^TNX", "10Y Yield")
    
    # --- SENTIMENT GAUGE ---
    if vix_now > 25:
        fng_status = "😨 EXTREME FEAR"
    elif vix_now > 20:
        fng_status = "😟 FEAR"
    elif vix_now < 15:
        fng_status = "🤑 GREED"
    else:
        fng_status = "😐 NEUTRAL"
    
    # --- THE GLOBAL OVERLAY ---
    st.markdown(f"### 🚀 Market Sentiment: `{fng_status}`")
    cols1 = st.columns(6)
    
    def show_metric(col, label, value, prefix="", suffix=""):
        if value == 0:
            col.metric(label, "Data Pending", "🔄 Refreshing")
        else:
            col.metric(label, f"{prefix}{value:,.2f}{suffix}")
    
    show_metric(cols1[0], "S&P 500", spx_now)
    show_metric(cols1[1], "Bitcoin", btc_now, prefix="$")
    show_metric(cols1[2], "Gold", gold_now, prefix="$")
    show_metric(cols1[3], "USD (DXY)", dxy_now)
    show_metric(cols1[4], "Nasdaq (QQQ)", qqq_now)
    show_metric(cols1[5], "International", intl_now)
    
    st.divider()
    
    # --- THE SUBSTANCE ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        with st.expander("₿ Crypto & Bitcoin Intelligence", expanded=True):
            st.write(f"**Current BTC:** ${btc_now:,.2f}")
            st.info("Agent Logic: Bitcoin is acting as a 'Macro Leading Indicator.'")
    
        with st.expander("🌍 Global & Foreign Markets", expanded=True):
            st.write(f"**VXUS (Intl Stocks):** ${intl_now:.2f}")
            st.write(f"**UUP (Dollar Strength):** {dxy_now:.2f}")
    
    with col_right:
        with st.expander("📉 Fear & Greed: Detailed Gauge", expanded=True):
            st.write(f"**VIX Index:** {vix_now:.2f}")
    
        with st.expander("🏦 Rates & Monetary Policy", expanded=True):
            st.write(f"**10-Year Yield:** {tnx_now:.2f}%")
            st.write("**US Prime Rate:** 6.75%")
    
    st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    

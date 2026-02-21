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
            return 0.0
    
    # Fetching individually to prevent KeyErrors
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
    
    # Helper for metrics to handle 0.0/NaN gracefully
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
            st.info("Agent Logic: Bitcoin is acting as a 'Macro Leading Indicator.' Strength here often precedes a broader equity rally.")
    
        with st.expander("🌍 Global & Foreign Markets", expanded=True):
            st.write(f"**VXUS (Intl Stocks):** ${intl_now:.2f}")
            st.write(f"**UUP (Dollar Strength):** {dxy_now:.2f}")
            st.warning("Substance: A rising DXY (Dollar) typically drains liquidity from Emerging Markets and Gold.")
    
    with col_right:
        with st.expander("📉 Fear & Greed: Detailed Gauge", expanded=True):
            st.write(f"**VIX Index:** {vix_now:.2f}")
            st.error("Sentiment Logic: High VIX readings suggest institutional hedging is increasing, creating a defensive posture.")
    
        with st.expander("🏦 Rates & Monetary Policy", expanded=True):
            st.write(f"**10-Year Yield:** {tnx_now:.2f}%")
            st.write("**US Prime Rate:** 6.75%")
            st.info("Logic: The spread between growth (QQQ) and rates (10Y) remains the primary driver of equity multiples.")
    
    st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data: Yahoo Finance")
    

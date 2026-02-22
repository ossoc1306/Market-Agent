import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Global Asset Intelligence", layout="wide")

st.title("🛡️ Global Asset Intelligence")
st.subheader("Multi-Asset Overlay")

# --- ROBUST DATA MINING FUNCTIONS ---
def get_safe_data(ticker):
    try:
        d = yf.download(ticker, period="5d", progress=False)
        if not d.empty:
            return d['Close'].dropna().iloc[-1].item()
        return 0.0
    except:
        return 0.0

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
        return 0.0

def get_sma(ticker, window):
    try:
        d = yf.download(ticker, period="2y", progress=False)
        return d['Close'].rolling(window=window).mean().iloc[-1].item()
    except:
        return 0.0

def get_sector_leaderboard():
    sectors = {
        "XLC": "Comm Services", "XLY": "Consumer Disc", "XLP": "Consumer Staples",
        "XLE": "Energy", "XLF": "Financials", "XLV": "Health Care",
        "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real Estate",
        "XLK": "Technology", "XLU": "Utilities"
    }
    tickers = list(sectors.keys())
    try:
        data = yf.download(tickers, period="2mo", progress=False)['Close']
        daily = ((data.iloc[-1] / data.iloc[-2]) - 1) * 100
        weekly = ((data.iloc[-1] / data.iloc[-6]) - 1) * 100
        monthly = ((data.iloc[-1] / data.iloc[-21]) - 1) * 100
        
        def format_top5(series):
            top5 = series.sort_values(ascending=False).head(5)
            return [f"{sectors[t]}: {v:+.1f}%" for t, v in top5.items()]

        return format_top5(daily), format_top5(weekly), format_top5(monthly)
    except:
        return ["Data Pending"]*5, ["Data Pending"]*5, ["Data Pending"]*5

# Fetch Core Data
spx_now = get_safe_data("^GSPC")
qqq_now = get_safe_data("QQQ")
vxus_now = get_safe_data("VXUS")
vix_now = get_safe_data("^VIX")
tnx_now = get_safe_data("^TNX")
short_rate = get_safe_data("^IRX")
btc_now = get_safe_data("BTC-USD")
gold_now = get_safe_data("GC=F")

# Indicators & Trend
sma_200d = get_sma("^GSPC", 200)
sma_40w = get_sma("^GSPC", 280)
spx_rsi_d = calculate_rsi("^GSPC", "1d")
spx_rsi_w = calculate_rsi("^GSPC", "1wk")

qqq_200d = get_sma("QQQ", 200)
qqq_rsi_d = calculate_rsi("QQQ", "1d")
qqq_rsi_w = calculate_rsi("QQQ", "1wk")

vxus_200d = get_sma("VXUS", 200)
vxus_rsi_d = calculate_rsi("VXUS", "1d")
vxus_rsi_w = calculate_rsi("VXUS", "1wk")

# Leaderboard Data
top_d, top_w, top_m = get_sector_leaderboard()

# --- THE 6 PILLARS OVERLAY ---
cols = st.columns(6)
mom_val = ((spx_now/sma_200d)-1)*100 if sma_200d > 0 else 0
mom_color = "🟢" if mom_val > 0 else "🔴"

def show_pillar(col, label, status_text, subtext):
    col.metric(label, status_text, subtext)

show_pillar(cols[0], "Momentum", f"{mom_color} BULLISH", f"{mom_val:+.1f}% vs 200D")
show_pillar(cols[1], "Inflation", "🟡 2.40%", "PCE Sticky at 3%")
show_pillar(cols[2], "Growth", "🟡 1.40%", "Q4 Slowdown")
show_pillar(cols[3], "Positioning", f"🟢 LITE", f"VIX {vix_now:.1f}")
show_pillar(cols[4], "Monetary", "🟡 6.75%", "Prime Rate")
show_pillar(cols[5], "Fiscal", "🔴 DEFICIT", "Duration Mix ↑")

st.divider()

# --- SECTOR LEADERBOARD ---
st.subheader("📊 SPDR Sector Leaderboard (Top 5)")
l_cols = st.columns(3)
with l_cols[0]:
    st.write("**Daily Leaders**")
    for item in top_d: st.write(item)
with l_cols[1]:
    st.write("**Weekly Leaders**")
    for item in top_w: st.write(item)
with l_cols[2]:
    st.write("**Monthly Leaders**")
    for item in top_m: st.write(item)

st.divider()

# --- THE SUBSTANCE (DEEP DIVES) ---
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
            st.write(f"Daily RSI: {qqq_rsi_d:.1f} | Weekly: {qqq_rsi_w:.1f}")
            st.write(f"200-MA: {qqq_200d:,.2f}")
        with c3:
            st.write("**International (VXUS)**")
            st.write(f"Price: {vxus_now:,.2f}")
            st.write(f"Daily RSI: {vxus_rsi_d:.1f} | Weekly: {vxus_rsi_w:.1f}")
            st.write(f"200-MA: {vxus_200d:,.2f}")
        st.info("Agent Logic: Primary trend is UP as long as we hold the 40-week line. Divergence between SPX, QQQ, and VXUS RSI can signal internal rotation.")

    with st.expander("📊 Inflation & Growth Dynamics", expanded=True):
        st.write("**Core PCE:** 3.0% YoY (Still above Fed target)")
        st.write("**GDP Growth:** 1.4% (Q4 Advance Estimate)")
        st.warning("Analysis: The 'Soft Landing' is being tested as growth cools to 1.4% while core inflation remains at 3%. Watch for 'Stagflation' signals.")

    with st.expander("₿ Crypto Intelligence Agent", expanded=True):
        st.write(f"**Bitcoin Price:** ${btc_now:,.2f}")
        btc_200ma = get_sma("BTC-USD", 200)
        btc_trend = "🟢 Bullish" if btc_now > btc_200ma else "🔴 Bearish"
        st.write(f"**BTC Trend:** {btc_trend}")
        st.info("Analysis: BTC acts as a sensor for global dollar liquidity. Strength here often precedes broader market risk appetite.")

with col_right:
    with st.expander("✨ Gold Intelligence Agent", expanded=True):
        st.write(f"**Current Gold Price:** ${gold_now:,.2f}")
        st.write(f"**Gold/SPX Ratio:** {gold_now/spx_now if spx_now > 0 else 0:.4f}")
        st.info("Agent Logic: Gold acts as the ultimate safe-haven. Strength here often signals a hedge against currency debasement or geopolitical risk.")

    with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
        st.write(f"**US Prime Rate:** 6.75% (Effective Dec 2025)")
        st.write(f"**10-Year Benchmark:** {tnx_now:.2f}%")
        st.write(f"**3-Month T-Bill:** {short_rate:.2f}%")
        st.write(f"**10Y/3M Spread:** {tnx_now - short_rate:.2f}%")
        st.error("Risk: The inverted curve historically precedes a tightening of credit and lower equity multiples.")

    with st.expander("📜 Fiscal Policy & Treasury Issuance", expanded=True):
        st.write("**Recent QRA:** Treasury offering $125B in securities (Feb 2026).")
        st.write("**Liquidity Summary:** Treasury is shifting more issuance into 10-year and 30-year 'Coupons.' This drains reserves.")
        st.info("Strategy: Monitor the 'Bill Share' of debt. A drop in T-Bill issuance relative to Coupons usually precedes a dip in stock market volatility.")

st.divider()

# --- NEW: GEOPOLITICAL HEADWINDS & TAILWINDS ---
st.subheader("🌍 Geopolitical Intelligence Agent")
geo_left, geo_right = st.columns(2)

with geo_left:
    st.write("**🔴 Geopolitical Headwinds**")
    st.write("- **Trade Friction:** Increasing tariffs and export controls on high-end semiconductors.")
    st.write("- **Energy Stability:** Escalating tensions in key maritime corridors impacting oil delivery cost.")
    st.write("- **Asset Impact:** 🔴 Bearish for Emerging Markets, Global Logistics, and Consumer Tech.")

with geo_right:
    st.write("**🟢 Geopolitical Tailwinds**")
    st.write("- **Near-Shoring:** Accelerating industrial capital expenditure in the Western Hemisphere pivot.")
    st.write("- **Defense Modernization:** Multi-year budget expansion for re-armament and cybersecurity.")
    st.write("- **Asset Impact:** 🟢 Bullish for Defense Stocks, Cybersecurity, Gold, and Domestic Industrials.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: [Yahoo Finance](https://finance.yahoo.com)")

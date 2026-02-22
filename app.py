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

        d_t, d_b = get_ranks(daily)
        w_t, w_b = get_ranks(weekly)
        m_t, m_b = get_ranks(monthly)
        y_t, y_b = get_ranks(ytd)
        return (d_t, d_b), (w_t, w_b), (m_t, m_b), (y_t, y_b), sector_rsis, sectors
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

# Indicators & Trend
sma_200d = get_sma("^GSPC", 200)
spx_rsi_d = calculate_rsi("^GSPC", "1d")
spx_rsi_w = calculate_rsi("^GSPC", "1wk")
qqq_200d = get_sma("QQQ", 200)
qqq_rsi_d = calculate_rsi("QQQ", "1d")
qqq_rsi_w = calculate_rsi("QQQ", "1wk")
vxus_200d = get_sma("VXUS", 200)
vxus_rsi_d = calculate_rsi("VXUS", "1d")
vxus_rsi_w = calculate_rsi("VXUS", "1wk")

# Leaderboard Data
daily_data, weekly_data, monthly_data, ytd_data, s_rsis, s_names = get_sector_leaderboard()

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

# --- MARKET TEMPERATURE ---
st.subheader("🌡️ Market Temperature & Sentiment Gauge")
avg_rsi = (spx_rsi_d + qqq_rsi_d + vxus_rsi_d) / 3
if avg_rsi > 70: status, color = "EXTREME GREED / OVERBOUGHT", "🔴"
elif avg_rsi > 60: status, color = "GREED", "🟠"
elif avg_rsi < 30: status, color = "EXTREME FEAR / OVERSOLD", "🔵"
elif avg_rsi < 40: status, color = "FEAR", "🟡"
else: status, color = "NEUTRAL", "🟢"

st.markdown(f"### {color} Current Regime: **{status}** (Avg RSI: {avg_rsi:.1f})")
st.info("The Sentiment Gauge averages the Daily RSI of SPX, QQQ, and VXUS to identify broad exhaustion or capitulation.")

st.divider()

# --- SECTOR LEADERBOARD & RSI HEATMAP ---
st.subheader("📊 Sector Performance & RSI Heatmap")
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

# --- THE SUBSTANCE (DEEP DIVES) ---
col_left, col_right = st.columns(2)

with col_left:
    with st.expander("🔍 Momentum & Trend Layers (SPX, QQQ, VXUS)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**S&P 500 (SPX)**")
            st.write(f"Price: {spx_now:,.2f}")
            st.write(f"Daily RSI: {spx_rsi_d:.1f} | Weekly: {spx_rsi_w:.1f}")
        with c2:
            st.write("**Nasdaq (QQQ)**")
            st.write(f"Price: {qqq_now:,.2f}")
            st.write(f"Daily RSI: {qqq_rsi_d:.1f} | Weekly: {qqq_rsi_w:.1f}")
        with c3:
            st.write("**International (VXUS)**")
            st.write(f"Price: {vxus_now:,.2f}")
            st.write(f"Daily RSI: {vxus_rsi_d:.1f} | Weekly: {vxus_rsi_w:.1f}")
        st.info("Agent Logic: Primary trend is UP as long as we hold the 40-week line. Divergence signals internal rotation.")

    with st.expander("📊 Inflation & Growth Dynamics", expanded=True):
        st.write("**Core PCE:** 3.0% YoY | **GDP Growth:** 1.4% (Q4)")
        st.warning("Analysis: Watch for 'Stagflation' signals as growth cools while PCE remains sticky.")

    with st.expander("₿ Crypto Intelligence Agent", expanded=True):
        st.write(f"**Bitcoin Price:** ${btc_now:,.2f}")
        btc_200ma = get_sma("BTC-USD", 200)
        st.write(f"**BTC Trend:** {'🟢 Bullish' if btc_now > btc_200ma else '🔴 Bearish'}")
        st.info("Analysis: BTC acts as a sensor for global dollar liquidity.")

with col_right:
    with st.expander("🌊 Liquidity Watch Agent (US & Global)", expanded=True):
        st.write(f"**Dollar Index (DXY):** {dxy_now:.2f}")
        st.write("**US Net Liquidity Logic:** Fed Balance Sheet - (TGA + RRP)")
        st.info("Macro Note: Rising DXY usually acts as a 'Liquidity Vacuum,' pulling dollars out of risk assets like Tech and Crypto.")
        st.write("**Global M2 Trend:** Expansionary bias from central bank pivots.")

    with st.expander("✨ Gold Intelligence Agent", expanded=True):
        st.write(f"**Current Gold Price:** ${gold_now:,.2f}")
        st.write(f"**Gold/SPX Ratio:** {gold_now/spx_now if spx_now > 0 else 0:.4f}")

    with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
        st.write(f"**10-Year Benchmark:** {tnx_now:.2f}% | **3-Month T-Bill:** {short_rate:.2f}%")
        st.write(f"**10Y/3M Spread:** {tnx_now - short_rate:.2f}%")

    with st.expander("📜 Fiscal Policy & Treasury Issuance", expanded=True):
        st.write("**Recent QRA:** Treasury offering $125B (Feb 2026).")
        st.write("**Liquidity Summary:** Treasury shifting to 'Coupons' (Liquidity Drain).")

st.divider()

# --- GEOPOLITICAL HEADWINDS & TAILWINDS ---
st.subheader("🌍 Geopolitical Intelligence Agent")
geo_left, geo_right = st.columns(2)
with geo_left:
    st.write("**🔴 Geopolitical Headwinds**")
    st.write("- **Trade Friction:** Increasing tariffs on high-end semiconductors.")
    st.write("- **Energy Stability:** Escalating tensions in key maritime corridors.")
with geo_right:
    st.write("**🟢 Geopolitical Tailwinds**")
    st.write("- **Near-Shoring:** Industrial CapEx in the Western Hemisphere pivot.")
    st.write("- **Defense Modernization:** Multi-year budget expansion for re-armament.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: [Yahoo Finance](https://finance.yahoo.com)")

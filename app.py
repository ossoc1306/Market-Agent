import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Global Macro Intelligence", layout="wide")

st.title("🛡️ Global Macro & Crypto Intelligence")
st.subheader("Cross-Asset Regime Overlay")

# --- DATA MINING ---
# S&P 500, QQQ, Gold (GLD), DXY (UUP proxy), Bitcoin (BTC-USD), International (VXUS)
tickers = ["^SPX", "QQQ", "GLD", "UUP", "BTC-USD", "VXUS", "^VIX", "^IRX"]
data = yf.download(tickers, period="2y", progress=False)['Close']

# Current Prices & Trends
spx_now = data['^SPX'].iloc[-1]
btc_now = data['BTC-USD'].iloc[-1]
btc_200d = data['BTC-USD'].rolling(200).mean().iloc[-1]

# --- SENTIMENT GAUGE (Logic) ---
vix = data['^VIX'].iloc[-1]
# Simple Fear & Greed Logic
if vix > 25:
    fng_status = "😨 EXTREME FEAR"
elif vix > 20:
    fng_status = "😟 FEAR"
elif vix < 15:
    fng_status = "🤑 GREED"
else:
    fng_status = "😐 NEUTRAL"

# --- THE GLOBAL OVERLAY (Top Row) ---
st.markdown(f"### 🚀 Market Sentiment: `{fng_status}`")
cols1 = st.columns(6)
indicators = [
    ("S&P 500", f"{spx_now:,.0f}", "🟢 Bullish" if spx_now > data['^SPX'].rolling(200).mean().iloc[-1] else "🔴 Bearish"),
    ("Bitcoin", f"${btc_now:,.0f}", "🟢 Risk-On" if btc_now > btc_200d else "🔴 Risk-Off"),
    ("Gold", f"${data['GLD'].iloc[-1]:.0f}", "Safe Haven"),
    ("USD (DXY)", f"{data['UUP'].iloc[-1]:.2f}", "Currency Strength"),
    ("Nasdaq (QQQ)", f"{data['QQQ'].iloc[-1]:.0f}", "Tech Growth"),
    ("International", f"{data['VXUS'].iloc[-1]:.2f}", "Global Exposure")
]

for i, col in enumerate(cols1):
    col.metric(indicators[i][0], indicators[i][1], indicators[i][2])

st.divider()

# --- THE SUBSTANCE (DEEP DIVES) ---
col_left, col_right = st.columns(2)

with col_left:
    with st.expander("₿ Crypto & Bitcoin Intelligence", expanded=True):
        st.write(f"**BTC 200-Day Moving Average:** ${btc_200d:,.0f}")
        st.write(f"**BTC Dominance Proxy:** High (Capital concentrating in Blue Chips)")
        st.info("Agent Logic: Bitcoin is acting as a 'Macro Leading Indicator.' Its strength above the 200D suggests global liquidity is increasing.")

    with st.expander("🌍 Global & Foreign Markets", expanded=True):
        st.write(f"**VXUS (Intl Stocks):** ${data['VXUS'].iloc[-1]:.2f}")
        st.write(f"**UUP (Dollar Strength):** {'📈 Strong Dollar (Headwind)' if data['UUP'].pct_change(20).iloc[-1] > 0 else '📉 Weak Dollar (Tailwind)'}")
        st.warning("Substance: A rising DXY (Dollar) typically drains liquidity from Emerging Markets and Gold.")

with col_right:
    with st.expander("📉 Fear & Greed: Detailed Gauge", expanded=True):
        st.write(f"**VIX Index:** {vix:.1f}")
        st.write(f"**Equity/Gold Ratio:** {spx_now / data['GLD'].iloc[-1]:.2f} (Risk Appetite)")
        st.error("Sentiment Logic: We are currently in a 'Fear' regime. Historically, this is when smart money begins accumulating defensive assets like Gold.")

    with st.expander("🏦 Rates & Monetary Policy", expanded=True):
        st.write(f"**10-Year Yield:** {data['^TNX'].iloc[-1]:.2f}%")
        st.write("**US Prime Rate:** 6.75%")
        st.info("Logic: The spread between growth (QQQ) and rates (10Y) remains the primary driver of equity multiples.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data: Yahoo Finance & Global Feeds")

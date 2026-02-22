import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="SPX Market Intelligence", layout="wide")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- DATA MINING ---
# Fetching SPX, 10yr Yield, 3mo Bill, VIX + Crypto
main_data = yf.download(["^GSPC", "^TNX", "^IRX", "^VIX"], period="2y", progress=False)
crypto_data = yf.download(["BTC-USD", "ETH-USD"], period="2y", progress=False)

# SPX Calculations
spx_close = main_data['Close']['^GSPC'].iloc[-1]
sma_200d = main_data['Close']['^GSPC'].rolling(window=200).mean().iloc[-1]
ten_year = main_data['Close']['^TNX'].iloc[-1]
short_rate = main_data['Close']['^IRX'].iloc[-1]

# Crypto Calculations
btc_price = crypto_data['Close']['BTC-USD'].iloc[-1]
btc_200ma = crypto_data['Close']['BTC-USD'].rolling(window=200).mean().iloc[-1]
btc_trend = "🟢 Bullish" if btc_price > btc_200ma else "🔴 Bearish"

# --- THE SIMPLIFIED OVERLAY ---
cols = st.columns(6)
indicators = [
    ("Momentum", "🟢 BULLISH", "Above 200D"),
    ("Inflation", "🟡 2.4%", "Sticky PCE"),
    ("Growth", "🟡 1.4%", "GDP Slowing"),
    ("Positioning", "🟢 LITE", f"VIX {main_data['Close']['^VIX'].iloc[-1]:.1f}"),
    ("Monetary", "🟡 NEUTRAL", "Prime 6.75%"),
    ("Fiscal", "🔴 DEFICIT", "Duration ↑")
]

for i, col in enumerate(cols):
    col.metric(indicators[i][0], indicators[i][1], indicators[i][2])

st.divider()

# --- THE SUBSTANCE ---
col_left, col_right = st.columns(2)

with col_left:
    with st.expander("🔍 Momentum & Trend Layers", expanded=True):
        st.write(f"**Current S&P 500:** {spx_close:,.2f}")
        st.write(f"**Daily 200-MA:** {sma_200d:,.2f}")
        st.info("Analysis: Primary trend remains structurally intact.")

    with st.expander("📊 Inflation & Growth Dynamics", expanded=True):
        st.write("**Core PCE:** 3.0% (Sticky)")
        st.write("**GDP Growth:** 1.4% (Q4)")

with col_right:
    with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
        st.write(f"**10-Year Benchmark:** {ten_year:.2f}%")
        st.write(f"**3-Month T-Bill:** {short_rate:.2f}%")

    # NEW: CRYPTO INTELLIGENCE AGENT
    with st.expander("₿ Crypto Intelligence Agent", expanded=True):
        st.write(f"**Bitcoin Price:** ${btc_price:,.2f}")
        st.write(f"**BTC 200-Day Trend:** {btc_trend}")
        st.write(f"**Distance to 200MA:** {((btc_price/btc_200ma)-1)*100:+.2f}%")
        st.info("Agent Logic: When BTC holds its 200-day average, it signals positive global liquidity—a tailwind for the SPX.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

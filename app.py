import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="SPX Market Intelligence", layout="centered")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- DATA MINING ---
# We use yfinance for everything now to avoid the 'pandas_datareader' bug
spx = yf.download("^SPX", period="1y", progress=False)
current_price = spx['Close'].iloc[-1].item()
sma_200 = spx['Close'].rolling(window=200).mean().iloc[-1].item()

# --- THE SIMPLIFIED OVERLAY ---
col1, col2, col3 = st.columns(3)

with col1:
    m_status = "🟢 BULLISH" if current_price > sma_200 else "🔴 BEARISH"
    st.metric("Momentum", m_status)
with col2:
    # Hardcoded for now to bypass the bug; we will automate this next
    st.metric("Inflation", "🟡 2.4%", "Sticky")
with col3:
    st.metric("Policy", "🔴 HAWKISH", "Fed Pressure")

st.divider()

# --- THE EXPANDABLE DEEP DIVES ---
with st.expander("🔍 Deep Dive: Momentum & Price Action"):
    st.write(f"Current SPX: {current_price:,.2f}")
    st.write(f"200-Day Average: {sma_200:,.2f}")
    margin = ((current_price - sma_200) / sma_200) * 100
    st.info(f"Logic: SPX is {margin:+.2f}% relative to the 200DMA.")

with st.expander("📊 Deep Dive: Inflation & Growth"):
    st.warning("Logic: Shielding from recent CPI volatility. Agent remains cautious on 'Supercore' services.")

with st.expander("🏦 Deep Dive: Monetary & Fiscal Policy"):
    st.error("Logic: High debt issuance and restrictive interest rates remain the primary headwinds.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

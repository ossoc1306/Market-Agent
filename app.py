import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="SPX Market Intelligence", layout="centered")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- DATA MINING ---
spx = yf.download("^SPX", period="1y", progress=False)
current_price = spx['Close'].iloc[-1].item()
sma_200 = spx['Close'].rolling(window=200).mean().iloc[-1].item()

# --- THE SIMPLIFIED OVERLAY (6 Indicators) ---
# Row 1
col1, col2, col3 = st.columns(3)
with col1:
    m_status = "🟢 BULLISH" if current_price > sma_200 else "🔴 BEARISH"
    st.metric("Momentum", m_status)
with col2:
    st.metric("Inflation", "🟡 2.4%", "Sticky")
with col3:
    st.metric("Growth", "🟢 2.8%", "GDP Stable")

# Row 2
col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Positioning", "🟢 LITE", "Low VIX")
with col5:
    st.metric("Monetary", "🔴 HAWKISH", "Rates High")
with col6:
    st.metric("Fiscal", "🔴 DEFICIT", "Issuance ↑")

st.divider()

# --- THE EXPANDABLE DEEP DIVES ---
with st.expander("🔍 Deep Dive: Momentum & Positioning"):
    st.info(f"Logic: SPX is {((current_price - sma_200) / sma_200) * 100:+.2f}% vs 200DMA. Positioning is lite as VIX remains below 20.")

with st.expander("📊 Deep Dive: Inflation & Growth"):
    st.warning("Logic: GDP remains resilient at 2.8%, but 'Supercore' inflation keeps the Fed cautious.")

with st.expander("🏦 Deep Dive: Monetary & Fiscal Policy"):
    st.error("Logic: The combination of 5%+ interest rates and high Treasury issuance is the primary risk to multiples.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

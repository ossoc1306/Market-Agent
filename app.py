import streamlit as st
import yfinance as yf
import pandas_datareader.data as web
from datetime import datetime

# PAGE CONFIG - This makes it look like a pro app on your phone
st.set_page_config(page_title="SPX Market Intelligence", layout="centered")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- THE SIMPLIFIED OVERLAY (Top Level) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Momentum", "🟢 BULLISH", "Trend Intact")
with col2:
    st.metric("Inflation", "🟡 ELEVATED", "Sticky CPI")
with col3:
    st.metric("Policy", "🔴 HAWKISH", "Fed Pressure")

st.divider()

# --- THE EXPANDABLE DEEP DIVES (Deep Research) ---

with st.expander("🔍 Deep Dive: Momentum & Price Action"):
    st.write("Agent Scout-1 has mined the 200-day Moving Average.")
    # Here the app would draw a chart
    st.info("Logic: SPX is 4.2% above the 200DMA. Momentum is strong but overextended.")

with st.expander("📊 Deep Dive: Inflation & Growth"):
    st.write("Agent Macro-1 analyzed the latest BLS reports.")
    st.warning("Logic: Shelter costs remain high. The agent expects the next CPI print to be 2.5% vs 2.3% estimate.")

with st.expander("🏦 Deep Dive: Monetary & Fiscal Policy"):
    st.write("Agent Policy-1 reviewed the latest Treasury Refunding Announcement.")
    st.error("Logic: High debt issuance is competing with equities for capital. This is a hidden headwind.")

# --- FOOTER ---
st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="SPX Market Intelligence", layout="wide")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- ROBUST DATA MINING FUNCTION ---
def get_safe_data(ticker):
    try:
        d = yf.download(ticker, period="5d", progress=False)
        if not d.empty:
            return d['Close'].dropna().iloc[-1].item()
        return 0.0
    except:
        return 0.0

def get_sma(ticker, window):
    try:
        d = yf.download(ticker, period="2y", progress=False)
        return d['Close'].rolling(window=window).mean().iloc[-1].item()
    except:
        return 0.0

# Fetch Data
spx_now = get_safe_data("^GSPC")
vix_now = get_safe_data("^VIX")
tnx_now = get_safe_data("^TNX")
short_rate = get_safe_data("^IRX")
btc_now = get_safe_data("BTC-USD")
gold_now = get_safe_data("GC=F")
sma_200d = get_sma("^GSPC", 200)
sma_40w = get_sma("^GSPC", 280)

# --- THE 6 PILLARS OVERLAY ---
cols = st.columns(6)

# Logic for indicators
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

# --- THE SUBSTANCE (DEEP DIVES) ---
col_left, col_right = st.columns(2)

with col_left:
    with st.expander("🔍 Momentum & Trend Layers", expanded=True):
        st.write(f"**Current S&P 500:** {spx_now:,.2f}")
        st.write(f"**Daily 200-MA:** {sma_200d:,.2f}")
        st.write(f"**Weekly 40-Week MA:** {sma_40w:,.2f}")
        st.info("Agent Logic: Momentum remains structurally intact above the 200-day line.")

    with st.expander("₿ Crypto Intelligence Agent", expanded=True):
        st.write(f"**Bitcoin Price:** ${btc_now:,.2f}")
        btc_200ma = get_sma("BTC-USD", 200)
        btc_trend = "🟢 Bullish" if btc_now > btc_200ma else "🔴 Bearish"
        st.write(f"**BTC Trend:** {btc_trend}")
        st.info("Analysis: BTC acts as a sensor for global dollar liquidity.")

with col_right:
    with st.expander("✨ Gold Intelligence Agent", expanded=True):
        st.write(f"**Current Gold Price:** ${gold_now:,.2f}")
        st.write(f"**Gold/SPX Ratio:** {gold_now/spx_now if spx_now > 0 else 0:.4f}")
        st.info("Agent Logic: Gold strength often signals a hedge against currency debasement.")

    with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
        st.write(f"**10-Year Benchmark:** {tnx_now:.2f}%")
        st.write(f"**3-Month T-Bill:** {short_rate:.2f}%")
        st.error("Risk: The inverted curve historically precedes credit tightening.")

    with st.expander("📜 Fiscal Policy & Treasury Issuance", expanded=True):
        st.write("**Recent QRA:** Treasury offering $125B in securities (Feb 2026).")
        st.write("**Liquidity & Duration Summary:** Treasury is shifting more issuance into 10-year and 30-year 'Coupons.' This drains reserves.")
        st.info("Strategy: A drop in T-Bill issuance relative to Coupons usually precedes a dip in stock market volatility.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: Yahoo Finance")

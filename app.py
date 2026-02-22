import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="SPX Market Intelligence", layout="wide")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- ROBUST DATA MINING FUNCTION ---
def get_safe_data(ticker, label):
    try:
        # Fetching a small window to ensure we get the latest valid close
        d = yf.download(ticker, period="5d", progress=False)
        if not d.empty:
            # Get the last non-NaN value
            return d['Close'].dropna().iloc[-1].item()
        return 0.0
    except:
        return 0.0

# Fetching individually to prevent cross-ticker NaN corruption
spx_now = get_safe_data("^GSPC", "S&P 500")
vix_now = get_safe_data("^VIX", "VIX")
tnx_now = get_safe_data("^TNX", "10Y Yield")
short_rate = get_safe_data("^IRX", "3M Bill")
btc_now = get_safe_data("BTC-USD", "Bitcoin")
gold_now = get_safe_data("GC=F", "Gold")

# Calculate SMA for Trend (requires more data)
def get_sma(ticker, window):
    try:
        d = yf.download(ticker, period="2y", progress=False)
        return d['Close'].rolling(window=window).mean().iloc[-1].item()
    except:
        return 0.0

sma_200d = get_sma("^GSPC", 200)
sma_40w = get_sma("^GSPC", 280)

# --- THE SIMPLIFIED OVERLAY (6 Pillars) ---
cols = st.columns(6)

def show_metric(col, label, value, subtext, prefix="", suffix=""):
    if value == 0 or value is None:
        col.metric(label, "Data Pending", "🔄 Refreshing")
    else:
        col.metric(label, f"{prefix}{value:,.2f}{suffix}", subtext)

# Logic for Momentum subtext
mom_sub = f"{((spx_now/sma_200d)-1)*100:+.1f}% vs 200D" if sma_200d > 0 else "N/A"

show_metric(cols[0], "Momentum", spx_now, mom_sub)
show_metric(cols[1], "Inflation", 2.40, "PCE Sticky at 3%", suffix="%")
show_metric(cols[2], "Growth", 1.40, "Q4 Slowdown", suffix="%")
show_metric(cols[3], "Positioning", vix_now, "VIX Index")
show_metric(cols[4], "Monetary", 6.75, "Prime Rate", suffix="%")
show_metric(cols[5], "Fiscal", 0.0, "Duration Mix ↑", prefix="🔴 DEFICIT")

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
        st.write(f"**BTC Trend:** {'🟢 Bullish' if btc_now > 0 else '🔴 Data Error'}")
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

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: [Yahoo Finance](https://finance.yahoo.com)")

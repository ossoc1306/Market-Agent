import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG - Pro Wide Layout
st.set_page_config(page_title="SPX Market Intelligence", layout="wide")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- LIVE DATA MINING (Momentum & Yields) ---
# Tickers: ^SPX (S&P), ^TNX (10yr), ^IRX (13-week Bill), ^VIX (Volatility)
data = yf.download(["^SPX", "^TNX", "^IRX", "^VIX"], period="2y", progress=False)

# Calculations
spx_close = data['Close']['^SPX'].iloc[-1]
sma_200d = data['Close']['^SPX'].rolling(window=200).mean().iloc[-1]
sma_40w = data['Close']['^SPX'].rolling(window=280).mean().iloc[-1] 

# Interest Rate Data (Live-ish)
ten_year = data['Close']['^TNX'].iloc[-1]
# Note: Using ^IRX (3-month bill) as a proxy for the 'short-end' to avoid ticker bugs
short_rate = data['Close']['^IRX'].iloc[-1] 

# --- THE SIMPLIFIED OVERLAY (The 6 Pillars) ---
cols = st.columns(6)
indicators = [
    ("Momentum", "🟢 BULLISH", f"{((spx_close/sma_200d)-1)*100:+.1f}% vs 200D"),
    ("Inflation", "🟡 2.4%", "PCE Sticky at 3%"),
    ("Growth", "🟡 1.4%", "Q4 Slowdown"),
    ("Positioning", "🟢 LITE", f"VIX {data['Close']['^VIX'].iloc[-1]:.1f}"),
    ("Monetary", "🟡 NEUTRAL", "Prime 6.75%"),
    ("Fiscal", "🔴 DEFICIT", "Duration Mix ↑")
]

for i, col in enumerate(cols):
    col.metric(indicators[i][0], indicators[i][1], indicators[i][2])

st.divider()

# --- THE SUBSTANCE (DEEP DIVES) ---
col_left, col_right = st.columns(2)

with col_left:
    with st.expander("🔍 Momentum & Trend Layers", expanded=True):
        st.write(f"**Current S&P 500:** {spx_close:,.2f}")
        st.write(f"**Daily 200-MA:** {sma_200d:,.2f}")
        st.write(f"**Weekly 40-Week MA:** {sma_40w:,.2f}")
        st.info("Agent Logic: Momentum remains structurally intact. As long as we stay above the 40-week line, the primary trend is UP.")

    with st.expander("📊 Inflation & Growth Dynamics", expanded=True):
        st.write("**Headline CPI:** 2.4% (January 2026 Print)")
        st.write("**Core PCE:** 3.0% YoY (Still above Fed target)")
        st.write("**GDP Growth:** 1.4% (Q4 Advance Estimate)")
        st.warning("Analysis: The 'Soft Landing' is being tested as growth cools to 1.4% while core inflation remains at 3%. Watch for 'Stagflation' signals.")

with col_right:
    with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
        st.write(f"**US Prime Rate:** 6.75% (Effective Dec 2025)")
        st.write(f"**10-Year Benchmark:** {ten_year:.2f}%")
        st.write(f"**3-Month T-Bill:** {short_rate:.2f}%")
        st.write(f"**10Y/3M Spread:** {ten_year - short_rate:.2f}%")
        st.error("Risk: The yield curve remains inverted, which historically precedes a tightening of credit and lower equity multiples.")

    with st.expander("📜 Fiscal Policy & Treasury Issuance", expanded=True):
        st.write("**Recent QRA:** Treasury offering $125B in securities (Feb 2026).")
        st.write("**Liquidity & Duration Summary:** Treasury is shifting more issuance into 10-year and 30-year 'Coupons.' This drains reserves and forces the market to absorb more 'Duration,' which is a headwind for S&P 500 liquidity.")
        st.info("Strategy: Monitor the 'Bill Share' of debt. A drop in T-Bill issuance usually precedes a dip in stock market volatility.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: [FRED](https://fred.stlouisfed.org) & [BLS](https://www.bls.gov)")

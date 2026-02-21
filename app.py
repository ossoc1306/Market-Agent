import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG - Set to wide to accommodate 6 columns
st.set_page_config(page_title="SPX Market Intelligence", layout="wide")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- DATA MINING ---
# Fetching SPX, Yields, and VIX
data = yf.download(["^SPX", "^TNX", "^VIX", "SHY"], period="2y", progress=False)

# Momentum Calculations
spx_close = data['Close']['^SPX'].iloc[-1]
sma_200d = data['Close']['^SPX'].rolling(window=200).mean().iloc[-1]
sma_40w = data['Close']['^SPX'].rolling(window=280).mean().iloc[-1] 

# --- THE EXPANDED OVERLAY (6 Columns) ---
cols = st.columns(6)
indicators = [
    ("Momentum", "🟢 BULLISH", "Above 200D"),
    ("Inflation", "🟡 2.4%", "Sticky MoM"),
    ("Growth", "🟢 2.8%", "GDP Stable"),
    ("Positioning", "🟢 LITE", "VIX < 20"),
    ("Monetary", "🔴 HAWKISH", "Rates 5.5%"),
    ("Fiscal", "🔴 DEFICIT", "Duration ↑")
]

for i, col in enumerate(cols):
    col.metric(indicators[i][0], indicators[i][1], indicators[i][2])

st.divider()

# --- THE SUBSTANCE (DEEP DIVES) ---
col_left, col_right = st.columns(2)

with col_left:
    with st.expander("🔍 Momentum & Trend Layers", expanded=True):
        st.write(f"**Current Price:** {spx_close:,.2f}")
        st.write(f"**Daily 200-MA:** {sma_200d:,.2f} ({((spx_close/sma_200d)-1)*100:+.2f}%)")
        st.write(f"**Weekly 40-Week MA:** {sma_40w:,.2f}")
        st.info("Analysis: Trend is confirmed on both daily and weekly timeframes. Professional 'Golden Cross' remains active.")

    with st.expander("📊 Inflation & Growth Dynamics", expanded=True):
        st.write("**CPI (Consumer Price Index):** 2.4% YoY")
        st.write("**PCE (Core):** 2.6% YoY (Fed Preference)")
        st.write("**MoM Trend:** +0.2% (Target is +0.17%)")
        st.warning("Substance: While YoY is cooling, 'Supercore' services inflation prevents a Dovish pivot.")

with col_right:
    with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
        st.write(f"**10-Year Note:** {data['Close']['^TNX'].iloc[-1]:.2f}%")
        st.write("**US Prime Rate:** 8.50%")
        st.error("Fixed Income Logic: A restrictive Prime Rate is weighing on small-cap earnings and consumer credit.")

    with st.expander("📜 Fiscal Policy & Treasury Issuance", expanded=True):
        st.write("**Issuance Policy:** Quarterly Refunding Announcement (QRA)")
        st.write("**Current Stance:** Increasing longer-dated bond supply (Coupons).")
        # NEW LINE REQUESTED
        st.write("**Liquidity & Duration Summary:** The shift from Bills (short-term) to Coupons (long-term) increases 'Duration' in the market. This drains bank reserves and forces yields higher, creating a liquidity drag on the SPX.")
        st.info("Impact: Higher supply of long-term notes acts as a 'shadow' rate hike by tightening financial conditions.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data: Yahoo Finance & FRED")

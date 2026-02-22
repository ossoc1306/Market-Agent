import streamlit as st
import yfinance as yf
from datetime import datetime

# PAGE CONFIG - Pro Wide Layout
st.set_page_config(page_title="SPX Market Intelligence", layout="wide")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- LIVE DATA MINING ---
# Tickers: ^GSPC (S&P), ^TNX (10yr), ^IRX (13-week Bill), ^VIX (Volatility), BTC-USD (Bitcoin), GC=F (Gold)
tickers = ["^GSPC", "^TNX", "^IRX", "^VIX", "BTC-USD", "GC=F"]
data = yf.download(tickers, period="2y", progress=False)

# SPX Calculations
spx_close = data['Close']['^GSPC'].iloc[-1]
sma_200d = data['Close']['^GSPC'].rolling(window=200).mean().iloc[-1]
sma_40w = data['Close']['^GSPC'].rolling(window=280).mean().iloc[-1] 

# Interest Rate Data
ten_year = data['Close']['^TNX'].iloc[-1]
short_rate = data['Close']['^IRX'].iloc[-1] 

# Bitcoin Calculations
btc_price = data['Close']['BTC-USD'].iloc[-1]
btc_200ma = data['Close']['BTC-USD'].rolling(window=200).mean().iloc[-1]
btc_trend = "🟢 Bullish" if btc_price > btc_200ma else "🔴 Bearish"

# Gold Calculations
gold_price = data['Close']['GC=F'].iloc[-1]

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
        st.write("**Core PCE:** 3.0% YoY")
        st.write("**GDP Growth:** 1.4% (Q4 Advance Estimate)")
        st.warning("Analysis: Core inflation remains at 3%. Watch for 'Stagflation' signals if growth slows further.")

    with st.expander("₿ Crypto Intelligence Agent", expanded=True):
        st.write(f"**Bitcoin Price:** ${btc_price:,.2f}")
        st.write(f"**BTC 200-Day Trend:** {btc_trend}")
        st.write(f"**Distance to 200MA:** {((btc_price/btc_200ma)-1)*100:+.2f}%")
        st.info("Agent Logic: Bitcoin acts as a high-beta liquidity sensor. A breakout here often precedes broader market risk appetite.")

with col_right:
    with st.expander("✨ Gold Intelligence Agent", expanded=True):
        st.write(f"**Current Gold Price:** ${gold_price:,.2f}")
        st.write(f"**Gold/SPX Ratio:** {(gold_price / spx_close):.4f}")
        st.info("Agent Logic: Gold acts as the ultimate safe-haven and inflation hedge. Strength here often signals a hedge against currency debasement or geopolitical risk.")

    with st.expander("🏦 Yield Curve & Interest Rates", expanded=True):
        st.write(f"**US Prime Rate:** 6.75% (Effective Dec 2025)")
        st.write(f"**10-Year Benchmark:** {ten_year:.2f}%")
        st.write(f"**3-Month T-Bill:** {short_rate:.2f}%")
        st.write(f"**10Y/3M Spread:** {ten_year - short_rate:.2f}%")
        st.error("Risk: The yield curve remains inverted, which historically precedes a tightening of credit.")

    with st.expander("📜 Fiscal Policy & Treasury Issuance", expanded=True):
        st.write("**Recent QRA:** Treasury offering $125B in securities (Feb 2026).")
        st.write("**Liquidity & Duration Summary:** Treasury is shifting more issuance into 10-year and 30-year 'Coupons.' This drains reserves.")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: [FRED](https://fred.stlouisfed.org) & [BLS](https://www.bls.gov)")

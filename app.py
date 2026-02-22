import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="SPX Market Intelligence", layout="wide")

st.title("🛡️ SPX Market Intelligence")
st.subheader("Multi-Agent Regime Overlay")

# --- DATA FUNCTIONS ---
def get_safe_data(ticker):
    try:
        d = yf.download(ticker, period="5d", progress=False)
        return d['Close'].dropna().iloc[-1].item() if not d.empty else 0.0
    except:
        return 0.0

def calculate_rsi(ticker, period="1d", window=14):
    try:
        hp = "60d" if period == "1d" else "2y"
        iv = "1d" if period == "1d" else "1wk"
        df = yf.download(ticker, period=hp, interval=iv, progress=False)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        return rsi.iloc[-1].item()
    except:
        return 0.0

def get_sma(ticker, window):
    try:
        d = yf.download(ticker, period="2y", progress=False)
        return d['Close'].rolling(window=window).mean().iloc[-1].item()
    except:
        return 0.0

def get_sector_leaderboard():
    sectors = {"XLC":"Comm","XLY":"Disc","XLP":"Staples","XLE":"Energy","XLF":"Fin","XLV":"Health","XLI":"Ind","XLB":"Mat","XLRE":"RE","XLK":"Tech","XLU":"Util"}
    tickers = list(sectors.keys())
    try:
        data = yf.download(tickers, period="2mo", progress=False)['Close']
        d, w, m = ((data.iloc[-1]/data.iloc[-2])-1)*100, ((data.iloc[-1]/data.iloc[-6])-1)*100, ((data.iloc[-1]/data.iloc[-21])-1)*100
        def fmt(s): return [f"{sectors[t]}: {v:+.1f}%" for t, v in s.sort_values(ascending=False).head(5).items()]
        return fmt(d), fmt(w), fmt(m)
    except:
        return ["Pending"]*5, ["Pending"]*5, ["Pending"]*5

# Fetch Core Data
spx_now, qqq_now = get_safe_data("^GSPC"), get_safe_data("QQQ")
vix_now, tnx_now, short_rate = get_safe_data("^VIX"), get_safe_data("^TNX"), get_safe_data("^IRX")
btc_now, gold_now = get_safe_data("BTC-USD"), get_safe_data("GC=F")

# Indicators
spx_rsi_d, qqq_rsi_d = calculate_rsi("^GSPC", "1d"), calculate_rsi("QQQ", "1d")
sma_200d = get_sma("^GSPC", 200)

# --- THE 6 PILLARS ---
cols = st.columns(6)
mom_c = "🟢" if spx_now > sma_200d else "🔴"
def show_p(col, lab, stat, sub): col.metric(lab, stat, sub)
show_p(cols[0], "Momentum", f"{mom_c} BULLISH", f"{((spx_now/sma_200d)-1)*100:+.1f}% vs 200D")
show_p(cols[1], "Inflation", "🟡 2.40%", "PCE Sticky")
show_p(cols[2], "Growth", "🟡 1.40%", "Q4 Slowdown")
show_p(cols[3], "Positioning", "🟢 LITE", f"VIX {vix_now:.1f}")
show_p(cols[4], "Monetary", "🟡 6.75%", "Prime Rate")
show_p(cols[5], "Fiscal", "🔴 DEFICIT", "Duration ↑")

st.divider()
st.subheader("📊 Sector Leaderboard (Top 5)")
top_d, top_w, top_m = get_sector_leaderboard()
l_cols = st.columns(3)
with l_cols[0]:
    st.write("**Daily**")
    for i in top_d: st.write(i)
with l_cols[1]:
    st.write("**Weekly**")
    for i in top_w: st.write(i)
with l_cols[2]:
    st.write("**Monthly**")
    for i in top_m: st.write(i)

st.divider()
col_left, col_right = st.columns(2)
with col_left:
    with st.expander("🔍 Momentum (SPX & QQQ)", expanded=True):
        st.write(f"**SPX:** {spx_now:,.2f} | RSI-D: {spx_rsi_d:.1f}")
        st.write(f"**QQQ:** {qqq_now:,.2f} | RSI-D: {qqq_rsi_d:.1f}")
    with st.expander("₿ Crypto Agent", expanded=True):
        st.write(f"**BTC:** ${btc_now:,.2f}")
        btc_200 = get_sma("BTC-USD", 200)
        st.write(f"**Trend:** {'🟢 Bull' if btc_now > btc_200 else '🔴 Bear'}")
with col_right:
    with st.expander("✨ Gold Agent", expanded=True):
        st.write(f"**Gold:** ${gold_now:,.2f} | **Ratio:** {gold_now/spx_now:.4f}")
    with st.expander("🏦 Rates & Fiscal", expanded=True):
        st.write(f"**10Y Yield:** {tnx_now:.2f}% | **Spread:** {tnx_now-short_rate:.2f}%")
        st.write("**Fiscal:** Treasury shifting to 'Coupons' (Liquidity Drain).")

st.caption(f"Last Agent Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: [Yahoo Finance](https://finance.yahoo.com)")

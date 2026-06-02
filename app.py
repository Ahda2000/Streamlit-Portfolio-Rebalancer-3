import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Allocator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #0f0f0f;
    --surface: #1a1a1a;
    --surface2: #222222;
    --border: #2e2e2e;
    --gold: #c9a84c;
    --gold-dim: #8a6f2e;
    --green: #4caf7d;
    --red: #e05c5c;
    --yellow: #d4a843;
    --text: #e8e2d6;
    --text-dim: #888880;
    --accent: #c9a84c;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

h1, h2, h3 { font-family: 'Playfair Display', serif; }

.header-block {
    border-left: 3px solid var(--gold);
    padding: 0.5rem 0 0.5rem 1.2rem;
    margin-bottom: 2rem;
}

.header-block h1 {
    font-size: 2.4rem;
    font-weight: 900;
    color: var(--text);
    margin: 0;
    letter-spacing: -0.5px;
}

.header-block p {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-dim);
    margin: 0.3rem 0 0 0;
    letter-spacing: 0.05em;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}

.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--gold);
}

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--gold-dim);
    margin: 2rem 0 0.8rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

.allocation-bar-bg {
    background: var(--surface2);
    border-radius: 3px;
    height: 6px;
    width: 100%;
    margin-top: 4px;
}

.tag-invest {
    background: rgba(76,175,125,0.15);
    color: var(--green);
    border: 1px solid rgba(76,175,125,0.3);
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
}

.tag-cash {
    background: rgba(212,168,67,0.12);
    color: var(--yellow);
    border: 1px solid rgba(212,168,67,0.3);
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
}

.tag-excluded {
    background: rgba(224,92,92,0.12);
    color: var(--red);
    border: 1px solid rgba(224,92,92,0.25);
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
}

.stDataFrame { background: var(--surface) !important; }

div[data-testid="stButton"] button {
    background: var(--gold);
    color: #0f0f0f;
    border: none;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    padding: 0.5rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
}

div[data-testid="stButton"] button:hover {
    background: #d4b060;
}

.footer-note {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-dim);
    text-align: center;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
}

.pos { color: var(--green); font-family: 'DM Mono', monospace; }
.neg { color: var(--red); font-family: 'DM Mono', monospace; }
.neu { color: var(--text-dim); font-family: 'DM Mono', monospace; }
.mono { font-family: 'DM Mono', monospace; font-size: 0.85rem; }

table { width: 100%; border-collapse: collapse; }
th {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-dim);
    padding: 0.5rem 0.8rem;
    text-align: right;
    border-bottom: 1px solid var(--border);
}
th:first-child { text-align: left; }
td {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    padding: 0.55rem 0.8rem;
    border-bottom: 1px solid #1e1e1e;
    text-align: right;
    color: var(--text);
}
td:first-child { text-align: left; font-weight: 500; }
tr:hover td { background: var(--surface2); }
</style>
""", unsafe_allow_html=True)

# ── Universe ──────────────────────────────────────────────────────────────────
TICKERS = [
    "VGT", "VHT", "GLD", "BLOK",
    "BND", "BNDX", "BRK-B", "PDBC",
    "VB", "VEA", "VNQ", "VNQI",
    "VO", "VV", "VWO"
]

TICKER_NAMES = {
    "VGT": "US Tech / AI",
    "VHT": "Healthcare",
    "GLD": "Gold",
    "BLOK": "Crypto-Adjacent",
    "BND": "US Bonds",
    "BNDX": "Intl Bonds",
    "BRK-B": "Value / Compounding",
    "PDBC": "Commodities",
    "VB": "US Small Cap",
    "VEA": "Intl Developed",
    "VNQ": "US Real Estate",
    "VNQI": "Intl Real Estate",
    "VO": "US Mid Cap",
    "VV": "US Large Cap",
    "VWO": "Emerging Markets",
}

# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_data():
    end = datetime.today()
    # Extra buffer to ensure 252 trading days
    start = end - timedelta(days=420)

    raw = yf.download(TICKERS, start=start, end=end, auto_adjust=True, progress=False)

    # yfinance returns MultiIndex columns when multiple tickers
    # Structure is (field, ticker) — extract Close
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"].copy()
    else:
        # Single ticker fallback
        close = raw[["Close"]].copy()
        close.columns = TICKERS[:1]

    # Rename BRK-B if yfinance returns it differently
    rename_map = {}
    for col in close.columns:
        if "BRK" in str(col).upper():
            rename_map[col] = "BRK-B"
    if rename_map:
        close = close.rename(columns=rename_map)

    return close

@st.cache_data(ttl=3600)
def fetch_fx():
    fx = yf.Ticker("USDSGD=X")
    hist = fx.history(period="5d")
    if not hist.empty:
        return round(hist["Close"].iloc[-1], 4)
    return None

# ── Calculations ──────────────────────────────────────────────────────────────
def compute_metrics(close_df):
    results = {}

    for ticker in TICKERS:
        col = ticker
        if col not in close_df.columns:
            continue

        series = close_df[col].dropna()
        if len(series) < 210:
            continue

        # Keep last 252 trading days
        series = series.iloc[-252:]
        price_today = series.iloc[-1]

        # 200D SMA
        sma200 = series.mean()
        vs_200sma = (price_today - sma200) / sma200

        # Performance periods
        def perf(n_days):
            if len(series) < n_days + 1:
                return None
            past = series.iloc[-(n_days + 1)]
            return (price_today - past) / past

        perf_1m = perf(21)   # ~1 month
        perf_6m = perf(126)  # ~6 months
        perf_12m = perf(252) # ~12 months

        if any(x is None for x in [perf_1m, perf_6m, perf_12m]):
            continue

        avg_perf = (perf_1m + perf_6m + perf_12m) / 3

        # Inverse volatility (squared return method matching your spreadsheet)
        daily_returns = series.pct_change().dropna()
        squared_returns = daily_returns ** 2
        sum_sq = squared_returns.sum()
        volatility = sum_sq ** 0.5
        inverse_vol = 1 / volatility if volatility > 0 else 0

        results[ticker] = {
            "price": price_today,
            "sma200": sma200,
            "vs_200sma": vs_200sma,
            "perf_1m": perf_1m,
            "perf_6m": perf_6m,
            "perf_12m": perf_12m,
            "avg_perf": avg_perf,
            "volatility": volatility,
            "inverse_vol": inverse_vol,
            "investable": vs_200sma > 0,
        }

    return results

def compute_allocation(metrics):
    # Step 1: rank all tickers by avg performance, pick top 6
    ranked = sorted(metrics.items(), key=lambda x: x[1]["avg_perf"], reverse=True)
    top6 = ranked[:6]

    # Step 2: apply 200D SMA filter — negative = cash for that slot
    # Step 3: compute inverse vol weights across the 6 slots
    total_inv_vol = sum(d["inverse_vol"] for _, d in top6)

    allocation = []
    for ticker, d in top6:
        weight = d["inverse_vol"] / total_inv_vol if total_inv_vol > 0 else 1/6
        status = "INVEST" if d["investable"] else "CASH (SGD)"
        allocation.append({
            "ticker": ticker,
            "name": TICKER_NAMES.get(ticker, ""),
            "price": d["price"],
            "vs_200sma": d["vs_200sma"],
            "avg_perf": d["avg_perf"],
            "perf_1m": d["perf_1m"],
            "perf_6m": d["perf_6m"],
            "perf_12m": d["perf_12m"],
            "weight": weight,
            "status": status,
            "investable": d["investable"],
        })

    return allocation, ranked

# ── Formatting helpers ────────────────────────────────────────────────────────
def fmt_pct(val, decimals=2):
    if val is None:
        return "—"
    sign = "+" if val > 0 else ""
    return f"{sign}{val*100:.{decimals}f}%"

def color_pct(val, decimals=2):
    if val is None:
        return "<span class='neu'>—</span>"
    cls = "pos" if val > 0 else ("neg" if val < 0 else "neu")
    sign = "+" if val > 0 else ""
    return f"<span class='{cls}'>{sign}{val*100:.{decimals}f}%</span>"

# ── Main app ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-block">
    <h1>Portfolio Allocator</h1>
    <p>TREND-FOLLOWING · INVERSE VOLATILITY WEIGHTING · MONTHLY REBALANCE</p>
</div>
""", unsafe_allow_html=True)

# Controls row
col_refresh, col_date, col_fx, col_spacer = st.columns([1, 2, 2, 4])

with col_refresh:
    refresh = st.button("↻ Refresh")

if refresh:
    st.cache_data.clear()

# Load data
with st.spinner("Fetching market data…"):
    try:
        close_df = fetch_data()
        fx_rate = fetch_fx()

        # ── Debug expander ────────────────────────────────────────────────
        with st.expander("🔍 Debug info (open if tables are empty)"):
            st.write(f"**Close DataFrame shape:** {close_df.shape}")
            st.write(f"**Columns returned:** {list(close_df.columns)}")
            st.write(f"**FX rate (USD/SGD):** {fx_rate}")
            missing = [t for t in TICKERS if t not in close_df.columns]
            if missing:
                st.warning(f"Missing tickers: {missing}")
            short = [t for t in TICKERS if t in close_df.columns and close_df[t].dropna().shape[0] < 210]
            if short:
                st.warning(f"Insufficient history (<210 rows): {short}")
            st.dataframe(close_df.tail(3))

        metrics = compute_metrics(close_df)
        st.write(f"**Tickers with valid metrics:** {list(metrics.keys())}")

        if len(metrics) < 6:
            st.error(f"Only {len(metrics)} tickers have sufficient data. Need at least 6. Check debug info above.")
            data_ok = False
        else:
            allocation, ranked = compute_allocation(metrics)
            data_ok = True

    except Exception as e:
        import traceback
        st.error(f"Data fetch error: {e}")
        st.code(traceback.format_exc())
        data_ok = False

if data_ok:
    now = datetime.now().strftime("%d %b %Y, %H:%M")

    with col_date:
        st.markdown(f"""
        <div class="metric-card" style="padding:0.7rem 1rem;">
            <div class="metric-label">As of</div>
            <div class="metric-value" style="font-size:1rem;">{now}</div>
        </div>""", unsafe_allow_html=True)

    with col_fx:
        fx_display = f"{fx_rate:.4f}" if fx_rate else "N/A"
        st.markdown(f"""
        <div class="metric-card" style="padding:0.7rem 1rem;">
            <div class="metric-label">USD / SGD</div>
            <div class="metric-value" style="font-size:1rem;">{fx_display}</div>
        </div>""", unsafe_allow_html=True)

    # ── Section 1: Monthly Allocation ────────────────────────────────────────
    st.markdown('<div class="section-label">① Monthly Allocation — Top 6</div>', unsafe_allow_html=True)

    alloc_html = """
    <table>
    <tr>
        <th>Ticker</th>
        <th>Asset Class</th>
        <th>Price</th>
        <th>vs 200D SMA</th>
        <th>1M</th>
        <th>6M</th>
        <th>12M</th>
        <th>Avg Perf</th>
        <th>Weight</th>
        <th>Status</th>
    </tr>
    """

    for row in allocation:
        status_tag = (
            f"<span class='tag-invest'>INVEST</span>"
            if row["investable"]
            else f"<span class='tag-cash'>CASH (SGD)</span>"
        )
        alloc_html += f"""
        <tr>
            <td><strong>{row['ticker']}</strong></td>
            <td style="color:#888880;font-size:0.75rem;">{row['name']}</td>
            <td>${row['price']:.2f}</td>
            <td>{color_pct(row['vs_200sma'])}</td>
            <td>{color_pct(row['perf_1m'])}</td>
            <td>{color_pct(row['perf_6m'])}</td>
            <td>{color_pct(row['perf_12m'])}</td>
            <td>{color_pct(row['avg_perf'])}</td>
            <td><strong style="color:#c9a84c;">{row['weight']*100:.2f}%</strong></td>
            <td>{status_tag}</td>
        </tr>
        """

    alloc_html += "</table>"
    st.markdown(alloc_html, unsafe_allow_html=True)

    # Visual weight bars
    st.markdown("<br>", unsafe_allow_html=True)
    bar_cols = st.columns(6)
    for i, row in enumerate(allocation):
        with bar_cols[i]:
            color = "#4caf7d" if row["investable"] else "#d4a843"
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="font-family:'DM Mono',monospace;font-size:0.75rem;color:#888880;">{row['ticker']}</div>
                <div style="font-family:'DM Mono',monospace;font-size:1.1rem;font-weight:500;color:{color};">{row['weight']*100:.1f}%</div>
                <div style="background:#2e2e2e;border-radius:3px;height:4px;margin-top:4px;">
                    <div style="background:{color};border-radius:3px;height:4px;width:{row['weight']*100:.1f}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Section 2: Full Universe Momentum ────────────────────────────────────
    st.markdown('<div class="section-label">② Full Universe — Momentum Screen</div>', unsafe_allow_html=True)

    universe_html = """
    <table>
    <tr>
        <th>Rank</th>
        <th>Ticker</th>
        <th>Asset Class</th>
        <th>Price</th>
        <th>200D SMA</th>
        <th>vs 200D SMA</th>
        <th>1M</th>
        <th>6M</th>
        <th>12M</th>
        <th>Avg Perf</th>
        <th>Signal</th>
    </tr>
    """

    for rank, (ticker, d) in enumerate(ranked, 1):
        in_top6 = rank <= 6
        signal = (
            f"<span class='tag-invest'>▲ INVEST</span>" if d["investable"]
            else f"<span class='tag-cash'>▼ CASH</span>"
        )
        row_style = "" if in_top6 else "opacity:0.45;"
        rank_display = f"<strong style='color:#c9a84c;'>{rank}</strong>" if in_top6 else str(rank)

        universe_html += f"""
        <tr style="{row_style}">
            <td>{rank_display}</td>
            <td><strong>{ticker}</strong></td>
            <td style="color:#888880;font-size:0.75rem;">{TICKER_NAMES.get(ticker,'')}</td>
            <td>${d['price']:.2f}</td>
            <td>${d['sma200']:.2f}</td>
            <td>{color_pct(d['vs_200sma'])}</td>
            <td>{color_pct(d['perf_1m'])}</td>
            <td>{color_pct(d['perf_6m'])}</td>
            <td>{color_pct(d['perf_12m'])}</td>
            <td>{color_pct(d['avg_perf'])}</td>
            <td>{signal if in_top6 else ''}</td>
        </tr>
        """

    universe_html += "</table>"
    st.markdown(universe_html, unsafe_allow_html=True)

    # ── Section 3: Rebalancing helper ────────────────────────────────────────
    st.markdown('<div class="section-label">③ Rebalancing Calculator</div>', unsafe_allow_html=True)

    st.markdown("""
    <p style="font-family:'DM Sans',sans-serif;font-size:0.85rem;color:#888880;margin-bottom:1rem;">
    Enter your current portfolio value in SGD to see target dollar amounts per slot.
    </p>
    """, unsafe_allow_html=True)

    portfolio_val = st.number_input(
        "Portfolio value (SGD)",
        min_value=0.0,
        value=10000.0,
        step=500.0,
        format="%.2f"
    )

    if portfolio_val > 0 and fx_rate:
        portfolio_usd = portfolio_val / fx_rate

        rebal_html = """
        <table>
        <tr>
            <th>Ticker</th>
            <th>Status</th>
            <th>Weight</th>
            <th>SGD Amount</th>
            <th>USD Amount</th>
            <th>Note</th>
        </tr>
        """

        for row in allocation:
            sgd_amt = row["weight"] * portfolio_val
            usd_amt = sgd_amt / fx_rate
            note = f"Buy ~{usd_amt/row['price']:.2f} units" if row["investable"] else "Keep as SGD cash"
            note_color = "#4caf7d" if row["investable"] else "#d4a843"
            status_tag = (
                f"<span class='tag-invest'>INVEST</span>"
                if row["investable"]
                else f"<span class='tag-cash'>CASH</span>"
            )

            rebal_html += f"""
            <tr>
                <td><strong>{row['ticker']}</strong></td>
                <td>{status_tag}</td>
                <td style="color:#c9a84c;">{row['weight']*100:.2f}%</td>
                <td>S${sgd_amt:,.2f}</td>
                <td>${usd_amt:,.2f}</td>
                <td style="color:{note_color};font-size:0.78rem;">{note}</td>
            </tr>
            """

        rebal_html += "</table>"
        st.markdown(rebal_html, unsafe_allow_html=True)

        # Summary
        invested = sum(r["weight"] for r in allocation if r["investable"]) * portfolio_val
        cash_sgd = sum(r["weight"] for r in allocation if not r["investable"]) * portfolio_val

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="metric-card" style="margin-top:1rem;">
                <div class="metric-label">To Invest (USD-denominated)</div>
                <div class="metric-value" style="color:#4caf7d;">S${invested:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card" style="margin-top:1rem;">
                <div class="metric-label">To Keep as SGD Cash</div>
                <div class="metric-value" style="color:#d4a843;">S${cash_sgd:,.2f}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-note">
        Data via Yahoo Finance · Rebalance monthly · Not financial advice · Built for personal use
    </div>
    """, unsafe_allow_html=True)

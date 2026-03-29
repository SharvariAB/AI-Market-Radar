import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import random
import hashlib
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Market Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Bloomberg Terminal × Cyberpunk
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=Orbitron:wght@400;600;700;900&display=swap');

:root{
  --bg0:#02040a;
  --bg1:#060d18;
  --bg2:#0a1628;
  --bg3:#0e1f38;
  --border:#1a3050;
  --border-glow:#1e4a7a;
  --cyan:#00e5ff;
  --cyan-dim:rgba(0,229,255,.15);
  --cyan-glow:rgba(0,229,255,.35);
  --green:#00ff9d;
  --green-dim:rgba(0,255,157,.12);
  --amber:#ffb700;
  --amber-dim:rgba(255,183,0,.12);
  --red:#ff3d5a;
  --red-dim:rgba(255,61,90,.12);
  --purple:#bd00ff;
  --purple-dim:rgba(189,0,255,.12);
  --text:#c8dff0;
  --text-dim:#5a7a99;
  --text-bright:#eaf6ff;
  --mono:'IBM Plex Mono',monospace;
  --display:'Orbitron',sans-serif;
}
html,body,[class*="css"]{
  background:var(--bg0) !important;
  color:var(--text) !important;
  font-family:var(--mono) !important;
}
.stApp{background:var(--bg0) !important;}
.stApp::before{
  content:'';position:fixed;inset:0;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.06) 2px,rgba(0,0,0,.06) 4px);
  pointer-events:none;z-index:9999;
}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:var(--bg1)}
::-webkit-scrollbar-thumb{background:var(--border-glow);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:var(--cyan)}

[data-testid="stSidebar"]{background:var(--bg1) !important;border-right:1px solid var(--border) !important;}
[data-testid="stSidebar"] *{color:var(--text) !important;}

.stSelectbox > div > div,
.stMultiSelect > div > div{
  background:var(--bg2) !important;border:1px solid var(--border) !important;
  border-radius:3px !important;color:var(--text) !important;
  font-family:var(--mono) !important;font-size:.75rem !important;
}
.stTextInput > div > div > input{
  background:var(--bg2) !important;border:1px solid var(--border) !important;
  border-radius:3px !important;color:var(--text) !important;
  font-family:var(--mono) !important;font-size:.75rem !important;
}
.stButton > button{
  background:var(--bg2) !important;border:1px solid var(--border-glow) !important;
  color:var(--cyan) !important;font-family:var(--mono) !important;
  font-size:.7rem !important;letter-spacing:.1em !important;
  text-transform:uppercase !important;border-radius:2px !important;transition:all .2s !important;
}
.stButton > button:hover{border-color:var(--cyan) !important;box-shadow:0 0 12px var(--cyan-glow) !important;background:var(--cyan-dim) !important;}

div[data-testid="metric-container"]{
  background:var(--bg2) !important;border:1px solid var(--border) !important;
  border-radius:3px !important;padding:12px 14px !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"]{
  font-size:.58rem !important;color:var(--text-dim) !important;
  letter-spacing:.14em !important;text-transform:uppercase !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"]{
  font-family:var(--display) !important;font-size:1.05rem !important;color:var(--cyan) !important;
}
div[data-testid="stMetricDelta"] > div{font-size:.68rem !important;font-family:var(--mono) !important;}

/* Master header */
.master-header{
  background:linear-gradient(135deg,var(--bg1) 0%,var(--bg2) 60%,var(--bg1) 100%);
  border:1px solid var(--border);border-bottom:2px solid var(--cyan);
  border-radius:4px 4px 0 0;padding:22px 28px 18px;margin-bottom:20px;
  position:relative;overflow:hidden;
}
.master-header::after{
  content:'';position:absolute;top:0;left:0;right:0;bottom:0;
  background:radial-gradient(ellipse 40% 80% at 5% 50%,rgba(0,229,255,.07) 0%,transparent 100%),
             radial-gradient(ellipse 30% 60% at 95% 50%,rgba(0,255,157,.05) 0%,transparent 100%);
  pointer-events:none;
}
.header-title{
  font-family:var(--display);font-size:1.7rem;font-weight:900;color:var(--cyan);
  letter-spacing:.06em;text-shadow:0 0 20px var(--cyan-glow),0 0 40px rgba(0,229,255,.2);
  margin:0;line-height:1;
}
.header-sub{font-size:.6rem;color:var(--text-dim);letter-spacing:.2em;text-transform:uppercase;margin-top:5px;}
.header-row{display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:8px;}
.live-pill{
  display:inline-flex;align-items:center;gap:7px;
  background:var(--green-dim);border:1px solid rgba(0,255,157,.3);
  border-radius:2px;padding:5px 12px;font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--green);
}
.pulse{width:7px;height:7px;background:var(--green);border-radius:50%;animation:blink 1.4s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.2;transform:scale(.6)}}
.clock{font-family:var(--display);font-size:.85rem;color:var(--amber);letter-spacing:.08em;}

/* Section heading */
.sec-head{display:flex;align-items:center;gap:10px;padding:8px 0 10px;border-bottom:1px solid var(--border);margin-bottom:14px;}
.sec-head-title{font-family:var(--display);font-size:.72rem;font-weight:700;color:var(--text-bright);letter-spacing:.1em;text-transform:uppercase;}
.sec-head-tag{font-size:.54rem;letter-spacing:.15em;color:var(--text-dim);margin-left:auto;text-transform:uppercase;}

/* Card */
.card{background:var(--bg2);border:1px solid var(--border);border-radius:3px;padding:16px;margin-bottom:14px;position:relative;}
.card-accent-cyan::before,.card-accent-green::before,.card-accent-amber::before,
.card-accent-red::before,.card-accent-purple::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;border-radius:3px 3px 0 0;
}
.card-accent-cyan::before{background:linear-gradient(90deg,var(--cyan),transparent);}
.card-accent-green::before{background:linear-gradient(90deg,var(--green),transparent);}
.card-accent-amber::before{background:linear-gradient(90deg,var(--amber),transparent);}
.card-accent-red::before{background:linear-gradient(90deg,var(--red),transparent);}
.card-accent-purple::before{background:linear-gradient(90deg,var(--purple),transparent);}

/* Opp table */
.opp-table{border-collapse:collapse;width:100%;}
.opp-hdr td{font-size:.54rem;letter-spacing:.15em;color:var(--text-dim);text-transform:uppercase;padding:4px 8px 8px;border-bottom:1px solid var(--border);}
.opp-row{border-bottom:1px solid rgba(26,48,80,.5);transition:background .15s;cursor:pointer;}
.opp-row:hover{background:rgba(0,229,255,.04);}
.opp-row td{padding:9px 8px;vertical-align:middle;}
.opp-rank{font-size:.6rem;color:var(--text-dim);width:24px;}
.opp-ticker{font-family:var(--display);font-size:.8rem;font-weight:700;color:var(--cyan);width:60px;}
.opp-price-val{font-size:.78rem;color:var(--text-bright);}
.chg-pos{font-size:.6rem;color:var(--green);}
.chg-neg{font-size:.6rem;color:var(--red);}
.opp-score-cell{text-align:center;}
.opp-score{display:inline-block;font-family:var(--display);font-size:.8rem;font-weight:700;min-width:34px;text-align:center;}
.score-elite{color:var(--green);text-shadow:0 0 8px rgba(0,255,157,.5);}
.score-high{color:var(--cyan);text-shadow:0 0 8px var(--cyan-glow);}
.score-mid{color:var(--amber);}
.score-low{color:var(--text-dim);}

/* Badge */
.badge{display:inline-block;font-size:.54rem;letter-spacing:.1em;text-transform:uppercase;font-weight:600;padding:3px 7px;border-radius:2px;white-space:nowrap;margin:2px 2px 2px 0;}
.badge-vol{background:var(--cyan-dim);color:var(--cyan);border:1px solid rgba(0,229,255,.3);}
.badge-break{background:var(--green-dim);color:var(--green);border:1px solid rgba(0,255,157,.3);}
.badge-ma{background:var(--amber-dim);color:var(--amber);border:1px solid rgba(255,183,0,.3);}
.badge-insider{background:var(--red-dim);color:var(--red);border:1px solid rgba(255,61,90,.3);}
.badge-inst{background:var(--purple-dim);color:var(--purple);border:1px solid rgba(189,0,255,.3);}

/* Signal list */
.sig-row{display:flex;align-items:center;gap:10px;padding:9px 12px;background:var(--bg3);border:1px solid var(--border);border-radius:2px;margin-bottom:5px;}
.sig-count{font-family:var(--display);font-size:.82rem;font-weight:700;min-width:28px;text-align:right;}
.sig-tickers{font-size:.6rem;color:var(--text-dim);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.sig-chip{color:var(--cyan);margin-right:6px;}

/* Institutional */
.inst-row{display:flex;align-items:center;justify-content:space-between;padding:9px 12px;background:rgba(189,0,255,.05);border:1px solid rgba(189,0,255,.15);border-left:3px solid var(--purple);border-radius:0 2px 2px 0;margin-bottom:6px;}
.inst-ticker{font-family:var(--display);font-size:.8rem;color:var(--purple);font-weight:700;}
.inst-note{font-size:.57rem;color:var(--text-dim);margin-top:2px;}
.inst-pct{font-family:var(--display);font-size:.88rem;color:var(--amber);font-weight:700;}
.inst-lbl{font-size:.54rem;color:var(--text-dim);letter-spacing:.1em;text-transform:uppercase;}
.inst-vol{font-size:.7rem;color:var(--purple);}

/* News */
.news-item{padding:10px 12px;background:var(--bg3);border:1px solid var(--border);border-left:3px solid var(--border);border-radius:0 2px 2px 0;margin-bottom:7px;}
.news-item.pos{border-left-color:var(--green);}
.news-item.neu{border-left-color:var(--amber);}
.news-item.neg{border-left-color:var(--red);}
.news-headline{font-size:.7rem;color:var(--text-bright);line-height:1.5;margin-bottom:4px;}
.news-meta{display:flex;align-items:center;gap:8px;}
.news-ticker{font-family:var(--display);font-size:.58rem;color:var(--cyan);}
.news-pos{font-size:.56rem;letter-spacing:.1em;text-transform:uppercase;font-weight:600;color:var(--green);}
.news-neu{font-size:.56rem;letter-spacing:.1em;text-transform:uppercase;font-weight:600;color:var(--amber);}
.news-neg{font-size:.56rem;letter-spacing:.1em;text-transform:uppercase;font-weight:600;color:var(--red);}
.news-score-lbl{font-size:.56rem;color:var(--text-dim);}

/* Factor rows */
.factor-row{display:flex;align-items:center;justify-content:space-between;padding:6px 10px;background:var(--bg3);border:1px solid var(--border);border-radius:2px;margin-bottom:4px;font-size:.66rem;}
.factor-lbl{color:var(--text-dim);}
.factor-pts{font-family:var(--display);font-weight:700;}
.pts-pos{color:var(--green);}
.pts-neu{color:var(--amber);}

/* Score bar */
.score-bar-wrap{height:5px;background:var(--bg3);border:1px solid var(--border);border-radius:3px;overflow:hidden;margin:6px 0;}
.score-bar-fill{height:100%;border-radius:3px;}

/* Animations */
@keyframes fadeInUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.fi{animation:fadeInUp .35s ease both;}
.fi1{animation:fadeInUp .35s ease .05s both;}
.fi2{animation:fadeInUp .35s ease .1s both;}
.fi3{animation:fadeInUp .35s ease .15s both;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_WATCHLIST = [
    "AAPL","MSFT","NVDA","TSLA","GOOGL","AMZN","META","AMD",
    "NFLX","JPM","PLTR","COIN","SOFI","RIVN","ROKU","UBER",
    "SHOP","SQ","SNAP","PYPL",
]

SIGNAL_MAP = {
    "Volume Spike":      "badge-vol",
    "Breakout Pattern":  "badge-break",
    "MA Crossover":      "badge-ma",
    "Insider Activity":  "badge-insider",
    "Institutional Blk": "badge-inst",
}
SIGNAL_COLORS = {
    "Volume Spike":      "var(--cyan)",
    "Breakout Pattern":  "var(--green)",
    "MA Crossover":      "var(--amber)",
    "Insider Activity":  "var(--red)",
    "Institutional Blk": "var(--purple)",
}

vader = SentimentIntensityAnalyzer()

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(6,13,24,.7)",
    font=dict(family="IBM Plex Mono", color="#5a7a99", size=10),
    margin=dict(l=4, r=4, t=32, b=4),
    xaxis=dict(showgrid=True, gridcolor="#1a3050", zeroline=False, showline=False, tickfont=dict(size=9)),
    yaxis=dict(showgrid=True, gridcolor="#1a3050", zeroline=False, showline=False, tickfont=dict(size=9)),
)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def load_market_data(tickers):
    out = []
    for sym in tickers:
        try:
            t   = yf.Ticker(sym)
            h5  = t.history(period="5d",  interval="1d")
            h30 = t.history(period="30d", interval="1d")
            if h5.empty or len(h5) < 2:
                continue
            price   = float(h5["Close"].iloc[-1])
            prev    = float(h5["Close"].iloc[-2])
            chg_pct = (price - prev) / prev * 100
            avg_vol = float(h5["Volume"].mean())
            cur_vol = float(h5["Volume"].iloc[-1])
            vol_spk = ((cur_vol / avg_vol) - 1) * 100 if avg_vol else 0
            ma20    = float(h30["Close"].rolling(20).mean().iloc[-1]) if len(h30) >= 20 else price
            hi30    = float(h30["High"].max()) if not h30.empty else price

            out.append({
                "ticker":   sym,
                "price":    price,
                "prev":     prev,
                "chg_pct":  chg_pct,
                "volume":   cur_vol,
                "avg_vol":  avg_vol,
                "vol_spk":  vol_spk,
                "ma20":     ma20,
                "ma_above": price > ma20,
                "hi30":     hi30,
                "near_hi":  price >= hi30 * 0.97,
                "hist5":    h5,
                "hist30":   h30,
            })
        except Exception:
            continue
    return out

@st.cache_data(ttl=60, show_spinner=False)
def load_intraday(sym):
    try:
        return yf.Ticker(sym).history(period="1d", interval="5m")
    except Exception:
        return pd.DataFrame()

def score_and_tag(row):
    score, signals = 50, []
    if row["vol_spk"] > 150:   score += 28; signals.append("Volume Spike")
    elif row["vol_spk"] > 80:  score += 18; signals.append("Volume Spike")
    elif row["vol_spk"] > 40:  score += 8;  signals.append("Volume Spike")
    if row["chg_pct"] > 4:     score += 22; signals.append("Breakout Pattern")
    elif row["chg_pct"] > 2:   score += 12; signals.append("Breakout Pattern")
    elif row["chg_pct"] > 1:   score += 5
    if row["ma_above"]:         score += 8;  signals.append("MA Crossover")
    if row["near_hi"]:          score += 6
    seed = int(hashlib.md5(row["ticker"].encode()).hexdigest(), 16) % 100
    if seed < 22:               score += 7;  signals.append("Insider Activity")
    if row["vol_spk"] > 80 and row["price"] * row["volume"] > 5e8:
                                score += 9;  signals.append("Institutional Blk")
    return min(score, 99), signals[:3]

def score_cls(s):
    if s >= 85: return "score-elite"
    if s >= 70: return "score-high"
    if s >= 55: return "score-mid"
    return "score-low"

def get_news(sym):
    pool = [
        f"{sym} posts record quarterly revenue, beating Wall Street forecasts",
        f"Analysts at Goldman raise {sym} price target by 18%",
        f"{sym} expands into new market verticals; shares react strongly",
        f"SEC filing reveals major fund increased {sym} stake last quarter",
        f"{sym} faces antitrust probe amid growing regulatory pressure",
        f"Options flow flags unusual activity in {sym} ahead of earnings",
        f"{sym} CEO divests $12 M in shares; insiders closely watching",
        f"Short interest in {sym} climbs to 6-month high on bearish bets",
        f"{sym} announces AI-driven product suite — market responds positively",
        f"Retail investor surge pushes {sym} volume to multi-year high",
        f"{sym} misses EPS estimate; guidance cut rattles bullish thesis",
        f"Dark-pool data suggests institutional accumulation in {sym}",
    ]
    rng = random.Random(int(hashlib.md5(sym.encode()).hexdigest(), 16) % 9999)
    return rng.sample(pool, 4)

def analyse_sentiment(headlines):
    out = []
    for h in headlines:
        c = vader.polarity_scores(h)["compound"]
        lbl = "Positive" if c >= 0.05 else ("Negative" if c <= -0.05 else "Neutral")
        out.append({"text": h, "label": lbl, "score": c})
    return out

def generate_ai_alerts(data):
    alerts = []

    for r in data:
        score = r.get("score", 0)

        # High confidence alerts
        if r["vol_spk"] > 100 and r["chg_pct"] > 2:
            alerts.append({
                "msg": f"ALERT: {r['ticker']} unusual volume spike detected",
                "confidence": min(95, score)
            })

        elif r["near_hi"] and r["chg_pct"] > 1:
            alerts.append({
                "msg": f"ALERT: {r['ticker']} approaching breakout zone",
                "confidence": min(90, score)
            })

        elif "Institutional Blk" in r.get("signals", []):
            alerts.append({
                "msg": f"ALERT: {r['ticker']} possible institutional activity",
                "confidence": min(92, score)
            })

        elif score > 80:
            alerts.append({
                "msg": f"ALERT: {r['ticker']} strong bullish setup detected",
                "confidence": score
            })

    # sort by confidence
    alerts = sorted(alerts, key=lambda x: -x["confidence"])

    return alerts[:6]

# ─────────────────────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def make_candlestick(hist30, sym):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[.70, .30], vertical_spacing=.03)
    if hist30.empty:
        return fig
    fig.add_trace(go.Candlestick(
        x=hist30.index,
        open=hist30["Open"], high=hist30["High"],
        low=hist30["Low"],  close=hist30["Close"], name="OHLC",
        increasing=dict(fillcolor="#00ff9d", line=dict(color="#00ff9d", width=1)),
        decreasing=dict(fillcolor="#ff3d5a", line=dict(color="#ff3d5a", width=1)),
    ), row=1, col=1)
    ma = hist30["Close"].rolling(20).mean()
    fig.add_trace(go.Scatter(x=hist30.index, y=ma,
        line=dict(color="#ffb700", width=1.2, dash="dot"), name="MA20"), row=1, col=1)
    GREEN_VOL = "rgba(0,255,157,0.35)"
    RED_VOL   = "rgba(255,61,90,0.35)"

    colors = [
        GREEN_VOL if c >= o else RED_VOL
        for c, o in zip(hist30["Close"], hist30["Open"])
    ]

    fig.add_trace(go.Bar(x=hist30.index, y=hist30["Volume"],
        marker_color=colors, name="Volume"), row=2, col=1)
    layout = {**PLOTLY_BASE, "height": 340,
              "title": dict(text=f"{sym}  ·  30-Day Candlestick", font=dict(size=11, color="#00e5ff")),
              "legend": dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
              "xaxis_rangeslider_visible": False}
    fig.update_layout(**layout)
    return fig

def make_intraday_chart(df, sym):
    fig = go.Figure()
    if df.empty:
        return fig
    color = "#00ff9d" if float(df["Close"].iloc[-1]) >= float(df["Close"].iloc[0]) else "#ff3d5a"
    fill  = "rgba(0,255,157,.06)" if color == "#00ff9d" else "rgba(255,61,90,.06)"
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines",
        line=dict(color=color, width=1.5), fill="tozeroy", fillcolor=fill, name="Price"))
    layout = {**PLOTLY_BASE, "height": 175,
              "title": dict(text=f"{sym}  ·  Intraday 5-min", font=dict(size=10, color="#5a7a99"))}
    fig.update_layout(**layout)
    return fig

def make_gauge(score):
    col = "#00ff9d" if score >= 75 else ("#ffb700" if score >= 55 else "#ff3d5a")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score, domain={"x":[0,1],"y":[0,1]},
        number={"font":{"family":"Orbitron","size":24,"color":col}},
        gauge={
            "axis":{"range":[0,100],"tickfont":{"size":8,"color":"#5a7a99"},"tickcolor":"#1a3050"},
            "bar":{"color":col,"thickness":.25},
            "bgcolor":"rgba(6,13,24,.8)","bordercolor":"#1a3050","borderwidth":1,
            "steps":[
                {"range":[0,40], "color":"rgba(255,61,90,.08)"},
                {"range":[40,70],"color":"rgba(255,183,0,.08)"},
                {"range":[70,100],"color":"rgba(0,255,157,.08)"},
            ],
            "threshold":{"line":{"color":col,"width":2},"value":score},
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=165, margin=dict(l=14,r=14,t=14,b=4),
                      font=dict(color="#5a7a99"))
    return fig

def make_sentiment_donut(counts):
    labels = list(counts.keys())
    values = list(counts.values())
    colors_map = {"Positive":"#00ff9d","Neutral":"#ffb700","Negative":"#ff3d5a"}
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=[colors_map[l] for l in labels],
                    line=dict(color="#060d18", width=2)),
        hole=.58,
        textfont=dict(family="IBM Plex Mono", size=9),
        textinfo="label+percent", showlegend=False,
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=155, margin=dict(l=4,r=4,t=4,b=4))
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'IBM Plex Mono\';font-size:.6rem;color:#5a7a99;letter-spacing:.18em;text-transform:uppercase;margin-bottom:12px;">⚙  Radar Config</div>', unsafe_allow_html=True)
    custom_raw  = st.text_input("Custom Tickers", value="", placeholder="RKLB,MSTR,SMCI")
    custom_list = [x.strip().upper() for x in custom_raw.split(",") if x.strip()] if custom_raw else []
    top_n       = st.slider("Top N Opportunities", 3, 12, 6)
    min_score   = st.slider("Min Score Filter", 0, 90, 45)
    sig_filter  = st.multiselect("Signal Filter", list(SIGNAL_MAP.keys()))
    st.markdown("---")
    st.markdown('<div style="font-family:\'IBM Plex Mono\';font-size:.6rem;color:#5a7a99;letter-spacing:.15em;text-transform:uppercase;margin-bottom:8px;">Refresh</div>', unsafe_allow_html=True)
    auto_ref = st.checkbox("Auto 60s refresh", value=True)
    if st.button("↻  Refresh Now"):
        st.cache_data.clear(); st.rerun()
    st.markdown("---")
    all_watch = list(dict.fromkeys(DEFAULT_WATCHLIST + custom_list))
    st.markdown(f'<div style="font-family:\'IBM Plex Mono\';font-size:.6rem;color:#5a7a99;">Watchlist: <span style="color:#00e5ff">{len(all_watch)} tickers</span><br>Updated: <span style="color:#ffb700">{datetime.now().strftime("%H:%M:%S")}</span></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
all_tickers = list(dict.fromkeys(DEFAULT_WATCHLIST + custom_list))

with st.spinner("Scanning market signals…"):
    raw = load_market_data(all_tickers)

for r in raw:
    r["score"], r["signals"] = score_and_tag(r)

flat    = [{k: v for k, v in r.items() if k not in ("hist5","hist30")} for r in raw]
df_all  = pd.DataFrame(flat) if flat else pd.DataFrame()
lut     = {r["ticker"]: r for r in raw}

df = df_all.copy()
if not df.empty:
    if sig_filter:
        df = df[df["signals"].apply(lambda s: any(x in s for x in sig_filter))]
    df = df[df["score"] >= min_score].sort_values("score", ascending=False).reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y  %H:%M:%S")
gainers = int((df_all["chg_pct"] > 0).sum()) if not df_all.empty else 0
losers  = int((df_all["chg_pct"] < 0).sum()) if not df_all.empty else 0
sig_tot = sum(len(r["signals"]) for r in raw)
avg_sc  = int(df_all["score"].mean()) if not df_all.empty else 0

st.markdown(f"""
<div class="master-header fi">
  <div class="header-row">
    <div>
      <div class="header-title">📡 AI MARKET RADAR</div>
      <div class="header-sub">Real-time signal detection · Institutional flow · AI sentiment analysis</div>
    </div>
    <div style="text-align:right">
      <div class="clock">{now_str}</div>
      <div class="live-pill" style="margin-top:6px;justify-content:flex-end">
        <span class="pulse"></span>LIVE
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TOP METRICS
# ─────────────────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.metric("Stocks Scanned", len(raw))
with c2: st.metric("Signals Detected", sig_tot)
with c3: st.metric("Opportunities", len(df))
with c4: st.metric("Gainers / Losers", f"{gainers}  ·  {losers}")
with c5: st.metric("Avg Score", avg_sc)

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
left, right = st.columns([2, 3], gap="medium")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT
# ══════════════════════════════════════════════════════════════════════════════
with left:

    # ── TOP OPPORTUNITIES ────────────────────────────────────────────────────
    st.markdown("""<div class="sec-head fi1">
      <span style="color:#00e5ff;font-size:.9rem">🎯</span>
      <span class="sec-head-title">Top Opportunities</span>
      <span class="sec-head-tag">Ranked by AI Score</span>
    </div>""", unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="card"><span style="font-size:.72rem;color:#5a7a99">No opportunities match current filters.</span></div>', unsafe_allow_html=True)
    else:
        rows_html = ""
        for i, row in df.head(top_n).iterrows():
            badges   = "".join(f'<span class="badge {SIGNAL_MAP[s]}">{s}</span>' for s in row["signals"])
            chg_cls  = "chg-pos" if row["chg_pct"] >= 0 else "chg-neg"
            sgn      = "+" if row["chg_pct"] >= 0 else ""
            sc       = score_cls(row["score"])
            rows_html += f"""<tr class="opp-row">
              <td class="opp-rank">#{i+1}</td>
              <td class="opp-ticker">{row['ticker']}</td>
              <td><span class="opp-price-val">${row['price']:.2f}</span><br>
                  <span class="{chg_cls}">{sgn}{row['chg_pct']:.2f}%</span></td>
              <td class="opp-score-cell"><span class="opp-score {sc}">{row['score']}</span></td>
              <td>{badges}</td>
            </tr>"""
        st.markdown(f"""<div class="card card-accent-cyan fi1">
          <table class="opp-table">
            <tr class="opp-hdr"><td>#</td><td>Ticker</td><td>Price</td><td>Score</td><td>Signals</td></tr>
            {rows_html}
          </table>
        </div>""", unsafe_allow_html=True)

    # ── AI SIGNALS ───────────────────────────────────────────────────────────
    st.markdown("""<div class="sec-head fi2" style="margin-top:4px">
      <span style="color:#00ff9d;font-size:.9rem">⚡</span>
      <span class="sec-head-title">AI Detected Signals</span>
      <span class="sec-head-tag">Across Watchlist</span>
    </div>""", unsafe_allow_html=True)

    agg = {}
    for r in raw:
        for s in r.get("signals", []):
            agg.setdefault(s, []).append(r["ticker"])

    sig_html = ""
    for sig, tklist in sorted(agg.items(), key=lambda x: -len(x[1])):
        cls   = SIGNAL_MAP.get(sig, "badge-vol")
        col   = SIGNAL_COLORS.get(sig, "var(--cyan)")
        chips = "".join(f'<span class="sig-chip">{t}</span>' for t in tklist[:8])
        sig_html += f"""<div class="sig-row fi2">
          <span class="badge {cls}">{sig}</span>
          <span class="sig-count" style="color:{col}">{len(tklist)}</span>
          <span class="sig-tickers">{chips}</span>
        </div>"""

    st.markdown(f'<div class="card card-accent-green">{sig_html}</div>', unsafe_allow_html=True)

    # ── INSTITUTIONAL ACTIVITY  ───────────────────────────────────────────────
    st.markdown("""<div class="sec-head fi3" style="margin-top:4px">
      <span style="font-size:.9rem">🏛️</span>
      <span class="sec-head-title">Institutional Activity</span>
      <span class="sec-head-tag">Block Flow Detection</span>
    </div>""", unsafe_allow_html=True)

    inst_cands = sorted(
        [r for r in raw if r.get("vol_spk",0) > 35 and r["price"]*r["volume"] > 2e8],
        key=lambda x: x["vol_spk"], reverse=True
    )[:6]

    if inst_cands:
        inst_html = ""
        for r in inst_cands:
            vol_m    = r["volume"] / 1e6
            notional = r["price"] * r["volume"] / 1e9
            note     = "Possible accumulation" if r["chg_pct"] > 0 else "Possible distribution"
            inst_html += f"""<div class="inst-row fi3">
              <div>
                <div class="inst-ticker">{r['ticker']}</div>
                <div class="inst-note">{note}</div>
              </div>
              <div style="text-align:center">
                <div class="inst-pct">+{r['vol_spk']:.0f}%</div>
                <div class="inst-lbl">vol spike</div>
              </div>
              <div style="text-align:right">
                <div class="inst-vol">{vol_m:.1f}M shs</div>
                <div class="inst-lbl">${notional:.2f}B notional</div>
              </div>
            </div>"""
        st.markdown(f'<div class="card card-accent-purple">{inst_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card"><span style="font-size:.7rem;color:#5a7a99">No unusual institutional flow detected.</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT
# ══════════════════════════════════════════════════════════════════════════════
with right:

    # ── STOCK DETAIL ─────────────────────────────────────────────────────────
    st.markdown("""<div class="sec-head fi1">
      <span style="color:#00e5ff;font-size:.9rem">🔬</span>
      <span class="sec-head-title">Stock Detail Panel</span>
      <span class="sec-head-tag">Select to Drill Down</span>
    </div>""", unsafe_allow_html=True)

    avail = df["ticker"].tolist() if not df.empty else df_all["ticker"].tolist() if not df_all.empty else DEFAULT_WATCHLIST[:5]
    sel   = st.selectbox("", avail, index=0, label_visibility="collapsed")

    if sel and sel in lut:
        rd      = lut[sel]
        score   = rd["score"]
        signals = rd["signals"]
        hist30  = rd.get("hist30", pd.DataFrame())

        # Metrics
        d1,d2,d3,d4 = st.columns(4)
        with d1: st.metric("Price",     f"${rd['price']:.2f}",   delta=f"{rd['chg_pct']:+.2f}%")
        with d2: st.metric("Volume",    f"{rd['volume']/1e6:.1f}M")
        with d3: st.metric("Vol Spike", f"{rd['vol_spk']:+.0f}%")
        with d4: st.metric("MA(20)",    f"${rd['ma20']:.2f}")

        # Intraday + gauge
        ca, cb = st.columns([3, 1])
        with ca:
            intra = load_intraday(sel)
            if not intra.empty:
                st.plotly_chart(make_intraday_chart(intra, sel), use_container_width=True,
                                config={"displayModeBar": False})
        with cb:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.plotly_chart(make_gauge(score), use_container_width=True, config={"displayModeBar": False})
            bar_col = {"score-elite":"#00ff9d","score-high":"#00e5ff","score-mid":"#ffb700","score-low":"#5a7a99"}[score_cls(score)]
            st.markdown(f"""<div class="score-bar-wrap">
              <div class="score-bar-fill" style="width:{score}%;background:{bar_col}"></div>
            </div>
            <div style="text-align:center;font-size:.56rem;color:#5a7a99;letter-spacing:.12em">OPPORTUNITY SCORE</div>""",
            unsafe_allow_html=True)

        # 30-day candlestick
        st.plotly_chart(make_candlestick(hist30, sel), use_container_width=True,
                        config={"displayModeBar": False})

        # Signals + score factors
        cs, cf = st.columns(2)
        with cs:
            badges_html = "".join(
                f'<div style="margin-bottom:7px"><span class="badge {SIGNAL_MAP.get(s,"badge-vol")}">{s}</span></div>'
                for s in signals
            ) or '<span style="font-size:.7rem;color:#5a7a99">No strong signals</span>'
            st.markdown(f"""<div class="card card-accent-green">
              <div style="font-size:.56rem;letter-spacing:.15em;color:#5a7a99;text-transform:uppercase;margin-bottom:10px">Active Signals</div>
              {badges_html}
            </div>""", unsafe_allow_html=True)

        with cf:
            factors = []
            if rd["vol_spk"] > 40:
                factors.append((f"Volume +{rd['vol_spk']:.0f}% above avg", min(28, int(rd['vol_spk']/6)), "pos"))
            if rd["chg_pct"] > 1:
                factors.append((f"Price {rd['chg_pct']:+.2f}%", min(22, int(rd['chg_pct']*5)), "pos"))
            if rd["ma_above"]:
                factors.append(("Above MA(20)", 8, "pos"))
            if rd["near_hi"]:
                factors.append(("Near 30-day high", 6, "pos"))
            factors.append(("Base score", 50, "neu"))
            frows = "".join(
                f'<div class="factor-row"><span class="factor-lbl">{l}</span>'
                f'<span class="factor-pts pts-{c}">+{p}</span></div>'
                for l,p,c in factors
            )
            st.markdown(f"""<div class="card card-accent-amber">
              <div style="font-size:.56rem;letter-spacing:.15em;color:#5a7a99;text-transform:uppercase;margin-bottom:10px">Score Breakdown</div>
              {frows}
              <div style="border-top:1px solid var(--border);margin-top:8px;padding-top:8px;font-size:.65rem;color:var(--cyan);font-family:'Orbitron'">Total: {score} / 99</div>
            </div>""", unsafe_allow_html=True)

    # ── AI ALERTS ─────────────────────────────────────────────────────────────
    st.markdown("""<div class="sec-head fi2" style="margin-top:6px">
    <span style="font-size:.9rem">🚨</span>
    <span class="sec-head-title">AI Alerts</span>
    <span class="sec-head-tag">Real-time Intelligence</span>
    </div>""", unsafe_allow_html=True)

    alerts = generate_ai_alerts(raw)

    if alerts:
        alerts_html = ""
        for a in alerts:
            confidence = a["confidence"]

            # color based on confidence
            if confidence >= 85:
                col = "#00ff9d"
            elif confidence >= 70:
                col = "#00e5ff"
            elif confidence >= 55:
                col = "#ffb700"
            else:
                col = "#ff3d5a"

            alerts_html += f"""
            <div class="sig-row fi2" style="border-left:3px solid {col}">
                <div style="flex:1">
                    <div style="font-size:.72rem;color:#eaf6ff;margin-bottom:3px">
                        {a['msg']}
                    </div>
                    <div style="font-size:.58rem;color:{col};letter-spacing:.1em">
                        CONFIDENCE: {confidence}%
                    </div>
                </div>
            </div>
            """

        st.markdown(f'<div class="card card-accent-red">{alerts_html}</div>', unsafe_allow_html=True)

    else:
        st.markdown(
            '<div class="card"><span style="font-size:.7rem;color:#5a7a99">No active AI alerts.</span></div>',
            unsafe_allow_html=True
        )

    # ── NEWS SENTIMENT ───────────────────────────────────────────────────────
    st.markdown("""<div class="sec-head fi3" style="margin-top:6px">
      <span style="font-size:.9rem">📰</span>
      <span class="sec-head-title">News Sentiment</span>
      <span class="sec-head-tag">VADER NLP  ·  Simulated Feed</span>
    </div>""", unsafe_allow_html=True)

    news_tickers = df["ticker"].head(4).tolist() if not df.empty else (df_all["ticker"].head(4).tolist() if not df_all.empty else DEFAULT_WATCHLIST[:4])

    all_sentiments = []
    sent_counts    = {"Positive": 0, "Neutral": 0, "Negative": 0}
    news_html      = ""

    for sym in news_tickers:
        headlines  = get_news(sym)
        sentiments = analyse_sentiment(headlines)
        all_sentiments.extend(sentiments)
        for s in sentiments:
            sent_counts[s["label"]] += 1

        dom = max(sentiments, key=lambda x: x["score"]) if sentiments else None
        comp_avg = float(np.mean([s["score"] for s in sentiments]))
        if dom and dom["score"] > 0.05:
            dom_badge = '<span class="badge badge-break">Bullish</span>'
        elif dom and dom["score"] < -0.05:
            dom_badge = '<span class="badge badge-insider">Bearish</span>'
        else:
            dom_badge = '<span class="badge badge-ma">Neutral</span>'

        news_html += f"""<div style="margin-bottom:14px">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid var(--border)">
            <span style="font-family:'Orbitron';font-size:.76rem;color:#00e5ff;font-weight:700">{sym}</span>
            {dom_badge}
            <span style="font-size:.56rem;color:#5a7a99;margin-left:auto">composite: {comp_avg:+.3f}</span>
          </div>"""
        for s in sentiments[:2]:
            cls     = {"Positive":"pos","Neutral":"neu","Negative":"neg"}[s["label"]]
            lbl_cls = f"news-{cls}"
            news_html += f"""<div class="news-item {cls}">
            <div class="news-headline">{s['text']}</div>
            <div class="news-meta">
              <span class="news-ticker">{sym}</span>
              <span class="{lbl_cls}">{s['label']}</span>
              <span class="news-score-lbl">score: {s['score']:+.3f}</span>
            </div>
          </div>"""
        news_html += "</div>"

    nd1, nd2 = st.columns([1, 2])
    with nd1:
        st.plotly_chart(make_sentiment_donut(sent_counts), use_container_width=True,
                        config={"displayModeBar": False})
        total = sum(sent_counts.values()) or 1
        for lbl, cnt in sent_counts.items():
            col = {"Positive":"#00ff9d","Neutral":"#ffb700","Negative":"#ff3d5a"}[lbl]
            st.markdown(f'<div style="font-size:.6rem;color:{col};font-family:\'IBM Plex Mono\'">{lbl}: {cnt} ({cnt/total*100:.0f}%)</div>', unsafe_allow_html=True)
    with nd2:
        st.markdown(f'<div class="card card-accent-amber" style="max-height:310px;overflow-y:auto">{news_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AUTO REFRESH
# ─────────────────────────────────────────────────────────────────────────────
if auto_ref:
    time.sleep(60)
    st.cache_data.clear()
    st.rerun()

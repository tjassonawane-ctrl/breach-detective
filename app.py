import random

import plotly.graph_objects as go
import streamlit as st

import stats_engine as eng

st.set_page_config(page_title="Breach Detective", page_icon="🕵️", layout="centered")

st.markdown(
    """
<style>
.big-title {font-family:'Courier New',monospace; font-size:2.4rem; font-weight:800;
            color:#00e5ff; letter-spacing:2px; text-shadow:0 0 14px rgba(0,229,255,.55);}
.sub {color:#8fb3c9; margin-top:-10px; margin-bottom:18px;}
.card {border:1px solid #1f6f8b; border-radius:12px; padding:14px 18px;
       background:rgba(16,36,58,.65); margin-bottom:10px;}
.rank {font-family:'Courier New',monospace; font-size:1.8rem; color:#2ecc71;}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# GAME DATA: 5 cyber-security scenarios, getting harder each round
# ---------------------------------------------------------------
THEMES = [
    dict(name="Failed logins per hour", where="Web server", unit="attempts",
         mean=14, sd=3, n=12, k=1, mult=(6, 8), side="up"),
    dict(name="Data uploaded per employee", where="Finance department", unit="MB",
         mean=120, sd=25, n=14, k=2, mult=(5, 7), side="both"),
    dict(name="Server response time", where="Payments API", unit="ms",
         mean=200, sd=30, n=14, k=2, mult=(4, 5), side="both"),
    dict(name="Logins per minute", where="VPN gateway", unit="logins",
         mean=20, sd=4, n=15, k=3, mult=(3.8, 5), side="up"),
    dict(name="Outbound traffic per device", where="Office network", unit="GB",
         mean=50, sd=8, n=15, k=2, mult=(3.3, 4), side="both"),
]


def make_round(rng, t):
    """Generate normal-looking data, hide a few anomalies, and let the
    IQR engine decide what is truly an outlier."""
    while True:
        vals = [max(1, round(rng.gauss(t["mean"], t["sd"]))) for _ in range(t["n"])]
        for idx in rng.sample(range(t["n"]), t["k"]):
            sign = 1 if t["side"] == "up" else rng.choice([1, -1])
            vals[idx] = max(1, round(t["mean"] + sign * rng.uniform(*t["mult"]) * t["sd"]))
        res = eng.detect_outliers_iqr(vals)
        truth = [i for i, v in enumerate(vals)
                 if v < res["lower_bound"] or v > res["upper_bound"]]
        if truth:
            return dict(theme=t, values=vals, res=res, truth=truth,
                        labels=[f"P{i + 1}" for i in range(len(vals))])


def new_game():
    rng = random.Random(random.randrange(10 ** 6))
    st.session_state.g = dict(rounds=[make_round(rng, t) for t in THEMES],
                              i=0, score=0, phase="play", log=[])


def score_round(r, picked):
    truth, picked = set(r["truth"]), set(picked)
    hits, misses, false = len(truth & picked), len(truth - picked), len(picked - truth)
    pts = 10 * hits - 5 * misses - 5 * false + (10 if misses == 0 and false == 0 else 0)
    return hits, misses, false, pts


def make_chart(r, picked, reveal):
    colors = []
    for i in range(len(r["values"])):
        if not reveal:
            colors.append("#ff9f1c" if i in picked else "#00e5ff")
        else:
            is_out, was_picked = i in r["truth"], i in picked
            colors.append("#2ecc71" if is_out and was_picked
                          else "#ff4d6d" if is_out
                          else "#ff9f1c" if was_picked
                          else "#5c7a8c")
    fig = go.Figure(go.Bar(x=r["labels"], y=r["values"], marker_color=colors,
                           text=r["values"], textposition="outside"))
    top = max(r["values"])
    if reveal:
        up, low = r["res"]["upper_bound"], r["res"]["lower_bound"]
        top = max(top, up)
        fig.add_hline(y=up, line_dash="dash", line_color="#ff4d6d",
                      annotation_text=f"upper fence {up:.1f}", annotation_position="top left")
        if low > 0:
            fig.add_hline(y=low, line_dash="dash", line_color="#ff4d6d",
                          annotation_text=f"lower fence {low:.1f}", annotation_position="bottom left")
    fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=30, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_yaxes(range=[0, top * 1.18])
    return fig


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("How scoring works")
    st.markdown(
        "- +10 for each real anomaly you catch\n"
        "- -5 for each false alarm\n"
        "- -5 for each anomaly you miss\n"
        "- +10 bonus for a perfect report"
    )
    st.caption("The judge is a statistics engine written from scratch in pure Python "
               "(merge sort, quartiles, IQR rule). No numpy.")

st.markdown('<div class="big-title">🕵️ BREACH DETECTIVE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Spot the anomalies hiding in the logs before the attacker wins.</div>',
            unsafe_allow_html=True)

# ---------------- Intro screen ----------------
if "g" not in st.session_state:
    st.markdown(
        '<div class="card"><b>Your mission:</b> you are a security analyst. In each of 5 rounds you '
        'get a chart of network activity. A few points are suspicious. Flag them, submit your '
        'report, and see how you did against the engine.</div>',
        unsafe_allow_html=True,
    )
    if st.button("▶ Start mission", type="primary"):
        new_game()
        st.rerun()
    st.stop()

g = st.session_state.g
total_rounds = len(g["rounds"])

# ---------------- Final screen ----------------
if g["i"] >= total_rounds:
    max_total = sum(10 * len(r["truth"]) + 10 for r in g["rounds"])
    pct = max(0, g["score"]) / max_total
    if pct >= 0.85:
        rank = "🕵️ Threat Hunter"
    elif pct >= 0.60:
        rank = "🛡️ SOC Analyst"
    elif pct >= 0.30:
        rank = "🔍 Junior Analyst"
    else:
        rank = "😅 Script Kiddie"
    st.markdown(f'<div class="rank">MISSION COMPLETE: {rank}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Final score", g["score"])
    c2.metric("Max possible", max_total)
    c3.metric("Accuracy", f"{pct * 100:.0f}%")
    st.dataframe(
        [{"Round": k + 1, "Scenario": g["rounds"][k]["theme"]["name"], "Caught": h,
          "Missed": m, "False alarms": f, "Points": p}
         for k, (h, m, f, p) in enumerate(g["log"])],
        hide_index=True,
    )
    if pct >= 0.6:
        st.balloons()
    if st.button("🔁 Play again", type="primary"):
        new_game()
        st.rerun()
    st.stop()

# ---------------- Round screen ----------------
i = g["i"]
r = g["rounds"][i]
t = r["theme"]
reveal = g["phase"] == "reveal"

m1, m2, m3 = st.columns(3)
m1.metric("Round", f"{i + 1} / {total_rounds}")
m2.metric("Score", g["score"])
m3.metric("Difficulty", ["Easy", "Easy", "Medium", "Hard", "Expert"][i])

st.markdown(
    f'<div class="card"><b>{t["name"]}</b> · {t["where"]} · measured in {t["unit"]}</div>',
    unsafe_allow_html=True,
)

chart_box = st.container()
chosen = st.multiselect("Flag the suspicious points", r["labels"], key=f"pick{i}", disabled=reveal)
picked = [r["labels"].index(x) for x in chosen]
with chart_box:
    st.plotly_chart(make_chart(r, picked, reveal), width="stretch")

with st.expander("Hint: how do analysts decide what is an outlier?"):
    st.write("Sort the data, find the middle of the lower half (Q1) and upper half (Q3). "
             "The gap between them is the IQR. Anything more than 1.5 x IQR below Q1 or above Q3 "
             "is flagged as an outlier.")

if not reveal:
    if st.button("🚨 Submit report", type="primary"):
        h, m, f, p = score_round(r, picked)
        g["score"] += p
        g["log"].append((h, m, f, p))
        g["phase"] = "reveal"
        st.rerun()
else:
    h, m, f, p = g["log"][i]
    if m == 0 and f == 0:
        st.success(f"Perfect report! +{p} points")
    else:
        st.warning(f"{h} caught, {m} missed, {f} false alarm(s): {p:+d} points")
    st.caption("Green = caught · Red = missed · Orange = false alarm · Grey = normal")

    res = r["res"]
    st.markdown(
        f'<div class="card"><b>Engine verdict:</b> Q1 = {res["q1"]}, Q3 = {res["q3"]}, '
        f'IQR = {res["iqr"]}. Anything below {res["lower_bound"]:.1f} or above '
        f'{res["upper_bound"]:.1f} is an outlier.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**Why outliers matter:**")
    a, b, c, d = st.columns(4)
    a.metric("Mean (with outliers)", f"{eng.calculate_mean(r['values']):.1f}")
    b.metric("Mean (cleaned)", f"{eng.calculate_mean(res['clean_data']):.1f}")
    c.metric("Median", f"{eng.calculate_median(r['values']):.1f}")
    d.metric("Std dev", f"{eng.calculate_std_dev(r['values']):.1f}")
    st.caption("Notice how outliers drag the mean around while the median barely moves.")

    if st.button("Next round ➡️" if i < total_rounds - 1 else "🏁 See final rank", type="primary"):
        g["i"] += 1
        g["phase"] = "play"
        st.rerun()

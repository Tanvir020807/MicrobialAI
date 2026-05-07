import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="MicrobialAI Growth Predictor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

MICROBES = {
    "Escherichia coli": {
        "type": "Gram-negative bacterium",
        "icon": "🦠",
        "color": "#22c55e",
        "base_rate": 1.05,
        "max_od": 1.00,
        "opt_temp": 37,
        "opt_ph": 7.0,
        "lag_time": 5
    },
    "Bacillus subtilis": {
        "type": "Gram-positive bacterium",
        "icon": "🧫",
        "color": "#fbbf24",
        "base_rate": 0.82,
        "max_od": 0.92,
        "opt_temp": 35,
        "opt_ph": 7.2,
        "lag_time": 7
    },
    "Staphylococcus aureus": {
        "type": "Gram-positive cocci",
        "icon": "🟣",
        "color": "#8b5cf6",
        "base_rate": 0.72,
        "max_od": 0.84,
        "opt_temp": 37,
        "opt_ph": 7.4,
        "lag_time": 8
    },
    "Pseudomonas aeruginosa": {
        "type": "Gram-negative bacterium",
        "icon": "🔬",
        "color": "#06b6d4",
        "base_rate": 0.88,
        "max_od": 0.95,
        "opt_temp": 33,
        "opt_ph": 7.1,
        "lag_time": 7
    },
    "Lactobacillus acidophilus": {
        "type": "Lactic acid bacterium",
        "icon": "🧬",
        "color": "#ec4899",
        "base_rate": 0.68,
        "max_od": 0.78,
        "opt_temp": 37,
        "opt_ph": 5.8,
        "lag_time": 9
    },
    "Saccharomyces cerevisiae": {
        "type": "Yeast",
        "icon": "🟡",
        "color": "#f59e0b",
        "base_rate": 0.60,
        "max_od": 0.88,
        "opt_temp": 30,
        "opt_ph": 5.5,
        "lag_time": 10
    }
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 71% 2%, rgba(60, 80, 190, 0.24), transparent 22rem),
        radial-gradient(circle at 8% 30%, rgba(20, 184, 166, 0.10), transparent 18rem),
        linear-gradient(135deg, #050914 0%, #07111f 45%, #081525 100%);
    color: #f8fafc;
}

.main .block-container {
    max-width: 1520px;
    padding: 1.45rem 1.7rem 1rem;
}

section[data-testid="stSidebar"] {
    width: 320px !important;
    background: linear-gradient(180deg, #071225 0%, #050914 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.20);
}

section[data-testid="stSidebar"] > div {
    padding: 1.2rem 0.8rem;
}

h1, h2, h3, p {
    margin: 0;
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
}

.logo-circle {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    border: 2px solid #14b8a6;
    color: #14b8a6;
    font-size: 25px;
    box-shadow: 0 0 22px rgba(20, 184, 166, 0.22);
}

.logo-title {
    font-size: 25px;
    font-weight: 800;
    line-height: 1.05;
}

.logo-title span {
    color: #3b82f6;
}

.logo-subtitle {
    color: #cbd5e1;
    font-size: 14px;
    margin-top: 4px;
}

.sidebar-heading {
    color: #60a5fa;
    text-transform: uppercase;
    font-size: 13px;
    letter-spacing: 0.05em;
    font-weight: 700;
    margin: 18px 0 10px;
}

.search-box {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 9px;
    padding: 12px 14px;
    color: #cbd5e1;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    font-size: 13px;
}

.microbe-card {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 9px;
    padding: 10px 12px;
    margin-bottom: 6px;
}

.microbe-card.active {
    border-color: #7c3aed;
    box-shadow: inset 0 0 0 1px rgba(124, 58, 237, 0.55);
    background: linear-gradient(90deg, rgba(30, 41, 59, 0.95), rgba(67, 56, 202, 0.18));
}

.microbe-icon {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 20px;
    background: rgba(255,255,255,0.08);
}

.microbe-name {
    font-weight: 800;
    font-size: 14px;
    color: white;
}

.microbe-type {
    color: #cbd5e1;
    font-size: 12px;
    margin-top: 3px;
}

.check {
    margin-left: auto;
    background: #8b5cf6;
    color: white;
    width: 25px;
    height: 25px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-weight: 800;
}

.slider-shell {
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 9px;
    padding: 10px 12px 2px;
    margin-bottom: 8px;
}

div[data-testid="stSlider"] {
    padding: 0;
}

.stButton > button {
    width: 100%;
    border: none;
    border-radius: 9px;
    padding: 0.75rem 1rem;
    color: white;
    font-weight: 800;
    background: linear-gradient(90deg, #1683ff, #b12cff);
}

.secondary-button button {
    background: rgba(15, 23, 42, 0.88) !important;
    border: 1px solid rgba(148, 163, 184, 0.18) !important;
}

.hero {
    position: relative;
    min-height: 92px;
    padding: 12px 10px 16px;
    overflow: hidden;
}

.hero:after {
    content: "🦠  🧫  🔬  🦠";
    position: absolute;
    right: 30px;
    top: -12px;
    font-size: 50px;
    opacity: 0.20;
    letter-spacing: 18px;
}

.hero h1 {
    font-size: 34px;
    font-weight: 800;
    color: white;
    margin-bottom: 10px;
}

.hero p {
    color: #cbd5e1;
    font-size: 15px;
}

.about-btn {
    position: absolute;
    right: 8px;
    top: 14px;
    padding: 12px 18px;
    border-radius: 10px;
    color: white;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.20);
    font-size: 14px;
    font-weight: 700;
}

.metric-card,
.chart-card,
.side-card,
.insight-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(8, 18, 34, 0.96));
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 10px;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
}

.metric-card {
    min-height: 138px;
    padding: 24px;
    position: relative;
    overflow: hidden;
}

.metric-card.glow {
    background:
        radial-gradient(circle at 80% 35%, rgba(34, 197, 94, 0.35), transparent 7rem),
        linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(8, 18, 34, 0.96));
}

.metric-label {
    color: #f8fafc;
    font-size: 15px;
    font-weight: 600;
}

.metric-value {
    margin-top: 17px;
    color: white;
    font-size: 30px;
    font-weight: 800;
}

.metric-caption {
    color: #cbd5e1;
    font-size: 13px;
    margin-top: 8px;
}

.metric-art {
    position: absolute;
    right: 24px;
    top: 48px;
    font-size: 42px;
    opacity: 0.75;
}

.green { color: #22c55e; }
.blue { color: #3b82f6; }
.purple { color: #8b5cf6; }
.yellow { color: #fbbf24; }
.pink { color: #ec4899; }
.red { color: #fb7185; }

.chart-card {
    padding: 20px 22px 14px;
}

.card-title {
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 8px;
}

.chart-sub {
    color: #cbd5e1;
    font-style: italic;
    margin-bottom: 10px;
}

.fake-tools {
    float: right;
    display: flex;
    gap: 10px;
    margin-top: -38px;
}

.fake-tool {
    width: 48px;
    height: 48px;
    border-radius: 9px;
    display: grid;
    place-items: center;
    background: rgba(30, 41, 59, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.14);
    color: white;
    font-size: 22px;
}

.side-card {
    padding: 18px;
    margin-bottom: 15px;
}

.phase-row {
    display: flex;
    gap: 12px;
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 9px;
    padding: 12px;
    margin-bottom: 8px;
}

.phase-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 18px;
    background: rgba(255,255,255,0.08);
}

.phase-name {
    font-size: 14px;
    font-weight: 800;
    color: white;
}

.phase-desc {
    color: #cbd5e1;
    font-size: 12px;
    margin-top: 4px;
    line-height: 1.45;
}

.summary-text {
    color: #cbd5e1;
    font-size: 13px;
    line-height: 1.55;
    margin-bottom: 14px;
}

.summary-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    color: #cbd5e1;
    font-size: 13px;
    border-top: 1px solid rgba(148, 163, 184, 0.14);
    padding: 9px 0;
}

.summary-row span:last-child {
    color: #60a5fa;
    font-weight: 700;
    text-align: right;
}

.insight-card {
    padding: 17px;
    min-height: 108px;
}

.insight-title {
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 9px;
}

.insight-text {
    color: #cbd5e1;
    font-size: 12px;
    line-height: 1.55;
}

.footer {
    border-top: 1px solid rgba(148, 163, 184, 0.18);
    color: #cbd5e1;
    padding: 18px 8px 4px;
    margin-top: 16px;
    font-size: 13px;
    display: flex;
    justify-content: space-between;
    gap: 20px;
}
</style>
""", unsafe_allow_html=True)


def bell_factor(value, optimum, tolerance):
    score = math.exp(-((value - optimum) / tolerance) ** 2)
    return max(0.05, min(1.0, score))


def calculate_growth(microbe_name, temperature, ph, nutrient):
    microbe = MICROBES[microbe_name]

    temp_factor = bell_factor(temperature, microbe["opt_temp"], 10)
    ph_factor = bell_factor(ph, microbe["opt_ph"], 1.6)
    nutrient_factor = max(0.10, min(1.25, nutrient))

    condition_score = (
        temp_factor * 0.40
        + ph_factor * 0.35
        + min(nutrient_factor, 1.0) * 0.25
    )

    growth_rate = microbe["base_rate"] * temp_factor * ph_factor * nutrient_factor
    max_od = microbe["max_od"] * (0.55 + 0.45 * nutrient_factor)
    lag_time = microbe["lag_time"] + (1 - condition_score) * 6

    return growth_rate, max_od, lag_time, condition_score


def logistic_growth(time, growth_rate, max_od, lag_time):
    return max_od / (1 + np.exp(-growth_rate * (time - lag_time)))


def get_phase(time, lag_time):
    if time < lag_time:
        return "Lag Phase", "Cells adapting"
    if time < 20:
        return "Log Phase", "Exponential growth"
    if time < 35:
        return "Stationary Phase", "Nutrient limitation"
    return "Death Phase", "Cell death exceeds growth"


def make_chart(df, current_time, current_od, lag_time, max_od):
    fig = go.Figure()

    regions = [
        ("Lag Phase", 0, lag_time, "rgba(148, 163, 184, 0.16)"),
        ("Log Phase", lag_time, 24, "rgba(139, 92, 246, 0.22)"),
        ("Stationary Phase", 24, 38, "rgba(251, 191, 36, 0.13)"),
        ("Death Phase", 38, 48, "rgba(244, 63, 94, 0.16)")
    ]

    for name, start, end, color in regions:
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor=color,
            opacity=1,
            line_width=1,
            line_color="rgba(255,255,255,0.12)",
            annotation_text=name,
            annotation_position="top"
        )

    fig.add_trace(go.Scatter(
        x=df["Time"],
        y=df["OD600"],
        mode="lines",
        name="Growth Curve",
        line=dict(color="#1f7aff", width=4)
    ))

    fig.add_trace(go.Scatter(
        x=[current_time],
        y=[current_od],
        mode="markers",
        name="Current Point",
        marker=dict(size=14, color="#34d399")
    ))

    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Lag Phase", line=dict(color="#94a3b8", width=4)))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Log Phase", line=dict(color="#8b5cf6", width=4)))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Stationary Phase", line=dict(color="#fbbf24", width=4)))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Death Phase", line=dict(color="#f43f5e", width=4)))

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=48, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.45)",
        font=dict(color="#f8fafc", size=12),
        legend=dict(
            orientation="h",
            y=1.14,
            x=0.00,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12)
        ),
        xaxis=dict(
            title="Time (hours)",
            range=[0, 48],
            tickmode="array",
            tickvals=[0, 8, 16, 24, 32, 40, 48],
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            title="Optical Density (OD600)",
            range=[0, max(1.25, max_od + 0.25)],
            tickmode="array",
            tickvals=[0, 0.25, 0.5, 0.75, 1.0, 1.25],
            gridcolor="rgba(255,255,255,0.08)"
        )
    )

    return fig


def metric_card(label, value, caption, color="", art="", glow=False):
    glow_class = "glow" if glow else ""
    st.markdown(f"""
    <div class="metric-card {glow_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{value}</div>
        <div class="metric-caption">{caption}</div>
        <div class="metric-art {color}">{art}</div>
    </div>
    """, unsafe_allow_html=True)


# Sidebar
st.sidebar.markdown("""
<div class="logo">
    <div class="logo-circle">⌬</div>
    <div>
        <div class="logo-title">Microbial<span>AI</span></div>
        <div class="logo-subtitle">Growth Predictor</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-heading">1. Select Microorganism</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="search-box"><span>Search microorganism...</span><span>⌕</span></div>', unsafe_allow_html=True)

microbe_name = st.sidebar.radio(
    "Microorganism",
    list(MICROBES.keys()),
    index=0,
    label_visibility="collapsed"
)

for name, data in MICROBES.items():
    active = "active" if name == microbe_name else ""
    check = '<div class="check">✓</div>' if name == microbe_name else ""
    st.sidebar.markdown(f"""
    <div class="microbe-card {active}">
        <div class="microbe-icon" style="color:{data['color']}; box-shadow:0 0 16px {data['color']}44;">
            {data['icon']}
        </div>
        <div>
            <div class="microbe-name">{name}</div>
            <div class="microbe-type">{data['type']}</div>
        </div>
        {check}
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-heading">2. Environmental Conditions</div>', unsafe_allow_html=True)

incubation_time = st.sidebar.slider("Incubation Time (hours)", 0, 48, 24)
temperature = st.sidebar.slider("Temperature (°C)", 15, 50, MICROBES[microbe_name]["opt_temp"])
ph = st.sidebar.slider("pH", 4.0, 9.0, MICROBES[microbe_name]["opt_ph"], 0.1)
nutrient = st.sidebar.slider("Nutrient Concentration", 0.1, 2.0, 1.0, 0.1)

st.sidebar.caption("(Relative scale: 0.1 - 2.0)")
st.sidebar.button("↗  Predict Growth")
st.sidebar.markdown('<div class="secondary-button">', unsafe_allow_html=True)
st.sidebar.button("↻  Reset All")
st.sidebar.markdown("</div>", unsafe_allow_html=True)


growth_rate, max_od, lag_time, condition_score = calculate_growth(
    microbe_name,
    temperature,
    ph,
    nutrient
)

time_values = np.linspace(0, 48, 260)
od_values = logistic_growth(time_values, growth_rate, max_od, lag_time)
current_od = float(logistic_growth(incubation_time, growth_rate, max_od, lag_time))
phase, phase_caption = get_phase(incubation_time, lag_time)

df = pd.DataFrame({"Time": time_values, "OD600": od_values})


# Header
st.markdown("""
<div class="hero">
    <h1>AI-Assisted Microbial Growth Predictor</h1>
    <p>Predict and analyze microbial growth under different environmental conditions</p>
    <div class="about-btn">ⓘ &nbsp; About Model</div>
</div>
""", unsafe_allow_html=True)


# Metrics
m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Growth Phase", phase, phase_caption, "green", "⌁", True)

with m2:
    metric_card("Predicted OD ᴾ⁶⁰⁰ⁿᵐᴾ", f"{current_od:.3f}", "Optical Density", "", "〰")

with m3:
    metric_card("Max OD (K)", f"{max_od:.3f}", "Carrying Capacity", "purple", "⚗")

with m4:
    metric_card("Growth Rate (r)", f"{growth_rate:.3f} /hr", "Intrinsic Growth Rate", "pink", "↗")


st.write("")

main_col, side_col = st.columns([3.1, 1.05])

with main_col:
    st.markdown(f"""
    <div class="chart-card">
        <div class="card-title">Predicted Growth Curve</div>
        <div class="chart-sub">{microbe_name}</div>
        <div class="fake-tools">
            <div class="fake-tool">⇩</div>
            <div class="fake-tool">↗</div>
        </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(
        make_chart(df, incubation_time, current_od, lag_time, max_od),
        use_container_width=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    st.markdown('<div class="chart-card"><div class="card-title">Growth Insights</div>', unsafe_allow_html=True)

    if condition_score >= 0.78:
        condition_msg = "Temperature, pH and nutrients are in optimal range for maximal growth."
    elif condition_score >= 0.50:
        condition_msg = "Growth is possible, but conditions can still be improved."
    else:
        condition_msg = "The microorganism may be stressed under these settings."

    if growth_rate >= 0.8:
        speed_msg = f"{microbe_name} shows rapid exponential growth under these conditions."
    elif growth_rate >= 0.45:
        speed_msg = f"{microbe_name} shows moderate growth under these conditions."
    else:
        speed_msg = f"{microbe_name} grows slowly under these conditions."

    i1, i2, i3, i4 = st.columns(4)

    with i1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title green">☘ Optimal Conditions</div>
            <div class="insight-text">{condition_msg}</div>
        </div>
        """, unsafe_allow_html=True)

    with i2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title purple">♜ Fast Growth</div>
            <div class="insight-text">{speed_msg}</div>
        </div>
        """, unsafe_allow_html=True)

    with i3:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title yellow">♟ High Biomass</div>
            <div class="insight-text">High carrying capacity indicates good nutrient availability.</div>
        </div>
        """, unsafe_allow_html=True)

    with i4:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title pink">✹ Recommendation</div>
            <div class="insight-text">Maintain conditions to prolong logarithmic phase for higher yield.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


with side_col:
    st.markdown("""
    <div class="side-card">
        <div class="card-title">Growth Phase Information</div>

        <div class="phase-row">
            <div class="phase-icon purple">◷</div>
            <div>
                <div class="phase-name">Lag Phase</div>
                <div class="phase-desc">Cells adapting to environment<br>0 - 8 hrs</div>
            </div>
        </div>

        <div class="phase-row">
            <div class="phase-icon green">↗</div>
            <div>
                <div class="phase-name">Log Phase</div>
                <div class="phase-desc">Exponential cell division<br>8 - 20 hrs</div>
            </div>
        </div>

        <div class="phase-row">
            <div class="phase-icon yellow">◔</div>
            <div>
                <div class="phase-name">Stationary Phase</div>
                <div class="phase-desc">Nutrient limitation begins<br>20 - 35 hrs</div>
            </div>
        </div>

        <div class="phase-row">
            <div class="phase-icon red">✖</div>
            <div>
                <div class="phase-name">Death Phase</div>
                <div class="phase-desc">Cell death exceeds growth<br>35+ hrs</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="side-card">
        <div class="card-title">Model Summary</div>
        <div class="summary-text">
            The prediction is based on a modified logistic growth model that considers
            environmental factors and microbial characteristics.
        </div>

        <div class="summary-row">
            <span>↗ &nbsp; Model Type</span>
            <span>Logistic Growth</span>
        </div>
        <div class="summary-row">
            <span>◷ &nbsp; Equation</span>
            <span>K / (1 + e<sup>-r(t-t0)</sup>)</span>
        </div>
        <div class="summary-row">
            <span>⚗ &nbsp; Lag Time (t_0)</span>
            <span>{lag_time:.1f} hours</span>
        </div>
        <div class="summary-row">
            <span>◷ &nbsp; Carry Capacity (K)</span>
            <span>{max_od:.3f} OD</span>
        </div>
        <div class="summary-row">
            <span>⚗ &nbsp; Growth Rate (r)</span>
            <span>{growth_rate:.3f} /hr</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div class="footer">
    <div>🧬 &nbsp; <b>Microbial<span style="color:#3b82f6;">AI</span></b> Growth Predictor<br>AI-Powered • Accurate • Intelligent</div>
    <div>Developed with <span style="color:#fb7185;">♥</span> for researchers, students and biotech professionals</div>
    <div>Built using Streamlit • Python • NumPy • Matplotlib &nbsp; ⚗</div>
</div>
""", unsafe_allow_html=True)

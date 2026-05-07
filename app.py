import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="MicrobialAI Growth Predictor",
    page_icon=":dna:",
    layout="wide"
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
        "color": "#a855f7",
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
        radial-gradient(circle at 72% 2%, rgba(59, 130, 246, 0.28), transparent 25rem),
        radial-gradient(circle at 10% 20%, rgba(20, 184, 166, 0.12), transparent 22rem),
        linear-gradient(135deg, #050914 0%, #07111f 45%, #081525 100%);
    color: #f8fafc;
}

.main .block-container {
    padding-top: 1.4rem;
    padding-bottom: 1.5rem;
    max-width: 1500px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071225 0%, #050914 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.20);
}

.logo-box {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 26px;
}

.logo-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    border: 2px solid #14b8a6;
    color: #14b8a6;
    font-size: 24px;
}

.logo-title {
    font-size: 25px;
    font-weight: 800;
    line-height: 1.1;
}

.logo-title span {
    color: #3b82f6;
}

.logo-sub {
    color: #cbd5e1;
    font-size: 14px;
}

.sidebar-heading {
    color: #60a5fa;
    text-transform: uppercase;
    font-size: 13px;
    letter-spacing: 0.06em;
    font-weight: 700;
    margin: 18px 0 10px;
}

.hero {
    position: relative;
    padding: 12px 10px 18px;
    overflow: hidden;
}

.hero::after {
    content: "🦠 🧫 🔬 🦠";
    position: absolute;
    right: 40px;
    top: -8px;
    font-size: 48px;
    opacity: 0.22;
    letter-spacing: 24px;
    filter: blur(0.2px);
}

.hero h1 {
    font-size: 36px;
    margin: 0;
    font-weight: 800;
    color: white;
}

.hero p {
    color: #cbd5e1;
    margin-top: 12px;
    font-size: 15px;
}

.metric-card,
.chart-card,
.side-card,
.insight-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(8, 18, 34, 0.96));
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 12px;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
}

.metric-card {
    min-height: 135px;
    padding: 26px;
    position: relative;
    overflow: hidden;
}

.metric-card::after {
    content: "";
    position: absolute;
    right: -25px;
    top: -25px;
    width: 120px;
    height: 120px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.22), transparent 70%);
}

.metric-label {
    color: #f8fafc;
    font-size: 15px;
    font-weight: 600;
}

.metric-value {
    margin-top: 18px;
    color: white;
    font-size: 30px;
    font-weight: 800;
}

.metric-caption {
    color: #cbd5e1;
    font-size: 13px;
    margin-top: 8px;
}

.green { color: #22c55e; }
.blue { color: #3b82f6; }
.purple { color: #8b5cf6; }
.yellow { color: #fbbf24; }
.pink { color: #ec4899; }

.chart-card {
    padding: 22px;
}

.side-card {
    padding: 20px;
    margin-bottom: 16px;
}

.card-title {
    font-size: 19px;
    font-weight: 800;
    margin-bottom: 14px;
}

.phase-row,
.summary-row {
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 10px;
    padding: 13px 14px;
    margin-bottom: 9px;
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
}

.summary-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    font-size: 13px;
    color: #cbd5e1;
}

.summary-row span:last-child {
    color: #60a5fa;
    font-weight: 700;
}

.insight-card {
    padding: 18px;
    min-height: 115px;
}

.insight-title {
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 10px;
}

.insight-text {
    color: #cbd5e1;
    font-size: 13px;
    line-height: 1.6;
}

.footer {
    border-top: 1px solid rgba(148, 163, 184, 0.18);
    color: #cbd5e1;
    padding: 18px 8px 4px;
    margin-top: 18px;
    font-size: 13px;
    display: flex;
    justify-content: space-between;
    gap: 20px;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #1683ff, #b12cff);
    border: none;
    color: white;
    border-radius: 9px;
    padding: 0.72rem 1rem;
    font-weight: 800;
}

div[data-testid="stSlider"] {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 10px;
    padding: 10px 12px 4px;
    margin-bottom: 8px;
}

div[role="radiogroup"] label {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 6px;
}

div[role="radiogroup"] label:hover {
    border-color: #8b5cf6;
    background: rgba(30, 41, 59, 0.85);
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
    nutrient_factor = max(0.1, min(1.25, nutrient))

    condition_score = (
        temp_factor * 0.40
        + ph_factor * 0.35
        + min(nutrient_factor, 1.0) * 0.25
    )

    growth_rate = microbe["base_rate"] * temp_factor * ph_factor * nutrient_factor
    max_od = microbe["max_od"] * (0.55 + 0.45 * nutrient_factor)
    lag_time = microbe["lag_time"] + (1 - condition_score) * 6

    return growth_rate, max_od, lag_time, condition_score, temp_factor, ph_factor, nutrient_factor


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


def create_growth_chart(df, current_time, current_od, lag_time, max_od):
    fig = go.Figure()

    regions = [
        ("Lag Phase", 0, lag_time, "rgba(148, 163, 184, 0.16)"),
        ("Log Phase", lag_time, 24, "rgba(139, 92, 246, 0.20)"),
        ("Stationary Phase", 24, 38, "rgba(251, 191, 36, 0.13)"),
        ("Death Phase", 38, 48, "rgba(244, 63, 94, 0.16)")
    ]

    for name, start, end, color in regions:
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor=color,
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
        marker=dict(size=14, color="#34d399", line=dict(color="#dcfce7", width=1))
    ))

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=45, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.45)",
        font=dict(color="#f8fafc"),
        legend=dict(
            orientation="h",
            y=1.12,
            x=0.02,
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            title="Time (hours)",
            range=[0, 48],
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            title="Optical Density (OD600)",
            range=[0, max(1.25, max_od + 0.25)],
            gridcolor="rgba(255,255,255,0.08)"
        )
    )

    return fig


def metric_card(label, value, caption, color_class=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color_class}">{value}</div>
        <div class="metric-caption">{caption}</div>
    </div>
    """, unsafe_allow_html=True)


st.sidebar.markdown("""
<div class="logo-box">
    <div class="logo-icon">⌬</div>
    <div>
        <div class="logo-title">Microbial<span>AI</span></div>
        <div class="logo-sub">Growth Predictor</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-heading">1. Select Microorganism</div>', unsafe_allow_html=True)

search_text = st.sidebar.text_input(
    "Search microorganism",
    placeholder="Search microorganism...",
    label_visibility="collapsed"
)

microbe_options = list(MICROBES.keys())
if search_text:
    filtered = [m for m in microbe_options if search_text.lower() in m.lower()]
    if filtered:
        microbe_options = filtered

microbe_name = st.sidebar.radio(
    "Microorganism",
    microbe_options,
    label_visibility="collapsed"
)

st.sidebar.caption(MICROBES[microbe_name]["type"])

st.sidebar.markdown('<div class="sidebar-heading">2. Environmental Conditions</div>', unsafe_allow_html=True)

incubation_time = st.sidebar.slider("Incubation Time (hours)", 0, 48, 24)
temperature = st.sidebar.slider("Temperature (°C)", 15, 50, MICROBES[microbe_name]["opt_temp"])
ph = st.sidebar.slider("pH", 4.0, 9.0, MICROBES[microbe_name]["opt_ph"], 0.1)
nutrient = st.sidebar.slider("Nutrient Concentration", 0.1, 2.0, 1.0, 0.1)

st.sidebar.caption("Relative scale: 0.1 - 2.0")

predict = st.sidebar.button("↗ Predict Growth")
reset = st.sidebar.button("↻ Reset All")


growth_rate, max_od, lag_time, condition_score, temp_factor, ph_factor, nutrient_factor = calculate_growth(
    microbe_name,
    temperature,
    ph,
    nutrient
)

time_values = np.linspace(0, 48, 260)
od_values = logistic_growth(time_values, growth_rate, max_od, lag_time)
current_od = float(logistic_growth(incubation_time, growth_rate, max_od, lag_time))

phase, phase_caption = get_phase(incubation_time, lag_time)

df = pd.DataFrame({
    "Time": time_values,
    "OD600": od_values
})


st.markdown("""
<div class="hero">
    <h1>AI-Assisted Microbial Growth Predictor</h1>
    <p>Predict and analyze microbial growth under different environmental conditions</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Growth Phase", phase, phase_caption, "green")

with m2:
    metric_card("Predicted OD (600nm)", f"{current_od:.3f}", "Optical Density", "")

with m3:
    metric_card("Max OD (K)", f"{max_od:.3f}", "Carrying Capacity", "purple")

with m4:
    metric_card("Growth Rate (r)", f"{growth_rate:.3f} /hr", "Intrinsic Growth Rate", "pink")


st.write("")

main_col, side_col = st.columns([3.1, 1.05])

with main_col:
    st.markdown(f"""
    <div class="chart-card">
        <div class="card-title">Predicted Growth Curve</div>
        <div style="color:#cbd5e1; margin-top:-8px; margin-bottom:10px;">
            <em>{microbe_name}</em>
        </div>
    """, unsafe_allow_html=True)

    chart = create_growth_chart(df, incubation_time, current_od, lag_time, max_od)
    st.plotly_chart(chart, use_container_width=True)

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
            <div class="insight-title green">Optimal Conditions</div>
            <div class="insight-text">{condition_msg}</div>
        </div>
        """, unsafe_allow_html=True)

    with i2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title purple">Fast Growth</div>
            <div class="insight-text">{speed_msg}</div>
        </div>
        """, unsafe_allow_html=True)

    with i3:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title yellow">High Biomass</div>
            <div class="insight-text">High carrying capacity indicates good nutrient availability.</div>
        </div>
        """, unsafe_allow_html=True)

    with i4:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title pink">Recommendation</div>
            <div class="insight-text">Maintain suitable conditions to prolong logarithmic growth phase.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


with side_col:
    st.markdown("""
    <div class="side-card">
        <div class="card-title">Growth Phase Information</div>

        <div class="phase-row">
            <div class="phase-name">Lag Phase</div>
            <div class="phase-desc">Cells adapting to environment<br>0 - 8 hrs</div>
        </div>

        <div class="phase-row">
            <div class="phase-name">Log Phase</div>
            <div class="phase-desc">Exponential cell division<br>8 - 20 hrs</div>
        </div>

        <div class="phase-row">
            <div class="phase-name">Stationary Phase</div>
            <div class="phase-desc">Nutrient limitation begins<br>20 - 35 hrs</div>
        </div>

        <div class="phase-row">
            <div class="phase-name">Death Phase</div>
            <div class="phase-desc">Cell death exceeds growth<br>35+ hrs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="side-card">
        <div class="card-title">Model Summary</div>
        <p style="color:#cbd5e1; font-size:13px; line-height:1.6;">
            The prediction is based on a modified logistic growth model that considers
            environmental factors and microbial characteristics.
        </p>

        <div class="summary-row">
            <span>Model Type</span>
            <span>Logistic Growth</span>
        </div>

        <div class="summary-row">
            <span>Equation</span>
            <span>K / (1 + e<sup>-r(t-t0)</sup>)</span>
        </div>

        <div class="summary-row">
            <span>Lag Time (t0)</span>
            <span>{lag_time:.1f} hours</span>
        </div>

        <div class="summary-row">
            <span>Carry Capacity (K)</span>
            <span>{max_od:.3f} OD</span>
        </div>

        <div class="summary-row">
            <span>Growth Rate (r)</span>
            <span>{growth_rate:.3f} /hr</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div class="footer">
    <div>MicrobialAI Growth Predictor<br>AI-Powered • Accurate • Intelligent</div>
    <div>Developed for researchers, students and biotech professionals</div>
    <div>Built using Streamlit • Python • NumPy • Plotly</div>
</div>
""", unsafe_allow_html=True)

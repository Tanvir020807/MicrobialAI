import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="MicrobialAI Growth Predictor",
    page_icon="🧬",
    layout="wide"
)

MICROBES = {
    "Escherichia coli": {
        "type": "Gram-negative bacterium",
        "color": "#22c55e",
        "base_rate": 1.05,
        "max_od": 1.00,
        "opt_temp": 37,
        "opt_ph": 7.0,
        "lag_time": 5
    },
    "Bacillus subtilis": {
        "type": "Gram-positive bacterium",
        "color": "#fbbf24",
        "base_rate": 0.82,
        "max_od": 0.92,
        "opt_temp": 35,
        "opt_ph": 7.2,
        "lag_time": 7
    },
    "Staphylococcus aureus": {
        "type": "Gram-positive cocci",
        "color": "#8b5cf6",
        "base_rate": 0.72,
        "max_od": 0.84,
        "opt_temp": 37,
        "opt_ph": 7.4,
        "lag_time": 8
    },
    "Pseudomonas aeruginosa": {
        "type": "Gram-negative bacterium",
        "color": "#06b6d4",
        "base_rate": 0.88,
        "max_od": 0.95,
        "opt_temp": 33,
        "opt_ph": 7.1,
        "lag_time": 7
    },
    "Lactobacillus acidophilus": {
        "type": "Lactic acid bacterium",
        "color": "#ec4899",
        "base_rate": 0.68,
        "max_od": 0.78,
        "opt_temp": 37,
        "opt_ph": 5.8,
        "lag_time": 9
    },
    "Saccharomyces cerevisiae": {
        "type": "Yeast",
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
.stApp {
    background: linear-gradient(135deg, #050914, #07111f, #081525);
    color: #f8fafc;
}

.main .block-container {
    max-width: 1500px;
    padding-top: 1.4rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071225, #050914);
    border-right: 1px solid rgba(148, 163, 184, 0.22);
}

.logo-title {
    font-size: 26px;
    font-weight: 800;
    color: white;
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
    font-weight: 700;
    margin-top: 18px;
    margin-bottom: 8px;
}

.metric-card,
.chart-card,
.side-card,
.insight-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.97), rgba(8, 18, 34, 0.97));
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 12px;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
}

.metric-card {
    min-height: 135px;
    padding: 24px;
}

.metric-label {
    color: white;
    font-size: 15px;
    font-weight: 600;
}

.metric-value {
    margin-top: 18px;
    color: white;
    font-size: 31px;
    font-weight: 800;
}

.metric-caption {
    color: #cbd5e1;
    margin-top: 8px;
    font-size: 13px;
}

.green { color: #22c55e; }
.blue { color: #3b82f6; }
.purple { color: #8b5cf6; }
.yellow { color: #fbbf24; }
.pink { color: #ec4899; }
.red { color: #fb7185; }

.hero {
    position: relative;
    padding: 12px 8px 20px;
}

.hero h1 {
    font-size: 35px;
    font-weight: 800;
    color: white;
    margin: 0;
}

.hero p {
    color: #cbd5e1;
    margin-top: 10px;
    font-size: 15px;
}

.about-btn {
    position: absolute;
    right: 10px;
    top: 8px;
    padding: 12px 18px;
    border-radius: 10px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.22);
    color: white;
    font-weight: 700;
}

.chart-card {
    padding: 22px;
}

.card-title {
    font-size: 20px;
    font-weight: 800;
    color: white;
    margin-bottom: 12px;
}

.chart-subtitle {
    color: #cbd5e1;
    font-style: italic;
    margin-top: -8px;
    margin-bottom: 10px;
}

/* IMPORTANT: This fixes Growth Phase Information */
.phase-panel {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.97), rgba(8, 18, 34, 0.97));
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 15px;
}

.phase-panel-title {
    font-size: 20px;
    font-weight: 800;
    color: white;
    margin-bottom: 14px;
}

.phase-row {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 10px;
    padding: 13px;
    margin-bottom: 9px;
}

.phase-icon {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 18px;
    font-weight: 800;
    flex-shrink: 0;
}

.phase-icon.purple {
    color: #8b5cf6;
    background: rgba(139, 92, 246, 0.16);
}

.phase-icon.green {
    color: #22c55e;
    background: rgba(34, 197, 94, 0.16);
}

.phase-icon.yellow {
    color: #fbbf24;
    background: rgba(251, 191, 36, 0.16);
}

.phase-icon.red {
    color: #fb7185;
    background: rgba(251, 113, 133, 0.16);
}

.phase-name {
    color: white;
    font-size: 14px;
    font-weight: 800;
}

.phase-desc {
    color: #cbd5e1;
    font-size: 12px;
    line-height: 1.5;
    margin-top: 4px;
}

.summary-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    border-top: 1px solid rgba(148, 163, 184, 0.14);
    padding: 9px 0;
    color: #cbd5e1;
    font-size: 13px;
}

.summary-row span:last-child {
    color: #60a5fa;
    font-weight: 700;
    text-align: right;
}

.summary-text {
    color: #cbd5e1;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 13px;
}

.insight-card {
    padding: 17px;
    min-height: 110px;
}

.insight-title {
    font-weight: 800;
    margin-bottom: 8px;
}

.insight-text {
    color: #cbd5e1;
    font-size: 12px;
    line-height: 1.55;
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

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=45, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.45)",
        font=dict(color="#f8fafc", size=12),
        legend=dict(orientation="h", y=1.14, x=0),
        xaxis=dict(
            title="Time (hours)",
            range=[0, 48],
            tickvals=[0, 8, 16, 24, 32, 40, 48],
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            title="Optical Density (OD600)",
            range=[0, max(1.25, max_od + 0.25)],
            tickvals=[0, 0.25, 0.5, 0.75, 1.0, 1.25],
            gridcolor="rgba(255,255,255,0.08)"
        )
    )

    return fig


def metric_card(label, value, caption, color=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{value}</div>
        <div class="metric-caption">{caption}</div>
    </div>
    """, unsafe_allow_html=True)


def growth_phase_information():
    st.markdown("""
    <div class="phase-panel">
        <div class="phase-panel-title">Growth Phase Information</div>

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
            <div class="phase-icon red">×</div>
            <div>
                <div class="phase-name">Death Phase</div>
                <div class="phase-desc">Cell death exceeds growth<br>35+ hrs</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


st.sidebar.markdown("""
<div class="logo-title">Microbial<span>AI</span></div>
<div class="logo-sub">Growth Predictor</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-heading">1. Select Microorganism</div>', unsafe_allow_html=True)

microbe_name = st.sidebar.selectbox(
    "Microorganism",
    list(MICROBES.keys())
)

st.sidebar.caption(MICROBES[microbe_name]["type"])

st.sidebar.markdown('<div class="sidebar-heading">2. Environmental Conditions</div>', unsafe_allow_html=True)

incubation_time = st.sidebar.slider("Incubation Time (hours)", 0, 48, 24)
temperature = st.sidebar.slider("Temperature (°C)", 15, 50, MICROBES[microbe_name]["opt_temp"])
ph = st.sidebar.slider("pH", 4.0, 9.0, MICROBES[microbe_name]["opt_ph"], 0.1)
nutrient = st.sidebar.slider("Nutrient Concentration", 0.1, 2.0, 1.0, 0.1)

st.sidebar.caption("Relative scale: 0.1 - 2.0")
st.sidebar.button("Predict Growth")
st.sidebar.button("Reset All")

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

df = pd.DataFrame({
    "Time": time_values,
    "OD600": od_values
})

st.markdown("""
<div class="hero">
    <h1>AI-Assisted Microbial Growth Predictor</h1>
    <p>Predict and analyze microbial growth under different environmental conditions</p>
    <div class="about-btn">ⓘ About Model</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card("Growth Phase", phase, phase_caption, "green")

with col2:
    metric_card("Predicted OD (600nm)", f"{current_od:.3f}", "Optical Density")

with col3:
    metric_card("Max OD (K)", f"{max_od:.3f}", "Carrying Capacity", "purple")

with col4:
    metric_card("Growth Rate (r)", f"{growth_rate:.3f} /hr", "Intrinsic Growth Rate", "pink")

st.write("")

main_col, side_col = st.columns([3.1, 1.05])

with main_col:
    st.markdown(f"""
    <div class="chart-card">
        <div class="card-title">Predicted Growth Curve</div>
        <div class="chart-subtitle">{microbe_name}</div>
    """, unsafe_allow_html=True)

    st.plotly_chart(
        make_chart(df, incubation_time, current_od, lag_time, max_od),
        use_container_width=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    st.markdown('<div class="chart-card"><div class="card-title">Growth Insights</div>', unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)

    with i1:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title green">Optimal Conditions</div>
            <div class="insight-text">Temperature, pH and nutrients affect microbial growth quality.</div>
        </div>
        """, unsafe_allow_html=True)

    with i2:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title purple">Fast Growth</div>
            <div class="insight-text">Higher growth rate means faster increase in optical density.</div>
        </div>
        """, unsafe_allow_html=True)

    with i3:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title yellow">High Biomass</div>
            <div class="insight-text">High carrying capacity indicates better final biomass production.</div>
        </div>
        """, unsafe_allow_html=True)

    with i4:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title pink">Recommendation</div>
            <div class="insight-text">Adjust temperature, pH, and nutrients to compare growth output.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with side_col:
    growth_phase_information()

    st.markdown(f"""
    <div class="side-card">
        <div class="card-title">Model Summary</div>
        <div class="summary-text">
            The prediction is based on a modified logistic growth model.
        </div>

        <div class="summary-row">
            <span>Model Type</span>
            <span>Logistic Growth</span>
        </div>
        <div class="summary-row">
            <span>Equation</span>
            <span>K / (1 + e<sup>-r(t-t0)</sup>)</span>
        </div>
        <div class="summary-row">
            <span>Lag Time</span>
            <span>{lag_time:.1f} hours</span>
        </div>
        <div class="summary-row">
            <span>Carry Capacity</span>
            <span>{max_od:.3f} OD</span>
        </div>
        <div class="summary-row">
            <span>Growth Rate</span>
            <span>{growth_rate:.3f} /hr</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

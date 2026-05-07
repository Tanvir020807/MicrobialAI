import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="MicrobialAI Growth Predictor",
    page_icon="🧬",
    layout="wide"
)


# -----------------------------
# Microorganism database
# -----------------------------
MICROORGANISMS = {
    "Escherichia coli": {
        "type": "Gram-negative bacterium",
        "base_rate": 1.05,
        "carrying_capacity": 1.00,
        "opt_temp": 37,
        "opt_ph": 7.0,
        "lag_time": 8
    },
    "Bacillus subtilis": {
        "type": "Gram-positive bacterium",
        "base_rate": 0.82,
        "carrying_capacity": 0.92,
        "opt_temp": 35,
        "opt_ph": 7.2,
        "lag_time": 9
    },
    "Staphylococcus aureus": {
        "type": "Gram-positive cocci",
        "base_rate": 0.72,
        "carrying_capacity": 0.84,
        "opt_temp": 37,
        "opt_ph": 7.4,
        "lag_time": 10
    },
    "Pseudomonas aeruginosa": {
        "type": "Gram-negative bacterium",
        "base_rate": 0.88,
        "carrying_capacity": 0.95,
        "opt_temp": 33,
        "opt_ph": 7.1,
        "lag_time": 9
    },
    "Lactobacillus acidophilus": {
        "type": "Lactic acid bacterium",
        "base_rate": 0.68,
        "carrying_capacity": 0.78,
        "opt_temp": 37,
        "opt_ph": 5.8,
        "lag_time": 11
    },
    "Saccharomyces cerevisiae": {
        "type": "Yeast",
        "base_rate": 0.60,
        "carrying_capacity": 0.88,
        "opt_temp": 30,
        "opt_ph": 5.5,
        "lag_time": 12
    }
}


# -----------------------------
# CSS styling
# -----------------------------
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(36, 214, 255, 0.16), transparent 32rem),
        linear-gradient(135deg, #050914, #08172d);
    color: white;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071225, #050914);
    border-right: 1px solid rgba(120, 160, 255, 0.22);
}

.main-title {
    font-size: 54px;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(90deg, #25e0f2, #477cff, #a75cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    color: #b7c7d9;
    font-size: 20px;
    margin-top: 6px;
}

.card {
    background: linear-gradient(145deg, #0d1d35, #081225);
    padding: 22px;
    border-radius: 14px;
    border: 1px solid rgba(120, 160, 255, 0.25);
    box-shadow: 0px 12px 35px rgba(0, 0, 0, 0.28);
    min-height: 130px;
}

.metric-label {
    color: #dce8f7;
    font-size: 15px;
}

.metric-value {
    color: #24d6ff;
    font-size: 32px;
    font-weight: 800;
    margin-top: 12px;
}

.green { color: #31e981; }
.yellow { color: #ffd34d; }
.pink { color: #ff4c87; }
.blue { color: #24d6ff; }

.info-box {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(120,160,255,0.20);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 10px;
}

.small-text {
    color: #b7c7d9;
    font-size: 14px;
}

hr {
    border-color: rgba(120, 160, 255, 0.18);
}

.stButton > button {
    background: linear-gradient(90deg, #1479ff, #a829e8);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Model functions
# -----------------------------
def bell_factor(value, optimum, tolerance):
    """
    Gives a value between 0 and 1.
    The score is highest when the input is close to the optimum.
    """
    score = math.exp(-((value - optimum) / tolerance) ** 2)
    return max(0.05, min(1.0, score))


def calculate_growth_parameters(microbe_name, temperature, ph, nutrient):
    microbe = MICROORGANISMS[microbe_name]

    temp_factor = bell_factor(temperature, microbe["opt_temp"], 10)
    ph_factor = bell_factor(ph, microbe["opt_ph"], 1.6)
    nutrient_factor = max(0.10, min(1.25, nutrient))

    condition_score = (
        temp_factor * 0.40
        + ph_factor * 0.35
        + min(nutrient_factor, 1.0) * 0.25
    )

    growth_rate = microbe["base_rate"] * temp_factor * ph_factor * nutrient_factor
    carrying_capacity = microbe["carrying_capacity"] * (0.55 + 0.45 * nutrient_factor)
    lag_time = microbe["lag_time"] + (1 - condition_score) * 8

    return {
        "growth_rate": growth_rate,
        "carrying_capacity": carrying_capacity,
        "lag_time": lag_time,
        "condition_score": condition_score,
        "temp_factor": temp_factor,
        "ph_factor": ph_factor,
        "nutrient_factor": nutrient_factor
    }


def logistic_growth(time, growth_rate, carrying_capacity, lag_time):
    return carrying_capacity / (1 + np.exp(-growth_rate * (time - lag_time)))


def get_growth_phase(time, lag_time):
    if time < lag_time:
        return "Lag Phase"
    elif time < 24:
        return "Log Phase"
    elif time < 40:
        return "Stationary Phase"
    else:
        return "Death Phase"


def create_growth_chart(df, incubation_time, current_od, lag_time, carrying_capacity):
    fig = go.Figure()

    phase_regions = [
        ("Lag Phase", 0, lag_time, "rgba(160,102,255,0.18)"),
        ("Log Phase", lag_time, 24, "rgba(36,214,255,0.14)"),
        ("Stationary Phase", 24, 40, "rgba(49,233,129,0.14)"),
        ("Death Phase", 40, 48, "rgba(255,76,135,0.14)")
    ]

    for phase_name, start, end, color in phase_regions:
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor=color,
            opacity=1,
            line_width=0,
            annotation_text=phase_name,
            annotation_position="top"
        )

    fig.add_trace(go.Scatter(
        x=df["Time"],
        y=df["OD600"],
        mode="lines",
        name="Growth Curve",
        line=dict(color="#24d6ff", width=4)
    ))

    fig.add_trace(go.Scatter(
        x=[incubation_time],
        y=[current_od],
        mode="markers",
        name="Current Point",
        marker=dict(size=15, color="#31e981", line=dict(color="white", width=1))
    ))

    fig.update_layout(
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,9,20,0.65)",
        font=dict(color="white"),
        xaxis_title="Time (hours)",
        yaxis_title="Optical Density (OD600)",
        xaxis=dict(range=[0, 48], gridcolor="rgba(255,255,255,0.12)"),
        yaxis=dict(
            range=[0, max(1.25, carrying_capacity + 0.2)],
            gridcolor="rgba(255,255,255,0.12)"
        ),
        legend=dict(orientation="h", y=-0.15)
    )

    return fig


def create_condition_chart(temp_factor, ph_factor, nutrient_factor):
    fig = go.Figure(go.Bar(
        x=[temp_factor, ph_factor, min(nutrient_factor, 1.0)],
        y=["Temperature", "pH", "Nutrients"],
        orientation="h",
        marker_color=["#24d6ff", "#31e981", "#ffd34d"],
        text=[
            f"{temp_factor * 100:.0f}%",
            f"{ph_factor * 100:.0f}%",
            f"{min(nutrient_factor, 1.0) * 100:.0f}%"
        ],
        textposition="auto"
    ))

    fig.update_layout(
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,9,20,0.65)",
        font=dict(color="white"),
        xaxis=dict(range=[0, 1], title="Suitability"),
        yaxis=dict(title="")
    )

    return fig


# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.markdown("## 🧬 MicrobialAI")
st.sidebar.caption("Growth Prediction Project")

microbe_name = st.sidebar.radio(
    "1. Select Microorganism",
    list(MICROORGANISMS.keys())
)

st.sidebar.caption(MICROORGANISMS[microbe_name]["type"])

st.sidebar.markdown("### 2. Environmental Conditions")

incubation_time = st.sidebar.slider("Incubation Time (hours)", 0, 48, 24)

temperature = st.sidebar.slider(
    "Temperature (°C)",
    15,
    50,
    MICROORGANISMS[microbe_name]["opt_temp"]
)

ph = st.sidebar.slider(
    "pH",
    4.0,
    9.0,
    MICROORGANISMS[microbe_name]["opt_ph"],
    0.1
)

nutrient = st.sidebar.slider(
    "Nutrient Concentration",
    0.1,
    2.0,
    1.0,
    0.1
)

st.sidebar.button("Predict Growth")

st.sidebar.caption("Nutrient scale: 0.1 = low, 1.0 = normal, 2.0 = high")


# -----------------------------
# Calculations
# -----------------------------
params = calculate_growth_parameters(
    microbe_name,
    temperature,
    ph,
    nutrient
)

growth_rate = params["growth_rate"]
carrying_capacity = params["carrying_capacity"]
lag_time = params["lag_time"]
condition_score = params["condition_score"]

time_values = np.linspace(0, 48, 250)
od_values = logistic_growth(time_values, growth_rate, carrying_capacity, lag_time)

current_od = logistic_growth(
    incubation_time,
    growth_rate,
    carrying_capacity,
    lag_time
)

phase = get_growth_phase(incubation_time, lag_time)

df = pd.DataFrame({
    "Time": time_values,
    "OD600": od_values
})


# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="main-title">MicrobialAI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">AI-Assisted Microbial Growth Prediction Platform</div>',
    unsafe_allow_html=True
)
st.write("Predict microbial growth using temperature, pH, nutrients, and incubation time.")

st.write("")


# -----------------------------
# Top metrics
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Growth Phase</div>
        <div class="metric-value green">{phase}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Predicted OD600</div>
        <div class="metric-value">{current_od:.3f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Growth Rate</div>
        <div class="metric-value pink">{growth_rate:.3f} /hr</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Carrying Capacity</div>
        <div class="metric-value yellow">{carrying_capacity:.3f}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# -----------------------------
# Main layout
# -----------------------------
left, right = st.columns([2.2, 1])

with left:
    st.markdown("### Predicted Growth Curve")

    growth_fig = create_growth_chart(
        df,
        incubation_time,
        current_od,
        lag_time,
        carrying_capacity
    )

    st.plotly_chart(growth_fig, use_container_width=True)

with right:
    st.markdown("### Growth Phase Information")

    st.markdown("""
    <div class="info-box">
        <b>Lag Phase</b><br>
        <span class="small-text">Cells adjust to the environment before rapid growth starts.</span>
    </div>

    <div class="info-box">
        <b>Log Phase</b><br>
        <span class="small-text">Cells divide quickly and population increases rapidly.</span>
    </div>

    <div class="info-box">
        <b>Stationary Phase</b><br>
        <span class="small-text">Growth slows because nutrients become limited.</span>
    </div>

    <div class="info-box">
        <b>Death Phase</b><br>
        <span class="small-text">More cells die than divide due to stress or waste buildup.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Model Summary")

    st.markdown(f"""
    <div class="info-box">Model Type: Logistic Growth</div>
    <div class="info-box">Equation: K / (1 + e<sup>-r(t-t0)</sup>)</div>
    <div class="info-box">Lag Time: {lag_time:.1f} hours</div>
    <div class="info-box">Growth Rate: {growth_rate:.3f} /hr</div>
    <div class="info-box">Carrying Capacity: {carrying_capacity:.3f} OD</div>
    """, unsafe_allow_html=True)


# -----------------------------
# Insights
# -----------------------------
st.write("")
st.markdown("### Growth Insights")

if condition_score >= 0.78:
    condition_msg = "Conditions are close to optimal for this microorganism."
elif condition_score >= 0.50:
    condition_msg = "Growth is possible, but conditions can be improved."
else:
    condition_msg = "The microorganism may be under environmental stress."

if growth_rate >= 0.8:
    speed_msg = "Fast growth is predicted under these conditions."
elif growth_rate >= 0.45:
    speed_msg = "Moderate growth is predicted under these conditions."
else:
    speed_msg = "Slow growth is predicted under these conditions."

i1, i2, i3, i4 = st.columns(4)

with i1:
    st.markdown(f"""
    <div class="card">
        <b class="green">Condition Score</b><br><br>
        {condition_msg}
    </div>
    """, unsafe_allow_html=True)

with i2:
    st.markdown(f"""
    <div class="card">
        <b class="blue">Growth Speed</b><br><br>
        {speed_msg}
    </div>
    """, unsafe_allow_html=True)

with i3:
    st.markdown(f"""
    <div class="card">
        <b class="yellow">Biomass</b><br><br>
        Maximum predicted OD600 is {carrying_capacity:.2f}.
    </div>
    """, unsafe_allow_html=True)

with i4:
    st.markdown(f"""
    <div class="card">
        <b class="pink">Recommendation</b><br><br>
        Compare different pH, temperature, and nutrient values to improve growth.
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# Condition suitability
# -----------------------------
st.write("")
st.markdown("### Condition Suitability")

condition_fig = create_condition_chart(
    params["temp_factor"],
    params["ph_factor"],
    params["nutrient_factor"]
)

st.plotly_chart(condition_fig, use_container_width=True)

st.caption(
    "Note: This is a student-level simulation project for learning purposes. "
    "It is not a real laboratory-validated prediction system."
)

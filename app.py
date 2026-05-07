import streamlit as st
import numpy as np
import plotly.graph_objects as go

# -------------------------------
# Page Config
# -------------------------------

st.set_page_config(
    page_title="MicrobialAI",
    page_icon="🧪",
    layout="wide"
)

# -------------------------------
# Custom Styling
# -------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #050816;
    color: white;
}

h1, h2, h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# Microbial Database
# -------------------------------

MICROBES = {

    "E. coli": {
        "K": 1.0,
        "r": 1.2,
        "t0": 8
    },

    "Bacillus subtilis": {
        "K": 1.1,
        "r": 1.0,
        "t0": 10
    },

    "Pseudomonas aeruginosa": {
        "K": 1.2,
        "r": 0.7,
        "t0": 14
    },

    "Staphylococcus aureus": {
        "K": 0.9,
        "r": 0.8,
        "t0": 12
    }
}

# -------------------------------
# Title
# -------------------------------

st.title("🧪 AI-Assisted Microbial Growth Predictor")

st.write(
    "Predict microbial growth under different environmental conditions."
)

# -------------------------------
# Sidebar
# -------------------------------

with st.sidebar:

    st.header("Growth Conditions")

    microbe = st.selectbox(
        "Select Organism",
        list(MICROBES.keys())
    )

    time = st.slider(
        "Incubation Time (hours)",
        0,
        48,
        24
    )

    temp = st.slider(
        "Temperature (°C)",
        20,
        45,
        37
    )

    ph = st.slider(
        "pH",
        4.0,
        10.0,
        7.0
    )

    nutrient = st.slider(
        "Nutrient Concentration",
        0.1,
        2.0,
        1.0
    )

# -------------------------------
# Growth Model
# -------------------------------

params = MICROBES[microbe]

K = params["K"]
r = params["r"]
t0 = params["t0"]

# Environmental effects

if temp < 30:
    r *= 0.75

elif temp > 40:
    r *= 0.65

if ph < 6 or ph > 8:
    r *= 0.8

K *= nutrient

# Logistic Growth Equation

growth = K / (1 + np.exp(-r * (time - t0)))

# Growth Phase

if time < t0:
    phase = "Lag Phase"

elif growth < 0.7 * K:
    phase = "Log Phase"

elif time < 40:
    phase = "Stationary Phase"

else:
    phase = "Death Phase"

# -------------------------------
# Metrics
# -------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Growth Phase", phase)

with col2:
    st.metric("Predicted OD600", round(growth, 3))

with col3:
    st.metric("Growth Rate", round(r, 3))

# -------------------------------
# Generate Curve
# -------------------------------

t_values = np.linspace(0, 48, 500)

growth_curve = K / (
    1 + np.exp(-r * (t_values - t0))
)

# -------------------------------
# Plotly Figure
# -------------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=t_values,
        y=growth_curve,
        mode='lines',
        name='Growth Curve',
        line=dict(color='cyan', width=4)
    )
)

fig.add_trace(
    go.Scatter(
        x=[time],
        y=[growth],
        mode='markers',
        name='Current Point',
        marker=dict(color='lime', size=14)
    )
)

# Layout

fig.update_layout(
    title=f"{microbe} Growth Prediction",
    template="plotly_dark",
    xaxis_title="Time (hours)",
    yaxis_title="Optical Density (OD600)",
    height=650
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Model Info
# -------------------------------

st.subheader("Model Information")

st.write(
    "This platform uses a logistic growth model modified by environmental conditions such as temperature, pH, and nutrient concentration."
)

st.latex(r"G(t) = \\frac{K}{1 + e^{-r(t-t_0)}}")

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MicrobialAI",
    page_icon="🧬",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

[data-testid="stAppViewContainer"]{
    background:
    linear-gradient(
        135deg,
        #020617,
        #071426,
        #0f172a
    );
    color:white;
}

section[data-testid="stSidebar"]{
    background:#07111f;
    border-right:1px solid rgba(255,255,255,0.08);
}

h1{
    font-size:64px !important;
    font-weight:900;
    color:white;
}

.glow {
    color:#67e8f9;
    text-shadow:0px 0px 20px rgba(0,255,255,0.7);
}

.metric-card{
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.08);
    padding:28px;
    border-radius:20px;
    backdrop-filter:blur(16px);
    box-shadow:0px 0px 25px rgba(0,255,255,0.08);
}

.metric-title{
    color:#94a3b8;
    font-size:16px;
}

.metric-value{
    font-size:34px;
    font-weight:800;
    color:#67e8f9;
}

.small-text{
    color:#cbd5e1;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# MICROBIAL DATABASE
# =========================================================

MICROBES = {

    "E. coli": {
        "K": 1.0,
        "r": 1.2,
        "t0": 8,
        "type": "Gram-negative"
    },

    "Bacillus subtilis": {
        "K": 1.1,
        "r": 1.0,
        "t0": 10,
        "type": "Gram-positive"
    },

    "Pseudomonas aeruginosa": {
        "K": 1.2,
        "r": 0.7,
        "t0": 14,
        "type": "Pathogenic"
    },

    "Staphylococcus aureus": {
        "K": 0.9,
        "r": 0.8,
        "t0": 12,
        "type": "Gram-positive cocci"
    },

    "Saccharomyces cerevisiae": {
        "K": 1.0,
        "r": 0.5,
        "t0": 16,
        "type": "Yeast"
    }
}

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚙️ Control Panel")

    st.write("Configure microbial conditions")

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

# =========================================================
# MODEL
# =========================================================

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

# Logistic equation

growth = K / (1 + np.exp(-r * (time - t0)))

# Phase detection

if time < t0:
    phase = "Lag Phase"

elif growth < 0.7 * K:
    phase = "Log Phase"

elif time < 40:
    phase = "Stationary Phase"

else:
    phase = "Death Phase"

# =========================================================
# HEADER
# =========================================================

st.markdown(
    "<h1>🧬 <span class='glow'>MicrobialAI</span></h1>",
    unsafe_allow_html=True
)

st.markdown("""
### AI-Assisted Microbial Growth Kinetics Platform
""")

st.write(
    "Predict microbial growth dynamics under varying environmental conditions using computational growth modeling."
)

st.write("")

# =========================================================
# METRIC CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Growth Phase</div>
        <div class="metric-value">{phase}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Predicted OD600</div>
        <div class="metric-value">{round(growth,3)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Growth Rate</div>
        <div class="metric-value">{round(r,3)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Microbial Type</div>
        <div class="metric-value">{params['type']}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# =========================================================
# GROWTH CURVE
# =========================================================

t_values = np.linspace(0, 48, 500)

growth_curve = K / (
    1 + np.exp(-r * (t_values - t0))
)

fig = go.Figure()

# Main growth curve

fig.add_trace(
    go.Scatter(
        x=t_values,
        y=growth_curve,
        mode='lines',
        name='Growth Curve',
        line=dict(
            color='#22d3ee',
            width=5
        )
    )
)

# Current point

fig.add_trace(
    go.Scatter(
        x=[time],
        y=[growth],
        mode='markers',
        name='Current Condition',
        marker=dict(
            color='#4ade80',
            size=16,
            line=dict(
                color='white',
                width=2
            )
        )
    )
)

# Phase regions

fig.add_vrect(
    x0=0,
    x1=10,
    fillcolor="purple",
    opacity=0.08,
    line_width=0
)

fig.add_vrect(
    x0=10,
    x1=25,
    fillcolor="blue",
    opacity=0.08,
    line_width=0
)

fig.add_vrect(
    x0=25,
    x1=40,
    fillcolor="green",
    opacity=0.08,
    line_width=0
)

fig.add_vrect(
    x0=40,
    x1=48,
    fillcolor="red",
    opacity=0.08,
    line_width=0
)

# Phase labels

fig.add_annotation(
    x=5,
    y=0.15,
    text="Lag",
    showarrow=False,
    font=dict(size=16)
)

fig.add_annotation(
    x=17,
    y=0.5,
    text="Log",
    showarrow=False,
    font=dict(size=16)
)

fig.add_annotation(
    x=32,
    y=0.95,
    text="Stationary",
    showarrow=False,
    font=dict(size=16)
)

fig.add_annotation(
    x=44,
    y=0.8,
    text="Death",
    showarrow=False,
    font=dict(size=16)
)

# Layout

fig.update_layout(

    template="plotly_dark",

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",

    title=f"{microbe} Growth Kinetics",

    title_font=dict(size=28),

    xaxis_title="Time (hours)",

    yaxis_title="Optical Density (OD600)",

    height=720,

    font=dict(
        color="white",
        size=16
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# EXTRA INFO PANELS
# =========================================================

st.markdown("---")

info1, info2 = st.columns(2)

with info1:

    st.subheader("📌 Model Information")

    st.write("""
This platform predicts microbial growth using a logistic growth kinetics model influenced by:
    
- Temperature
- pH
- Nutrient concentration
- Incubation time
""")

    st.latex(r"G(t)=\frac{K}{1+e^{-r(t-t_0)}}")

with info2:

    st.subheader("🧪 Current Biological Interpretation")

    st.write(f"""
- Organism: **{microbe}**
- Predicted phase: **{phase}**
- Estimated OD600: **{round(growth,3)}**
- Simulated growth rate: **{round(r,3)}**
""")

st.markdown("---")

st.caption("MicrobialAI • Computational Microbiology & AI Platform")

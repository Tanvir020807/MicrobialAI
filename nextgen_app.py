import streamlit as st
import numpy as np
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MicrobialAI NextGen",
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
    background:#050b16;
    border-right:1px solid rgba(255,255,255,0.08);
}

h1{
    color:white;
    font-size:52px !important;
    font-weight:800;
}

.metric-card{
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:18px;
    padding:22px;
    backdrop-filter:blur(14px);
    box-shadow:0px 0px 24px rgba(0,255,255,0.06);
}

.metric-title{
    color:#94a3b8;
    font-size:15px;
}

.metric-value{
    color:#67e8f9;
    font-size:34px;
    font-weight:800;
}

.phase-card{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;
    padding:16px;
    margin-bottom:12px;
}

.insight-card{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:16px;
    padding:18px;
    text-align:center;
}

.big-glow{
    color:#67e8f9;
    text-shadow:0px 0px 25px rgba(0,255,255,0.7);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================

MICROBES = {

    "Escherichia coli": {
        "K": 1.0,
        "r": 1.05,
        "t0": 8,
        "type": "Gram-negative bacterium"
    },

    "Bacillus subtilis": {
        "K": 1.1,
        "r": 0.9,
        "t0": 10,
        "type": "Gram-positive bacterium"
    },

    "Staphylococcus aureus": {
        "K": 0.95,
        "r": 0.8,
        "t0": 12,
        "type": "Gram-positive cocci"
    },

    "Pseudomonas aeruginosa": {
        "K": 1.15,
        "r": 0.7,
        "t0": 14,
        "type": "Gram-negative bacterium"
    },

    "Lactobacillus acidophilus": {
        "K": 0.85,
        "r": 0.65,
        "t0": 16,
        "type": "Lactic acid bacterium"
    },

    "Saccharomyces cerevisiae": {
        "K": 0.9,
        "r": 0.55,
        "t0": 18,
        "type": "Yeast"
    }
}

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("# 🧬 MicrobialAI")
    st.caption("Growth Predictor")

    st.markdown("---")

    microbe = st.selectbox(
        "Select Microorganism",
        list(MICROBES.keys())
    )

    st.markdown("### Environmental Conditions")

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

# Environmental adjustments

if temp < 30:
    r *= 0.75

elif temp > 40:
    r *= 0.65

if ph < 6 or ph > 8:
    r *= 0.8

K *= nutrient

growth = K / (1 + np.exp(-r * (time - t0)))

# Phase logic

if time < 8:
    phase = "Lag Phase"

elif time < 24:
    phase = "Log Phase"

elif time < 40:
    phase = "Stationary Phase"

else:
    phase = "Death Phase"

# =========================================================
# MAIN LAYOUT
# =========================================================

left, right = st.columns([3,1])

# =========================================================
# LEFT PANEL
# =========================================================

with left:

    st.markdown(
        "<h1>AI-Assisted <span class='big-glow'>Microbial Growth Predictor</span></h1>",
        unsafe_allow_html=True
    )

    st.write(
        "Predict and analyze microbial growth under different environmental conditions."
    )

    st.write("")

    # METRICS

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Growth Phase</div>
            <div class="metric-value">{phase}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Predicted OD600</div>
            <div class="metric-value">{round(growth,3)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Max OD (K)</div>
            <div class="metric-value">{round(K,3)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Growth Rate (r)</div>
            <div class="metric-value">{round(r,3)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # GRAPH

    t_values = np.linspace(0,48,500)

    curve = K / (
        1 + np.exp(-r * (t_values - t0))
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=t_values,
            y=curve,
            mode='lines',
            line=dict(
                color='#3b82f6',
                width=4
            ),
            name='Growth Curve'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[time],
            y=[growth],
            mode='markers',
            marker=dict(
                color='#22c55e',
                size=14
            ),
            name='Current Point'
        )
    )

    # Phase regions

    fig.add_vrect(
        x0=0,
        x1=10,
        fillcolor="gray",
        opacity=0.08,
        line_width=0
    )

    fig.add_vrect(
        x0=10,
        x1=25,
        fillcolor="purple",
        opacity=0.08,
        line_width=0
    )

    fig.add_vrect(
        x0=25,
        x1=40,
        fillcolor="yellow",
        opacity=0.05,
        line_width=0
    )

    fig.add_vrect(
        x0=40,
        x1=48,
        fillcolor="red",
        opacity=0.05,
        line_width=0
    )

    fig.update_layout(

        template="plotly_dark",

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        title=f"{microbe} Growth Curve",

        height=620,

        xaxis_title="Time (hours)",

        yaxis_title="Optical Density (OD600)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # INSIGHTS

    st.markdown("## Growth Insights")

    i1, i2, i3, i4 = st.columns(4)

    with i1:
        st.markdown("""
        <div class="insight-card">
        <h4>🧪 Optimal Conditions</h4>
        <p>Conditions are favorable for growth.</p>
        </div>
        """, unsafe_allow_html=True)

    with i2:
        st.markdown("""
        <div class="insight-card">
        <h4>⚡ Fast Growth</h4>
        <p>Exponential phase predicted.</p>
        </div>
        """, unsafe_allow_html=True)

    with i3:
        st.markdown("""
        <div class="insight-card">
        <h4>📈 High Biomass</h4>
        <p>High carrying capacity detected.</p>
        </div>
        """, unsafe_allow_html=True)

    with i4:
        st.markdown("""
        <div class="insight-card">
        <h4>💡 Recommendation</h4>
        <p>Maintain current incubation conditions.</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# RIGHT PANEL
# =========================================================

with right:

    st.markdown("## Growth Phases")

    st.markdown("""
    <div class="phase-card">
    <h4>🟣 Lag Phase</h4>
    <p>Cells adapting to environment.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="phase-card">
    <h4>🟢 Log Phase</h4>
    <p>Rapid exponential growth.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="phase-card">
    <h4>🟡 Stationary Phase</h4>
    <p>Nutrient depletion begins.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="phase-card">
    <h4>🔴 Death Phase</h4>
    <p>Cell death exceeds growth.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("## Model Summary")

    st.markdown(f"""
    <div class="phase-card">

    <p><b>Model:</b> Logistic Growth</p>

    <p><b>Growth Rate:</b> {round(r,3)}</p>

    <p><b>Carrying Capacity:</b> {round(K,3)}</p>

    <p><b>Lag Time:</b> {t0} hrs</p>

    <p><b>Microbe Type:</b> {params['type']}</p>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "MicrobialAI • AI-Powered Computational Microbiology Platform"
)

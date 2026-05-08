import streamlit as st
import numpy as np
import plotly.graph_objects as go

# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="MicrobialAI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"]{
    font-family: 'Segoe UI', sans-serif;
}

[data-testid="stAppViewContainer"]{
    background: linear-gradient(
        135deg,
        #020617,
        #081224,
        #0f172a
    );
    color:white;
}

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    max-width:1400px;
}

.card{
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:18px;
    padding:18px;
}

.metric{
    font-size:34px;
    font-weight:700;
    color:#67e8f9;
}

.metric-label{
    color:#94a3b8;
    font-size:14px;
}

.title{
    font-size:52px;
    font-weight:800;
    color:#67e8f9;
}

.subtitle{
    color:#cbd5e1;
    font-size:18px;
}

.small-card{
    background:rgba(255,255,255,0.03);
    border-radius:14px;
    padding:14px;
    border:1px solid rgba(255,255,255,0.05);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# DATA
# =====================================================

MICROBES = {
    "E. coli": [1.0,1.05,8],
    "Bacillus subtilis": [1.1,0.9,10],
    "Pseudomonas": [1.15,0.7,14],
    "Yeast": [0.9,0.55,18]
}

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🧬 MicrobialAI")

    microbe = st.selectbox(
        "Microorganism",
        list(MICROBES.keys())
    )

    time = st.slider(
        "Time (hrs)",
        0,
        48,
        24
    )

    temp = st.slider(
        "Temperature",
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

# =====================================================
# MODEL
# =====================================================

K,r,t0 = MICROBES[microbe]

growth = K / (
    1 + np.exp(-r * (time - t0))
)

if time < 8:
    phase = "Lag"

elif time < 24:
    phase = "Log"

elif time < 40:
    phase = "Stationary"

else:
    phase = "Death"

# =====================================================
# HEADER
# =====================================================

st.markdown(
    "<div class='title'>🧬 MicrobialAI</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>AI-Assisted Microbial Growth Prediction Platform</div>",
    unsafe_allow_html=True
)

st.write("")

# =====================================================
# TOP METRICS
# =====================================================

m1,m2,m3,m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class='card'>
    <div class='metric-label'>Growth Phase</div>
    <div class='metric'>{phase}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class='card'>
    <div class='metric-label'>Predicted OD600</div>
    <div class='metric'>{round(growth,3)}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class='card'>
    <div class='metric-label'>Growth Rate</div>
    <div class='metric'>{r}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class='card'>
    <div class='metric-label'>Carrying Capacity</div>
    <div class='metric'>{K}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# =====================================================
# GRAPH + SIDE INFO
# =====================================================

left,right = st.columns([3.5,1])

# =====================================================
# GRAPH
# =====================================================

with left:

    t = np.linspace(0,48,500)

    y = K / (
        1 + np.exp(-r * (t - t0))
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=t,
            y=y,
            mode='lines',
            line=dict(
                color='#38bdf8',
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
                size=12,
                color='#22c55e'
            ),
            name='Current'
        )
    )

    fig.update_layout(
        template='plotly_dark',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis_title="Time (hours)",
        yaxis_title="OD600"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# SIDE PANEL
# =====================================================

with right:

    st.markdown("""
    <div class='small-card'>
    <h4>🟣 Lag Phase</h4>
    Adaptation stage
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class='small-card'>
    <h4>🟢 Log Phase</h4>
    Exponential growth
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class='small-card'>
    <h4>🟡 Stationary</h4>
    Nutrient depletion
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class='small-card'>
    <h4>🔴 Death</h4>
    Cell decline
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# INSIGHTS
# =====================================================

st.write("")
st.subheader("Growth Insights")

i1,i2,i3 = st.columns(3)

with i1:
    st.markdown("""
    <div class='small-card'>
    ⚡ Fast exponential growth predicted
    </div>
    """, unsafe_allow_html=True)

with i2:
    st.markdown("""
    <div class='small-card'>
    🧪 Conditions suitable for biomass production
    </div>
    """, unsafe_allow_html=True)

with i3:
    st.markdown("""
    <div class='small-card'>
    📈 Logistic model predicts stable carrying capacity
    </div>
    """, unsafe_allow_html=True)

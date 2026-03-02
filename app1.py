import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="SL Soil Classification Tool")

# -------------------------------
# SIDEBAR INPUTS
# -------------------------------
st.sidebar.header("Input Soil Data")

region = st.sidebar.selectbox(
    "Select Region",
    ["North", "South", "East", "West/Freetown"]
)

LL = st.sidebar.number_input("Liquid Limit (LL)", min_value=0.0, max_value=120.0, value=45.0)
PL = st.sidebar.number_input("Plastic Limit (PL)", min_value=0.0, max_value=120.0, value=25.0)

fines = st.sidebar.number_input("Fines (%)", min_value=0.0, max_value=100.0, value=20.0)
sand = st.sidebar.number_input("Sand (%)", min_value=0.0, max_value=100.0, value=40.0)
gravel = st.sidebar.number_input("Gravel (%)", min_value=0.0, max_value=100.0, value=40.0)

# Compute Plasticity Index
PI = LL - PL if LL and PL else None

# -------------------------------
# USCS CLASSIFICATION FUNCTIONS
# -------------------------------
def classify_uscs_coarse(sand, gravel, fines):
    if sand is None or gravel is None or fines is None:
        return "Undetermined"
    total = sand + gravel
    if total == 0:
        return "Undetermined"
    sand_ratio = sand / total
    gravel_ratio = gravel / total
    if fines < 12:
        if sand_ratio >= 0.5 and gravel_ratio >= 0.5:
            return "GW – Well-graded gravel/sand"
        elif gravel_ratio > sand_ratio:
            return "GP – Poorly-graded gravel"
        else:
            return "SP – Poorly-graded sand"
    else:
        if 12 <= fines <= 50:
            return "GM – Silty gravel"
        elif fines > 50:
            return "GC – Clayey gravel"
    return "Unknown"

def uscs_classification(LL, PI, sand, gravel, fines):
    if fines >= 50:
        # Fine-grained
        A_line = 0.73 * (LL - 20)
        if LL < 50 and PI >= A_line:
            return "CL – Lean Clay"
        elif LL < 50 and PI < A_line:
            return "ML – Silt"
        elif LL >= 50 and PI >= A_line:
            return "CH – Fat Clay"
        elif LL >= 50 and PI < A_line:
            return "MH – Elastic Silt"
    else:
        # Coarse-grained
        return classify_uscs_coarse(sand, gravel, fines)

soil_type = uscs_classification(LL, PI, sand, gravel, fines)

# -------------------------------
# REGIONAL ENGINEERING PREDICTION
# -------------------------------
def regional_prediction(region, soil_type):
    database = {
        "North": {
            # Fine-grained
            "CL – Lean Clay": {"OMC":14, "MDD":1.85, "CBR":8, "k":1e-7},
            "CH – Fat Clay": {"OMC":18, "MDD":1.65, "CBR":3, "k":1e-9},
            "ML – Silt": {"OMC":12, "MDD":1.90, "CBR":10, "k":1e-6},
            "MH – Elastic Silt": {"OMC":16, "MDD":1.70, "CBR":5, "k":1e-8},
            # Coarse-grained
            "GW – Well-graded gravel/sand": {"OMC":12, "MDD":1.95, "CBR":20, "k":1e-5},
            "GP – Poorly-graded gravel": {"OMC":11, "MDD":1.90, "CBR":15, "k":5e-6},
            "SW – Well-graded sand": {"OMC":10, "MDD":1.92, "CBR":18, "k":1e-5},
            "SP – Poorly-graded sand": {"OMC":9, "MDD":1.88, "CBR":12, "k":8e-6},
            "GM – Silty gravel": {"OMC":14, "MDD":1.85, "CBR":10, "k":1e-7},
            "GC – Clayey gravel": {"OMC":16, "MDD":1.80, "CBR":8, "k":1e-8},
        },
        "South": {
            "CL – Lean Clay": {"OMC":16, "MDD":1.80, "CBR":6, "k":1e-8},
            "CH – Fat Clay": {"OMC":20, "MDD":1.60, "CBR":2, "k":1e-10},
            "ML – Silt": {"OMC":13, "MDD":1.88, "CBR":9, "k":1e-6},
            "MH – Elastic Silt": {"OMC":17, "MDD":1.68, "CBR":4, "k":1e-8},
            # Coarse-grained
            "GW – Well-graded gravel/sand": {"OMC":13, "MDD":1.93, "CBR":18, "k":1e-5},
            "GP – Poorly-graded gravel": {"OMC":12, "MDD":1.90, "CBR":14, "k":5e-6},
            "SW – Well-graded sand": {"OMC":11, "MDD":1.90, "CBR":16, "k":1e-5},
            "SP – Poorly-graded sand": {"OMC":10, "MDD":1.87, "CBR":12, "k":8e-6},
            "GM – Silty gravel": {"OMC":15, "MDD":1.83, "CBR":9, "k":1e-7},
            "GC – Clayey gravel": {"OMC":17, "MDD":1.78, "CBR":7, "k":1e-8},
        },
        "East": {
            "CL – Lean Clay": {"OMC":15, "MDD":1.82, "CBR":7, "k":1e-8},
            "CH – Fat Clay": {"OMC":19, "MDD":1.62, "CBR":3, "k":1e-9},
            "ML – Silt": {"OMC":12, "MDD":1.92, "CBR":11, "k":1e-6},
            "MH – Elastic Silt": {"OMC":16, "MDD":1.72, "CBR":5, "k":1e-8},
            # Coarse-grained
            "GW – Well-graded gravel/sand": {"OMC":12, "MDD":1.94, "CBR":19, "k":1e-5},
            "GP – Poorly-graded gravel": {"OMC":11, "MDD":1.89, "CBR":14, "k":5e-6},
            "SW – Well-graded sand": {"OMC":10, "MDD":1.91, "CBR":17, "k":1e-5},
            "SP – Poorly-graded sand": {"OMC":9, "MDD":1.88, "CBR":13, "k":8e-6},
            "GM – Silty gravel": {"OMC":14, "MDD":1.84, "CBR":9, "k":1e-7},
            "GC – Clayey gravel": {"OMC":16, "MDD":1.79, "CBR":7, "k":1e-8},
        },
        "West/Freetown": {
            "CL – Lean Clay": {"OMC":17, "MDD":1.78, "CBR":5, "k":1e-8},
            "CH – Fat Clay": {"OMC":21, "MDD":1.58, "CBR":2, "k":1e-10},
            "ML – Silt": {"OMC":14, "MDD":1.85, "CBR":8, "k":1e-6},
            "MH – Elastic Silt": {"OMC":18, "MDD":1.65, "CBR":4, "k":1e-8},
            # Coarse-grained
            "GW – Well-graded gravel/sand": {"OMC":13, "MDD":1.92, "CBR":17, "k":1e-5},
            "GP – Poorly-graded gravel": {"OMC":12, "MDD":1.88, "CBR":14, "k":5e-6},
            "SW – Well-graded sand": {"OMC":11, "MDD":1.90, "CBR":16, "k":1e-5},
            "SP – Poorly-graded sand": {"OMC":10, "MDD":1.87, "CBR":12, "k":8e-6},
            "GM – Silty gravel": {"OMC":15, "MDD":1.83, "CBR":9, "k":1e-7},
            "GC – Clayey gravel": {"OMC":17, "MDD":1.78, "CBR":7, "k":1e-8},
        }
    }
    return database.get(region, {}).get(soil_type, None)

# -------------------------------
# PLASTICITY CHART
# -------------------------------
def plot_plasticity_chart(LL, PI):
    fig, ax = plt.subplots(figsize=(7,6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    LL_line = np.linspace(20, 100, 200)
    PI_A = 0.73 * (LL_line - 20)

    # Shaded zones
    LL_cl = np.linspace(20, 50, 200)
    PI_cl = 0.73 * (LL_cl - 20)
    ax.fill_between(LL_cl, PI_cl, 60, alpha=0.4, label="CL")
    ax.fill_between(LL_cl, 0, PI_cl, alpha=0.4, label="ML")
    LL_ch = np.linspace(50, 100, 200)
    PI_ch = 0.73 * (LL_ch - 20)
    ax.fill_between(LL_ch, PI_ch, 60, alpha=0.4, label="CH")
    ax.fill_between(LL_ch, 0, PI_ch, alpha=0.4, label="MH")

    # A-line
    ax.plot(LL_line, PI_A, 'k-', label='A-line')

    # Sample point
    ax.plot(LL, PI, 'ro', markersize=8, label='Sample')

    ax.set_xlabel("Liquid Limit (LL)")
    ax.set_ylabel("Plasticity Index (PI)")
    ax.set_title("USCS Plasticity Chart")
    ax.legend(loc="upper left")
    ax.grid(True)
    return fig

# -------------------------------
# OUTPUT
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Computed Parameters")
    st.write(f"Plasticity Index (PI): {PI:.2f}")
    st.success(f"USCS Soil Type: {soil_type}")

    if predicted:
        st.subheader("Predicted Engineering Parameters")
        st.write(f"OMC (%): {predicted['OMC']}")
        st.write(f"MDD (Mg/m³): {predicted['MDD']}")
        st.write(f"CBR (%): {predicted['CBR']}")
        st.write(f"Permeability k (m/s): {predicted['k']:.1e}")

with col2:
    st.subheader("Plasticity Chart")
    if fines >= 50:
        fig = plot_plasticity_chart(LL, PI)
        st.pyplot(fig)
    else:
        st.info("Plasticity chart not shown for coarse-grained soils (sand/gravel).")

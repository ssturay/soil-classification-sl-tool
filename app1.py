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

gravel = st.sidebar.number_input("Gravel (%)", min_value=0.0, max_value=100.0, value=40.0)
sand = st.sidebar.number_input("Sand (%)", min_value=0.0, max_value=100.0, value=40.0)
fines = st.sidebar.number_input("Fines (%)", min_value=0.0, max_value=100.0, value=20.0)

# NEW: SPT input
N = st.sidebar.number_input("SPT N-value (optional)", min_value=0.0, max_value=60.0, value=0.0)

# Compute Plasticity Index
PI = LL - PL if LL and PL else None

# -------------------------------
# USCS CLASSIFICATION FUNCTIONS
# -------------------------------
def classify_uscs_coarse(sand, gravel, fines):
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
        return classify_uscs_coarse(sand, gravel, fines)

soil_type = uscs_classification(LL, PI, sand, gravel, fines)

# -------------------------------
# REGIONAL ENGINEERING DATABASE (UNCHANGED)
# -------------------------------
def regional_prediction(region, soil_type):
    database = {
        "North": {
            "CL – Lean Clay": {"OMC":14, "MDD":1.85, "CBR":8, "k":1e-7},
            "CH – Fat Clay": {"OMC":18, "MDD":1.65, "CBR":3, "k":1e-9},
            "ML – Silt": {"OMC":12, "MDD":1.90, "CBR":10, "k":1e-6},
            "MH – Elastic Silt": {"OMC":16, "MDD":1.70, "CBR":5, "k":1e-8},
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
# EXTENDED ENGINEERING LOGIC
# -------------------------------
def regional_prediction_extended(region, soil_type, N):
    base = regional_prediction(region, soil_type)
    if not base:
        return None

    # Default regional shear strength
    if soil_type.startswith("CL"):
        c, phi = 35, 22
    elif soil_type.startswith("CH"):
        c, phi = 50, 17
    elif soil_type.startswith("ML"):
        c, phi = 15, 28
    elif soil_type.startswith("MH"):
        c, phi = 20, 25
    elif soil_type.startswith(("GW","GP","SW","SP")):
        c, phi = 5, 35
    elif soil_type.startswith(("GM","GC")):
        c, phi = 20, 30
    else:
        c, phi = 10, 25

    # 🔹 Override with SPT if available
    if N > 0:
        if soil_type.startswith(("GW","GP","SW","SP")):
            phi = 27 + 0.3 * N
            c = 0
        elif soil_type.startswith(("GM","GC")):
            phi = 30
            c = 10 + 0.5 * N
        else:
            phi = 20
            c = 5 * N

    # 🔹 Bearing capacity from CBR (regional)
    qa_cbr = 30 * base["CBR"]

    # 🔹 Bearing capacity from SPT
    qa_spt = None
    if N > 0:
        if soil_type.startswith(("GW","GP","SW","SP")):
            qa_spt = 12 * N
        elif soil_type.startswith(("GM","GC")):
            qa_spt = 10 * N
        else:
            qa_spt = 6 * N

    # 🔹 Controlling allowable bearing capacity
    qa_values = [q for q in [qa_cbr, qa_spt] if q is not None]
    qa_final = min(qa_values) if qa_values else qa_cbr

    foundation = "Suitable for shallow foundation" if qa_final > 150 else \
                 "Shallow foundation with improvement" if qa_final > 100 else \
                 "Consider deep foundation"

    return {
        **base,
        "c": round(c,1),
        "phi": round(phi,1),
        "qa_cbr": round(qa_cbr,1),
        "qa_spt": round(qa_spt,1) if qa_spt else None,
        "q_allow": round(qa_final,1),
        "foundation": foundation
    }

predicted_extended = regional_prediction_extended(region, soil_type, N)

# -------------------------------
# DISPLAY OUTPUT (UNCHANGED LAYOUT)
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Computed Parameters")
    st.write(f"Plasticity Index (PI): {PI:.2f}")
    st.success(f"USCS Soil Type: {soil_type}")

    if predicted_extended:
        st.subheader("Predicted Engineering Parameters")
        st.write(f"OMC (%): {predicted_extended['OMC']}")
        st.write(f"MDD (Mg/m³): {predicted_extended['MDD']}")
        st.write(f"CBR (%): {predicted_extended['CBR']}")
        st.write(f"Permeability k (m/s): {predicted_extended['k']:.1e}")
        st.write(f"Cohesion c (kPa): {predicted_extended['c']}")
        st.write(f"Friction angle φ (°): {predicted_extended['phi']}")
        st.write(f"q_allow from CBR (kPa): {predicted_extended['qa_cbr']}")
        if predicted_extended["qa_spt"]:
            st.write(f"q_allow from SPT (kPa): {predicted_extended['qa_spt']}")
        st.write(f"Controlling q_allow (kPa): {predicted_extended['q_allow']}")
        st.write(f"Foundation Recommendation: {predicted_extended['foundation']}")

with col2:
    st.subheader("Plasticity Chart")
    if fines >= 50:
        fig = plot_plasticity_chart(LL, PI)
        st.pyplot(fig)
    else:
        st.info("Plasticity chart not shown for coarse-grained soils (sand/gravel).")

    st.subheader("Grain Size Distribution")
    fig2 = plot_grain_size(gravel, sand, fines)
    st.pyplot(fig2)

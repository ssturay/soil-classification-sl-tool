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

N = st.sidebar.number_input("SPT N-value (optional)", min_value=0.0, value=0.0)

# -------------------------------
# DERIVED PARAMETERS
# -------------------------------
PI = LL - PL if LL and PL else None

# -------------------------------
# GRAIN SIZE DISTRIBUTION CHART
# -------------------------------
def plot_grain_size(gravel, sand, fines):
    fig, ax = plt.subplots(figsize=(7, 5))
    fractions = ["Gravel", "Sand", "Fines"]
    percentages = [gravel, sand, fines]
    ax.bar(fractions, percentages)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Grain Size Distribution")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    return fig

# -------------------------------
# PLASTICITY CHART
# -------------------------------
def plot_plasticity_chart(LL, PI):
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)

    LL_line = np.linspace(20, 100, 200)
    PI_A = 0.73 * (LL_line - 20)

    LL_cl = np.linspace(20, 50, 200)
    PI_cl = 0.73 * (LL_cl - 20)
    ax.fill_between(LL_cl, PI_cl, 60, alpha=0.3, label="CL")
    ax.fill_between(LL_cl, 0, PI_cl, alpha=0.3, label="ML")

    LL_ch = np.linspace(50, 100, 200)
    PI_ch = 0.73 * (LL_ch - 20)
    ax.fill_between(LL_ch, PI_ch, 60, alpha=0.3, label="CH")
    ax.fill_between(LL_ch, 0, PI_ch, alpha=0.3, label="MH")

    ax.plot(LL_line, PI_A, 'k-', label='A-line')

    if PI is not None:
        ax.plot(LL, PI, 'ro', markersize=8, label='Sample')

    ax.set_xlabel("Liquid Limit (LL)")
    ax.set_ylabel("Plasticity Index (PI)")
    ax.set_title("USCS Plasticity Chart")
    ax.legend(loc="upper left")
    ax.grid(True)
    return fig

# -------------------------------
# USCS CLASSIFICATION
# -------------------------------
def classify_uscs_coarse(sand, gravel, fines):
    total = sand + gravel
    if total == 0:
        return "Undetermined"

    sand_ratio = sand / total
    gravel_ratio = gravel / total

    if fines < 12:
        if gravel_ratio > sand_ratio:
            return "GP – Poorly-graded gravel"
        else:
            return "SP – Poorly-graded sand"

    elif 12 <= fines <= 50:
        if gravel_ratio > sand_ratio:
            return "GM – Silty gravel"
        else:
            return "SM – Silty sand"

    else:
        if gravel_ratio > sand_ratio:
            return "GC – Clayey gravel"
        else:
            return "SC – Clayey sand"

def uscs_classification(LL, PI, sand, gravel, fines):
    if fines >= 50 and PI is not None:
        A_line = 0.73 * (LL - 20)

        if LL < 50 and PI >= A_line:
            return "CL – Lean Clay"
        elif LL < 50 and PI < A_line:
            return "ML – Silt"
        elif LL >= 50 and PI >= A_line:
            return "CH – Fat Clay"
        elif LL >= 50 and PI < A_line:
            return "MH – Elastic Silt"

    return classify_uscs_coarse(sand, gravel, fines)

soil_type = uscs_classification(LL, PI, sand, gravel, fines)

# -------------------------------
# REGIONAL DATABASE
# -------------------------------
def regional_prediction(region, soil_type):
    database = {
        "North": {
            "CL – Lean Clay": {"OMC":14, "MDD":1.85, "CBR":8, "k":1e-7},
            "CH – Fat Clay": {"OMC":18, "MDD":1.65, "CBR":3, "k":1e-9},
            "ML – Silt": {"OMC":12, "MDD":1.90, "CBR":10, "k":1e-6},
            "MH – Elastic Silt": {"OMC":16, "MDD":1.70, "CBR":5, "k":1e-8},
            "GP – Poorly-graded gravel": {"OMC":11, "MDD":1.90, "CBR":15, "k":5e-6},
            "SP – Poorly-graded sand": {"OMC":9, "MDD":1.88, "CBR":12, "k":8e-6},
            "GM – Silty gravel": {"OMC":14, "MDD":1.85, "CBR":10, "k":1e-7},
            "GC – Clayey gravel": {"OMC":16, "MDD":1.80, "CBR":8, "k":1e-8},
            "SM – Silty sand": {"OMC":13, "MDD":1.87, "CBR":11, "k":1e-6},
            "SC – Clayey sand": {"OMC":15, "MDD":1.82, "CBR":9, "k":1e-7},
        },
        "West/Freetown": {
            "CL – Lean Clay": {"OMC":17, "MDD":1.78, "CBR":5, "k":1e-8},
            "CH – Fat Clay": {"OMC":21, "MDD":1.58, "CBR":2, "k":1e-10},
            "ML – Silt": {"OMC":14, "MDD":1.85, "CBR":8, "k":1e-6},
            "MH – Elastic Silt": {"OMC":18, "MDD":1.65, "CBR":4, "k":1e-8},
            "GP – Poorly-graded gravel": {"OMC":12, "MDD":1.88, "CBR":14, "k":5e-6},
            "SP – Poorly-graded sand": {"OMC":10, "MDD":1.87, "CBR":12, "k":8e-6},
            "GM – Silty gravel": {"OMC":15, "MDD":1.83, "CBR":9, "k":1e-7},
            "GC – Clayey gravel": {"OMC":17, "MDD":1.78, "CBR":7, "k":1e-8},
            "SM – Silty sand": {"OMC":14, "MDD":1.85, "CBR":10, "k":1e-6},
            "SC – Clayey sand": {"OMC":16, "MDD":1.80, "CBR":8, "k":1e-7},
        }
    }
    return database.get(region, {}).get(soil_type, None)

# -------------------------------
# SHEAR + BEARING CAPACITY
# -------------------------------
def bearing_capacity_from_N(N):
    if N <= 0:
        return None
    return 12 * N  # kPa (empirical for shallow foundations)

def bearing_capacity_from_CBR(CBR):
    if CBR is None:
        return None
    return 2.5 * CBR  # kPa

def regional_prediction_extended(region, soil_type, N):
    base = regional_prediction(region, soil_type)
    if not base:
        return None

    # Shear strength parameters
    if soil_type.startswith("CL"):
        c, phi = 35, 22
    elif soil_type.startswith("CH"):
        c, phi = 50, 17
    elif soil_type.startswith("ML"):
        c, phi = 15, 28
    elif soil_type.startswith("MH"):
        c, phi = 20, 25
    elif soil_type.startswith(("GP", "SP")):
        c, phi = 5, 35
    elif soil_type.startswith(("GM", "SM", "SC", "GC")):
        c, phi = 20, 30
    else:
        c, phi = 10, 25

    q_from_N = bearing_capacity_from_N(N)
    q_from_CBR = bearing_capacity_from_CBR(base["CBR"])

    q_allow = q_from_N if q_from_N else q_from_CBR

    extended = {
        **base,
        "c": c,
        "phi": phi,
        "q_allow": q_allow,
        "q_from_N": q_from_N,
        "q_from_CBR": q_from_CBR
    }

    extended["foundation"] = (
        "Suitable for shallow foundation"
        if q_allow and q_allow > 100
        else "Consider ground improvement or deep foundation"
    )

    return extended

predicted_extended = regional_prediction_extended(region, soil_type, N)

# -------------------------------
# DISPLAY
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Computed Parameters")
    if PI is not None:
        st.write(f"Plasticity Index (PI): {PI:.2f}")
    else:
        st.write("Plasticity Index (PI): Not available")

    st.success(f"USCS Soil Type: {soil_type}")

    if predicted_extended:
        st.subheader("Predicted Engineering Parameters")
        st.write(f"OMC (%): {predicted_extended['OMC']}")
        st.write(f"MDD (Mg/m³): {predicted_extended['MDD']}")
        st.write(f"CBR (%): {predicted_extended['CBR']}")
        st.write(f"Permeability k (m/s): {predicted_extended['k']:.1e}")
        st.write(f"Cohesion c (kPa): {predicted_extended['c']}")
        st.write(f"Friction angle φ (°): {predicted_extended['phi']}")

        st.write("### Allowable Bearing Capacity (kPa)")
        if predicted_extended["q_from_N"]:
            st.write(f"From SPT N-value: {predicted_extended['q_from_N']:.2f}")
        if predicted_extended["q_from_CBR"]:
            st.write(f"From CBR: {predicted_extended['q_from_CBR']:.2f}")

        st.write(f"Adopted q_allow: {predicted_extended['q_allow']:.2f}")
        st.write(f"Foundation Recommendation: {predicted_extended['foundation']}")

with col2:
    st.subheader("Plasticity Chart")
    if fines >= 50 and PI is not None:
        fig = plot_plasticity_chart(LL, PI)
        st.pyplot(fig)
    else:
        st.info("Plasticity chart only for fine-grained soils with PI.")

    st.subheader("Grain Size Distribution")
    fig2 = plot_grain_size(gravel, sand, fines)
    st.pyplot(fig2)

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="wide", page_title="SL Soil Classification Tool")

# -------------------------------
# SIDEBAR INPUTS
# -------------------------------
st.sidebar.header("Input Soil Data")

region = st.sidebar.selectbox(
    "Select Region",
    ["North", "South", "East", "West/Freetown"]
)

LL = st.sidebar.number_input("Liquid Limit (LL)", 0.0, 120.0, 45.0)
PL = st.sidebar.number_input("Plastic Limit (PL)", 0.0, 120.0, 25.0)

gravel = st.sidebar.number_input("Gravel (%)", 0.0, 100.0, 40.0)
sand = st.sidebar.number_input("Sand (%)", 0.0, 100.0, 40.0)
fines = st.sidebar.number_input("Fines (%)", 0.0, 100.0, 20.0)

N = st.sidebar.number_input("SPT N-value (optional)", 0.0, value=0.0)

# NEW: FOUNDATION INPUTS
st.sidebar.header("Foundation Parameters")
B = st.sidebar.number_input("Footing Width B (m)", 0.5, value=1.5)
Df = st.sidebar.number_input("Foundation Depth Df (m)", 0.5, value=1.0)
FS = st.sidebar.selectbox("Factor of Safety", [2.5, 3.0, 3.5])

# -------------------------------
# DERIVED PARAMETERS
# -------------------------------
PI = LL - PL if LL and PL else None

# -------------------------------
# CHART FUNCTIONS
# -------------------------------
def plot_grain_size(gravel, sand, fines):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["Gravel", "Sand", "Fines"], [gravel, sand, fines])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Grain Size Distribution")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    return fig

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
        return "GP – Poorly-graded gravel" if gravel_ratio > sand_ratio else "SP – Poorly-graded sand"
    elif 12 <= fines <= 50:
        return "GM – Silty gravel" if gravel_ratio > sand_ratio else "SM – Silty sand"
    else:
        return "GC – Clayey gravel" if gravel_ratio > sand_ratio else "SC – Clayey sand"

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
# REGIONAL DATABASE (Updated with South and East)
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
        "South": {
            "CL – Lean Clay": {"OMC":16, "MDD":1.80, "CBR":6, "k":1e-8},
            "CH – Fat Clay": {"OMC":20, "MDD":1.60, "CBR":2, "k":1e-10},
            "ML – Silt": {"OMC":13, "MDD":1.88, "CBR":9, "k":1e-6},
            "MH – Elastic Silt": {"OMC":17, "MDD":1.68, "CBR":4, "k":1e-8},
            "GP – Poorly-graded gravel": {"OMC":12, "MDD":1.90, "CBR":14, "k":5e-6},
            "SP – Poorly-graded sand": {"OMC":10, "MDD":1.87, "CBR":12, "k":8e-6},
            "GM – Silty gravel": {"OMC":15, "MDD":1.83, "CBR":9, "k":1e-7},
            "GC – Clayey gravel": {"OMC":17, "MDD":1.78, "CBR":7, "k":1e-8},
            "SM – Silty sand": {"OMC":14, "MDD":1.85, "CBR":10, "k":1e-6},
            "SC – Clayey sand": {"OMC":16, "MDD":1.80, "CBR":8, "k":1e-7},
        },
        "East": {
            "CL – Lean Clay": {"OMC":15, "MDD":1.82, "CBR":7, "k":1e-8},
            "CH – Fat Clay": {"OMC":19, "MDD":1.62, "CBR":3, "k":1e-9},
            "ML – Silt": {"OMC":12, "MDD":1.92, "CBR":11, "k":1e-6},
            "MH – Elastic Silt": {"OMC":16, "MDD":1.72, "CBR":5, "k":1e-8},
            "GP – Poorly-graded gravel": {"OMC":11, "MDD":1.89, "CBR":14, "k":5e-6},
            "SP – Poorly-graded sand": {"OMC":9, "MDD":1.88, "CBR":13, "k":8e-6},
            "GM – Silty gravel": {"OMC":14, "MDD":1.84, "CBR":9, "k":1e-7},
            "GC – Clayey gravel": {"OMC":16, "MDD":1.79, "CBR":7, "k":1e-8},
            "SM – Silty sand": {"OMC":13, "MDD":1.86, "CBR":10, "k":1e-6},
            "SC – Clayey sand": {"OMC":15, "MDD":1.81, "CBR":8, "k":1e-7},
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
# SHEAR PARAMETERS
# -------------------------------
def shear_parameters(soil_type):
    if soil_type.startswith("CL"): return 35, 22
    if soil_type.startswith("CH"): return 50, 17
    if soil_type.startswith("ML"): return 15, 28
    if soil_type.startswith("MH"): return 20, 25
    if soil_type.startswith(("GP", "SP")): return 5, 35
    if soil_type.startswith(("GM", "SM", "SC", "GC")): return 20, 30
    return 10, 25

# -------------------------------
# BEARING CAPACITY FUNCTIONS
# -------------------------------
def bearing_capacity_from_N(N):
    return 12 * N if N > 0 else None

def bearing_capacity_from_CBR(CBR):
    return 2.5 * CBR if CBR else None

def terzaghi_bearing_capacity(c, phi, gamma, B, Df, FS):
    phi_rad = math.radians(phi)

    Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.radians(45 + phi/2)) ** 2)
    Nc = (Nq - 1) / math.tan(phi_rad) if phi > 0 else 5.7
    Ngamma = 2 * (Nq + 1) * math.tan(phi_rad)

    q = gamma * Df
    qult = c * Nc + q * Nq + 0.5 * gamma * B * Ngamma
    qall = qult / FS

    return qult, qall

def settlement_from_spt(N, B):
    return (25 * B) / N if N > 0 else None

# -------------------------------
# COMPUTE RESULTS
# -------------------------------
predicted = regional_prediction(region, soil_type)

if predicted:
    c, phi = shear_parameters(soil_type)
    gamma = predicted["MDD"] * 9.81

    qult, qall_terzaghi = terzaghi_bearing_capacity(c, phi, gamma, B, Df, FS)

    q_N = bearing_capacity_from_N(N)
    q_CBR = bearing_capacity_from_CBR(predicted["CBR"])

    if qall_terzaghi:
        q_allow = qall_terzaghi
        method = "Terzaghi (c-φ)"
    elif q_N:
        q_allow = q_N
        method = "SPT correlation"
    else:
        q_allow = q_CBR
        method = "CBR correlation"

    settlement = settlement_from_spt(N, B)

# -------------------------------
# DISPLAY
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Computed Parameters")
    st.write(f"Plasticity Index (PI): {PI:.2f}" if PI is not None else "PI not available")
    st.success(f"USCS Soil Type: {soil_type}")

    if predicted:
        st.subheader("Engineering Parameters")
        st.write(f"OMC (%): {predicted['OMC']}")
        st.write(f"MDD (Mg/m³): {predicted['MDD']}")
        st.write(f"CBR (%): {predicted['CBR']}")
        st.write(f"Permeability k (m/s): {predicted['k']:.1e}")
        st.write(f"Cohesion c (kPa): {c}")
        st.write(f"Friction angle φ (°): {phi}")
        st.write(f"Unit weight γ (kN/m³): {gamma:.2f}")

        st.subheader("Bearing Capacity")
        st.write(f"Terzaghi q_ult (kPa): {qult:.2f}")
        st.write(f"Terzaghi q_allow (kPa): {qall_terzaghi:.2f}")
        if q_N:
            st.write(f"From SPT N-value (kPa): {q_N:.2f}")
        if q_CBR:
            st.write(f"From CBR (kPa): {q_CBR:.2f}")
        st.success(f"Adopted q_allow ({method}): {q_allow:.2f}")

        st.subheader("Estimated Settlement")
        if settlement:
            st.write(f"Settlement ≈ {settlement:.2f} mm")
        else:
            st.write("Settlement requires SPT N-value")

with col2:
    st.subheader("Plasticity Chart")
    if fines >= 50 and PI is not None:
        st.pyplot(plot_plasticity_chart(LL, PI))
    else:
        st.info("Plasticity chart only for fine-grained soils with PI.")

    st.subheader("Grain Size Distribution")
    st.pyplot(plot_grain_size(gravel, sand, fines))

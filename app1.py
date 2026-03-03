import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="wide", page_title="SL Regional Soil Classification Tool 🇸🇱")

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

# -------------------------------
# Soil Composition: Autofill Fines
# -------------------------------
st.sidebar.write("**Soil Composition (%)** (Total = 100%)")

gravel = st.sidebar.number_input("Gravel (%)", 0.0, 100.0, 40.0)
max_sand = max(0.0, 100.0 - gravel)
sand = st.sidebar.number_input("Sand (%)", 0.0, max_sand, 40.0)
fines = 100.0 - (gravel + sand)
st.sidebar.text(f"Fines (%) auto-calculated: {fines:.2f}")

N = st.sidebar.number_input("SPT N-value (optional)", 0.0, value=0.0)
CBR_input = st.sidebar.number_input("CBR (%) optional", 0.0, value=0.0)

# -------------------------------
# FOUNDATION INPUTS
# -------------------------------
st.sidebar.header("Foundation Parameters")
B = st.sidebar.number_input("Footing Width B (m)", 0.5, value=1.5)
Df = st.sidebar.number_input("Foundation Depth Df (m)", 0.5, value=1.0)
FS = st.sidebar.selectbox("Factor of Safety", [2.5, 3.0, 3.5])
water_table = st.sidebar.checkbox("Groundwater within foundation depth?")

# -------------------------------
# DERIVED PARAMETERS
# -------------------------------
PI = LL - PL if LL and PL else None

# -------------------------------
# CHART FUNCTIONS
# -------------------------------
def plot_grain_size(gravel, sand, fines):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["Gravel", "Sand", "Fines"], [gravel, sand, fines], color=['#a0522d','#f4a460','#deb887'])
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
    ax.plot(LL_line, PI_A, 'k-', label='A-line', linewidth=1.5)

    # Shaded USCS regions
    # CL – Lean Clay
    LL_CL = np.linspace(20, 50, 200)
    PI_CL = 0.73*(LL_CL - 20)
    ax.fill_between(LL_CL, PI_CL, 60, color='#ff9999', alpha=0.5, label="CL – Lean Clay")
    # ML – Silt
    ax.fill_between(LL_CL, 0, PI_CL, color='#99ccff', alpha=0.5, label="ML – Silt")
    # CH – Fat Clay
    LL_CH = np.linspace(50, 100, 200)
    PI_CH = 0.73*(LL_CH - 20)
    ax.fill_between(LL_CH, PI_CH, 60, color='#ff6666', alpha=0.5, label="CH – Fat Clay")
    # MH – Elastic Silt
    ax.fill_between(LL_CH, 0, PI_CH, color='#6699ff', alpha=0.5, label="MH – Elastic Silt")

    if PI is not None:
        ax.plot(LL, PI, 'ro', markersize=8, label='Sample')

    ax.set_xlabel("Liquid Limit (LL)")
    ax.set_ylabel("Plasticity Index (PI)")
    ax.set_title("USCS Plasticity Chart")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True)
    return fig

# -------------------------------
# USCS CLASSIFICATION
# -------------------------------
def classify_uscs_coarse(sand, gravel, fines, LL, PI):
    total = sand + gravel
    if total == 0:
        return "Undetermined"
    primary = "G" if gravel > sand else "S"
    if PI is not None:
        A_line = 0.73 * (LL - 20)
        fines_symbol = "C" if PI >= A_line else "M"
    else:
        fines_symbol = "M"
    if fines < 5:
        return "GW – Well-graded gravel" if primary == "G" else "SW – Well-graded sand"
    elif 5 <= fines <= 12:
        return f"{primary}W-{primary}{fines_symbol}"
    else:
        if primary == "G":
            return f"G{fines_symbol} – {'Clayey gravel' if fines_symbol=='C' else 'Silty gravel'}"
        else:
            return f"S{fines_symbol} – {'Clayey sand' if fines_symbol=='C' else 'Silty sand'}"

def uscs_classification(LL, PI, sand, gravel, fines):
    if fines >= 50 and PI is not None:
        A_line = 0.73 * (LL - 20)
        if LL < 50 and PI >= A_line:
            return "CL – Lean Clay"
        elif LL < 50 and PI < A_line:
            return "ML – Silt"
        elif LL >= 50 and PI >= A_line:
            return "CH – Fat Clay"
        else:
            return "MH – Elastic Silt"
    return classify_uscs_coarse(sand, gravel, fines, LL, PI)

soil_type = uscs_classification(LL, PI, sand, gravel, fines)

# -------------------------------
# DATABASE LOOKUP FIX
# -------------------------------
lookup_key = soil_type
if " – " in lookup_key:
    lookup_key = lookup_key.split(" – ")[0]
if "-" in lookup_key:
    parts = lookup_key.split("-")
    lookup_key = parts[1] if fines > 12 else parts[0]
symbol_map = {
    "GW": "GW – Well-graded gravel",
    "SW": "SW – Well-graded sand",
    "GP": "GP – Poorly-graded gravel",
    "SP": "SP – Poorly-graded sand",
    "GM": "GM – Silty gravel",
    "GC": "GC – Clayey gravel",
    "SM": "SM – Silty sand",
    "SC": "SC – Clayey sand",
}
if lookup_key in symbol_map:
    lookup_key = symbol_map[lookup_key]

# -------------------------------
# AASHTO CLASSIFICATION
# -------------------------------
def classify_aashto(fines, LL, PI):
    if fines < 35:
        return "A-1"
    elif LL < 40 and PI < 10:
        return "A-2-4"
    elif LL < 40:
        return "A-2-6"
    elif PI <= 10:
        return "A-4"
    else:
        return "A-7"

aashto_type = classify_aashto(fines, LL, PI)

# -------------------------------
# REGIONAL DATABASE (FULL)
# -------------------------------
def regional_prediction(region, soil_type):
    database = {
        "North": {
            "CL – Lean Clay": {"OMC":14, "MDD":1.85, "CBR":8, "k":1e-7},
            "CH – Fat Clay": {"OMC":18, "MDD":1.65, "CBR":3, "k":1e-9},
            "ML – Silt": {"OMC":12, "MDD":1.90, "CBR":10, "k":1e-6},
            "MH – Elastic Silt": {"OMC":16, "MDD":1.70, "CBR":5, "k":1e-8},
            "GW – Well-graded gravel": {"OMC":11, "MDD":1.90, "CBR":18, "k":5e-6},
            "SW – Well-graded sand": {"OMC":10, "MDD":1.88, "CBR":16, "k":6e-6},
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
            "GW – Well-graded gravel": {"OMC":12, "MDD":1.90, "CBR":16, "k":5e-6},
            "SW – Well-graded sand": {"OMC":11, "MDD":1.87, "CBR":14, "k":6e-6},
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
            "GW – Well-graded gravel": {"OMC":11, "MDD":1.89, "CBR":17, "k":5e-6},
            "SW – Well-graded sand": {"OMC":10, "MDD":1.88, "CBR":15, "k":6e-6},
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
            "GW – Well-graded gravel": {"OMC":12, "MDD":1.88, "CBR":16, "k":5e-6},
            "SW – Well-graded sand": {"OMC":11, "MDD":1.87, "CBR":14, "k":6e-6},
            "GP – Poorly-graded gravel": {"OMC":12, "MDD":1.88, "CBR":14, "k":5e-6},
            "SP – Poorly-graded sand": {"OMC":10, "MDD":1.87, "CBR":12, "k":8e-6},
            "GM – Silty gravel": {"OMC":15, "MDD":1.83, "CBR":9, "k":1e-7},
            "GC – Clayey gravel": {"OMC":17, "MDD":1.78, "CBR":7, "k":1e-8},
            "SM – Silty sand": {"OMC":14, "MDD":1.85, "CBR":10, "k":1e-6},
            "SC – Clayey sand": {"OMC":16, "MDD":1.80, "CBR":8, "k":1e-7},
        }
    }
    return database.get(region, {}).get(soil_type, None)

predicted = regional_prediction(region, lookup_key)

# -------------------------------
# DISPLAY RESULTS
# -------------------------------
st.title("SL Regional Soil Classification Tool 🇸🇱")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Classification")
    st.write("USCS:", soil_type)
    st.write("AASHTO:", aashto_type)
    st.pyplot(plot_grain_size(gravel, sand, fines))
    if PI is not None:
        st.pyplot(plot_plasticity_chart(LL, PI))

with col2:
    st.subheader("Regional Engineering Parameters")
    if predicted:
        OMC = predicted["OMC"]
        MDD = predicted["MDD"]
        CBR_db = predicted["CBR"]
        k = predicted["k"]

        st.write("OMC (%):", OMC)
        st.write("MDD (Mg/m³):", MDD)
        st.write("CBR (Database %):", CBR_db)
        st.write("Permeability k (m/s):", k)

        # Shear strength
        if soil_type.startswith(("CL","CH")):
            c, phi = 25, 22
        elif soil_type.startswith(("ML","MH")):
            c, phi = 10, 25
        else:
            c, phi = 5, 30
        gamma = MDD * 9.81
        st.write("Cohesion c (kPa):", c)
        st.write("Friction angle φ (°):", phi)
        st.write("Unit weight γ (kN/m³):", gamma)

        # Terzaghi bearing capacity
        phi_rad = math.radians(phi)
        Nq = math.exp(np.pi * math.tan(phi_rad)) * (np.tan(math.radians(45 + phi/2)))**2
        Nc = (Nq - 1)/math.tan(phi_rad) if phi!=0 else 5.7
        Ngamma = 2*(Nq + 1)*math.tan(phi_rad)
        gamma_eff = gamma - 9.81 if water_table else gamma
        qult = c*Nc + gamma_eff*Df*Nq + 0.5*gamma_eff*B*Ngamma
        qall_terzaghi = qult / FS
        st.write("Terzaghi Ultimate q_ult (kPa):", round(qult,2))
        st.write("Terzaghi Allowable q_allow (kPa):", round(qall_terzaghi,2))

        if N>0:
            q_spt = 12*N
            st.write("Allowable from SPT (kPa):", round(q_spt,2))
        if CBR_input>0:
            q_cbr = 30*CBR_input
            st.write("Allowable from CBR (kPa):", round(q_cbr,2))
    else:
        st.warning("No regional parameters found.")

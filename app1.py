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

# -------------------------------
# FOUNDATION INPUTS
# -------------------------------
st.sidebar.header("Foundation Parameters")
B = st.sidebar.number_input("Footing Width B (m)", 0.5, value=1.5)
Df = st.sidebar.number_input("Foundation Depth Df (m)", 0.5, value=1.0)
FS = st.sidebar.selectbox("Factor of Safety", [2.5, 3.0, 3.5])

# -------------------------------
# DERIVED PARAMETERS
# -------------------------------
PI = LL - PL if LL and PL else None

# -------------------------------
# USCS CLASSIFICATION (FULL LOGIC)
# -------------------------------
def uscs_classification(LL, PI, sand, gravel, fines):

    total_coarse = sand + gravel

    if PI is None:
        return "Insufficient data"

    # Determine if coarse or fine grained
    if fines >= 50:
        # Fine-grained soil
        A_line = 0.73 * (LL - 20)

        if LL < 50:
            if PI >= A_line:
                base = "CL – Lean Clay"
            else:
                base = "ML – Silt"
        else:
            if PI >= A_line:
                base = "CH – Fat Clay"
            else:
                base = "MH – Elastic Silt"

        # If coarse fraction is significant (>30%), indicate sandy/clayey mix
        if total_coarse > 30:
            if sand > gravel:
                return "SC – Clayey Sand (Fines-dominated)"
            else:
                return "GC – Clayey Gravel (Fines-dominated)"

        return base

    else:
        # Coarse-grained soil
        if total_coarse == 0:
            return "Undetermined"

        sand_ratio = sand / total_coarse
        gravel_ratio = gravel / total_coarse

        dominant = "sand" if sand_ratio >= gravel_ratio else "gravel"

        A_line = 0.73 * (LL - 20)

        if fines < 12:
            if dominant == "sand":
                return "SP – Poorly-graded Sand"
            else:
                return "GP – Poorly-graded Gravel"

        else:
            # Use plasticity of fines
            if PI >= A_line:
                if dominant == "sand":
                    return "SC – Clayey Sand"
                else:
                    return "GC – Clayey Gravel"
            else:
                if dominant == "sand":
                    return "SM – Silty Sand"
                else:
                    return "GM – Silty Gravel"

soil_type = uscs_classification(LL, PI, sand, gravel, fines)

# -------------------------------
# REGIONAL DATABASE (UNCHANGED)
# -------------------------------
def regional_prediction(region, soil_type):
    database = {
        "North": {
            "CL – Lean Clay": {"OMC":14,"MDD":1.85,"CBR":8,"k":1e-7},
            "CH – Fat Clay": {"OMC":18,"MDD":1.65,"CBR":3,"k":1e-9},
            "ML – Silt": {"OMC":12,"MDD":1.90,"CBR":10,"k":1e-6},
            "MH – Elastic Silt": {"OMC":16,"MDD":1.70,"CBR":5,"k":1e-8},
            "SP – Poorly-graded Sand": {"OMC":9,"MDD":1.88,"CBR":12,"k":8e-6},
            "GP – Poorly-graded Gravel": {"OMC":11,"MDD":1.90,"CBR":15,"k":5e-6},
            "SM – Silty Sand": {"OMC":13,"MDD":1.87,"CBR":11,"k":1e-6},
            "SC – Clayey Sand": {"OMC":15,"MDD":1.82,"CBR":9,"k":1e-7},
            "GM – Silty Gravel": {"OMC":14,"MDD":1.85,"CBR":10,"k":1e-7},
            "GC – Clayey Gravel": {"OMC":16,"MDD":1.80,"CBR":8,"k":1e-8},
        },
        "South": {},
        "East": {},
        "West/Freetown": {}
    }
    return database.get(region, {}).get(soil_type, None)

# -------------------------------
# DISPLAY
# -------------------------------
st.subheader("Computed Parameters")
st.write(f"Plasticity Index (PI): {PI:.2f}" if PI is not None else "PI not available")
st.success(f"USCS Soil Type: {soil_type}")

st.subheader("Grain Size Distribution")
fig, ax = plt.subplots()
ax.bar(["Gravel","Sand","Fines"], [gravel,sand,fines])
ax.set_ylim(0,100)
st.pyplot(fig)

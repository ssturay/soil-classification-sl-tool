import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🇸🇱 Sierra Leone Regional Soil Classification Platform")

# ==========================================================
# 1️⃣ REGIONAL DATABASE (ALL REGIONS INCLUDED)
# ==========================================================

REGIONAL_DATABASE = {

    "North": {
        "GW": {"gamma": 20, "phi": 40, "c": 0, "CBR": 40},
        "GP": {"gamma": 19, "phi": 38, "c": 0, "CBR": 35},
        "SW": {"gamma": 19, "phi": 36, "c": 0, "CBR": 30},
        "SP": {"gamma": 18, "phi": 34, "c": 0, "CBR": 25},
        "SM": {"gamma": 18, "phi": 32, "c": 5, "CBR": 15},
        "SC": {"gamma": 19, "phi": 30, "c": 10, "CBR": 12},
        "CL": {"gamma": 18, "phi": 22, "c": 25, "CBR": 6},
        "CH": {"gamma": 17, "phi": 18, "c": 40, "CBR": 3},
        "ML": {"gamma": 17, "phi": 26, "c": 8, "CBR": 8},
        "MH": {"gamma": 16, "phi": 20, "c": 15, "CBR": 4},
    },

    "South": {
        "GW": {"gamma": 21, "phi": 41, "c": 0, "CBR": 45},
        "GP": {"gamma": 20, "phi": 39, "c": 0, "CBR": 38},
        "SW": {"gamma": 20, "phi": 37, "c": 0, "CBR": 32},
        "SP": {"gamma": 19, "phi": 35, "c": 0, "CBR": 28},
        "SM": {"gamma": 18, "phi": 31, "c": 6, "CBR": 18},
        "SC": {"gamma": 19, "phi": 29, "c": 12, "CBR": 14},
        "CL": {"gamma": 18, "phi": 23, "c": 28, "CBR": 7},
        "CH": {"gamma": 17, "phi": 19, "c": 42, "CBR": 4},
        "ML": {"gamma": 17, "phi": 27, "c": 9, "CBR": 9},
        "MH": {"gamma": 16, "phi": 21, "c": 18, "CBR": 5},
    },

    "East": {
        "GW": {"gamma": 20, "phi": 39, "c": 0, "CBR": 42},
        "GP": {"gamma": 19, "phi": 37, "c": 0, "CBR": 36},
        "SW": {"gamma": 19, "phi": 35, "c": 0, "CBR": 29},
        "SP": {"gamma": 18, "phi": 33, "c": 0, "CBR": 24},
        "SM": {"gamma": 18, "phi": 30, "c": 7, "CBR": 16},
        "SC": {"gamma": 19, "phi": 28, "c": 11, "CBR": 13},
        "CL": {"gamma": 18, "phi": 24, "c": 30, "CBR": 8},
        "CH": {"gamma": 17, "phi": 20, "c": 45, "CBR": 4},
        "ML": {"gamma": 17, "phi": 25, "c": 10, "CBR": 8},
        "MH": {"gamma": 16, "phi": 22, "c": 20, "CBR": 5},
    },

    "West": {
        "GW": {"gamma": 21, "phi": 42, "c": 0, "CBR": 48},
        "GP": {"gamma": 20, "phi": 40, "c": 0, "CBR": 40},
        "SW": {"gamma": 20, "phi": 38, "c": 0, "CBR": 35},
        "SP": {"gamma": 19, "phi": 36, "c": 0, "CBR": 30},
        "SM": {"gamma": 18, "phi": 33, "c": 6, "CBR": 20},
        "SC": {"gamma": 19, "phi": 31, "c": 12, "CBR": 16},
        "CL": {"gamma": 18, "phi": 25, "c": 30, "CBR": 8},
        "CH": {"gamma": 17, "phi": 20, "c": 45, "CBR": 4},
        "ML": {"gamma": 17, "phi": 27, "c": 10, "CBR": 9},
        "MH": {"gamma": 16, "phi": 22, "c": 18, "CBR": 5},
    }
}

# ==========================================================
# 2️⃣ INPUT SECTION
# ==========================================================

region = st.selectbox("Select Region", ["North", "South", "East", "West"])

col1, col2 = st.columns(2)

with col1:
    sand = st.number_input("Sand (%)", 0.0, 100.0, 40.0)
    gravel_max = 100.0 - sand
    gravel = st.number_input("Gravel (%)", 0.0, gravel_max, 30.0)

with col2:
    fines = 100 - (sand + gravel)
    st.number_input("Fines (%)", value=fines, disabled=True)

LL = st.number_input("Liquid Limit (LL)", 0.0, 150.0, 40.0)
PI = st.number_input("Plasticity Index (PI)", 0.0, 100.0, 15.0)
N = st.number_input("SPT N-value (optional)", 0.0, 100.0, 0.0)
CBR_input = st.number_input("CBR % (optional)", 0.0, 100.0, 0.0)
water_table = st.checkbox("Groundwater within foundation depth?")

# ==========================================================
# 3️⃣ USCS CLASSIFICATION
# ==========================================================

def classify_uscs(gravel, sand, fines, LL, PI):
    if fines < 5:
        if gravel > sand:
            return "GW" if PI < 4 else "GP"
        else:
            return "SW" if PI < 4 else "SP"
    elif fines > 12:
        if LL < 50:
            return "CL" if PI > 7 else "ML"
        else:
            return "CH" if PI > 7 else "MH"
    else:
        return "SM"

uscs = classify_uscs(gravel, sand, fines, LL, PI)
st.subheader(f"USCS Classification: {uscs}")

# ==========================================================
# 4️⃣ AASHTO CLASSIFICATION
# ==========================================================

def classify_aashto(fines, LL, PI):
    if fines < 35:
        return "A-1"
    elif LL < 40 and PI < 10:
        return "A-2-4"
    elif LL < 40 and PI >= 10:
        return "A-2-6"
    elif LL >= 40 and PI <= 10:
        return "A-4"
    else:
        return "A-7"

aashto = classify_aashto(fines, LL, PI)
st.subheader(f"AASHTO Classification: {aashto}")

# ==========================================================
# 5️⃣ ENGINEERING PARAMETERS
# ==========================================================

params = REGIONAL_DATABASE[region][uscs]
gamma = params["gamma"]
phi = params["phi"]
c = params["c"]
CBR_default = params["CBR"]

st.write("### Predicted Engineering Parameters")
st.write(f"Unit Weight γ = {gamma} kN/m³")
st.write(f"Friction Angle φ = {phi}°")
st.write(f"Cohesion c = {c} kPa")

# ==========================================================
# 6️⃣ BEARING CAPACITY
# ==========================================================

def bearing_from_spt(N):
    return 12 * N

def bearing_from_cbr(CBR):
    return 10 * CBR

qa_spt = bearing_from_spt(N) if N > 0 else None
qa_cbr = bearing_from_cbr(CBR_input if CBR_input > 0 else CBR_default)

if qa_spt:
    st.write(f"Allowable Bearing Capacity (SPT) = {qa_spt:.2f} kPa")

if qa_cbr:
    st.write(f"Allowable Bearing Capacity (CBR) = {qa_cbr:.2f} kPa")

qa = qa_spt if qa_spt else qa_cbr

if qa:
    gamma_eff = gamma - 9.81 if water_table else gamma
    if water_table:
        st.write("Groundwater correction applied.")

    net_qa = qa - gamma_eff
    st.write(f"Net Allowable Bearing Capacity = {net_qa:.2f} kPa")

# ==========================================================
# 7️⃣ PLASTICITY CHART
# ==========================================================

def plot_plasticity(LL, PI):
    fig, ax = plt.subplots()
    LL_line = np.linspace(0,100,100)
    A_line = 0.73*(LL_line-20)
    ax.plot(LL_line, A_line)
    ax.scatter(LL, PI)
    ax.set_xlabel("LL")
    ax.set_ylabel("PI")
    return fig

st.pyplot(plot_plasticity(LL, PI))

# ==========================================================
# 8️⃣ GRAIN SIZE TRIANGLE
# ==========================================================

def plot_grain(gravel, sand, fines):
    fig, ax = plt.subplots()
    ax.bar(["Gravel","Sand","Fines"],[gravel,sand,fines])
    return fig

st.pyplot(plot_grain(gravel, sand, fines))

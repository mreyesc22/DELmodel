import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io
import numpy as np
import os
import datetime

def save_feedback(tab_name, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_line = f"{timestamp} | {tab_name} | {message}\n"
    
    with open("stakeholder_feedback.txt", "a") as f:
        f.write(feedback_line)

# --- Add Reference Image ---
# Replace 'Location.png' with the path to your image file.
# st.image("Location.png", caption="Reference: Dashboard Explanation", use_container_width=True)

# --- Load the .mat file ---
mat_file = 'result_analytisch_dynamisch_evenwicht_newA125.mat'
mat_data = scipy.io.loadmat(mat_file)
# Extract the 'result' variable
result_data = mat_data['result']

# Initialize a list to hold each row of the dataframe
records = []

# Loop through each salinity scenario
for iVD in range(result_data.shape[1]):
    entry = result_data[0, iVD]
    inlaat = entry['inlaat']
    spui = entry['spui']
    S_VD = entry['S_VD']
    put = entry['put']
    fac5 = entry['fac5']  # New parameter: flushing efficiency

    # Go through each combination of inlaat and spui (and fac5)
    for i in range(inlaat.shape[0]):
        for j in range(inlaat.shape[1]):
            records.append({
                'Inlet Volume': inlaat[i, j],
                'Ebb Volume': spui[i, j],
                'Salinity Level': S_VD[i, j],
                'Location Code': int(put[i, j]),
                'fac5': fac5[i, j]
            })

# Convert to DataFrame
data = pd.DataFrame(records)

# Map location codes to names
location_mapping = {1: 'A', 2: 'D', 3: 'F1', 4: 'F2', 5: 'NO'}
data['Location'] = data['Location Code'].map(location_mapping)

# Filter out invalid or unknown locations (optional)
data = data[data['Location'] != 'NO']

# Map location to distance (used in Tab 2 and Tab 3 scatter plots)
location_distances = {'A': 2.1, 'D': 5.9, 'F1': 8.8, 'F2': 11.70}
data['Distance (km)'] = data['Location'].map(location_distances)

# Define the color mapping for locations
colors = {'A': 'blueviolet', 'D': 'blue', 'F1': 'orangered', 'F2': 'gold'}

tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "Testing-Dashboard", 
    "Project Overview", 
    "Inlet Volume vs Distance", 
    "Strategy Comparison", 
    "Uncertainty Analysis"
])

with tab0:
    st.header("Testig-Dashoboard")

    st.markdown("""
    This dashboard is currently in a testing phase. The goal of this version is to:

    - Verify the correct functioning of the interactive components.
    - Evaluate the clarity and usefulness of visualizations.
    - Collect feedback from potential users on usability and data presentation.
    - Ensure proper integration of the underlying analytical model and input data.

    Please explore the tabs and functionalities, and feel free to share any suggestions for improvement.

    """)

# -------------------------
# Tab 1: Proyect Overview
# -------------------------
with tab1:
    st.header("Project Overview: Saltwater Management in the Haringvliet Estuary")

    st.markdown("""
    This dashboard supports the analysis of **saltwater intrusion and flushing strategies** 
    in the **Haringvliet estuary**, based on an **analytical model** developed from 
    3D simulation outputs and expert consultation.

    ### 📌 Objective
    To visualize and compare dynamic equilibrium locations, flushing efficiencies, and uncertainties 
    under different management strategies.

    ### 🔍 Key Protocol Variables:
    - **Salinity Level (mg/L):** Salinity levels seawards of the floodgates. 
    - **Ebb Volume (Mm³ per tidal cycle):** Volume of freshwater that can be released from the estuary to the sea during ebb tide. It helps flush saltwater out of the system.
    - **Inlet Volume (Mm³ per tidal cycle):** Volume of saltwater that is allowed to enter the estuary through the floodgates during a tidal cycle.(when the gates are open).
    - **Location:** Represents where the dynamic equilibrium occurs, typically in one of the bottom depressions (A, D, F1, or F2).
    - **Flushing Efficiency (fac5):** A performance indicator that reflects how effectively saltwater is flushed from the system.
    """)

    ### 📊 Protocol Structure
    st.image("Keywords.png", caption="Figure: Key Protocol Variables and Their Interactions", use_container_width=True)

    st.markdown("""
    ### 📍 Model Basis

    Use the tabs above to explore:
    - Location of equilibrium zones (Tab 1, 2)
    - Strategy comparisons (Tab 3)
    - Uncertainty quantification and recommendations (Tab 4)
    """)

    with st.form(key="feedback"):
        st.markdown("### 💬 Stakeholder Feedback")
        feedback = st.text_area("All the information :", "")
        submitted = st.form_submit_button("Submit Feedback")
        if submitted and feedback:
            save_feedback("Testing-Dashboard", feedback)
            st.success("✅ Feedback submitted. Thank you!")
# -------------------------
# Tab 3: Strategy Comparison
# -------------------------
with tab3:
    st.header("Strategy Comparison")
    
    # Create two columns for two independent strategy selections
    col1, col2 = st.columns(2)
    
    # --- Strategy 1 ---
    with col1:
        st.subheader("Strategy 1")
        sal_1 = st.selectbox("Select Salinity Level (mg/L) for Strategy 1", 
                             sorted(data['Salinity Level'].unique()), key="tab3_sal_1")
        data_1 = data[data['Salinity Level'] == sal_1]
        ebb_1_options = sorted(data_1['Ebb Volume'].unique())
        ebb_1 = st.selectbox("Select Ebb Volume (Mm³ per tydal cycle) for Strategy A", ebb_1_options, key="tab3_ebb_A")
        data_1 = data_1[data_1['Ebb Volume'] == ebb_1]
        inlet_1_options = sorted(data_1['Inlet Volume'].unique())
        inlet_1 = st.multiselect("Select Inlet Volumes (Mm³ per tydal cycle) for Strategy 1", inlet_1_options, 
                                 default=inlet_1_options, key="tab3_inlet_1")
        data_1 = data_1[data_1['Inlet Volume'].isin(inlet_1)]
        
        st.write("**Strategy 1 – Data Preview:**")
        st.dataframe(data_1)
            
    # --- Strategy 2 ---
    with col2:
        st.subheader("Strategy 2")
        sal_2 = st.selectbox("Select Salinity Level (mg/L) for Strategy 2", 
                             sorted(data['Salinity Level'].unique()), key="tab3_sal_2")
        data_2 = data[data['Salinity Level'] == sal_2]
        ebb_2_options = sorted(data_2['Ebb Volume'].unique())
        ebb_2 = st.selectbox("Select Ebb Volume (Mm³ per tydal cycle) for Strategy 2", ebb_2_options, key="tab3_ebb_2")
        data_2 = data_2[data_2['Ebb Volume'] == ebb_2]
        inlet_2_options = sorted(data_2['Inlet Volume'].unique())
        inlet_2 = st.multiselect("Select Inlet Volumes (Mm³ per tydal cycle) for Strategy B", inlet_2_options, 
                                 default=inlet_2_options, key="tab3_inlet_2")
        data_2 = data_2[data_2['Inlet Volume'].isin(inlet_2)]
        
        st.write("**Strategy 2 – Data Preview:**")
        st.dataframe(data_2)
        
    # --- Combined Strategy Plot ---
    st.subheader("Strategy 1 vs Strategy 2 (Distance vs Inlet Volume)")

    fig_combined, ax_combined = plt.subplots(figsize=(8, 5))

    # Plot for Strategy 1
    for loc in data_1['Location'].unique():
        loc_data = data_1[data_1['Location'] == loc]
        ax_combined.scatter(
            loc_data['Distance (km)'], 
            loc_data['Inlet Volume'], 
            color=colors.get(loc, 'grey'), 
            marker='o',  # Circle for 1
            s=70,
            edgecolors='black',
            label=f"Strag1 - {loc}"
        )

    # Plot for Strategy 2
    for loc in data_2['Location'].unique():
        loc_data = data_2[data_2['Location'] == loc]
        ax_combined.scatter(
            loc_data['Distance (km)'], 
            loc_data['Inlet Volume'], 
            color=colors.get(loc, 'grey'), 
            marker='^',  # Triangle for B
            s=70,
            edgecolors='black',
            label=f"Strag2 - {loc}"
        )

    ax_combined.set_title("Strategy 1 vs 2: Inlet Volume by Distance")
    ax_combined.set_xlabel("Distance from floodgates (km)")
    ax_combined.set_ylabel("Inlet Volume (Mm³ per tydal cycle)")
    ax_combined.grid(True)
    ax_combined.legend(title="Strategy & Location", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig_combined)

    
    # --- Flushing Efficiency Comparison ---
    st.subheader("Flushing Efficiency Comparison")
    # Prepare fac5 data from each strategy
    fac5_1 = data_1['fac5'] if not data_1.empty else None
    fac5_2 = data_2['fac5'] if not data_2.empty else None
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    data_to_plot = []
    labels = []
    if fac5_1 is not None and not fac5_1.empty:
        data_to_plot.append(fac5_1)
        labels.append("Strategy 1")
    if fac5_2 is not None and not fac5_2.empty:
        data_to_plot.append(fac5_2)
        labels.append("Strategy 2")
        
    if data_to_plot:
        ax3.boxplot(data_to_plot, labels=labels)
        ax3.set_title("Flushing Efficiency Comparison\n(Data shown is fictional and used for demonstration purposes only)")
        ax3.set_xlabel("Strategy")
        ax3.set_ylabel("Flushing Efficiency (-)")
        st.pyplot(fig3)
    else:
        st.write("No flushing efficiency data available for the selected strategies.")

with tab4:
    st.header("Inlet Volume Uncertainty Analysis")

    # Column layout
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Select Scenario")

        salinity_unc = st.selectbox("Salinity Level (mg/L)",
                                    sorted(data['Salinity Level'].unique()), key="tab4_salinity")
        data_unc = data[data['Salinity Level'] == salinity_unc]

        ebb_unc_options = sorted(data_unc['Ebb Volume'].unique())
        ebb_unc = st.selectbox("Ebb Volume (Mm³ per tydal cycle)",
                               ebb_unc_options, key="tab4_ebb")

        dynamic_pits = st.multiselect("Dynamic Equilibrium Pits",
                                      options=sorted(data['Location'].unique()),
                                      default=sorted(data['Location'].unique()),
                                      key="tab4_pits")

        st.image("Location.png", caption="Dashboard Explanation", use_container_width=True)

    with col2:
        st.subheader("Uncertainty Results")

        subset_unc = data_unc[
            (data_unc['Ebb Volume'] == ebb_unc) &
            (data_unc['Location'].isin(dynamic_pits))
        ]

        if subset_unc.empty:
            st.write("No data available for selected criteria.")
        else:
            inlet_volumes = sorted(subset_unc['Inlet Volume'].unique())
            np.random.seed(42)
            uncertainty_vals = {iv: np.random.uniform(0.05, 0.15, 100) for iv in inlet_volumes}

            uncertainty_df = pd.DataFrame({
                iv: uncertainty_vals[iv] for iv in inlet_volumes
            })

            # Box plot visualization for uncertainty
            fig4, ax4 = plt.subplots(figsize=(8,5))
            ax4.boxplot(uncertainty_df.values, labels=inlet_volumes, patch_artist=True,
                       boxprops=dict(facecolor="skyblue", color="navy"),
                       medianprops=dict(color="red"))
            ax4.set_title("Uncertainty Analysis \n (Data shown is fictional and used for demonstration purposes only)")
            ax4.set_xlabel("Inlet Volume (Mm³ per tydal cycle)")
            ax4.set_ylabel("Relative Uncertainty")
            ax4.grid(True)

            st.pyplot(fig4)

            # Recommended option (lowest median uncertainty)
            median_unc = uncertainty_df.median()
            best_iv = median_unc.idxmin()
            st.success(f"Recommended Inlet Volume: {best_iv} Mm³ per tydal cycle (Median Uncertainty: {median_unc.min():.3f})")

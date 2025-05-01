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
    "Inlet Volume vs Distance from floodgates", 
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

    Please read the scenarios, explore the tabs and functionalities, answer the questions and feel free to share any suggestions for improvement.

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
    To visualize and compare salinity intrusion location, flushing efficiencies, and uncertainties 
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
    - Dynamic equilibrium or salt intrusion location (Window 3)
    - Strategy comparisons (Window 4)
    - Uncertainty quantification and recommendations (Window 5)
    """)

    with st.form(key="feedback_tab1"):
        st.markdown("### 💬 Stakeholder Evaluation – Project Overview")

        q1 = st.radio("1. Do you understand the purpose of this project?", [3, 2, 1], format_func=lambda x: f"{x} - {'Yes' if x == 3 else 'Partly' if x == 2 else 'No'}")
        q2 = st.radio("2. Are the definitions of each element clear?", [3, 2, 1], format_func=lambda x: f"{x} - {'Yes' if x == 3 else 'Partly' if x == 2 else 'No'}")
        optional_comment = st.text_area("Could you tell me the key variables of the protocol?")
        optional_comment = st.text_area("Additional comments?")

        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            message = f"Q1:{q1}, Q2:{q2}, Q3:{q3}, Comment:{optional_comment}"
            save_feedback("Project Overview", message)
            st.success("✅ Feedback submitted. Thank you!")

# -------------------------
# Tab 2: Inlet Volume vs Distance Plot (with columns)
# -------------------------
with tab2:
    
    st.header("Inlet Volume vs Distance")

    st.markdown("""
    ### For this scenario, consider: 
    The salinity level is **2500 mg/L** and the amount of water that is able in the river is **30 Mm³ per tydal cycle**
    """)

    col1, col2 = st.columns([1, 1.2])  # Adjust widths as needed

    with col1:
        selected_salinity = st.selectbox(
            "Select: Salinity Level (mg/L) for Tab 2",
            sorted(data['Salinity Level'].unique()),
            key="tab2_salinity"
        )
        filtered_ebb = data[data['Salinity Level'] == selected_salinity]
        selected_ebb = st.selectbox(
            "Select: Ebb Volume (Mm³ per tydal cycle) for Tab 2",
            sorted(filtered_ebb['Ebb Volume'].unique()),
            key="tab2_ebb"
        )
        st.image("Location.png", caption="Reference: Dashboard Explanation", use_container_width=True)

    with col2:
        subset = data[
            (data['Salinity Level'] == selected_salinity) & 
            (data['Ebb Volume'] == selected_ebb)
        ]
        fig2, ax2 = plt.subplots(figsize=(8, 6))

        for loc in subset['Location'].unique():
            loc_data = subset[subset['Location'] == loc]
            ax2.scatter(
                loc_data['Distance (km)'], 
                loc_data['Inlet Volume'], 
                color=colors.get(loc, 'grey'), 
                s=50, 
                edgecolors='black', 
                label=loc
            )
        ax2.set_title(f"Inlet Volume vs Distance\nSalinity: {selected_salinity} mg/L, Ebb Volume: {selected_ebb} Mm³ per tydal cycle")
        ax2.set_xlabel("Distance from floodgates (km)")
        ax2.set_ylabel("Inlet Volume (Mm³ per tydal cycle)")
        ax2.grid(True)
        ax2.legend(title="Location")
        st.pyplot(fig2)

    # Questionaries
    with st.form(key="feedback_tab2"):  # Assuming tab index 2
        st.markdown("### 💬 Stakeholder Evaluation – Inlet Volume vs Distance")

        q1 = st.text_input("1. How many dynamic equilibrium (salt intrusion) locations are shown in the selected scenario?")
        q2 = st.text_input("2. What is the **maximum inlet volume (Mm³)** shown for location 'A' in this scenario?")
        q3 = st.radio(
            "3. Is the plot of **Distance vs Inlet Volume** clear and understandable?",
            [3, 2, 1],
            format_func=lambda x: f"{x} - {'Yes' if x == 3 else 'Partly' if x == 2 else 'No'}"
        )
        q4 = st.text_area("4. Do you have any additional feedback or suggestions for this window?")
            
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            message = f"Q1:{q1}, Q2:{q2}, Q3:{q3}, Comment:{q4}"
            save_feedback("Inlet Volume vs Distance", message)
            st.success("✅ Feedback submitted. Thank you!")

# -------------------------
# Tab 3: Strategy Comparison
# -------------------------
with tab3:
    st.header("Strategy Comparison")

    st.markdown("""
    ###  For this scenario, consider: 
    For strategy **1**, select a salinity level of The salinity level of **1000 mg/L** and the amount of water that is able in the river is **10 Mm³ per tydal cycle.**
                
    For strategy **2**, select a salinity level of The salinity level of **2500 mg/L** and the amount of water that is able in the river is **10 Mm³ per tydal cycle.**
    """)
    
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

    # Questionaries
    with st.form(key="feedback_tab3"):  # Assuming tab index 3
        st.markdown("### 💬 Stakeholder Evaluation – Strategy comparation")

        q1 = st.text_input("1. Which dynamic equilibrium location(s) appear for each strategy under this scenario?")
        q2 = st.text_input("2. Now, Set **Inlet Volume = 2 Mm³** for Strategy 1 and **1 Mm³** for Strategy 2. Which strategy shows the **higher flushing efficiency** according to the plot or boxplot?")
        q3 = st.text_area("3. Do you have any additional feedback or suggestions for improving this comparison window?")

        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            message = f"Q1:{q1}, Q2:{q2}, Comment:{q3}"
            save_feedback("Strategy Comparison", message)
            st.success("✅ Feedback submitted. Thank you!")

with tab4:
    st.header("Inlet Volume Uncertainty Analysis")

    st.markdown("""
    ### For this scenario, consider:  
    The salinity level is **2500 mg/L**, the available water in the river is **80 Mm³ per tidal cycle**, and the target location is the bottom depression **"D"**.
    """)

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

    # Questionaries
    with st.form(key="feedback_tab4"):  # Assuming tab index 3
        st.markdown("### 💬 Stakeholder Evaluation – Uncertainty Analysis")

        q1 = st.text_input("1. How many dynamic equilibrium (salt intrusion) locations are shown in the selected scenario?")
        q2 = st.text_input("2. What is the **maximum inlet volume (Mm³)** shown for location 'A' in this scenario?")
        q3 = st.radio(
            "3. Is the plot of **Distance vs Inlet Volume** clear and understandable?",
            [3, 2, 1],
            format_func=lambda x: f"{x} - {'Yes' if x == 3 else 'Partly' if x == 2 else 'No'}"
        )
        q4 = st.text_area("4. Do you have any additional feedback or suggestions for this window?")
            
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            message = f"Q1:{q1}, Q2:{q2}, Q3:{q3}, Comment:{q4}"
            save_feedback("Inlet Volume vs Distance", message)
            st.success("✅ Feedback submitted. Thank you!")

"""
MaLDReTH Research Data Lifecycle Visualization

A Streamlit application that visualizes the MaLDReTH Research Data Lifecycle
with tool exemplars, implemented in a style similar to the Harvard RDM visualization.
"""

import streamlit as st
import pandas as pd
import json
import os
from utils.data_loader import load_lifecycle_data
from utils.visualization import create_lifecycle_visualization

# Page configuration
st.set_page_config(
    page_title="MaLDReTH Research Data Lifecycle",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
with open(os.path.join("utils", "styles.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page header
st.title("MaLDReTH Research Data Lifecycle")
st.markdown("""
This visualization shows the MaLDReTH Research Data Lifecycle with tool exemplars for each stage.
Use the controls below to explore the lifecycle and learn about the various tools available at each stage.
""")

# Load lifecycle data
lifecycle_data = load_lifecycle_data()

# Sidebar controls
st.sidebar.header("Visualization Controls")

# View mode selection
view_mode = st.sidebar.radio(
    "Select View Mode",
    ["Complete Lifecycle", "Focus on Stage", "Compare Tools"]
)

# Stage filter for focused view
if view_mode == "Focus on Stage":
    selected_stage = st.sidebar.selectbox(
        "Select Stage to Focus On",
        [stage["name"] for stage in lifecycle_data["stages"]]
    )
elif view_mode == "Compare Tools":
    # Multi-select for tool categories
    all_categories = []
    for stage in lifecycle_data["stages"]:
        for exemplar in lifecycle_data["exemplars"]:
            if exemplar["stage"] == stage["name"] and exemplar["category"] not in all_categories:
                all_categories.append(exemplar["category"])
    
    selected_categories = st.sidebar.multiselect(
        "Select Tool Categories to Compare",
        sorted(all_categories),
        default=all_categories[:3] if len(all_categories) > 3 else all_categories
    )

# Display options
st.sidebar.header("Display Options")
show_connections = st.sidebar.checkbox("Show Connections", value=True)
show_exemplars = st.sidebar.checkbox("Show Tool Exemplars", value=True)
connection_type = st.sidebar.multiselect(
    "Connection Types to Show",
    ["normal", "alternative"],
    default=["normal", "alternative"]
)

# Main visualization
st.header("Lifecycle Visualization")

# Create and display the visualization
fig = create_lifecycle_visualization(
    lifecycle_data, 
    view_mode=view_mode,
    selected_stage=selected_stage if view_mode == "Focus on Stage" else None,
    selected_categories=selected_categories if view_mode == "Compare Tools" else None,
    show_connections=show_connections,
    show_exemplars=show_exemplars,
    connection_types=connection_type
)

st.plotly_chart(fig, use_container_width=True)

# Details section
if view_mode == "Focus on Stage":
    st.header(f"{selected_stage} Stage Details")
    
    # Find the selected stage data
    stage_data = next((stage for stage in lifecycle_data["stages"] if stage["name"] == selected_stage), None)
    
    if stage_data:
        st.subheader("Description")
        st.write(stage_data["description"])
        
        st.subheader("Tool Categories and Exemplars")
        
        # Get exemplars for this stage
        stage_exemplars = [ex for ex in lifecycle_data["exemplars"] if ex["stage"] == selected_stage]
        
        # Group by category
        exemplars_by_category = {}
        for exemplar in stage_exemplars:
            if exemplar["category"] not in exemplars_by_category:
                exemplars_by_category[exemplar["category"]] = []
            exemplars_by_category[exemplar["category"]].append(exemplar)
        
        # Display each category
        for category, exemplars in exemplars_by_category.items():
            with st.expander(f"{category} ({len(exemplars)} tools)", expanded=True):
                # Create a DataFrame for better display
                exemplar_df = pd.DataFrame([{
                    "Tool Name": ex["name"],
                    "Description": ex["description"]
                } for ex in exemplars])
                
                st.dataframe(exemplar_df, use_container_width=True)

elif view_mode == "Compare Tools":
    st.header("Tool Comparison")
    
    # Filter exemplars by selected categories
    filtered_exemplars = [ex for ex in lifecycle_data["exemplars"] 
                         if ex["category"] in selected_categories]
    
    # Group by tool name to handle duplicates across stages
    exemplars_by_name = {}
    for exemplar in filtered_exemplars:
        if exemplar["name"] not in exemplars_by_name:
            exemplars_by_name[exemplar["name"]] = exemplar
            exemplars_by_name[exemplar["name"]]["stages"] = [exemplar["stage"]]
        else:
            if exemplar["stage"] not in exemplars_by_name[exemplar["name"]]["stages"]:
                exemplars_by_name[exemplar["name"]]["stages"].append(exemplar["stage"])
    
    # Create DataFrame for display
    comparison_data = []
    for name, ex in exemplars_by_name.items():
        comparison_data.append({
            "Tool Name": name,
            "Category": ex["category"],
            "Stages Used In": ", ".join(ex["stages"]),
            "Description": ex["description"]
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)

else:
    # Show overview of all stages
    st.header("Lifecycle Stages Overview")
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    # First half of stages in first column
    half_index = len(lifecycle_data["stages"]) // 2
    
    with col1:
        for i, stage in enumerate(lifecycle_data["stages"][:half_index]):
            with st.expander(f"{stage['name']}", expanded=False):
                st.write(stage["description"])
                
                # Count exemplars for this stage
                stage_exemplars = [ex for ex in lifecycle_data["exemplars"] if ex["stage"] == stage["name"]]
                st.write(f"**Number of tools:** {len(stage_exemplars)}")
    
    # Second half of stages in second column
    with col2:
        for i, stage in enumerate(lifecycle_data["stages"][half_index:]):
            with st.expander(f"{stage['name']}", expanded=False):
                st.write(stage["description"])
                
                # Count exemplars for this stage
                stage_exemplars = [ex for ex in lifecycle_data["exemplars"] if ex["stage"] == stage["name"]]
                st.write(f"**Number of tools:** {len(stage_exemplars)}")

# Footer
st.markdown("""---
*This visualization is based on the MaLDReTH Research Data Lifecycle model. 
Data sourced from the RDA-OfR Mapping the Landscape of Digital Research Tools Working Group.*
""")

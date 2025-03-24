"""
MaLDReTH Research Data Lifecycle Visualization

A Streamlit application that visualizes the MaLDReTH Research Data Lifecycle
with a three-level structure: stages, substages, and tools.
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
This visualization shows the MaLDReTH Research Data Lifecycle with a three-level structure:
- **Inner Ring**: Lifecycle Stages
- **Middle Ring**: Tool Categories/Substages
- **Outer Ring**: Tool Exemplars

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
selected_stage = None
selected_categories = None

if view_mode == "Focus on Stage":
    selected_stage = st.sidebar.selectbox(
        "Select Stage to Focus On",
        [stage["name"] for stage in lifecycle_data["stages"]]
    )
    
    # Get categories for the selected stage
    if selected_stage:
        stage_categories = set()
        for exemplar in lifecycle_data["exemplars"]:
            if exemplar["stage"] == selected_stage:
                stage_categories.add(exemplar["category"])
        
        st.sidebar.markdown(f"### Categories in {selected_stage}")
        for category in sorted(stage_categories):
            st.sidebar.markdown(f"- {category}")

elif view_mode == "Compare Tools":
    # Multi-select for tool categories
    all_categories = set()
    for exemplar in lifecycle_data["exemplars"]:
        all_categories.add(exemplar["category"])
    
    selected_categories = st.sidebar.multiselect(
        "Select Tool Categories to Compare",
        sorted(all_categories),
        default=list(sorted(all_categories))[:3] if len(all_categories) > 3 else list(sorted(all_categories))
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

# Explanation of the three-level structure
with st.expander("How to Read This Visualization", expanded=False):
    st.markdown("""
    ### Three-Level Structure
    
    This visualization uses a concentric circle layout with three levels:
    
    1. **Inner Ring (Center)**: Research Data Lifecycle Stages
        - These are the main phases of the research data lifecycle
        - Color-coded for easy identification
    
    2. **Middle Ring**: Tool Categories/Substages
        - These are categories of tools used in each stage
        - Colored to match their parent stage
    
    3. **Outer Ring**: Tool Exemplars
        - Specific tools that belong to each category
        - Colored to match their parent category and stage
    
    ### Interactivity
    
    - **Hover** over any segment to see details
    - Use the **Focus on Stage** mode to zoom in on a specific stage
    - Use the **Compare Tools** mode to compare tools across different categories
    
    ### Connections
    
    - **Solid lines** show the normal flow between stages
    - **Dashed lines** show alternative connections or feedback loops
    """)

# Create and display the visualization
fig = create_lifecycle_visualization(
    lifecycle_data, 
    view_mode=view_mode,
    selected_stage=selected_stage,
    selected_categories=selected_categories,
    show_connections=show_connections,
    show_exemplars=show_exemplars,
    connection_types=connection_type
)

st.plotly_chart(fig, use_container_width=True)

# Additional information based on view mode
if view_mode == "Focus on Stage" and selected_stage:
    st.header(f"{selected_stage} Stage Details")
    
    # Find the selected stage data
    stage_data = next((stage for stage in lifecycle_data["stages"] if stage["name"] == selected_stage), None)
    
    if stage_data:
        st.subheader("Description")
        st.write(stage_data["description"])
        
        # Get categories and tools for this stage
        stage_tools = {}
        for exemplar in lifecycle_data["exemplars"]:
            if exemplar["stage"] == selected_stage:
                if exemplar["category"] not in stage_tools:
                    stage_tools[exemplar["category"]] = []
                stage_tools[exemplar["category"]].append(exemplar)
        
        st.subheader("Tool Categories and Exemplars")
        
        # Display each category in an expander
        for category, tools in stage_tools.items():
            with st.expander(f"{category} ({len(tools)} tools)", expanded=True):
                # Create a DataFrame for better display
                tools_df = pd.DataFrame([{
                    "Tool Name": tool["name"],
                    "Description": tool["description"]
                } for tool in tools])
                
                st.dataframe(tools_df, use_container_width=True)

elif view_mode == "Compare Tools" and selected_categories:
    st.header("Tool Category Comparison")
    
    # Create a DataFrame with tools from selected categories
    tools_data = []
    for exemplar in lifecycle_data["exemplars"]:
        if exemplar["category"] in selected_categories:
            tools_data.append({
                "Tool Name": exemplar["name"],
                "Category": exemplar["category"],
                "Stage": exemplar["stage"],
                "Description": exemplar["description"]
            })
    
    tools_df = pd.DataFrame(tools_data)
    
    # Display grouped by category
    for category in selected_categories:
        category_tools = tools_df[tools_df["Category"] == category]
        if not category_tools.empty:
            st.subheader(f"{category}")
            st.dataframe(
                category_tools[["Tool Name", "Stage", "Description"]].sort_values("Stage"),
                use_container_width=True
            )
    
    # Show statistics
    st.subheader("Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Tools", len(tools_df))
        
        # Count tools per category
        category_counts = tools_df["Category"].value_counts()
        
        # Display as a horizontal bar chart
        if not category_counts.empty:
            st.bar_chart(category_counts)
    
    with col2:
        # Count tools per stage within selected categories
        stage_counts = tools_df["Stage"].value_counts()
        
        if not stage_counts.empty:
            st.metric("Stages Covered", len(stage_counts))
            st.bar_chart(stage_counts)

else:
    # Overview of lifecycle stages
    st.header("Lifecycle Stages Overview")
    
    # Create a tabular view of stages and their tools count
    stage_data = []
    for stage in lifecycle_data["stages"]:
        # Count tools for this stage
        tools_count = len([ex for ex in lifecycle_data["exemplars"] if ex["stage"] == stage["name"]])
        
        # Count categories for this stage
        categories = set(ex["category"] for ex in lifecycle_data["exemplars"] if ex["stage"] == stage["name"])
        
        stage_data.append({
            "Stage": stage["name"],
            "Description": stage["description"],
            "Tool Categories": len(categories),
            "Total Tools": tools_count
        })
    
    # Display as a table
    st.dataframe(pd.DataFrame(stage_data), use_container_width=True)
    
    # Show global statistics
    st.subheader("Global Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Stages", len(lifecycle_data["stages"]))
    
    with col2:
        total_categories = len(set(ex["category"] for ex in lifecycle_data["exemplars"]))
        st.metric("Total Tool Categories", total_categories)
    
    with col3:
        st.metric("Total Tools", len(lifecycle_data["exemplars"]))
    
    with col4:
        st.metric("Connections", len(lifecycle_data["connections"]))

# Footer
st.markdown("""---
*This visualization is based on the MaLDReTH Research Data Lifecycle model. 
Data sourced from the RDA-OfR Mapping the Landscape of Digital Research Tools Working Group.*
""")

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

Use the controls below and to the left to explore the lifecycle and learn about 
the various tools available at each stage.
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
        
        if stage_categories:
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

# Level visibility controls
st.sidebar.markdown("### Show/Hide Levels")
show_connections = st.sidebar.checkbox("Show Connections", value=True)
show_substages = st.sidebar.checkbox("Show Substages", value=True)
show_tools = st.sidebar.checkbox("Show Tools", value=False)

# Connection type filter
if show_connections:
    connection_type = st.sidebar.multiselect(
        "Connection Types to Show",
        ["normal", "alternative"],
        default=["normal", "alternative"]
    )
else:
    connection_type = []

# Main visualization with control buttons at the top
st.header("Lifecycle Visualization")

# Add buttons for quick controls
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Show All Levels"):
        show_connections = True
        show_substages = True
        show_tools = True
with col2:
    if st.button("Show Stages & Substages"):
        show_connections = True
        show_substages = True
        show_tools = False
with col3:
    if st.button("Show Stages Only"):
        show_connections = True
        show_substages = False
        show_tools = False
with col4:
    if st.button("Reset View"):
        # Reset to default view
        show_connections = True
        show_substages = True
        show_tools = False
        view_mode = "Complete Lifecycle"
        selected_stage = None
        selected_categories = None

# Store session state
if 'show_connections' not in st.session_state:
    st.session_state.show_connections = show_connections
if 'show_substages' not in st.session_state:
    st.session_state.show_substages = show_substages
if 'show_tools' not in st.session_state:
    st.session_state.show_tools = show_tools
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = view_mode
if 'selected_stage' not in st.session_state:
    st.session_state.selected_stage = selected_stage
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = selected_categories

# Update session state based on controls
st.session_state.show_connections = show_connections
st.session_state.show_substages = show_substages
st.session_state.show_tools = show_tools
st.session_state.view_mode = view_mode
st.session_state.selected_stage = selected_stage
st.session_state.selected_categories = selected_categories

# Explanation of the three-level structure
with st.expander("How to Read This Visualization", expanded=False):
    st.markdown("""
    ### Three-Level Structure
    
    This visualization uses a concentric circle layout with three levels, separated by white space for clarity:
    
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
    - Use the buttons at the top to quickly change what's displayed
    
    ### Connections
    
    - **Solid lines** show the normal flow between stages
    - **Dashed lines** show alternative connections or feedback loops
    """)

# Create and display the visualization
fig = create_lifecycle_visualization(
    lifecycle_data, 
    view_mode=st.session_state.view_mode,
    selected_stage=st.session_state.selected_stage,
    selected_categories=st.session_state.selected_categories,
    show_connections=st.session_state.show_connections,
    show_substages=st.session_state.show_substages,
    show_tools=st.session_state.show_tools,
    connection_types=connection_type
)

# Register click events
config = {
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
    'displaylogo': False,
    'responsive': True
}

# Display the figure with click handling
st.plotly_chart(fig, use_container_width=True, config=config)

# Display help text for interactive elements
st.info("**Interactive Tips**: Click on any stage to focus on it. Use the sidebar controls to customize the view.")

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
        if exemplar["category"]
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

# Add JavaScript for click event handling
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    const plotDiv = document.querySelector('.js-plotly-plot');
    if (plotDiv) {
        plotDiv.on('plotly_click', function(data) {
            const point = data.points[0];
            const customdata = point.customdata;
            const meta = point.meta;
            
            // Handle click based on segment type
            if (customdata === 'stage') {
                // Focus on the stage
                const stage = meta.stage;
                if (stage) {
                    // Use Streamlit's postMessage to communicate with the Python code
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            action: 'focus_stage',
                            stage: stage
                        }
                    }, '*');
                }
            } else if (customdata === 'category') {
                // Focus on the category
                const stage = meta.stage;
                const category = meta.category;
                if (stage && category) {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            action: 'focus_category',
                            stage: stage,
                            category: category
                        }
                    }, '*');
                }
            }
        });
    }
});
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("""---
*This visualization is based on the MaLDReTH Research Data Lifecycle model. 
Data sourced from the RDA-OfR Mapping the Landscape of Digital Research Tools Working Group.*
""")

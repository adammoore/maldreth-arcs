"""
Data loading utilities for the MaLDReTH Research Data Lifecycle Visualization.
"""

import json
import os
import streamlit as st

@st.cache_data
def load_lifecycle_data():
    """
    Load lifecycle data from JSON file.
    
    Returns:
        dict: The lifecycle data including stages, connections, and exemplars.
    """
    try:
        # Try to load from the data directory
        data_path = os.path.join("data", "lifecycle_data.json")
        
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                return json.load(f)
        else:
            # If file doesn't exist, create it with example data
            example_data = create_example_data()
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            with open(data_path, 'w') as f:
                json.dump(example_data, f, indent=2)
            return example_data
    except Exception as e:
        st.error(f"Error loading lifecycle data: {str(e)}")
        return create_example_data()

def create_example_data():
    """
    Create example lifecycle data.
    
    Returns:
        dict: Example lifecycle data.
    """
    return {
        "stages": [
            {
                "name": "Conceptualise",
                "description": "To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.",
                "color": "#90be33"
            },
            {
                "name": "Plan",
                "description": "To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis. Data management plans (DMP) should be established for this phase of the lifecycle.",
                "color": "#90be44"
            },
            {
                "name": "Fund",
                "description": "To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.",
                "color": "#90be55"
            },
            {
                "name": "Collect",
                "description": "To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.",
                "color": "#90be66"
            },
            {
                "name": "Process",
                "description": "To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.",
                "color": "#90be79"
            },
            {
                "name": "Analyse",
                "description": "To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results.",
                "color": "#90be83"
            },
            {
                "name": "Store",
                "description": "To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.",
                "color": "#90be9a"
            },
            {
                "name": "Publish",
                "description": "To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.",
                "color": "#90beaa"
            },
            {
                "name": "Preserve",
                "description": "To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.",
                "color": "#90bebb"
            },
            {
                "name": "Share",
                "description": "To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community and society at large.",
                "color": "#90becc"
            },
            {
                "name": "Access",
                "description": "To control and manage data access by designated users and reusers. This may be in the form of publicly available published information. Necessary access control and authentication methods are applied.",
                "color": "#90bedd"
            },
            {
                "name": "Transform",
                "description": "To create new data from the original, for example: (i) by migration into a different format; (ii) by creating a subset, by selection or query, to create newly derived results, perhaps for publication; or, (iii) combining or appending with other data.",
                "color": "#90beee"
            }
        ],
        "connections": [
            {"from": "Conceptualise", "to": "Plan", "type": "normal"},
            {"from": "Plan", "to": "Fund", "type": "normal"},
            {"from": "Fund", "to": "Collect", "type": "normal"},
            {"from": "Collect", "to": "Process", "type": "normal"},
            {"from": "Process", "to": "Analyse", "type": "normal"},
            {"from": "Analyse", "to": "Store", "type": "normal"},
            {"from": "Store", "to": "Publish", "type": "normal"},
            {"from": "Publish", "to": "Preserve", "type": "normal"},
            {"from": "Preserve", "to": "Share", "type": "normal"},
            {"from": "Share", "to": "Access", "type": "normal"},
            {"from": "Access", "to": "Transform", "type": "normal"},
            {"from": "Transform", "to": "Conceptualise", "type": "normal"},
            {"from": "Analyse", "to": "Collect", "type": "alternative"},
            {"from": "Store", "to": "Analyse", "type": "alternative"},
            {"from": "Process", "to": "Collect", "type": "alternative"}
        ],
        "exemplars": [
            {"stage": "Conceptualise", "category": "Mind mapping", "name": "Miro", "description": "Collaborative online whiteboard platform for cross-functional team collaboration"},
            {"stage": "Conceptualise", "category": "Mind mapping", "name": "MindMeister", "description": "Online mind mapping software for brainstorming and idea management"},
            {"stage": "Conceptualise", "category": "Mind mapping", "name": "XMind", "description": "Full-featured mind mapping and brainstorming tool"},
            {"stage": "Conceptualise", "category": "Diagramming", "name": "Lucidchart", "description": "Web-based diagramming application for creating flowcharts, org charts, and more"},
            {"stage": "Plan", "category": "Data Management Planning", "name": "DMPTool", "description": "Tool for creating data management plans that meet institutional and funder requirements"},
            {"stage": "Plan", "category": "Project Planning", "name": "Trello", "description": "Web-based Kanban-style list-making application for project management"}
            # More exemplars would be added here in a real implementation
        ]
    }

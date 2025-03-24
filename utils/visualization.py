"""
Visualization functions for the MaLDReTH Research Data Lifecycle.
"""

import plotly.graph_objects as go
import numpy as np
import math
import pandas as pd
from collections import defaultdict

def create_lifecycle_visualization(
    lifecycle_data, 
    view_mode="Complete Lifecycle",
    selected_stage=None,
    selected_categories=None,
    show_connections=True,
    show_exemplars=True,
    connection_types=["normal", "alternative"]
):
    """
    Create a three-level circular visualization of the MaLDReTH Research Data Lifecycle.
    
    Args:
        lifecycle_data (dict): The lifecycle data including stages, connections, and exemplars.
        view_mode (str): The view mode, can be "Complete Lifecycle", "Focus on Stage", or "Compare Tools".
        selected_stage (str, optional): The selected stage for focused view.
        selected_categories (list, optional): The selected categories for tool comparison.
        show_connections (bool): Whether to show connections between stages.
        show_exemplars (bool): Whether to show tool exemplars.
        connection_types (list): The types of connections to show.
        
    Returns:
        plotly.graph_objects.Figure: The visualization figure.
    """
    # Configuration
    config = {
        "center_x": 0,
        "center_y": 0,
        "center_radius": 0.1,      # Center circle
        "inner_radius": 0.2,       # Stages (inner ring)
        "middle_radius": 0.5,      # Substages (middle ring)
        "outer_radius": 0.8,       # Tools (outer ring)
        "padding": 0.01,
        "stage_opacity": 0.9,
        "substage_opacity": 0.8,
        "tool_opacity": 0.7
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add center circle
    fig.add_shape(
        type="circle",
        x0=-config["center_radius"],
        y0=-config["center_radius"],
        x1=config["center_radius"],
        y1=config["center_radius"],
        fillcolor="#f0f0f0",
        line_color="#ccc",
        layer="below"
    )
    
    # Add center text
    fig.add_annotation(
        x=0, y=0,
        text="Research<br>Data<br>Lifecycle",
        showarrow=False,
        font=dict(size=14, color="#333")
    )
    
    # Get stages
    stages = lifecycle_data["stages"]
    num_stages = len(stages)
    
    # Calculate stage angles
    stage_angle = 2 * math.pi / num_stages
    start_angle = -math.pi / 2  # Start at the top
    
    # Create a dictionary to store stage positions
    stage_positions = {}
    
    # Prepare data structures for categories and tools
    categories_by_stage = defaultdict(list)
    tools_by_category = defaultdict(list)
    
    # Group tool exemplars by stage and category
    for exemplar in lifecycle_data["exemplars"]:
        stage_name = exemplar["stage"]
        category_name = exemplar["category"]
        
        # Create a unique category key
        category_key = f"{stage_name}_{category_name}"
        
        # Add category to list if not already there
        if category_name not in [c["name"] for c in categories_by_stage[stage_name]]:
            categories_by_stage[stage_name].append({
                "name": category_name,
                "key": category_key
            })
        
        # Add tool to category
        tools_by_category[category_key].append(exemplar)
    
    # Draw stages (inner ring)
    for i, stage in enumerate(stages):
        # Calculate angles for this stage
        angle_start = start_angle + i * stage_angle
        angle_end = angle_start + stage_angle - config["padding"]
        
        # Store middle point angle for connections
        middle_angle = (angle_start + angle_end) / 2
        stage_positions[stage["name"]] = {
            "angle": middle_angle,
            "start_angle": angle_start,
            "end_angle": angle_end,
            "x": config["inner_radius"] * math.cos(middle_angle),
            "y": config["inner_radius"] * math.sin(middle_angle)
        }
        
        # Determine opacity based on view mode
        opacity = config["stage_opacity"]
        if view_mode == "Focus on Stage" and stage["name"] != selected_stage:
            opacity = 0.3
        
        # Draw stage segment
        draw_sector(
            fig, 
            angle_start, 
            angle_end,
            config["center_radius"], 
            config["inner_radius"],
            stage["color"],
            opacity=opacity,
            hover_text=f"{stage['name']}<br>{stage['description']}"
        )
        
        # Add stage label
        label_angle = middle_angle
        label_radius = (config["center_radius"] + config["inner_radius"]) / 2
        label_x = label_radius * math.cos(label_angle)
        label_y = label_radius * math.sin(label_angle)
        
        # Adjust text angle for readability
        if label_angle > math.pi/2 and label_angle < 3*math.pi/2:
            text_angle = (label_angle * 180 / math.pi) - 180
        else:
            text_angle = label_angle * 180 / math.pi
            
        fig.add_annotation(
            x=label_x, y=label_y,
            text=stage["name"],
            showarrow=False,
            textangle=text_angle,
            font=dict(size=12, color="#333", family="Arial Black")
        )
    
    # Draw substages (middle ring)
    for stage_name, stage_pos in stage_positions.items():
        stage_color = next((s["color"] for s in stages if s["name"] == stage_name), "#ccc")
        categories = categories_by_stage[stage_name]
        num_categories = len(categories)
        
        if num_categories > 0:
            # Calculate angle for each category
            category_angle = (stage_pos["end_angle"] - stage_pos["start_angle"]) / num_categories
            
            for j, category in enumerate(categories):
                # Calculate angles for this category
                cat_angle_start = stage_pos["start_angle"] + j * category_angle
                cat_angle_end = cat_angle_start + category_angle - config["padding"]
                
                # Store category position
                middle_cat_angle = (cat_angle_start + cat_angle_end) / 2
                category["angle"] = middle_cat_angle
                category["start_angle"] = cat_angle_start
                category["end_angle"] = cat_angle_end
                
                # Determine opacity
                opacity = config["substage_opacity"]
                if view_mode == "Focus on Stage" and stage_name != selected_stage:
                    opacity = 0.2
                elif view_mode == "Compare Tools" and selected_categories:
                    if category["name"] not in selected_categories:
                        opacity = 0.2
                
                # Draw category segment
                draw_sector(
                    fig, 
                    cat_angle_start, 
                    cat_angle_end,
                    config["inner_radius"], 
                    config["middle_radius"],
                    lighten_color(stage_color, 0.1),
                    opacity=opacity,
                    hover_text=f"{category['name']}<br>Stage: {stage_name}"
                )
                
                # Add category label for important categories
                if (view_mode == "Complete Lifecycle" or 
                    (view_mode == "Focus on Stage" and stage_name == selected_stage) or
                    (view_mode == "Compare Tools" and not selected_categories or 
                     category["name"] in selected_categories)):
                    
                    label_radius = (config["inner_radius"] + config["middle_radius"]) / 2
                    label_x = label_radius * math.cos(middle_cat_angle)
                    label_y = label_radius * math.sin(middle_cat_angle)
                    
                    # Adjust text angle for readability
                    if middle_cat_angle > math.pi/2 and middle_cat_angle < 3*math.pi/2:
                        text_angle = (middle_cat_angle * 180 / math.pi) - 180
                    else:
                        text_angle = middle_cat_angle * 180 / math.pi
                    
                    # Shortened category name if too long
                    display_name = category["name"]
                    if len(display_name) > 15:
                        display_name = display_name[:12] + "..."
                        
                    fig.add_annotation(
                        x=label_x, y=label_y,
                        text=display_name,
                        showarrow=False,
                        textangle=text_angle,
                        font=dict(size=10, color="#333")
                    )
                
                # Draw tools (outer ring) for this category
                tools = tools_by_category[category["key"]]
                num_tools = len(tools)
                
                if num_tools > 0 and show_exemplars:
                    # Calculate angle for each tool
                    tool_angle = (cat_angle_end - cat_angle_start) / num_tools
                    
                    for k, tool in enumerate(tools):
                        # Calculate angles for this tool
                        tool_angle_start = cat_angle_start + k * tool_angle
                        tool_angle_end = tool_angle_start + tool_angle - config["padding"]
                        
                        # Determine opacity
                        opacity = config["tool_opacity"]
                        if view_mode == "Focus on Stage" and stage_name != selected_stage:
                            opacity = 0.1
                        elif view_mode == "Compare Tools" and selected_categories:
                            if category["name"] not in selected_categories:
                                opacity = 0.1
                        
                        # Draw tool segment
                        draw_sector(
                            fig, 
                            tool_angle_start, 
                            tool_angle_end,
                            config["middle_radius"], 
                            config["outer_radius"],
                            lighten_color(stage_color, 0.2),
                            opacity=opacity,
                            hover_text=f"{tool['name']}<br>{tool['description']}<br>Category: {category['name']}<br>Stage: {stage_name}"
                        )
    
    # Draw connections between stages if enabled
    if show_connections:
        for connection in lifecycle_data["connections"]:
            if connection["type"] in connection_types:
                from_pos = stage_positions[connection["from"]]
                to_pos = stage_positions[connection["to"]]
                
                # Determine line style based on connection type
                line_dash = "solid" if connection["type"] == "normal" else "dash"
                
                # Create curved path between stages
                path = create_curved_path(
                    from_pos["x"], from_pos["y"], 
                    to_pos["x"], to_pos["y"], 
                    config["inner_radius"] * 0.6,  # Control point offset
                    steps=50
                )
                
                # Draw connection line
                fig.add_trace(go.Scatter(
                    x=path[0],
                    y=path[1],
                    mode="lines",
                    line=dict(color="#555", width=1.5, dash=line_dash),
                    hoverinfo="none",
                    showlegend=False
                ))
                
                # Add arrow marker
                add_arrow(
                    fig, 
                    path[0][-2], path[1][-2],  # Second-to-last point
                    path[0][-1], path[1][-1],  # Last point
                    arrow_size=0.02
                )
    
    # Configure the layout
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),
        width=800,
        height=800,
        shapes=[],
        annotations=[],
        xaxis=dict(
            visible=False,
            range=[-1, 1]
        ),
        yaxis=dict(
            visible=False,
            range=[-1, 1],
            scaleanchor="x",
            scaleratio=1
        )
    )
    
    # Enable hover information
    fig.update_traces(hovertemplate="%{text}")
    
    return fig

def draw_sector(fig, angle_start, angle_end, r_inner, r_outer, color, opacity=0.8, hover_text=None):
    """
    Draw a sector in the circular visualization.
    
    Args:
        fig (plotly.graph_objects.Figure): The figure to add the sector to.
        angle_start (float): The starting angle in radians.
        angle_end (float): The ending angle in radians.
        r_inner (float): The inner radius.
        r_outer (float): The outer radius.
        color (str): The sector color.
        opacity (float, optional): The opacity of the sector. Defaults to 0.8.
        hover_text (str, optional): The hover text for the sector. Defaults to None.
    """
    # Generate points for the sector
    theta = np.linspace(angle_start, angle_end, 50)
    
    # Inner arc points (in reverse to create a closed shape)
    x_inner = r_inner * np.cos(theta[::-1])
    y_inner = r_inner * np.sin(theta[::-1])
    
    # Outer arc points
    x_outer = r_outer * np.cos(theta)
    y_outer = r_outer * np.sin(theta)
    
    # Combine to form a closed shape
    x = np.concatenate([x_outer, x_inner, [x_outer[0]]])
    y = np.concatenate([y_outer, y_inner, [y_outer[0]]])
    
    # Add to figure
    fig.add_trace(go.Scatter(
        x=x, y=y,
        fill="toself",
        fillcolor=color,
        opacity=opacity,
        line=dict(color="white", width=1),
        hoverinfo="text" if hover_text else "none",
        text=hover_text,
        showlegend=False
    ))

def create_curved_path(x1, y1, x2, y2, control_offset=0.3, steps=50):
    """
    Create a curved path between two points using a quadratic Bezier curve.
    
    Args:
        x1, y1: Starting point coordinates
        x2, y2: Ending point coordinates
        control_offset: Distance from midpoint for control point
        steps: Number of points to generate along the curve
        
    Returns:
        tuple: Two arrays containing x and y coordinates of the path
    """
    # Calculate midpoint
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    
    # Find perpendicular direction
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    udx = dx / length if length > 0 else 0
    udy = dy / length if length > 0 else 0
    
    # Perpendicular vector
    pdx = -udy
    pdy = udx
    
    # Control point
    cx = mx + pdx * control_offset
    cy = my + pdy * control_offset
    
    # Generate points along the quadratic Bezier curve
    t = np.linspace(0, 1, steps)
    x = (1-t)**2 * x1 + 2*(1-t)*t * cx + t**2 * x2
    y = (1-t)**2 * y1 + 2*(1-t)*t * cy + t**2 * y2
    
    return x, y

def add_arrow(fig, x0, y0, x1, y1, arrow_size=0.02, color="#555"):
    """
    Add an arrow marker to indicate direction in a connection.
    
    Args:
        fig (plotly.graph_objects.Figure): The figure to add the arrow to.
        x0 (float): X-coordinate of the start point.
        y0 (float): Y-coordinate of the start point.
        x1 (float): X-coordinate of the end point.
        y1 (float): Y-coordinate of the end point.
        arrow_size (float, optional): The size of the arrow. Defaults to 0.02.
        color (str, optional): The color of the arrow. Defaults to "#555".
    """
    # Calculate direction vector
    dx = x1 - x0
    dy = y1 - y0
    
    # Normalize
    length = math.sqrt(dx**2 + dy**2)
    udx = dx / length if length > 0 else 0
    udy = dy / length if length > 0 else 0
    
    # Calculate perpendicular vector for arrow head
    perpx = -udy
    perpy = udx
    
    # Add arrow head
    fig.add_trace(go.Scatter(
        x=[x1 - arrow_size * (udx - perpx), 
           x1, 
           x1 - arrow_size * (udx + perpx)],
        y=[y1 - arrow_size * (udy - perpy), 
           y1, 
           y1 - arrow_size * (udy + perpy)],
        fill="toself",
        fillcolor=color,
        line=dict(color=color),
        mode="lines",
        hoverinfo="none",
        showlegend=False
    ))

def lighten_color(color, factor=0.2):
    """
    Lighten a color by the given factor.
    
    Args:
        color (str): The color to lighten in hex format (e.g., "#ff0000").
        factor (float, optional): The factor to lighten the color. Defaults to 0.2.
        
    Returns:
        str: The lightened color in hex format.
    """
    # Remove '#' if present
    color = color.lstrip('#')
    
    # Convert hex to RGB
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    # Lighten
    r = min(int(r + (255 - r) * factor), 255)
    g = min(int(g + (255 - g) * factor), 255)
    b = min(int(b + (255 - b) * factor), 255)
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"

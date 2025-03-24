"""
Visualization functions for the MaLDReTH Research Data Lifecycle.
"""

import plotly.graph_objects as go
import numpy as np
import math

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
    Create a circular visualization of the MaLDReTH Research Data Lifecycle.
    
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
        "inner_radius": 0.2,
        "middle_radius": 0.5,
        "outer_radius": 0.8,
        "padding": 0.01,
        "stage_opacity": 0.8,
        "exemplar_opacity": 0.7
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add center circle
    fig.add_shape(
        type="circle",
        x0=-config["inner_radius"],
        y0=-config["inner_radius"],
        x1=config["inner_radius"],
        y1=config["inner_radius"],
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
    
    # Draw stages
    for i, stage in enumerate(stages):
        # Calculate angles for this stage
        angle_start = start_angle + i * stage_angle
        angle_end = angle_start + stage_angle - config["padding"]
        
        # Store middle point angle for connections
        middle_angle = (angle_start + angle_end) / 2
        stage_positions[stage["name"]] = {
            "angle": middle_angle,
            "x": config["middle_radius"] * math.cos(middle_angle),
            "y": config["middle_radius"] * math.sin(middle_angle)
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
            config["inner_radius"], 
            config["middle_radius"],
            stage["color"],
            opacity=opacity
        )
        
        # Add stage label
        label_angle = middle_angle
        label_radius = (config["inner_radius"] + config["middle_radius"]) / 2
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
            font=dict(size=12, color="#333")
        )
    
    # Draw connections between stages if enabled
    if show_connections:
        for connection in lifecycle_data["connections"]:
            if connection["type"] in connection_types:
                from_pos = stage_positions[connection["from"]]
                to_pos = stage_positions[connection["to"]]
                
                # Determine line style based on connection type
                line_dash = "solid" if connection["type"] == "normal" else "dash"
                
                # Draw connection line
                fig.add_trace(go.Scatter(
                    x=[from_pos["x"], to_pos["x"]],
                    y=[from_pos["y"], to_pos["y"]],
                    mode="lines",
                    line=dict(color="#555", width=1.5, dash=line_dash),
                    hoverinfo="none",
                    showlegend=False
                ))
                
                # Add arrow marker
                add_arrow(fig, from_pos["x"], from_pos["y"], to_pos["x"], to_pos["y"])
    
    # Draw exemplars if enabled
    if show_exemplars:
        # Group exemplars by stage
        exemplars_by_stage = {}
        for exemplar in lifecycle_data["exemplars"]:
            if exemplar["stage"] not in exemplars_by_stage:
                exemplars_by_stage[exemplar["stage"]] = []
            
            # Apply category filter if in Compare Tools mode
            if view_mode == "Compare Tools" and selected_categories:
                if exemplar["category"] in selected_categories:
                    exemplars_by_stage[exemplar["stage"]].append(exemplar)
            else:
                exemplars_by_stage[exemplar["stage"]].append(exemplar)
        
        # Draw exemplars for each stage
        for stage_name, exemplars in exemplars_by_stage.items():
            if stage_name not in stage_positions:
                continue
                
            # Skip if not the selected stage in Focus mode
            if view_mode == "Focus on Stage" and stage_name != selected_stage:
                continue
                
            # Get stage position and color
            stage_pos = stage_positions[stage_name]
            stage_color = next((s["color"] for s in stages if s["name"] == stage_name), "#ccc")
            
            # Calculate exemplar positions
            num_exemplars = len(exemplars)
            if num_exemplars > 0:
                exemplar_angle = stage_angle / max(num_exemplars, 1)
                
                # Calculate starting angle for this stage's exemplars
                exemplar_start_angle = stage_pos["angle"] - stage_angle / 2
                
                for j, exemplar in enumerate(exemplars):
                    # Calculate angles for this exemplar
                    ex_angle_start = exemplar_start_angle + j * exemplar_angle
                    ex_angle_end = ex_angle_start + exemplar_angle - config["padding"]
                    
                    # Draw exemplar segment
                    draw_sector(
                        fig, 
                        ex_angle_start, 
                        ex_angle_end,
                        config["middle_radius"], 
                        config["outer_radius"],
                        lighten_color(stage_color, 0.2),
                        opacity=config["exemplar_opacity"],
                        hover_text=f"{exemplar['name']}<br>{exemplar['category']}<br>{exemplar['description']}"
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
    udx = dx / length
    udy = dy / length
    
    # Calculate arrow position (slightly before the end point)
    arrow_x = x1 - udx * 0.05
    arrow_y = y1 - udy * 0.05
    
    # Calculate perpendicular vector for arrow head
    perpx = -udy
    perpy = udx
    
    # Add arrow head
    fig.add_trace(go.Scatter(
        x=[arrow_x - arrow_size * (udx - perpx), 
           arrow_x, 
           arrow_x - arrow_size * (udx + perpx)],
        y=[arrow_y - arrow_size * (udy - perpy), 
           arrow_y, 
           arrow_y - arrow_size * (udy + perpy)],
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

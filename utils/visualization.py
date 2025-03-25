"""
Visualization functions for the MaLDReTH Research Data Lifecycle.
"""

import plotly.graph_objects as go
import numpy as np
import math
from collections import defaultdict

def create_lifecycle_visualization(
    lifecycle_data, 
    view_mode="Complete Lifecycle",
    selected_stage=None,
    selected_categories=None,
    show_connections=True,
    show_substages=True,
    show_tools=False,
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
        show_substages (bool): Whether to show substages.
        show_tools (bool): Whether to show tools.
        connection_types (list): The types of connections to show.
        
    Returns:
        plotly.graph_objects.Figure: The visualization figure.
    """
    # Configuration
    config = {
        "center_x": 0,
        "center_y": 0,
        "center_radius": 0.15,     # Center circle
        "inner_radius": 0.28,      # Stages (inner ring)
        "middle_radius": 0.50,     # Substages (middle ring)
        "outer_radius": 0.75,      # Tools (outer ring)
        "padding_angle": 0.02,     # Angular padding between segments
        "ring_padding": 0.03,      # Radial padding between rings
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
        fillcolor="#f8f8f8",
        line_color="#dddddd",
        line_width=2,
        layer="below"
    )
    
    # Add separator rings
    fig.add_shape(
        type="circle",
        x0=-(config["inner_radius"] - config["ring_padding"]/2),
        y0=-(config["inner_radius"] - config["ring_padding"]/2),
        x1=(config["inner_radius"] - config["ring_padding"]/2),
        y1=(config["inner_radius"] - config["ring_padding"]/2),
        fillcolor="rgba(0,0,0,0)",
        line_color="#dddddd",
        line_width=1,
        layer="below"
    )
    
    fig.add_shape(
        type="circle",
        x0=-(config["middle_radius"] - config["ring_padding"]/2),
        y0=-(config["middle_radius"] - config["ring_padding"]/2),
        x1=(config["middle_radius"] - config["ring_padding"]/2),
        y1=(config["middle_radius"] - config["ring_padding"]/2),
        fillcolor="rgba(0,0,0,0)",
        line_color="#dddddd",
        line_width=1,
        layer="below"
    )
    
    fig.add_shape(
        type="circle",
        x0=-(config["outer_radius"] + config["ring_padding"]/2),
        y0=-(config["outer_radius"] + config["ring_padding"]/2),
        x1=(config["outer_radius"] + config["ring_padding"]/2),
        y1=(config["outer_radius"] + config["ring_padding"]/2),
        fillcolor="rgba(0,0,0,0)",
        line_color="#dddddd",
        line_width=1,
        layer="below"
    )
    
    # Add center text
    fig.add_annotation(
        x=0, y=0,
        text="Research<br>Data<br>Lifecycle",
        showarrow=False,
        font=dict(size=14, color="#333", family="Arial"),
        align="center"
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
        category_key = f"{stage_name}::{category_name}"
        
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
        angle_end = angle_start + stage_angle - config["padding_angle"]
        
        # Store middle point angle for connections
        middle_angle = (angle_start + angle_end) / 2
        stage_positions[stage["name"]] = {
            "angle": middle_angle,
            "start_angle": angle_start,
            "end_angle": angle_end,
            "x": (config["center_radius"] + config["inner_radius"]) / 2 * math.cos(middle_angle),
            "y": (config["center_radius"] + config["inner_radius"]) / 2 * math.sin(middle_angle)
        }
        
        # Determine opacity based on view mode
        opacity = config["stage_opacity"]
        if view_mode == "Focus on Stage" and stage["name"] != selected_stage:
            opacity = 0.4
        
        # Inner radius with padding
        r_inner = config["center_radius"] + config["ring_padding"]
        # Outer radius with padding
        r_outer = config["inner_radius"] - config["ring_padding"]
        
        # Draw stage segment
        draw_sector(
            fig, 
            angle_start, 
            angle_end,
            r_inner, 
            r_outer,
            stage["color"],
            opacity=opacity,
            hover_text=f"<b>{stage['name']}</b><br>{stage['description']}",
            stage_name=stage['name'],
            segment_type="stage"
        )
        
        # Add stage label
        label_angle = middle_angle
        label_radius = (r_inner + r_outer) / 2
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
            font=dict(size=10, color="#333", family="Arial"),
            align="center"
        )
    
    # Draw substages (middle ring) if enabled
    if show_substages:
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
                    cat_angle_end = cat_angle_start + category_angle - config["padding_angle"]
                    
                    # Store category position
                    middle_cat_angle = (cat_angle_start + cat_angle_end) / 2
                    category["angle"] = middle_cat_angle
                    category["start_angle"] = cat_angle_start
                    category["end_angle"] = cat_angle_end
                    
                    # Determine opacity
                    opacity = config["substage_opacity"]
                    if view_mode == "Focus on Stage" and stage_name != selected_stage:
                        opacity = 0.3
                    elif view_mode == "Compare Tools" and selected_categories:
                        if category["name"] not in selected_categories:
                            opacity = 0.3
                    
                    # Inner radius with padding
                    r_inner = config["inner_radius"] + config["ring_padding"]
                    # Outer radius with padding
                    r_outer = config["middle_radius"] - config["ring_padding"]
                    
                    # Draw category segment
                    draw_sector(
                        fig, 
                        cat_angle_start, 
                        cat_angle_end,
                        r_inner, 
                        r_outer,
                        lighten_color(stage_color, 0.1),
                        opacity=opacity,
                        hover_text=f"<b>{category['name']}</b><br>Stage: {stage_name}",
                        stage_name=stage_name,
                        category_name=category['name'],
                        segment_type="category"
                    )
                    
                    # Add category label for important categories
                    if ((view_mode == "Complete Lifecycle") or 
                        (view_mode == "Focus on Stage" and stage_name == selected_stage) or
                        (view_mode == "Compare Tools" and 
                         (not selected_categories or category["name"] in selected_categories))):
                        
                        label_radius = (r_inner + r_outer) / 2
                        label_x = label_radius * math.cos(middle_cat_angle)
                        label_y = label_radius * math.sin(middle_cat_angle)
                        
                        # Adjust text angle for readability
                        if middle_cat_angle > math.pi/2 and middle_cat_angle < 3*math.pi/2:
                            text_angle = (middle_cat_angle * 180 / math.pi) - 180
                        else:
                            text_angle = middle_cat_angle * 180 / math.pi
                        
                        # Shortened category name if too long
                        display_name = category["name"]
                        if len(display_name) > 12:
                            display_name = display_name[:10] + "..."
                            
                        # Add the label
                        # Only add labels if there's enough space
                        if category_angle > 0.15:  # Minimum angle for labels
                            fig.add_annotation(
                                x=label_x, y=label_y,
                                text=display_name,
                                showarrow=False,
                                textangle=text_angle,
                                font=dict(size=8, color="#333"),
                                align="center"
                            )
                    
                    # Draw tools (outer ring) for this category if enabled
                    if show_tools:
                        tools = tools_by_category[category["key"]]
                        num_tools = len(tools)
                        
                        if num_tools > 0:
                            # Calculate angle for each tool
                            tool_angle = (cat_angle_end - cat_angle_start) / num_tools
                            
                            for k, tool in enumerate(tools):
                                # Calculate angles for this tool
                                tool_angle_start = cat_angle_start + k * tool_angle
                                tool_angle_end = tool_angle_start + tool_angle - config["padding_angle"]
                                
                                # Determine opacity
                                opacity = config["tool_opacity"]
                                if view_mode == "Focus on Stage" and stage_name != selected_stage:
                                    opacity = 0.2
                                elif view_mode == "Compare Tools" and selected_categories:
                                    if category["name"] not in selected_categories:
                                        opacity = 0.2
                                
                                # Inner radius with padding
                                r_inner = config["middle_radius"] + config["ring_padding"]
                                # Outer radius with padding
                                r_outer = config["outer_radius"] - config["ring_padding"]
                                
                                # Draw tool segment
                                draw_sector(
                                    fig, 
                                    tool_angle_start, 
                                    tool_angle_end,
                                    r_inner, 
                                    r_outer,
                                    lighten_color(stage_color, 0.2),
                                    opacity=opacity,
                                    hover_text=f"<b>{tool['name']}</b><br>{tool['description']}<br>Category: {category['name']}<br>Stage: {stage_name}",
                                    stage_name=stage_name,
                                    category_name=category['name'],
                                    tool_name=tool['name'],
                                    segment_type="tool"
                                )
    
    # Draw connections between stages if enabled
    if show_connections:
        for connection in lifecycle_data["connections"]:
            if connection["type"] in connection_types:
                # Skip if either the source or target stage doesn't exist
                if connection["from"] not in stage_positions or connection["to"] not in stage_positions:
                    continue
                    
                from_pos = stage_positions[connection["from"]]
                to_pos = stage_positions[connection["to"]]
                
                # Determine line style based on connection type
                line_dash = "solid" if connection["type"] == "normal" else "dash"
                
                # Draw connection line with appropriate styling
                draw_connection(
                    fig,
                    from_pos["angle"],
                    to_pos["angle"],
                    config["center_radius"] * 0.8,  # Radius for connections
                    line_type=line_dash,
                    hover_text=f"Connection: {connection['from']} → {connection['to']}<br>Type: {connection['type']}"
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
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # Enable hover information
    fig.update_traces(hovertemplate="%{text}")
    
    return fig

def draw_sector(fig, angle_start, angle_end, r_inner, r_outer, color, opacity=0.8, 
                hover_text=None, stage_name=None, category_name=None, tool_name=None, segment_type=None):
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
        stage_name (str, optional): The name of the stage. Defaults to None.
        category_name (str, optional): The name of the category. Defaults to None.
        tool_name (str, optional): The name of the tool. Defaults to None.
        segment_type (str, optional): The type of segment ("stage", "category", or "tool"). Defaults to None.
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
    
    # Create custom data for click events
    customdata = np.full(len(x), segment_type)
    
    # Add to figure
    fig.add_trace(go.Scatter(
        x=x, y=y,
        fill="toself",
        fillcolor=color,
        opacity=opacity,
        line=dict(color="white", width=1),
        hoverinfo="text" if hover_text else "none",
        text=hover_text,
        customdata=customdata,
        showlegend=False,
        meta={
            "type": segment_type,
            "stage": stage_name,
            "category": category_name,
            "tool": tool_name
        },
        name=f"{stage_name or ''}-{category_name or ''}-{tool_name or ''}"
    ))

def draw_connection(fig, angle1, angle2, radius, line_type="solid", hover_text=None):
    """
    Draw a connection between two points on the circle.
    
    Args:
        fig (plotly.graph_objects.Figure): The figure to add the connection to.
        angle1 (float): The starting angle in radians.
        angle2 (float): The ending angle in radians.
        radius (float): The radius of the circle.
        line_type (str, optional): The type of line ("solid" or "dash"). Defaults to "solid".
        hover_text (str, optional): The hover text for the connection. Defaults to None.
    """
    # Ensure angles are in the right order for the shortest path
    if abs(angle2 - angle1) > math.pi:
        if angle1 < angle2:
            angle1 += 2 * math.pi
        else:
            angle2 += 2 * math.pi
    
    # Number of points to interpolate
    num_points = 50
    
    # Create angles for the arc
    theta = np.linspace(angle1, angle2, num_points)
    
    # Calculate points on the arc
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    
    # Draw the connection
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="lines",
        line=dict(
            color="#555",
            width=1.5,
            dash="dash" if line_type == "dash" else "solid"
        ),
        hoverinfo="text" if hover_text else "none",
        text=hover_text,
        showlegend=False
    ))
    
    # Add an arrow at the end
    last_angle = theta[-1]
    arrow_angle = last_angle + math.pi / 2  # Perpendicular to the tangent
    
    arrow_length = 0.02
    arrow_x = [x[-1], 
               x[-1] + arrow_length * math.cos(arrow_angle + math.pi/8), 
               x[-1] + arrow_length * math.cos(arrow_angle - math.pi/8)]
    arrow_y = [y[-1], 
               y[-1] + arrow_length * math.sin(arrow_angle + math.pi/8), 
               y[-1] + arrow_length * math.sin(arrow_angle - math.pi/8)]
    
    fig.add_trace(go.Scatter(
        x=arrow_x, y=arrow_y,
        fill="toself",
        fillcolor="#555",
        line=dict(color="#555"),
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

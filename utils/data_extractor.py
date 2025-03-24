"""
Data extraction utilities for the MaLDReTH Research Data Lifecycle Visualization.
"""

def extract_categories_by_stage(lifecycle_data):
    """
    Extract categories grouped by stage from the lifecycle data.
    
    Args:
        lifecycle_data (dict): The lifecycle data.
        
    Returns:
        dict: A dictionary mapping stage names to lists of categories.
    """
    categories_by_stage = {}
    
    for exemplar in lifecycle_data["exemplars"]:
        stage_name = exemplar["stage"]
        category_name = exemplar["category"]
        
        if stage_name not in categories_by_stage:
            categories_by_stage[stage_name] = set()
        
        categories_by_stage[stage_name].add(category_name)
    
    # Convert sets to sorted lists
    for stage_name in categories_by_stage:
        categories_by_stage[stage_name] = sorted(categories_by_stage[stage_name])
    
    return categories_by_stage

def extract_tools_by_category(lifecycle_data):
    """
    Extract tools grouped by category from the lifecycle data.
    
    Args:
        lifecycle_data (dict): The lifecycle data.
        
    Returns:
        dict: A dictionary mapping category names to lists of tools.
    """
    tools_by_category = {}
    
    for exemplar in lifecycle_data["exemplars"]:
        stage_name = exemplar["stage"]
        category_name = exemplar["category"]
        
        # Create a unique key for each stage-category combination
        key = f"{stage_name}::{category_name}"
        
        if key not in tools_by_category:
            tools_by_category[key] = []
        
        tools_by_category[key].append(exemplar)
    
    return tools_by_category

def get_stage_color(lifecycle_data, stage_name):
    """
    Get the color for a specific stage.
    
    Args:
        lifecycle_data (dict): The lifecycle data.
        stage_name (str): The name of the stage.
        
    Returns:
        str: The color for the stage, or a default color if not found.
    """
    for stage in lifecycle_data["stages"]:
        if stage["name"] == stage_name:
            return stage["color"]
    
    # Default color if stage not found
    return "#cccccc"

def get_stages_with_counts(lifecycle_data):
    """
    Get information about stages with counts of categories and tools.
    
    Args:
        lifecycle_data (dict): The lifecycle data.
        
    Returns:
        list: A list of dictionaries with stage information.
    """
    stages_info = []
    
    # Get categories by stage
    categories_by_stage = extract_categories_by_stage(lifecycle_data)
    
    for stage in lifecycle_data["stages"]:
        stage_name = stage["name"]
        
        # Count tools for this stage
        tools_count = len([ex for ex in lifecycle_data["exemplars"] if ex["stage"] == stage_name])
        
        # Get categories for this stage
        categories = categories_by_stage.get(stage_name, [])
        
        stages_info.append({
            "name": stage_name,
            "description": stage["description"],
            "color": stage["color"],
            "categories_count": len(categories),
            "tools_count": tools_count,
            "categories": categories
        })
    
    return stages_info

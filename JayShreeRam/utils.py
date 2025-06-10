def get_element_color(element_type):
    """
    Get a color for a given element type.
    
    Args:
        element_type (str): Type of element
    
    Returns:
        str: Hex color code
    """
    type_colors = {
        'conduit': '#1f77b4',  # blue
        'dummy': '#ff7f0e',    # orange
        'reservoir': '#2ca02c', # green
        'junction': '#d62728',  # red
        'node': '#9467bd',     # purple
        'storage': '#8c564b',  # brown
        'flowbalancing': '#e377c2',  # pink
        'unknown': '#7f7f7f'   # gray
    }
    
    return type_colors.get(element_type.lower(), '#7f7f7f')

def get_node_group_colors(n_groups):
    """
    Get a list of colors for node groups.
    
    Args:
        n_groups (int): Number of groups
    
    Returns:
        list: List of color codes
    """
    if n_groups <= 1:
        return ['#1f77b4']
    
    # Predefined set of colors for small number of groups
    if n_groups <= 10:
        palette = [
            '#1f77b4',  # blue
            '#ff7f0e',  # orange
            '#2ca02c',  # green
            '#d62728',  # red
            '#9467bd',  # purple
            '#8c564b',  # brown
            '#e377c2',  # pink
            '#7f7f7f',  # gray
            '#bcbd22',  # yellow
            '#17becf'   # teal
        ]
        return palette[:n_groups]
    
    # Generate colors for larger number of groups
    colors = []
    for i in range(n_groups):
        # Create a color gradient from blue to red
        r = int(255 * (i / (n_groups - 1)))
        g = 100
        b = int(255 * (1 - i / (n_groups - 1)))
        colors.append(f'rgb({r},{g},{b})')
    
    return colors

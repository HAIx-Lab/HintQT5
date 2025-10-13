def get_all_components(jsondata: dict) -> list:
    """Recursively extracts all UI components from the hierarchy, ignoring system UI."""
    root = jsondata.get('hierarchy', {})
    queue = [root]
    res = []
    while queue:
        current_node = queue.pop(0)
        if not isinstance(current_node, dict):
            continue
            
        # Check for nested nodes
        node_children = current_node.get('node')
        if node_children:
            if isinstance(node_children, dict):
                queue.append(node_children)
            elif isinstance(node_children, list):
                queue.extend(node_children)

        # Add the node itself to results if it's not a container for other nodes
        else:
            # Filter out system UI components
            package = current_node.get('@package', '')
            resource_id = current_node.get('@resource-id', '')
            if 'com.android.systemui' not in package and 'com.android.systemui' not in resource_id:
                res.append(current_node)
    return res

def find_edit_text(jsondata: dict) -> list:
    """Finds all EditText or AutoCompleteTextView components."""
    all_components = get_all_components(jsondata)
    return [
        comp for comp in all_components 
        if comp.get('@class') in ['android.widget.EditText', 'android.widget.AutoCompleteTextView']
    ]

def get_basic_info(component: dict) -> dict:
    """Extracts a standardized set of properties from a component dictionary."""
    return {
        'id': component.get('@resource-id'),
        'text': component.get('@text'),
        'label': component.get('@content-desc'), # 'label' is often in content-desc
        'text-hint': component.get('@content-desc'), # Also check here for hints
        'app_name': component.get('@package')
    }

def parse_bounds(bounds_str: str) -> list:
    """Converts a bounds string like '[x1,y1][x2,y2]' to a list of integers."""
    try:
        parts = bounds_str.replace('][', ',').strip('[]').split(',')
        return [int(p) for p in parts]
    except (ValueError, IndexError):
        return [0, 0, 0, 0] # Return a default on parsing error

def choose_from_pos(all_components: list, bounds: str, screen_height: int, screen_width: int) -> list:
    """Finds components that are physically close to the target component's bounds."""
    target_bounds = parse_bounds(bounds)
    left, top, right, bottom = target_bounds
    
    # Define search area around the target component
    vertical_range = screen_height // 8
    horizontal_range = screen_width // 4
    
    extended_top = max(0, top - vertical_range)
    extended_bottom = min(screen_height, bottom + vertical_range)
    extended_left = max(0, left - horizontal_range)
    extended_right = min(screen_width, right + horizontal_range)
    
    nearby_components = []
    for comp in all_components:
        comp_bounds = parse_bounds(comp.get('@bounds', ''))
        c_left, c_top, c_right, c_bottom = comp_bounds
        
        if comp_bounds == target_bounds:
            continue
        
        # Check for overlap between the component and the extended search area
        if (c_left < extended_right and c_right > extended_left and
            c_top < extended_bottom and c_bottom > extended_top):
            nearby_components.append(comp)
            
    return nearby_components


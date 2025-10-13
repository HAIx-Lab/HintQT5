def turn_null_to_str(prop):
    """Converts None to an empty string, otherwise returns the property."""
    return '' if prop is None else str(prop)

def format_component_info(component_info: dict) -> str:
    """Creates a descriptive sentence from a component's basic info."""
    parts = []
    # Use resource-id to infer purpose
    if component_info.get('id'):
        purpose = component_info['id'].split('/')[-1].replace('_', ' ')
        parts.append(f"its purpose might be '{purpose}'")
    # Use text if available
    if component_info.get('text'):
        parts.append(f"it displays the text '{component_info['text']}'")
    # Use label/content-desc if available
    if component_info.get('label'):
        parts.append(f"its label is '{component_info['label']}'")

    if not parts:
        return ""
        
    return "There is a nearby component, and " + ", and ".join(parts) + "."

def use_context_info_generate_prompt(jsondata: dict, screen_height: int, screen_width: int) -> str:
    """Constructs the final prompt for the T5 model based on component context."""
    
    # --- Basic Info ---
    app_name = turn_null_to_str(jsondata.get('app_name')).split('.')[-1]
    prompt = f"In the '{app_name}' app, there is an input field. "

    if jsondata.get('id'):
        purpose = jsondata['id'].split('/')[-1].replace('_', ' ')
        prompt += f"Its purpose seems to be '{purpose}'. "
    if jsondata.get('text'):
        prompt += f"It currently contains the text '{jsondata['text']}'. "
    
    # --- Contextual Info from Nearby Components ---
    nearby_info = ""
    if 'nearby-components' in jsondata:
        for component in jsondata['nearby-components']:
            info_str = format_component_info(component)
            if info_str:
                nearby_info += info_str + " "
    
    if nearby_info:
        prompt += "\nContext from nearby elements: " + nearby_info.strip()

    prompt += "\nQuestion: What is the most appropriate hint text for this input field?"
    return prompt


import re
import os

def parse_preference_index_moc(moc_file_path: str) -> dict:
    """
    Parses the content of the Preference_Index_MOC.md file to extract defined preferences.

    Args:
        moc_file_path: The full path to the Preference_Index_MOC.md file.

    Returns:
        A dictionary containing the parsed preferences.
    """
    preferences = {
        "behavioral_constraints": {},
        "content_prioritization": {"keywords_to_emphasize": [], "topics_to_prioritize": []},
        "output_structure_preferences": {},
        "source_prioritization": {"preferred_sources": []}
    }

    try:
        with open(moc_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Preference Index MOC not found at {moc_file_path}")
        return preferences

    current_section = None
    current_sub_section = None # To track nested lists like keywords/topics

    for line_num, line_content in enumerate(content.splitlines()):
        line = line_content.strip()
        if not line:
            continue

        if line.startswith("## Behavioral Constraints"):
            current_section = "behavioral_constraints"
            current_sub_section = None
        elif line.startswith("## Content Prioritization"):
            current_section = "content_prioritization"
            current_sub_section = None
        elif line.startswith("## Output Structure Preferences"):
            current_section = "output_structure_preferences"
            current_sub_section = None
        elif line.startswith("## Source Prioritization"):
            current_section = "source_prioritization"
            current_sub_section = None
        elif current_section:
            if line.startswith("- **Tone:**"):
                preferences[current_section]["tone"] = [t.strip() for t in line.replace("- **Tone:**", "").split(',')]
            elif line.startswith("- **Verbosity:**"):
                preferences[current_section]["verbosity"] = line.replace("- **Verbosity:**", "").strip()
            elif line.startswith("- **Audience:**"):
                preferences[current_section]["audience"] = line.replace("- **Audience:**", "").strip()
            elif line.startswith("- **Perspective:**"):
                preferences[current_section]["perspective"] = line.replace("- **Perspective:**", "").strip()
            elif line.startswith("- **Keywords to emphasize:**"):
                current_sub_section = "keywords_to_emphasize"
            elif line.startswith("- **Topics to prioritize:**"):
                current_sub_section = "topics_to_prioritize"
            elif line.startswith("- **Include Summary:**"):
                preferences[current_section]["include_summary"] = "Yes" in line
            elif line.startswith("- **Include Key Takeaways:**"):
                preferences[current_section]["include_key_takeaways"] = "Yes" in line
            elif line.startswith("- **Include Ambiguities/Contradictions:**"):
                preferences[current_section]["include_ambiguities_contradictions"] = "Yes" in line
            elif line.startswith("- **Reference Style:**"):
                preferences[current_section]["reference_style"] = line.replace("- **Reference Style:**", "").strip()
            elif line.startswith("- **Preferred sources:**"):
                pass # The actual list items are parsed below
            elif line.startswith("- "):
                if current_section == "content_prioritization":
                    if current_sub_section == "keywords_to_emphasize":
                        preferences[current_section]["keywords_to_emphasize"].append(line.replace("-", "").strip())
                    elif current_sub_section == "topics_to_prioritize":
                        preferences[current_section]["topics_to_prioritize"].append(line.replace("-", "").strip())
                elif current_section == "source_prioritization":
                    # This assumes the preferred sources are directly under "Preferred sources:" list
                    preferences[current_section]["preferred_sources"].append(line.replace("-", "").strip())
                
    return preferences


def parse_project_context(context_file_path: str) -> dict:
    """
    Parses the content of the PROJECT_VARIABLE.md file to extract configurations,
    including INI-style sections like [section.subsection].

    Args:
        context_file_path: The full path to the PROJECT_VARIABLE.md file.

    Returns:
        A dictionary containing the parsed project context settings.
    """
    context = {}

    try:
        with open(context_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Project Variable file not found at {context_file_path}")
        return context

    current_section = None
    current_ini_section_path = [] # To keep track of nested INI sections as a list of keys

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        # Handle ## Markdown headers (resets INI section context)
        if line.startswith("## "):
            current_section = line.replace("## ", "").strip().replace(' ', '_').lower()
            context[current_section] = {}
            current_ini_section_path = [] # Reset INI section context
        # Handle [INI-style sections] (e.g., [notion_templates.journals])
        elif line.startswith("[") and line.endswith("]"):
            current_ini_section_path = [part.strip().replace('-', '_').lower() for part in line[1:-1].split('.')]
            
            # Start building the nested dictionary structure from the current_section if it exists, otherwise from context root
            target_root_for_ini = context
            if current_section and current_section in context:
                target_root_for_ini = context[current_section]
            
            temp_ctx = target_root_for_ini
            for part in current_ini_section_path:
                temp_ctx = temp_ctx.setdefault(part, {})
            
        # Handle key = value pairs
        elif "=" in line:
            key, value = line.split("=", 1)
            key = key.strip().replace('-', '_').lower() # Convert to snake_case
            value = value.strip()
            
            target_dict = context
            # Navigate to the correct target dictionary for the key-value pair
            if current_section and current_section in context:
                target_dict = context[current_section]
                if current_ini_section_path:
                    for part in current_ini_section_path:
                        target_dict = target_dict.setdefault(part, {})
            elif current_ini_section_path: # Only INI section, no Markdown section parent
                for part in current_ini_section_path:
                    target_dict = target_dict.setdefault(part, {})
            else: # No active section, fall back to top-level context (shouldn't happen often for well-formed files)
                pass # Already target_dict = context

            # Store the key-value pair
            # If value is a comma-separated list, store as list
            if "," in value:
                target_dict[key] = [item.strip() for item in value.split(',')]
            else:
                target_dict[key] = value

        # Handle - **Key:** Value for Markdown sections (only if no INI section is active)
        elif line.startswith("- **") and current_section and not current_ini_section_path:
            match = re.match(r"- \*\*(.*?):\*\*\s*(.*)", line)
            if match:
                key = match.group(1).strip().replace(' ', '_').lower()
                value = match.group(2).strip()
                context[current_section][key] = value
    return context


def load_user_preferences(preferences_dir: str, moc_file_path: str) -> dict:
    """
    Loads and consolidates user preferences from the Preference Index MOC and individual preference files.

    Args:
        preferences_dir: The path to the directory containing individual preference Markdown files.
        moc_file_path: The full path to the Preference_Index_MOC.md file.

    Returns:
        A dictionary containing consolidated preferences.
    """
    # Start with structured preferences from the MOC
    consolidated_preferences = parse_preference_index_moc(moc_file_path)

    # Add content from individual preference files
    individual_preferences_content = []
    if os.path.exists(preferences_dir) and os.path.isdir(preferences_dir):
        for filename in os.listdir(preferences_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(preferences_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        individual_preferences_content.append(f.read())
                except Exception as e:
                    print(f"Warning: Could not read preference file {file_path}: {e}")
    
    # Combine individual preferences into a single string for LLM consumption
    # This unstructured text will be passed to the LLM to guide its understanding of preferences.
    if individual_preferences_content:
        consolidated_preferences["unstructured_preferences"] = "\n\n---\n\n".join(individual_preferences_content)
    else:
        consolidated_preferences["unstructured_preferences"] = ""


    return consolidated_preferences
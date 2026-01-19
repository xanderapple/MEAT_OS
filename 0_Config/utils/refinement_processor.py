import re
import os
import yaml
import datetime

# Assuming vault_root is the current working directory for simplicity in these utilities
# In main application, vault_root should be passed or derived from project context.

def _read_file_content(file_path: str) -> str:
    """Reads the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def _write_file_content(file_path: str, content: str) -> bool:
    """Writes content to a file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def _parse_suggestion_block(block_content: str) -> dict:
    """Parses key-value pairs from a suggestion block's content, handling multi-line content for 'CONTENT'."""
    suggestion_details = {}
    lines = block_content.splitlines()
    
    current_key = None
    current_content_lines = []

    for line in lines:
        line_stripped = line.strip()
        
        # Check for start of a new key-value pair
        # Regex handles:
        # **KEY**: VALUE (Colon outside)
        # **KEY:** VALUE (Colon inside)
        # **KEY": VALUE (Quote terminator from previous bug)
        # - **TITLE:** "Value" (Standard)
        key_match = re.match(r'- \*\*(.*?)(?:[\*"]+):?\s*(.*)', line_stripped)
        if key_match:
            # If we were collecting multi-line content for a previous key, save it
            if current_key is not None and current_content_lines:
                # Remove leading/trailing empty lines, but preserve internal ones
                while current_content_lines and not current_content_lines[0].strip():
                    current_content_lines.pop(0)
                while current_content_lines and not current_content_lines[-1].strip():
                    current_content_lines.pop(-1)
                suggestion_details[current_key] = "\n".join(current_content_lines)
                current_content_lines = [] # Reset for next content

            current_key = key_match.group(1).strip().replace(' ', '_').upper()
            # Clean up key if it has trailing chars like " or :
            current_key = current_key.rstrip('":')
                
            initial_value = key_match.group(2).strip()
            
            if initial_value:
                # If the value is wrapped in quotes, unwrap them slightly to handle the \n literals if needed
                if initial_value.startswith('"') and initial_value.endswith('"'):
                     # Remove surrounding quotes and unescape \n
                     # Simple unescape for basic cases
                     initial_value = initial_value[1:-1].replace('\\n', '\n')
                
                suggestion_details[current_key] = initial_value
                current_key = None # Not expecting multi-line content for this key
            
            if initial_value:
                # Check for multi-line quoted string starting on this line
                if initial_value.startswith('"') and not initial_value.endswith('"'):
                    # Start of multi-line quoted string
                    current_content_lines.append(initial_value)
                    # current_key remains set, so we continue collecting lines
                else:
                    # Single line value (quoted or unquoted)
                    # Clean up quotes if present
                    if initial_value.startswith('"') and initial_value.endswith('"'):
                         initial_value = initial_value[1:-1].replace('\\n', '\n')
                    
                    suggestion_details[current_key] = initial_value
                    current_key = None # Value complete
            # If initial value is empty, current_key is set, and subsequent lines will be collected (existing logic)
            # If initial value is empty, current_key is set, and subsequent lines will be collected
        elif current_key is not None: # If we are in multi-line collection mode
            current_content_lines.append(line) # Append the original line (not stripped) to preserve indentation for content

    # After loop, save any remaining collected multi-line content
    if current_key is not None and current_content_lines:
        # Remove leading/trailing empty lines, but preserve internal ones
        while current_content_lines and not current_content_lines[0].strip():
            current_content_lines.pop(0)
        while current_content_lines and not current_content_lines[-1].strip():
            current_content_lines.pop(-1)
        suggestion_details[current_key] = "\n".join(current_content_lines)

    return suggestion_details

def _add_to_update_history(file_content: str, section_name: str, old_content: str, source_file_path: str) -> str:
    """
    Adds old content of a section to an "Update History" section at the end of the note.
    Creates the "Update History" section if it doesn't exist.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Make a wikilink to the refinement analysis file
    source_link_target = os.path.splitext(os.path.basename(source_file_path))[0]
    source_link = f"[[{source_link_target}]]" # Assuming it's in a discoverable path for Obsidian
    
    history_entry = f"""
### Update to "{section_name}" on {timestamp}
Source: {source_link}

```markdown
{old_content.strip()}
```
"""
    # Regex to find the Update History section, capture its content
    update_history_pattern = re.compile(r'(## Update History\s*\n)(.*)', re.DOTALL)
    history_match = update_history_pattern.search(file_content)

    if history_match:
        # Prepend to existing history entries (after the heading)
        # Find the end of the history heading and insert the new entry
        start_of_history_content = history_match.start(2)
        return file_content[:start_of_history_content] + history_entry + "\n" + file_content[start_of_history_content:]
    else:
        # Create new history section at the very end of the file
        return file_content.strip() + f"\n\n## Update History\n{history_entry}"


def parse_refinement_analysis(refinement_analysis_content: str) -> tuple[list[dict], str, str]:
    """
    Parses the Markdown content of the Refinement Analysis and extracts:
    1. Actionable suggestions (UPDATE_NOTE, CREATE_NOTE, UPDATE_MOC)
    2. Content of "Direct Contradictions/Discrepancies"
    3. Content of "Ambiguities/Questions"
    
    Returns a tuple: (suggestions: list[dict], contradictions: str, ambiguities: str)
    """
    suggestions = []
    contradictions = ""
    ambiguities = ""

    # Capture main sections for contradictions and ambiguities first
    # This also helps to isolate the 'Integration Opportunities' section later
    contradiction_section_match = re.search(
        r'(## Direct Contradictions/Discrepancies\s*\n.*?)(?=\n##|$)', 
        refinement_analysis_content, re.DOTALL
    )
    if contradiction_section_match:
        contradictions = contradiction_section_match.group(1).strip()
    
    ambiguity_section_match = re.search(
        r'(## Ambiguities/Questions\s*\n.*?)(?=\n##|$)', 
        refinement_analysis_content, re.DOTALL
    )
    if ambiguity_section_match:
        ambiguities = ambiguity_section_match.group(1).strip()

    # Extract Integration Opportunities section to then parse suggestions
    # Simplified approach: Find the start of the section and parse everything after it
    integration_start_match = re.search(
        r'(?:##|###\s*\d+\.)\s*Integration Opportunities \(Actionable Steps for Gemini CLI\)',
        refinement_analysis_content
    )
    
    if integration_start_match:
        # Start parsing from the end of the header
        integration_content_to_parse = refinement_analysis_content[integration_start_match.end():]

        # Optional: If the content is wrapped in a single huge markdown block, try to unwrap it
        # This check is simple: if it starts with ```markdown and ends with ```, strip them.
        # But we need to be careful not to strip internal code blocks if the whole thing isn't wrapped.
        # Given the variety, it's safer to just parse the raw content, as the regex for suggestions
        # (### TYPE:...) is unlikely to trigger falsely inside a normal code block description unless
        # the description is quoting a suggestion, which is rare.
        
        # Regex to find structured blocks within the content
        suggestion_block_pattern = re.compile(
            r'###\s*(UPDATE_NOTE|CREATE_NOTE|UPDATE_MOC):\s*(.+?\.md)\s*\n(.*?)(?=\n###|\Z)', 
            re.DOTALL
        )
        
        for match in suggestion_block_pattern.finditer(integration_content_to_parse):
            full_block = match.group(0) # Get the full matched block
            header_match = re.match(r'###\s*(UPDATE_NOTE|CREATE_NOTE|UPDATE_MOC):(.+?\.md)', full_block) # Re-match header
            if header_match:
                suggestion_type = header_match.group(1)
                file_path = header_match.group(2).strip()
                block_content = full_block[header_match.end(0):].strip() # Content after header
                
                suggestion_details = _parse_suggestion_block(block_content)
                
                suggestions.append({
                    'type': suggestion_type,
                    'target_file': file_path,
                    **suggestion_details
                })

        
    return suggestions, contradictions, ambiguities

def execute_refinement_suggestion(suggestion: dict, vault_root: str, refinement_analysis_file_path: str) -> None: # Added refinement_analysis_file_path
    """
    Executes a single parsed refinement suggestion.
    """
    suggestion_type = suggestion.get('type')
    target_file_relative = suggestion.get('target_file')
    full_target_file_path = os.path.join(vault_root, target_file_relative)

    print(f"Executing {suggestion_type} for {target_file_relative}...")

    if suggestion_type == "UPDATE_NOTE":
        section = suggestion.get('SECTION')
        action = suggestion.get('ACTION')
        content_to_add_or_replace = suggestion.get('CONTENT_TO_ADD/REPLACE', '')
        
        if not all([section, action, content_to_add_or_replace]):
            print(f"Warning: Incomplete UPDATE_NOTE suggestion for {target_file_relative}. Skipping.")
            return

        existing_content = _read_file_content(full_target_file_path)
        if not existing_content:
            print(f"Error: Could not read {full_target_file_path} for UPDATE_NOTE. Skipping.")
            return
        
        updated_content_for_note = existing_content # Use a new variable for content being updated

        # Citation for the new content
        source_link_target = os.path.splitext(os.path.basename(refinement_analysis_file_path))[0]
        citation = f"\n\n^(Source: [[{source_link_target}]])"

        if section.upper() == "FRONTMATTER":
            frontmatter_match = re.match(r'---\s*\n(.*?)\n---\s*\n(.*)', existing_content, re.DOTALL)
            if frontmatter_match:
                frontmatter_str = frontmatter_match.group(1)
                body_content = frontmatter_match.group(2)
                try:
                    frontmatter_data = yaml.safe_load(frontmatter_str)
                    if frontmatter_data is None: frontmatter_data = {}
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML frontmatter in {target_file_relative}: {e}. Skipping frontmatter update.")
                    return
                
                try:
                    update_data = yaml.safe_load(content_to_add_or_replace)
                    if not isinstance(update_data, dict):
                        print(f"Warning: CONTENT_TO_ADD/REPLACE for FRONTMATTER is not valid YAML dict. Skipping.")
                        return
                    
                    # Store old frontmatter before updating for history
                    old_frontmatter_content = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    
                    frontmatter_data.update(update_data)
                    new_frontmatter_str = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    updated_content_for_note = f"---\n{new_frontmatter_str}---\n{body_content}"
                    
                    # Add old frontmatter to history
                    updated_content_for_note = _add_to_update_history(updated_content_for_note, f"FRONTMATTER", old_frontmatter_content, refinement_analysis_file_path)

                except yaml.YAMLError as e:
                    print(f"Error parsing CONTENT_TO_ADD/REPLACE for FRONTMATTER in {target_file_relative}: {e}. Skipping.")
                    return
            else:
                print(f"Warning: No frontmatter found in {target_file_relative}. Cannot update FRONTMATTER section. Skipping.")
                return
        else:
            # Section-based update (Handles H1 to H6)
            # This regex captures the section heading and its content until the next heading of same or higher level, or end of file
            section_heading_pattern = re.compile(rf"(^#{{1,6}}\s*{re.escape(section)}\s*\n)(.*?)(?=\n#{{1,6}} |\Z)", re.DOTALL | re.MULTILINE)
            section_match = section_heading_pattern.search(existing_content)

            current_section_content = ""
            if section_match:
                section_start_marker = section_match.group(1)
                current_section_content = section_match.group(2)
            else:
                section_start_marker = f"## {section}\n" # If section not found, assume H2
                
            # Add existing section content to history BEFORE modifying
            updated_content_for_note = _add_to_update_history(updated_content_for_note, section, current_section_content, refinement_analysis_file_path)

            if action == "ADD_CONTENT":
                new_section_content = current_section_content.strip() + "\n\n" + content_to_add_or_replace + citation
                # Replace the content of the matched section, keeping the heading intact
                if section_match:
                    updated_content_for_note = section_heading_pattern.sub(f"{section_start_marker}{new_section_content.strip()}\n", existing_content)
                else:
                    # Append new section and its content
                    updated_content_for_note += f"\n\n{section_start_marker}{new_section_content.strip()}\n"
            elif action == "REPLACE_SECTION":
                # Replace the entire section content
                if section_match:
                    updated_content_for_note = section_heading_pattern.sub(f"{section_start_marker}{content_to_add_or_replace.strip()}{citation}\n", existing_content)
                else:
                    # Append new section and its content
                    updated_content_for_note += f"\n\n{section_start_marker}{content_to_add_or_replace.strip()}{citation}\n"
            else:
                print(f"Warning: Unknown action '{action}' for UPDATE_NOTE section '{section}'. Skipping.")
                return

        if _write_file_content(full_target_file_path, updated_content_for_note):
            print(f"Successfully updated note: {target_file_relative}")

    elif suggestion_type == "CREATE_NOTE":
        title = suggestion.get('TITLE')
        content = suggestion.get('CONTENT')
        tags_str = suggestion.get('TAGS', '')
        
        # --- Atomic Note Creation for Values Logic ---
        # Detect if this is a value summary note (e.g., PKM_Integration_Values_and_Preferences.md)
        if target_file_relative.startswith("2_Literature_Notes/Personal/Values/") and "values" in target_file_relative.lower():
            print(f"Detected potential value summary note: {target_file_relative}. Attempting atomic breakdown...")
            
            # Try to parse content as Markdown list items or table rows
            atomic_value_pattern = re.compile(r'^- \*\*(.*?):\*\*\s*(.*)|\*\*([^\*]+?)\*\*:\s*(.*)', re.MULTILINE) # Matches bolded list items or bolded phrases
            table_row_pattern = re.compile(r'\|\s*\*\*([^\*]+?)\*\*\s*\|\s*(.*?)\s*\|', re.MULTILINE) # Matches bolded item in first column of a table
            
            extracted_atomic_values = []

            # First, try to parse from a Markdown table in the content (from Value Synthesis)
            # Regex updated to match 4 columns: Value | Aliases | Context | Implication
            table_match = re.search(r'\| Value \/ Preference \| Aliases \| Context \/ Source \| Strategic Implication \|\n\|:---|:---|:---|:---|\n(.*?)(?=\n\||---|$)', content, re.DOTALL)
            if table_match:
                table_body = table_match.group(1)
                for line in table_body.splitlines():
                    # Match 4 columns. Note: content might be empty for Aliases
                    row_match = re.match(r'\|\s*\*\*(.*?)\*\*\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', line)
                    if row_match:
                        value_name = row_match.group(1).strip()
                        aliases_str = row_match.group(2).strip()
                        value_description = f"Context: {row_match.group(3).strip()}\nStrategic Implication: {row_match.group(4).strip()}"
                        if value_name:
                            extracted_atomic_values.append({'name': value_name, 'aliases': aliases_str, 'description': value_description})
            
            # Fallback to Markdown list if no table or if table parsing failed (old format support)
            if not extracted_atomic_values:
                for match in atomic_value_pattern.finditer(content):
                    value_name = (match.group(1) or match.group(3)).strip()
                    value_description = (match.group(2) or match.group(4)).strip()
                    if value_name:
                        extracted_atomic_values.append({'name': value_name, 'aliases': '', 'description': value_description})
            
            if extracted_atomic_values:
                print(f"Found {len(extracted_atomic_values)} atomic values. Creating individual notes...")
                for atomic_value in extracted_atomic_values:
                    atomic_value_name = atomic_value['name']
                    atomic_value_description = atomic_value['description']
                    atomic_aliases = atomic_value.get('aliases', '')
                    sanitized_value_name = re.sub(r'[^\w\-_\. ]', '', atomic_value_name).replace(' ', '_')

                    # Prepare frontmatter with aliases
                    new_frontmatter = {'title': atomic_value_name}
                    if tags_str:
                        new_frontmatter['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]
                    if atomic_aliases:
                        new_frontmatter['aliases'] = [a.strip() for a in atomic_aliases.split(',') if a.strip()]
                    
                    frontmatter_block = yaml.dump(new_frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)

                    # Create a new CREATE_NOTE suggestion for each atomic value
                    atomic_note_suggestion = {
                        'type': 'CREATE_NOTE',
                        'target_file': f"2_Literature_Notes/Personal/Values/{sanitized_value_name}.md",
                        'TITLE': atomic_value_name,
                        'CONTENT': f"---\n{frontmatter_block}---\n# {atomic_value_name}\n\n{atomic_value_description}\n\n^(Source: [[{os.path.basename(refinement_analysis_file_path).replace('.md', '')}]])\n",
                        'TAGS': '' # Tags handled in frontmatter block manual creation
                    }
                    print(f"  -> Generating atomic note for: {atomic_value_name} (Aliases: {atomic_aliases})")
                    execute_refinement_suggestion(atomic_note_suggestion, vault_root, refinement_analysis_file_path)
                
                print(f"Skipping creation of original grouped note: {target_file_relative}")
                return # Skip creating the grouped note
        # --- End Atomic Note Creation for Values Logic ---

        if not all([title, content]):
            print(f"Warning: Incomplete CREATE_NOTE suggestion for {target_file_relative}. Skipping.")
            return
        
        tags_list = [t.strip() for t in tags_str.split(',') if t.strip()]

        # Ensure directory exists for the new note
        os.makedirs(os.path.dirname(full_target_file_path), exist_ok=True)
        
        frontmatter_data = {}
        if title: frontmatter_data['title'] = title
        if tags_list: frontmatter_data['tags'] = tags_list
        
        frontmatter_str = ""
        if frontmatter_data:
            try:
                frontmatter_str = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            except yaml.YAMLError as e:
                print(f"Error dumping YAML for new note {target_file_relative}: {e}")
                frontmatter_str = "" # Fallback to no frontmatter if error

        note_content = ""
        if frontmatter_str:
            note_content += f"---\n{frontmatter_str}---\n"
        note_content += f"# {title}\n\n{content}"
        
        if _write_file_content(full_target_file_path, note_content):
            print(f"Successfully created new note: {target_file_relative}")
            # Potentially trigger MOC update here if it's a new atomic note

    elif suggestion_type == "UPDATE_MOC":
        section = suggestion.get('SECTION')
        action = suggestion.get('ACTION')
        link_target = suggestion.get('LINK_TARGET')
        link_display_text = suggestion.get('LINK_DISPLAY_TEXT')

        if not all([section, action, link_target, link_display_text]):
            print(f"Warning: Incomplete UPDATE_MOC suggestion for {target_file_relative}. Skipping.")
            return

        existing_moc_content = _read_file_content(full_target_file_path)
        if not existing_moc_content:
            print(f"Error: Could not read {full_target_file_path} for UPDATE_MOC. Skipping.")
            return

        updated_moc_content = existing_moc_content
        
        if action == "ADD_LINK":
            section_heading_pattern = re.compile(rf"(^#{{1,6}}\s*{re.escape(section)}\s*\n)(.*?)(?=\n#{{1,6}} |\Z)", re.DOTALL | re.MULTILINE)
            section_match = section_heading_pattern.search(existing_moc_content)

            new_link = f"- [[{link_target}|{link_display_text}]]"

            if section_match:
                section_start_marker = section_match.group(1)
                existing_section_content = section_match.group(2)
                
                # Check if the link already exists in the section
                # Use a more robust check to find the link within existing_section_content
                if re.search(re.escape(new_link), existing_section_content, re.DOTALL) is None: 
                    # Replace the content of the matched section with new content including the link
                    # Ensure new_section_content preserves existing structure and adds new link appropriately
                    # This might need refinement for list items vs. paragraphs. For now, simple append.
                    new_section_content_with_link = existing_section_content.strip() + "\n" + new_link
                    updated_moc_content = section_heading_pattern.sub(f"{section_start_marker}{new_section_content_with_link.strip()}\n", existing_moc_content)
                    if _write_file_content(full_target_file_path, updated_moc_content):
                        print(f"Successfully added link to MOC: {target_file_relative} in section '{section}'")
                else:
                    print(f"Link '{new_link}' already exists in {target_file_relative}. Skipping.")
            else:
                print(f"Warning: Section '{section}' not found in {full_target_file_path} for UPDATE_MOC. Appending to end.")
                # If section not found, append to the end for now
                updated_moc_content += f"\n\n## {section}\n{new_link}"
                if _write_file_content(full_target_file_path, updated_moc_content):
                    print(f"Successfully added link to MOC: {target_file_relative}")
        else:
            print(f"Warning: Unknown action '{action}' for UPDATE_MOC. Skipping.")

    else:
        print(f"Warning: Unknown suggestion type '{suggestion_type}'. Skipping.")

def process_refinement_analysis_file(refinement_analysis_file_path: str, vault_root: str) -> None:
    """
    Orchestrates the parsing and execution of suggestions from a Refinement Analysis file.
    """
    print(f"Processing refinement analysis file: {refinement_analysis_file_path}")
    content = _read_file_content(refinement_analysis_file_path)
    if not content:
        print("Error: Refinement analysis file is empty or could not be read.")
        return
    
    suggestions, contradictions, ambiguities = parse_refinement_analysis(content)
    
    if not suggestions:
        print("No actionable suggestions found in the refinement analysis.")
        
    for suggestion in suggestions:
        execute_refinement_suggestion(suggestion, vault_root, refinement_analysis_file_path) # Pass the file path
        
    if contradictions:
        print("\n--- Identified Contradictions ---")
        print(contradictions)
    
    if ambiguities:
        print("\n--- Identified Ambiguities/Questions ---")
        print(ambiguities)

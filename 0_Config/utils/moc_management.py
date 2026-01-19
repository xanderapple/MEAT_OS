import re
import os
import yaml # <--- Add this import

def parse_gemini_index_moc(moc_content: str, moc_file_path: str) -> dict:
    """
    Parses the content of a MOC file to extract a mapping of
    note titles/wikilinks to their full file paths.

    Args:
        moc_content: The full content of the MOC file.
        moc_file_path: The path of the MOC file itself, relative to the vault root.

    Returns:
        A dictionary where keys are note titles (from wikilinks) and values are
        their corresponding file paths (relative to vault root, without .md extension).
    """
    note_map = {}
    wikilink_pattern = re.compile(r'\[\[(.*?)\]\]')
    
    moc_base_dir = os.path.dirname(moc_file_path)

    for line in moc_content.splitlines():
        matches = wikilink_pattern.findall(line)
        for match in matches:
            parts = match.split('|')
            linked_content = parts[0] # This is the part with the path or just title

            note_title = os.path.splitext(os.path.basename(linked_content))[0]
            
            # Normalize path separators for consistency
            normalized_linked_content = linked_content.replace('/', os.sep).replace('\\', os.sep)

            # Join the base directory of the MOC with the linked content path
            # and then normalize it to resolve '..'
            full_path = os.path.normpath(os.path.join(moc_base_dir, normalized_linked_content))
            
            # The result should be a path relative to the vault root, without '.md'
            # Assuming the script is run from the vault root.
            note_map[note_title] = full_path.replace('.md', '') # Also remove extension from path
            
    return note_map

def list_markdown_files(vault_root: str) -> list[tuple[str, dict]]:
    """
    Lists all Markdown files in the vault, excluding specified directories,
    and extracts their frontmatter metadata and a concise summary if available.

    Args:
        vault_root: The root directory of the Obsidian vault.

    Returns:
        A list of tuples: (relative_path, metadata_dict), sorted alphabetically by path.
        metadata_dict includes 'tags', 'aliases', and 'summary_text' if found.
    """
    markdown_files = []
    
    # Directories to ignore
    ignore_dirs = ['.obsidian', '.git', 'Templates', '.trash'] 

    for root, dirs, files in os.walk(vault_root):
        # Modify dirs in-place to prune the search
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, vault_root)
                
                metadata = {}
                summary_text = ""

                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read() # Read full content to extract summary effectively
                        
                        yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                        if yaml_match:
                            try:
                                frontmatter = yaml.safe_load(yaml_match.group(1))
                                if frontmatter is None: frontmatter = {}
                                metadata.update(frontmatter) # Add frontmatter to metadata
                            except yaml.YAMLError:
                                pass # Ignore YAML errors for now
                    
                    # Try to extract summary from frontmatter first
                    if metadata.get('summary'):
                        summary_text = metadata['summary']
                    
                    # If it's a chat log and no summary in frontmatter, try to find associated Refinement_Analysis
                    if not summary_text and relative_path.startswith("1_Fleeting_Notes/Capture/Chat_Logs/"):
                        # Extract date and sanitized title from the filename
                        # Filename example: YYYY-MM-DD_SanitizedTitle.md
                        filename_parts = os.path.basename(relative_path).split('_', 1) # Split only on first underscore
                        if len(filename_parts) > 1:
                            date_str = filename_parts[0]
                            # Remove .md and extension, then sanitize
                            sanitized_title = os.path.splitext(filename_parts[1])[0]
                            
                            # Construct expected Refinement_Analysis filename
                            expected_analysis_filename = f"Refinement_Analysis-{date_str}-{sanitized_title}.md"
                            analysis_path = os.path.join(vault_root, "2_Literature_Notes/Experience/Chat_Synthesis", expected_analysis_filename)
                            
                            if os.path.exists(analysis_path):
                                analysis_content = ""
                                try:
                                    with open(analysis_path, 'r', encoding='utf-8') as af:
                                        analysis_content = af.read()
                                    
                                    # Try to extract 'Summary' or 'Key Takeaways' from Refinement Analysis
                                    summary_match = re.search(r'### Summary\n(.*?)(?=\n###|\Z)', analysis_content, re.DOTALL)
                                    if summary_match:
                                        summary_text = summary_match.group(1).strip().split('\n')[0] # Take only the first line as summary
                                    else:
                                        key_takeaways_match = re.search(r'### Key Takeaways\n(.*?)(?=\n###|\Z)', analysis_content, re.DOTALL)
                                        if key_takeaways_match:
                                            summary_text = key_takeaways_match.group(1).strip().split('\n')[0] # Take only the first line as summary
                                except Exception:
                                    pass # Ignore errors reading analysis file
                except Exception:
                    pass # Ignore file reading errors
                
                if summary_text:
                    metadata['summary_text'] = summary_text

                markdown_files.append((relative_path, metadata))
    
    markdown_files.sort(key=lambda x: x[0])
    return markdown_files


def generate_moc_markdown(markdown_files: list[tuple[str, dict]]) -> str:
    """
    Generates a hierarchical Markdown string from a list of Markdown files with metadata,
    mirroring the folder structure with headers and wikilinks appended with tags/aliases/summary.

    Args:
        markdown_files: A list of tuples (relative_path, frontmatter_dict).

    Returns:
        A Markdown string representing the hierarchical structure.
    """
    
    # Revised Hierarchy Builder
    root_node = {}

    for f_path, metadata in markdown_files:
        parts = os.path.splitext(f_path)[0].split(os.sep)
        current = root_node
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            
            if part not in current:
                if is_last:
                    current[part] = {"__type__": "FILE", "metadata": metadata, "children": {}}
                else:
                    current[part] = {"__type__": "FOLDER", "children": {}}
            
            # Navigate down
            node = current[part]
            
            # Update type if we find a folder that matches an existing file name (Note vs Note/Subnote)
            if is_last:
                node["__type__"] = "FILE" # Mark as file (it might also have children later)
                node["metadata"] = metadata
            
            current = node["children"]

    markdown_output_lines = ["# GEMINI_INDEX", "", "This is a master index of the permanent notes in your second brain, created and maintained by Gemini. I use this file as my primary reference point to understand the structure and content of your vault efficiently.", ""]

    # Recursive Printer
    def print_node(node_dict, level, prefix=""):
        sorted_keys = sorted(node_dict.keys())
        
        for key in sorted_keys:
            node = node_dict[key]
            full_path_segment = os.path.join(prefix, key)
            display_name = key.replace('_', ' ')
            
            # Print header or item
            if node.get("__type__") == "FILE":
                # Format metadata
                meta = node.get("metadata", {})
                meta_str = ""
                tags = meta.get('tags')
                aliases = meta.get('aliases')
                summary = meta.get('summary_text') # Get summary_text
                
                extras = []
                if tags:
                    if isinstance(tags, list):
                        extras.append(f"Tags: {', '.join(str(t) for t in tags)}")
                    else:
                        extras.append(f"Tags: {tags}")
                if aliases:
                    if isinstance(aliases, list):
                        extras.append(f"Aliases: {', '.join(aliases)}")
                    else:
                        extras.append(f"Aliases: {aliases}")
                if summary: # Append summary to extras
                    extras.append(f"Summary: {summary}")
                
                if extras:
                    meta_str = f" -- { ' | '.join(extras)}"
                else: # Only if extras list is empty, but summary might be there alone
                    if summary:
                        meta_str = f" -- Summary: {summary}"

                markdown_output_lines.append(f"{ '  ' * (level)}- [[{full_path_segment}|{display_name}]]{meta_str}")
            else:
                # It's purely a folder
                header_level = min(level + 2, 6) # ##, ###, ...
                header_hashes = '#' * header_level
                markdown_output_lines.append(f"\n{header_hashes} {display_name}")

            # Recursively print children
            if node["children"]:
                print_node(node["children"], level + 1, full_path_segment)

    print_node(root_node, 0)
    return "\n".join(line for line in markdown_output_lines if line.strip() != "")


def update_gemini_index_moc(vault_root: str, output_moc_path: str = "0_Config/GEMINI_INDEX.md") -> None:
    """
    Orchestrates the process of updating the Gemini_Index_MOC.md file.
    Lists all Markdown files with metadata, generates the hierarchical Markdown content,
    and writes it to the specified MOC file.

    Args:
        vault_root: The root directory of the Obsidian vault.
        output_moc_path: The path where the Gemini_Index_MOC.md should be written,
                         relative to the vault_root.
    """
    print(f"Updating {output_moc_path}...")
    markdown_files = list_markdown_files(vault_root)
    generated_moc_content = generate_moc_markdown(markdown_files)

    full_output_path = os.path.join(vault_root, output_moc_path)
    os.makedirs(os.path.dirname(full_output_path), exist_ok=True)

    try:
        with open(full_output_path, 'w', encoding='utf-8') as f:
            f.write(generated_moc_content)
        print(f"Successfully updated {output_moc_path}")
    except Exception as e:
        print(f"Error writing to {output_moc_path}: {e}")

def update_preference_index_moc(vault_root: str, preferences_dir: str = "3_Permanent_Notes/Personal/Preferences/", output_moc_path: str = "4_Map_of_Content/Preference_Index_MOC.md") -> None:
    """
    Updates the Preference_Index_MOC.md file by dynamically generating a table
    of preferences from individual preference notes.

    Args:
        vault_root: The root directory of the Obsidian vault.
        preferences_dir: The directory containing individual preference Markdown files.
        output_moc_path: The path where the Preference_Index_MOC.md should be written,
                         relative to the vault_root.
    """
    print(f"Updating {output_moc_path}...")
    
    full_preferences_dir = os.path.join(vault_root, preferences_dir)
    preferences_data = []

    if os.path.exists(full_preferences_dir) and os.path.isdir(full_preferences_dir):
        file_list = [f for f in os.listdir(full_preferences_dir) if f.endswith(".md")]
        
        for filename in file_list:
            file_path = os.path.join(full_preferences_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            yaml_match = re.match(r"---(.*?)---(.*)", content, re.DOTALL)
            frontmatter = {}
            body = content
            if yaml_match:
                yaml_str = yaml_match.group(1)
                try:
                    frontmatter = yaml.safe_load(yaml_str)
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML in {filename}: {e}")
                    continue
                body = yaml_match.group(2)
            
            # Extract Title (h1)
            title_match = re.search(r"^#\s*(.*)", body, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else filename.replace(".md", "").replace("_", " ")

            action = ""
            # Attempt 1: Look for **Action:** or Action:
            action_match_inline = re.search(r'^(?:\*\*)?Action:\s*(?:\*\*)?\s*(.*)', body, re.MULTILINE | re.IGNORECASE)
            if action_match_inline:
                action = action_match_inline.group(1).strip()
            else:
                # Attempt 2: Look for ## Action header and the line immediately following
                header_action_match = re.search(r'^##\s*Action\s*\n(?!#)(.*)', body, re.MULTILINE | re.IGNORECASE)
                if header_action_match:
                    action = header_action_match.group(1).strip()

            preferences_data.append({
                'filename': filename,
                'title': title,
                'action': action,
                'value': frontmatter.get('value', 'N/A'),
                'effort': frontmatter.get('effort', 'N/A')
            })
    
    preferences_data.sort(key=lambda x: x['filename'])

    # Generate Markdown table
    markdown_table = """<!-- GEMINI_AUTO_GENERATED_PREFERENCES_START -->
| Preference | Action | Value | Effort |
|:---|:---|:---|:---|
"""

    for p in preferences_data:
        wikilink_target = p['filename'].replace('.md', '')
        wikilink = f"[[{preferences_dir}/{wikilink_target}|{p['title']}]]"
        markdown_table += f"| {wikilink} | {p['action']} | {p['value']} | {p['effort']} |\n"
    markdown_table += "<!-- GEMINI_AUTO_GENERATED_PREFERENCES_END -->"

    # Read the existing MOC content
    full_output_moc_path = os.path.join(vault_root, output_moc_path)
    existing_moc_content = ""
    try:
        with open(full_output_moc_path, 'r', encoding='utf-8') as f:
            existing_moc_content = f.read()
    except FileNotFoundError:
        print(f"Error: {output_moc_path} not found. Creating a new one.")
        # Create a basic structure if not found
        existing_moc_content = """---
Tags: moc, preference, config
---

# Preference Index MOC

This MOC serves as the active configuration file for guiding the RAG synthesis process.

## Value-Driven Priorities (Dynamic List)

"""

    # Replace content between markers or append if markers not found
    start_marker = "<!-- GEMINI_AUTO_GENERATED_PREFERENCES_START -->"
    end_marker = "<!-- GEMINI_AUTO_GENERATED_PREFERENCES_END -->"

    if start_marker in existing_moc_content and end_marker in existing_moc_content:
        # Replace existing block
        new_moc_content = re.sub(
            f"{re.escape(start_marker)}.*{re.escape(end_marker)}",
            markdown_table,
            existing_moc_content,
            flags=re.DOTALL
        )
    else:
        # Append to the end of the "Value-Driven Priorities (Dynamic List)" section
        # Ensure the section header exists
        if "## Value-Driven Priorities (Dynamic List)" not in existing_moc_content:
            existing_moc_content += "\n## Value-Driven Priorities (Dynamic List)\n"
        
        # Insert just before any subsequent H2 or at the end of the file
        insert_index_match = re.search(r"## Value-Driven Priorities \(Dynamic List\)\s*\n(.*?)(\n##|\Z)", existing_moc_content, re.DOTALL)
        if insert_index_match:
            insert_point = insert_index_match.end(1) # End of the content within the section
            new_moc_content = existing_moc_content[:insert_point].rstrip() + "\n\n" + markdown_table + existing_moc_content[insert_index_match.end(2) if insert_index_match.group(2) else len(existing_moc_content):]
        else:
            new_moc_content = existing_moc_content.rstrip() + "\n\n" + markdown_table
    
    os.makedirs(os.path.dirname(full_output_moc_path), exist_ok=True)
    try:
        with open(full_output_moc_path, 'w', encoding='utf-8') as f:
            f.write(new_moc_content)
        print(f"Successfully updated {output_moc_path}")
    except Exception as e:
        print(f"Error writing to {output_moc_path}: {e}")

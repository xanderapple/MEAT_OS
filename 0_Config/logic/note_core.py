import os
import datetime
import re
import yaml
from ..utils.command_utils import sanitize_filename

def create_atomic_note(content: str, title: str = None, tags: str = None, directory: str = "3_Permanent_Notes") -> (bool, str, str):
    """
    Core logic for creating an atomic note.
    Returns (success: bool, message: str, file_path: str).
    """
    # Generate title if not provided
    if not title:
        title = content.split('\n')[0][:50].strip() 
        if title.startswith('# '):
            title = title[2:].strip()
        if not title: # Fallback for empty content
            title = "Untitled Note"
    
    # Generate filename
    safe_title = sanitize_filename(title)
    filename = f"{safe_title}.md"
    
    note_path = os.path.join(directory, filename)
    
    # Construct YAML frontmatter
    frontmatter_tags = ""
    if tags:
        frontmatter_tags = "\n".join([f"  - {tag.strip()}" for tag in tags.split(',')])

    # Standardized to date-only
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # Smart Header: Only add H1 if content doesn't start with one
    header_block = ""
    if not content.strip().startswith("# "):
        header_block = f"# {title}\nCreated on [[{current_date}]]\n\n"

    frontmatter = f"""---
Tags:
{frontmatter_tags}
Aliases: []
Created: {current_date}
---

{header_block}{content}

---
## References
"""
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)

    # Write the note
    try:
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        return True, f"Successfully created note: {note_path}", note_path
    except Exception as e:
        return False, f"Error creating note at {note_path}: {e}", ""

from .note_history import trim_note_history

def edit_existing_note(file_path: str, content: str, mode: str, title: str = None) -> (bool, str, str):
    """
    Core orchestrator for modifying existing notes.
    """
    if not os.path.exists(file_path):
        return False, f"Error: File not found at {file_path}", ""

    current_date = datetime.date.today().strftime("%Y-%m-%d")
    success = False
    message = ""

    if mode == "prepend_to_file":
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_content = f.read()

            final_title = title
            # YAML extraction
            yaml_pattern = re.compile(r'^(---.*?---)', re.DOTALL)
            match = yaml_pattern.match(full_content)
            
            if not final_title:
                if match:
                    yaml_content = match.group(1)
                    metadata = yaml.safe_load(yaml_content[3:-3]) or {}
                    final_title = metadata.get('title')
                
                if not final_title:
                    final_title = os.path.splitext(os.path.basename(file_path))[0]

            new_section = f"# {final_title}\nEdited on [[{current_date}]]\n\n{content}"

            if match:
                yaml_block = match.group(1)
                remaining_content = full_content[match.end():].strip()
                
                # History Trimming Logic
                version_pattern = re.compile(r'(Edited on \[\[\d{4}-\d{2}-\d{2}\]\])', re.DOTALL)
                versions = version_pattern.split(remaining_content)
                
                actual_versions = []
                if versions[0].strip():
                    actual_versions.append(versions[0].strip())
                
                for i in range(1, len(versions), 2):
                    actual_versions.append(versions[i] + versions[i+1])

                if len(actual_versions) >= 2:
                    note_name = os.path.splitext(os.path.basename(file_path))[0]
                    trim_success, trim_msg = trim_note_history(file_path, actual_versions, note_name)
                    if trim_success:
                        print(trim_msg)

                remaining_content = "\n\n".join(actual_versions).strip()
                new_full_content = f"{yaml_block}\n\n{new_section}\n\n{remaining_content}"
            else:
                new_full_content = f"{new_section}\n\n{full_content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_full_content)
            
            success = True
            message = f"Successfully prepended content (rephrased) to {file_path}."
        except Exception as e:
            success = False
            message = f"Error prepending content to {file_path}: {e}"
    
    elif mode in ["prepend_to_main", "append_to_main"]:
        success, message, _ = edit_note_section(file_path, content, mode)
    
    elif mode == "append_ref":
        success, message, _ = add_reference_to_note(file_path, content)
    
    else:
        return False, "Invalid edit mode specified.", ""

    if success:
         # Note: Caller might want to update metadata separately, 
         # but we'll import it here to keep the 'edited' stamp logic automatic.
         from .note_metadata import update_note_metadata
         update_note_metadata(file_path, update_edited_timestamp=True)
         return True, message, file_path
    else:
        return False, message, ""

def edit_note_section(file_path: str, content: str, mode: str) -> (bool, str, str):
    """
    Edits content within the FIRST header section of the Markdown file.
    Mode can be 'prepend_to_main' or 'append_to_main'.
    """

    if not os.path.exists(file_path):
        return False, f"Error: File not found at {file_path}", ""

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find YAML frontmatter end (first --- after initial ---)
        frontmatter_end_line = -1
        in_frontmatter = False
        if lines and lines[0].strip() == "---":
             in_frontmatter = True
             for i in range(1, len(lines)):
                 if lines[i].strip() == "---":
                     frontmatter_end_line = i
                     break
        
        start_search_line = frontmatter_end_line + 1 if frontmatter_end_line != -1 else 0

        # Find the first header
        first_header_line = -1
        for i in range(start_search_line, len(lines)):
            if lines[i].strip().startswith('#'):
                first_header_line = i
                break

        if first_header_line == -1:
            return False, f"Error: No section header found in {file_path}", ""

        # Find end of this section (the start of the NEXT header or end of file)
        next_header_line = len(lines)
        for i in range(first_header_line + 1, len(lines)):
            if lines[i].strip().startswith('#'):
                next_header_line = i
                break

        new_content_lines = []
        if mode == "prepend_to_main":
            # Add new content immediately after the first header line
            new_content_lines = lines[:first_header_line + 1] + [content + "\n"] + lines[first_header_line + 1:]
            
        elif mode == "append_to_main":
            # Add new content before the next header (or end of file)
            new_content_lines = lines[:next_header_line] + [content + "\n"] + lines[next_header_line:]
        else:
             return False, "Invalid section-based edit mode specified.", ""

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content_lines)
        
        return True, f"Successfully {mode} content to the first section in {file_path}.", file_path

    except Exception as e:
        return False, f"Error editing first section in {file_path}: {e}", ""

def add_reference_to_note(file_path: str, reference_content: str) -> (bool, str, str):
    """
    Adds a reference link to the '## References' section.
    Creates the section if it doesn't exist.
    Inserts the new reference at the TOP of the list (immediately after the header).
    """
    if not os.path.exists(file_path):
        return False, f"Error: File not found at {file_path}", ""

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check if reference already exists to avoid duplicates
        # Normalized check (ignoring whitespace/list markers)
        clean_ref = reference_content.strip()
        for line in lines:
            if clean_ref in line:
                 return True, f"Reference '{clean_ref}' already exists in {file_path}.", file_path

        # Find "## References" header (or fallback to "# References")
        ref_header_index = -1
        for i, line in enumerate(lines):
            stripped = line.strip().lower()
            if stripped == "## references" or stripped == "# references":
                ref_header_index = i
                break
        
        new_lines = []
        formatted_ref = f"- {clean_ref}\n"

        if ref_header_index != -1:
            # Header exists, insert immediately after
            new_lines = lines[:ref_header_index+1] + [formatted_ref] + lines[ref_header_index+1:]
        else:
            # Header missing, append to end of file with a separator
            # Ensure there is a newline before the separator if file is not empty
            prefix = "\n" if lines and lines[-1].strip() != "" else ""
            footer = f"{prefix}\n---\n## References\n{formatted_ref}"
            new_lines = lines + [footer]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        return True, f"Successfully added reference to {file_path}.", file_path

    except Exception as e:
        return False, f"Error adding reference to {file_path}: {e}", ""

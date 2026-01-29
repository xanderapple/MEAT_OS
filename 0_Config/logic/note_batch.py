import os
import json
import sys
import re
from .note_core import create_atomic_note, edit_existing_note
from .note_metadata import update_note_metadata, propagate_rename
from ..utils.command_utils import execute_script

def _fix_invalid_json(json_str: str) -> str:
    """
    Attempts to fix common sub-agent JSON errors:
    1. Raw newlines inside string values.
    2. Unescaped quotes inside string values.
    """
    fixed_chars = []
    in_string = False
    escaped = False
    
    i = 0
    while i < len(json_str):
        char = json_str[i]
        
        if escaped:
            fixed_chars.append(char)
            escaped = False
        elif char == '\\':
            fixed_chars.append(char)
            escaped = True
        elif char == '"':
            if in_string:
                # Potential end of string. Check if it's followed by JSON structure.
                is_structural = False
                j = i + 1
                while j < len(json_str) and json_str[j].isspace():
                    j += 1
                if j < len(json_str) and json_str[j] in [',', '}', ']', ':']:
                    is_structural = True
                
                if is_structural:
                    fixed_chars.append(char)
                    in_string = False
                else:
                    # Unescaped quote inside string
                    fixed_chars.append('\\"')
            else:
                fixed_chars.append(char)
                in_string = True
        elif char == '\n' and in_string:
            fixed_chars.append('\\n')
        else:
            fixed_chars.append(char)
        i += 1
        
    return "".join(fixed_chars)

def execute_integration_plan(processed_json_file: str, source_note_path: str = None) -> (bool, str):
    """
    Executes a batch integration plan from a JSON file.
    Handles Git commits and MOC updates.
    """
    if not os.path.exists(processed_json_file):
        return False, f"Error: Processed JSON file not found at {processed_json_file}"
    
    try:
        with open(processed_json_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            
        try:
            structured_insights = json.loads(raw_content)
        except json.JSONDecodeError:
            # Attempt to fix and reload
            fixed_content = _fix_invalid_json(raw_content)
            structured_insights = json.loads(fixed_content)
            
    except json.JSONDecodeError as e:
        return False, f"Error decoding JSON from {processed_json_file}: {e}"
    except Exception as e:
        return False, f"Error reading processed JSON file {processed_json_file}: {e}"

    files_to_add_to_git = []
    integration_messages = []
    manual_review_items = []
    files_modified = set()

    for item in structured_insights:
        file_changed = False
        current_file_path = ""
        
        if item["type"] == "new_note":
            # Default to 2_Literature_Notes for synthesis, 3_Permanent_Notes otherwise
            default_dir = "2_Literature_Notes" if "SYNTH-" in item.get("title", "") else "3_Permanent_Notes"
            target_directory = item.get("directory") or default_dir
            
            success, message, file_path = create_atomic_note(
                item.get("content", ""), 
                item.get("title"), 
                item.get("tags"), 
                target_directory,
                aliases=item.get("aliases")
            )
            integration_messages.append(message)
            if success and file_path:
                files_to_add_to_git.append(file_path)
                file_changed = True
                current_file_path = file_path

        elif item["type"] == "edit_note":
            if item.get("mode") == "manual_review":
                manual_review_items.append(item)
                continue

            success, message, file_path = edit_existing_note(item["file"], item.get("content", ""), item["mode"], item.get("title"))
            integration_messages.append(message)
            if success and file_path:
                files_to_add_to_git.append(file_path)
                file_changed = True
                current_file_path = file_path

        elif item["type"] == "manual_review":
            manual_review_items.append(item)
            continue

        elif item["type"] == "update_metadata":
            success, message = update_note_metadata(
                item["file"], 
                item.get("new_title"), 
                item.get("add_tags"), 
                item.get("add_aliases"),
                remove_tags=item.get("remove_tags"),
                remove_aliases=item.get("remove_aliases")
            )
            integration_messages.append(message)
            if success:
                files_to_add_to_git.append(item["file"])
                file_changed = True

        elif item["type"] == "rename_note":
            success, message = propagate_rename(item["file"], item["new_name"])
            integration_messages.append(message)
            if success:
                new_path = os.path.join(os.path.dirname(item["file"]), f"{item['new_name']}.md")
                files_to_add_to_git.append(new_path)
                files_to_add_to_git.append(item["file"])
                file_changed = True
        
        else:
            integration_messages.append(f"Warning: Unknown insight type '{item.get('type')}' in JSON.")
        
        if file_changed and current_file_path:
            files_modified.add(current_file_path)

    # Batch append references
    if source_note_path and files_modified:
        source_link = f"[[{os.path.basename(source_note_path)}]]"
        integration_messages.append(f"Linking source {source_link} to {len(files_modified)} modified notes...")
        for file_path in files_modified:
            ref_success, ref_msg, _ = edit_existing_note(file_path, source_link, "append_ref")
            if not ref_success:
                integration_messages.append(f"  - Failed to add reference to {os.path.basename(file_path)}: {ref_msg}")

    # MOC and Git
    success_moc, message_moc = execute_script(sys.executable, ["0_Config/main_cli.py", "rag", "update-moc"])
    if success_moc:
        integration_messages.append(message_moc)
        files_to_add_to_git.append("0_Config/Context/GEMINI_INDEX.md")
    else:
        integration_messages.append(f"Failed to update MOC: {message_moc}")

    if files_to_add_to_git:
        unique_files = list(set(files_to_add_to_git))
        execute_script("git", ["add"] + unique_files)

        commit_message_ref = os.path.basename(source_note_path) if source_note_path else "batch integration"
        commit_message = f"feat: Integrate knowledge from synthesis note '{commit_message_ref}'"
        
        commit_success, commit_output = execute_script("git", ["commit", "-m", commit_message])
        if commit_success:
            integration_messages.append("Knowledge integration complete and committed to Git.")
        else:
            integration_messages.append(f"Failed to commit changes to Git: {commit_output}")
    
    try:
        os.remove(processed_json_file)
        integration_messages.append(f"Cleaned up temporary JSON file: {processed_json_file}")
    except:
        pass

    # Build Final Report
    final_report = "\n".join(integration_messages)
    if manual_review_items:
        final_report += "\n\n" + "="*40 + "\n"
        final_report += "⚠️  ITEMS REQUIRING MANUAL REVIEW / DISCUSSION\n"
        final_report += "="*40 + "\n"
        for i, item in enumerate(manual_review_items):
            files = item.get('file') or item.get('affected_files')
            files_str = ", ".join(files) if isinstance(files, list) else str(files)
            final_report += f"\n[{i+1}] Context/Affected Files: {files_str}\n"
            final_report += f"    Proposal:\n    {item.get('content')}\n"
            if "rationale" in item:
                final_report += f"    Rationale: {item.get('rationale')}\n"
        final_report += "\n" + "="*40 + "\n"
        final_report += "Please discuss these items with the Agent to decide on the best integration strategy."

    return True, final_report

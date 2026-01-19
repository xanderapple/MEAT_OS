import os
import re

def trim_note_history(file_path: str, actual_versions: list, note_name: str) -> (bool, str):
    """
    Handles moving the oldest version block to the archive folder.
    Returns (success, message).
    """
    try:
        # Max 3 versions allowed in main note (including the new one)
        # The caller should have already counted them.
        # Move oldest to Archive
        oldest_version = actual_versions.pop(-1)
        archive_dir = "=3_Archived"
        os.makedirs(archive_dir, exist_ok=True)
        
        archive_file = os.path.join(archive_dir, f"{note_name}_History.md")
        
        # Prepend oldest to the top of the history file (after header)
        if not os.path.exists(archive_file):
            with open(archive_file, 'w', encoding='utf-8') as af:
                af.write(f"""---
title: {note_name} History
tags: #type/archive
---

# {note_name} Intellectual History

--- ARCHIVED FROM MAIN NOTE ---
{oldest_version.strip()}
""")
        else:
            with open(archive_file, 'r', encoding='utf-8') as af:
                archive_content = af.read()
            
            # Find the end of the header section (# Note Intellectual History)
            header_pattern = re.compile(r'(# .*? Intellectual History\n\n)', re.DOTALL)
            header_match = header_pattern.search(archive_content)
            
            if header_match:
                header_end = header_match.end()
                new_archive_content = archive_content[:header_end] + f"--- ARCHIVED FROM MAIN NOTE ---\n{oldest_version.strip()}\n\n" + archive_content[header_end:]
            else:
                # Fallback if header not found
                new_archive_content = f"--- ARCHIVED FROM MAIN NOTE ---\n{oldest_version.strip()}\n\n" + archive_content
                
            with open(archive_file, 'w', encoding='utf-8') as af:
                af.write(new_archive_content)
        
        return True, f"Archived oldest version of {note_name} to {archive_file}"
    except Exception as e:
        return False, f"Error archiving history for {note_name}: {e}"

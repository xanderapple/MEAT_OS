import os
import datetime
import yaml
import re
from .note_core import sanitize_filename

def update_note_metadata(file_path: str, add_tags: list = None, add_aliases: list = None, new_title: str = None, update_edited_timestamp: bool = False, remove_tags: list = None, remove_aliases: list = None) -> (bool, str):
    """
    Updates the YAML frontmatter of a note.
    """
    if not os.path.exists(file_path):
        return False, f"Error: File not found at {file_path}"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        frontmatter_start = -1
        frontmatter_end = -1
        
        for i in range(len(lines)):
            if lines[i].strip() == "---":
                if frontmatter_start == -1:
                    frontmatter_start = i
                else:
                    frontmatter_end = i
                    break
        
        if frontmatter_start == -1 or frontmatter_end == -1:
            return False, "Error: Invalid or missing YAML frontmatter."

        # Extract YAML content
        yaml_content = "".join(lines[frontmatter_start+1:frontmatter_end])
        metadata = yaml.safe_load(yaml_content) or {}

        # Normalize keys to Capitalized for writing, but read flexibly
        # Helper to get value from either Capitalized or lowercase key
        def get_meta(key, default=None):
            return metadata.get(key.capitalize(), metadata.get(key.lower(), default))
            
        updated = False

        # --- TAGS ---
        if add_tags or remove_tags:
            current_tags = get_meta('tags', [])
            if isinstance(current_tags, str):
                current_tags = [t.strip() for t in current_tags.split(',')]
            if not isinstance(current_tags, list):
                current_tags = []

            if add_tags:
                for tag in add_tags:
                    if tag not in current_tags:
                        current_tags.append(tag)
                        updated = True
            
            if remove_tags:
                new_tags = [t for t in current_tags if t not in remove_tags]
                if len(new_tags) != len(current_tags):
                    current_tags = new_tags
                    updated = True
            
            # Clean up old lowercase key if present, enforce Capitalized
            if 'tags' in metadata: del metadata['tags']
            metadata['Tags'] = current_tags

        # --- ALIASES ---
        if add_aliases or remove_aliases:
            current_aliases = get_meta('aliases', [])
            if not isinstance(current_aliases, list):
                current_aliases = []

            if add_aliases:
                for alias in add_aliases:
                    if alias not in current_aliases:
                        current_aliases.append(alias)
                        updated = True
            
            if remove_aliases:
                new_aliases = [a for a in current_aliases if a not in remove_aliases]
                if len(new_aliases) != len(current_aliases):
                    current_aliases = new_aliases
                    updated = True

            # Clean up old lowercase key if present, enforce Capitalized
            if 'aliases' in metadata: del metadata['aliases']
            metadata['Aliases'] = current_aliases
        
        # --- TITLE (Aliases Only) ---
        # We no longer store 'title' in YAML, but we handle renaming by adding old title to aliases
        if new_title:
             # Logic: If we are renaming, we assume the file rename happens elsewhere (propagate_rename)
             # Here we just ensure the OLD title is preserved as an alias if needed.
             # We rely on the caller to provide the *old* title context if they want it aliased,
             # but propagate_rename passes 'new_title' as the target name.
             
             # Actually, propagate_rename calls this. Let's look at how it uses it.
             # It says: update_note_metadata(old_path, add_aliases=[old_name], new_title=safe_new_name...)
             # So we just need to ensure we don't WRITE 'title' to YAML.
             
             # If 'title' key exists in legacy note, remove it.
             if 'title' in metadata: 
                 del metadata['title']
                 updated = True
             if 'Title' in metadata:
                 del metadata['Title']
                 updated = True

        # --- EDITED ---
        if update_edited_timestamp:
            # Clean up old lowercase key
            if 'edited' in metadata: del metadata['edited']
            metadata['Edited'] = datetime.date.today().strftime("%Y-%m-%d")
            updated = True

        if updated:
            # Ensure 'Created' is Capitalized if it exists as 'created'
            if 'created' in metadata:
                metadata['Created'] = metadata.pop('created')
            
            new_yaml = yaml.dump(metadata, sort_keys=False, default_flow_style=False)
            new_frontmatter = ["---\n", new_yaml, "---\n"]
            new_file_lines = new_frontmatter + lines[frontmatter_end+1:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_file_lines)
            return True, f"Updated metadata for {file_path}"
        else:
            return True, f"No metadata changes needed for {file_path}"

    except Exception as e:
        return False, f"Error updating metadata: {e}"

def propagate_rename(old_path: str, new_name: str) -> (bool, str):
    """Renames a note and updates all wikilinks in the vault."""
    try:
        if not os.path.exists(old_path):
            return False, f"Source file not found: {old_path}"

        old_name = os.path.splitext(os.path.basename(old_path))[0]
        directory = os.path.dirname(old_path)
        
        # Ensure we sanitize the new name
        safe_new_name = sanitize_filename(new_name)
        new_path = os.path.join(directory, f"{safe_new_name}.md")

        if os.path.exists(new_path):
            return False, f"Target filename already exists: {new_path}"

        # 1. Update all links in the vault
        # Handle optional paths (using / or \) before the note name
        link_pattern = re.compile(rf'\[\[(.*?[\/\\])?{re.escape(old_name)}(\|.*?)?\]\]')
        
        vault_files = []
        for root, _, files in os.walk("."):
            for file in files:
                if file.endswith(".md"):
                    vault_files.append(os.path.join(root, file))

        updated_files_count = 0
        for file in vault_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if link_pattern.search(content):
                    # We use a lambda to preserve the optional path captured in group 1
                    new_content = link_pattern.sub(lambda m: f'[[{m.group(1) or ""}{safe_new_name}{m.group(2) or ""}]]', content)
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated_files_count += 1
            except UnicodeDecodeError:
                continue # Skip files that are not valid UTF-8

        # 2. Add old title to aliases of the note itself BEFORE renaming
        update_note_metadata(old_path, add_aliases=[old_name], new_title=safe_new_name, update_edited_timestamp=True)

        # 3. Rename the file
        os.rename(old_path, new_path)

        return True, f"Renamed '{old_name}' to '{safe_new_name}'. Updated links in {updated_files_count} files."

    except Exception as e:
        return False, f"Error during rename propagation: {e}"

import os
import re
import sys
import yaml

def add_tag_to_md_file(filepath, tag_to_add):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter_match = re.match(r'---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    
    new_content = content
    tag_added = False

    if frontmatter_match:
        frontmatter_str = frontmatter_match.group(1)
        try:
            frontmatter_data = yaml.safe_load(frontmatter_str)
            if frontmatter_data is None: # Handle empty frontmatter
                frontmatter_data = {}
        except yaml.YAMLError:
            frontmatter_data = {} # Fallback if frontmatter is invalid

        if 'tags' in frontmatter_data:
            if isinstance(frontmatter_data['tags'], list):
                if tag_to_add not in frontmatter_data['tags']:
                    frontmatter_data['tags'].append(tag_to_add)
                    tag_added = True
            elif isinstance(frontmatter_data['tags'], str):
                existing_tags = [t.strip() for t in frontmatter_data['tags'].split(',') if t.strip()]
                if tag_to_add not in existing_tags:
                    existing_tags.append(tag_to_add)
                    frontmatter_data['tags'] = ', '.join(existing_tags)
                    tag_added = True
        else: # 'tags' key not present in frontmatter
            frontmatter_data['tags'] = [tag_to_add]
            tag_added = True
        
        if tag_added:
            new_frontmatter_str = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            new_content = f"---\n{new_frontmatter_str}---{content[frontmatter_match.end():]}"
    elif not frontmatter_match: # No frontmatter, append tag to the end
        if content.strip(): # Only append if content is not entirely empty
            new_content = content.strip() + f'\n\n#{tag_to_add.replace("/", "_")}' # Simple append, sanitize tag for non-frontmatter
            tag_added = True
        elif not content.strip(): # File is empty, just add frontmatter with tag
            new_content = f"---\ntags:\n  - {tag_to_add}\n---\n"
            tag_added = True
            
    if tag_added:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def bulk_tagger(directory, tag, dry_run=False):
    files_tagged = []
    print(f"Searching for .md files in '{directory}' to add tag '{tag}'...")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                if dry_run:
                    print(f"DRY RUN: Would tag '{filepath}' with '{tag}'")
                    files_tagged.append(filepath)
                else:
                    if add_tag_to_md_file(filepath, tag):
                        print(f"Tagged '{filepath}' with '{tag}'")
                        files_tagged.append(filepath)
    return files_tagged

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python bulk_tagger.py <directory_path> <tag_to_add> [--dry-run]")
        sys.exit(1)
    
    dir_path = sys.argv[1]
    tag = sys.argv[2]
    dry_run = "--dry-run" in sys.argv

    if not os.path.isdir(dir_path):
        print(f"Error: Directory '{dir_path}' not found.")
        sys.exit(1)
    
    tagged_files = bulk_tagger(dir_path, tag, dry_run)
    print(f"\nSummary: {len(tagged_files)} files processed.")
    if dry_run:
        print("This was a DRY RUN. No files were actually modified.")

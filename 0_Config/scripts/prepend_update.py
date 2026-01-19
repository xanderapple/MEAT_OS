import os
import sys
import re

def prepend_content_after_yaml(file_path: str, update_content: str) -> bool:
    """
    Reads a Markdown file, inserts update_content immediately after the YAML frontmatter,
    and writes the modified content back to the file.
    Assumes YAML frontmatter is at the very beginning of the file, enclosed by '---'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        sys.stderr.write(f"Error: File not found at {file_path}\n")
        return False
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            sys.stderr.write(f"Error reading {file_path} with latin-1 fallback: {e}\n")
            return False
    except Exception as e:
        sys.stderr.write(f"Error reading {file_path}: {e}\n")
        return False

    # Regex to find YAML frontmatter (between two '---' lines at the beginning of the file)
    yaml_frontmatter_pattern = re.compile(r"^(---.*?---)\s*\n", re.DOTALL)
    match = yaml_frontmatter_pattern.match(content)

    if match:
        yaml_block = match.group(1)
        remaining_content = content[match.end():]
        
        # Insert new content after the YAML block and a blank line
        new_content = f"{yaml_block}\n\n{update_content}\n\n{remaining_content}"
    else:
        # No YAML frontmatter found, just prepend to the beginning (or after first H1 if present)
        sys.stderr.write(f"Warning: No YAML frontmatter found in {file_path}. Prepending to beginning.\n")
        new_content = f"{update_content}\n\n{content}"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        sys.stderr.write(f"Error writing to {file_path}: {e}\n")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3: 
        sys.stderr.write("Usage: python prepend_update.py <file_path> <update_content>\n")
        sys.exit(1)

    file_to_update = sys.argv[1]
    # The update_content is now passed directly as sys.argv[2]
    # Join all subsequent arguments to form the complete update_content string
    update_content = " ".join(sys.argv[2:]) 
    
    if prepend_content_after_yaml(file_to_update, update_content):
        print(f"Successfully prepended update to {file_to_update}")
    else:
        sys.stderr.write(f"Failed to prepend update to {file_to_update}\n")
        sys.exit(1)